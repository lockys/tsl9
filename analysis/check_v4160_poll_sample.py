"""Execute only the 0x16896 transfer leaf with synthetic halfword samples."""
from pathlib import Path
from hashlib import sha256

B=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def need(v):
    if not v: raise ValueError('transfer evidence mismatch')
def sign(x,n): return x-((x>>(n-1))<<n)
def run(tx,rx,data):
    r=[0]*32; r[10]=0xabcdef12; pc=0x16896; polls=[0,0]; writes=[]; reads=0
    for _ in range(4096):
        need(0x16896<=pc<0x168de); i=pc-0x8000; w=int.from_bytes(B[i:i+4],'little'); h=w&65535
        if h&3==3:
            d=w>>7&31; a=w>>15&31; z=w>>20&31; op=w&0x707f; imm=sign(w>>20,12)
            if w&127==55: r[d]=w&0xfffff000
            elif op==19: r[d]=r[a]+imm
            elif op==0x7013: r[d]=r[a]&imm
            elif op==0x5003:
                addr=r[a]+imm
                if addr==0x40013008:
                    j=int(bool(writes)); polls[j]+=1; r[d]=(2>>j) if polls[j]==(tx,rx)[j] else 0
                else: need(addr==0x4001300c); reads+=1; r[d]=data
            elif op==0x1023:
                off=sign((w>>25<<5)|(w>>7&31),12); need(r[a]+off==0x4001300c); writes.append(r[z]&65535)
            else: raise ValueError(hex(pc))
            pc+=4
        elif h==0x8082: return r[10],polls,writes,reads
        elif h in (0x8b09,0x8b05): r[14]&=(h>>2)&31; pc+=2
        elif h in (0x0542,0x8141): r[10]=((r[10]<<16)&0xffffffff) if h==0x0542 else r[10]>>16; pc+=2
        elif h==0x17fd: r[15]-=1; pc+=2
        elif h==0x4501: r[10]=0; pc+=2
        elif h>>13 in (6,7):
            disp=sign(((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5),9)
            taken=(r[8+(h>>7&7)]!=0)==(h>>13==7); pc+=disp if taken else 2
        elif h==0xbfd5: pc=0x168d0
        else: raise ValueError(hex(pc))
    raise ValueError('budget')
need(sha256(B).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for n in range(1,256):
    for t,r in ((n,1),(1,n)):
        need(run(t,r,0xcd9f)==(0x9f,[t,r],[0xef12],1))
need(run(256,1,0xffff)==(0,[255,0],[],0)); need(run(255,256,0xffff)==(0,[255,255],[0xef12],0)); need(run(255,255,0xab00)==(0,[255,255],[0xef12],1))
print('PASS: 510 ready-position runs; TX timeout, RX timeout, successful zero byte distinguished')
