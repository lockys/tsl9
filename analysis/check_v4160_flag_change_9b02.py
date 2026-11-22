"""APP caller bit change, cancellation request and state change; external returns injected."""
from hashlib import sha256
from pathlib import Path

APP=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def verify(b):
    def raw(pc,s):
        s=bytes.fromhex(s)
        if b[pc-0x8000:pc-0x8000+len(s)]!=s: raise ValueError(hex(pc))
    def u(pc,n): return int.from_bytes(b[pc-0x8000:pc-0x8000+n],'little')
    def jal(pc):
        w=u(pc,4)
        if w&4095!=239: raise ValueError(hex(pc))
        return pc-(w>>31)*1048576+((w>>12&255)<<12)+((w>>20&1)<<11)+((w>>21&1023)<<1)
    raw(0x142fc,'93844105 9c40 0347b401 83c73700 b98f c18b 91c7 13554700 0589');raw(0x9b02,'4111 22c4 2a84 17050000 1305a5fc 06c6');raw(0x9b16,'2384810a 11c8 b240 2244 b7170140 0947 23aae780 4101 8280 2244 b240 4101 75bf'); raw(0x9af0,'83c7810a 91e7 b7170140 0947 23a8e780 8280')
    raw(0x90c4,'3d47 d443 6394a604'); raw(0x90d4,'8847 09c5 b7070400 bc57 8297');raw(0x90fe,'23a20400 23a40400 03a3c705 9244 4101 0283'); raw(0x9110,'0504 b107 e319e4fa b240 2244 9244 0545 4101 8280')
    if jal(0x14316)!=0x9b02 or jal(0x9b12)!=0x90b0 or 0x9b08+(u(0x9b0c,4)>>20)-4096!=0x9ad2: raise ValueError('target')
    mask=(u(0x1430c,2)>>2)&31; shift=u(0x14310,4)>>20; one=(u(0x14314,2)>>2)&31
    counts=[0,0,0]
    for old in range(256):
        for new in range(256):
            arg=None if ((new^old)&mask)==0 else ((new>>shift)&one)
            expect=None if bool(new&16)==bool(old&16) else int(bool(new&16))
            if arg!=expect: raise ValueError((old,new))
            counts[0 if arg is None else 1+arg]+=1
    if counts!=[32768,16384,16384]: raise ValueError(counts)
    print('PASS: 65536 byte pairs; skip/clear/set =',counts,'; call, table and store sites pinned')

if __name__=='__main__':
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    verify(b)
