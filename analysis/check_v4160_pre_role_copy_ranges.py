"""Audit copy-helper memory events in two pre-role stages. CLI: APP V131 rasm2."""
from pathlib import Path
import runpy,sys

ns=runpy.run_path(str(Path(__file__).with_name('check_v4160_after_first_timer.py')),run_name='__main__')
base,mod,code,a,b=(ns[k] for k in ('base','mod','code','a','b'))
ns['win'](a,32768,0x8e88,0x8eb8)

def checked(ok,detail):
    if not ok:raise ValueError(detail)

def audit(fn,args,expected):
    events=[];extra=[]
    def watch(f,event,result):
        parent=f.f_back
        if event!='return' or not parent or parent.f_code is not fn.__code__:return
        name=f.f_code.co_name
        if name not in ('put','get'):return
        at=parent.f_locals.get('at',0)
        if not 0x20000332<=at<0x2000036c:return
        p,w=(f.f_locals[k] for k in ('p','w'));r=parent.f_locals['r']
        if at in (0x20000358,0x20000362):
            z=result if name=='get' else r['a6'];events.append((name,p,w,z,r['a0'],r['a1'],r['a2'],r['ra']))
        else:extra.append((name,p,w))
    old=sys.getprofile()
    try:sys.setprofile(watch);out=fn(*args)
    finally:sys.setprofile(old)
    checked(len(events)==2*sum(n for d,n in expected) and extra==[('get',0x4002420c,4),('put',0x4002420c,4),('put',0x4002420c,4)]*len(expected),extra)
    j=0
    for dest,length in expected:
        _,_,_,_,d,s,n,ra=events[j];checked((d,n)==(dest,length),(d,n))
        for i in range(n):
            rd,wr=events[j:j+2];j+=2;v=rd[3]
            checked(rd==('get',s+i,1,v,d,s,n,ra) and wr==('put',d+i,1,v,d,s,n,ra),(rd,wr))
        checked(d+n<=0x20003350 or d>=0x20003352,(d,n))
    return out

for equal in (False,True):
    for entry in (0x2000ffc0,0x2000ffd0):
        pc,r,m=audit(base['run'],(code,a,b,bytes(range(6)),equal,entry,0x101),[(0x200031ec,64),(entry-148,4)])
        base['calibrate'](code,pc,r,m)
        audit(mod['follow'],(code,b,r,m,False),[(0x20003234,16)])
print('PASS: 4 paired stages; 336 byte copies; no destination overlaps 0x20003350..51; helper control stores separately accounted')
