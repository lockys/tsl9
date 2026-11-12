"""Raw adjacent address-materialization/store patterns, not instruction simulation."""
import hashlib
import json
from pathlib import Path

BASE = 0x8000
SIZE = 76800
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
TARGET = 0x2000bed5
MASK = 0xffffffff


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def store32(word):
    if word & 127 != 0x23 or (word >> 12) & 7 not in (0, 1, 2):
        return None
    width = 1 << ((word >> 12) & 7)
    imm = signed(((word >> 25) << 5) | ((word >> 7) & 31), 12)
    return ((word >> 15) & 31, (word >> 20) & 31, imm, width)


def store16(half):
    # C.SW only: compact base and source registers, unsigned scaled offset.
    if half & 3 != 0 or half >> 13 != 6:
        return None
    imm = (((half >> 10) & 7) << 3) | (((half >> 6) & 1) << 2) | (((half >> 5) & 1) << 6)
    return (8 + ((half >> 7) & 7), 8 + ((half >> 2) & 7), imm, 4)


def overlaps(address, width):
    return any((address + i) & MASK == TARGET for i in range(width))


def scan(data):
    """Every even offset; 4-byte AUIPC/LUI immediately followed by S or C.SW,
    plus standalone 32-bit S with rs1=x0. Image offset zero maps to BASE."""
    hits = []
    for off in range(0, len(data) - 1, 2):
        pc = BASE + off
        if off + 4 > len(data):
            continue
        word = int.from_bytes(data[off:off + 4], 'little')
        s = store32(word)
        if s and s[0] == 0 and overlaps(s[2] & MASK, s[3]):
            hits.append(dict(kind='x0', materializer=None, store=pc, base_register=0,
                             source_register=s[1], immediate=s[2], width=s[3], address=s[2] & MASK))
        opcode, rd = word & 127, (word >> 7) & 31
        if opcode not in (0x17, 0x37) or rd == 0:
            continue
        value = ((pc if opcode == 0x17 else 0) + (word & 0xfffff000)) & MASK
        pos = off + 4
        if pos + 2 > len(data):
            continue
        half = int.from_bytes(data[pos:pos + 2], 'little')
        candidates = [(store16(half), 'compressed')]
        if pos + 4 <= len(data):
            candidates.append((store32(int.from_bytes(data[pos:pos + 4], 'little')), 'standard'))
        for st, encoding in candidates:
            if st is None or st[0] != rd:
                continue
            address = (value + st[2]) & MASK
            if overlaps(address, st[3]):
                hits.append(dict(kind='auipc' if opcode == 0x17 else 'lui', encoding=encoding,
                                 materializer=pc, store=pc + 4, base_register=rd,
                                 source_register=st[1], immediate=st[2], width=st[3], address=address))
    return hits


def check_image(data):
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('entire image size/SHA-256 mismatch')


def report(data):
    check_image(data)
    hits = scan(data)
    known = [0xa874, 0xa8bc, 0xa8e0, 0xa910]
    return {'image_sha256': SHA256, 'image_size': SIZE, 'base': BASE,
            'end_exclusive': BASE + SIZE, 'halfword_start_first': BASE,
            'halfword_start_last': BASE + SIZE - 2,
            'known_store_sites_present': {hex(x): any(h['store'] == x for h in hits) for x in known},
            'candidates': hits, 'local_scan_complete': True, 'global_writer_complete': False}


if __name__ == '__main__':
    print(json.dumps(report(IMAGE.read_bytes()), indent=2))
