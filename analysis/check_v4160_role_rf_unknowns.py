"""CLI: APP V131 rasm2. Treat each RF sample as a fresh unconstrained 32-bit word."""
from pathlib import Path
import runpy
D=runpy.run_path(str(Path(__file__).with_name('check_v4160_inherited_role_prefix.py')))
s=D['s'];code=D['code'];ck=D['ck'];M=D['M']
s['ns']['win'](s['b'],0x40000,0x638ea,0x63944)
s['ns']['win'](s['b'],0x40000,0x641b0,0x641fc)
fields=runpy.run_path(str(Path(__file__).with_name('v131_rf_register_return.py')))['FIELDS']

def resume(r,m):
    pc=0x660e8;loads=[];stores=[];branches=[]; calls=[]
    def v(x):return r[x] if x in r else int(x,0)
    def scalar(x):
        if not isinstance(x,int):raise ValueError('symbolic address, branch or unexpected operand')
        return x
    for _ in range(280):
        if pc==0x63eda:break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('sw','lw','lbu'):
            d,k=x[1][:-1].split('(');p=(scalar(r[k])+int(d))&M;w=1 if o=='lbu' else 4
            if 0x40024000<=p<0x40026000:
                if o=='sw':stores.append((p,r[t]))
                else:ck(o=='lw');r[t]=(len(loads),M,0);loads.append(p)
            elif o=='sw':
                z=scalar(r[t]);m.update({p+i:(z>>(8*i))&255 for i in range(w)})
            else:r[t]=int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
        elif o in ('and','andi','or','ori'):
            a,b=v(x[1]),v(x[2]);is_and=o.startswith('and')
            if isinstance(b,tuple):a,b=b,a
            b=scalar(b)&M
            if isinstance(a,tuple):
                i,mask,bits=a;r[t]=(i,mask&b,bits&b) if is_and else (i,mask&~b,bits|b)
            else:r[t]=(a&b if is_and else a|b)&M
        elif o in ('ret','j','jal'):
            dest=scalar(r['ra'] if o=='ret' else v(x[-1]));
            if o=='jal':r['ra']=pc;calls.append(dest)
            pc=dest&~1
        elif o in ('beq','bne'):
            same=scalar(r[t])==scalar(r[x[1]]);branches.append((at,same));
            if same==(o=='beq'):pc=v(x[-1])
        elif o!='fence.i':
            a=scalar(v(x[1]));b=scalar(v(x[2])) if len(x)>2 else 0
            if o=='lui':z=a<<12
            elif o=='li':z=a
            elif o=='addi':z=a+b
            elif o=='slli':z=a<<b
            else:raise ValueError((hex(at),o))
            r[t]=z&M
    else:raise ValueError('step limit')
    ck(loads[:28]==[0x40025000+d for d,_,_ in fields]); ck(stores[:28]==[(0x40025000+d,(i,M&~(c|b),b)) for i,(d,c,b) in enumerate(fields)])
    ck(branches==[(0x641cc,False),(0x641d2,False),(0x641e6,True)] and calls==[0x638ea,0x63eda] and r['a0']==13)
    ck(s['word'](m,s['HOOK'])==0 and len(loads)==32 and len(stores)==35)

for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
    for equal in (False,True):
        pc,r,m=s['base']['run'](code,s['a'],s['b'],bytes(range(6)),equal,entry,clock,outer=True);s['base']['calibrate'](code,pc,r,m)
        for control in (False,True):
            rr,mm=r.copy(),m.copy();s['mod']['follow'](code,s['b'],rr,mm,control);s['ns']['advance'](code,s['b'],rr,mm,control)
            ck(s['target'](code,s['b'],rr)==(0x401a0,0x6dd16));ck(D['follow'](rr,mm)==(0x660e8,0x40025048,4));resume(rr,mm)
print('PASS: 8 inherited paths; 32 fresh RF words each, 28 masked updates checked; three concrete branches to 0x63eda(13)')
