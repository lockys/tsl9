"""V1.31 660d6..66240. Caller supplies live regs, RAM and a readback policy. No hardware IO."""
import re
M=0xffffffff
# (register byte offset, bits to clear, bits to set), in observed read/write order.
FIELDS=[(72,0x70000000,0x20000000),(72,0x07000000,0x04000000),(72,15,9),(72,0x70000,0),(72,0,1<<31),
 (76,7,3),(76,0x70,0x30),(76,0x700,0x300),(76,0x01000000,0),(76,0,0x02000000),
 (80,0xf000,0x4000),(84,15,12),(84,0,128),(84,0x1000,0),
 (60,0xf000,0x8000),(60,0x07000000,0x02000000),(60,0xe0000000,0x40000000),
 (44,0,0x700000),(44,0x07000000,0),(44,0x3000,0x2000),(44,0x30000,0x20000),
 (48,15,0),(48,0xf0,0),(48,0x700,0),(48,0,0x700000),(48,0x70000000,0x50000000),
 (56,0x00f80000,0x100000),(56,0,1<<31)]

def run(code,r,get,put,readback):
    pc=0x660d6;sp=r['sp'];base=get(0x20003590,4);saved=get(sp+12,4);expected=[];events=[];writes=[]
    def val(x):return r[x] if x in r else int(x,0)
    for _ in range(256):
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o=='ret':pc=r['ra']&~1;break
        if o in ('lw','sw'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups();p=(r[k]+int(d))&M
            if o=='sw':z=r[t];put(p,4,z);writes.append((at,p,4,z))
            elif p in (sp+12,0x20003590):z=get(p,4);r[t]=z
            else:z=readback(p,len(expected));r[t]=z;expected.append(z)
            events.append((o,p,z));continue
        y=val(x[1]);z=val(x[2]) if len(x)>2 else 0
        if o=='lui':v=y<<12
        elif o=='li':v=y
        elif o=='addi':v=y+z
        elif o in ('and','andi'):v=y&z
        elif o in ('or','ori'):v=y|z
        else:raise ValueError((hex(at),o))
        r[t]=v&M
    oracle=[('lw',0x20003590,base),('sw',base+40,1152)]
    for (d,clear,bits),sample in zip(FIELDS,expected):oracle.extend([('lw',base+d,sample),('sw',base+d,(sample&~clear)|bits)])
    oracle.append(('lw',sp+12,saved))
    if len(expected)!=28 or events!=oracle or pc!=(saved&~1) or r['sp']!=sp+16:raise ValueError('RF register trace mismatch')
    return pc,writes
