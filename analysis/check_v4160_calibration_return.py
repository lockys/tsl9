"""Continue the previous eight synthetic CPU snapshots through the actual APP calibration.
Args: decoded APP, V1.31, rasm2. Profile hook observes run() return, not instruction execution.
Peripheral samples and missing clock input are fixtures; not a model of physical calibration.
"""
from pathlib import Path
import runpy, sys, re
M=0xffffffff
def ck(v):
    if not v: raise ValueError('calibration trace mismatch')
def signed(x): return (x^0x80000000)-0x80000000
def quotient(a,b):
    a,b=signed(a),signed(b)
    return -1 if not b else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)

def calibrate(code,pc,r,m):
    def put(p,w,v): m.update({p+i:v>>(8*i)&255 for i in range(w)})
    def get(p,w): return sum(m[p+i]<<(8*i) for i in range(w))
    gp=r['gp']; task=gp+388; sp=r['sp']; saved={k:r[k] for k in ['s'+str(i) for i in range(12)]}; writes=[]; ticks=0
    ck(pc==0x19ba8 and saved['s0']==task and get(task,1)==3)
    # Supply only unmodelled input bytes; never replace a byte inherited from the prefix.
    for p,w,val in [(gp+108,4,60000000),(0x40022036,2,0),(0x40022049,1,0),(0x4002204c,4,0)]:
        for i in range(w): m.setdefault(p+i,val>>(8*i)&255)
    for _ in range(20000):
        if pc==0x19bac: break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        def v(k):return r[k] if k in r else int(k,0)
        if o in ('lw','lhu','lbu','sw','sh','sb'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups(); p=(r[k]+int(d))&M;w={'lw':4,'sw':4,'lhu':2,'sh':2,'sb':1,'lbu':1}[o]
            if o.startswith('s'): put(p,w,r[t]);writes.append((at,p,w));continue
            z=get(p,w)
            if at in (0x1933e,0x193ac,0x19456,0x194cc,0x19592,0x19608,0x193a0,0x194bc,0x195f8):
                ck((p,w)==(0x4002204c,2)); z=(z&32767) if at in (0x193a0,0x194bc,0x195f8) else z|32768
            if at in (0x191de,0x191e2): ck((p,w)==(0x4000281c,2));z=ticks&65535
            r[t]=z
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=v(x[1]);ticks+=int(pc==0x191c6)
        elif o=='j':pc=v(t)
        elif o=='ret':pc=r['ra']&~1
        elif o.startswith('b'):
            z=r[t]; y=0 if len(x)==2 else v(x[1]); match={'blez':signed(z)<=0,'bgez':signed(z)>=0,'bltz':signed(z)<0,'blt':signed(z)<signed(y),'ble':signed(z)<=signed(y),'beq':z==y,'beqz':z==0,'bne':z!=y}[o]
            if match:pc=v(x[-1])
        else:
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('li','mv'): q=y
            elif o=='lui':q=y<<12
            elif o in ('add','addi'):q=y+z
            elif o=='sub':q=y-z
            elif o=='div':q=quotient(y,z)
            elif o=='mul':q=y*z
            elif o in ('or','ori'):q=y|z
            elif o in ('and','andi'):q=y&z
            elif o in ('sll','slli'):q=y<<(z&31)
            elif o=='srli':q=y>>(z&31)
            elif o=='srai':q=signed(y)>>(z&31)
            else:raise ValueError((at,o))
            r[t]=q&M
    ck(pc==0x19bac and r['sp']==sp and all(r[k]==val for k,val in saved.items()) and get(task,1)==3)
    ck(6<=ticks<=12 and writes[-1]==(0x196b4,0x40022036,2))
    ck(all((sp-80<=p and p+w<=sp) or (p,w) in [(0x40022036,2),(0x40022049,1),(0x4002204c,2),(0x4002204f,1)] for _,p,w in writes))
    return ticks

if __name__=='__main__':
    here=Path(__file__).parent;g=runpy.run_path(str(here/'check_v4160_geometry_chain.py'));win=g['window'];a,b=g['a'],g['b'];run=runpy.run_path(str(here/'check_v4160_app_page_return.py'))['run']; results=[]
    for lo,hi in [(0x8ea8,0x8eb0),(0x199e2,0x19bac),(0x19106,0x19124),(0x18f56,0x18f88),(0x19076,0x19106),(0x19142,0x19160),(0x1919c,0x19282),(0x1929a,0x196c4),(0x197b8,0x197be)]:win(a,32768,lo,hi)
    for lo,hi in [(0x43c4e,0x43c7e),(0x43d50,0x43d62)]:win(b,0x40000,lo,hi)
    for lo,hi in [(0x442,0x48a),(0x4bc,0x4fa)]:win(b,0x20000000-0x270,0x20000000+lo,0x20000000+hi)
    def capture(f,event,arg):
        if f.f_code is run.__code__ and event=='return':
            s=f.f_locals;results.append((s['pc'],dict(s['r']),dict(s['m'])))
    for six in (bytes(range(6)),b'\xff'*5+b'\0'):
        for equal in (False,True):
            for sp,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
                sys.setprofile(capture)
                try:run(g['code'],a,b,six,equal,sp,clock)
                finally:sys.setprofile(None)
    ck(len(results)==8); counts=[calibrate(g['code'],*s) for s in results];print('PASS: 8 inherited states return to 19bac with SP, s0-s11 and task byte 3 preserved; clock calls:',counts)
