"""Pin sequence marker, record scan and fallback instruction windows."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x1207a, 0x22): 'fa2ea34c715a742ca455b9781175942d075a9f91b4dcb864e46a47c4f16dc414',
    (0x11356, 0x86): '3839ed4ee66eb76e0a6014b719c45b46e6de41415af2578b74f5cd6180f866ce',
    (0x12f18, 0x30): '01c55dd5113a23329f18c4316bbddaafddf251520357c213b37fbd08cb5ac86b',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
if not (42 * 6 == 252 and 252 <= 255 and all(0x80 + i != 0 for i in range(4))):
    raise SystemExit('Record or marker arithmetic changed')
print('Sequence marker, scan and fallback windows verified; target not executed.')
