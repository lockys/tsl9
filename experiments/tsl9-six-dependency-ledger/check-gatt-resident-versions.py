"""Check selected jump-table and version bytes in two candidate Intel HEX files."""
import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--v131', type=Path, required=True)
parser.add_argument('--v140', type=Path, required=True)
args = parser.parse_args()
CASES = (
    (args.v131, '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5', 0x6e6a0, b'CH32V20x_BLE_LIB_V1.31\0', 0x4cf22),
    (args.v140, '5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23', 0x6e890, b'CH32V20x_BLE_LIB_V1.40\0', 0x4cfba),
)
for path, expected_sha, version_ptr, version, slot in CASES:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise SystemExit('Candidate HEX digest changed')
    selected = set(range(0x40034, 0x40038)) | set(range(0x40130, 0x40134)) | set(range(version_ptr, version_ptr + len(version)))
    found = {}
    upper = 0
    eof = False
    for line in raw.splitlines():
        if eof or not line.startswith(b':'):
            raise SystemExit('Invalid HEX record ordering')
        record = bytes.fromhex(line[1:].decode('ascii'))
        if len(record) < 5 or len(record) != record[0] + 5 or sum(record) & 0xff:
            raise SystemExit('Invalid HEX record length or checksum')
        size, address, kind = record[0], int.from_bytes(record[1:3], 'big'), record[3]
        data = record[4:4 + size]
        if kind == 0:
            for i, value in enumerate(data):
                location = upper + address + i
                if location in selected:
                    if location in found:
                        raise SystemExit('Overlapping selected HEX data')
                    found[location] = value
        elif kind in (2, 4):
            if size != 2:
                raise SystemExit('Invalid HEX address record')
            upper = int.from_bytes(data, 'big') << (4 if kind == 2 else 16)
        elif kind == 1:
            if size != 0:
                raise SystemExit('Invalid HEX end record')
            eof = True
        elif kind not in (3, 5):
            raise SystemExit('Unsupported HEX record type')
    if not eof or set(found) != selected:
        raise SystemExit('Incomplete selected HEX data')
    def read(address, size):
        return bytes(found[address + i] for i in range(size))
    if int.from_bytes(read(0x40034, 4), 'little') != version_ptr or read(version_ptr, len(version)) != version:
        raise SystemExit('Candidate version pointer or string changed')
    if int.from_bytes(read(0x40130, 4), 'little') != slot:
        raise SystemExit('Candidate registration slot changed')
print('Two candidate resident versions and registration slots verified; installed device unverified.')
