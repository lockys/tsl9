"""Fixed-PC projection 0x12946..0x1298a through call to 0x18ba2.

Synthetic shared byte memory; all reads succeed. Writes/read order matters
when input overlaps the stack. No trap, MMIO or callee is executed.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('calls',HERE/'case01_calls.py')
calls=importlib.util.module_from_spec(spec); spec.loader.exec_module(calls)
START=0x12946
CODE=bytes.fromhex('0356040083562400035744008357640002ca230b910085041606960616079607680093f4f40f02cca30b41012316c1002317d1002318e1002319f1004ece2104ef60c021')
MASK=0xffffffff


def step(image,mem,sp,s0,s1,s3,s4):
    if image[START-0x8000:START-0x8000+len(CODE)]!=CODE: raise ValueError('instruction mismatch')
    if calls.jal(0x12986,CODE[-4:])!=0x18ba2: raise ValueError('call target mismatch')
    sp&=MASK; s0&=MASK; s1&=MASK; events=[]
    def load(addr,n):
        addr&=MASK; value=sum(mem[(addr+i)&MASK]<<(8*i) for i in range(n))
        events.append(('r',addr,n,value)); return value
    def store(addr,n,value):
        addr&=MASK; value&=(1<<(8*n))-1; events.append(('w',addr,n,value))
        for i in range(n): mem[(addr+i)&MASK]=(value>>(8*i))&255
    words=[load(s0+2*i,2) for i in range(4)]
    store(sp+20,4,0); store(sp+22,1,s1)
    next_s1=(s1+1)&255
    store(sp+24,4,0); store(sp+23,1,s4)
    for i,value in enumerate(words): store(sp+12+2*i,2,value<<5)
    store(sp+28,4,s3)
    return (0x18ba2,(sp+12)&MASK,0x1298a,(s0+8)&MASK,next_s1,events)


def main():
    image=calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    count=0
    for value in range(65536):
        mem={0x1000+i:((value>>(8*(i&1)))&255) for i in range(8)}
        result=step(image,mem,0x2000,0x1000,value,0x12345678,0x1ff)
        if result[:5]!=(0x18ba2,0x200c,0x1298a,0x1008,(value+1)&255): raise ValueError('register mismatch')
        for i in range(4):
            got=mem[0x200c+2*i]|mem[0x200d+2*i]<<8
            if got!=(value<<5)&65535: raise ValueError('shift mismatch')
        if [e[0] for e in result[5]]!=['r']*4+['w']*9: raise ValueError('event order mismatch')
        count+=1
    # Four reads must precede stack writes, including on a shared address.
    mem={0x3000+i:i for i in range(64)}; old=mem.copy()
    result=step(image,mem,0x3000,0x3014,0xff,9,7)
    if [x[3] for x in result[5][:4]]!=[old[0x3014+2*i]|old[0x3015+2*i]<<8 for i in range(4)]: raise ValueError('alias order mismatch')
    for i in range(len(CODE)):
        bad=bytearray(image); bad[START-0x8000+i]^=1
        try: step(bad,{},0,0,0,0,0)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print(f'PASS: {count} halfword/counter cases, shared-memory alias witness, {len(CODE)} byte mutations')
    print('Four halfwords are read before writes, shifted left five and stored as halfwords; then calls 0x18ba2(sp+12).')
    print('Fixed-PC event projection only; no aligned-access, reachability, callee or hardware claim.')

if __name__=='__main__': main()
