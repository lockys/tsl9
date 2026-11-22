"""Replay row-13 request paths on selected RV32 instructions (not a device).
Calls have normally returning getter/copy models; stop at fba2, or at return.
Copy model supplies only the observed local length byte and leaves gp state alone.
No callback delivery or actual RAM contents assumed.
"""
from hashlib import sha256
from pathlib import Path
B=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('row13 gate mismatch')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def u(p,n): return int.from_bytes(B[p-32768:p-32768+n],'little')
def pin(p,h):
    v=bytes.fromhex(h);ck(B[p-32768:p-32768+len(v)]==v)
ck(sha256(B).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
pin(0xd052,'17f5ff1f034525ef8280');pin(0x10402,'03d501058280')
ck(0xd052+(u(0xd052,4)&0xfffff000)+sx(u(0xd056,4)>>20,12)==0x2000bf44)

def run(entry,arg,state,mode,n,length):
    pc=entry;r=[0]*32;r[2]=0x1000;r[3]=0x20000000;r[10]=arg
    mem={r[3]+289:state};events=[]
    for _ in range(48):
        w=u(pc,4);h=w&65535;rd=w>>7&31;s=w>>15&31;t=w>>20&31;fn=w>>12&7
        step=2 if h&3!=3 else 4
        if h in (0x1101,0x6105): r[2]+= -32 if h==0x1101 else 32
        elif h in (0xce06,0x40f2): pass # saved ra disjoint; stop at ret
        elif h==0x8082: return events,mem[r[3]+289]
        elif h&0xe003==0x4001: r[rd]=sx((h>>12&1)<<5|(h>>2&31),6)
        elif h in (0x0050,0x0048): r[8+(h>>2&7)]=r[2]+4
        elif h&0xe003==0xc001:
            d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
            if not r[8+(h>>7&7)]: step=sx(d,9)
        elif h in (0xbfe1,0xa811):
            d=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5;step=sx(d,12)
        elif w&127==99:
            take={1:r[s]!=r[t],7:r[s]>=r[t]}[fn]
            if take: step=sx((w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1,13)
        elif w&0x707f==0x4003: r[rd]=mem[r[s]+sx(w>>20,12)]
        elif w&0x707f==0x23:
            addr=r[s]+sx((w>>25<<5)|(w>>7&31),12);ck(addr==r[3]+289);mem[addr]=r[t]&255;events.append(('state',mem[addr]))
        elif w&4095==239:
            dest=pc+sx((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)
            if dest==0xd052: events.append('mode');r[10]=mode
            elif dest==0x10402: events.append('half');r[10]=n
            elif dest==0x82a8:
                ck(r[10:13]==[1,13,r[2]+4]);events.append('copy');mem[r[12]+2]=length;r[10]=0
            elif dest==0xfba2:
                ck(r[10]==r[2]+4);events.append('process');return events,mem[r[3]+289]
            else: raise ValueError(hex(dest))
        else: raise ValueError(hex(pc))
        pc+=step
    raise ValueError('no stop')

count=0
for arg in (0,1,256,0xffffffff):
 for state in (0,1,2,3,255):
  for mode in (0,3,4,5,255):
   for n in (0,7,8,9,255,256,65535):
    for length in (0,1,8,255):
     read=(arg==0 and state==1) or (arg!=0 and mode==4 and n>8)
     new=(2 if state==1 else 0) if not arg else (1 if read else state)
     trace=(['mode']+(['half'] if mode==4 else [])) if arg else []
     if not arg or read: trace.append(('state',new))
     if read: trace+=['copy']+(['process'] if length else [])
     ck(run(0xfda6,arg,state,mode,n,length)==(trace,new));count+=1
     ck(run(0xfd3e,arg,state,mode,n,length)==(['copy']+(['process'] if length else []),state))
pin(0xfc44,'03c7111285466308d70889466305d70c');pin(0xfcda,'8347540093e70704a302f400');pin(0xfd1a,'a38001128347540093f7f7fba302f400')
print(f'PASS: {count} input tuples per entry; ordered writes/reads and process gate; downstream bit-6 set/clear windows')
