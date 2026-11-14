"""Original 0x8a20 post-store length test, with a successful synthetic LHU.

The loaded halfword is its value at this instant, not necessarily the length
before prior writes or concurrent/provider activity. No full packet is run.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry',HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py'); entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
MASK=0xffffffff
EXPECTED=bytes.fromhex('83d6e108e362d7f855bf')
def signed(x,bits): return x-(1<<bits) if x&(1<<(bits-1)) else x

def run(code,gp,next_index,loaded):
    if len(code)!=10 or not 0<=gp<=MASK or not 0<=next_index<=MASK or not 0<=loaded<=65535: raise ValueError('invalid input')
    r=[0]*32; r[3]=gp; r[14]=next_index; pc=0x8a20; reads=[]; trace=[]
    for _ in range(3):
        if pc in (0x89a8,0x89dc): return pc,reads,trace
        off=pc-0x8a20
        if off<0 or off+2>len(code) or pc&1: raise ValueError('outside transition')
        trace.append(pc); h=int.from_bytes(code[off:off+2],'little')
        if h&3!=3:
            if (h&3,h>>13)!=(1,5): raise ValueError('unsupported compressed instruction')
            imm=((h>>12&1)<<11 | (h>>11&1)<<4 | (h>>9&3)<<8 | (h>>8&1)<<10 | (h>>7&1)<<6 | (h>>6&1)<<7 | (h>>3&7)<<1 | (h>>2&1)<<5)
            pc=(pc+signed(imm,12))&MASK
        else:
            if off+4>len(code): raise ValueError('truncated instruction')
            w=int.from_bytes(code[off:off+4],'little'); op,rd,f3,rs1,rs2=w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
            if op==3 and f3==5:
                address=(r[rs1]+signed(w>>20,12))&MASK
                if address!=(gp+142)&MASK: raise ValueError('unexpected length read')
                reads.append(address); r[rd]=loaded; pc+=4
            elif op==0x63 and f3==6:
                imm=(w>>31&1)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
                pc=(pc+signed(imm,13))&MASK if r[rs1]<r[rs2] else pc+4
            else: raise ValueError('unsupported instruction')
        r[0]=0
    if pc in (0x89a8,0x89dc): return pc,reads,trace
    raise ValueError('transition did not finish')

def check(code,gp,next_index,loaded):
    actual=run(code,gp,next_index,loaded)
    expected=(0x89a8,[(gp+142)&MASK],[0x8a20,0x8a24]) if next_index<loaded else (0x89dc,[(gp+142)&MASK],[0x8a20,0x8a24,0x8a28])
    if actual!=expected: raise ValueError(f'transition mismatch: {actual!r}')

def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8a20-0x8000:0x8a2a-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for n in (1,520,1040):
        for loaded in range(65536): check(code,0x20004000,n,loaded)
    for gp in (0,0xffffff72,MASK):
        for n in (0,1,1039,1040,65535,65536,MASK):
            for loaded in (0,1,1039,1040,65535): check(code,gp,n,loaded)
    for i in range(len(code)):
        mutated=bytearray(code); mutated[i]^=1
        try:
            for gp,n,loaded in ((0x20004000,1,0),(0x20004000,1,2),(0x20004000,1040,1040)): check(mutated,gp,n,loaded)
        except ValueError: continue
        raise ValueError(f'undetected mutation {i}')
    print('PASS: 196608 length values across three indices, 105 boundary cases and 10 byte mutations')
    print('At 0x8a20 the length is freshly loaded; full ingress execution and hardware unverified.')

if __name__=='__main__': main()
