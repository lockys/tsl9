"""Verify bounded instruction/data windows and a 12-bit arithmetic guard."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0xa114, 0x58): 'b750b488b310fb5ef9094907b983be0392d8ae1c3506b600bfd9afdaf92661c9',
    (0x1ab48, 8): 'f39e341bab92c73ab8a2f7c9afcc543cd2f982d599ca715de8ed738d67912dd8',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original instruction or data window changed')
        if address == 0x1ab48:
            values = tuple(int.from_bytes(data[i:i + 2], 'little') for i in range(0, 8, 2))
accepted = [value for value in range(4096) if ((value - 1961) & 0xffff) <= 178]
if accepted != list(range(1961, 2140)):
    raise SystemExit('Unexpected input guard')
if values != (0x0096, 0x00b4, 0xff6a, 0xff4c):
    raise SystemExit('Unexpected conditional counter data')
outputs = [((value + 0x802) & 0xfff) for value in values] + [1960, 2140]
if outputs != [2200, 2230, 1900, 1870, 1960, 2140] or any(v in accepted for v in outputs):
    raise SystemExit('Unexpected conditional output relationship')
center = 0x802
if (accepted[0] - center, accepted[-1] - center) != (-89, 89):
    raise SystemExit('Unexpected input window symmetry')
if [value - center for value in outputs] != [150, 180, -150, -180, -90, 90]:
    raise SystemExit('Unexpected output symmetry')
print('Counter input guard and conditional values verified; target not executed.')
