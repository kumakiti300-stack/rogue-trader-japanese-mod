#!/usr/bin/env python3
"""Build a release ZIP from an explicitly supplied external localization file.

Requires Python 3.11+ and the standard library. No upload or game operations
are performed, and the localization is never extracted into the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any
from uuid import UUID
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MOD_ROOT = "RTJP_Japanese"
PROJECT_URL = "https://github.com/kumakiti300-stack/rogue-trader-japanese-mod"
LOCALIZATION_ENTRY = f"{MOD_ROOT}/Localization/jaJP.json"
EMPTY_DIRECTORIES = tuple(f"{MOD_ROOT}/{name}/" for name in ("Assemblies", "Bundles", "Blueprints"))
DOCUMENTS = {
    f"{MOD_ROOT}/NOTICE.md": "NOTICE.md",
    f"{MOD_ROOT}/docs/install.md": "docs/install.md",
    f"{MOD_ROOT}/docs/reporting.md": "docs/reporting.md",
}
FIXED_MANIFEST_FIELDS = {
    "UniqueName": MOD_ROOT,
    "DisplayName": "Rogue Trader Japanese",
    "Author": "Rogue Trader Japanese project",
    "Repository": PROJECT_URL,
    "HomePage": PROJECT_URL,
    "Dependencies": [],
}
EXPECTED_SETTINGS = {
    "BundlesLayout": {"m_Guids": [], "m_Bundles": []},
    "BundleDependencies": {"m_List": []},
    "BlueprintPatches": [],
}
GUID_PATTERN = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
VERSION_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+){2,3}")


class PackageError(ValueError):
    """The input or package does not meet the release contract."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackageError("JSON contains a duplicate object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise PackageError(f"JSON contains the non-standard value {value}")


def _decode_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise PackageError(f"{label} must be valid UTF-8 JSON") from exc


def _inside(path: Path, repository: Path) -> bool:
    return path.is_relative_to(repository)


def _read_localization(path: Path, repository: Path) -> tuple[bytes, int]:
    # Check both forms: an in-repository symlink pointing out is still an
    # in-repository input, and an external symlink pointing in is also refused.
    candidate = Path(os.path.abspath(path.expanduser()))
    if _inside(candidate, repository):
        raise PackageError("localization input must be outside the repository")
    try:
        resolved = candidate.resolve(strict=True)
        if _inside(resolved, repository):
            raise PackageError("localization input must resolve outside the repository")
        if not stat.S_ISREG(resolved.stat().st_mode):
            raise PackageError("localization input must be an existing regular file")
        raw = resolved.read_bytes()
    except OSError as exc:
        raise PackageError("localization input must be a readable existing regular file") from exc

    payload = _decode_json(raw, "localization input")
    if not isinstance(payload, dict) or not isinstance(payload.get("strings"), dict):
        raise PackageError("localization input must contain a strings object")
    strings = payload["strings"]
    if not strings:
        raise PackageError("localization strings must not be empty")

    seen_guids: set[str] = set()
    for key, entry in strings.items():
        if not GUID_PATTERN.fullmatch(key):
            raise PackageError("localization strings contain an invalid GUID")
        normalized = UUID(key).hex
        if normalized in seen_guids:
            raise PackageError("localization strings contain a duplicate GUID")
        seen_guids.add(normalized)
        if not isinstance(entry, dict) or type(entry.get("Offset")) is not int:
            raise PackageError("every localization entry must contain an integer Offset")
        text = entry.get("Text")
        if not isinstance(text, str) or not text.strip():
            raise PackageError("every localization entry must contain non-empty Text")
        try:
            text.encode("utf-8")
        except UnicodeError as exc:
            raise PackageError("localization Text contains an invalid Unicode surrogate") from exc
    return raw, len(strings)


def _read_asset(repository: Path, relative: str) -> bytes:
    try:
        return (repository / relative).read_bytes()
    except OSError as exc:
        raise PackageError(f"required package source is missing or unreadable: {relative}") from exc


