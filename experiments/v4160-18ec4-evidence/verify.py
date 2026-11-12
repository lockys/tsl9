#!/usr/bin/env python3
"""Offline identity, window and RV32C branch checks; never executes target code."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOW = bytes.fromhex('b7270240984bb7060200137505f0558f98cbc8cb984b1367070498cbd847058b75ff984b8176fd16758f98cb8280')
BASE, START, END = 0x8000, 0x18ec4, 0x18ef2
BRANCH = 0x18ee4


def require(ok, message):
    if not ok:
        raise ValueError(message)


def decode_branch(window):
    """Decode C.BNEZ's scattered signed 9-bit displacement and source register."""
    pos = BRANCH - START
    require(len(window) >= pos + 2, 'short branch window')
    insn = int.from_bytes(window[pos:pos + 2], 'little')
    require(insn & 0xe003 == 0xe001, 'not C.BNEZ')
    imm = (((insn >> 12) & 1) << 8 | ((insn >> 10) & 3) << 3 |
           ((insn >> 5) & 3) << 6 | ((insn >> 3) & 3) << 1 |
           ((insn >> 2) & 1) << 5)
    if imm & 0x100:
        imm -= 0x200
    return 8 + ((insn >> 7) & 7), BRANCH + imm


def check_window(window):
    require(decode_branch(window) == (14, 0x18ee0), 'branch register/target mismatch')
    require(window == WINDOW, 'window bytes mismatch')


def verify(data):
    require(len(data) == 76800, 'image length mismatch')
    require(hashlib.sha256(data).hexdigest() == IMAGE_SHA, 'image SHA-256 mismatch')
    check_window(data[START - BASE:END - BASE])


def main():
    try:
        require(len(sys.argv) <= 2, 'usage: verify.py [image.bin]')
        path = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT
        verify(path.read_bytes())
        print('OK: image, window and C.BNEZ x14 -> 0x18ee0')
    except (ValueError, OSError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
