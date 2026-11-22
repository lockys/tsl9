"""Trace APP 8e88 to its first indirect role call. CLI: decoded APP, V1.31 carrier, rasm2.
Same synthetic RTC/MMIO/RAM assumptions as the preceding timer tests. Stop at callee entry.
"""
from pathlib import Path
import runpy

def target(code,rom,r):
    n,op,x=code[0x8eb2]; assert_load=(n,op,x)==(4,'lw',['a5','416(s0)'])
    if not assert_load or code[0x8eb6]!=(2,'jalr',['a5']):raise ValueError('slot instructions')
    p=(r['s0']+416)&0xffffffff
    if not 0x40000<=p<=0x40000+len(rom)-4:raise ValueError('slot outside reference')
    r['a5']=int.from_bytes(rom[p-0x40000:p-0x40000+4],'little');r['ra']=0x8eb8
    return p,r['a5']&~1

if __name__=='__main__':
    here=Path(__file__).parent; ns=runpy.run_path(str(here/'check_v4160_after_first_timer.py'),run_name='__main__');mod=ns['mod'];base=ns['base'];win=ns['win'];code=ns['code'];a,b=ns['a'],ns['b'];win(a,0x8000,0x8e88,0x8eb8)
    for six in (bytes(range(6)),b'\xff'*5+b'\0'):
        for equal in (False,True):
            for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
                pc,r,m=base['run'](code,a,b,six,equal,entry,clock,outer=True)
                base['calibrate'](code,pc,r,m)
                for control in (False,True):
                    rr,mm=r.copy(),m.copy();mod['follow'](code,b,rr,mm,control);ns['advance'](code,b,rr,mm,control)
                    if rr['s0']!=0x40000 or target(code,b,rr)!=(0x401a0,0x6dd16) or rr['ra']!=0x8eb8:raise ValueError('role entry')
    other=bytearray(b);other[416:420]=(0x60001).to_bytes(4,'little')
    if target(code,other,{'s0':0x40000})!=(0x401a0,0x60000):raise ValueError('slot data control')
    print('PASS: 8 real APP prologue paths, 2124 zero-byte stores each; 16 scheduler outcomes reach [401a0] -> 6dd16, link 8eb8; slot substitution distinguished')
