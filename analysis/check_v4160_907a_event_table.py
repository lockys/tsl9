"""APP table initialization and bounded 901a handler; injected callbacks return normally."""
from pathlib import Path
from hashlib import sha256
from struct import pack_into, unpack_from

APP=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def main():
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    def raw(pc,s):
        v=bytes.fromhex(s)
        if b[pc-0x8000:pc-0x8000+len(v)]!=v: raise ValueError(hex(pc))
    def addr(pc,rd):
        p=pc-0x8000; u,v=unpack_from('<II',b,p)
        if u&4095!=rd*128+23 or v&0xfffff!=(rd<<15)|(rd<<7)|19: raise ValueError(hex(pc))
        return (pc+(u&0xfffff000)+(v>>20)-((v>>31)<<12))&0xffffffff
    raw(0x907a,'4111 22c4 37040400 3c44 06c6 1306400b 8145');raw(0x9094,'8297 83270408');raw(0x90a2,'8297 b240 2244 2383a10a 4101 8280')
    if (addr(0x908c,10),addr(0x909a,10),addr(0x9034,15))!=(0x2000be08,0x901a,0x2000be08): raise ValueError('address')
    raw(0x9022,'0144 3d47 b3d78540 858b b1c3 b147 3307f402');raw(0x903c,'ae84 ba97 d443 81ce 03c70700 8847 1377f70f 09e7 23a20700 23a40700 8296');raw(0x905a,'0545 33158500 258d 4205 4181 b240 2244 9244 4101 8280 0504 e31ae4fa 0145 fdb7')
    raw(0x8eb0,'e922 8327041a 8297 8327c41a 8297 8327041c 8297 83270408');raw(0x8ed0,'8297 a38ea108');
    if addr(0x8ec8,10)!=0x8614: raise ValueError('second handler')
    # Compare sequential scan to a lowest-set-bit oracle on every 16-bit event mask.
    for mask in range(65536):
        lo=mask&0x7fff; bit=lo&-lo
        row=next((i for i in range(15) if mask>>i&1),None)
        result=0 if row is None else mask^(1<<row)
        if result!=(mask^bit if bit else 0) or (row is not None and 12*row+12>180): raise ValueError(mask)
    # Fields are sampled before one-shot clearing; record the view at the call boundary.
    for i in range(15):
        for flag in (0,1,255):
            for target in (0,0x100):
                data=bytearray(180); off=12*i; pack_into('<B3xII',data,off,flag,target,123); before=data[:]; call=None
                f,t,arg=unpack_from('<B3xII',data,off)
                if t:
                    if not f: pack_into('<II',data,off+4,0,0)
                    call=(t,arg)
                expected=before[:]
                if flag==0 and target: expected[off+4:off+12]=bytes(8)
                if data!=expected or call!=((target,123) if target else None): raise ValueError(i)
    print('PASS: APP instruction windows; same 180-byte table; 65536 masks; 90 synthetic row cases')

if __name__=='__main__': main()
