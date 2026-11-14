"""Conservative linear write-set audit of original 0x18ba2..0x18ca4.

Includes post-return branch blocks. No CFG reachability, successful access,
exception/interrupt behavior or hardware semantics is inferred.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('loop',HERE/'filter_loop_step.py')
loop=importlib.util.module_from_spec(spec); spec.loader.exec_module(loop)
START=0x18ba2; END=0x18ca4


def scan(image):
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=loop.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    pc=START; writes=set(); controls=[]; count=0
    while pc<END:
        hw=int.from_bytes(image[pc-0x8000:pc-0x8000+2],'little'); q=hw&3
        if q==3:
            w=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little'); op=w&127
            if op in (0x03,0x13,0x33,0x37): writes.add((w>>7)&31)
            elif op==0x63: controls.append((pc,'branch'))
            elif op!=0x23: raise ValueError(f'unknown RV32 op {pc:x}: {w:08x}')
            pc+=4
        else:
            f=hw>>13
            if q==0 and f==2: writes.add(8+((hw>>2)&7))
            elif q==1 and f in (0,2): writes.add((hw>>7)&31)
            elif q==1 and f==4: writes.add(8+((hw>>7)&7))
            elif q==1 and f in (6,7): controls.append((pc,'branch'))
            elif q==1 and f==5: controls.append((pc,'jump'))
            elif q==2 and f==0: writes.add((hw>>7)&31)
            elif q==2 and f==4:
                rd=(hw>>7)&31; rs2=(hw>>2)&31
                if hw==0x8082: controls.append((pc,'ret'))
                elif rs2!=0: writes.add(rd)
                else: raise ValueError(f'unknown indirect transfer {pc:x}')
            else: raise ValueError(f'unknown RVC op {pc:x}: {hw:04x}')
            pc+=2
        count+=1
    if pc!=END: raise ValueError('instruction boundary mismatch')
    if writes!={11,12,13,14,15,16}: raise ValueError(f'unexpected writes {writes}')
    if controls!=[(0x18bd2,'branch'),(0x18c10,'branch'),(0x18c28,'branch'),(0x18c38,'branch'),(0x18c58,'ret'),(0x18c5a,'branch'),(0x18c88,'jump'),(0x18c90,'jump'),(0x18c94,'branch'),(0x18ca2,'jump')]: raise ValueError('unexpected transfers')
    return count,writes,controls


def main():
    image=loop.calls.case.dispatch.IMAGE.read_bytes(); count,writes,controls=scan(image)
    for offset in range(END-START):
        bad=bytearray(image); bad[START-0x8000+offset]^=1
        try: scan(bad)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print(f'PASS: {count} instructions, writes x{sorted(writes)}, {len(controls)} transfers, {END-START} byte mutations rejected by image hash')
    print('Conditional static audit: no direct writes to s0-s4, sp, ra; no call instruction recognized.')
    print('Not a CFG, execution, memory-safety, interrupt, fault or MMIO-completion proof.')

if __name__=='__main__': main()
