"""Pin caller/scheduler evidence and check three conditional arithmetic values."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x172b6, 0x4a): '9567e295d85dee36d242e89c952adf091b12ab5e67486dea7d8c0b0597473ea7',
    (0xa2ee, 0x8e): '1e3ba5cad99891ddf478123a9015736168e7bdad51c01abbed0cda7e4d043480',
    (0x9124, 0x12c): '45dd01a76fedc4bd8d01fdb7ff005f410166a68f171d52420d19da2cbba2e992',
    (0x9f74, 6): '551e0bd058e88a00ef29c2d561808a758ace0ff36fdb09af56e8a915ccdd31e8',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
values = [((x * 1000 & 0xffffffff) * 1000 & 0xffffffff) // 625 for x in (1, 2, 3)]
if values != [1600, 3200, 4800]:
    raise SystemExit('Conversion changed')
print('Counter caller delay windows verified; target execution unverified.')
