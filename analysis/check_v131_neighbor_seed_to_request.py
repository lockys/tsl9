"""Conditional startup word and separate role traces. Args: v4.1.60 APP, V1.31, rasm2."""
from pathlib import Path
import runpy,sys

here=Path(__file__).resolve().parent
N=0x20003351

def ck(ok):
    if not ok:raise ValueError('neighbor provenance mismatch')

startup=runpy.run_path(str(here.parent/'scripts/check-rf-3538-init.py'))
s=startup['verify'](startup['HEX'].read_bytes());lo,hi=s['zero_range']
ck(hi-lo==456*4 and N==lo+278*4+1 and not any(a<=N<b for a,b in s['copy_ranges']))
ck(s['missing_source']==[0x6eb2c,0x6eb30])
trace=runpy.run_path(str(here/'check_v131_live_third_count.py'))['trace']
class Boundary(Exception):pass

def audit(seed,outer,cap):
    init=[];reads=[];writes=[];calls=[];results=[]
    def watch(f,event,arg):
        parent=f.f_back
        if event!='return' or parent is None or parent.f_code is not trace.__code__:return
        d=parent.f_locals;v=f.f_locals;name=f.f_code.co_name
        if name not in ('get','put'):return
        p,w=v['p'],v['w'];at=d.get('at')
        if p<=N<p+w:
            if at is None:
                ck(name=='put' and (p,w)==(N,1));init.append(v['z']);d['m'][N]=seed
            elif name=='put':writes.append((at,p,w))
            else:reads.append((at,p,w,arg))
        if at==0x4db60 and name=='put':
            calls.extend(d['calls']);results.extend(d['results']);raise Boundary
    old=sys.getprofile()
    try:
        sys.setprofile(watch);trace(cap,outer)
    except Boundary:pass
    finally:sys.setprofile(old)
    copied=bool(outer and cap==1024)
    ck(init==[2] and not writes and reads==([(0x4db2a,N,1,seed)] if copied else []))
    ck(calls[-1]==(16*((5+(seed if copied else 0))&255),0x4c05,0x4db60))
    if outer:ck(bool(results[1])==copied)
    return calls[-1][0]

for n in (0,1,2,251,255):
    ck(audit(n,0,1024)==audit(n,5,300)==80)
    ck(audit(n,5,1024)==16*((5+n)&255))
print('PASS: startup word 279/456 byte +1; 15 separate role traces: 5 skip, 5 null, 5 successful first allocations; no store to neighbor before second request')
