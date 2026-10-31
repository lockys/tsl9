"""Verify bounded original SPI transfer and status-check windows."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x16896, 72): '654d0f600794c1548c617d0f476ca4f0fa5aaf780f49be7c328b3df69e8878dc',
    (0x16994, 72): '0949ef0357f5c7543bc480b214103d78880ccba36a0551e0cb8cfb1edab2d538',
    (0x16e0c, 124): '25f275f34ebedf790263a15965d0ffbcaaf025ffc8360dfa710b7f06d63daca9',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original SPI instruction window changed')
print('SPI timeout and status instruction windows verified; target not executed.')
