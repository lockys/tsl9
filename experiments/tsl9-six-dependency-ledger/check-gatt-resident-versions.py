"""Check selected jump-table and version bytes in two candidate Intel HEX files."""
import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--v131', type=Path, required=True)
parser.add_argument('--v140', type=Path, required=True)
args = parser.parse_args()
image = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
with image.open('rb') as stream:
    stream.seek(0x1ab1c - 0x8000)
    app_prefix = stream.read(21)
if hashlib.sha256(app_prefix).hexdigest() != 'd7983408b1cfeabbf840e9d03286b5bc9b3a5e948ac60211bc91ada510b48b68':
    raise SystemExit('Original APP version prefix changed')
CASES = (
    (args.v131, '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5', 0x6e6a0, b'CH32V20x_BLE_LIB_V1.31\0', 0x4cf22, 0x402b0, 0x6de0c, '7a0cf58801fabb3dcb9d26fcece3d01b2f41276dacce4130daff0e663559927f', (0x43728, 0x43520, 0x43c4e)),
    (args.v140, '5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23', 0x6e890, b'CH32V20x_BLE_LIB_V1.40\0', 0x4cfba, 0x402f0, 0x6dffc, 'e5a738246f7b39ca8dc057596acaf0040bb6673935fac8015ef1dba8af84c74e', (0x437b4, 0x435ac, 0x43cda)),
)
for path, expected_sha, version_ptr, version, slot, copy_source, loader, loader_hash, flash_slots in CASES:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise SystemExit('Candidate HEX digest changed')
    selected = set(range(0x40034, 0x40038)) | set(range(0x40130, 0x40134)) | set(range(version_ptr, version_ptr + len(version)))
    slot_checks = dict(zip((0x4003c, 0x40048, 0x4004c, 0x40058, 0x4007c, 0x40080), (0x20000442, 0x2000039c, 0x20000332, *flash_slots)))
    bodies = ((0x20000040, 38, 'd97248aeb37504e1b1878588e47ed8bdfa613e66361ef3dc84e310cd77c48cbe'), (0x20000442, 72, 'a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa'), (0x2000039c, 46, 'd67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3'), (0x20000332, 58, '558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'))
    for address in slot_checks:
        selected.update(range(address, address + 4))
    selected.update(range(loader, loader + 0x72))
    for ram, size, _ in bodies:
        source = copy_source + ram - 0x20000040
        selected.update(range(source, source + size))
    second_start, second_size = (0x6eaa4, 140) if copy_source == 0x402b0 else (0x6ec94, 144)
    if copy_source == 0x402b0:
        selected.update(range(0x430e0, 0x430e4))
        selected.update(range(0x6eaa4, 0x6eaa8))
    else:
        selected.update(range(0x4316c, 0x43170))
        selected.update(range(0x6ec94, 0x6ec98))
    second_coverage = set()
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
                if second_start <= location < second_start + second_size:
                    second_coverage.add(location)
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
    expected_coverage = set(range(second_start, second_start + second_size - 4))
    if second_coverage != expected_coverage:
        raise SystemExit('Candidate second-copy source coverage changed')
    def read(address, size):
        return bytes(found[address + i] for i in range(size))
    if copy_source == 0x402b0:
        if read(0x430e0, 4) == read(0x6eaa4, 4):
            raise SystemExit('V1.31 overlapping copy source words unexpectedly equal')
        if not (0x20002e70 + 4 <= 0x20002ef8):
            raise SystemExit('V1.31 overlapping word enters zero range')
    else:
        if read(0x4316c, 4) == read(0x6ec94, 4):
            raise SystemExit('V1.40 overlapping copy source words unexpectedly equal')
        if not (0x20002ebc + 4 <= 0x20002f48):
            raise SystemExit('V1.40 overlapping word enters zero range')
        for offset, expected in ((0x32, '1306c6eb'), (0x52, '130686f4'), (0x56, '9385c5eb'), (0x5a, '130545c9')):
            if read(loader + offset, 4).hex() != expected:
                raise SystemExit('V1.40 loader copy geometry changed')
    if int.from_bytes(read(0x40034, 4), 'little') != version_ptr or read(version_ptr, len(version)) != version:
        raise SystemExit('Candidate version pointer or string changed')
    if (version[:21] == app_prefix) != (version_ptr == 0x6e6a0):
        raise SystemExit('Candidate version-prefix comparison changed')
    if int.from_bytes(read(0x40130, 4), 'little') != slot:
        raise SystemExit('Candidate registration slot changed')
    for address, expected in slot_checks.items():
        if int.from_bytes(read(address, 4), 'little') != expected:
            raise SystemExit('Candidate service slot changed')
    if hashlib.sha256(read(loader, 0x72)).hexdigest() != loader_hash:
        raise SystemExit('Candidate loader window changed')
    if read(loader + 0x2c, 4) != bytes.fromhex('37050400') or read(loader + 0x36, 4) != bytes.fromhex('93850504'):
        raise SystemExit('Candidate loader base instructions changed')
    source_addi = '1305052b' if copy_source == 0x402b0 else '1305052f'
    if read(loader + 0x3a, 4) != bytes.fromhex(source_addi):
        raise SystemExit('Candidate copy-source immediate changed')
    for ram, size, expected in bodies:
        source = copy_source + ram - 0x20000040
        if hashlib.sha256(read(source, size)).hexdigest() != expected:
            raise SystemExit('Candidate copied RAM body changed')
print('Two candidate resident versions and registration slots verified; installed device unverified.')
