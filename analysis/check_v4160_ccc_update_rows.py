"""APP and V1.31 reference sites, followed by a finite first-match model."""
from itertools import product
from collections import Counter
from pathlib import Path
from hashlib import sha256
import sys


def need(ok):
    if not ok: raise ValueError('unexpected CCC evidence')


def check(app, carrier):
    a,d=(Path(p).read_bytes() for p in (app,carrier))
    need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    need(sha256(d).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    need([int.from_bytes(d[i:i+4],'little') for i in range(312,328,4)]==[0x4cfd0,0x4b456,0x4b46c,0x4b4a4])
    need(a[0x8be:0x8ca].hex()=='b707040003a3471485470283' and a[0xfaa:0xfb8].hex()=='832784134165938501087d158297')
    for pc,reg,off,width in [(0x4b490,9,0,2),(0x4b492,8,2,1),(0x4b34e,13,0,2),(0x4cfea,15,0,2)]:
        h=int.from_bytes(d[pc-0x40000:pc-0x40000+2],'little')
        need(h>>13==5 and ((h>>7)&7)+8==10 and ((h>>2)&7)+8==reg and (h&3)==(2 if width==2 else 0) and (((h>>10)&7)*8+((h>>5)&3)*2)==off and not h&0x1000)
    c=Counter(); key=7; free=65535
    for n in range(4):
        for rows in product(product((key,8,free),(0,1,3)),repeat=n):
            for v in (0,1):
                new=list(rows); first=next((i for i,r in enumerate(rows) if r[0]==key),None); prev=0 if first is None else rows[first][1]; i=first
                if prev==v: t='same'
                else:
                    if i is None: i=next((j for j,r in enumerate(rows) if r[0]==free),None)
                    if i is None: t='full'
                    else: t='set' if first is not None else 'claim'; new[i]=(key,v)
                val=next((b for k,b in new if k==key),0)
                need(val==(prev if t=='full' else v) and all(old==new[j] for j,old in enumerate(rows) if j!=i)); c[t]+=1
    print('PASS: APP sites, 4 slots, 4 Xwchc stores;',dict(c),'cases',sum(c.values()))


if __name__=='__main__': check(*sys.argv[1:])
