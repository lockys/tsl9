"""Execute three straight/branched APP leaves against synthetic memory (not GPIO)."""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

APP=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
GP=0x20004000  # synthetic, only GP+168 is material
FLAG=GP+168

def sx(x,n): return x-((x>>(n-1))<<n)

def run(b,pc,mem,arg):
    r=[0]*32; r[3]=GP; r[10]=arg; log=[]
    for _ in range(12):
        h=unpack_from('<H',b,pc-0x8000)[0]; nxt=pc+2
        if h==0x8082: return log
        if h&0xe003==0x4001: r[h>>7&31]=sx(((h>>12&1)<<5)|(h>>2&31),6)
        elif h&0xe003==0xe001:
            d=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
            if r[8+(h>>7&7)]: nxt=pc+sx(d,9)
        elif h&3==3:
            w=unpack_from('<I',b,pc-0x8000)[0]; op=w&127; rd=w>>7&31; f=w>>12&7; a=w>>15&31; v=w>>20&31; nxt=pc+4
            if op==55: r[rd]=w&0xfffff000
            elif op==19 and f==4: r[rd]=(r[a]^sx(w>>20,12))&0xffffffff
            elif op==3 and f in (2,4):
                addr=(r[a]+sx(w>>20,12))&0xffffffff; n=4 if f==2 else 1
                r[rd]=mem[addr]&((1<<(8*n))-1); log.append(('r',addr,n,r[rd]))
            elif op==35 and f in (0,2):
                addr=(r[a]+sx((w>>25)<<5|rd,12))&0xffffffff; n=1<<f
                mem[addr]=r[v]&((1<<(8*n))-1); log.append(('w',addr,n,mem[addr]))
            else: raise ValueError(hex(pc))
        else: raise ValueError(hex(pc))
        pc=nxt
    raise ValueError('did not return')

def main():
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    for flag in range(256):
        for word in (0,2,0xfffffffd,0xffffffff):
            data={FLAG:flag,0x4001080c:word}; read=[('r',FLAG,1,flag)]
            if run(b,0x9af0,data.copy(),0)!=read+([] if flag else [('w',0x40010810,4,2)]): raise ValueError('conditional store')
            if run(b,0x9b36,data.copy(),0)!=read+([] if flag else [('r',0x4001080c,4,word),('w',0x4001080c,4,word^2)]): raise ValueError('conditional toggle')
            if run(b,0x9ad2,data,word)!=[('w',FLAG,1,1),('w',0x40010814,4,2)]: raise ValueError('callback stores')
            for entry in (0x9af0,0x9b36):
                if run(b,entry,data,word)!=[('r',FLAG,1,1)]: raise ValueError('post-callback gate')
    print('PASS: 1024 entry states; callback write order, two live flag readers, shared-memory composition')

if __name__=='__main__': main()
