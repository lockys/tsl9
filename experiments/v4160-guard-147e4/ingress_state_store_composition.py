"""Compose the state gate with the existing payload-store projection.

This reconstructs a boundary between independently decoded instruction blocks,
not continuous execution; it assumes a successful stable halfword read.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gate=load('gate',HERE/'ingress_state_gate.py')
store=load('store',HERE/'ingress_payload_store.py')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    first=image[0x89f6-0x8000:0x8a06-0x8000]
    second=image[0x8a02-0x8000:0x8a20-0x8000]
    if first!=gate.EXPECTED or second!=store.EXPECTED or first[-4:]!=second[:4]: raise ValueError('original overlap mismatch')
    for index in range(65536):
        pc,reads,a2,a4,_=gate.run(first,0x20004000,5,5,index)
        store_pc,writes,_=store.run(second,0x20004000,a2,0x1ab)
        if a4!=1039 or reads!=[0x2000408a]: raise ValueError('gate register or read mismatch')
        if index <= 1039:
            expected=[(0x2000408a,2,index+1),(0x2000b9d8+index,1,0xab)]
            if pc!=0x8a06 or store_pc!=0x8a20 or writes!=expected: raise ValueError(f'accepted mismatch {index}')
        elif pc!=0x8a4c or store_pc!=0x8a4c or writes:
            raise ValueError(f'rejected mismatch {index}')
    for index in (0,1039,1040,65535):
        pc,reads,_,_,_=gate.run(first,0x20004000,5,6,index)
        if pc!=0x8a2a or reads: raise ValueError('unequal state unexpectedly reads')
    print('PASS: 65536 composed counter cases and 4 unequal-state cases')
    print('Segmented original-byte projections; no continuous CPU, hardware or concurrency validation.')

if __name__=='__main__': main()
