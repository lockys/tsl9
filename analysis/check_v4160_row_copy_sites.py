"""Offline APP census of JAL/J and standard C.J/C.JAL encodings to 0x82a8.
Classify selected local setup paths, including shared tails in the dispatcher.
No assertion of execution order, ABI, indirect edges, or exclusive RAM ownership.
"""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(ok):
    if not ok: raise ValueError('row-copy census mismatch')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n],'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def cj(p,h):
    d=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5
    return p+sx(d,12)
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
edges={}
for p in range(32768,32768+len(b),2):
    w=u(p,4); h=w&65535
    if w&127==111:
        d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
        if p+sx(d,21)==0x82a8: edges[p]=w>>7&31
    if h&0xe003 in (0x2001,0xa001): ck(cj(p,h)!=0x82a8)
# (call PC, start PC, expected row); each intervening instruction must be
# either a literal for a0/a1 or a whitelisted non-clobbering instruction.
reads=[(0xb600,0xb5fa,10),(0xc7d0,0xc7cc,8),(0xc838,0xc834,8),(0xd7e2,0xd7dc,8),(0xed7e,0xed7a,9),(0xedfc,0xedf6,9),(0xf4da,0xf4d4,2),(0xf584,0xf57c,2),(0xfd48,0xfd42,13),(0xfdcc,0xfdc4,13),(0x14572,0x1456e,1),(0x1459c,0x14590,11),(0x145e2,0x145b4,5),(0x14632,0x14628,6),(0x1465c,0x14650,7),(0x14676,0x1466e,3),(0x14770,0x1476c,4),(0x17d10,0x17d0c,16),(0x17e20,0x17e1c,17),(0x1827a,0x18276,16),(0x1836a,0x18366,17)]
writes=[(0x14e6c,0x14e68,2),(0x14ff2,0x14fee,15),(0x1506e,0x1506a,0),(0x150a2,0x15098,1),(0x15166,0x15162,5),(0x151bc,0x151b8,8),(0x15204,0x15200,9),(0x15234,0x1522e,13),(0x152c0,0x152bc,18)]
for rows,direction in ((reads,1),(writes,0)):
    for end,p,row in rows:
        r={}
        while p<end:
            h=u(p,2); reg=h>>7&31
            if h&0xe003==0x4001 and reg in (10,11): r[reg]=sx((h>>12&1)<<5|(h>>2&31),6)
            elif h&3==3:
                w=u(p,4);ck(w&127==35 or (w&127==3 and (w>>7&31) in (14,15)));p+=2
            else: ck(h in (0xce06,0xcc22,0x07a2,0x8fd9,0x97ba,0x0762,0xda3e,0x0742,0xdc3e,0xc0ba,0x4422,0x40b2,0x0141,0x8622))
            p+=2
        ck(p==end and r=={10:direction,11:row})
ck(edges=={pc:(0 if pc==0x150a2 else 1) for pc,_,_ in reads+writes+[(0x184c6,0,0)]})
# Alternate short-jump predecessors select additional fixed rows at two sites.
alt={0x14f44:7,0x15118:3,0x1512a:4,0x151b4:6,0x1520e:10,0x15220:11,0x15260:12,0x1527c:14,0x1529a:16,0x152ac:17}
for p,row in alt.items():
    ck(u(p-2,2)==0x4581+(row<<2) and u(p,2)&0xe003==0xa001)
    ck(cj(p,u(p,2))==(0x15202 if row==10 else 0x1509a))
ck(sorted([i for _,_,i in writes]+list(alt.values()))==list(range(19)))
# Unsigned input >9 branches away; admitted inputs choose 16+(4<input), read only.
ck(b[0x184b2-32768:0x184c6-32768].hex()=='a54463e0a4129145b3b5a5005008c1052a840545')
print('PASS: 31 JAL/J sites; 21 fixed read, 1 computed read (16/17), 9 write sites; 19 fixed write setups, row 13 only at 0x15234 on these paths')
