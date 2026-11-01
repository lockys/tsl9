"""Compare one bounded TX guard without executing target or reading excluded ranges."""
from pathlib import Path
import json
root = Path(__file__).resolve().parents[2]
official = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
candidate = root / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
pc = 0x8a76
def read_window(path):
    if path.stat().st_size != 76800:
        raise ValueError('image size changed')
    with path.open('rb') as f:
        f.seek(pc-0x8000)
        value=f.read(12)
    if len(value)!=12: raise ValueError('short window')
    return value
def branch(word, address):
    if word & 0x7f != 0x63: raise ValueError('not a RISC-V branch')
    funct3=(word>>12)&7;rs1=(word>>15)&31;rs2=(word>>20)&31
    imm=((word>>31)&1)<<12|((word>>7)&1)<<11|((word>>25)&0x3f)<<5|((word>>8)&15)<<1
    if imm & 0x1000: imm-=0x2000
    return funct3,rs1,rs2,address+imm
a,b=read_window(official),read_window(candidate)
if a.hex()!=('6310a702'+'c167f917'+'630cf700') or b.hex()!=('6310a702'+'c167f917'+'638ca700'):
    raise ValueError('reviewed guard bytes changed')
prior=branch(int.from_bytes(a[:4],'little'),pc)
original=branch(int.from_bytes(a[8:12],'little'),pc+8)
rebuilt=branch(int.from_bytes(b[8:12],'little'),pc+8)
if prior!=(1,14,10,0x8a96) or original!=(0,14,15,0x8a96) or rebuilt!=(0,15,10,0x8a96):
    raise ValueError('branch fields or destinations differ')
if a[4:8]!=bytes.fromhex('c167f917') or b[4:8]!=a[4:8]:
    raise ValueError('intervening compressed instructions changed')
print(json.dumps({'prior_branch':'bne a4,a0 to 0x8a96',
                  'original':'beq a4,a5 to 0x8a96',
                  'candidate':'beq a5,a0 to 0x8a96',
                  'fallthrough_condition':'a4 == a0',
                  'scope':'one branch, no alternate entry or asynchronous change assumed',
                  'excluded_app_read':False,'target_executed':False}))
