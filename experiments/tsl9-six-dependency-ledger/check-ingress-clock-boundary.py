"""Check bounded parser/clock evidence and arithmetic without target execution."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x88e4, 0x54): '17eb10efadd7beb6cc66cf95ee83136f3c9235f080ff0004cf5aff2ce6800ccd',
    (0x81b0, 0x1a): 'f03a9478d6361df881745068e9c322098ea7317e3bb4d1be5f62f97ff7e4c239',
    (0x8962, 0xf0): '89feb5dfd5228799d8cb19b2ac3a4dcb71555df6ea87ed1cb3d04e1c252f2c8b',
}
raw = {}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
        raw[address] = data
word = int.from_bytes(raw[0x88e4][0x8916-0x88e4:0x891a-0x88e4], 'little')
offset = ((word >> 31) & 1) << 12 | ((word >> 7) & 1) << 11 | ((word >> 25) & 63) << 5 | ((word >> 8) & 15) << 1
if offset & 0x1000:
    offset -= 0x2000
if (word & 0x7f, (word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31, 0x8916 + offset) != (0x63, 7, 14, 15, 0x891e):
    raise SystemExit('Expected unsigned threshold branch changed')
def clock(x):
    return ((x * 10) & 0xffffffff) >> 4
for k in range(1, 10):
    boundary = (k * (1 << 32) + 9) // 10
    previous, current = clock(boundary - 1), clock(boundary)
    delta = (current - previous) & 0xffffffff
    if (previous, current, delta) != (268435455, 0, 4026531841) or delta <= 299:
        raise SystemExit('Clock boundary arithmetic changed')
print('Ingress clock windows and nine boundaries verified; target not executed.')
