"""Single fixed-PC 0x19c40 bulk step with shared synthetic byte memory.

Precondition: aligned readable/writable addresses and an already selected bulk
step. This is a projected event sequence, not a complete routine or CPU.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original',HERE/'transfer_original.py')
original=importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
MASK=0xffffffff


def step(mem,src,dst):
    src &= MASK; dst &= MASK
    if (src|dst)&3: raise ValueError('unaligned word')
    events=[]
    def load(addr):
        addr &= MASK; value=sum(mem[(addr+i)&MASK]<<(8*i) for i in range(4))
        events.append(('r',addr,value)); return value
    def store(addr,value):
        addr &= MASK; events.append(('w',addr,value))
        for i in range(4): mem[(addr+i)&MASK]=(value>>(8*i))&255
    words=[load(src+4*i) for i in range(8)]
    store(dst,words[0]); ninth=load(src+32)
    for i in range(1,8): store(dst+4*i,words[i])
    store(dst+32,ninth)
    return ((src+36)&MASK,(dst+36)&MASK,events)


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    ops=next(x['operations'] for x in evidence['functions'] if x['start']==original.START)
    original.validate(image,ops)
    cases=0
    for src in range(32,96,4):
        for dst in range(32,96,4):
            memory={i:(i*73+19)&255 for i in range(160)}
            before=memory.copy()
            expected=[bytes(before[src+4*i+j] for j in range(4)) for i in range(8)]
            expected_ninth=bytes(before[src+32+j] if src+32+j not in range(dst,dst+4) else expected[0][src+32+j-dst] for j in range(4))
            nextsrc,nextdst,trace=step(memory,src,dst)
            if (nextsrc,nextdst)!=(src+36,dst+36) or len(trace)!=18: raise ValueError('step shape mismatch')
            if [t[0] for t in trace]!=['r']*8+['w','r']+['w']*8: raise ValueError('event order mismatch')
            if bytes(memory[dst+i] for i in range(36))!=b''.join(expected)+expected_ninth: raise ValueError('payload mismatch')
            cases+=1
    mem={i:i&255 for i in range(128)}
    _,_,events=step(mem,32,64)
    if events[8][1]!=64 or events[9][1]!=64 or events[8][2]!=events[9][2]: raise ValueError('overlap witness mismatch')
    if bytes(mem[i] for i in range(96,100))!=bytes(range(32,36)): raise ValueError('ninth word did not observe first store')
    try: step({},1,0)
    except ValueError: pass
    else: raise ValueError('unaligned accepted')
    print(f'PASS: {cases} aligned shared-memory cases, read/write ordering, one overlap witness')
    print('First store precedes ninth load; dst=src+32 causes ninth load to observe that store.')
    print('Single bounded projection only: no bulk-loop reachability, faults, interrupts or hardware claim.')

if __name__=='__main__': main()
