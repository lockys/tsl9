"""Check bounded candidate SPI input and fixed CAN filter evidence offline."""
import hashlib
import struct
from pathlib import Path
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x16dd4, 0x38, '986860b86812929c691ba1ccd2bd9099bb562ce0df5d74e7cd1e25ed18d6f49a'), (0x14f18, 8, '536595ce0cd6c5662e3ed3569c77edc62713ab317a07e37974450c592dc844ee'), (0x152d0, 12, 'af8d5e0fc04744afb2032edd5d80d7c245ff5ff8cbdf6389dbaec574454ab2c7'), (0x12b82, 0x12, '3b436f0f2de215a5c82eed092b3e2833e39b12e44b59e11a9ad3240578d98961'), (0x16a7c, 0x8e, 'd823c819bbe92c3b7ee17c92411825549084d08dc32c36378d8e60d4915f40e2'), (0x12c86, 0x108, '87e5ac94aebdeed15684f7803a31b0b193278d6de348517c63738b75056bdb8f'), (0x19ca8, 96, '72c4511144ac0693fff827ccfaf986b85b93313446cdf43cced132148f19089a'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056 or address + size > 0x1a69c:
            raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000); data = f.read(size)
        if hashlib.sha256(data).hexdigest() != expected: raise SystemExit('Instruction or table window changed')
        if address == 0x19ca8: ids = struct.unpack('<48H', data)
if 0x370 in ids or struct.unpack('<4H', (0x039b0370).to_bytes(4, 'little') + bytes(4)) != (0x370, 0x39b, 0, 0):
    raise SystemExit('Candidate filter comparison changed')
print('SPI channel 2 and fixed CAN list evidence verified; hardware behavior unverified.')
