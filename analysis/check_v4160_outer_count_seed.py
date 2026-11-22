"""Conditional origin of the byte read at 4daf6. Args: decoded APP, V1.31, rasm2.
Startup and the APP prefix are separate observations, not a continuous boot trace.
"""
from pathlib import Path
import runpy

here = Path(__file__).resolve().parent
count = 0x20003350
startup = runpy.run_path(str(here.parent / 'scripts/check-rf-3538-init.py'))
v = startup['verify'](startup['HEX'].read_bytes())
lo, hi = v['zero_range']
if list(range(lo, hi, 4))[278:279] != [count] or (hi-lo)//4 != 456:
    raise ValueError('startup count word')
if any(a <= count < b for a,b in v['copy_ranges']) or v['missing_source'] != [0x6eb2c,0x6eb30]:
    raise ValueError('startup predecessor')

ns = runpy.run_path(str(here / 'check_v4160_after_first_timer.py'), run_name='__main__')
base, mod, code, a, b = (ns[k] for k in ('base','mod','code','a','b'))
ns['win'](a,0x8000,0x8e88,0x8eb8)
target = runpy.run_path(str(here / 'check_v4160_first_role_slot.py'))['target']
paths = 0
for six in (bytes(range(6)), b'\xff'*5+b'\0'):
    for equal in (False,True):
        for entry,clock in ((0x2000ffc0,0x101),(0x2000ffd0,0x5555)):
            pc,r,m = base['run'](code,a,b,six,equal,entry,clock,outer=True)
            base['calibrate'](code,pc,r,m)
            if count in m: raise ValueError('prefix populated count byte')
            for control in (False,True):
                rr,mm = r.copy(),m.copy()
                mod['follow'](code,b,rr,mm,control)
                ns['advance'](code,b,rr,mm,control)
                if target(code,b,rr)!=(0x401a0,0x6dd16) or count in mm:
                    raise ValueError('first role entry or count footprint')
                paths += 1
print(f'PASS: startup word 279/456; {paths} sparse APP paths to first role leave count byte absent (not an observed zero)')
