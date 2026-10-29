"""Release-packager tests; synthetic localization exists only in external temp files."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package_release", REPOSITORY / "tools/package_release.py")
assert SPEC is not None and SPEC.loader is not None
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)

GUID = "11111111-1111-1111-1111-111111111111"
# Intentionally include a UTF-8 BOM, CRLF, whitespace, and Japanese text to
# catch any accidental reserialization of the caller's localization bytes.
VALID_LOCALIZATION = b"\xef\xbb\xbf" + (
    '{\r\n  "strings": {\r\n'
    '    "11111111-1111-1111-1111-111111111111": {"Offset": 0, "Text": "検証専用の架空文"}\r\n'
    "  }\r\n}\r\n"
).encode("utf-8")


class PackageReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rtjp-package-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "fixture-repository"
        for relative in (
            "templates/mod/OwlcatModificationManifest.json",
            "templates/mod/OwlcatModificationSettings.json",
            "templates/package-README.md",
        ):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPOSITORY / relative).read_bytes())
        for relative in ("NOTICE.md", "docs/install.md", "docs/reporting.md"):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"Synthetic document: {relative}\n", encoding="utf-8")
        (self.repo / ".env").write_text("unrelated file; do not package\n", encoding="utf-8")
        (self.repo / "docs/not-in-package.md").write_text("not included\n", encoding="utf-8")
        self.localization = self.base / "private-input" / "jaJP.json"
        self.localization.parent.mkdir()
        self.localization.write_bytes(VALID_LOCALIZATION)
        self.output = self.base / "packages" / "RTJP-1.2.3.zip"
        self.checksum = self.output.with_name(self.output.name + ".sha256")

    def build(self, **overrides):
        args = {
            "localization": self.localization,
            "version": "1.2.3",
            "output": self.output,
            "repository_root": self.repo,
        }
        args.update(overrides)
        return packager.package_release(**args)

    def assert_no_output(self) -> None:
        self.assertFalse(self.output.exists())
        self.assertFalse(self.checksum.exists())

    def test_valid_package_preserves_input_and_contains_only_allowlisted_members(self) -> None:
        result = self.build()
        expected_files = {
            "RTJP_Japanese/OwlcatModificationManifest.json",
            "RTJP_Japanese/OwlcatModificationSettings.json",
            "RTJP_Japanese/Localization/jaJP.json",
            "RTJP_Japanese/README.md",
            "RTJP_Japanese/NOTICE.md",
            "RTJP_Japanese/docs/install.md",
            "RTJP_Japanese/docs/reporting.md",
        }
        expected_dirs = {"RTJP_Japanese/Assemblies/", "RTJP_Japanese/Bundles/", "RTJP_Japanese/Blueprints/"}
        with zipfile.ZipFile(self.output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), expected_files | expected_dirs)
            self.assertEqual(len(archive.namelist()), len(expected_files | expected_dirs))
            self.assertEqual(archive.read("RTJP_Japanese/Localization/jaJP.json"), VALID_LOCALIZATION)
            for name in expected_dirs:
                self.assertTrue(archive.getinfo(name).is_dir())
                self.assertEqual(archive.read(name), b"")
            manifest = json.loads(archive.read("RTJP_Japanese/OwlcatModificationManifest.json"))
            for key, value in packager.FIXED_MANIFEST_FIELDS.items():
                self.assertEqual(manifest[key], value)
            self.assertEqual(manifest["Version"], "1.2.3")
            settings = json.loads(archive.read("RTJP_Japanese/OwlcatModificationSettings.json"))
            self.assertEqual(settings, packager.EXPECTED_SETTINGS)
            readme = archive.read("RTJP_Japanese/README.md").decode("utf-8")
            self.assertIn("1.2.3", readme)
            self.assertNotIn("{{VERSION}}", readme)
            for name, source in packager.DOCUMENTS.items():
                self.assertEqual(archive.read(name), (self.repo / source).read_bytes())
        self.assertEqual(self.localization.read_bytes(), VALID_LOCALIZATION)
        self.assertEqual(list(self.repo.rglob("jaJP.json")), [])
        digest = hashlib.sha256(self.output.read_bytes()).hexdigest()
        self.assertEqual(self.checksum.read_text(encoding="utf-8"), f"{digest}  {self.output.name}\n")
        self.assertEqual(result["sha256"], digest)
        self.assertEqual(result["strings"], 1)

    def test_four_component_version_always_replaces_template_version(self) -> None:
        manifest_path = self.repo / "templates/mod/OwlcatModificationManifest.json"
        template = json.loads(manifest_path.read_text(encoding="utf-8"))
        template["Version"] = "99.99.99"
        manifest_path.write_text(json.dumps(template), encoding="utf-8")
        self.build(version="1.2.3.4")
        with zipfile.ZipFile(self.output) as archive:
            manifest = json.loads(archive.read("RTJP_Japanese/OwlcatModificationManifest.json"))
        self.assertEqual(manifest["Version"], "1.2.3.4")

    def test_japanese_zip_filename_has_utf8_checksum_sidecar(self) -> None:
        output = self.output.with_name("日本語再翻訳-1.2.3.zip")
        self.build(output=output)
        checksum = output.with_name(output.name + ".sha256")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        self.assertEqual(checksum.read_text(encoding="utf-8"), f"{digest}  {output.name}\n")

    def test_invalid_localizations_are_rejected_without_outputs(self) -> None:
        def entry(value):
            return json.dumps({"strings": {GUID: value}}, ensure_ascii=False).encode("utf-8")

        cases = {
            "empty file": b"",
            "whitespace": b" \n\t",
            "broken JSON": b'{"strings":',
            "invalid UTF-8": b"\xff",
            "array root": b"[]",
            "missing strings": b"{}",
            "null strings": b'{"strings":null}',
            "list strings": b'{"strings":[]}',
            "empty strings": b'{"strings":{}}',
            "bad GUID": json.dumps({"strings": {"not-a-guid": {"Offset": 0, "Text": "x"}}}).encode(),
            "unhyphenated GUID": json.dumps({"strings": {"1" * 32: {"Offset": 0, "Text": "x"}}}).encode(),
            "null entry": entry(None),
            "list entry": entry([]),
            "missing Offset": entry({"Text": "x"}),
            "string Offset": entry({"Offset": "0", "Text": "x"}),
            "float Offset": entry({"Offset": 0.0, "Text": "x"}),
            "boolean Offset": entry({"Offset": False, "Text": "x"}),
            "missing Text": entry({"Offset": 0}),
            "null Text": entry({"Offset": 0, "Text": None}),
            "numeric Text": entry({"Offset": 0, "Text": 1}),
            "empty Text": entry({"Offset": 0, "Text": ""}),
            "whitespace Text": entry({"Offset": 0, "Text": " \n\u3000"}),
            "NaN": f'{{"strings":{{"{GUID}":{{"Offset":NaN,"Text":"x"}}}}}}'.encode(),
            "Infinity": f'{{"strings":{{"{GUID}":{{"Offset":Infinity,"Text":"x"}}}}}}'.encode(),
            "unpaired surrogate": f'{{"strings":{{"{GUID}":{{"Offset":0,"Text":"\\ud800"}}}}}}'.encode(),
            "duplicate top-level key": b'{"strings":{},"strings":{}}',
            "duplicate Text key": f'{{"strings":{{"{GUID}":{{"Offset":0,"Text":"x","Text":"y"}}}}}}'.encode(),
            "duplicate GUID key": f'{{"strings":{{"{GUID}":{{"Offset":0,"Text":"x"}},"{GUID}":{{"Offset":0,"Text":"y"}}}}}}'.encode(),
            "case-equivalent GUIDs": json.dumps({"strings": {
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa": {"Offset": 0, "Text": "x"},
                "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA": {"Offset": 0, "Text": "y"},
            }}).encode(),
        }
        for label, payload in cases.items():
            with self.subTest(label=label):
                self.localization.write_bytes(payload)
                with self.assertRaises(packager.PackageError):
                    self.build()
                self.assert_no_output()

    def test_invalid_versions_are_rejected(self) -> None:
        for version in ("1.2", "1", "1.2.3.4.5", "v1.2.3", "-1.2.3", "1.2.x", "1..3", "1.2.3\n", "１.２.３"):
            with self.subTest(version=version):
                with self.assertRaisesRegex(packager.PackageError, "version"):
                    self.build(version=version)
                self.assert_no_output()

    def test_input_inside_repository_is_rejected(self) -> None:
        source = self.repo / "jaJP.json"
        source.write_bytes(VALID_LOCALIZATION)
        with self.assertRaisesRegex(packager.PackageError, "outside the repository"):
            self.build(localization=source)
        self.assert_no_output()
        self.assertEqual(source.read_bytes(), VALID_LOCALIZATION)

    def test_external_symlink_into_repository_is_rejected(self) -> None:
        source = self.repo / "private-jaJP.json"
        source.write_bytes(VALID_LOCALIZATION)
        link = self.base / "external-link.json"
        try:
            link.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("file symlinks are unavailable on this host")
        with self.assertRaisesRegex(packager.PackageError, "resolve outside"):
            self.build(localization=link)
        self.assert_no_output()

    def test_repository_symlink_to_external_input_is_rejected(self) -> None:
        link = self.repo / "local-link.json"
        try:
            link.symlink_to(self.localization)
        except (OSError, NotImplementedError):
            self.skipTest("file symlinks are unavailable on this host")
        with self.assertRaisesRegex(packager.PackageError, "outside the repository"):
            self.build(localization=link)
        self.assert_no_output()

    def test_missing_input_and_directory_are_rejected(self) -> None:
        for source in (self.base / "missing.json", self.localization.parent):
            with self.subTest(source=source):
                with self.assertRaises(packager.PackageError):
                    self.build(localization=source)
                self.assert_no_output()

    def test_existing_zip_is_preserved(self) -> None:
        self.output.parent.mkdir()
        self.output.write_bytes(b"existing output")
        with self.assertRaisesRegex(packager.PackageError, "overwriting is forbidden"):
            self.build()
        self.assertEqual(self.output.read_bytes(), b"existing output")
        self.assertFalse(self.checksum.exists())

    def test_existing_checksum_is_preserved_and_zip_not_created(self) -> None:
        self.output.parent.mkdir()
        self.checksum.write_bytes(b"existing checksum")
        with self.assertRaisesRegex(packager.PackageError, "overwriting is forbidden"):
            self.build()
        self.assertFalse(self.output.exists())
        self.assertEqual(self.checksum.read_bytes(), b"existing checksum")

    def test_missing_required_document_fails_before_creating_output(self) -> None:
        (self.repo / "docs/install.md").unlink()
        with self.assertRaisesRegex(packager.PackageError, "docs/install.md"):
            self.build()
        self.assert_no_output()

    def test_wrong_metadata_and_nonempty_mod_settings_are_rejected(self) -> None:
        manifest = self.repo / "templates/mod/OwlcatModificationManifest.json"
        original = manifest.read_bytes()
        changed = json.loads(original)
        changed["UniqueName"] = "different-mod"
        manifest.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaisesRegex(packager.PackageError, "metadata"):
            self.build()
        manifest.write_bytes(original)
        settings = self.repo / "templates/mod/OwlcatModificationSettings.json"
        changed = json.loads(settings.read_bytes())
        changed["BlueprintPatches"].append("not-allowed")
        settings.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaisesRegex(packager.PackageError, "localization-only"):
            self.build()
        self.assert_no_output()

    def test_verification_failure_cleans_only_its_new_output(self) -> None:
        self.output.parent.mkdir()
        unrelated = self.output.parent / "keep-me.txt"
        unrelated.write_bytes(b"unrelated")
        with mock.patch.object(packager, "_verify_zip", side_effect=packager.PackageError("CRC failure")):
            with self.assertRaisesRegex(packager.PackageError, "CRC failure"):
                self.build()
        self.assert_no_output()
        self.assertEqual(unrelated.read_bytes(), b"unrelated")
        self.assertEqual(self.localization.read_bytes(), VALID_LOCALIZATION)

    def test_checksum_race_preserves_other_file_and_removes_its_zip(self) -> None:
        def create_competing_checksum(path):
            self.checksum.write_bytes(b"created by someone else")
            return hashlib.sha256(path.read_bytes()).hexdigest()

        with mock.patch.object(packager, "_digest_file", side_effect=create_competing_checksum):
            with self.assertRaises(FileExistsError):
                self.build()
        self.assertFalse(self.output.exists())
        self.assertEqual(self.checksum.read_bytes(), b"created by someone else")

    def test_cleanup_does_not_delete_an_output_replaced_by_another_writer(self) -> None:
        def replace_output_and_fail(output, expected):
            competing = output.with_name("competing-output.tmp")
            competing.write_bytes(b"replacement owned by someone else")
            os.replace(competing, output)
            raise packager.PackageError("verification interrupted")

        with mock.patch.object(packager, "_verify_zip", side_effect=replace_output_and_fail):
            with self.assertRaisesRegex(packager.PackageError, "verification interrupted"):
                self.build()
        self.assertEqual(self.output.read_bytes(), b"replacement owned by someone else")
        self.assertFalse(self.checksum.exists())

    def test_cli_uses_explicit_arguments_and_outputs_result(self) -> None:
        stdout = io.StringIO()
        with mock.patch.object(packager, "REPOSITORY_ROOT", self.repo), contextlib.redirect_stdout(stdout):
            result = packager.main([
                "--localization", str(self.localization), "--version", "2.3.4", "--output", str(self.output)
            ])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue())["strings"], 1)
        self.assertTrue(self.output.exists())


if __name__ == "__main__":
    unittest.main()
