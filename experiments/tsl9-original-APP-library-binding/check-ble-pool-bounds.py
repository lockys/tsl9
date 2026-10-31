"""Verify original config windows and bounded BLE/RAM interval arithmetic."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x19a3a, 16): 'a5a8841ffe918d1e61e5b4d1a2862744eb83a522884ad8dfe18592dd9a6c5892',
    (0x19ad2, 32): 'fcd5faa670571cfe6360a8bb5428748f437ee38af7272013882a8dd807275104',
    (0x186de, 26): '53e8753086d6a33d612f27e3f21393ac8c64e9603498c443023275973c3fa5a0',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        if hashlib.sha256(stream.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
start = (0x19a3a + 0x1ffea000 + 1874) & 0xffffffff
end = start + 0x7000
if (start, end) != (0x2000418c, 0x2000b18c):
    raise SystemExit('Unexpected pool address')
if not (0x20004080 <= start < end <= 0x2000c958 and
        0x20004184 <= start and end + 0x84c == 0x2000b9d8 and
        end > 0x20008000 and end <= 0x2000c000):
    raise SystemExit('Unexpected RAM interval relationship')
print('BLE pool instruction windows and RAM bounds verified; target not executed.')
