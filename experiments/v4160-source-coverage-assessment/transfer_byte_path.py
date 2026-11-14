"""Bounded fixed-PC projection of 0x19c02 byte transfer path.

Byte-addressed synthetic memory; accesses must exist. Mutations take effect
in program order, including aliases. Does not emulate traps or interrupts.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original',HERE/'transfer_original.py')
original=importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
MASK=0xffffffff


def execute(image,ops,mem,dst,src,length):
    original.validate(image,ops)
    dst &= MASK; src &= MASK; end=(dst+length)&MASK
    cursor=dst; events=[]
    if end<=dst: return events,cursor,src
    while True:
        value=mem[src]; events.append(('r',src,value))
        cursor=(cursor+1)&MASK; src=(src+1)&MASK
        address=(cursor-1)&MASK
        mem[address]=value; events.append(('w',address,value))
        if cursor>=end: return events,cursor,src
        if len(events)>2048: raise ValueError('execution bound')


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    ops=next(x['operations'] for x in evidence['functions'] if x['start']==original.START)
    count=0
    for dst in range(8,24):
        for src in range(8,24):
            for length in range(17):
                memory={i:(i*37+11)&255 for i in range(64)}
                expected=memory.copy(); trace=[]
                for i in range(length):
                    value=expected[src+i]; trace.extend((('r',src+i,value),('w',dst+i,value))); expected[dst+i]=value
                got,cursor,final_src=execute(image,ops,memory,dst,src,length)
                if got!=trace or memory!=expected or cursor!=dst+length or final_src!=src+length: raise ValueError('trace mismatch')
                count+=1
    # Unsigned wrapped end causes an immediate return without attempting reads.
    for dst,length in ((0xffffffff,1),(0xfffffffe,2),(0xfffffff0,16),(0xffffffff,0xffffffff)):
        mem={}; events,cursor,src=execute(image,ops,mem,dst,7,length)
        if events or cursor!=dst or src!=7: raise ValueError('wrapped end mismatch')
    # Forward copy with dst=src+1 repeatedly reads the just-written byte.
    mem={i:i for i in range(8)}
    trace,_,_=execute(image,ops,mem,1,0,4)
    if [x[2] for x in trace if x[0]=='r']!=[0,0,0,0]: raise ValueError('alias witness mismatch')
    print(f'PASS: {count} synthetic memory cases, 4 wrapped-end cases, forward-alias witness')
    print('Unsigned end <= destination returns without reads; overlap may propagate prior writes.')
    print('Fixed-PC projection, not ISA execution or a claim of caller reachability or hardware safety.')

if __name__=='__main__': main()
