"""Verify bounded instruction windows and arithmetic for upstream code 64."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0xb6a8, 0x14, '66c6dc51c552aed142987e4c48cf4016e56d048be234666d58fdd5c211c2cc2d'),
    (0xe288, 0x18, '79d42b6b9bcfe9612c296fa08e0c9aaea2429950378fe058d6abd7cf6d595a09'),
    (0xe380, 0xc, 'bcf164c65328cf251543e55384e06fe376c86fd792902a581f3789a8b810dde5'),
    (0xe3be, 0x10, '9248ab90aafe925788aa96d2bc90cdb7bd0cf486065c457f4fb655d6f8b4b23a'),
    (0xe3de, 0x12, '92a04154d38747f53380940ebeedf773b6975d5e4e62f5b69054f25038a95658'),
    (0xe2bc, 0x26, 'b19a7ac835e1de0b7ee063712f0645c33230c4ffaa9587817bb64c765497c8f5'),
    (0xe506, 0x32, 'fc81295a3a45b0503ad842c2681610af662760fc83d2ca11fc3d81e29a6b7d5a'),
    (0xe532, 0x12, '8941b9c9905a0cfcdb95efb319d4b9c911a5528239b696dcc134cdc06f21930c'),
    (0xe642, 0x18, 'a715df1d049d13f2351ae5f94310fb2169a605a9acdff8ac3bd2e635b77bd021'),
    (0xbd00, 0xa, '59abb1cd0261c104f732e89f4ce469c3fb994d94cc84b76013e99d731e24007f'),
    (0xda36, 0x1c, '91de10ef7a89b6a88646d9796b54f455f07e75fe12e8db71d280e755f18bae06'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
if not ((1 << (64 - 35)) & 0x76000000):
    raise SystemExit('Code 64 bitmask path changed')
if 0xb6a8 + 0x20001000 - 1140 != 0x2000c234 or 0xbd00 + 0x20000000 + 509 != 0x2000befd:
    raise SystemExit('PC-relative address arithmetic changed')
if 0x20004000 + 263 != 0x20004107:
    raise SystemExit('GP-relative address arithmetic changed')
print('Conditional code-64 windows and addresses verified; target not executed.')
