"""V1.31 reference: registration / saved-ID / later repost slices, not continuous boot."""
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('task origin mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p,n=4):return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    x=w(p);ck(x&4095==0xef);return p+sx(x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
ck((w(0x6dd1e)&0xfffff000)+sx(w(0x6dd22)>>20,12)==0x4dbf2)
ck((jal(0x6dd26),jal(0x6dd2a),jal(0x4dace),jal(0x4dcc2))==(0x43c4e,0x4da70,0x4edd2,0x4354a))
save=w(0x4dab8,2);load=w(0x4dad2,2)
ck(save==0xc62a and load==0x4532)
so=(save>>9&15)*4+(save>>7&3)*64;lo=(load>>12&1)*32+(load>>4&7)*4+(load>>2&3)*64
ck(so==lo==12)
x=w(0x4dadc);ck(x&0x1fff07f==0xa78023);store=(w(0x4dad4)&0xfffff000)+sx(x>>25<<5|(x>>7&31),12)
x=w(0x4dcbc);ck(x&0xfffff==0x7c503);read=(w(0x4dcb8)&0xfffff000)+sx(x>>20,12)
ck(read==store==0x20003314 and w(0x43562)==0x02e57063 and w(0x43586,2)==0x450d)
# Project successful helper return, unchanged saved word, then no intervening task-ID write.
ok=bad=0
for used in range(256):
    for cap in range(256):
        saved=used if used<cap else 255;frame={so:saved};ram={store:frame[lo]&255};task=ram[read]
        count=used+int(used<cap)
        if task<count:ck(task==used and used<cap);ok+=1
        else:ck(task==255 and used>=cap);bad+=1
ck((ok,bad)==(32640,32896));ck(all(not 255<n for n in range(256)))
print('PASS: stack +12 to RAM byte 0x20003314; 32640 assigned IDs pass unchanged count, 32896 full cases store 255 and cannot post')
