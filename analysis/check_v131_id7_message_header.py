"""V1.31 candidate reader slice. CLI: python check_v131_id7_message_header.py CARRIER.
Conditional Xwchc; stop at the first distinct arm or call. No hardware or callee model.
"""
from hashlib import sha256
from pathlib import Path
import sys

def need(ok):
    if not ok: raise ValueError('message-header evidence mismatch')

def bind(b):
    need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    def window(pc,h):
        raw=bytes.fromhex(h);need(b[pc-0x40000:pc-0x40000+len(raw)]==raw)
    window(0x46632,'1c201307200a639be70003ca34002a20c1652286fd15eff04f8e')
    window(0x4664e,'62471307c73a034a270013071009639fe714')
    window(0x4e31c,'130520fa08a010b02ea0')
    def compact(pc):
        w=int.from_bytes(b[pc-0x40000:pc-0x40000+2],'little');q=w&3
        need(q in (0,2) and w>>13 in (1,5))
        return (w>>13,1 if q==0 else 2,8+(w>>2&7),8+(w>>7&7),8*((w>>10)&(3 if q==0 else 7))+2*(w>>5&3)+((w>>12&1) if q==0 else 0))
    need(compact(0x46632)==(1,1,15,8,0) and compact(0x46640)==(1,2,10,8,2))
    need(compact(0x4e320)==(5,1,10,8,0) and compact(0x4e324)==(5,2,11,8,2))
    return classify

def classify(m,p):
    tag=m[p]
    if tag==162:return 0x4572c,(m[p+2]|(m[p+3]<<8),65535,p),0x2000324b
    return (0x46660 if tag==145 else 0x467ba),None,0x200033ae
    # Final field is the address of the separate s4 byte load, not its value.

if __name__=='__main__':
    f=bind(Path(sys.argv[1]).read_bytes());p=0x21001000;counts={}
    for tag in range(256):
        m={p:tag};m.update({p+2:0x34,p+3:0x12} if tag==162 else {})
        pc,args,_=f(m,p);counts[pc]=counts.get(pc,0)+1
        if args:need(args==(0x1234,0xffff,p))
    need(counts=={0x4572c:1,0x46660:1,0x467ba:254});print('PASS: 256 first-byte controls: 1 / 1 / 254')
