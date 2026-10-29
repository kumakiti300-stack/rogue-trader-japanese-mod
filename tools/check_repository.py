"""Reject translation payloads and development artifacts from the distribution Git tree."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CONFIG_JSON = {
    'templates/mod/OwlcatModificationManifest.json',
    'templates/mod/OwlcatModificationSettings.json',
}
PRIVATE_DIRECTORIES = {'data', 'raw', 'input', 'output', 'tmp', '.tmp', 'build', 'dist', 'reports', 'translations', 'localization', '.agents', '.venv'}
ARTIFACT_SUFFIXES = {'.jsonl', '.zip', '.7z', '.tar', '.gz', '.dll', '.exe', '.pdb', '.unitypackage', '.log', '.sha256'}


def contains_translation(value: object) -> bool:
    if isinstance(value, dict):
        if isinstance(value.get('strings'), dict) or {'source_en', 'revised_ja'} <= value.keys() or {'source_en', 'official_ja'} <= value.keys():
            return True
        return any(contains_translation(item) for item in value.values())
    return isinstance(value, list) and any(contains_translation(item) for item in value)


def check_file(name: str, content: bytes) -> list[str]:
    path = PurePosixPath(name)
    errors = []
    if any(part.lower() in PRIVATE_DIRECTORIES for part in path.parts[:-1]):
        errors.append(f'{name}: development/translation directory is not allowed')
    if path.name.lower().startswith('.env') or path.suffix.lower() in ARTIFACT_SUFFIXES:
        errors.append(f'{name}: generated data, binary, archive or secret file is not allowed')
    if path.suffix.lower() == '.json' and name not in CONFIG_JSON:
        errors.append(f'{name}: only the two MOD configuration JSON templates are allowed')
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        return errors + [f'{name}: non-text file requires an explicit distribution review']
    try:
        value = json.loads(text)
    except (ValueError, RecursionError):
        value = None
        if path.suffix.lower() == '.json':
            errors.append(f'{name}: invalid JSON configuration')
    if contains_translation(value):
        errors.append(f'{name}: localization pack or parallel translation content is not allowed')
    return errors


def git(*args: str) -> bytes:
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def check_repository(history: bool = False) -> dict:
    paths = [p for p in git('ls-files', '-z').decode('utf-8').split('\0') if p]
    errors = []
    for name in paths:
        path = ROOT/name
        if not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
            errors.append(f'{name}: missing file or external symbolic link')
            continue
        errors.extend(check_file(name, path.read_bytes()))
    commits = git('rev-list', '--all').decode('ascii').splitlines() if history else []
    seen = set()
    for commit in commits:
        for record in git('ls-tree', '-r', '-z', commit).split(b'\0'):
            if not record:
                continue
            metadata, raw_name = record.split(b'\t', 1)
            mode, kind, blob = metadata.decode('ascii').split()
            name = raw_name.decode('utf-8')
            identity = (name, blob)
            if identity in seen:
                continue
            seen.add(identity)
            if kind != 'blob' or mode == '120000':
                errors.append(f'{name}: submodule or symbolic link in history')
                continue
            errors.extend('history '+e for e in check_file(name, git('cat-file', 'blob', blob)))
    return {'tracked_files': len(paths), 'history_commits': len(commits), 'errors': sorted(set(errors))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true', help='also inspect all reachable Git commits')
    args = parser.parse_args()
    report = check_repository(args.history)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(report['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
