"""Fourteen decoded filter calls with ordinary synthetic word-backed registers.

Not a peripheral model: no write-one-to-clear, read side effects, asynchronous
changes, faults, interrupts, aliasing, or real memory mapping are modeled.
"""
import importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('machine',HERE/'filter_selected_machine.py')
machine=importlib.util.module_from_spec(spec); spec.loader.exec_module(machine)
MASK=0xffffffff
CTL=0x40006600; ACTIVE=0x4000661c; SCALE=0x4000660c; MODE=0x40006604; FIFO=0x40006614


def run(image,initial,fields_by_index):
    if len(fields_by_index)!=14 or set(initial)!={CTL,ACTIVE,SCALE,MODE,FIFO}: raise ValueError('bad inputs')
    regs=dict(initial); data={}; all_events=[]
    for index,fields in enumerate(fields_by_index):
        bit=1<<index
        # Reads 5 and 6 occur after writes 1 and 0 respectively. This memory
        # premise is a test assumption, not a property of physical devices.
        reads=(regs[CTL],regs[ACTIVE],regs[SCALE],regs[MODE],regs[FIFO],regs[ACTIVE]&~bit,regs[CTL]|1)
        events,pc=machine.run(image,index,fields,reads)
        if pc!=0x18c58: raise ValueError('did not return')
        observed=[]
        for addr,value in events:
            if addr in regs: regs[addr]=value
            else: data[addr]=value
            observed.append((addr,value))
        if len(observed)!=9: raise ValueError('unexpected write count')
        all_events.extend(observed)
    return regs,data,all_events


def main():
    image=machine.projection.route.A.audit.loop.calls.case.dispatch.IMAGE.read_bytes(); machine.projection.route.flow.flow(image)
    rng=random.Random(0x1804160)
    for case in range(512):
        initial={a:rng.getrandbits(32) for a in (CTL,ACTIVE,SCALE,MODE,FIFO)}
        fields=[tuple(rng.randrange(65536) for _ in range(4)) for _ in range(14)]
        regs,data,events=run(image,initial,fields)
        want={CTL:initial[CTL]&~1,ACTIVE:initial[ACTIVE]|0x3fff,SCALE:initial[SCALE]&~0x3fff,MODE:initial[MODE]|0x3fff,FIFO:initial[FIFO]&~0x3fff}
        if regs!=want or len(events)!=126 or len(data)!=28: raise ValueError(f'register mismatch {case}')
        for i,f in enumerate(fields):
            if data[0x40006640+8*i]!=(f[3]<<16|f[1]) or data[0x40006644+8*i]!=(f[2]<<16|f[0]): raise ValueError('packed field mismatch')
    # A peripheral that returns arbitrary values on repeated reads can defeat
    # ordinary-memory composition: use the original decoder as a witness.
    e,_=machine.run(image,0,(1,2,3,4),(0,0,0,0,0,0,0x80))
    if e[-1]!=(CTL,0x80): raise ValueError('independent-read witness mismatch')
    print('PASS: 512 synthetic word-memory sequences x 14 decoded calls; independent-read counterexample')
    print('Conditional final masks and 28 packed words; no real MMIO or asynchronous behavior.')
if __name__=='__main__': main()
