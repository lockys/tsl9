"""Offline RV32 slice: three distinct handoffs, not execution of resident targets."""
from hashlib import sha256
from pathlib import Path

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def verify(b):
    def u(pc): return int.from_bytes(b[pc-0x8000:pc-0x8000+4],'little')
    def raw(pc,code):
        s=bytes.fromhex(code)
        if b[pc-0x8000:pc-0x8000+len(s)]!=s: raise ValueError(hex(pc))
    def pair(pc,rd,rel):
        w,v=u(pc),u(pc+4)
        if w&4095!=rd*128+(0x17 if rel else 0x37) or v&0xfffff!=(rd<<15)|(rd<<7)|19: raise ValueError(hex(pc))
        return ((pc if rel else 0)+(w&0xfffff000)+(v>>20)-((v>>31)<<12))&0xffffffff
    raw(0x19b16,'4111 26c2 b7040400 83a70408 06c6 22c4'); raw(0x19b2e,'8297 13844118 2300a400 3928 03450400 2244 03a38405 b240 9244'); raw(0x19b50,'8965 4101 0283')
    raw(0x19b56,'0111 8545 37050018 06ce 02c0 02c2 02c4 02c6'); raw(0x19bac,'fd57 3ec2'); raw(0x19bb8,'3ec4'); raw(0x19bc2,'3ec0 b7070400 fc5b 0a85 8297 f240 0561 8280')
    if (pair(0x19b26,10,True),pair(0x19b48,12,False),pair(0x19bb0,15,False),pair(0x19bba,15,True))!=(0x1995c,192000,0x03e83e80,0x191c6): raise ValueError('handoff constants')
    # Handler's bit-13 path: same slot offset, delay, event mask and a fresh GP byte load.
    raw(0x199ac,'bc4c'); raw(0x199b6,'8965 03c54118 8297');
    if pair(0x199ae,12,False)!=192000: raise ValueError('rearm delay')

if __name__=='__main__':
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    verify(b)
    for pc in (0x19b1e,0x19b2a,0x19b34,0x19b3a,0x19b40,0x19b4c,0x19bbe,0x19bc8,0x199b8):
        x=bytearray(b); x[pc-0x8000]^=4
        try: verify(x)
        except ValueError: continue
        raise ValueError('mutation accepted: '+hex(pc))
    print('PASS: handler 1995c, config callback 191c6, initial/rearm delay 192000; 9 mutation controls')
