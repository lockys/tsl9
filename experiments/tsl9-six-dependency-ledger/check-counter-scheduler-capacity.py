"""Pin bounded scheduler and callback instruction evidence offline."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x901a, 0x60): '1ca1876ac3f3458d2a170336f9d1598ee7dd62f359f802ceae6739d04fda437f',
    (0x907a, 0x36): '901ef49b5e03e522d166f5ea11ae041f799b6733971e69ad6fc8fb252c6923f8',
    (0x9124, 0x12c): '45dd01a76fedc4bd8d01fdb7ff005f410166a68f171d52420d19da2cbba2e992',
    (0xa2ee, 0x8e): '1e3ba5cad99891ddf478123a9015736168e7bdad51c01abbed0cda7e4d043480',
    (0x9f74, 6): '551e0bd058e88a00ef29c2d561808a758ace0ff36fdb09af56e8a915ccdd31e8',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
print('Scheduler capacity windows verified; target execution unverified.')
