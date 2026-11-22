"""Run both linked TXs with synthetic query returns and a freshly sampled second handle."""
from itertools import product
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_v4160_linked_tx_loop_exit import image, need
from tx_multicall_clobber import patched_engine, action


def run(engine, code, h, x, y, fresh, u, v):
    gp,src,sp,base = 0x20004000,0x20008000,0x2000d020,0x2000b18c
    regs=[0]*32
    regs[1:4]=[0x11110000,sp,gp]; regs[10:14]=[h,0xa7,src,1]
    mem={a:0 for lo,n in [(sp-32,32),(gp+128,30),(src,1),(base,2124),(0x4013c,4),(0x40050,4)] for a in range(lo,lo+n)}
    def put(addr,b): mem.update((addr+i,val) for i,val in enumerate(b))
    put(gp+150,x.to_bytes(2,'little')); put(gp+154,y.to_bytes(2,'little')); put(0x4013c,(0x12345678).to_bytes(4,'little'))
    calls=[]; stubs=[]; bank=None
    if h!=65534 and h==x:
        calls.append(0x8a8e); stubs.append(action(u,writes=[(gp+154,2,fresh)])); y=fresh
        if u==1: bank=0
    if bank is None and h!=65534 and h==y:
        calls.append(0x8ab4); stubs.append(action(v)); bank=1 if v==1 else None
    result=engine.execute(code,regs,mem,stub=stubs)
    need([(pc,r[10],r[11]) for pc,_,r in result['calls']]==[(pc,h,gp+128) for pc in calls],'query trace')
    headers=[r for pc,r,_ in result['trace'] if pc==0x8ace]
    need([r[12] for r in headers]==([] if bank is None else [bank]),'selected bank')
    need(all((r[8],r[9],r[19])==(1,src,0xa7) for r in headers),'header inputs')
    need(result['boundary']==('opaque_return' if bank is None else 'opaque_tail'),'stop')
    if bank is None: need(not any(base<=addr<base+2124 for addr,_,_ in result['writes']),'unexpected bank write')
    return bank, len(calls), headers, result['writes'], result['memory'], result['registers']


def main(original,c,cpp):
    orig=image(original,'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'); engine,_=patched_engine()
    for label,p in [('C',c),('C++',cpp)]:
        other=image(p,'ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54'); counts={None:0,0:0,1:0}
        for args in product((7,65534),(7,65534),(7,65534),(7,65534),(0,1,0x101),(0,1,0xffffffff)):
            got=run(engine,orig,*args); need(got==run(engine,other,*args),'linked mismatch'); counts[got[0]]+=1
        print(f'PASS {label}: return={counts[None]}, bank0={counts[0]}, bank1={counts[1]}')


if __name__=='__main__': main(*sys.argv[1:])
