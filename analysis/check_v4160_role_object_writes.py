"""Args: APP V131 rasm2. Trace 5366c until the call at 537b2, including 43e24.
Conditional reference RAM/Xwchc, object from preceding initialization, no interference.
Vary the initial feature bits to test whether the initializer overwrites them.
"""
from pathlib import Path
import re,runpy

OBJ=0x200033b8
CFG=0x200031ec
ID=0x200035f5

def need(ok,msg):
    if not ok:raise ValueError(msg)

def trace(code,level,length,features):
    pc=0x5366c;r=dict(zero=0,s1=0x20003000,s0=11);m={};stores=[];sample=[];taken=[]
    def put(p,w,z):m.update({p+i:z>>(8*i)&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    def v(k):return r[k] if k in r else int(k,0)
    def adr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&0xffffffff
    for i in range(296):put(OBJ+i,1,0)
    put(ID,1,11);put(0x2000323e,2,level);put(CFG+4,2,0x7000);put(CFG+14,1,3);put(CFG+16,2,length)
    for i in range(2):put(OBJ+60+i,1,(features>>i&1)*4)
    for _ in range(180):
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('sb','sh','sw','lbu','lhu','lw'):
            p=adr(x[1]);w={'sb':1,'sh':2,'sw':4,'lbu':1,'lhu':2,'lw':4}[o]
            if o.startswith('s'):put(p,w,r[t]);stores.append((p,w))
            else:r[t]=get(p,w)
        elif o=='jal':
            dest=v(x[-1]);r['ra']=pc;pc=dest
            if at==0x537b2:break
            need((at,pc)==(0x536fe,0x43e24),'unexpected call')
        elif o=='ret':sample.append(r['a0']);pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('beqz','bleu'):
            if (v(t)==0 if o=='beqz' else v(t)<=v(x[1])):pc=v(x[-1]);taken.append(at)
        else:
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o=='lui':q=y<<12
            elif o in ('li','mv'):q=y
            elif o=='addi':q=y+z
            elif o=='or':q=y|z
            elif o=='andi':q=y&z
            elif o=='slli':q=y<<(z&31)
            elif o=='srli':q=y>>(z&31)
            elif o=='sltiu':q=int(y<z)
            else:raise ValueError((at,o))
            r[t]=q&0xffffffff
    need(pc==0x64298 and sample==[sum(level<=t for t in (20,30,50,75,100,150,250))],'threshold or next call')
    need(all(OBJ<=p and p+w<=OBJ+296 for p,w in stores) and get(ID,1)==11,'store outside object')
    need(get(OBJ+60,2)==0x0f0f and 0x53758 not in taken and 0x5376c not in taken,'initialized feature bits')
    l=min(length,251);need(get(OBJ+3,1)==sample[0] and all(get(OBJ+i,2)==(l+138)*8 for i in (44,48)),'derived fields')
    return len(stores)

if __name__=='__main__':
    g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
    for lo,hi in [(0x5366c,0x537b6),(0x537cc,0x537d8),(0x43e24,0x43e6a)]:g['window'](g['b'],0x40000,lo,hi)
    cases=[trace(g['code'],level,l,f) for level in (0,20,21,30,31,50,51,75,76,100,101,150,151,250,251,65535) for l in (0,26,27,250,251,252,65535) for f in range(4)]
    print(f'PASS: {len(cases)} traces; store counts {sorted(set(cases))}, all in 296-byte object; read-only threshold call, stop at 64298')
