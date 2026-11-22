"""APP V131 rasm2. Two roles share one RAM. Six consumers and first role's post-registration helpers are opaque normal returns.
Execute the RF prefix to 660d6. There assume the remaining initializer returns with saved registers restored and
no further memory effects. Both calls from 53654 execute the mapped 296-byte fill.
"""
from pathlib import Path
import re,runpy
g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
w=g['window'];b=g['b'];w(g['a'],32768,0x8eb8,0x8ebe)
for lo,hi in [(0x64298,0x6434a),(0x66098,0x660d6),(0x5366c,0x537b6),(0x537cc,0x537d8),(0x43e24,0x43e6a),(0x61b1c,0x61b5a),(0x55bde,0x55c32),(0x5362e,0x5366c),(0x55bd4,0x55bde),(0x55c48,0x55c52),(0x6dd16,0x6dd86),(0x6d572,0x6d682),(0x43c4e,0x43c7e),(0x6dd86,0x6dda4),(0x5a004,0x5a026),(0x60856,0x6089a),(0x58ef2,0x58f14)]:w(b,0x40000,lo,hi)
ID=0x200035f5;N=0x2000319d;T=0x20004800;M=0xffffffff
OPAQUE={0x4da70,0x46570,0x4a7d6,0x50412,0x6c300,0x4d172,0x4600e,0x2000039c,0x440c2,0x20000332}
def ck(ok,msg):
    if not ok:raise ValueError(msg)
