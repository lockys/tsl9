"""Check bounded fixed-filter evidence without running target code."""
import hashlib
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x128fe, 0xa0): '0191afe9afa2ecad8b58295c50301bfac35115a1e33140f61c4678b5997dda4e',
    (0x1299e, 0x26): '722428b52f60e85f2d3b40ab39a2be581def68ef8a795977b64b5f9edc3d18fe',
    (0x18ba2, 0x102): 'a7740d7785b0ab0def54148e8d56242da4341de1d4041a0ee7fffceed37338cc',
    (0x12b82, 0x12): '3b436f0f2de215a5c82eed092b3e2833e39b12e44b59e11a9ad3240578d98961',
    (0x19ca8, 96): '72c4511144ac0693fff827ccfaf986b85b93313446cdf43cced132148f19089a',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original evidence window changed')
        if address == 0x19ca8:
            ids = struct.unpack('<48H', data)
if max(ids) > 0x7ff:
    raise SystemExit('Table contains a value outside 11-bit range')
encoded = [(value << 5) & 0xffff for value in ids] + [0] * 8
if len(encoded) != 14 * 4 or any((value << 5) in encoded for value in (0x399, 0x39b)):
    raise SystemExit('Fixed list comparison changed')
print('Fixed filter windows verified; resident contracts and target execution unverified.')
