"""Check candidate GATT ABI and bounded APP evidence without target execution."""
import argparse
import hashlib
import re
import struct
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--header', type=Path, required=True, help='Local WCH V1.30 wchble_rom.h')
args = parser.parse_args()
header = args.header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate WCH V1.30 header changed')
text = re.sub(r'\s+', ' ', header.decode('latin-1'))
if not re.search(r'pfnGATTWriteAttrCB_t\)\( uint16_t connHandle, gattAttribute_t \*pAttr, uint8_t \*pValue, uint16_t len, uint16_t offset, uint8_t method \)', text):
    raise SystemExit('Write callback declaration changed')
if not re.search(r'pfnGATTReadAttrCB_t pfnReadAttrCB;.*?pfnGATTWriteAttrCB_t pfnWriteAttrCB;.*?pfnGATTAuthorizeAttrCB_t pfnAuthorizeAttrCB;', text):
    raise SystemExit('Callback table field order changed')
if not re.search(r'uint16_t handle;.*?uint16_t len;.*?uint8_t \*pValue;.*?0 to ATT_MTU_SIZE-3.*?\} attWriteReq_t;', text):
    raise SystemExit('Candidate ATT write value declaration changed')
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {(0x19dfc, 12): 'fee8f4a9372c367610e10a834bbcec4780c23ed1123eea2576deeba414340604',
           (0x88e4, 0x7e): 'b541098af332377c84924b48fd98b48bfbde889083b951f281d5e3f470f6901a',
           (0x8962, 0xea): '2e615c2aee14dbc3e3b33d5420d3389b2987b054ba68e52c70eddfe93e6e34c7'}
raw = {}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original evidence window changed')
        raw[address] = data
if struct.unpack('<III', raw[0x19dfc]) != (0, 0x888c, 0):
    raise SystemExit('Callback pointer table changed')
word = int.from_bytes(raw[0x88e4][0x893e-0x88e4:0x8942-0x88e4], 'little')
offset = ((word >> 31) & 1) << 12 | ((word >> 7) & 1) << 11 | ((word >> 25) & 63) << 5 | ((word >> 8) & 15) << 1
if offset & 0x1000:
    offset -= 0x2000
if (word & 0x7f, (word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31, 0x893e + offset) != (0x63, 6, 15, 18, 0x8962):
    raise SystemExit('Expected unsigned loop branch changed')
if 2 + 1 + 2 + 1040 + 1 != 1046 or (1046 + 244 - 1) // 244 != 5 or 244 - 6 != 238:
    raise SystemExit('Conditional ATT frame-size arithmetic changed')
print('Candidate GATT callback and bounded loop evidence verified; target not executed.')
