#!/usr/bin/env python3
"""Pin the image and static instruction windows; never execute the target."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE = 0x8000
LENGTH = 76800
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0xae0e: bytes.fromhex('797122d42a8403453500854726d2171700202302f70c06d64ad04ece3d899717002083c7d70b8144638ba70097170020a387a70a751513354500013785440357040093079039631cf70e0347b40085476317f70eb7070400fc473146a285480082979389810b171900200349d90683a709006300090c89e7efd0afb223aca10a8347c100414793f7c7036389e70601499717002083c7d70499cb19478d07238ee10aa38ef10a97170020a38b070283c7c10bc1c7fd17238ef10a83c7d10bbd8b139727008347c10093f737fcd98f2306f100b2470347d1009d45b183bd8b85073d8b9207d98f4800a306f100ef3070602307a1004800ef70503091a0efd04fad098951d5efd0efd22a8951d1efd06fa983a709001d8d8d679387f7ede3e9a7f68347c10093f737fc93e747002306f10085b7b1df23ac010aa1bfe31c09f8'),
    0x81b0: bytes.fromhex('b7070400fc5f411106c68297a9473305f502b240410111818280'),
    0x81de: bytes.fromhex('938741059c4303c557000d8905058280'),
    0x8440: bytes.fromhex('03c5c1168280'),
}

class VerificationError(ValueError):
    pass

def check_windows(image):
    for pc, expected in WINDOWS.items():
        actual = image[pc - BASE:pc - BASE + len(expected)]
        if actual != expected:
            raise VerificationError(f'window mismatch at {pc:#x}')

def address(image, pc, store=False):
    """Decode AUIPC plus adjacent LBU/SB; use AUIPC's own PC, RV32 wrap."""
    off = pc - BASE
    if off < 0 or len(image[off:off + 8]) != 8:
        raise VerificationError('truncated address pair')
    u = int.from_bytes(image[off:off + 4], 'little')
    ins = int.from_bytes(image[off + 4:off + 8], 'little')
    rd = (u >> 7) & 31
    if u & 127 != 0x17 or rd == 0 or (ins >> 15) & 31 != rd:
        raise VerificationError('not an AUIPC address pair')
    if store:
        if ins & 127 != 0x23 or (ins >> 12) & 7 != 0 or (ins >> 20) & 31 != 0:
            raise VerificationError('not SB zero')
        imm = ((ins >> 25) << 5) | ((ins >> 7) & 31)
    else:
        if ins & 127 != 0x03 or (ins >> 12) & 7 != 4:
            raise VerificationError('not LBU')
        imm = ins >> 20
    imm = imm - 4096 if imm & 0x800 else imm
    return (pc + (u & 0xfffff000) + imm) & 0xffffffff

def verify(image):
    if len(image) != LENGTH:
        raise VerificationError('incorrect full image length')
    if hashlib.sha256(image).hexdigest() != SHA256:
        raise VerificationError('incorrect full image SHA-256')
    check_windows(image)
    if address(image, 0xae9e) != 0x2000beeb or address(image, 0xaeb4, True) != 0x2000beeb:
        raise VerificationError('incorrect PC-relative address')

def main():
    verify(IMAGE.read_bytes())
    print('verified image, windows and PC-relative addresses')

if __name__ == '__main__':
    main()
