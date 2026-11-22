"""V1.31 selector/ID read projection only. Not a path from init to dispatch.
Other operand loads at 4dff0/2 are assumed successful, not modeled here.
"""
from collections import ChainMap

START=0x4dfdc
RAW=bytes.fromhex('aa8469f537350020130505325e2599e381446dbf1830142068253c000146ca85cd2c')

def verify(image, memory):
    if image[START-0x40000:0xdffe]!=RAW: raise ValueError('selector reader bytes')
    base=(int.from_bytes(RAW[4:8],'little')&0xfffff000)+(int.from_bytes(RAW[8:12],'little',signed=True)>>20)
    sel=base+12; dest=base+14
    def project(status,m):
        # Project only selector and destination reads, not all effects of the reader.
        reads=[]
        def load(p,w):
            reads.append(p)
            return int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
        target=0x4dfa8; value=None
        if not status and load(sel,2):
            target=0x4e2ee; value=load(dest,1)
        return target,tuple(reads),value
    if (sel,dest)!=(0x2000332c,0x2000332e) or bytes(memory[p] for p in (sel,sel+1,dest))!=b'\x05\x00\x07':raise ValueError('inherited record')
    checks=[(0,memory,(0x4e2ee,(sel,dest),7)),(1,memory,(0x4dfa8,(),None)),
            (0,ChainMap({sel:0,sel+1:0},memory),(0x4dfa8,(sel,),None)),
            (0,ChainMap({sel:0,sel+1:1,dest:91},memory),(0x4e2ee,(sel,dest),91))]
    for status,m,expected in checks:
        if project(status,m)!=expected:raise ValueError('selector reader projection')
    return len(checks)
