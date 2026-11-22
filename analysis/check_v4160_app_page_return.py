"""Continuous APP post-fill -> config gate -> page path -> APP branch.
CLI: python check_v4160_app_page_return.py APP V131 RASM2
Reuses the checked geometry-chain instruction ledger, not its synthetic config or final CPU state.
Reference slots/RAM/Xwchc, prior zero fill, ready MMIO and noninterference are assumptions.
"""
from pathlib import Path
import re, runpy


def run(code, rom, six, equal):
    m = {}; u = 0x2000ff80; a = 0x08077c00; b = 0x40012400; mask = 0xffffffff
    def put(p,w,v):
        for i in range(w): m[p+i] = v>>(8*i)&255
    def get(p,w): return int.from_bytes(bytes(m[p+i] for i in range(w)), 'little')
    def ck(ok):
        if not ok: raise ValueError(f'trace mismatch at {pc:#x}')
    r = dict(zero=0,sp=u-16,s0=0x40000,gp=0x20004000,ra=0,s1=0x2222,
             **{'s'+str(i):i for i in range(2,12)})
    put(u,64,0); put(0x1ffff7e8,8,int.from_bytes(six+b'\xad\xde','little'))
    for off in (76,124,164): put(0x40000+off,4,int.from_bytes(rom[off:off+4],'little'))
    put(a,4,a^int(not equal)); put(r['gp']+382,1,73)
    for p in (0x4002420c,0x40021004,0x40021018,0x4002100c,b+76,*range(b,b+60,4)): put(p,4,p)
    for p in (0x40022010,0x4002200c,0xe000f000,0xe000f004): put(p,4,0)
    pc=0x19a3a; polls=0; reads=[]; entries=[]; words=[]; levels=[]; calls=[]
    for _ in range(40000):
        if pc in (0x19af0,0x19af2): break
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
            elif at==0x1978c: ck(p==0xe000f004); r[t]=1
            else: r[t]=get(p,w)
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
    bad=six==b'\xff'*6; ck((pc,r['sp'],r['s0'],r['s1'])==((0x19af0 if bad else 0x19af2),u-16,0x40000,0x2222))
    ck(levels==([(0x19aee,3)] if bad else [(0x43c06,int(equal)),(0x19aee,0)]))
    ck(polls==(0 if bad else 2))
    pages=[] if bad or equal else [a+i*256 for i in range(3)]
    ck([(p,n) for p,n,_ in entries]==[(p,64) for p in pages]); expected=[]
    for p,n,buf in entries:
        ck(buf==entries[0][2]);
        for off in range(0,256,4):
            data=p if not off else mask; expected.extend([('lw',buf+off,data),('sw',p+off,data)])
    ck(words==expected)


if __name__=='__main__':
    base=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
    win=base['window']; app=base['a']; rom=base['b']
    win(app,0x8000,0x19a3a,0x19ae6); win(app,0x8000,0x18f56,0x18f88)
    win(rom,0x40000,0x43d50,0x43d62); win(rom,0x20000000-0x270,0x200004bc,0x200004fa)
    for six in (bytes(range(6)),b'\xff'*5+b'\x00',b'\xff'*6):
        for equal in (False,True): run(base['code'],rom,six,equal)
    print('PASS: 6 post-fill APP traces: 2 equal, 2 three-page mismatches (384 paired transfers), 2 status-3 rejections')
