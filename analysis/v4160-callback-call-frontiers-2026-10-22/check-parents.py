#!/usr/bin/env python3
"""Read only the documentation and independent-scope seal identities."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    seal = json.loads((HERE / 'parent-seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = HERE / name
        if not path.resolve().is_relative_to(HERE) or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('parent evidence identity: ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('full Traditional Chinese default')
    print(json.dumps(dict(passed=True, metadata_only=True, members=len(seal['members']),
                          actual_native_artifacts_read=False, actual_candidate_artifacts_read=False,
                          physical_ROM_identified=False, target_execution=False, new_BIN=False)))


if __name__ == '__main__':
    main()
