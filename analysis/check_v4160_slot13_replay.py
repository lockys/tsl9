"""ID 1001 replay: fd3e reads row 13 into a local 12-byte copy via 82a8.
The branch tests local byte +2, not ID, checksum or copy status. If nonzero
it calls fba2(local), not the original dispatch/validation path. A new row
can replace the old one: replay concerns current contents, not necessarily
what the earlier registration saw. No proof of callback delivery or copy.
Offline, selected successful instructions only; run from repository root.
"""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('slot13 replay mismatch')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n],'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    w=u(p,4); ck(w&4095==239)
    return p+sx((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)
def pin(p,h):
    v=bytes.fromhex(h); ck(b[p-32768:p-32768+len(v)]==v)
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
pin(0xfd3e,'01115000b545054506ce');pin(0xfd52,'4800');pin(0xfd58,'f24005618280')
ck(jal(0xfd48)==0x82a8 and jal(0xfd54)==0xfba2)
pin(0x82a8,'b707040003a3c704b147b385f50297470020938727f032873146ae9701c5be853a850283ba853e85edbf')
row=0x82b6+(u(0x82b6,4)&0xfffff000)+sx(u(0x82ba,4)>>20,12)+13*12
ck(row==0x2000c254)
w=u(0xfd4c,4); ck(w&0xfffff==0x14783); off=sx(w>>20,12)
h=u(0xfd50,2); ck(h&0xe383==0xc381)
d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
ck(0xfd50+sx(d,9)==0xfd58 and off==6)

def boundary(cache,local,status,copy):
    # Local is sp+4. Model a service return; deliberately vary what it wrote.
    frame=bytearray(32); frame[4:16]=local
    if copy: frame[4:16]=cache
    if frame[off]==0: return ('return',status)
    return ('call-fba2',bytes(frame[4:16]))

for n in range(256):
    cache=bytes([233,3,n])+bytes(range(9)); other=bytes([0,0,n^255])+bytes(range(9,18))
    for status in (0,1,6,0xffffffff):
        for copy in (False,True):
            result=boundary(cache,other,status,copy); data=cache if copy else other
            ck(result==(('call-fba2',data) if data[2] else ('return',status)))
print('PASS: row 13 0x2000c254 -> sp+4; branch on sp+6; 2048 projections; nonzero calls fba2 with local copy')
