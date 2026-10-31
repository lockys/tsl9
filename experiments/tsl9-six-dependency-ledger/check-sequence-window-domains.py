"""Classify numerical comparison windows without reading excluded bytes."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
with image.open('rb') as stream:
    stream.seek(0x12032 - 0x8000)
    if hashlib.sha256(stream.read(0x30)).hexdigest() != 'e53c95dcfde7f6ae8bcdfbb73c5515a534fd0436f277e0279f41ec54781ae6c9':
        raise SystemExit('Original sequence instruction window changed')
if 0x8000 + image.stat().st_size != 0x1ac00:
    raise SystemExit('Original APP numerical end changed')
excluded = range(0x1a69c, 0x1a6a0)
total_excluded = total_beyond = 0
for channel in range(4):
    overlaps = []
    beyond = []
    for state in range(256):
        start = 0x1a638 + 6 * (2 * channel + state)
        end = start + 6
        if start < excluded.stop and excluded.start < end:
            overlaps.append(state)
        if end > 0x1ac00:
            beyond.append(state)
    if overlaps != [16 - 2 * channel, 17 - 2 * channel]:
        raise SystemExit('Excluded-range overlap classification changed')
    if beyond != list(range(246 - 2 * channel, 256)):
        raise SystemExit('APP-end classification changed')
    total_excluded += len(overlaps)
    total_beyond += len(beyond)
if (total_excluded, total_beyond) != (8, 52):
    raise SystemExit('Classification totals changed')
print('Sequence window domains verified; excluded bytes and target not read or executed.')
