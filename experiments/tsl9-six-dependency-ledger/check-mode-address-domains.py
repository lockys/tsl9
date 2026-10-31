"""Classify numerical mode lookup addresses without reading excluded bytes."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
with image.open('rb') as stream:
    stream.seek(0xcedc - 0x8000)
    if hashlib.sha256(stream.read(0xbc)).hexdigest() != 'e6dd2498940c6d477836f3411ad6e381fc9a485d0eb5d54f300f1c7809e9f27f':
        raise SystemExit('Original mode instruction window changed')
if 0x8000 + image.stat().st_size != 0x1ac00:
    raise SystemExit('Original APP numerical end changed')
excluded = []
beyond = []
for mode in range(256):
    for column in range(16):
        address = 0x1a078 + 16 * mode + column
        if 0x1a69c <= address < 0x1a6a0:
            excluded.append((mode, column))
        if address >= 0x1ac00:
            beyond.append((mode, column))
if excluded != [(98, c) for c in range(4, 8)]:
    raise SystemExit('Excluded-range classification changed')
if beyond != [(184, c) for c in range(8, 16)] + [(m, c) for m in range(185, 256) for c in range(16)]:
    raise SystemExit('APP-end classification changed')
if len(beyond) != 1144:
    raise SystemExit('APP-end total changed')
print('Mode address domains verified; excluded bytes and target not read or executed.')
