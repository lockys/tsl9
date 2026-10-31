"""Check bounded upstream state-machine instruction and table windows."""
import hashlib
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x150be, 0x12, '2edb37492cb3360cf4e45acc8b9015c529f454a779d64e484ee5a94b4dd8fbe7'),
    (0xcec0, 0x1c, '26a2dfa5698bda458204757e5726737792d9c1b304e64cdf45ad03b9cd67d8ed'),
    (0xebac, 0x68, '7a1e65ea317c15000cc33eafc830173ce2bcfe98da525e2d897428f59c9c3960'),
    (0xec22, 2, '0b1bb8fd760a9674b11cfcb0042a49139dd73963ce3cf860b097729c3837bd20'),
    (0xe220, 0x6e, 'e04fdf7feb27e6560faf1b3ead6ec204e2b0bcfc3abb3b678a196907e444633a'),
    (0x1a13c, 4, 'cc842773bbede2ab26963d5ff95d0da20418eee4b6bf2ac124979fdcec5f822a'),
    (0x1a18c, 28, 'c0e2e3bed8ee2dc5214e7982ca624db24601cc7afdd19825bb9f48174847fae5'),
)
data = {}
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056 or address < 0x1a6a0 and address + size > 0x1a69c:
            raise SystemExit('Excluded window')
        f.seek(address - 0x8000)
        raw = f.read(size)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise SystemExit('Instruction or table window changed')
        data[address] = raw
if 0x1a13c + struct.unpack('<i', data[0x1a13c])[0] != 0xe246:
    raise SystemExit('Type-0 table target changed')
if any(0x1a150 + off != 0xe288 for off in struct.unpack('<7i', data[0x1a18c])):
    raise SystemExit('Record value table targets changed')
values = {57 + ((b >> 4) & 7) for b in range(256)}
if values != set(range(57, 65)) or 0xcec4 + 0x1ffff000 + 120 != 0x2000bf3c:
    raise SystemExit('Record argument arithmetic changed')
print('Upstream record state and table targets verified; target not executed.')
