"""APP, V1.31 carrier, rasm2. Same synthetic RAM from 4da70 through third allocation, optional fill, and the role's tail registration.
Xwchc, both allocator cursors initially at the same free header, null failure hook,
ordinary MMIO, successful accesses. This is not continuous execution from boot.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for l,h in [(0x4da70,0x4dbf2),(0x4edd2,0x4ee72),(0x4efd8,0x4f00c)]: g['window'](g['b'],0x40000,l,h)
C=0x200033b4; H=0x200048a4; IO=0x4002420c; M=0xffffffff

def trace(cap,outer,occupied=0):
    m={}; hits=[]; calls=[]; results=[]; last_fill=[]; table_reads=[]; installs=[]; pc=0x4da70
    table=0x20003358; cb=0x4d916
    r=dict(sp=0x2000ff80,s0=8,s1=9,s2=18,s3=19,s4=20,ra=0x6dd2e,zero=0,a0=5)
    def put(p,w,z): m.update({p+i:(z>>(8*i))&255 for i in range(w)})
    def get(p,w): return sum(m[p+i]<<(8*i) for i in range(w))
    for p,w,z in [(0x20003201,1,14),(C,1,0xa5),(0x20003350,1,outer),(0x20003351,1,2),(IO,4,17),(0x20003190,4,H),(0x20003194,4,H),(0x2000318c,4,H+8+cap),(H,4,H+8+cap),(H+4,2,cap),(H+6,2,0),(0x200031a2,2,cap),(0x20003220,4,0)]: put(p,w,z)
    def val(k):return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&M
    def signed(z):return (z^0x80000000)-0x80000000
    for _ in range(20000):
        if pc==0x20000040:
            calls.append((r['a0'],r['a1'],r['ra']))
        if pc==0x6dd2e:break
        if pc==0x4efe2:
            if r['a0']!=cb or any(get(table+4*i,4) for i in range(12)): raise ValueError('tail entry')
            # Optional diagnostic only: seed occupied prefix after the real clear.
            for i in range(occupied): put(table+4*i,4,cb)
        if pc==cb:raise ValueError('unexpected callback invocation')
        if pc in (0x4ee10,0x4db18,0x4db60,0x4dba0):results.append(r['a0'])
        at=pc; n,op,x=g['code'][pc]; pc+=n;t=x[0]
        if op in ('lw','lbu','lhu','sw','sb','sh'):
            p=addr(x[1]);w={'lw':4,'lbu':1,'lhu':2,'sw':4,'sb':1,'sh':2}[op]
            if op.startswith('s'):
                put(p,w,r[t])
                if at==0x200003c0 and r['ra']==0x4dbc2:last_fill.append((p,w,get(p,w)))
            else:r[t]=get(p,w)
            if at==0x4eff2:table_reads.append((p,r[t]))
            if pc>0x4efe2 and at==0x4effa:installs.append((p,get(p,w)))
            if p<=C<p+w:hits.append((at,op,m[C]))
        elif op in ('jal','jalr','jr','ret','j'):
            dest=r['ra'] if op=='ret' else addr(t) if '(' in t else val(x[-1]);
            if op in ('jal','jalr'):r['ra']=pc
            pc=dest&~1
        elif op.startswith('b'):
            a=r[t]; b=0 if len(x)==2 else val(x[1]); take={'bne':a!=b,'bnez':a!=0,'beqz':a==0,'bltu':a<b,'bleu':a<=b,'blt':signed(a)<signed(b)}[op]
            if take:pc=val(x[-1])
        elif op!='fence.i':
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op in ('li','mv'):z=a
            elif op in ('lui','auipc'):z=(a<<12)+(at if op=='auipc' else 0)
            elif op in ('addi','add'):z=a+b
            elif op=='sub':z=a-b
            elif op=='andi':z=a&b
            elif op=='mul':z=a*b
            elif op=='slli':z=a<<b
            elif op=='srli':z=a>>b
            else:raise ValueError((at,op))
            r[t]=z&M
    else: raise ValueError('step bound')
    p1=H+8; p2=H+316 if outer and cap>=388 else 0
    n2=7 if p2 else 5; used=308+(88 if p2 else 0)
    p3=H+used+8 if cap>=used+16*n2 else 0
    expected=[(300,0x9001,0x4ee10)]+([(80,0x4c04,0x4db18)] if outer else [])+[(16*n2,0x4c05,0x4db60),(60,0x4c06,0x4dba0)]
    p4=p3+16*n2+8 if cap==1024 else 0
    if calls!=expected or results!=[p1]+([p2] if outer else [])+[p3,p4]: raise ValueError((calls,results))
    if get(0x20003318,4)!=p4 or last_fill!=([(p4+i,1,0) for i in range(60)] if p4 else []): raise ValueError('third record area')
    reads=[0x4ee10,0x4ee2c,0x4db42,0x4efdc]+([0x4efdc] if p4 else [])
    if hits!=[(0x4edf4,'sb',5)]+[(pc,'lbu',5) for pc in reads]: raise ValueError(hits)
    free=occupied<12
    if table_reads!=[(table+4*i,cb if i<occupied else 0) for i in range(min(occupied+1,12))]:raise ValueError(table_reads)
    if installs!=([(table+4*occupied,cb)] if free else []) or r['a0']!=(0 if free else 19):raise ValueError(installs)
    if r['sp']!=0x2000ff80 or [r[k] for k in ('s0','s1','s2','s3','s4')]!=[8,9,18,19,20]:raise ValueError('caller frame')

for cap in (300,388,1024):
    for outer in (0,5): trace(cap,outer)
for occupied in range(1,13): trace(300,0,occupied)
print('PASS: 6 continuous traces (4 null, 2 success) install callback in slot 0; 12 occupancy controls; full returns 19')
