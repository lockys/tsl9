"""Static field/edge checks for the sixth settings area; not a flash emulator."""
from hashlib import sha256
from pathlib import Path

BASE = 0x8000
D = 0x2000c40c
PAGE = 0x08077500

def sx(x, bits):
    return x - ((x >> (bits-1)) << bits)

def verify(b):
    def word(pc): return int.from_bytes(b[pc-BASE:pc-BASE+4], 'little')
    def need(ok, pc):
        if not ok: raise ValueError(hex(pc))
    def addr(pc, rd, last, value, absolute=False):
        w, v = word(pc), word(pc+4)
        need(w&4095 == rd*128+(0x37 if absolute else 0x17),pc)
        need(v&0xfffff == last,pc+4)
        need(((0 if absolute else pc)+(w&0xfffff000)+sx(v>>20,12))&0xffffffff == value,pc)
    def jal(pc,rd,target):
        w=word(pc); disp=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        need(w&4095==rd*128+0x6f and pc+sx(disp,21)==target,pc)
    for pc in (0x132d2,0x1311e,0x130e4): need(word(pc)==(133<<20)|0x613,pc)
    addr(0x132da,10,0x50513,D); addr(0x132e4,14,0x74703,D+132)
    addr(0x13112,8,0x40413,D); addr(0x130e8,11,0x58593,D)
    for pc in (0x132ce,0x130f2):
        off = 8 if pc==0x132ce else 6
        rd = 11 if pc==0x132ce else 10
        w,v=word(pc),word(pc+off)
        need(w&4095==rd*128+0x37 and v&0xfffff==(rd<<15)|(rd<<7)|0x13 and (w&0xfffff000)+sx(v>>20,12)==PAGE,pc)
    need(word(0x132ec)==0x05a00793 and word(0x132f0)==0x00f70a63,0x132f0)
    need(word(0x13126)==0x05a00793 and word(0x1312a)==0x08f40223,0x1312a)
    for p,r,t in [(0x132f8,0,0x13108),(0x13134,0,0x130d6),(0x130fc,1,0x9c0a),(0x9c34,1,0x18ef2)]: jal(p,r,t)
    need(word(0x18f16)==0x10000613 and word(0x18f1e)==0x0006a803 and word(0x18f26)==0x0106a023,0x18f16)
    need(word(0x18f30)&65535==0x0791 and word(0x18f32)==0xfec794e3,0x18f30)

if __name__=='__main__':
    b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP identity')
    verify(b)
    for pc in (0x132d2,0x1311e,0x130e4,0x1312a,0x18f16,0x18f32):
        x=bytearray(b); x[pc-BASE+2]^=0x10
        try: verify(x)
        except ValueError: continue
        raise ValueError('accepted mutation at '+hex(pc))
    print('PASS: 133-byte requests, marker +132, writer bound 256/step 4; six negative controls')
