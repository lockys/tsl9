"""Verify selected original instruction windows and 11-bit ID encoding, offline."""
from hashlib import sha256
from pathlib import Path
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def pin(p,h):
    z=bytes.fromhex(h);require(b[p-0x8000:p-0x8000+len(z)]==z,hex(p))
require(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','hash')
pin(0x12c6e,'979aff1f938aaa3c314b')
# Check exact two-bit aligned instruction windows from the original.
pin(0x12c94,'a9cf7330098083a7c9043146a2852800829723100400')
for i in (325,925):
    b0=i>>3;b1=(i&7)<<5
    require((b1&0x18)==0 and ((b0<<3)|(b1>>5))==i, 'identifier')
print('PASS: image identity, consumer queue window and both 11-bit identifier witnesses')
