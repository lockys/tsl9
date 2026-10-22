#!/usr/bin/env python3
"""Check the sealed registration report; do not claim local BIN replay."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for name, expected in seal['members'].items():
        path = (HERE / name).resolve(strict=True)
        path.relative_to(HERE)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('immutable registration member ' + name)
    report = json.loads((HERE / 'selected-original.json').read_bytes())
    if not report['passed'] or len(report['proof']['selected_operands']) != 27 or len(report['controls']) != 27:
        raise ValueError('exact archived selected-operand result')
    if report['runner_sha256'] != hashlib.sha256((HERE / 'check.py').read_bytes()).hexdigest():
        raise ValueError('actual report runner identity')
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('full Traditional Chinese default')
    print(json.dumps({'passed': True, 'metadata_members': len(seal['members']),
                      'actual_local_firmware_read': False, 'target_execution': False,
                      'installed_ROM_semantics_proved': False}))


if __name__ == '__main__':
    main()
