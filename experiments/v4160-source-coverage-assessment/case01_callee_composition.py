"""Connect case 0/1 calls to bounded 0x12ad0 entry/continuation projections.

The projections are reconstructed at call boundaries, not continuous CPU
execution. External callees are stubs assumed to return without affecting the
callee's SP or saved RA; memory accesses and asynchronous effects are omitted.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

entry=load('entry','case01_callee_entry.py')
continuation=load('continuation','callee_12ad0_continuation.py')
calls=entry.calls


def run(image,index,handle,sp):
    first,second,exit_pc=calls.run(image,index,handle)
    if second[0]!=0x12ad0: raise ValueError('unexpected selector call')
    mode=second[1]; saved_ra=second[2]
    frame,ra_addr,ra,first_target,args=entry.project(image,mode,sp,saved_ra)
    follow,ret=continuation.run(image,mode,frame,ra)
    if ret!=(sp&0xffffffff,saved_ra) or ra_addr!=(sp-4)&0xffffffff: raise ValueError('selector return mismatch')
    return first,(first_target,args),follow,exit_pc


def main():
    image=calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for index in (0,1):
        for handle in range(65536):
            sp=(0x20000000+handle*4)&0xffffffff
            first,callee,follow,exit_pc=run(image,index,handle,sp)
            if first[0:3]!=(0x13ba6,handle,(0,3)[index]) or exit_pc!=0x14098: raise ValueError('case call mismatch')
            if index==0:
                if callee!=(0x1299e,None) or follow is not None: raise ValueError('case zero mismatch')
            else:
                if callee!=(0x19bf0,((sp-124)&0xffffffff,0x19d68,106)) or follow!=(0x128fe,(sp-124)&0xffffffff,106,0x12b0a): raise ValueError('case one mismatch')
    for sp in (0,1,127,128,0xfffffffc,0xffffffff):
        for index in (0,1): run(image,index,0xffffffff,sp)
    for pc in (0x1452e,0x14538,0x12ad0,0x12b0c,0x12b22,0x12b06,0x12ae2):
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: run(bad,1 if pc!=0x1452e else 0,1,0x20001000)
        except ValueError: continue
        raise ValueError(f'mutation accepted: {pc:#x}')
    print('PASS: 131072 case/handle/stack combinations, 12 wrap cases, 7 boundary mutation checks')
    print('Case 0 -> 0x1299e; case 1 -> 0x19bf0 then 0x128fe with same synthetic stack address.')
    print('Conditional projections; callees, memory effects, interrupts, reachability and hardware unverified.')

if __name__=='__main__': main()
