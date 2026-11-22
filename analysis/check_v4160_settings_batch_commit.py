"""Static APP request ledger: injected live settings pointers need not be equal."""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

APP=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def verify(b):
    def raw(pc,code):
        s=bytes.fromhex(code)
        if b[pc-0x8000:pc-0x8000+len(s)]!=s: raise ValueError(hex(pc))
    def w(pc): return unpack_from('<I',b,pc-0x8000)[0]
    def imm(pc):
        x=w(pc)>>20; return x-4096 if x&2048 else x
    def addr(pc): return (pc+(w(pc)&0xfffff000)+imm(pc+4))&0xffffffff
    def jal(pc):
        x=w(pc)
        if x&4095!=239: raise ValueError(hex(pc))
        return pc-(x>>31)*1048576+((x>>12&255)<<12)+((x>>20&1)<<11)+((x>>21&1023)<<1)
    raw(0x1431a,'9c40 03478401 83c70700 b98f 9d8b 99c3');raw(0xfa3c,'93874111 03c70700 a380e700 8280');raw(0x1432e,'37090400 8327c904 8840 4146 93058401 8297 8840 8327c904 4146 9305b403 13050506 8297');raw(0x13138,'b7070400 fc47 6d71 23261110 0a85 13060007 9795ff1f 93852515 8297 37850708 8a85 130505a0');raw(0x14356,'8146 13064006 8145 1755ffff 1305052b');raw(0x1436a,'0145');raw(0x14370,'9c40 83c74700 a18b e38007d2')
    if [jal(p) for p in (0x1432a,0x14352,0x1315e,0x14366,0x1436c,0x1437c)]!=[0xfa3c,0x13138,0x9c0a,0x9124,0x13dd4,0xe20c]: raise ValueError('call chain')
    if (addr(0x1314a),addr(0x1435e),(w(0x13154)&0xfffff000)+imm(0x1315a))!=(0x2000c29c,0x960e,0x08077a00): raise ValueError('literal')
    mask=(b[0x14326-0x8000]>>2)&31
    if sum(bool((x^y)&mask) for x in range(256) for y in range(256))!=57344: raise ValueError('low-three gate')
    # Pure copy-service projection: demonstrate when both ranges reach staging, and when they do not.
    for a in (0,1):
        for c in (0,1):
            pages=[bytearray(112),bytearray(112)]; src=bytes(range(80))
            pages[a][:16]=src[imm(0x1433a):imm(0x1433a)+16]
            off=imm(0x1434c); pages[c][off:off+16]=src[imm(0x14348):imm(0x14348)+16]
            stage=pages[0][:imm(0x13146)]
            if stage!=(src[24:40] if a==0 else bytes(16))+bytes(80)+(src[59:75] if c==0 else bytes(16)): raise ValueError('staging')

if __name__=='__main__':
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('identity')
    verify(b)
    print('PASS: six calls; 65536 low-three comparisons; four live/fixed pointer staging cases')
