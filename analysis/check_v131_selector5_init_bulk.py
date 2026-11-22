"""Args: decoded APP, V1.31 reference, rasm2. Observe the role trace's RAM writes."""
import runpy, sys
from pathlib import Path

role=Path(__file__).with_name('check_v131_live_third_count.py').resolve()
flag=0x20002f9c

def observe(f,event,arg):
    if f.f_code.co_filename!=str(role):return
    if f.f_code.co_name=='trace':
        if event=='call': runs.append(([],[]))
    elif event=='call' and f.f_code.co_name=='put':
        pc=f.f_back.f_locals.get('at'); p,w,z=(f.f_locals[k] for k in ('p','w','z'))
        if pc is None:return # fixture setup
        if p<=flag<p+w:runs[-1][0].append((pc,w,z>>(8*(flag-p))&255))
        if pc==0x200003c0:runs[-1][1].append((p,w))

runs=[];sys.setprofile(observe)
try:runpy.run_path(str(role))
finally:sys.setprofile(None)
if len(runs)!=18:raise ValueError('case count')
for idx,(hits,writes) in enumerate(runs):
    if hits!=[(0x4da80,1,0)]:raise ValueError(('flag writes',idx,hits))
    spans=[(0x200048ac,300),(0x20003358,48),(0x20003320,48)]
    if idx in (2,3,4,5):spans.append((0x200049e0,80))
    if idx==4:spans.append((0x20004a38,60))
    if idx==5:spans.extend([(0x20004a38,112),(0x20004ab0,60)])
    if writes!=[(p+i,1) for p,n in spans for i in range(n)]:raise ValueError(('fill footprint',idx))
print('PASS: 18 role returns; only the explicit clear covers the flag; all fill-byte destinations checked in order')
