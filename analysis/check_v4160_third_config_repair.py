"""Third settings page (APP only): +255 marker; no five-word defaults after fill.
Assumes normal fill/copy returns and valid saved registers; no flash observation.
Run from the checkout root, with the original APP locally available.
"""
from pathlib import Path
from hashlib import sha256

D = 0x2000c30c

def verify(b):
    def u(pc, n=4):
        return int.from_bytes(b[pc-0x8000:pc-0x8000+n], 'little')
    def need(x):
        if not x: raise ValueError('unexpected APP instruction')
    def literal(pc, hexbytes):
        s = bytes.fromhex(hexbytes)
        need(b[pc-0x8000:pc-0x8000+len(s)] == s)
    def pair(pc, rd, lo, target):
        w, v = u(pc), u(pc+4)
        need(w & 4095 == rd*128+0x17 and v & 0xfffff == lo)
        need((pc+(w&0xfffff000)+(v>>20)-((v>>31)<<12))&0xffffffff == target)
    def jump(pc, rd, target):
        w = u(pc)
        d = ((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
        need(w&4095 == rd*128+0x6f and pc+d-((w>>31)<<20) == target)
    pair(0x13254,14,0x74703,D+255)
    literal(0x1325c,'9307a005 6304f700'); jump(0x13264,1,0x12f18)
    literal(0x12f18,'b7070400 4111 bc47 22c4'); pair(0x12f22,8,0x40413,D)
    literal(0x12f2a,'06c6 2285 13060010 8145 8297 9307a005 a30ff40e 2244 b240 4101')
    jump(0x12f44,0,0x12ee6)
    literal(0x12ee6,'b7070400 fc47 6d71 23261110 0a85 13060010'); pair(0x12ef8,11,0x58593,D)
    literal(0x12f00,'8297 37850708 8a85 13050580'); jump(0x12f0c,1,0x9c0a)
    literal(0x12f10,'8320c110 5161 8280')
    pair(0x1327a,10,0x50513,0x2000c594); pair(0x13284,14,0x74703,0x2000c594+255)
    jump(0x13294,1,0x12f7a)

if __name__ == '__main__':
    b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP identity')
    verify(b)
    for pc in range(0x12ee6,0x12f48):
        bad=bytearray(b); bad[pc-0x8000]^=1
        try: verify(bad)
        except ValueError: continue
        raise ValueError(f'accepted changed byte at {pc:x}')
    print('PASS: third-page guard, repair and writer; 98 one-byte mutations rejected')
