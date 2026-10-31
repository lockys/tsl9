"""Verify bounded APP registration evidence and pinned WCH header declarations."""
import argparse
import hashlib
import re
import struct
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--wch-header', required=True, type=Path)
a = p.parse_args()
header = a.wch_header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate header changed')
for pattern in (rb'#define\s+GAP_LINK_TERMINATED_EVENT\s+0x06', rb'#define\s+GAPROLE_ADVERTISING\s+2\b', rb'#define\s+GAPROLE_WAITING\s+3\b', rb'GAPRole_PeripheralStartDevice[^\n]+BLE_LIB_JT\(92\)', rb'gapRolesStateNotify_t\s+pfnStateChange', rb'tmos_event_hdr_t\s+hdr;[^\n]*\n\s*uint8_t\s+opcode;[^\n]*\n\s*uint16_t\s+connectionHandle;'):
    if not re.search(pattern, header):
        raise SystemExit('Expected candidate header declaration missing')
for pattern in (rb'#define\s+GAP_LINK_ESTABLISHED_EVENT\s+0x05', rb'#define\s+GAPROLE_CONNECTED\s+4\b', rb'#define\s+GAPROLE_ADVERT_ENABLED\s+0x305', rb'GAPRole_SetParameter[^\n]+BLE_LIB_JT\(80\)', rb'GATT_ExchangeMTU[^\n]+BLE_LIB_JT\(41\)'):
    if not re.search(pattern, header):
        raise SystemExit('Expected candidate GAP or GATT declaration missing')
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x886e, 0x1c, '7c163da0713d3c343537f0192653df521a5198cbb952855a5afd33609c2da176'),
    (0x8b90, 0x16, '6e4414fe0d602ab0827750b095ee16f6f42525b0e169de2f7ae1fcf7142502ee'),
    (0x8b6e, 0x22, '529cb7ed4851439431f1c5427dd7699ed3570a13fd4eb23fa979c0f73726eac3'),
    (0x8c00, 0x18, 'e75d97abf5f328b743771db155caec55e0f9eacbad614711747d535af99e47a5'),
    (0x8f76, 0x42, 'ccc18a9773aa538adfbc262d3b39d3d453a2e1b9282bd2fc11272344b734acbc'),
    (0x9250, 0x1c, 'a02e7937f9f218f641046cf4b6f8e602149dcdc8da4375e01fafa2d0b69162ad'),
    (0x8c3e, 0x42, '2c57606edcc159ae8808054e89473d6ee27c28e7d64964f3d626efccac7495a9'),
    (0x19de0, 12, '3c02897e159ad4ff0d978aad736caad9131d0ead11407774026a983b13f1ad7b'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if (address < 0x14c8a and address + size > 0x14056) or (address < 0x1a6a0 and address + size > 0x1a69c):
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        raw = f.read(size)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise SystemExit('APP window changed')
        if address == 0x19de0 and struct.unpack('<III', raw) != (0x8b90, 0, 0x85c8):
            raise SystemExit('Callback table changed')
if 0x40034 + 4 * 92 != 0x401a4 or 0x887a + 0x11000 + 1382 != 0x19de0:
    raise SystemExit('Registration address arithmetic changed')
if (0x40034 + 4 * 80, 0x40034 + 4 * 41) != (0x40174, 0x400d8):
    raise SystemExit('Candidate GAP and GATT slot arithmetic changed')
if ((-2) & 0xffff) != 0xfffe or not all(0x20004080 <= 0x20004000 + offset < 0x2000c958 for offset in (150, 151, 154, 155)):
    raise SystemExit('Connection marker or reset-zero relationship changed')
print('Candidate GAP registration and event declarations verified; device behavior unverified.')
