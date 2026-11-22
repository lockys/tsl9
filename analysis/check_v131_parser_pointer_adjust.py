"""Args: APP, V1.31, rasm2. Parser success arm and candidate RAM pointer helper."""
from pathlib import Path
import re,runpy
G=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
G['window'](G['b'],0x40000,0x4df1e,0x4df3a)
G['window'](G['b'],0x20000000-0x270,0x200001e4,0x2000021c)
G['window'](G['b'],0x40000,0x4e1ae,0x4e1c2)
G['window'](G['b'],0x40000,0x4df18,0x4df1a)
code=G['code'];mask=0xffffffff
for at,op,args in [(0x4e1ae,'addi',['sp','sp','-48']),(0x4e1ba,'addi',['a0','sp','24']),(0x4e1be,'jal',['ra','0x4ded0']),(0x4df18,'mv',['s2','a0'])]:
    if code[at][1:]!=(op,args):raise ValueError('caller output location')

def case(p,s,kind):
    head=0x20004800;mid=head+32;end=mid+48;msg=0x20005700;out=s-24
    r=dict(s3=msg,s2=out,s1=20,s0=5);mem={msg+8:p,0x20003194:head,0x2000318c:end,head:mid,mid:end};writes=[];loads=[];pc=0x4df1e
    for _ in range(64):
        if pc==0x4df3a:break
        at=pc;n,op,x=code[pc];pc+=n;t=x[0]
        def addr(k):
            off,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(off))&mask
        if op=='lw':
            a=addr(x[1]);loads.append(a);r[t]=mem[a]
        elif op in ('sh','sw'):writes.append((at,addr(x[1]),2 if op=='sh' else 4,r[t]))
        elif op in ('lui','auipc','li','mv','sub','addi'):
            a=r[x[1]] if x[1] in r else int(x[1],0);b=(r[x[2]] if x[2] in r else int(x[2],0)) if len(x)==3 else 0
            r[t]=((a<<12)+(at if op=='auipc' else 0) if op in ('auipc','lui') else a-b if op=='sub' else a+b)&mask
        elif op=='jalr':dest=addr(t)&~1;r['ra']=pc;pc=dest
        elif op in ('bleu','bltu','bne'):
            a,b=r[t],r[x[1]]
            if {'bleu':a<=b,'bltu':a<b,'bne':a!=b}[op]:pc=int(x[-1],0)
        elif op=='j':pc=int(t,0)
        elif op=='ret':pc=r['ra']&~1
        else:raise ValueError((at,op))
    else:raise ValueError('step bound')
    q=(p+4)&mask;valid=any(lo<=p<hi and lo<=q<hi for lo,hi in [(head+8,mid),(mid+8,end)])
    expected=q if valid else p
    if writes!=[(0x4df22,out+2,2,20),(0x4df26,out,2,5),(0x4df34,out+4,4,expected)] or r['a0']!=0:raise ValueError('output')
    if loads[:3]!=[msg+8,0x20003194,0x2000318c] or any(a not in (head,mid) for a in loads[3:]):raise ValueError('unexpected read')
    if any(a<=0x20002f9c<a+w for _,a,w,_ in writes):raise ValueError('flag overlap')
    kind[valid]+=1

kind=[0,0]
for s in (0x2000ff80,0x2000ffc0):
    for p in [*range(0x200047ff,0x20004852),0,0xfffffffc]:case(p,s,kind)
print('PASS: unchanged/advanced pointer cases',kind,'; 3 stack stores only; no payload copy or flag store')