def _package_files(repository: Path, localization: bytes, version: str) -> dict[str, bytes]:
    manifest = _decode_json(
        _read_asset(repository, "templates/mod/OwlcatModificationManifest.json"), "manifest template"
    )
    if not isinstance(manifest, dict) or any(
        manifest.get(key) != value for key, value in FIXED_MANIFEST_FIELDS.items()
    ):
        raise PackageError("manifest template has unexpected release metadata")
    manifest["Version"] = version

    settings_raw = _read_asset(repository, "templates/mod/OwlcatModificationSettings.json")
    if _decode_json(settings_raw, "settings template") != EXPECTED_SETTINGS:
        raise PackageError("settings template must describe an empty localization-only MOD")

    readme_raw = _read_asset(repository, "templates/package-README.md")
    try:
        readme = readme_raw.decode("utf-8")
    except UnicodeError as exc:
        raise PackageError("package README template must be UTF-8") from exc
    if "{{VERSION}}" not in readme:
        raise PackageError("package README template is missing its version placeholder")
    files = {
        f"{MOD_ROOT}/OwlcatModificationManifest.json": (
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8"),
        f"{MOD_ROOT}/OwlcatModificationSettings.json": settings_raw,
        LOCALIZATION_ENTRY: localization,
        f"{MOD_ROOT}/README.md": readme.replace("{{VERSION}}", version).encode("utf-8"),
    }
    # Only these named files are read. No directory glob or repository archive
    # can accidentally add the translation corpus, hidden files, or other docs.
    files.update({name: _read_asset(repository, relative) for name, relative in DOCUMENTS.items()})
    return files


def _zip_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    info.external_attr = ((stat.S_IFDIR | 0o755) if directory else (stat.S_IFREG | 0o644)) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def _verify_zip(output: Path, expected_files: dict[str, bytes]) -> None:
    try:
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != set(expected_files) | set(EMPTY_DIRECTORIES):
                raise PackageError("ZIP entries do not match the explicit package allowlist")
            bad_member = archive.testzip()
            if bad_member is not None:
                raise PackageError("ZIP CRC verification failed")
            for name in EMPTY_DIRECTORIES:
                if not archive.getinfo(name).is_dir() or archive.getinfo(name).file_size != 0:
                    raise PackageError("ZIP is missing a required empty MOD directory")
            for name, expected in expected_files.items():
                if archive.read(name) != expected:
                    raise PackageError("ZIP content does not match its package source")
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise PackageError("ZIP verification failed") from exc


def _digest_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _identity(stream: Any) -> tuple[int, int]:
    file_stat = os.fstat(stream.fileno())
    return file_stat.st_dev, file_stat.st_ino


def _cleanup_created(created: list[tuple[Path, tuple[int, int]]]) -> None:
    for path, identity in reversed(created):
        try:
            current = path.lstat()
            if stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == identity:
                path.unlink()
        except FileNotFoundError:
            pass


def package_release(
    localization: Path,
    version: str,
    output: Path,
    *,
    repository_root: Path | None = None,
) -> dict[str, str | int]:
    """Build and verify one new ZIP and its SHA-256 sidecar.

    ``repository_root`` supports an isolated fixture repository in tests; the
    command-line entry point always uses this script's own repository root.
    """
    repository = (repository_root or REPOSITORY_ROOT).resolve(strict=True)
    if not VERSION_PATTERN.fullmatch(version):
        raise PackageError("version must contain three or four dot-separated numeric components")
    output = Path(os.path.abspath(output.expanduser()))
    if output.suffix.lower() != ".zip" or any(c in output.name for c in "\r\n"):
        raise PackageError("output must be a ZIP filename without line breaks")
    checksum_path = output.with_name(output.name + ".sha256")
    if any(path.exists() or path.is_symlink() for path in (output, checksum_path)):
        raise PackageError("output ZIP and checksum must both be new files; overwriting is forbidden")

    localization_raw, count = _read_localization(localization, repository)
    files = _package_files(repository, localization_raw, version)
    output.parent.mkdir(parents=True, exist_ok=True)
    created: list[tuple[Path, tuple[int, int]]] = []
    try:
        # Exclusive creation also protects against a file appearing after the
        # preflight check. Never use ZipFile(path, 'w') on the final pathname.
        with output.open("xb") as stream:
            created.append((output, _identity(stream)))
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for directory in EMPTY_DIRECTORIES:
                    archive.writestr(_zip_info(directory, directory=True), b"")
                for name, payload in files.items():
                    archive.writestr(_zip_info(name), payload, compresslevel=9)
        _verify_zip(output, files)
        digest = _digest_file(output)
        with checksum_path.open("x", encoding="utf-8", newline="\n") as stream:
            created.append((checksum_path, _identity(stream)))
            stream.write(f"{digest}  {output.name}\n")
        return {"output": str(output), "sha256_file": str(checksum_path), "sha256": digest, "strings": count}
    except BaseException:
        _cleanup_created(created)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localization", type=Path, required=True, help="existing jaJP.json outside this repository")
    parser.add_argument("--version", required=True, help="three or four dot-separated numeric components")
    parser.add_argument("--output", type=Path, required=True, help="new release ZIP; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        result = package_release(args.localization, args.version, args.output)
    except (PackageError, OSError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
