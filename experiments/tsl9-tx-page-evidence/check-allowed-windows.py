"""Compare explicit allowed APP ranges; never read either excluded range."""
from hashlib import sha256
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
official = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
candidate = root / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
windows = (
    (0x8000, 0x14056, 'a72dadc0b92a6e282740a5e094188ba96d50213501c6d7c3a9981d482154dabc', 'e413ffe8b89b71c00697465aa8148e38206c55bfd9bd57f55737516201ece449'),
    (0x14c8a, 0x1a69c, 'a0973b4ca22c95f369a10dbdaf787dd1911176ca16ba14de8ceb3a39f01fa412', 'a0973b4ca22c95f369a10dbdaf787dd1911176ca16ba14de8ceb3a39f01fa412'),
    (0x1a6a0, 0x1ac00, 'c6dbc0aa42789a01b0fd27ad69a8c5cfa9d88633c1b0169826cb30d90b56e31e', 'c6dbc0aa42789a01b0fd27ad69a8c5cfa9d88633c1b0169826cb30d90b56e31e'),
)
excluded = ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))
if any(path.stat().st_size != 76800 for path in (official, candidate)):
    raise ValueError('Unexpected image size')
diffs = []
with official.open('rb') as source, candidate.open('rb') as target:
    for lo, hi, source_hash, target_hash in windows:
        if not 0x8000 <= lo < hi <= 0x1ac00 or any(not (hi <= x or lo >= y) for x, y in excluded):
            raise ValueError('Invalid or excluded window')
        source.seek(lo - 0x8000)
        target.seek(lo - 0x8000)
        a, b = source.read(hi - lo), target.read(hi - lo)
        if len(a) != hi - lo or len(b) != hi - lo or sha256(a).hexdigest() != source_hash or sha256(b).hexdigest() != target_hash:
            raise ValueError('Reviewed allowed window differs')
        diffs.extend(lo + i for i, (x, y) in enumerate(zip(a, b)) if x != y)
if len(diffs) != 93 or (min(diffs), max(diffs)) != (0x8a7f, 0x8b6b) or any(not 0x8a56 <= x < 0x8b6e for x in diffs):
    raise ValueError('Unexpected allowed-region differences')
print(json.dumps({'allowed_bytes_per_image': sum(hi-lo for lo, hi, _, _ in windows), 'different_bytes': len(diffs), 'differences_within_tx': True, 'excluded_bytes_read': False, 'full_image_equality_proved': False, 'hardware_tested': False}))
