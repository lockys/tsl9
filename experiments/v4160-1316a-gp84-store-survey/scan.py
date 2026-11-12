"""Raw 2-byte-aligned standard GP-base stores overlapping GP+[84,88)."""
import hashlib
import json
from pathlib import Path

BASE = 0x8000
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


def candidates(data):
    hits = []
    for offset in range(0, len(data) - 3, 2):
        raw = data[offset:offset + 4]
        word = int.from_bytes(raw, 'little')
        funct3 = (word >> 12) & 7
        if word & 0x7f != 0x23 or (word >> 15) & 31 != 3 or funct3 not in (0, 1, 2):
            continue
        immediate = (((word >> 25) & 0x7f) << 5) | ((word >> 7) & 31)
        immediate = (immediate ^ 0x800) - 0x800
        width = 1 << funct3
        if immediate < 88 and immediate + width > 84:
            hits.append({'pc': BASE + offset, 'file_offset': offset, 'bytes': raw.hex(' '),
                         'instruction': ('sb', 'sh', 'sw')[funct3],
                         'source_register': (word >> 20) & 31,
                         'immediate': immediate, 'width': width})
    return hits


def report(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('firmware identity mismatch')
    return {'image_sha256': SHA256, 'base': BASE, 'end_exclusive': BASE + len(data),
            'target_gp_offsets': [84, 88], 'candidates': candidates(data),
            'global_writers_complete': False}


if __name__ == '__main__':
    print(json.dumps(report(IMAGE.read_bytes()), indent=2))
