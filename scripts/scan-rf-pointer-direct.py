#!/usr/bin/env python3
"""Bounded adjacent RISC-V LUI[/ADDI]+load/store encoding scan; not reachability."""
import hashlib
import json
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[1] / 'analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
SHA = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
BASE = 0x40000
TARGET = 0x20003538

def sx(x, n):
    return x - (1 << n) if x & (1 << (n - 1)) else x

def scan(data):
    hits = []
    # Every halfword, including data and overlapping instructions. Only contiguous
    # 32-bit LUI, optional ADDI, then load/store, same base register.
    for i in range(0, len(data) - 7, 2):
        lui = int.from_bytes(data[i:i+4], 'little')
        reg = (lui >> 7) & 31
        if lui & 127 != 0x37 or not reg:
            continue
        value = lui & 0xfffff000
        j = i + 4
        word = int.from_bytes(data[j:j+4], 'little')
        if word & 0x707f == 0x13 and (word >> 7 & 31) == reg and (word >> 15 & 31) == reg:
            value = (value + sx(word >> 20, 12)) & 0xffffffff
            j += 4
            if j + 2 > len(data):
                continue
            word = int.from_bytes(data[j:j+4], 'little')
        # Compressed register-relative LW/SW, including a base alias such as
        # 0x20003514 plus offset 36. This is still only an adjacent sequence.
        h = word & 0xffff
        if h & 3 == 0 and h >> 13 in (2, 6) and 8 + (h >> 7 & 7) == reg:
            offset = ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)
            addr = (value + offset) & 0xffffffff
            if addr <= TARGET + 3 and addr + 4 > TARGET:
                store = h >> 13 == 6
                hits.append({'pc': hex(BASE+i), 'access_pc': hex(BASE+j), 'bytes': data[i:j+2].hex(), 'kind': 'store' if store else 'load', 'address': hex(addr), 'width': 4, 'source_register': 8 + (h >> 2 & 7) if store else None})
        if j + 4 > len(data):
            continue
        op, funct, rs = word & 127, word >> 12 & 7, word >> 15 & 31
        if rs != reg or op not in (3, 0x23):
            continue
        widths = {0: 1, 1: 2, 2: 4, 4: 1, 5: 2} if op == 3 else {0: 1, 1: 2, 2: 4}
        if funct not in widths:
            continue
        imm = sx(word >> 20, 12) if op == 3 else sx((word >> 25) << 5 | (word >> 7 & 31), 12)
        addr = (value + imm) & 0xffffffff
        if addr <= TARGET + 3 and addr + widths[funct] > TARGET:
            hits.append({'pc': hex(BASE+i), 'access_pc': hex(BASE+j), 'bytes': data[i:j+4].hex(), 'kind': 'load' if op == 3 else 'store', 'address': hex(addr), 'width': widths[funct], 'source_register': (word >> 20 & 31) if op == 0x23 else None})
    return hits

def verify(data):
    if len(data) != 191078 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('candidate identity mismatch')
    return scan(data)

if __name__ == '__main__':
    print(json.dumps({'sha256': SHA, 'range': ['0x40000', '0x6ea66'], 'hits': verify(IMAGE.read_bytes())}, indent=2))
