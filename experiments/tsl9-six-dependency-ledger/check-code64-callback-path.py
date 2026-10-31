"""Verify permitted callback instruction windows and candidate tick arithmetic."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0xfe1c, 0x30, '7a52ce15dfac5073d934be93f0dac2b6e0d8339a110f12701fbce225fb30ea49'),
    (0xfb1e, 0x40, '4d645277b8d5df69f0b35adf2c092dc5d40a41b9d7d5533f19b8ceafdd6c8746'),
    (0xa9de, 0xa, 'e5f1820771529754ba18fce55414e81dece3414ec6a3f6b94f4782dfcdf2bb3c'),
    (0x91d0, 0x28, '1f605d21c05deea7076cabe8b625907c0fc4820e0fcba9689a9d1dca1487a3df'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
if 0xa9de + 0x20001000 + 1278 != 0x2000bedc:
    raise SystemExit('Status byte address changed')
if [(n * 1000) // 625 for n in (500, 1500)] != [800, 2400]:
    raise SystemExit('Candidate tick arithmetic changed')
print('Conditional callback windows and tick arithmetic verified; target not executed.')
