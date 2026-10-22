#!/usr/bin/env python3
"""Validate archived layout metadata without claiming local artifact replay."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    seal = json.loads((HERE / 'seal.json').read_bytes())
    for name, pin in seal['members'].items():
        path = (HERE / name).resolve(strict=True)
        path.relative_to(HERE)
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('archived layout member changed: ' + name)
    if (HERE / 'README.md').read_bytes() != (HERE / 'readme.zh-TW.md').read_bytes():
        raise ValueError('full Traditional Chinese default')
    print(json.dumps({'metadata_passed': True, 'members': len(seal['members']),
                      'actual_local_build_replayed': False, 'hardware_OTA_proved': False}))


if __name__ == '__main__':
    main()
