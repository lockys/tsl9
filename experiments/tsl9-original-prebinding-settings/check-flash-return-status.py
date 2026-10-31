"""Verify bounded original settings writer and FLASH transaction windows."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x9c0a, 0x40): 'd30c3f9e7f6a4e4b13a2f845bf9f84c9a31afca152309a1607eb2589dd4245d5',
    (0x18e90, 0xc6): 'fc815702f69e9182069b3e07309ef703671ca796a0201029549e4b27a89e3d41',
    (0x13138, 0x32): '486e5cb5e4babb89d8b7cc96f32f7d3ab63c8fd4e5b904c0539e1972e531da9e',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original FLASH instruction window changed')
if (0x08077a00 & ~0xff) != 0x08077a00:
    raise SystemExit('Unexpected address alignment')
print('FLASH transaction instruction windows verified; target not executed.')
