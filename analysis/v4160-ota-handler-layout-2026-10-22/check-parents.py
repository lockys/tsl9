#!/usr/bin/env python3
"""Read only the sealed parent documentation and dependency digests."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(name):
    path = ROOT / name
    if name.startswith('analysis/') and not path.exists():
        path = ROOT / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError('contained dependency path')
    return path


def main():
    seal = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = HERE / name
        if not path.resolve().is_relative_to(HERE) or digest(path) != pin:
            raise ValueError('parent member digest: ' + name)
    for name, pin in seal['external_inputs'].items():
        if digest(locate(name)) != pin:
            raise ValueError('external dependency digest: ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('default Traditional Chinese copy')
    print(json.dumps(dict(passed=True, metadata_only=True,
                          sealed_parent_members=len(seal['members']),
                          external_dependencies=len(seal['external_inputs']),
                          actual_native_artifacts_read=False, HOST_tests_rerun=False,
                          original_ABI_admitted=False, placement_admitted=False,
                          BIN_generated=False)))


if __name__ == '__main__':
    main()
