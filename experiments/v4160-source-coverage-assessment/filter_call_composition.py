"""Conditional composition of 0x128fe's two indirect call boundaries.

The first provider is not executed. Its post-return SP/s0/s1 and second slot
are explicit inputs; optional preserved-state cases are assumptions, not ABI
claims. Synthetic memory is used only for the entry's provider and saves.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj

first=load('first','filter_entry_128fe.py')
second=load('second','filter_second_call_12920.py')
MASK=0xffffffff


def run(image,sp,source,length,ptr0,ptr1,post_sp,post_s0,post_s1):
    mem={0x40048+i:(ptr0>>(8*i))&255 for i in range(4)}
    initial=first.project(image,mem,sp,0x12b0a,0x11,0x22,0x33,0x44,0x55,source,length)
    later=second.project(image,post_sp,post_s0,post_s1,ptr1)
    return initial,later


def main():
    image=first.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=first.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    count=0
    for length in (94,106):
        for source in range(0x20000000,0x20010000,4):
            sp=0x20001000; frame=(sp-176)&MASK
            initial,later=run(image,sp,source,length,0x40051,0x4004d,frame,length,source)
            if initial[:8]!=(0x40050,(frame+32)&MASK,0,112,0x12920,frame,source,length): raise ValueError('first call mismatch')
            if later!=(0x4004c,(frame+32)&MASK,source,length,0x1293c): raise ValueError('preserved call mismatch')
            count+=1
    # Explicit changed-state counterexample: normal return need not preserve
    # private ABI registers, pointers, or the provider table slot.
    initial,later=run(image,0x20001000,0x20002000,106,0x40050,0xdeadbeef,0xffffffff,0x100,0x12345678)
    if later!=(0xdeadbeee,31,0x12345678,112,0x1293c): raise ValueError('changed state mismatch')
    if later[1:4]==(initial[1],initial[6],initial[7]): raise ValueError('changed state ignored')
    for pc in (0x128fe,0x1291e,0x12920,0x12930,0x1293a):
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: run(bad,0x20001000,0x20002000,106,1,3,0x20000f50,106,0x20002000)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print(f'PASS: {count} preserved-state compositions, changed-state counterexample, 5 byte mutations')
    print('When SP/s0/s1 survive first call, second call uses the initial buffer and 94/106 length.')
    print('Provider preservation is only an assumption; no actual call, memory effect, CPU or hardware execution.')

if __name__=='__main__': main()
