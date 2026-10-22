#!/usr/bin/env python3
"""Verify only the parent-owned source/documentation seal; no native build."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    sealed = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in sealed['members'].items():
        path = HERE / name
        if not path.resolve().is_relative_to(HERE) or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('parent source/documentation seal: ' + name)
    root = HERE.parents[1]
    for name, pin in sealed['external_inputs'].items():
        path = root / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('parent external source input: ' + name)
    for prefix in ('', 'entry-plan/', 'gp-plan/', 'tail-plan/'):
        if (HERE / (prefix + 'README.md')).read_bytes() != (HERE / (prefix + 'readme.zh-TW.md')).read_bytes():
            raise ValueError('default Traditional Chinese copy: ' + prefix)
    print(json.dumps(dict(passed=True, sealed_parent_members=len(sealed['members']),
                          metadata_only=True, actual_native_artifacts_read=False,
                          HOST_tests_rerun=False, original_ABI_admitted=False,
                          placement_admitted=False, BIN_generated=False)))


if __name__ == '__main__':
    main()
