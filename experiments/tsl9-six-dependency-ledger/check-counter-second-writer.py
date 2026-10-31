"""Check bounded counter-writer evidence without running target code."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0xa2ee, 0x8e): '1e3ba5cad99891ddf478123a9015736168e7bdad51c01abbed0cda7e4d043480',
    (0x81de, 0x10): 'fe6583f69447a91467e981387fde5e03250f7dd9c0c6a9ab25af208a5f464dc0',
    (0x829e, 0xa): '237f5833a80ead32ef214fce5c360966f882b57191ef5e76b99e9c855a243c5e',
    (0x9f74, 0x6): '551e0bd058e88a00ef29c2d561808a758ace0ff36fdb09af56e8a915ccdd31e8',
    (0xa1e2, 0x6): '23940c5fb1e1e35fe5901c98cde41404927846a24a46608979fc95373acb2a7b',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
if [value for value in range(4) if ((value + 1) & 2)] != [1, 2]:
    raise SystemExit('Low-bit condition changed')
print('Counter second-writer windows verified; target execution unverified.')
