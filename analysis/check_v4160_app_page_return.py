"""Continuous APP 8ea8 call -> version/fill -> config -> page path -> caller -> first registration -> four RTC waits -> calibration boundary, or rejection.
CLI: python check_v4160_app_page_return.py APP V131 RASM2
Reuses the checked geometry-chain instruction ledger, not its synthetic config or final CPU state.
Reference slots/RAM/Xwchc, synthetic stack/MMIO, successful accesses and noninterference are assumptions.
"""
from pathlib import Path
import re, runpy


def run(code, app, rom, six, equal, entry, clock, *, outer=False):
    m = {}; u = entry-80; a = 0x08077c00; b = 0x40012400; mask = 0xffffffff
    def put(p,w,v):
        for i in range(w): m[p+i] = v>>(8*i)&255
    def get(p,w): return int.from_bytes(bytes(m[p+i] for i in range(w)), 'little')
    def ck(ok):
        if not ok: raise ValueError(f'trace mismatch at {pc:#x}')
    r = dict(zero=0,sp=entry+32*outer,s0=0x12345,gp=0x20004000,ra=0,s1=0x2222,
             **{'s'+str(i):i for i in range(2,12)})
    for i in range(96): put(entry-96+i,1,0xa5)
    put(0x20000008,4,0x12345678); put(0x4002202c,4,0xabcdef01); put(0x40021014,4,clock)
    for i in range(22):
        put(0x1ab1c+i,1,app[0x12b1c+i]); put(0x6e6a0+i,1,rom[0x2e6a0+i])
    put(0x1ffff7e8,8,int.from_bytes(six+b'\xad\xde','little'))
    for off in (52,60,72,76,124,128,164): put(0x40000+off,4,int.from_bytes(rom[off:off+4],'little'))
    put(a,4,a^int(not equal)); put(r['gp']+382,1,73)
    for p in (0x4002420c,0x40021004,0x40021018,0x4002100c,b+76,*range(b,b+60,4)): put(p,4,p)
    for p in (0x40022010,0x4002200c,0xe000f000,0xe000f004): put(p,4,0)
    pc=0x8e88 if outer else 0x8ea8; outer_s0=0x40000 if outer else r['s0']; outer_writes=[]; pre=outer
    prefix=[]; zeros=[]; tail=[]; polls=0; reads=[]; entries=[]; words=[]; levels=[]; calls=[]
    handoff=[]; registration=[]; regstores=[]; rtc=[]; writes=[]; clock_start=[]
    for p in (0x4002101c,0x40007000,0x40021024,0x40021020): put(p,4,0x55000001)
    put(0x40002804,2,0x25)
    for _ in range(40000):
        if pc in (0x19af0,0x19ba8): break
        if pre and pc==0x8ea8:
            ck((r['sp'],r['ra'],r['s0'])==(entry,0x8ea8,0x40000))
            ck(outer_writes==[(entry+24,4,0x12345),(entry+28,4,0),(entry+20,4,0x2222),(0x4002420c,4,0)]+[(0x2000b18c+i,1,0) for i in range(2124)]+[(0x4002420c,4,0x4002420c)])
            pre=False
        if pc==0x19b38: clock_start.append((r['sp'],r['s0'],r['a0']))
        if pc==0x19272: rtc.append([r['ra'],0])
        if pc==0x8eac: handoff.append((r['sp'],r['s0'],r['s1'],r['a0']))
        if pc==0x43c4e: registration.append((r['a0'],get(0x2000319d,1),get(0x2000319e,1),get(0x200031c4,4)))
        if not pre and not calls and pc in (0x199e2,0x20000442,0x2000039c,0x19a3a): prefix.append(pc)
        if pc==0x19a3a: ck(r['sp']==u-16 and get(u,64)==0 and get(entry-8,4)==outer_s0 and get(entry-4,4)==0x8eac)
        if pc==0x43c7e:
            ck(r['a0']==u and get(u+24,6)==int.from_bytes(six,'little'))
            ck([get(u+d,w) for d,w in [(0,4),(4,2),(8,4),(12,4),(44,4),(56,4),(60,4)]]==
               [0x2000418c,0x7000,a,0x08030000,0x197f0,0x1979a,0x197be]); calls.append(pc)
        if pc==0x197be: entries.append((r['a0'],r['a1'],r['a2']))
        if pc in (0x43c06,0x19aee): levels.append((pc,r['a0']))
        at=pc; n,op,x=code[pc]; pc+=n; t=x[0]
        def v(s): return r[s] if s in r else int(s,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups(); return (int(d)+r[k])&mask
        if op in ('lw','lbu','lhu','sw','sb','sh'):
            w={'lw':4,'lbu':1,'lhu':2,'sw':4,'sb':1,'sh':2}[op]; p=addr(x[1])
            if op.startswith('s'): put(p,w,r[t])
            elif at==0x18a8e: ck(p==b); r[t]=2 if polls else 0; polls+=1
            elif at==0x19276:
                ck(p==0x40002804 and w==2); rtc[-1][1]+=1
                r[t]=(get(p,2)&~32) if rtc[-1][1]==1 else get(p,2)
            elif at==0x1978c: ck(p==0xe000f004); r[t]=1
            else: r[t]=get(p,w)
            if pre and op.startswith('s'): outer_writes.append((p,w,r[t]&((1<<(8*w))-1)))
            if clock_start and op.startswith('s'): writes.append((p,w,r[t]&((1<<(8*w))-1)))
            if at in (0x43c6a,0x43c72,0x19b34): regstores.append((at,p,w,r[t]&((1<<(8*w))-1)))
            if at==0x200003c0 and len(prefix)==3: zeros.append((p,r[t]))
            if at in (0x1910c,0x19110,0x19b04,0x19b06,0x19b08,0x19b0e): tail.append((op,p,r[t]))
            if at in (0x18f5a,0x18f78): reads.append((p,w))
            if at in (0x18f1e,0x18f26): words.append((op,p,r[t]))
        elif op in ('jal','jalr'):
            target=v(x[-1]) if op=='jal' else addr(t) if '(' in t else v(t); r['ra']=pc; pc=target&~1
        elif op=='j': pc=v(t)
        elif op=='ret': pc=r['ra']&~1
        elif op in ('beq','beqz','bne','bnez','bltu','bleu','blt'):
            y=0 if op.endswith('z') else v(x[1]); z=r[t]
            if (z==y if op.startswith('beq') else z!=y if op.startswith('bne') else z<y if op=='bltu' else z<=y if op=='bleu' else (z^0x80000000)<(y^0x80000000)): pc=v(x[-1])
        elif op in ('li','mv','lui','auipc','snez','not'):
            y=v(x[1]); r[t]=(y if op in ('li','mv') else y<<12 if op=='lui' else at+(y<<12) if op=='auipc' else int(y!=0) if op=='snez' else ~y)&mask
        elif op in ('add','addi','sub','and','andi','or','ori','mul','sll','slli','srli'):
            y,z=map(v,x[1:]); r[t]=(y+z if op.startswith('add') else y-z if op=='sub' else y&z if op.startswith('and') else y|z if op.startswith('or') else y*z if op=='mul' else y>>(z&31) if op=='srli' else y<<(z&31))&mask
        elif op!='fence.i': raise ValueError((at,op))
    ck(reads==[(0x1ffff7e8,4),(0x1ffff7ec,4)] and calls==[0x43c7e])
    bad=six==b'\xff'*6; ck(prefix==[0x199e2,0x20000442,0x2000039c,0x19a3a] and zeros==[(u+i,0) for i in range(64)])
    if bad:
        ck((pc,r['sp'],r['s0'],r['s1'],r['a0'])==(0x19af0,u-16,0x40000,0x2222,3) and not (handoff or registration or regstores or clock_start or rtc or writes))
    else:
        ck(handoff==[(entry,outer_s0,0x2222,clock|64)] and len(registration)==1)
        handler,n,cap,table=registration[0]; ck(handler==0x1995c and n==3 and n<cap)
        ck(regstores==[(0x43c6a,0x2000319d,1,4),(0x43c72,table+4*n,4,handler),(0x19b34,r['gp']+388,1,n)])
        task=r['gp']+388
        ck(clock_start==[(entry-16,task,3)] and (pc,r['sp'],r['s0'],get(task,1))==(0x19ba8,entry-48,task,3))
        ck(rtc==[[p,2] for p in (0x19b90,0x19b94,0x19b9e,0x19ba8)])
        ck(all(p+w<=task or task+1<=p for p,w,_ in writes))
        ck([(p,v) for p,w,v in writes if 0x40002800<=p<0x40002820]==[(0x40002804,0x35),(0x40002808,0),(0x4000280c,1),(0x40002804,0x25),(0x40002804,0x35),(0x40002818,0),(0x4000281c,0),(0x40002804,0x25)])
    ck(tail==([] if bad else [('lw',0x40021014,clock),('sw',0x40021014,clock|64),('lw',entry-4,0x8eac),('lw',entry-8,outer_s0),('sw',0xe000e104,0x80000000),('sw',0xe000e108,1)]))
    ck(levels==([(0x19aee,3)] if bad else [(0x43c06,int(equal)),(0x19aee,0)]))
    ck(polls==(0 if bad else 2))
    pages=[] if bad or equal else [a+i*256 for i in range(3)]
    ck([(p,n) for p,n,_ in entries]==[(p,64) for p in pages]); expected=[]
    for p,n,buf in entries:
        ck(buf==entries[0][2]);
        for off in range(0,256,4):
            data=p if not off else mask; expected.extend([('lw',buf+off,data),('sw',p+off,data)])
    ck(words==expected)
    return pc,r,m


if __name__=='__main__':
    base=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
    win=base['window']; app=base['a']; rom=base['b']
    win(app,0x8000,0x8ea8,0x8eb0); win(app,0x8000,0x199e2,0x19bac); win(rom,0x40000,0x43c4e,0x43c7e); win(app,0x8000,0x19106,0x19124); win(rom,0x20000000-0x270,0x20000442,0x2000048a); win(app,0x8000,0x18f56,0x18f88)
    win(rom,0x40000,0x43d50,0x43d62); win(rom,0x20000000-0x270,0x200004bc,0x200004fa)
    for lo,hi in [(0x19076,0x19106),(0x19142,0x19160),(0x1919c,0x191c6),(0x19220,0x19282)]: win(app,0x8000,lo,hi)
    for six in (bytes(range(6)),b'\xff'*5+b'\x00',b'\xff'*6):
        for equal in (False,True):
            for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]: run(base['code'],app,rom,six,equal,entry,clock)
    print('PASS: 12 continuous call traces; 8 task-ID-3 paths through four twice-sampled RTC waits to calibration; 4 earlier status-3 stops; 768 paired transfers')
