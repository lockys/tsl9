"""Bounded transfer composition with original caller-referenced data bytes.

Uses synthetic memory and destinations. Source slices are not proof of object
extents. No actual CPU, hardware, call ABI or provider execution is performed.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('composition',HERE/'transfer_aligned_composition.py')
comp=importlib.util.module_from_spec(spec); spec.loader.exec_module(comp)
original=comp.original
SLICES=((0x19d08,94,'88bd8a192643d363037b448c2707c53b3921fda53416859dfe96e08ddf057cde'),
        (0x19d68,106,'a1a8eb84eb3ad1e54c06631aeeebf1863dc26c1be369b3c67f05b670c66e58d3'))


def slice_data(image,start,length,digest):
    data=image[start-0x8000:start-0x8000+length]
    if len(data)!=length or hashlib.sha256(data).hexdigest()!=digest: raise ValueError('source slice mismatch')
    return data


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    original.validate(image,next(x['operations'] for x in evidence['functions'] if x['start']==original.START))
    count=0
    for src,length,digest in SLICES:
        data=slice_data(image,src,length,digest)
        for dst in range(0x1000,0x1100,4):
            # Dense synthetic byte memory to honor the composition's bounds contract.
            memory={i:(i*29+7)&255 for i in range(0x1a000)}
            for i,value in enumerate(data): memory[src+i]=value
            before=memory.copy()
            counts=comp.run(memory,src,dst,length)
            if counts!=((2,5,2) if length==94 else (2,8,2)): raise ValueError('transfer count mismatch')
            if bytes(memory[dst+i] for i in range(length))!=data: raise ValueError('wrong output')
            if any(memory[i]!=before[i] for i in memory if not dst<=i<dst+length): raise ValueError('unexpected writes')
            count+=1
        for offset in range(length):
            bad=bytearray(image); bad[src-0x8000+offset]^=1
            try: slice_data(bad,src,length,digest)
            except ValueError: continue
            raise ValueError('source mutation accepted')
    print(f'PASS: {count} original-slice/synthetic-destination cases; 200 source-byte mutations rejected')
    print('Copy windows match original SHA-256; two-byte gap is not included.')
    print('Synthetic composition only; source object extents, hardware execution and provider effects unverified.')

if __name__=='__main__': main()
