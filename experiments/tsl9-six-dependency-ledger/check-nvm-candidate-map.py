"""Compare candidate HEX record coverage and header ranges without device access."""
import argparse
import hashlib
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--header', type=Path, required=True)
parser.add_argument('--v131', type=Path, required=True)
parser.add_argument('--v140', type=Path, required=True)
args = parser.parse_args()
header = args.header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate WCH header changed')
for name, value in (('LIB_FLASH_BASE_ADDRESSS', '0x00040000'), ('LIB_FLASH_MAX_SIZE', '0x00040000')):
    if not re.search(rb'#define\s+' + name.encode() + rb'\s+' + value.encode() + rb'\b', header):
        raise SystemExit('Candidate header macro changed')
if not re.search(rb'CODE:\s+00040000H\s+-\s+0006FFFFH\s+192K', header):
    raise SystemExit('Candidate header CODE comment changed')
if (0x08077500 - 0x08000000, 0x08077b00 - 0x08000000) != (0x77500, 0x77b00):
    raise SystemExit('Conditional address arithmetic changed')
if not (0x40000 <= 0x77500 < 0x77b00 <= 0x40000 + 0x40000):
    raise SystemExit('Macro range arithmetic changed')
cases = ((args.v131, '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5', 0x6eb2c),
         (args.v140, '5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23', 0x6ed20))
for path, expected_hash, expected_end in cases:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise SystemExit('Candidate HEX digest changed')
    upper = 0
    max_end = 0
    coverage = 0
    eof = False
    for line in raw.splitlines():
        if eof or not line.startswith(b':'):
            raise SystemExit('Invalid HEX record ordering')
        record = bytes.fromhex(line[1:].decode('ascii'))
        if len(record) < 5 or len(record) != record[0] + 5 or sum(record) & 0xff:
            raise SystemExit('Invalid HEX record length or checksum')
        size, address, kind = record[0], int.from_bytes(record[1:3], 'big'), record[3]
        data = record[4:4 + size]
        if kind == 0 and size:
            start, end = upper + address, upper + address + size
            max_end = max(max_end, end)
            coverage += max(0, min(end, 0x77b00) - max(start, 0x77500))
        elif kind in (2, 4):
            if size != 2:
                raise SystemExit('Invalid HEX address record')
            upper = int.from_bytes(data, 'big') << (4 if kind == 2 else 16)
        elif kind == 1:
            if size:
                raise SystemExit('Invalid HEX end record')
            eof = True
        elif kind not in (0, 3, 5):
            raise SystemExit('Unsupported HEX record type')
    if not eof or max_end != expected_end or coverage:
        raise SystemExit('Candidate HEX record coverage changed')
print('Candidate header ranges and two HEX coverage maps verified; device mapping unverified.')
