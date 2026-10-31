"""Compare observed APP coordinates with the documented WCH example, offline."""
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
with image.open('rb') as f:
    f.seek(0x186aa - 0x8000)
    if hashlib.sha256(f.read(0x8a)).hexdigest() != '9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d':
        raise SystemExit('Original reset instruction window changed')
if image.stat().st_size != 76800: raise SystemExit('APP image length changed')
app = (0x8000, 0x8000 + image.stat().st_size)
example_flash_end = 64 * 1024
example_ram_end = 0x20000000 + 20 * 1024
zero_end = 0x2000c958; pool_end = 0x2000b18c; initial_sp = 0x20010000
if app != (0x8000, 0x1ac00) or app[1] - example_flash_end != 44032:
    raise SystemExit('Example FLASH comparison changed')
if (zero_end - example_ram_end, pool_end - example_ram_end, initial_sp - example_ram_end) != (31064, 24972, 45056):
    raise SystemExit('Example RAM comparison changed')
if initial_sp != 0x20000000 + 64 * 1024 or not (0x20000000 <= initial_sp - 16 < initial_sp):
    raise SystemExit('Candidate 64K stack-top relationship changed')
print('WCH example memory geometry checked; physical configuration and linkability unverified.')
