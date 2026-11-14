"""Compose bounded projections for two aligned nonoverlapping caller transfers.

This is not an instruction emulator. We reconstruct at fixed control-flow
boundaries; memory is synthetic, accesses succeed, no asynchronous effects.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

bulk=load('bulk','transfer_bulk_step.py')
gate=load('bulk_gate','transfer_bulk_gate.py')
entry=load('entry','transfer_gate.py')
original=bulk.original
MASK=0xffffffff


def run(memory,src,dst,length):
    if (src|dst)&3 or length not in (94,106): raise ValueError('outside projection domain')
    if dst+length>MASK or src+length>MASK or dst+length>=len(memory) or src+length>=len(memory): raise ValueError('invalid bounds')
    if not (dst+length<=src or src+length<=dst): raise ValueError('overlap excluded')
    pc,end=entry.gate(dst,src,length)
    if pc!=0x19c1a: raise ValueError('unexpected entry')
    initial_dst=dst; initial_src=src; batches=0; words=0; byte_count=0
    aligned_end,threshold,_=gate.gate(end,dst)
    while dst<threshold:
        src,dst,_=bulk.step(memory,src,dst); batches+=1
        if batches>4: raise ValueError('bulk bound exceeded')
    while dst<aligned_end:
        data=[memory[src+i] for i in range(4)]
        for i,value in enumerate(data): memory[dst+i]=value
        src+=4; dst+=4; words+=1
    while dst<end:
        memory[dst]=memory[src]; src+=1; dst+=1; byte_count+=1
    if dst!=initial_dst+length or src!=initial_src+length: raise ValueError('cursor mismatch')
    return batches,words,byte_count


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    original.validate(image,next(x['operations'] for x in evidence['functions'] if x['start']==original.START))
    count=0
    for length in (94,106):
        for src in range(256,384,4):
            for dst in range(768,896,4):
                memory={i:(i*73+length)&255 for i in range(1200)}
                before=memory.copy()
                result=run(memory,src,dst,length)
                if result!=((2,5,2) if length==94 else (2,8,2)): raise ValueError('batch/word/tail counts mismatch')
                if any(memory[dst+i]!=before[src+i] for i in range(length)): raise ValueError('destination mismatch')
                if any(memory[i]!=before[i] for i in memory if not dst<=i<dst+length): raise ValueError('unexpected mutation')
                count+=1
    for args in ((256,260,94),(257,768,94),(256,768,95)):
        try: run({i:0 for i in range(1200)},*args)
        except ValueError: continue
        raise ValueError('invalid input accepted')
    print(f'PASS: {count} aligned nonoverlap cases, 3 rejected domain cases')
    print('Length 94: 2 bulk, 5 word, 2 byte; length 106: 2 bulk, 8 word, 2 byte.')
    print('Conditional composition only: external calls, actual pointers, memory faults and hardware not verified.')

if __name__=='__main__': main()
