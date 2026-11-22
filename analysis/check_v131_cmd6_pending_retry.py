"""Two responses then a selector-5 retry. Bounded row/call projection, not hardware.
Uses the V1.31 ROM argument checked by the producer. Xwchc halfword reads.
"""
import check_v131_cmd6_occupied_owner as owner

s=owner.slot
r=s.row
flag=0x20002fa2

def read(m,a,n): return int.from_bytes(bytes(m[a+i] for i in range(n)), 'little')
def word(m,a,v): m.update({a+i:x for i,x in enumerate(v.to_bytes(4,'little'))})
def code(pc,n): return s.b[pc-0x40000:pc-0x40000+n]
def branch(pc):
    h=int.from_bytes(code(pc,2),'little'); s.ck(h&0xe003==0xc001)
    return pc+s.sx((h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1,9)

s.ck([branch(p) for p in (0x4e7d2,0x4e7e2,0x4e7f4)]==[0x4e81c,0x4e80e,0x4e800])
s.ck(code(0x4e7d0,2).hex()=='d840' and code(0x4e7ec,4).hex()=='3ac67c85')
s.ck(code(0x4e7f0,4).hex()=='eff0bfed' and code(0x4e7f6,10).hex()=='c8409720fb1fe7808091')
s.ck(code(0x4e808,6).hex()=='23a207008547' and code(0x4e81c,2).hex()=='8147')

def retry(m,status,release_returns=True):
    # Project only the selector-5 row and calls; stack frame is separate.
    p=read(m,r+4,4); log=[('load',p)]
    if not p: return 0,log
    if not m[flag]: return 1,log
    log.append(('dispatch',read(m,r+10,2),5,read(m,r+8,2),p))
    if status:
        live=read(m,r+4,4); log.append(('release',live))
        if not release_returns: return None,log
    word(m,r+4,0); log.append(('clear',r+4)); return 1,log

count=0
for old,new in ((0x2000460e,0x2000480e),(0x2000480e,0x2000460e)):
    for status,returns in ((0,True),(22,True),(22,False)):
        m={r+i:0 for i in range(12)};m[flag]=0
        s.ck(owner.attempt(m,s.desc,11,old)[:2]==(0,[]))
        s.ck(owner.attempt(m,s.desc,12,new)[:2]==(22,[new]))
        snap=m.copy();s.ck(retry(m,status)==(1,[('load',old)]) and m==snap)
        m[flag]=1; expected=[('load',old),('dispatch',11,5,8,old)]
        if status: expected.append(('release',old))
        if returns: expected.append(('clear',r+4))
        s.ck(retry(m,status,returns)==(1 if returns else None,expected))
        snap[flag]=1
        if returns:
            word(snap,r+4,0);s.ck(retry(m,status)==(0,[('load',0)]))
        s.ck(m==snap);count+=1
print(f'PASS: {count} inherited-row cases; flag zero retains old D; success clears, failure waits for release return')
