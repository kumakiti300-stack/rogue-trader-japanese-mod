"""Exercise the distribution guard without storing translation fixtures in Git."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKER_PATH = Path(__file__).resolve().parents[1] / 'tools/check_repository.py'
SPEC = importlib.util.spec_from_file_location('distribution_repository_check', CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)

MANIFEST_PATH = 'templates/mod/OwlcatModificationManifest.json'
SETTINGS_PATH = 'templates/mod/OwlcatModificationSettings.json'
MANIFEST = {
    'UniqueName': 'RTJP_Japanese',
    'Version': '0.1.0',
    'DisplayName': 'Rogue Trader Japanese',
    'Description': 'Japanese localization MOD.',
    'Author': 'Rogue Trader Japanese project',
    'Repository': '',
    'HomePage': '',
    'Dependencies': [],
}
SETTINGS = {
    'BundlesLayout': {'m_Guids': [], 'm_Bundles': []},
    'BundleDependencies': {'m_List': []},
    'BlueprintPatches': [],
}


def encoded(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode('utf-8')


class FilePolicyTests(unittest.TestCase):
    def assert_translation_rejected(self, name: str, value: object) -> None:
        errors = CHECKER.check_file(name, encoded(value))
        self.assertTrue(
            any('localization pack or parallel translation content' in error for error in errors),
            (name, errors),
        )

    def test_both_mod_metadata_templates_are_allowed(self) -> None:
        for name, value in ((MANIFEST_PATH, MANIFEST), (SETTINGS_PATH, SETTINGS)):
            with self.subTest(name=name):
                self.assertEqual(CHECKER.check_file(name, encoded(value)), [])

    def test_utf8_bom_is_allowed_for_metadata(self) -> None:
        self.assertEqual(CHECKER.check_file(MANIFEST_PATH, b'\xef\xbb\xbf' + encoded(MANIFEST)), [])

    def test_markdown_documentation_with_a_format_example_is_allowed(self) -> None:
        markdown = (
            '# 導入手順\n\n'
            '配布ファイルはReleasesから取得してください。\n\n'
            '```json\n{"strings":{"<GUID>":{"Offset":0,"Text":"<text>"}}}\n```\n'
        ).encode('utf-8')
        self.assertEqual(CHECKER.check_file('docs/install.md', markdown), [])

    def test_unapproved_json_path_is_rejected_even_for_benign_metadata(self) -> None:
        errors = CHECKER.check_file('docs/manifest.json', encoded(MANIFEST))
        self.assertTrue(any('only the two MOD configuration JSON templates' in error for error in errors))

    def test_renaming_localization_json_cannot_bypass_content_detection(self) -> None:
        pack = {'strings': {'example-id': {'Offset': 0, 'Text': '架空の検査用文章'}}}
        for name in ('docs/release.txt', 'docs/release.md', 'docs/release', 'docs/release.csv'):
            with self.subTest(name=name):
                self.assert_translation_rejected(name, pack)

    def test_nested_localization_pack_is_rejected(self) -> None:
        self.assert_translation_rejected('docs/notes.txt', {'metadata': [{'payload': {'strings': {}}}]})

    def test_source_and_revised_parallel_rows_are_rejected(self) -> None:
        self.assert_translation_rejected(
            'docs/candidates.txt',
            [{'key': 'example-id', 'source_en': 'Synthetic source.', 'revised_ja': '架空の修正訳。'}],
        )

    def test_source_and_official_parallel_rows_are_rejected(self) -> None:
        self.assert_translation_rejected(
            'docs/candidates.md',
            {'results': [{'source_en': 'Synthetic source.', 'official_ja': '架空の参照訳。'}]},
        )

    def test_allowlisted_metadata_paths_still_reject_translation_payloads(self) -> None:
        payloads = (
            {'strings': {'example-id': {'Text': '架空の検査用文章'}}},
            {'source_en': 'Synthetic source.', 'revised_ja': '架空の修正訳。'},
            {'source_en': 'Synthetic source.', 'official_ja': '架空の参照訳。'},
        )
        for name, template in ((MANIFEST_PATH, MANIFEST), (SETTINGS_PATH, SETTINGS)):
            for payload in payloads:
                with self.subTest(name=name, payload=payload):
                    self.assert_translation_rejected(name, {**template, 'unexpected': [payload]})

    def test_private_directories_are_rejected_case_insensitively(self) -> None:
        for name in (
            'Localization/notes.md',
            'LOCALIZATION/notes.md',
            'lOcAlIzAtIoN/notes.md',
            'data/notes.md',
            'DaTa/notes.md',
            'docs/DATA/notes.md',
        ):
            with self.subTest(name=name):
                errors = CHECKER.check_file(name, b'# Notes\n')
                self.assertTrue(any('development/translation directory' in error for error in errors))

    def test_directory_words_in_document_filenames_are_allowed(self) -> None:
        for name in ('docs/localization.md', 'docs/data-policy.md', 'docs/environment.md'):
            with self.subTest(name=name):
                self.assertEqual(CHECKER.check_file(name, b'# Notes\n'), [])

    def test_archives_and_build_artifacts_are_rejected_case_insensitively(self) -> None:
        for suffix in ('.zip', '.ZIP', '.7z', '.tar', '.gz', '.dll', '.exe', '.pdb', '.unitypackage'):
            with self.subTest(suffix=suffix):
                errors = CHECKER.check_file('assets/package' + suffix, b'synthetic content')
                self.assertTrue(any('generated data, binary, archive or secret file' in error for error in errors))

    def test_environment_secret_files_are_rejected_case_insensitively(self) -> None:
        for name in ('.env', '.env.local', 'docs/.ENV.production'):
            with self.subTest(name=name):
                errors = CHECKER.check_file(name, b'EXAMPLE_TOKEN=not-a-real-secret\n')
                self.assertTrue(any('secret file' in error for error in errors))

    def test_non_utf8_payload_is_rejected_even_with_a_text_extension(self) -> None:
        for name in ('docs/notes.txt', MANIFEST_PATH):
            with self.subTest(name=name):
                errors = CHECKER.check_file(name, b'\xff\xfe\x00\x80')
                self.assertTrue(any('non-text file' in error for error in errors))

    def test_invalid_json_in_an_allowed_metadata_path_is_rejected(self) -> None:
        errors = CHECKER.check_file(SETTINGS_PATH, b'{ "BundlesLayout": ')
        self.assertTrue(any('invalid JSON configuration' in error for error in errors))


@unittest.skipUnless(shutil.which('git'), 'Git is required for repository history checks')
class GitHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix='rtjp-repository-guard-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.repository = Path(cls.temporary.name)
        cls.script = cls.repository / 'tools/check_repository.py'
        cls.script.parent.mkdir()
        cls.script.write_bytes(CHECKER_PATH.read_bytes())
        (cls.repository / 'README.md').write_text('# Synthetic distribution repository\n', encoding='utf-8')
        for name, value in ((MANIFEST_PATH, MANIFEST), (SETTINGS_PATH, SETTINGS)):
            path = cls.repository / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
        cls.run_git('init', '-q')
        cls.commit_all('Clean metadata and documentation')
        cls.clean_commit = cls.run_git('rev-parse', 'HEAD').stdout.strip()
        cls.main_branch = cls.run_git('symbolic-ref', '--short', 'HEAD').stdout.strip()

        # These payloads disappear from the current files but remain in ancestors.
        cls.retired_path = 'docs/retired-notes.md'
        retired = cls.repository / cls.retired_path
        retired.parent.mkdir()
        retired.write_bytes(encoded({'strings': {'example-id': {'Text': '架空の旧出力'}}}))
        (cls.repository / MANIFEST_PATH).write_bytes(encoded({**MANIFEST, 'strings': {}}))
        cls.commit_all('Synthetic forbidden historical payloads')
        retired.unlink()
        (cls.repository / MANIFEST_PATH).write_bytes(encoded(MANIFEST))
        cls.commit_all('Remove historical payloads from the current tree')

        # Also exercise --all: this payload was never present in the main branch.
        cls.run_git('checkout', '-q', '-b', 'legacy-payload', cls.clean_commit)
        cls.branch_only_path = 'branch-only.txt'
        (cls.repository / cls.branch_only_path).write_bytes(encoded({
            'source_en': 'Synthetic branch-only source.',
            'official_ja': '架空の参照訳。',
        }))
        cls.commit_all('Synthetic forbidden payload on another reachable branch')
        cls.run_git('checkout', '-q', cls.main_branch)

    @classmethod
    def run_git(cls, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ['git', *args], cwd=cls.repository, check=True, capture_output=True, text=True,
        )

    @classmethod
    def commit_all(cls, message: str) -> None:
        cls.run_git('add', '-A')
        cls.run_git(
            '-c', 'user.name=Repository Guard Tests',
            '-c', 'user.email=repository-guard-tests@example.invalid',
            '-c', 'commit.gpgsign=false',
            'commit', '-q', '-m', message,
        )

    def check(self, *, history: bool) -> tuple[int, dict]:
        command = [sys.executable, '-B', str(self.script)]
        if history:
            command.append('--history')
        result = subprocess.run(command, cwd=self.repository, capture_output=True, text=True, encoding='utf-8')
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_clean_current_files_pass_despite_removed_historical_payloads(self) -> None:
        returncode, report = self.check(history=False)
        self.assertEqual(returncode, 0, report)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['tracked_files'], 4)
        self.assertEqual(report['history_commits'], 0)

    def test_deleted_translation_and_contaminated_metadata_are_detected_in_history(self) -> None:
        returncode, report = self.check(history=True)
        self.assertEqual(returncode, 1, report)
        self.assertEqual(report['history_commits'], 4)
        for name in (self.retired_path, MANIFEST_PATH):
            with self.subTest(name=name):
                self.assertTrue(any(
                    error.startswith('history ' + name + ':')
                    and 'localization pack or parallel translation content' in error
                    for error in report['errors']
                ), report)

    def test_translation_on_another_reachable_branch_is_detected(self) -> None:
        returncode, report = self.check(history=True)
        self.assertEqual(returncode, 1, report)
        self.assertTrue(any(
            error.startswith('history ' + self.branch_only_path + ':')
            and 'localization pack or parallel translation content' in error
            for error in report['errors']
        ), report)


if __name__ == '__main__':
    unittest.main()
