"""Pin two allowed TX completion paths without executing the target."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
items=(
 (root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',0x8b14),
 (root/'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin',0x8b2e),
)
def read(item):
    path,pc=item
    if path.stat().st_size!=76800: raise ValueError('unexpected image size')
    with path.open('rb') as f:
        f.seek(pc-0x8000)
        b=f.read(62)
    if len(b)!=62: raise ValueError('short TX tail')
    return b
a,b=map(read,items)
if a[:10]!=b[:10] or a[14:38]!=b[14:38] or a[44:]!=b[44:]:
    raise ValueError('matching tail portions changed')
if a[10:14]!=bytes.fromhex('b307f602') or b[10:14]!=bytes.fromhex('b387c702'):
    raise ValueError('multiply instructions changed')
if a[38:44]!=bytes.fromhex('93874109 3e96') or b[38:44]!=bytes.fromhex('0e96 13064609'):
    raise ValueError('GP-relative address arithmetic changed')
if a[-18:]!=bytes.fromhex('6244 b7070400 03a30705 03450600 0561 0283'):
    raise ValueError('restore and indirect tail changed')
print(json.dumps({'original_tail':'[0x8b14,0x8b52)',
 'candidate_tail':'[0x8b2e,0x8b6c)','differing_groups':2,
 'common_indirect_slot':'0x40050','address_expression':'(4*a2_before + gp + 148) mod 2^32',
 'scope':'normal execution with matching inputs and memory; exceptions and alternate entries unverified',
 'excluded_app_read':False,'target_executed':False}))
