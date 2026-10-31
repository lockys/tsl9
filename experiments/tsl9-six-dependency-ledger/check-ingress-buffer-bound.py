"""Verify fixed instruction windows and RAM interval arithmetic offline."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    0x89fa: '03d6a1081307f0406365c70413071600420741832395e10897360020938666fcb2962380f600',
    0x186de: '138501089745ff1f938565276377b500232005001105e36db5fe',
}
with image.open('rb') as stream:
    for address, hex_bytes in windows.items():
        expected = bytes.fromhex(hex_bytes)
        stream.seek(address - 0x8000)
        if stream.read(len(expected)) != expected:
            raise SystemExit('Pinned instruction window changed')

start, end = 0x2000b9d8, 0x2000b9d8 + 1040
zero_start, zero_end = 0x20004080, 0x2000c958
if not (zero_start <= start < end <= zero_end and end == 0x2000bde8):
    raise SystemExit('Unexpected buffer/reset intersection')
for offset, width in [(138, 2), (142, 2), (156, 1), (165, 1)]:
    field = 0x20004000 + offset
    if not zero_start <= field < field + width <= zero_end:
        raise SystemExit('Parser field outside reset range')
if not (0x20008000 < start and end <= 0x2000c000 and zero_end > 0x2000c000):
    raise SystemExit('Unexpected candidate RAM bounds')
print('Ingress store and reset/RAM bounds verified; target not executed.')
