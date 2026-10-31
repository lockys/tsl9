"""Check candidate GATT length bounds and bounded APP instruction windows."""
import argparse
import hashlib
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--wch-header', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x12392, 0x1c, '657ed9c93e2ede1c42eb7ffd5f21e23b5233065f661f74b76277ff3d15489025'), (0x12020, 0x10, 'f6c8a2fa5ea8a724a13def2beddda8a6e3ff30606436d64e4f84ac730a3dcbc9'), (0x8c00, 0x18, 'e75d97abf5f328b743771db155caec55e0f9eacbad614711747d535af99e47a5'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address + size > 0x14056: raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected: raise SystemExit('Instruction window changed')
header = args.wch_header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate WCH header changed')
for token in (b'#define ATT_MAX_MTU_SIZE                512', b'attHandleValueNoti_t', b'attHandleValueInd_t', b'GATT_ExchangeMTU', b'0 to ATT_MTU_SIZE-3'):
    if token not in header: raise SystemExit('Candidate GATT declaration changed')
def candidates(max_mtu): return [n for n in range(max_mtu - 2) if n & 255 == 6]
if candidates(512) != [6, 262] or candidates(264) != [6] or candidates(247) != [6]:
    raise SystemExit('Conditional length arithmetic changed')
print('GATT length candidates and bounded instruction windows verified; installed ABI and negotiated MTU unverified.')
