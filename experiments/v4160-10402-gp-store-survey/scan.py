"""Raw RV32I x3-base stores overlapping GP+0x50..0x51; not a CFG."""
import hashlib
import json
from pathlib import Path

BASE = 0x8000
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


def candidates(data):
    found = []
    for offset in range(0, len(data) - 3, 2):
        word = int.from_bytes(data[offset:offset + 4], 'little')
        f = (word >> 12) & 7
        if word & 0x7f != 0x23 or (word >> 15) & 31 != 3 or f not in (0, 1, 2):
            continue
        imm = ((word >> 25) << 5) | ((word >> 7) & 31)
        imm = (imm ^ 0x800) - 0x800
        size = 1 << f
        if imm <= 0x51 and imm + size - 1 >= 0x50:
            found.append({'pc': BASE + offset, 'bytes': data[offset:offset + 4].hex(),
                          'source_register': (word >> 20) & 31, 'offset': imm, 'width': size})
    return found


def report(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('firmware identity mismatch')
    return {'image_sha256': SHA256, 'base': BASE, 'end_exclusive': BASE + len(data),
            'candidates': candidates(data), 'global_writers_complete': False}


if __name__ == '__main__':
    print(json.dumps(report(IMAGE.read_bytes()), indent=2))
