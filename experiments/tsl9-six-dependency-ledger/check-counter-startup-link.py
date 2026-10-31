"""Pin main-to-counter initialization and the two known counter updates."""
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x9268, 0x20, 'db9d51b9f6a92cc56ac394893cef48705bbc1eaf0ba6c9cdc4e49e66e6e1498c'), (0x154a6, 0x20, '392d4ae3f3b01ba15481d90deb7601ae8d2e8d0769844c2ebe96be9594075645'), (0xa37c, 0x12, 'd6ecb512dbb8f33c2e5d509024ff7e147fd3be89e1afb882d9b61c9760add961'), (0xa0e2, 0x1c, 'cba0f680cafd8c838947df3691e60e032d00c00dbaaaf3a5055bf622a6a316e1'), (0xa33a, 0x12, 'c5fcfa58b93c6d52f40d3f7ba52aa53430ed279c7583ebd6c5a5394ec3ee9689'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056 or address + size > 0x1a69c:
            raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
if not (172 <= 176 < 172 + 5 and all(((x + 1) & 3) < 4 for x in range(256))):
    raise SystemExit('Counter range arithmetic changed')
print('Main-to-counter startup windows and masked update bound verified; target not executed.')
