"""Compose 960e's initialized halfwords with the timer reader's selected fields.
Run from repo root. Synthetic stable P, index and phase, successful accesses,
normal provider returns, preserved bases and eligible IRQ entries; not a CPU run.
"""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def need(ok, label):
    if not ok: raise ValueError(label)
def raw(pc, n): return b[pc-0x8000:pc-0x8000+n]
def word(pc): return int.from_bytes(raw(pc,4),'little')
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','APP')
rows={}; regs={0:0}
for pc in (0x9620,0x9624,0x9628,0x962c,0x9630,0x9634,0x963a,0x963e,0x9642,0x9646,0x964a):
    w=word(pc)
    if w&0xfffff==0x793: regs[15]=w>>20
    else:
        need(w&0xff07f==0x51023,'SH via a0'); rows[((w>>25)<<5)|(w>>7&31)]=regs[w>>20&31]
for pc,code in [(0x980e,'99463307d70283270901ba97'),(0x9874,'99463307d7029c48ba97'),(0x98a2,'99463307d70283270901ba97'),(0x98e2,'1947b387e702aa97'),(0x981e,'b7470f0093870724b3c7e7021307800cfd17c207c1832316f402'),(0x98d4,'850793f7f70f'),(0x98ee,'a9e309c9')]:
    s=bytes.fromhex(code); need(raw(pc,len(s))==s,hex(pc))
fields=[]
for pc,rd in [(0x981a,14),(0x987e,15),(0x98ae,15),(0x98ea,15)]:
    w=word(pc); need(w&0xfffff==(15<<15|5<<12|rd<<7|3),hex(pc)); fields.append(w>>20)
need(fields==[0,2,4,0],'LHU offsets')
reads=[]
def load(i,off):
    k=6*i+off; reads.append(k); return rows[k]
periods=[]; deltas=[]
for i in (0,1):
    periods.append((1000000//load(i,fields[0])-1)&65535)
    deltas.append((load(i,fields[1]),load(i,fields[2])))
    need(bool(load(i+1,fields[3]))==(i==0),'next-row decision')
need((periods,deltas,reads)==([857,681],[(130,0),(150,0)],[0,2,4,6,6,8,10,12]),'writer/reader join')
print('PASS: period halfwords',periods,'deadline increments',deltas,'descriptor read offsets',reads)
