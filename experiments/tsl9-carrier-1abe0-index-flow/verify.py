#!/usr/bin/env python3
"""Offline, conditional ordinary-entry arithmetic replay; not an ISA emulator."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
CONSUMER = bytes.fromhex('97f7ff1f83c7c705c5cb17f7ff1f034747059306f00f834745006318d70697f6ff1f9386e60383c6360017f7ff1f03473703fd1693f6f60f17f6ff1fa303d602bdc69546631ed7048346550093f7f7f8f19a93e61600a302d5002302f50083474500120793861700bd8ac19bd58f2302f50097d700009387a7123e97369783470700a301f5006f50702a0d4693061700b3e6c60217f6ff1f2305d6fc49d3014793767700920693f7f7f8d58f7db797f6ff1f238706fa71b78280')
SETTER = bytes.fromhex('97f7ff1f9387c7ed05473306c0402380e700a380a7002381c700a381b7008280')


def verify(data, pin=True):
    if len(data) != 76800 or (pin and hashlib.sha256(data).hexdigest() != SHA):
        raise ValueError('APP identity mismatch')
    for pc, raw in ((0xcedc, CONSUMER), (0xd05c, SETTER)):
        if data[pc-BASE:pc-BASE+len(raw)] != raw:
            raise ValueError(f'instruction witness changed at {pc:#x}')


def read_address(enable, phase, mode, record4):
    """Inputs are sampled bytes at their indicated loads, not initial RAM snapshot."""
    if any(not isinstance(x, int) or not 0 <= x <= 255 for x in (enable, phase, mode, record4)):
        raise ValueError('expected four bytes')
    if not enable:
        return None
    # CF78: phase == 0 enters CEFA and samples the mode; phase == FF
    # enters CEFA directly. Otherwise CF7A overwrites a4 with zero.
    row = mode if phase in (0, 255) else 0
    return 0x1a078 + 16 * row + ((record4 + 1) & 15)


def main():
    verify(IMAGE.read_bytes())
    hits = {(m, n) for m in range(256) for n in range(16)
            if 0x1abe0 <= read_address(1, 255, m, (n-1) & 255) < 0x1ac00}
    expected = {(182, n) for n in range(8, 16)} | {(183, n) for n in range(16)} | {(184, n) for n in range(8)}
    if hits != expected:
        raise ValueError('carrier intersection mismatch')
    print(f'fixed APP {SHA}; ordinary-entry conditional carrier pairs: {len(hits)}; modes 182, 183, 184')


if __name__ == '__main__':
    main()
