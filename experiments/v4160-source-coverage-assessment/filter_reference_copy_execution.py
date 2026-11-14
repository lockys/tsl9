"""Execute the retained reference copy bytes in the limited host interpreter.

Caller and zero-fill are reconstructed at the call boundary, not executed.
Only ordinary synthetic RAM and the interpreter's synthetic MMIO are modeled.
"""
import importlib.util
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
p=load('providers',HERE/'filter_reference_providers.py')
INTERPRETER=ROOT/'experiments/tsl9-copy-instruction-interpreter/interpreter.py'
if not INTERPRETER.is_file(): raise SystemExit('SKIP: optional local copy instruction interpreter unavailable')
i=load('interpreter',INTERPRETER)
BIN=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DIGEST='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def main():
    raw=BIN.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST: raise ValueError('APP hash')
    checked=0
    for name,path,digest,copy,fill in p.CANDIDATES:
        f=ROOT/path
        if not f.exists(): print(f'SKIP {name}'); continue
        carrier=f.read_bytes(); p.check(carrier,digest,copy,fill)
        code=carrier[copy-0x40000:copy-0x40000+58]
        if code!=i.BODY: raise ValueError('interpreter code mismatch')
        for pc,n in ((0x19d08,94),(0x19d68,106)):
            source=raw[pc-0x8000:pc-0x8000+n]
            data=bytearray([0xa5]*320); data[32:144]=bytes(112); data[180:180+n]=source
            m=i.Machine(data,i.RAM+32,i.RAM+180,n,code=code)
            m.r[2]=i.RAM+176; m.r[8]=n; m.r[9]=i.RAM+180
            m.run(budget=2000)
            if m.data[32:144]!=source+bytes(112-n): raise ValueError('copy result')
            if (m.r[2],m.r[8],m.r[9],m.r[10])!=(i.RAM+176,n,i.RAM+180,i.RAM+32): raise ValueError('register state')
            if m.mmio!=0x12345678 or sum(e[0]=='read8' for e in m.effects)!=n or sum(e[0]=='write8' for e in m.effects)!=n: raise ValueError('events')
            # On an injected failed read, earlier writes remain and MMIO is not restored.
            fault=i.Machine(data,i.RAM+32,i.RAM+180,n,code=code,unmapped_reads={i.RAM+220})
            try: fault.run(budget=2000)
            except i.Halt as exc:
                if str(exc)!='unmapped data': raise
            else: raise ValueError('expected fault')
            if fault.data[32:72]!=source[:40] or fault.data[72:144]!=bytes(72) or fault.mmio!=0: raise ValueError('fault effects')
            checked+=1
        print(f'PASS {name}: 94/106 original bytes; register/effect checks and two injected read faults')
    if not checked: raise SystemExit('No candidate carrier available')
    print('Conditional host interpreter of reference copy only; fill and caller reconstructed, no installed ROM or hardware.')
if __name__=='__main__': main()
