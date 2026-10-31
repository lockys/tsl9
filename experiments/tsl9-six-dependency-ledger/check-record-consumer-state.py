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
    (0x14d5e, 0x20, 'ba19ee81649f201a82bc52aa3d8830c23520bcb528bccae729398ba541fe0b80'),
    (0x14ed8, 0x0c, 'f2f2324e7622dc5d4b48689d5488e37addc9ce0adab43b1d76d27f4c35aa4df8'),
    (0x14fa0, 0x18, '2cd614c52428feed12f96051e14abb9d876f36e4c8ae3098afd9239c34e53325'),
    (0x1522e, 0x1e, '4f419ed0549e2f65a49831191e613a0be586be5ef98605f511ccfbeb37d475c2'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if (address < 0x14c8a and address + size > 0x14056) or (address < 0x1a6a0 and address + size > 0x1a69c):
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
if [n for n in range(1, 256) if n + 2 < 12] != list(range(1, 10)):
    raise SystemExit('Checksum output range changed')
print('Conditional record-consumer windows and arithmetic verified; target not executed.')
