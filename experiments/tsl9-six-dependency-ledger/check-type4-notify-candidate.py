"""Bounded APP windows and candidate WCH declarations; no target execution."""
import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--wch-header', required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x13bd2, 0x7c, 'a6761aae01a3470f01947b1f3c04d88bae8cebc8a6b3382e69f3aeeec8585853'), (0x8a56, 0x78, '12b67bcd39d594240712fd915464d0047fc9a32fc2d7f02923c6a91c83fbdfa4'), (0x8b14, 0x3e, 'aebf41c8da4c992eb96144b63d6f8385a09ff5e058eedc6abe66643fe5b85c11'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056:
            raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Original instruction window changed')
header = args.wch_header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate WCH header changed')
for token in (b'FUNCITON_BASE_ADDRESSS    (LIB_FLASH_BASE_ADDRESSS+0x34)', b'GATT_CLIENT_CFG_NOTIFY          0x0001', b'GATT_CLIENT_CFG_INDICATE        0x0002', b'BLE_LIB_JT(66)', b'GATTServApp_ReadCharCfg', b'BLE_LIB_JT(7)', b'tmos_set_event'):
    if token not in header:
        raise SystemExit('Candidate WCH declaration changed')
if 0x40034 + 66 * 4 != 0x4013c or 0x40034 + 7 * 4 != 0x40050:
    raise SystemExit('Candidate slot arithmetic changed')
print('Type-4 transport and candidate WCH declarations verified; device behavior unverified.')
