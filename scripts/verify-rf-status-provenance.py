#!/usr/bin/env python3
"""Pin bounded static RF status evidence; does not establish reachability or ABI."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SDK = ROOT / 'analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
SPECS = {
    'app': (0x8000, 76800, '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', (
        (0x174ee, 0x1753a, '8d1fe26ede0b1c74b6c550872c3a3db09c6ce90f8b129501d4d6e50156c974d0'),
        (0x175e8, 0x17666, 'f4a0f1fe856e488853f27ae937fdca1e9e0240a4b705e79b77265675c3513c5e'),
    )),
    'sdk': (0x40000, 191078, '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', (
        (0x401c4, 0x401c8, 'dc55dfbb2d2cbe1162d1469abf1e87506fc55a4b1b2cfb005508cdfd23fe64b0'),
        (0x645dc, 0x646a8, '1d6f1e4f8b846f93e35696b266869542744609b60bb6dbaad732a78576174331'),
        (0x64bae, 0x64cec, '0e73a5cebf069a716f6967b386c8cc9de529e25608933422eda98997a0ec9bf4'),
    )),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_windows(kind, data):
    base, _, _, windows = SPECS[kind]
    for start, end, expected in windows:
        if start < base or end - base > len(data) or digest(data[start-base:end-base]) != expected:
            raise ValueError(f'{kind} window {start:#x}..{end:#x} mismatch')


def verify(kind, data):
    _, size, expected, _ = SPECS[kind]
    if len(data) != size or digest(data) != expected:
        raise ValueError(f'{kind} full artifact mismatch')
    check_windows(kind, data)


if __name__ == '__main__':
    for kind, path in (('app', APP), ('sdk', SDK)):
        verify(kind, path.read_bytes())
        print(f'{kind}: artifact and bounded windows match')
