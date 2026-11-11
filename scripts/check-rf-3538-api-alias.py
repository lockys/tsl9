#!/usr/bin/env python3
"""Pinned RF_Tx alias witness; static bytes and conditional arithmetic only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
HEADER = ROOT / 'analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h'
IMAGE_SHA = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
HEADER_SHA = '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c'
# Individual instruction bytes, including the branch to the indirect word store.
WINDOWS = {
    0x64d14: '37340020', 0x64d22: '13044451',
    0x64e0e: '0850', 0x64e10: '63080c0c',
    0x64e14: '23007501', 0x64e18: '04b1',
    0x64e1a: '2686', 0x64e1c: 'e285', 0x64e1e: '0905',
    0x64e20: '97b0f91f', 0x64e24: 'e7802051',
    0x64ee0: '23207501',
}
TARGET = (0x20003538, 0x2000353c)

def intersects(address, size):
    if not 0 <= address <= 0xffffffff or not 0 <= size <= 0x100000000 - address:
        raise ValueError('invalid or wrapping interval')
    return size > 0 and address < TARGET[1] and TARGET[0] < address + size

def verify(image, header):
    if len(image) != 0x2ea66 or hashlib.sha256(image).hexdigest() != IMAGE_SHA:
        raise ValueError('candidate image identity mismatch')
    if hashlib.sha256(header).hexdigest() != HEADER_SHA:
        raise ValueError('header identity mismatch')
    for pc, encoded in WINDOWS.items():
        data = bytes.fromhex(encoded)
        if image[pc - 0x40000:pc - 0x40000 + len(data)] != data:
            raise ValueError(f'instruction mismatch at {pc:#x}')
    for signature in (b'BLE_LIB_JT(102)', b'uint8_t *rxBuf', b'uint8_t *txBuf'):
        if signature not in header:
            raise ValueError('header declaration missing')
    return {'entry': '0x64cec', 'pointer_word': '0x20003534',
            'target_word': '0x20003538', 'byte_store': '0x64e14',
            'word_store': '0x64ee0', 'conditional_alias_only': True}

if __name__ == '__main__':
    print(json.dumps(verify(IMAGE.read_bytes(), HEADER.read_bytes()), indent=2))
