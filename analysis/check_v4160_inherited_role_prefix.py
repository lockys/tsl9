"""APP, V1.31, rasm2. Continue the first role without seeding extra RAM or RF registers."""
from pathlib import Path
import runpy
here=Path(__file__).resolve().parent
s=runpy.run_path(str(here/'check_v4160_role_failure_hook_origin.py'))
code=s['code']; ck=s['ck']; word=s['word']; M=0xffffffff
for lo,hi in [(0x6dd16,0x6dd1e),(0x61b1c,0x61b24),(0x55bde,0x55c32),(0x43c4e,0x43c7e),(0x5362e,0x537b6),(0x55bd4,0x55bde),(0x55c48,0x55c52),(0x43e24,0x43e6a),(0x64298,0x6434a),(0x66098,0x66242)]:s['ns']['win'](s['b'],0x40000,lo,hi)

def follow(r,m):
    pc=0x6dd16; visits=[];init_heap=(word(m,0x20003190),word(m,0x2000318c));table=word(m,0x200031c4)
    def v(k):return r[k] if k in r else int(k,0)
    for _ in range(4000):
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        ck(at!=0x20000040)
        if at in (0x43c4e,0x5362e,0x2000039c,0x64298):visits.append((at,r['a0']))
        if o in ('sb','sh','sw','lw','lhu','lbu'):
            d,k=x[1][:-1].split('(');p=(r[k]+int(d))&M;w={'sb':1,'sh':2,'sw':4,'lw':4,'lhu':2,'lbu':1}[o]
            if o.startswith('s'):m.update({p+i:r[t]>>(8*i)&255 for i in range(w)})
            elif any(p+i not in m for i in range(w)):break
            else:r[t]=int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
        elif o in ('ret','jal','jalr','j'):
            if o=='jalr' and '(' in t:
                d,k=t[:-1].split('(');dest=r[k]+int(d)
            else:dest=r['ra'] if o=='ret' else v(x[-1]);
            if o in ('jal','jalr'):r['ra']=pc
            pc=dest&~1
        elif o in ('bleu','bnez','beqz','bne'):
            a=r[t];b=0 if len(x)==2 else v(x[1]);take=a<=b if o=='bleu' else a==0 if o=='beqz' else a!=b
            if take:pc=v(x[-1])
        elif o not in ('fence.i','nop'):
            if len(x)<2:raise ValueError((hex(at),o,x))
            a=v(x[1]);b=v(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):z=a
            elif o in ('lui','auipc'):z=(a<<12)+(at if o=='auipc' else 0)
            elif o in ('add','addi'):z=a+b
            elif o=='slli':z=a<<b
            elif o=='or':z=a|b
            elif o in ('and','andi'):z=a&b
            elif o=='srli':z=a>>b
            elif o=='sltiu':z=int(a<b)
            else:raise ValueError((hex(at),o))
            r[t]=z&M
    else:raise ValueError('step bound')
    ck(visits[:3]==[(0x43c4e,0x5352c),(0x5362e,5),(0x2000039c,0x200033b8)])
    ck(word(m,table+20)==0x5352c and m[0x2000319d]==6 and word(m,s['HOOK'])==0)
    ck(init_heap==(word(m,0x20003190),word(m,0x2000318c)))
    return at,p,w

ends=[]
for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
    for equal in (False,True):
        pc,r,m=s['base']['run'](code,s['a'],s['b'],bytes(range(6)),equal,entry,clock,outer=True)
        s['base']['calibrate'](code,pc,r,m)
        for control in (False,True):
            rr,mm=r.copy(),m.copy();s['mod']['follow'](code,s['b'],rr,mm,control);s['ns']['advance'](code,s['b'],rr,mm,control)
            ck(s['target'](code,s['b'],rr)==(0x401a0,0x6dd16));ends.append(follow(rr,mm))
ck(ends==[(0x660e8,0x40025048,4)]*8)
print('PASS: 8 inherited role prefixes register task 5; no allocation before first missing RF word at 0x660e8')
