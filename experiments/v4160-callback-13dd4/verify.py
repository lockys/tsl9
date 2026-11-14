"""Static, bounded checks for the callback at 0x13dd4; no target execution."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x13dd4
CODE = bytes.fromhex('41 11 17 05 00 00 13 05 e5 ff 06 c6 ef 50 0f ad 01 45 ef f0 3f f6 ef 40 0f bc 09 ed b2 40 81 46 13 06 c0 12 81 45 17 05 00 00 13 05 e5 18 41 01 6f 50 0f b2 b2 40 41 01 82 80')


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


def jal_target(pc, w, rd):
    if w & 127 != 0x6f or w >> 7 & 31 != rd: raise ValueError('wrong JAL encoding')
    imm = ((w >> 31 & 1) << 20 | (w >> 12 & 255) << 12 |
           (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
    return (pc + signed(imm, 21)) & 0xffffffff


def bnez_target(pc, h):
    if h & 3 != 1 or h >> 13 != 7 or (h >> 7 & 7) != 2:
        raise ValueError('not C.BNEZ a0')
    imm = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 |
           (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
    return pc + signed(imm, 9)


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    raw = image[BASE-0x8000:BASE-0x8000+len(CODE)]
    if raw != CODE: raise ValueError('instruction window mismatch')
    targets = ((0x0c, 1, 0x90b0), (0x12, 1, 0x13d48), (0x16, 1, 0x81aa), (0x30, 0, 0x9124))
    for offset, rd, expected in targets:
        pc = BASE + offset
        w = int.from_bytes(raw[offset:offset+4], 'little')
        if jal_target(pc, w, rd) != expected: raise ValueError(f'JAL target mismatch at {pc:#x}')
        if jal_target(pc, w ^ (1 << 21), rd) == expected: raise ValueError('JAL mutation undetected')
    if bnez_target(BASE+0x1a, int.from_bytes(raw[0x1a:0x1c], 'little')) != 0x13e08:
        raise ValueError('wrong conditional branch target')
    print('PASS: pinned 58-byte callback, three call targets, conditional return and tail target')
    print('calls: 0x90b0(self), 0x13d48(0), 0x81aa(); nonzero returns; zero tail-jumps 0x9124')
    print('Static decoded control flow only; external callees, normal return and hardware not established.')


if __name__ == '__main__': main()
