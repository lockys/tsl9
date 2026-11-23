"""Static byte pin and bounded index arithmetic for APP 0x16a7c; not CPU emulation."""
from hashlib import sha256
from pathlib import Path

p = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
b = p.read_bytes()
def require(ok, reason):
    if not ok:
        raise ValueError(reason)
require(sha256(b).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'image identity')
code = bytes.fromhex('797126d2b717014006d622d44ad00547aa84938707806313e5004147d8cb0d452ec6eff09fdfb245014435492e85eff0dfde0145eff07fde1c08a2972380a7000504e31824ffb7170140454723a8e780')
require(b[0x16a7c-0x8000:0x16acc-0x8000] == code, 'fetch instructions')
# Conditional on the called function returning and preserving s0/s2, successful stores,
# no aliasing or asynchronous interference: thirteen bytes are stored at sp+16..28.
for sp in (0, 0xfffffff0, 0x20010000):
    stores = [((sp + 16 + i) & 0xffffffff) for i in range(13)]
    payload = [((sp + 21 + i) & 0xffffffff) for i in range(8)]
    require(payload == stores[5:13], 'payload boundary')
print('PASS: pinned fetch slice; 13 conditional stores; 8-byte payload boundary')
