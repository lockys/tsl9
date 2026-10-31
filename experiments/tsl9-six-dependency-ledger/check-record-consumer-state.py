"""Verify bounded record consumer windows and field arithmetic."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0xfba2, 0xbe, 'e5b89fbf4fc07a53af8533180d262ae3247010875f0544b029812378f256e2a9'),
    (0xfc90, 0x4a, '165d22f59812925322a4a90cb316a655b84b8de0992273ddab1af0f64f1d28eb'),
    (0xfd3e, 0x20, 'ab35aae6d6348937ac4e913868e37a3d67a062ba805dcaaa5697ebb5c88aaf9e'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
for byte in range(256):
    set_bits = (byte & 0xf3) | 4
    clear_bits = byte & 0xf3
    next_high = ((byte & 0xf0) + 0x10 | (byte & 0x0f)) & 0xff
    if set_bits & 0x0c != 4 or clear_bits & 0x0c or next_high & 15 != byte & 15:
        raise SystemExit('Record field arithmetic changed')
if (20 * 1000) // 625 != 32:
    raise SystemExit('Candidate tick arithmetic changed')
print('Conditional record-consumer windows and arithmetic verified; target not executed.')
