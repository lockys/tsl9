"""Trace the APP config call through the page paths and back to the APP status branch (256- and 513-byte fixtures). Args: APP, V1.31, rasm2.
Synthetic source config, stack, MMIO and page; reference RAM mapping and Xwchc assumed.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

def ck(x):
    if not x: raise ValueError('geometry chain mismatch')
a,b=[Path(x).read_bytes() for x in sys.argv[1:3]]
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
code={}; compact='s0 s1 a0 a1 a2 a3 a4 a5'.split()
def window(img,base,lo,hi):
    raw=img[lo-base:hi-base];p=lo
    for line in subprocess.check_output([sys.argv[3],'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,n,h,o,*args=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(h)==raw[p-lo:p-lo+n]);x=''.join(args).split(',')
        if o in ('fld','fsd'):
            w=int.from_bytes(bytes.fromhex(h),'little');q=w&3;f=w>>13;ck(img is b and q in (0,2) and f in (1,5));d=8*((w>>10)&(7 if q==2 else 3))+2*(w>>5&3)+(0 if q==2 else w>>12&1);o=('lhu' if q==2 else 'lbu') if f==1 else ('sh' if q==2 else 'sb');x=[compact[w>>2&7],f'{d}({compact[w>>7&7]})']
        code[p]=n,o,x;p+=n
    ck(p==hi)
for l,h in [(0x197f0,0x1995c),(0x8520,0x854a),(0x19124,0x19142),(0x1908c,0x1909e),(0x188e2,0x189fe),(0x19160,0x1917e),(0x18a66,0x18aa6),(0x1979a,0x197b8),(0x197be,0x197f0),(0x19764,0x1979a),(0x18e98,0x18f56),(0x19ae6,0x19af2)]:window(a,0x8000,l,h)
for l,h in [(0x43c7e,0x43d5c),(0x43b3e,0x43c4e),(0x430e0,0x43174),(0x4329a,0x432a4),(0x44022,0x440c2)]:window(b,0x40000,l,h)
for l,h in [(0x40,0x1e4),(0x332,0x36c),(0x39c,0x3ca),(0x4bc,0x4ee)]:window(b,0x20000000-0x270,0x20000000+l,0x20000000+h)
M=0xffffffff;C=0x200031ec;U=0x2000ff80;S=U-32;A=0x08077c00;B=0x40012400
for length,count in [(0,3),(513,7),(1,0),(32000,3)]:
 for equal in (False,True):
    mem={};events=[];vis=[];polls=0;pc=0x19ae6;r={'zero':0,'sp':S+16,'ra':0,'a5':0x40000,'s0':0x1111,'s1':0x2222,**{'s'+str(i):i for i in range(2,12)}}
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    put(U,64,0);put(U,4,0x2000418c);put(U+4,2,0x7000);put(U+8,4,A);put(U+12,4,length+(count<<16)+(8<<24));put(U+44,4,0x197f0);put(U+56,4,0x1979a);put(U+60,4,0x197be);put(A,4,A^int(not equal));put(0x4004c,4,int.from_bytes(b[76:80],'little'))
    put(0x400a4,4,int.from_bytes(b[164:168],'little'))
    for p in [0x4002420c,0x40021004,0x40021018,0x4002100c,B+76,*range(B,B+60,4)]:put(p,4,p)
    request=[];fill=[];written=[];slots=[];entry=[];stage=[];io=[];L=length or 256
    put(0x40022010,4,0);put(0x4002200c,4,0)  # synthetic ready controller
    timer=0xe000f000;r['gp']=0x20004000;put(r['gp']+382,1,73);put(timer,4,0);put(timer+4,4,0)
    K=0x200031bc;acct=0x200031a2;freed=[];cleanup=[];aligned=[];returns=[]
    levels=[];registration=[]
    for step in range(40000):
        if pc in (0x43c06,0x43d4e,0x19aee):levels.append((pc,r['a0'],r['sp']))
        if pc==0x440c0:returns.append((r['a0'],r['s0'],r['s2'],r['sp']))
        if pc==0x20000110:
            ptr=r['a0'];tail=get(ptr-8,4)
            freed.append((ptr,r['ra'],get(ptr-2,2),get(ptr-4,2),get(tail,4),get(tail+4,2),get(acct,2),get(0x4002420c,4)))
        if pc in (0x19af0,0x19af2) or (pc==0x44092 and L<4):break
        if pc==0x197be:entry.append(tuple(r[k] for k in ('a0','a1','a2','s2','sp','ra')))
        if 0x44022 in vis:
            if pc==0x20000040:request.append((r['a0'],r['a1']))
            if pc==0x2000039c:fill.append((r['a0'],r['a1'],r['a2']))
            if pc==0x44076:slots.append(r['a0'])
        if pc in (0x197f0,0x43d3a,0x43104,0x20000040,0x43be2,0x44022,0x1979a):vis.append(pc)
        at=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda s:r[s] if s in r else int(s,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
        if o in ('sw','sh','sb','lw','lhu','lbu'):
            p=addr(x[1]);w={'sw':4,'lw':4,'sh':2,'lhu':2,'sb':1,'lbu':1}[o]
            if o[0]=='s':put(p,w,r[t])
            elif at==0x18a8e:ck(p==B);r[t]=2 if polls else 0;polls+=1
            elif at==0x1978c:ck(p==timer+4);r[t]=1  # synthetic timer has expired
            else:r[t]=get(p,w)
            if 0x43c06<=at<0x43c4e and o[0]=='s':registration.append((p,w,r[t]&((1<<(8*w))-1)))
            if freed and o[0]=='s' and not levels:cleanup.append((at,p,w,r[t]&((1<<(8*w))-1)))
            if at==0x18ed6:aligned.append((p,r[t]))
            if at in (0x18f1e,0x18f26):io.append((o,p,r[t]))
            if fill and at==0x200003c0:written.append((p,r[t]&255))
            if at in (0x440bc,0x197c0,0x197c2,0x197c4):stage.append((at,p,w,r[t]))
            if p<C+15 and p+w>C+12:events.append((at,o,p-C,w))
        elif o=='jal':r['ra']=pc;pc=v(x[-1])
        elif o=='jalr':dest=(addr(t) if '(' in t else r[t])&~1;r['ra']=pc;pc=dest
        elif o=='j':pc=v(t)
        elif o=='ret':pc=r['ra']&~1
        elif o=='blt':
            if (r[t]^0x80000000)<(v(x[1])^0x80000000):pc=v(x[-1])
        elif o in ('beq','bne','beqz','bnez','bltu','bleu'):
            y=0 if o.endswith('z') else v(x[1]);take=r[t]==y if o.startswith('beq') else r[t]!=y if o.startswith('bne') else r[t]<y if o=='bltu' else r[t]<=y;pc=v(x[-1]) if take else pc
        elif o in ('li','mv','lui','auipc','snez','not'):
            y=v(x[1]);r[t]=((y<<12)+at if o=='auipc' else y<<12 if o=='lui' else int(y!=0) if o=='snez' else ~y if o=='not' else y)&M
        elif o in ('add','addi','sub','and','andi','or','ori','mul','sll','slli','srli'):
            y,z=map(v,x[1:]);r[t]=(y+z if o in ('add','addi') else y-z if o=='sub' else y*z if o=='mul' else y&z if o in ('and','andi') else y|z if o in ('or','ori') else y>>(z&31) if o=='srli' else y<<(z&31))&M
        elif o!='fence.i':raise ValueError((hex(at),o))
    ck(vis==[0x197f0,0x43d3a,0x43104,0x20000040,0x43be2,0x44022,0x1979a]+([] if equal else [0x20000040]) and polls==2)
    defaults=[(0x43cf0,'lhu',12,2)]+([] if length else [(0x43cf8,'sh',12,2)])+[(0x43cfa,'lbu',14,1)]+([] if count else [(0x43d00,'sb',14,1)])
    success=not equal and length!=32000;callback=success and L>=4
    expected=[] if equal else [(0x44060,'lhu',12,2)]
    if success:expected += [(0x4407e,'lhu',12,2),(0x4408e,'lbu',14,1)]
    if callback:expected += [(0x440ac,'lhu',12,2),(0x4408e,'lbu',14,1)]*count
    ck(events[6:]==defaults+expected)
    ck([e[1:] for e in events[:6]]==[('sb',i,1) for i in (12,13,14)*2]);ck(get(C+12,2)==(length or 256) and get(C+14,1)==(count or 1))
    ck(request==([] if equal else [(L,78)]) and pc==(0x44092 if success and not callback else 0x19af2))
    if pc==0x19af2:
        inner=int(not callback);table=get(0x200031c4,4)
        ck(levels==[(0x43c06,inner,S-16),(0x43d4e,inner,S),(0x19aee,0,S+16)])
        ck((r['s0'],r['s1'])==(0x1111,0x2222))
        ck(registration==[(table,4,0x432a4),(table+4,4,0x43326),(0x2000319d,1,3),(table+8,4,0x43326)])
    else:ck(not levels and not registration)
    if success:
        P,=slots;ck(P!=0 and fill==[(P,255,L)] and get(P-2,2)==(0 if callback else 78))
        ck(written==[(P+i,255) for i in range(L)])
        if callback:
            T=S-16-32;F=T-32
            pages=[A+i*L for i in range(count)]
            ck(entry==[(page,L//4,P,i+1,T,0x440c0) for i,page in enumerate(pages)])
            ck(returns==[(0,C,i+1,T) for i in range(count)] and r['a0']==0)
            (ptr,ra,tag,size,end,rest,available,control),=freed
            ck((ptr,ra,tag,size)==(P,0x440a0,78,(L+3)&~3))
            ck(cleanup==[(0x20000118,0x4002420c,4,0),(0x20000178,P-2,2,0),
                (0x20000186,acct,2,(available+size)&65535),(0x200001ce,P-4,2,(size+8+rest)&65535),
                (0x200001d0,P-8,4,end),(0x200001d6,acct,2,(available+size+8)&65535),
                (0x20000122,0x4002420c,4,control),(0x440a2,K,4,0),(0x440a6,K+4,4,0)])
            ck(get(K,8)==0)
            ck(aligned==[(0x40022014,page&~255) for page in pages])
            pairs=[];stages=[]
            for page in pages:
                stages.extend([(0x440bc,P,4,page),(0x197c0,F+28,4,0x440c0),(0x197c2,F+24,4,C),(0x197c4,F+12,4,P)])
                for off in range(0,256,4):
                    data=page if off==0 else M
                    pairs.extend([('lw',P+off,data),('sw',(page&~255)+off,data)])
            ck(io==pairs and stage==stages)
            ck(get(P,4)==pages[-1] and all(get(P+i,1)==255 for i in range(4,L)))
        else:ck(get(P,L)==(1<<(8*L))-1 and (r['s2'],r['a5'],r['a2'])==(0,count or 1,P))
    if not callback:ck(not entry and not stage and not io and not aligned and not returns and not freed and not cleanup)
    if not success:ck(not fill and not written and slots==([] if equal else [0]) and (equal or get(0x200031bc,4)==0))
print('PASS: 8 chains; 3+7 page returns, 640 paired word transfers, 7 APP zero branches (5 inner ones, 2 inner zeros); 1 count-only cutoff')
