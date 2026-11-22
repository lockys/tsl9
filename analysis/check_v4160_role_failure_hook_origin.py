"""Args: APP, V1.31, rasm2. Trace the origin of cfg+52 to role entry (synthetic peripherals)."""
from pathlib import Path
import runpy,sys
here=Path(__file__).resolve().parent
ns=runpy.run_path(str(here/'check_v4160_after_first_timer.py'),run_name='__main__')
base,mod,code,a,b=(ns[k] for k in ('base','mod','code','a','b'))
ns['win'](a,0x8000,0x8e88,0x8eb8)
target=runpy.run_path(str(here/'check_v4160_first_role_slot.py'))['target']
HOOK=0x20003220
def ck(x):
    if not x:raise ValueError('hook origin mismatch')
def word(m,p):return int.from_bytes(bytes(m[p+i] for i in range(4)),'little')
rows=[]
for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
    field=entry-80+52
    for equal in (False,True):
        writes=[];reads=[]
        def watch(f,event,arg):
            if event!='call' or f.f_code.co_name not in ('get','put') or f.f_back.f_code is not base['run'].__code__:return
            d=f.f_locals;p=d['p'];w=d['w'];at=f.f_back.f_locals.get('at')
            if at is None:return
            for name,q in [('src',field),('dst',HOOK)]:
                if p<q+4 and p+w>q:
                    (writes if f.f_code.co_name=='put' else reads).append((name,at,p-q,w,d.get('v')))
        prev=sys.getprofile()
        try:
            sys.setprofile(watch);pc,r,m=base['run'](code,a,b,bytes(range(6)),equal,entry,clock,outer=True)
        finally:sys.setprofile(prev)
        def stores(at):return [(at,i,1,0) for i in range(4)]
        ck([(at,i,w,v) for k,at,i,w,v in writes if k=='src']==stores(0x200003c0))
        ck([(i,w) for k,at,i,w,_ in reads if k=='src' and at==0x20000358]==[(i,1) for i in range(4)])
        ck([(at,i,w,v) for k,at,i,w,v in writes if k=='dst']==stores(0x200003c0)+stores(0x20000362))
        ck(word(m,HOOK)==0);base['calibrate'](code,pc,r,m)
        for control in (False,True):
            rr,mm=r.copy(),m.copy();mod['follow'](code,b,rr,mm,control);ns['advance'](code,b,rr,mm,control)
            ck(target(code,b,rr)==(0x401a0,0x6dd16) and word(mm,HOOK)==0)
            rows.append((word(mm,0x20003190),word(mm,0x2000318c)))
ck(rows==[(0x200045ac,0x2000b184)]*8)
print('PASS: four APP cfg+52 bytes cleared, read and copied; eight role entries have an explicit zero hook; heap bounds differ from small-heap failure fixture')
