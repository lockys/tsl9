#!/usr/bin/env python3
"""Static operand check for one QingKe RF_Tx callsite window; not execution."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
SHA256 = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
START = 0x64e0e


def decode_load(data):
    if len(data) != 2:
        raise ValueError('invalid c.lw')
    w = int.from_bytes(data, 'little')
    if w & 0xe003 != 0x4000:
        raise ValueError('invalid c.lw')
    return (8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7),
            ((w >> 10) & 7) * 8 + ((w >> 6) & 1) * 4 + ((w >> 5) & 1) * 64)


def decode_sb(data):
    if len(data) != 4:
        raise ValueError('invalid sb')
    w = int.from_bytes(data, 'little')
    if w & 0x707f != 0x23:
        raise ValueError('invalid sb')
    imm = ((w >> 25) << 5) | ((w >> 7) & 31)
    return ((w >> 20) & 31, (w >> 15) & 31, imm - 4096 if imm & 2048 else imm)


def decode_qk_sb(data):
    # QingKe compressed byte-store encoding, not standard RVC C.FSD.
    if len(data) != 2:
        raise ValueError('invalid qk.c.sb')
    w = int.from_bytes(data, 'little')
    if w & 0xe003 != 0xa000:
        raise ValueError('invalid qk.c.sb')
    return (8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7),
            ((w >> 10) & 3) * 8 + ((w >> 12) & 1) + ((w >> 5) & 3) * 2)


def check_window(window):
    if len(window) != 12 or window[2:6] != bytes.fromhex('63080c0c'):
        raise ValueError('window or branch mismatch')
    operands = (decode_load(window[:2]), decode_sb(window[6:10]), decode_qk_sb(window[10:12]))
    if operands != ((10, 8, 32), (23, 10, 0), (9, 10, 1)):
        raise ValueError('operand mismatch')
    return operands


def check_image(image):
    if len(image) != 0x2ea66 or hashlib.sha256(image).hexdigest() != SHA256:
        raise ValueError('image identity mismatch')
    return check_window(image[START - 0x40000:START - 0x40000 + 12])


if __name__ == '__main__':
    print('static operands (register, base, offset):', check_image(IMAGE.read_bytes()))
