"""Project original 0x8a02 payload index guard and writes, up to 0x8a20.

Entry registers, successful accesses and no trap are synthetic. This does not
prove a complete packet path, object bounds or real device state.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry',HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py'); entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
MASK=0xffffffff
EXPECTED=bytes.fromhex('6365c70413071600420741832395e10897360020938666fcb2962380f600')

def signed(x,n): return x-(1<<n) if x&(1<<(n-1)) else x

def run(code,gp,index,byte):
    if len(code)!=30 or any(not 0<=v<=MASK for v in (gp,index,byte)): raise ValueError('invalid input')
    r=[0]*32; r[3]=gp; r[12]=index; r[14]=1039; r[15]=byte; pc=0x8a02; writes=[]; trace=[]
    for _ in range(10):
        if pc in (0x8a20,0x8a4c): return pc,writes,trace
        off=pc-0x8a02
        if off<0 or off+2>len(code) or pc&1: raise ValueError('outside store projection')
        h=int.from_bytes(code[off:off+2],'little'); trace.append(pc)
        if h&3!=3:
            if h==0x0742: r[14]=(r[14]<<16)&MASK
            elif h==0x8341: r[14]>>=16
            elif h==0x96b2: r[13]=(r[13]+r[12])&MASK
            else: raise ValueError('unsupported compressed instruction')
            pc+=2
        else:
            if off+4>len(code): raise ValueError('truncated')
            w=int.from_bytes(code[off:off+4],'little'); op,rd,f3,rs1,rs2=w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
            if op==0x63 and f3==6:
                imm=(w>>31&1)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
                pc=(pc+signed(imm,13))&MASK if r[rs1]<r[rs2] else pc+4; continue
            elif op==0x13 and f3==0: r[rd]=(r[rs1]+signed(w>>20,12))&MASK
            elif op==0x17: r[rd]=(pc+(w&0xfffff000))&MASK
            elif op==0x23 and f3 in (0,1):
                imm=(w>>25)<<5 | (w>>7&31); width=1 if f3==0 else 2
                writes.append(((r[rs1]+signed(imm,12))&MASK,width,r[rs2]&((1<<(width*8))-1)))
            else: raise ValueError('unsupported instruction')
            pc+=4
        r[0]=0
    raise ValueError('instruction budget exceeded')


def check(code,gp,index,byte):
    pc,writes,trace=run(code,gp,index,byte)
    if index>1039: want=(0x8a4c,[],[0x8a02])
    else: want=(0x8a20,[((gp+138)&MASK,2,index+1),(0x2000b9d8+index,1,byte&255)],[0x8a02,0x8a06,0x8a0a,0x8a0c,0x8a0e,0x8a12,0x8a16,0x8a1a,0x8a1c])
    if (pc,writes,trace)!=want: raise ValueError('store projection mismatch')


def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8a02-0x8000:0x8a20-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for index in range(65536): check(code,0x20004000,index,0x1ab)
    for index in (0,1,1039,1040,0xffff,0x10000,MASK):
        for gp in (0,MASK,0xffffff76):
            for byte in (0,1,255,256,MASK): check(code,gp,index,byte)
    for i in range(len(code)):
        changed=bytearray(code); changed[i]^=1
        try:
            for index in (0,1,1039,1040): check(changed,0x20004000,index,0xab)
        except ValueError: continue
        raise ValueError(f'undetected mutation {i}')
    print('PASS: 65536 index values, 105 boundary cases, 30 byte mutations; 1040 indices store into fixed payload range')
    print('Synthetic 0x8a02 entry and successful stores assumed; no full ingress or hardware execution.')

if __name__=='__main__': main()
