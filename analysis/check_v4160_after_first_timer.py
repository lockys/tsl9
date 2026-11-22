"""Follow both scheduler outcomes through the next APP registration. Args: APP, V1.31, rasm2.
Stop before the caller's next s0-relative read: earlier fixtures seeded outer s0 synthetically.
"""
from pathlib import Path
import re,runpy

def ck(ok,label):
    if not ok:raise ValueError(label)

def advance(code,rom,r,m,control):
    pc=0x8eb0; sp=r['sp']; old=r['s0']; head=0x200031e8; node=0x200043b4; count=0x2000319d
    task=r['gp']+388; second=r['gp']+166; dest=0x2000be08; mm=0x4002420c
    def get(p,w):return sum((rom[p+i-0x40000] if 0x40000<=p+i<0x40000+len(rom) else m[p+i])<<(8*i) for i in range(w))
    def put(p,w,z):m.update({p+i:z>>(8*i)&255 for i in range(w)})
    ck(r['a0']==int(not control) and get(task,1)==(150 if control else 3),'input outcome')
    initial=get(head,4);ck(initial==(0 if control else node),'head'); timer=get(node,16) if initial else None
    table=get(0x200031c4,4); ck(get(count,1)==4 and get(count+1,1)>4,'capacity'); io=get(mm,4)
    path=[];stores=[];calls=[];sampled=[]
    for _ in range(2000):
        if pc==0x8eb2:break
        at=pc;path.append(at);n,o,x=code[pc];pc+=n;t=x[0]
        def v(k):return r[k] if k in r else int(k,0)
        def adr(k):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[k]+int(d))&0xffffffff
        if o in ('sw','sb','lw','lbu'):
            p=adr(x[1]);w=4 if o in ('sw','lw') else 1
            if o in ('sw','sb'):put(p,w,r[t]);stores.append((at,p,w,r[t]&((1<<(8*w))-1)))
            else:r[t]=get(p,w)
        elif o in ('jal','jalr'):
            target=v(x[-1]);r['ra']=pc;pc=target&~1;calls.append((at,pc))
            if at==0x9094:sampled.append((r['a0'],r['a1'],r['a2']))
            if at==0x90a2:sampled.append(r['a0'])
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('bleu','beqz','bnez','bne'):
            y=0 if len(x)==2 else v(x[1]);z=r[t]
            if (z<=y if o=='bleu' else z==y if o=='beqz' else z!=y):pc=v(x[-1])
        elif o!='fence.i':
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('li','mv'):q=y
            elif o=='auipc':q=at+(y<<12)
            elif o=='lui':q=y<<12
            elif o in ('add','addi'):q=y+z
            elif o=='slli':q=y<<(z&31)
            else:raise ValueError((at,o))
            r[t]=q&0xffffffff
    ck(calls==[(0x8eb0,0x907a),(0x9094,0x2000039c),(0x90a2,0x43c4e)] and sampled==[(dest,0,180),0x901a],'call inputs')
    ck(stores==[(0x907c,sp-8,4,old),(0x9084,sp-4,4,0x8eb2),(0x200003a4,mm,4,0)]+[(0x200003c0,dest+i,1,0) for i in range(180)]+[(0x200003b8,mm,4,io),(0x43c6a,count,1,5),(0x43c72,table+16,4,0x901a),(0x90a8,second,1,4)],'ordered stores')
    ck((pc,r['sp'],r['s0'],r['a0'],get(second,1),get(head,4))==(0x8eb2,sp,old,4,4,initial),'handoff')
    ck(not initial or get(node,16)==timer,'timer contents');return path

if __name__=='__main__':
    mod=runpy.run_path(str(Path(__file__).with_name('check_v4160_clock_task_reload.py')),run_name='__main__');base=mod['base'];code=mod['code'];a,b=mod['a'],mod['b'];win=mod['win']
    win(a,32768,0x8eb0,0x8eb2);win(a,32768,0x907a,0x90b0)
    for _,regs,mem in base['results']:
        paths=[]
        for control in (False,True):
            r,m=regs.copy(),mem.copy();mod['follow'](code,b,r,m,control);paths.append(advance(code,b,r,m,control))
        ck(paths[0]==paths[1],'paired PC sequences')
    print('PASS: 8 paired scheduler outcomes; same path, 180 zero stores and handler 901a registered as ID 4; old timer state retained through 8eb2')
