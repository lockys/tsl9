"""Check candidate GATT length bounds and bounded APP instruction windows."""
import argparse
import hashlib
import json
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--wch-header', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = ((0x12392, 0x1c, '657ed9c93e2ede1c42eb7ffd5f21e23b5233065f661f74b76277ff3d15489025'), (0x12020, 0x10, 'f6c8a2fa5ea8a724a13def2beddda8a6e3ff30606436d64e4f84ac730a3dcbc9'), (0x8c00, 0x18, 'e75d97abf5f328b743771db155caec55e0f9eacbad614711747d535af99e47a5'), (0x19a3a, 0xb8, '3046ae74140455dfbb26e3dba155d97b69b7256d99ef241fa5c2348ecd6c22b3'))
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056 or address + size > 0x1a69c: raise SystemExit('Refusing excluded APP region')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected: raise SystemExit('Instruction window changed')
header = args.wch_header.read_bytes()
if hashlib.sha256(header).hexdigest() != '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':
    raise SystemExit('Candidate WCH header changed')
for token in (b'#define ATT_MAX_MTU_SIZE                512', b'attHandleValueNoti_t', b'attHandleValueInd_t', b'GATT_ExchangeMTU', b'0 to ATT_MTU_SIZE-3', b'uint16_t BufMaxLen;', b'ATT_MTU = BufMaxLen-4', b'BLE_LibInit'):
    if token not in header: raise SystemExit('Candidate GATT declaration changed')
def candidates(max_mtu): return [n for n in range(max_mtu - 2) if n & 255 == 6]
if candidates(512) != [6, 262] or candidates(264) != [6] or candidates(247) != [6]:
    raise SystemExit('Conditional length arithmetic changed')
offset = 0
for size, alignment in ((4, 4), (2, 2), (4, 4), (2, 2), (1, 1), (1, 1)):
    offset = (offset + alignment - 1) // alignment * alignment + size
if offset != 16 or 16 + offset != 0x20 or 251 - 4 != 247:
    raise SystemExit('Candidate config layout or MTU arithmetic changed')
evidence = root / 'experiments/tsl9-resident-ble-initialization/evidence-v1.json'
raw = evidence.read_bytes()
if hashlib.sha256(raw).hexdigest() != 'd32203b264e1f0c63b7a263997965fbbab7ed7397750e19a67dfdb2a33bf9208':
    raise SystemExit('Candidate resident instruction evidence changed')
function = next(f for f in json.loads(raw)['selected_functions'] if f['start'] == 0x43c7e)
part = [o for o in function['operations'] if 0x43cc4 <= o['addr'] < 0x43d0a]
body = b''.join(bytes.fromhex(o['bytes']) for o in part)
if len(body) != 70 or hashlib.sha256(body).hexdigest() != '8f0754d9eb779ff6110a2a16c95b39bcf7069e3b7bcb3e22303708223cb49d48':
    raise SystemExit('Candidate config copy/default body changed')
expected = {0x43cc8:'li a2, 64', 0x43cda:'li a2, 64', 0x43cde:'mv a1, s1', 0x43ce0:'addi a0, s0, 492', 0x43cec:'addi a5, s0, 492', 0x43d02:'qk.c.lhu a4, 16(a5)', 0x43d04:'bnez a4, 0x43d0a', 0x43d06:'li a4, 27', 0x43d08:'qk.c.sh a4, 16(a5)'}
ops = {o['addr']: o['opcode'] for o in part}
if any(ops.get(pc) != code for pc, code in expected.items()):
    raise SystemExit('Candidate config default control flow changed')
carrier = root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
with carrier.open('rb') as f:
    f.seek(0xa4)
    if int.from_bytes(f.read(4), 'little') != 0x43c7e: raise SystemExit('Candidate slot target changed')
    f.seek(0x43cc4 - 0x40000)
    if f.read(70) != body: raise SystemExit('Candidate resident original bytes changed')
print('GATT length candidates and bounded instruction windows verified; installed ABI and negotiated MTU unverified.')
