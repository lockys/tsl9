"""Continue eight calibrated states through the V1.31 clock-config provider and APP task reload.
CLI as check_v4160_calibration_return.py. Same synthetic MMIO/clock assumptions, not live firmware.
"""
from pathlib import Path
import re,runpy
M=0xffffffff
def ck(x,msg):
    if not x:raise ValueError(msg)
def s(x):return (x^0x80000000)-0x80000000

def follow(code,rom,r,m,control=False):
    pc=0x19bac;C=r['sp'];task=r['gp']+388; ticks=0; hits=[];copies=[]
    head=0x200031e8; node=0x200043b4; scheduling=[]; changes=[]; samples=[]; mm=0x4002420c
    def get(p,w):return sum((rom[p+i-0x40000] if 0x40000<=p+i<0x40000+len(rom) else m[p+i])<<(8*i) for i in range(w))
    def put(p,w,z):m.update({p+i:z>>(8*i)&255 for i in range(w)})
    ck(get(task,1)==3 and get(0x2000321c,4)==0x197b8,'initial task/hook')
    config=bytes.fromhex('c6910100ffffffff803ee80300000000')
    for _ in range(20000):
        if pc==0x8eb0:break
        if pc==0x43728:
            ident=150 if control else 3
            ck((r['a0'],r['a1'],r['a2'],r['ra'],get(0x2000319d,1),get(head,4))==(ident,8192,192000,0x8eb0,4,0),'scheduler entry')
            initial_mm=get(mm,4)
        if pc in (0x43728,0x437ca,0x20000314,0x20000040,0x43850,0x437c8):scheduling.append(pc)
        if pc==0x437cc:samples.append(r['a0'])
        if pc==0x20000040:ck((r['a0'],r['a1'])==(16,0xff03),'timer allocation')
        if pc in (0x43f46,0x197b8,0x43f62,0x20000332,0x43b0a,0x43d62,0x19bce,0x19b3a):hits.append(pc)
        if pc==0x43f62:ck(get(C-20,4)==C,'saved pointer')
        if pc==0x20000332:ck((r['a0'],r['a1'],r['a2'])==(0x20003234,C,16),'copy args')
        if pc==0x19b3a:
            ck((r['s0'],get(task,1),r['a0'])==(task,3,0),'pre reload')
            if control:put(task,1,0x96)
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        def v(k):return r[k] if k in r else int(k,0)
        def addr(k):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[k]+int(d))&M
        if o in ('lw','lhu','lbu','sw','sh','sb'):
            p=addr(x[1]);w={'lw':4,'sw':4,'lhu':2,'sh':2,'sb':1,'lbu':1}[o]
            if o.startswith('s'):
                ck(not p<=task<p+w,'store overlaps task');put(p,w,r[t]);
                if 0x20003234<=p<0x20003244:copies.append((p,w,r[t]&255))
                if scheduling and (p==head or node<=p<node+16):changes.append((at,p,w,r[t]&((1<<(8*w))-1)))
                continue
            z=get(p,w)
            if at in (0x1933e,0x193ac,0x19456,0x194cc,0x19592,0x19608,0x193a0,0x194bc,0x195f8):
                ck((p,w)==(0x4002204c,2),'cal poll');z=z&32767 if at in (0x193a0,0x194bc,0x195f8) else z|32768
            if at in (0x191de,0x191e2):ck(p==0x4000281c,'RTC low');z=ticks
            if at==0x19b3a:ck((p,w)==(task,1),'LBU source')
            r[t]=z
        elif o in ('jal','jalr'):
            k=x[-1];target=addr(k) if '(' in k else v(k);r['ra']=pc;pc=target&~1;ticks+=int(pc==0x191c6)
        elif o=='ret':pc=r['ra']&~1
        elif o in ('j','jr'):pc=v(t)&~1
        elif o.startswith('b'):
            z=r[t];y=0 if len(x)==2 else v(x[1]);test={'beq':z==y,'beqz':z==0,'bne':z!=y,'bnez':z!=0,'blez':s(z)<=0,'bgez':s(z)>=0,'bltz':s(z)<0,'blt':s(z)<s(y),'ble':s(z)<=s(y),'bltu':z<y,'bleu':z<=y}[o]
            if test:pc=v(x[-1])
        elif o!='fence.i':
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('li','mv'):q=y
            elif o=='auipc':q=at+(y<<12)
            elif o=='lui':q=y<<12
            elif o in ('add','addi'):q=y+z
            elif o=='sub':q=y-z
            elif o=='mul':q=y*z
            elif o=='mulhu':q=(y*z)>>32
            elif o=='sltu':q=int(y<z)
            elif o=='div':q=-1 if not z else abs(s(y))//abs(s(z))*(-1 if (s(y)<0)!=(s(z)<0) else 1)
            elif o=='divu':q=y//z if z else M
            elif o=='remu':q=y%z if z else y
            elif o in ('or','ori'):q=y|z
            elif o in ('and','andi'):q=y&z
            elif o in ('sll','slli'):q=y<<(z&31)
            elif o in ('srl','srli'):q=y>>(z&31)
            elif o=='srai':q=s(y)>>(z&31)
            else:raise ValueError((at,o))
            r[t]=q&M
    ck(hits==[0x43f46,0x197b8,0x43f62,0x20000332,0x43b0a,0x43d62,0x19bce,0x19b3a],'path')
    ck(copies==[(0x20003234+i,1,b) for i,b in enumerate(config)],'copy sequence')
    ck((pc,r['a0'],r['sp'],get(mm,4))==(0x8eb0,int(not control),C+48,initial_mm),'scheduler return')
    if control:
        ck(scheduling==[0x43728,0x437c8] and not changes and not samples and get(head,4)==0,'rejected ID')
    else:
        ck(scheduling==[0x43728,0x437ca,0x20000314,0x20000040,0x43850,0x437c8] and len(samples)==1,'create path')
        due=samples[0]+(16000*192000+800)//1600
        ck(due<M and changes==[(0x43850,head,4,node),(0x43856,node+12,4,0),(0x4385a,node+8,4,due),(0x4385c,node+2,2,8192),(0x43860,node,1,3),(0x43862,node+1,1,1),(0x43864,node+4,4,0)],'installation order')
        ck(get(head,4)==node and [get(node+d,w) for d,w in [(0,1),(1,1),(2,2),(4,4),(8,4),(12,4)]]==[3,1,8192,0,due,0],'completed timer')

if __name__=='__main__':
    base=runpy.run_path(str(Path(__file__).with_name('check_v4160_calibration_return.py')),run_name='__main__'); win=base['win'];a,b=base['a'],base['b'];code=base['g']['code']
    win(a,32768,0x19bac,0x19bd4)
    for l,h in [(0x43f46,0x43fe6),(0x43b0a,0x43b28),(0x43d62,0x43de4),(0x6df1a,0x6e2ac)]:win(b,0x40000,l,h)
    win(b,0x40000,0x43728,0x43874);win(b,0x20000000-0x270,0x20000314,0x20000332)
    for _,r,m in base['results']:
        for control in (False,True):follow(code,b,r.copy(),m.copy(),control)
    print('PASS: 8 timers created for (3,8192,192000), head and 6 node writes verified; 8 changed-ID controls rejected before lookup; all returned to 8eb0')
