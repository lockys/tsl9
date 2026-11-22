"""APP V131 rasm2. Follow 63eda on inherited states, splitting only the sampled mask bits."""
from pathlib import Path
import runpy
u=runpy.run_path(str(Path(__file__).with_name('check_v4160_role_rf_unknowns.py')))
s,D,code,ck,M=(u[k] for k in ('s','D','code','ck','M'))
s['ns']['win'](s['b'],0x40000,0x63e58,0x63fa0)
IO=0x4002420c; state=0x2000351b

def follow(r,m,mask,bit):
    r=r.copy();m=m.copy();pc=0x63eda;entry=r.copy(); events=[];seen=[]
    ck(r['a0']==13 and r['ra']==0x641fc and m[state]==1)
    def v(k):return r[k] if k in r else int(k,0)
    def num(x):
        if not isinstance(x,int):raise ValueError('unknown branch/address')
        return x
    def masked(at,free,fixed):return (at,free,fixed) if free else fixed
    for _ in range(160):
        if pc==0x641fc:break
        at=pc;seen.append(at);n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('sw','lw','lbu','sb'):
            d,k=x[1][:-1].split('(');p=(num(r[k])+int(d))&M;w=4 if o.endswith('w') else 1
            if 0x40024000<=p<0x40026000:
                if o=='lw':
                    free,fixed=(M^3,mask) if at==0x63efc else (M^8,bit<<3) if at==0x63e6e else (M,0)
                    r[t]=masked(at,free,fixed)
                else:ck(o=='sw')
                events.append((at,o,p,r[t]))
            elif o.startswith('s'):
                z=num(r[t]);m.update({p+i:z>>(8*i)&255 for i in range(w)})
            elif any(p+i not in m for i in range(w)):return ('missing',at,p,w)
            else:r[t]=int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
        elif o in ('and','andi','or','ori','srli'):
            a,b=v(x[1]),num(v(x[2]))&M
            if isinstance(a,tuple):
                tag,free,fixed=a
                if o.startswith('and'):r[t]=masked(tag,free&b,fixed&b)
                elif o.startswith('or'):r[t]=masked(tag,free&~b,fixed|b)
                else:r[t]=masked(tag,free>>b,fixed>>b)
            else:r[t]=a&b if o.startswith('and') else a|b if o.startswith('or') else a>>b
        elif o in ('beq','bne','beqz','bnez'):
            eq=num(r[t])==(0 if o.endswith('z') else num(v(x[1])))
            if eq==o.startswith('beq'):pc=v(x[-1])
        elif o in ('ret','jal','j'):
            dest=r['ra'] if o=='ret' else v(x[-1]);
            if o=='jal':r['ra']=pc
            pc=num(dest)&~1
        elif o not in ('nop','fence.i'):
            a=v(x[1]);
            if o=='lui':z=num(a)<<12
            elif o=='addi':z=num(a)+v(x[2])
            elif o in ('mv','li'):z=num(a)
            else:raise ValueError((hex(at),o))
            r[t]=z&M
    else:raise ValueError('step limit')
    ck([e for e in events if e[2]==IO]==[(0x63ee8,'lw',IO,(0x63ee8,M,0)),(0x63eec,'sw',IO,0),(0x63f5e,'sw',IO,(0x63ee8,M,0))])
    ck(all(r[k]==entry[k] for k in ('sp','s0','s1','s2','s4')) and (0x63e58 in seen)==bool(mask) and 0x63f26 not in seen)
    ck([p for p in seen if 0x63e76<=p<0x63e7e]==(list(range(0x63e76,0x63e7e,2)) if mask and bit else []))
    ck(m[state]==(0 if mask else 1) and s['word'](m,s['HOOK'])==0);return ('return',pc)

out=[]
for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
    for equal in (False,True):
        pc,r,m=s['base']['run'](code,s['a'],s['b'],bytes(range(6)),equal,entry,clock,outer=True);s['base']['calibrate'](code,pc,r,m)
        for control in (False,True):
            rr,mm=r.copy(),m.copy();s['mod']['follow'](code,s['b'],rr,mm,control);s['ns']['advance'](code,s['b'],rr,mm,control)
            ck(s['target'](code,s['b'],rr)==(0x401a0,0x6dd16));ck(D['follow'](rr,mm)==(0x660e8,0x40025048,4));u['resume'](rr,mm)
            out.extend(follow(rr,mm,mask,bit) for mask in range(4) for bit in range(2 if mask else 1))
ck(out==[('return',0x641fc)]*56)
print('PASS: 56 inherited branch paths; 8 bypass and 48 helper paths return to 0x641fc, no indirect callback; independent inner RF sample restored')
