"""Check bounded instruction windows and arithmetic; never execute target code."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    0x81b0: 'b7070400fc5f411106c68297a9473305f502b240410111818280',
    0xe1cc: 'ef905ffe938701119c431307f07c2a84b307f5406379f700',
}
with image.open('rb') as stream:
    for address, expected_hex in windows.items():
        expected = bytes.fromhex(expected_hex)
        stream.seek(address - 0x8000)
        if stream.read(len(expected)) != expected:
            raise SystemExit('Pinned instruction window changed')

modulus = 1 << 32
def f(value):
    return ((value * 10) % modulus) >> 4

for k in range(1, 10):
    boundary = (k * modulus + 9) // 10
    before, after = f(boundary - 1), f(boundary)
    if (before, after, (after - before) % modulus) != (268435455, 0, 4026531841):
        raise SystemExit('Unexpected multiplication boundary')
# 10 * 2^31 == 5 * 2^32 establishes repetition for every 32-bit input.
if 10 * (1 << 31) != 5 * modulus:
    raise SystemExit('Period identity failed')
print('Instruction windows and nine arithmetic boundaries verified; target not executed.')
