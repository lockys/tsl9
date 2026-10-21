#!/usr/bin/env python3
"""Metadata-only validation. Actual build archives are never implicit inputs."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_source(root, name):
    direct = root / name
    if direct.is_file():
        return direct
    prefix = 'apk-analysis/tsl9-'
    if name.startswith(prefix):
        return root / ('analysis/' + name[len(prefix):])
    return direct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for member in seal['files']:
        path = HERE / member['path']
        require(path.is_file() and path.stat().st_size == member['bytes'] and
                sha(path) == member['sha256'], 'Sealed metadata/source member: ' + member['path'])
    summary = json.loads((HERE / 'summary.json').read_bytes())
    for name, expected in summary['external_source_pins'].items():
        require(sha(resolve_source(root, name)) == expected, 'Current independent dependency pin: ' + name)
    require(summary['original_ABI_admitted'] is False and summary['full_image_updated'] is False,
            'Partial component boundary remains explicit')
    print(json.dumps(dict(metadata_checked=True, actual_build_artifact_replay=False,
                         firmware_read=False, original_ABI_admitted=False,
                         full_image_updated=False, sealed_members=len(seal['files']))))


if __name__ == '__main__':
    main()
