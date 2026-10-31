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
if image.stat().st_size + 0x8000 != 0x1ac00:
    raise SystemExit('Unexpected APP image end')
inside = [i for i in range(256) if 0x1ab48 + 2 * i + 2 <= 0x1ac00]
if inside != list(range(92)) or 0x1ab48 + 2 * 4 != 0x1ab50:
    raise SystemExit('Unexpected counter-index image boundaries')
inverse = [x for x in range(4096) if ((x + center) & 0xfff) in accepted]
if inverse != list(range(90)) + list(range(4007, 4096)):
    raise SystemExit('Unexpected low-12-bit inverse guard')
if sum(1 for x in range(65536) if ((x + center) & 0xfff) in accepted) != 2864:
    raise SystemExit('Unexpected halfword inverse guard count')
print('Counter input guard and conditional values verified; target not executed.')
