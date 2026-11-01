"""Compare only the allowed 1 KiB TX page; never read excluded APP ranges."""
from hashlib import sha256
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
official = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
candidate = root / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
image_base, page, page_size = 0x8000, 2, 1024
start = image_base + page * page_size
end = start + page_size
excluded = ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))
assert all(end <= lo or start >= hi for lo, hi in excluded)
def read_page(path):
    if path.stat().st_size != 76800:
        raise ValueError('Image size changed')
    with path.open('rb') as f:
        f.seek(page * page_size)
        data = f.read(page_size)
    if len(data) != page_size:
        raise ValueError('Short page')
    return data
a,b = read_page(official),read_page(candidate)
changed = [i for i,(x,y) in enumerate(zip(a,b)) if x != y]
if len(changed) != 93 or (start + min(changed),start + max(changed)) != (0x8a7f,0x8b6b):
    raise ValueError('Reviewed TX page changed')
if not all(0x8a56 <= start+i < 0x8b6e for i in changed):
    raise ValueError('Page differences extend beyond reviewed TX')
print(json.dumps({'page_index':page,'page_range':[hex(start),hex(end)],'changed_bytes':len(changed),
 'official_page_sha256':sha256(a).hexdigest(),'candidate_page_sha256':sha256(b).hexdigest(),
 'other_pages_read':False,'target_executed':False}))
