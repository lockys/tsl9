"""Static RV32 compressed branch decoding; external returns/loaded fields are inputs."""
from pathlib import Path
from hashlib import sha256
from itertools import product

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def main():
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    def raw(pc,s):
        data=bytes.fromhex(s)
        if b[pc-0x8000:pc-0x8000+len(data)]!=data: raise ValueError(hex(pc))
    def cb(pc,reg,x):
        h=int.from_bytes(b[pc-0x8000:pc-0x8000+2],'little'); f=h>>13
        if h&3!=1 or f not in (6,7) or 8+((h>>7)&7)!=reg: raise ValueError(hex(pc))
        delta=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
        return pc+(delta-((delta>>8)<<9) if (x!=0)==(f==7) else 2)
    raw(0x199e2,'b7070020 9c47 1d71 a2cc 23a0f118 37040400 5c5c 4858 86ce 5546 97150000 93850512 8297')
    text=0x199fc+0x1000+288
    if b[text-0x8000:text-0x8000+22]!=b'CH32V20x_BLE_LIB_V1.3\0': raise ValueError('tag')
    for loop in (0x19a08,0x19ae0,0x19af0): raw(loop,'01a0')
    raw(0x19ad2,'c247'); raw(0x19ad6,'03574101 8567 6373f700')
    raw(0x19ae2,'b7070400 83a7470a 0808 8297'); raw(0x19af2,'8545 13050004 eff0efe0')
    raw(0x19b04,'f640 6644 23a2e710 0547 23a4e710 2561 8280'); raw(0x8eac,'ef00b146')
    w=int.from_bytes(b[0x11adc:0x11ae0],'little')
    if (w&0x7f,(w>>12)&7,(w>>15)&31,(w>>20)&31)!=(0x63,7,14,15): raise ValueError('unsigned comparison')
    disp=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    tally=[0]*4
    for v,p,n,status in product((0,1,0xffffffff),(0,1),(0,4095,4096,65535),(0,1,0x80000000)):
        pc=cb(0x19a06,10,v)
        if pc==0x19a0a:
            pc=cb(0x19ad4,15,p)
            if pc==0x19ad6: pc=0x19adc+(disp if n>=4096 else 4)
            if pc==0x19ae2: pc=cb(0x19aee,10,status)
        expected=0x19a08 if v==0 else 0x19ae0 if not p or n<4096 else 0x19af0 if status else 0x19af2
        if pc!=expected: raise ValueError(hex(pc))
        tally[(0x19a08,0x19ae0,0x19af0,0x19af2).index(pc)]+=1
    print('PASS: gate projections (tag-loop, field-loop, init-loop, continuation):',tally)

if __name__=='__main__': main()
