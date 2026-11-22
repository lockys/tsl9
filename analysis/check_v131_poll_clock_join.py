"""Join V1.31 clock delta to APP scaling. Inject division results, not RTC readings."""
import hashlib
from pathlib import Path

M=0xffffffff

def image(path,digest):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=digest: raise ValueError('image identity')
    return b

def need(v):
    if not v: raise ValueError('clock join mismatch')

rom=image('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
app=image('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(int.from_bytes(rom[124:128],'little')==0x43520)
for off,h in [(0x3536,'89c7 8297 5c48 3e95 48c8 4848'),(0x3da0,'004f aa84 0145 63069402 9389c719 33858440 636e9400'),(0x3db6,'03254900 5686 8146 b335aa02 3305aa02 efa04215 018d 2695 23ac9900')]:
    need(rom[off:off+len(bytes.fromhex(h))]==bytes.fromhex(h))
need(app[0x1bc:0x1c8]==bytes.fromhex('a947 3305f502 b240 4101 1181'))

def project(present,last,q,wrap,acc):
    # No concurrent/aliased writes; acc is the freshly loaded accumulator.
    writes=[]
    if present:
        delta=0 if last==q else (q-last+(wrap if q<last else 0))&M
        if q!=last: writes.append(('last',q))
        acc=(acc+delta)&M; writes.append(('acc',acc))
    return writes,acc,((acc*10)&M)>>4

need(project(False,0,1,100,8)==([],8,5))
need(project(True,1,1,100,8)==([('acc',8)],8,5))
need(project(True,1,2,100,8)==([('last',2),('acc',9)],9,5))
need(project(True,99,2,100,8)==([('last',2),('acc',11)],11,6))
need(project(True,1,6,100,M-2)==([('last',6),('acc',2)],2,1))
print('PASS: absent hook, equal sample, hidden increment, backward sample and accumulator wrap')
