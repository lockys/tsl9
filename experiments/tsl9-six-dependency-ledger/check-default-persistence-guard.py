"""Check allowed instruction windows and byte-guard arithmetic only."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x13138, 0x32, '486e5cb5e4babb89d8b7cc96f32f7d3ab63c8fd4e5b904c0539e1972e531da9e'),
    (0x131a0, 0x16, '71be2c768196e96db7812aca79d39465c76a681f8dbaa85e6f9d8971d3406166'),
    (0x131c2, 0x48, 'c63fb92e9c5703770f5790d2de48f9afd11f7f8be04403581e96a2d413bf547c'),
    (0x132fc, 8, '6cfb4f74c64460502033c91553b9db3a92601360be4174b8071b933c4e59ee8a'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded code or data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
accepted = [byte for byte in range(256) if ((byte - 32) & 255) <= 94]
if accepted != list(range(32, 127)) or len(accepted) ** 4 != 81450625:
    raise SystemExit('Guard arithmetic changed')
print('Four-byte conditional guard verified; excluded data not read; target not executed.')
