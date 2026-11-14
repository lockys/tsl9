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
    pc=START; writes=set(); controls=[]; count=0; edges={}
    while pc<END:
        hw=int.from_bytes(image[pc-0x8000:pc-0x8000+2],'little'); q=hw&3
        if q==3:
            w=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little'); op=w&127
            if op in (0x03,0x13,0x33,0x37): writes.add((w>>7)&31)
            elif op==0x63:
                imm=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
                if imm&4096: imm-=8192
                controls.append((pc,'branch')); edges[pc]=(pc+4,pc+imm)
            elif op!=0x23: raise ValueError(f'unknown RV32 op {pc:x}: {w:08x}')
            if pc not in edges: edges[pc]=(pc+4,)
            pc+=4
        else:
            f=hw>>13
            if q==0 and f==2: writes.add(8+((hw>>2)&7))
            elif q==1 and f in (0,2): writes.add((hw>>7)&31)
            elif q==1 and f==4: writes.add(8+((hw>>7)&7))
            elif q==1 and f in (6,7):
                imm=((hw>>12)&1)<<8|((hw>>10)&3)<<3|((hw>>5)&3)<<6|((hw>>3)&3)<<1|((hw>>2)&1)<<5
                if imm&256: imm-=512
                controls.append((pc,'branch')); edges[pc]=(pc+2,pc+imm)
            elif q==1 and f==5:
                imm=((hw>>12)&1)<<11|((hw>>11)&1)<<4|((hw>>9)&3)<<8|((hw>>8)&1)<<10|((hw>>7)&1)<<6|((hw>>6)&1)<<7|((hw>>3)&7)<<1|((hw>>2)&1)<<5
                if imm&2048: imm-=4096
                controls.append((pc,'jump')); edges[pc]=(pc+imm,)
            elif q==2 and f==0: writes.add((hw>>7)&31)
            elif q==2 and f==4:
                rd=(hw>>7)&31; rs2=(hw>>2)&31
                if hw==0x8082: controls.append((pc,'ret')); edges[pc]=()
                elif rs2!=0: writes.add(rd)
                else: raise ValueError(f'unknown indirect transfer {pc:x}')
            else: raise ValueError(f'unknown RVC op {pc:x}: {hw:04x}')
            if pc not in edges: edges[pc]=(pc+2,)
            pc+=2
        count+=1
    if pc!=END: raise ValueError('instruction boundary mismatch')
    if writes!={11,12,13,14,15,16}: raise ValueError(f'unexpected writes {writes}')
    if controls!=[(0x18bd2,'branch'),(0x18c10,'branch'),(0x18c28,'branch'),(0x18c38,'branch'),(0x18c58,'ret'),(0x18c5a,'branch'),(0x18c88,'jump'),(0x18c90,'jump'),(0x18c94,'branch'),(0x18ca2,'jump')]: raise ValueError('unexpected transfers')
    expected={0x18bd2:(0x18bd4,0x18c5a),0x18c10:(0x18c12,0x18c8a),
              0x18c28:(0x18c2a,0x18c92),0x18c38:(0x18c3c,0x18c4a),
              0x18c58:(),0x18c5a:(0x18c5e,0x18c04),0x18c88:(0x18bfe,),
              0x18c90:(0x18c18,),0x18c94:(0x18c98,0x18c34),0x18ca2:(0x18c34,)}
    if any(edges[pc]!=targets for pc,targets in expected.items()): raise ValueError('control target mismatch')
    for source,targets in edges.items():
        if any(target not in edges for target in targets): raise ValueError(f'edge outside instruction set at {source:x}')
    visited=set(); pending=[START]
    while pending:
        current=pending.pop()
        if current in visited: continue
        visited.add(current); pending.extend(edges[current])
    if visited!=set(edges): raise ValueError('unexpected unreachable instructions')
    # All possible branch edges are considered; cycles would preclude a
    # structural termination conclusion even if a real predicate forbids one.
    visiting=set(); finished=set()
    def visit(node):
        if node in visiting: raise ValueError('control-flow cycle')
        if node in finished: return
        visiting.add(node)
        for child in edges[node]: visit(child)
        visiting.remove(node); finished.add(node)
    visit(START)
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
    print('All encoded branches/jumps form a closed acyclic graph ending at ret; both branch outcomes are included.')
    print('Not an execution, memory-safety, interrupt, fault or MMIO-completion proof.')

if __name__=='__main__': main()
