#!/usr/bin/env python3
"""Bounded static field checks; never execute target instructions."""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
START = 0x8a82
RAW = bytes.fromhex('b707040083a7c7139385010882978547630df50283d7a10963922703c167f917630ef900b707040083a7c713938501084a85829785470546630af500f240')

# Expected major ISA fields: LUI(op,rd,upper), I(op,rd,funct3,rs1,imm),
# B(op,funct3,rs1,rs2,signed displacement), or exact compressed halfword.
RECORDS = [
 (0x8a82,'U',(0x37,15,0x40)), (0x8a86,'I',(3,15,2,15,316)),
 (0x8a8a,'I',(0x13,11,0,3,128)), (0x8a8e,'C',0x9782),
 (0x8a90,'C',0x4785), (0x8a92,'B',(0x63,0,10,15,58)),
 (0x8a96,'I',(3,15,5,3,154)), (0x8a9a,'B',(0x63,1,15,18,36)),
 (0x8a9e,'C',0x67c1), (0x8aa0,'C',0x17f9),
 (0x8aa2,'B',(0x63,0,18,15,28)), (0x8aa6,'U',(0x37,15,0x40)),
 (0x8aaa,'I',(3,15,2,15,316)), (0x8aae,'I',(0x13,11,0,3,128)),
 (0x8ab2,'C',0x854a), (0x8ab4,'C',0x9782),
 (0x8ab6,'C',0x4785), (0x8ab8,'C',0x4605),
 (0x8aba,'B',(0x63,0,10,15,20)), (0x8abe,'C',0x40f2),
]

def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

def fields(kind, w):
    if kind == 'C': return w
    op, rd, f, rs1 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31
    if kind == 'U': return op, rd, w >> 12
    if kind == 'I': return op, rd, f, rs1, signed(w >> 20, 12)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    return op, f, rs1, (w >> 20) & 31, signed(imm, 13)

def require(ok, msg):
    if not ok: raise ValueError(msg)

def run():
    image = BIN.read_bytes()
    require(len(image) == 76800, 'reference length mismatch')
    require(sha256(image).hexdigest() == SHA, 'reference SHA mismatch')
    raw = image[START-0x8000:START-0x8000+len(RAW)]
    require(raw == RAW, 'reference window mismatch')
    end = START
    mutations = 0
    for pc, kind, expected in RECORDS:
        size = 2 if kind == 'C' else 4
        require(pc == end, f'gap at {end:#x}')
        w = int.from_bytes(raw[pc-START:pc-START+size], 'little')
        require(fields(kind, w) == expected, f'fields at {pc:#x}')
        # Each encoded field is flipped directly, bypassing the full-window pin.
        bits = {'C': (0, 2, 7, 12, 15), 'U': (0, 7, 12),
                'I': (0, 7, 12, 15, 20), 'B': (0, 12, 15, 20, 7, 8, 25, 31)}[kind]
        for bit in bits:
            require(fields(kind, w ^ (1 << bit)) != expected, f'mutation accepted {pc:#x}/{bit}')
            mutations += 1
        end += size
    require(end == START + len(RAW), 'window coverage')
    print(f'OK SHA, {len(raw)} bytes, {len(RECORDS)} instructions, {mutations} direct field mutations rejected')

if __name__ == '__main__': run()
