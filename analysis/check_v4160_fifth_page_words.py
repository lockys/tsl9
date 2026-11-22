"""Replay the fifth settings repair's post-fill field edits (APP only, no device).
Run from repo root. s0 points to a valid, separate 256-byte little-endian buffer.
"""
from hashlib import sha256
from pathlib import Path

APP = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')

def signed(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))

def replay(code, page):
    r = {0:0, 8:0}; pos = 0; events = []
    while pos < len(code):
        h = int.from_bytes(code[pos:pos+2], 'little'); n = 4 if h&3 == 3 else 2
        if pos+n > len(code): raise ValueError('short instruction')
        w = int.from_bytes(code[pos:pos+n], 'little'); pos += n
        if n == 4:
            op = w&127; rd = (w>>7)&31; a = (w>>15)&31; b = (w>>20)&31; f = (w>>12)&7
            if op == 0x37: r[rd] = w & 0xfffff000
            elif op == 0x13 and f in (0,7):
                imm = signed(w>>20,12); r[rd] = ((r[a]+imm) if f == 0 else (r[a]&imm)) & 0xffffffff
            elif op == 0x23 and f in (0,1) and a == 8:
                p = signed((w>>25)<<5 | rd,12); size = 1<<f
                if not 0 <= p <= len(page)-size: raise ValueError('store range')
                page[p:p+size] = r[b].to_bytes(4,'little')[:size]; events.append(('w',p,size))
            else: raise ValueError(hex(w))
        elif h in (0x401c,0xc01c): # c.lw/c.sw a5,0(s0)
            if h == 0x401c: r[15] = int.from_bytes(page[:4],'little'); events.append(('r',0,4))
            else: page[:4] = r[15].to_bytes(4,'little'); events.append(('w',0,4))
        elif h == 0x8fd9: r[15] |= r[14]
        elif h&0xe003 in (0x6001,0x4001) and (h>>7)&31 == 15:
            imm = signed(((h>>12)&1)<<5 | ((h>>2)&31),6)
            r[15] = (imm << (12 if h&0xe000 == 0x6000 else 0)) & 0xffffffff
        else: raise ValueError(hex(h))
    return events

def main():
    b=APP.read_bytes()
    if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP identity')
    code=b[0xb0a2:0xb0cc]
    for i in range(258):
        p=bytearray([0 if i==256 else 255]*256); p[1]=i if i<256 else p[1]; expected=p.copy()
        expected[0:7]=bytes([0,8|(p[1]&2),255,0,255,96,20]); expected[255]=90
        if replay(code,p)!=[('w',255,1),('r',0,4),('w',0,4),('w',4,2),('w',6,1)] or p!=expected: raise ValueError(i)
    print('PASS: 258 post-fill buffers; whole-page bytes and ordered access widths match')

if __name__=='__main__': main()
