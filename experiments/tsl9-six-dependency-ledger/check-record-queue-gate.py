"""Pin the queue precheck and its two-entry scan."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x82d2, 0xbc, '7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30'),
    (0x12ca6, 0x1c, 'f87f1cdf41fca0ef1272ef68d89b916072a09d24e957d4245bd4052ebaf2e5b9'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
if 0x82f2 + 0x20004000 + 1186 != 0x2000c794:
    raise SystemExit('Two-entry base address changed')
print('Queue precheck windows and base verified; target not executed.')
