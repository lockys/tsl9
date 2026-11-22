"""Track dispatch index to APP retry arguments. No timer provider is executed."""
from pathlib import Path
from hashlib import sha256

def need(ok):
    if not ok: raise ValueError('retry ID evidence mismatch')

def load(path, digest):
    data = Path(path).read_bytes(); need(sha256(data).hexdigest() == digest); return data

app = load('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
rom = load('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')

def pin(data,off,h):
    raw=bytes.fromhex(h); need(data[off:off+len(raw)]==raw)

pin(app,0xf05a,'83a70408 17050000 130525ea 1389b116 8297 37140140 2300a900')
pin(rom,0xb5e,'0345c419 b7370020 83a7471c 13172500 b73a0020 ba97 9c43 239e0a1c 8297')
pin(app,0xef7e,'aa84 0145 ddd3 0545 eff03ff0 09ed 0945 eff0bfef 09e9')
pin(app,0xefa4,'b7070400 bc4f 13060003 8545 2685 8297')
need([int.from_bytes(rom[k:k+4],'little') for k in (128,88)]==[0x43c4e,0x43728])

def move(off,r):
    h=int.from_bytes(app[off:off+2],'little'); need(h&0xf003==0x8002)
    r[h>>7&31]=r[h>>2&31]

def dispatch(idx,rows):
    r={8:0x20003000}; mem={0x2000319c:idx,0x200031c4:0x200047f4,**rows}
    pc=0xb5e
    while pc<=0xb7a:
        w=int.from_bytes(rom[pc:pc+4],'little'); h=w&65535
        d,a=w>>7&31,w>>15&31
        if h&3!=3:
            if h==0x97ba: r[15]=(r[15]+r[14])&0xffffffff
            elif h==0x439c: r[15]=mem[r[15]]
            elif h==0x9782: return r[15]&~1,r[10]
            else: raise ValueError(hex(pc))
            pc+=2; continue
        if w&127==0x37: r[d]=w&0xfffff000
        elif w&0x707f in (0x4003,0x2003): r[d]=mem[r[a]+(w>>20)]
        elif w&0x707f==0x1013: r[d]=r[a]<<(w>>20&31)
        elif pc!=0xb76: raise ValueError(hex(pc))  # pinned clear, separate from table
        pc+=4
    raise ValueError('missing dispatch')

# Isolate the identity flow from the two setup calls. Model only the normal ABI.
for index in range(255):
    for poll_returns in ((1,),(0,1)):
        other=(index+1)%255
        rows={0x200047f4+4*index:0x16f00,0x200047f4+4*other:0x901a}
        target,arg=dispatch(index,rows); need(target==0x16f00 and arg==index)
        need(dispatch(other,rows)==(0x901a,other))
        r={10:arg}; move(0xef7e,r)
        for val in poll_returns: r[10]=val
        move(0xefb0,r); need(r[10]==index)
        # Same handler at a different table slot would receive that other index.
        rows[0x200047f4+4*other]=0x16f00
        target,arg=dispatch(other,rows); need(target==0x16f00)
        r={10:arg}; move(0xef7e,r); r[10]=1
        move(0xefb0,r); need(r[10]!=index and r[10]==other)
print('PASS: 255 possible successful IDs x 2 failure paths; alternate-index controls')