def trace(n,cap,cfg,initial):
    m={};r=dict(sp=0x2000ffc0,s0=0x40000,s1=11,s2=12,ra=0x8eb8,zero=0);pc=0x6dd16;ids=[];handlers=[];status=[];writes=[];sample=[]
    def put(p,k,v):m.update({p+i:v>>(8*i)&255 for i in range(k)})
    def get(p,k):return sum(m[p+i]<<(8*i) for i in range(k))
    def v(s):return r[s] if s in r else int(s,0)
    def addr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
    for p,k,z in [(0x200031ec,4,0x2000418c),(0x2000323e,2,31),(0x200031f0,2,0x7000),(0x200031fa,1,3),(0x200031fc,2,27),(0x4002420c,4,17),(N,1,n),(N+1,1,cap),(0x200031c4,4,T),(ID,1,255),(0x20003201,1,cfg),(0x2000319f,1,initial)]:put(p,k,z)
    reads=[];flag=0x2000319f;second=[];fills=[];tails=[]
    for _ in range(6000):
        if pc in (0x6dda4,0x6de04):break
        if pc==0x60870:second.append((r['a0'],get(ID,1)))
        if pc==0x2000039c and r['ra']==0x53658:
            ck((r['a0'],r['a1'],r['a2'])==(0x200033b8,0,296),'fill arguments');fills.append(len(writes))
        if pc==0x5366c:tails.append((len(writes),get(flag,1),get(ID,1)))
        if pc==0x64298:
            start,old_flag,old_id=tails[-1];obj=0x200033b8;segment=writes[start:]
            ck(r['ra']==0x537b6 and len(segment)==35 and all(obj<=p and p+k<=obj+296 for _,p,k,_ in segment),'initializer writes')
            ck((get(flag,1),get(ID,1))==(old_flag,old_id) and get(obj+60,2)==0x0f0f and get(obj+44,2)==1320,'initializer fields')
            frame=r['sp'];rf_start=len(writes);delay=[0,0]
        if pc in (0x660aa,0x660ba):delay[int(pc==0x660ba)]+=1
        if pc==0x660d6:
            expected=[(0x20003510,1,0),(0x2000350c,4,0),(0x20003504,4,0x40024300),(0x2000353c,4,0x40024200),(0x20003590,4,0x40025000),(0x20003508,4,0x40024100),(frame-4,4,0x537b6),(0x2000351b,1,1),(0x20003538,4,0x2000418c),(0x20003534,4,0x2000429c)]
            expected += [(0x40024200+d,4,z) for d,z in [(20,140),(28,108),(36,140),(44,60),(52,140),(60,60),(68,140),(76,108),(116,0x2000418c),(8,65535),(12,0xf00f)]]
            expected += [(frame-20,4,0x64302)]+[(0x4002500c,4,z) for z in (0x1101,0,0x1101)]
            ck([row[1:] for row in writes[rf_start:]]==expected and delay==[20,20] and r['sp']==frame-32,'RF prefix trace')
            ck((get(flag,1),get(ID,1))==(old_flag,old_id),'RF ID survival')
            sp=frame;r.update({k:get(sp+d,4) for k,d in [('ra',12),('s0',8),('s1',4),('s2',0)]});r['sp']=sp+16;pc=r['ra'];continue
        if pc in OPAQUE and not (pc==0x2000039c and r['ra']==0x53658):r['a0']=0;pc=r['ra'];continue
        if pc==0x43c4e:handlers.append(r['a0'])
        if pc==0x8eb8:status.append(r['a0'])
        at=pc;k,o,x=g['code'][pc];pc+=k;t=x[0]
        if at==0x642ea:
            ck(b[at-0x40000:at-0x40000+2]==bytes.fromhex('f8b3'),'Xwchc byte store');o='sb';t='a4';x=[t,'7(a5)']
        if o in ('lw','lhu','lbu','sw','sh','sb'):
            p=addr(x[1]);nbyte={'lw':4,'sw':4,'sh':2,'lhu':2,'lbu':1,'sb':1}[o]
            if o.startswith('s'):
                put(p,nbyte,r[t]);writes.append((at,p,nbyte,get(p,nbyte)))
                if p==ID:ids.append((at,r[t]&255))
            else:
                r[t]=int.from_bytes(b[p-0x40000:p-0x40000+nbyte],'little') if 0x40000<=p<0x40000+len(b) else get(p,nbyte)
                if at in (0x55be2,0x6085a):reads.append((at,p,r[t]))
                if at==0x6dd92:sample.append((p,r[t]))
        elif o in ('jal','jalr'):
            dest=addr(t) if '(' in t else v(x[-1]);r['ra']=pc;pc=dest&~1
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o.startswith('b'):
            z=0 if len(x)==2 else v(x[1]);y=r[t]
            if {'bleu':y<=z,'beqz':y==0,'bnez':y!=0,'bne':y!=z,'beq':y==z}[o]:pc=v(x[-1])
        elif o not in ('nop','fence.i'):
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):q=y
            elif o in ('auipc','lui'):q=(at if o=='auipc' else 0)+(y<<12)
            elif o in ('add','addi'):q=y+z
            elif o=='or':q=y|z
            elif o=='srli':q=y>>(z&31)
            elif o=='sltiu':q=int(y<z)
            elif o=='andi':q=y&z
            elif o=='slli':q=y<<z
            else:raise ValueError((at,o))
            r[t]=q&M
    live=initial or (n if n<cap else 255)
    ck(reads==[(0x55be2,flag,initial),(0x6085a,flag,live)],'two flag samples')
    hs=([] if initial else [0x5352c])+[0x4dbf2,0x465b4,0x4a808,0x502b4,0x6cc4c,0x4d1b0]+([0x6d26c] if cfg&3 else [])
    candidate=n+6+int(initial==0);result=candidate if cfg&3 and candidate<cap else 255
    next_id=n+len(hs) if n+len(hs)<cap else 255
    ck(second==([] if live else [(next_id,result)]),'second init arguments and shared ID')
    flags=([] if initial else [live])+([] if live else [next_id]);hs+=([] if live else [0x5352c]);slots=min(len(hs),max(0,cap-n))
    ck([(at,p,k,z) for at,p,k,z in writes if p<=flag<p+k]==[(0x53668,flag,1,z) for z in flags],'flag stores')
    ck([z for _,z,_ in tails]==flags,'initializer ID sequence')
    ck(len(fills)==len(flags) and all(writes[start:start+298]==[(0x200003a4,0x4002420c,4,0)]+[(0x200003c0,0x200033b8+i,1,0) for i in range(296)]+[(0x200003b8,0x4002420c,4,0xf00f if index else 17)] for index,start in enumerate(fills)),'mapped fills')
    ck(handlers==hs and get(N,1)==n+slots,'count or handler')
    ck([(p,z) for at,p,k,z in writes if at==0x43c72]==[(T+4*(n+i),h) for i,h in enumerate(hs[:slots])],'task table')
    ck(ids==([(0x6d5b6,result)] if cfg&3 else []) and sample==[(ID,result)],'ID store/load')
    ck(all(p==ID and k==1 and at==0x6d5b6 for at,p,k,z in writes if p<=ID<p+k),'shared ID overlap')
    ck(status==[24 if result==255 else 0] and pc==(0x6dda4 if result==255 else 0x6de04),'status or branch')
    return second,sample
for n,cap,cfg in [(5,29,1),(6,29,1),(5,11,1),(5,29,0),(11,11,1),(248,255,3),(0,29,1)]:
    for initial in (0,1,255):print(n,cap,cfg,initial,'=>',trace(n,cap,cfg,initial))
for cap in range(1,256):
    for cfg in (0,1):trace(0,cap,cfg,0)
print('PASS: 21 regression + 510 repeated-registration paths; RF prefix to 660d6, 25 ordered stores, two 20-iteration software delays per entry; both IDs preserved')
