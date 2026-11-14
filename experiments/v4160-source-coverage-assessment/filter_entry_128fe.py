"""Bounded 0x128fe entry projection up to the first indirect call.

Events follow original instruction order. Shared synthetic byte memory allows
stack writes to alias the provider slot; the target is loaded before writes.
No instruction execution, access fault, external callee or hardware modeled.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('calls',HERE/'case01_calls.py')
calls=importlib.util.module_from_spec(spec); spec.loader.exec_module(calls)
START=0x128fe
CODE=bytes.fromhex('b7070400bc47717122d526d31306000706d74ad14ecf52cdaa842e84081081458297')
MASK=0xffffffff


def project(image,mem,sp,ra,s0,s1,s2,s3,s4,a0,a1):
    if image[START-0x8000:START-0x8000+len(CODE)]!=CODE: raise ValueError('instruction mismatch')
    def load32(addr): return sum(mem[(addr+i)&MASK]<<(8*i) for i in range(4))
    events=[]
    def store32(addr,value):
        addr&=MASK; value&=MASK; events.append(('w',addr,value))
        for i in range(4): mem[(addr+i)&MASK]=(value>>(8*i))&255
    ptr=load32(0x40048); events.append(('r',0x40048,ptr))
    frame=(sp-176)&MASK
    for offset,value in ((168,s0),(164,s1),(172,ra),(160,s2),(156,s3),(152,s4)): store32(frame+offset,value)
    return (ptr&0xfffffffe,(frame+32)&MASK,0,112,0x12920,frame,a0&MASK,a1&MASK,events)


def main():
    image=calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    count=0
    for ptr in range(65536):
        mem={0x40048+i:(ptr>>(8*i))&255 for i in range(4)}
        result=project(image,mem,0x20001000,0x1453c,1,2,3,4,5,0x1234,106)
        if result[:8]!=(ptr&0xfffffffe,0x20000f70,0,112,0x12920,0x20000f50,0x1234,106): raise ValueError('projection mismatch')
        if [e[1] for e in result[8]]!=[0x40048,0x20000ff8,0x20000ff4,0x20000ffc,0x20000ff0,0x20000fec,0x20000fe8]: raise ValueError('event order mismatch')
        count+=1
    # Incoming sp makes saved s0 overwrite the same address as the loaded slot.
    mem={0x40048+i:x for i,x in enumerate((0x11,0x22,0x33,0x44))}
    result=project(image,mem,0x40050,1,0xaabbccdd,2,3,4,5,6,7)
    if result[0]!=0x44332210 or [mem[0x40048+i] for i in range(4)]!=[0xdd,0xcc,0xbb,0xaa]: raise ValueError('slot alias mismatch')
    for i in range(len(CODE)):
        bad=bytearray(image); bad[START-0x8000+i]^=1
        try: project(bad,{},0,0,0,0,0,0,0,0,0)
        except ValueError: continue
        raise ValueError('mutation accepted')
    for sp in (0,1,175,176,0xffffffff):
        mem={0x40048+i:0 for i in range(4)}
        result=project(image,mem,sp,0,0,0,0,0,0,0,0)
        if result[5]!=(sp-176)&MASK or result[1]!=(sp-144)&MASK: raise ValueError('wrap mismatch')
    print(f'PASS: {count} target cases, 1 provider-slot alias, 5 stack boundaries, {len(CODE)} byte mutations')
    print('Indirect target loaded from 0x40048 before stack saves; call args (new sp+32, 0, 112), JALR clears bit 0.')
    print('No target identity, return, provider effect, alignment/traps or hardware claim.')

if __name__=='__main__': main()
