"""Pin shared precheck windows and reset-zero address relationships."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = (
    (0x13bd2, 0x7c, 'a6761aae01a3470f01947b1f3c04d88bae8cebc8a6b3382e69f3aeeec8585853'),
    (0x14c8a, 0x3e, '2a64c4187219346a42ab6556f8b1c167a16f97b1ebf4747de20855fbbe082a75'),
    (0x8b90, 0x16, '6e4414fe0d602ab0827750b095ee16f6f42525b0e169de2f7ae1fcf7142502ee'),
    (0x8c3e, 0x42, '2c57606edcc159ae8808054e89473d6ee27c28e7d64964f3d626efccac7495a9'),
    (0x82d2, 0xbc, '7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30'),
    (0x838e, 0xb2, '1f0ea770b8556ae5d311cf5b4973faed6a2f4374bd3343f4ba1af06c66e35651'),
    (0x13ba6, 0x2c, '3a615f24a57973d9922fa9bb2d87eb80ef33d51d46121c9a9cb0f3a77a521e62'),
    (0x13e0e, 0x8a, '5bdb6138205ebc523ef2a3d68d7524f10a6e5723910fc06462c2f6023a50455a'),
)
with image.open('rb') as f:
    for address, size, expected in windows:
        if address < 0x14c8a and address + size > 0x14056:
            raise SystemExit('Refusing excluded code and data')
        f.seek(address - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Instruction window changed')
a = 0x82f2 + 0x20004000 + 1186
b = 0x839c + 0x20004000 + 1016
if a != b or a != 0x2000c794:
    raise SystemExit('Precheck base addresses changed')
if 0x13ba6 + 0x1fff9000 - 1040 != a + 2 or 0x13bae + 0x1fff9000 - 1050 != a:
    raise SystemExit('Type writer address relationship changed')
if 0x13e10 + 0x1fff9000 - 1660 != a:
    raise SystemExit('Flag writer base address changed')
if 0x14c94 + 0x1fff8000 - 1280 != a:
    raise SystemExit('Initializer base address changed')
addresses = {a + 4*i + offset for i in range(2) for offset in (2, 3, 4, 5)}
if not all(0x20004080 <= x < 0x2000c958 for x in addresses):
    raise SystemExit('Precheck fields leave reset-zero numerical range')
evidence = root / 'experiments/tsl9-resident-ble-initialization/evidence-v1.json'
data = evidence.read_bytes()
if hashlib.sha256(data).hexdigest() != 'd32203b264e1f0c63b7a263997965fbbab7ed7397750e19a67dfdb2a33bf9208':
    raise SystemExit('Candidate resident instruction evidence changed')
fill = next(f for f in json.loads(data)['selected_functions'] if f['start'] == 0x2000039c)
body = b''.join(bytes.fromhex(o['bytes']) for o in fill['operations'])
if fill['end'] != 0x200003ca or len(fill['operations']) != 14 or hashlib.sha256(body).hexdigest() != 'd67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3':
    raise SystemExit('Candidate resident fill body changed')
expected = {0x2000039c:'lui a4, 0x40024',0x200003a0:'lw a5, 524(a4)',0x200003a4:'sw zero, 524(a4)',0x200003a8:'fence.i',0x200003ac:'beqz a0, 0x200003b4',0x200003ae:'add a4, a0, a2',0x200003b2:'bnez a2, 0x200003be',0x200003b4:'lui a4, 0x40024',0x200003b8:'sw a5, 524(a4)',0x200003bc:'ret',0x200003be:'addi a0, a0, 1',0x200003c0:'sb a1, -1(a0)',0x200003c4:'bne a0, a4, 0x200003be',0x200003c8:'j 0x200003b4'}
if {o['addr']:o['opcode'] for o in fill['operations']} != expected:
    raise SystemExit('Candidate fill control flow changed')
if 0x13bd2 + 0x1fff9000 - 1086 != a:
    raise SystemExit('Type-4 dispatcher gate address changed')
print('Shared precheck instruction windows and zero-range relationship verified; target not executed.')
