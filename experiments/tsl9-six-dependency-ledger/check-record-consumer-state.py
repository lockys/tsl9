"""Verify bounded record consumer windows and field arithmetic."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x82a8, 0x2c, 'ccc429b7070700aac8d5f1cbb6a1777b201f4284ce1aba424673bd30c5d728d0'),
    (0xfba2, 0xbe, 'e5b89fbf4fc07a53af8533180d262ae3247010875f0544b029812378f256e2a9'),
    (0xfc90, 0x4a, '165d22f59812925322a4a90cb316a655b84b8de0992273ddab1af0f64f1d28eb'),
    (0xfcb8, 0x62, '5257d0c8665b1b590cc4b7b9a7a4944af8f1cee6d4b72609eca11b3e523431db'),
    (0xfd1a, 0x24, '6ebce66829bf49f9b6748383fdeac1e79e189737c9e03af46de0e61b4abbd8b7'),
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
if 0x82b6 + 0x20004000 - 254 + 12 * 13 != 0x2000c254 or 7 + 2 != 9:
    raise SystemExit('Record source or checksum overlap changed')
print('Conditional record-consumer windows and arithmetic verified; target not executed.')
