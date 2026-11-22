"""python check_v131_even_payload_fields.py V131.bin -- offline Xwchc reference."""
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v:raise ValueError('selector 5 field parser mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(pc,n):return int.from_bytes(b[pc-0x40000:pc-0x40000+n],'little')
def sign(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
def jal(pc):
    w=word(pc,4);ck(w&4095==0xef);return pc+sign((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)
def fields(entry,length,data):
    p=0x20004824;dst=0x2000ff18;r={10:dst,11:p,12:length};mem={p+i:v for i,v in enumerate(data)};events=[];pc=entry
    for _ in range(50):
        h=word(pc,2);at=pc;pc+=2;q=h&3;f=h>>13;c=8+(h>>2&7);a=8+(h>>7&7)
        if q==3:
            w=word(at,4);ck(w&0x707f==0x1063);pc+=2
            if r[w>>15&31]!=r[w>>20&31]:pc=at+sign((w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1,13)
        elif q==1 and f==2:r[h>>7&31]=sign((h>>12&1)<<5|(h>>2&31),6)
        elif q==0 and f==1:
            addr=r[a]+8*(h>>10&3)+2*(h>>5&3)+(h>>12&1);r[c]=mem[addr];events.append(('r',addr-p,r[c]))
        elif q==2 and f==5:
            addr=r[a]+8*(h>>10&7)+2*(h>>5&3);v=r[c]&65535;events.append(('w',addr-dst,v));mem[addr]=v&255;mem[addr+1]=v>>8
        elif h==0x07a2:r[15]<<=8
        elif h==0x8fd9:r[15]|=r[14]
        elif h==0x8082:return r[10],events
        else:raise ValueError(hex(at))
    raise ValueError('step budget')
for cmd,call,n,entry in [(6,0x4df72,4,0x4dd12),(18,0x4dfd8,8,0x4dd56)]:
    ck(jal(call)==entry and word(call-2,2)==0x0028) # a0=sp+8
    for length in range(24):
        for seed in range(256):
            data=bytes((seed+37*i)&255 for i in range(n));trace=[]
            if length==n:
                for i in range(0,n,2):trace.extend([('r',i+1,data[i+1]),('r',i,data[i]),('w',i,int.from_bytes(data[i:i+2],'little'))])
            ck(fields(entry,length,data)==(int(length!=n),trace))
print('PASS: 12288 helper traces; commands 6/18: 4/8 bytes -> 2/4 stack halfwords; invalid lengths: no data accesses')
