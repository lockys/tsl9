"""Pin allowed CAN1 and mode-dispatch evidence without executing target code."""
import hashlib
import struct
from pathlib import Path
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x19ca8, 96, '72c4511144ac0693fff827ccfaf986b85b93313446cdf43cced132148f19089a'), (0x128fe, 0xa0, '0191afe9afa2ecad8b58295c50301bfac35115a1e33140f61c4678b5997dda4e'), (0x12c24, 0x26, 'ae3ab641b76d67a6dab81d3967a671fa6204b64e31d7b11297ba7ef5f27311ac'), (0x18d78, 0x76, '95a507725d76c78b0f1a18a106c3955cb6d746b5be805018292011d31f0ed3a7'), (0x12c86, 0x108, '87e5ac94aebdeed15684f7803a31b0b193278d6de348517c63738b75056bdb8f'), (0x14dce, 8, 'e85df98f564c3ef355552c0d821d2a7782a6e4735fb9a3123a7300541fef5142'), (0x150be, 0x18, '737512952451356bdc1c4a5bb268301dd33057eb67615274bc2d9ade50edfb39'), (0xcec0, 0x1c, '26a2dfa5698bda458204757e5726737792d9c1b304e64cdf45ad03b9cd67d8ed'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056 or address + size > 0x1a69c:
            raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000); data = f.read(size)
        if hashlib.sha256(data).hexdigest() != expected: raise SystemExit('Instruction or table window changed')
        if address == 0x19ca8: ids = struct.unpack('<48H', data)
if [i for i, value in enumerate(ids) if value == 0x229] != [2] or (ids[2] << 5) != 0x4520:
    raise SystemExit('Candidate 0x229 fixed filter location or encoding changed')
print('CAN1 0x229 filter and mode-dispatch windows verified; device behavior unverified.')
