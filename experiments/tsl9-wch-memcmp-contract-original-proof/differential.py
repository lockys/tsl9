"""Compare candidate-byte PC interpreter with existing C semantic contract.

Xwchc 0x2294 is assumed to mean lbu a3,0(a3) ONLY when profile=1.
Successful/failing synthetic callbacks and PC boundaries, not hardware.
"""
import argparse
import ctypes as C
import importlib.util
from pathlib import Path
import random
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('proof',HERE/'verify.py'); proof=importlib.util.module_from_spec(spec); spec.loader.exec_module(proof)
MASK=0xffffffff; BASE=proof.RAM; MMIO=0x4002420c


def machine(s1,s2,length,saved,profile,limit,fail,read8):
    proof.verify(proof.RAW); r=[0]*32; r[10]=s1; r[11]=s2; r[12]=length
    pc=BASE; events=[]; operations=0; known=restored=return_known=0; saved_mmio=return_value=boundary=0
    def request(kind,address=0,value=0):
        nonlocal operations,boundary
        boundary=pc
        if operations>=limit: return False,3,0
        operations+=1; events.append((kind,pc,address,value))
        if operations==fail: return False,1,0
        if kind==0: return True,0,saved
        if kind==3: return True,0,read8(address)
        return True,0,0
    for _ in range(10000):
        o=pc-BASE
        if o==0: r[15]=0x40024000; pc+=4
        elif o==4:
            ok,flow,x=request(0,MMIO)
            if not ok: break
            r[14]=x; saved_mmio=x; known=1; pc+=4
        elif o==8:
            ok,flow,_=request(1,MMIO,0)
            if not ok: break
            pc+=4
        elif o==12:
            ok,flow,_=request(2)
            if not ok: break
            pc+=4
        elif o in (16,18,22,38,56):
            op,a,b,target=proof.branch(proof.RAW,o); cond=(r[a]==r[b]); pc=target if (cond if op=='beq' else not cond) else pc+(2 if o in (16,18,22) else 4)
        elif o==20: r[15]=0; pc+=2
        elif o==24 or o==60: r[15]=0x40024000; pc+=4
        elif o==28 or o==64:
            ok,flow,_=request(1,MMIO,r[14])
            if not ok: break
            restored=1; pc+=4
        elif o==32: r[10]=1; pc+=2
        elif o==68: r[10]=0; pc+=2
        elif o==34 or o==70:
            return_known=1; return_value=r[10]; flow=0; break
        elif o==36: r[15]=(r[15]+1)&MASK; pc+=2
        elif o==42: r[16]=(r[10]+r[15])&MASK; pc+=4
        elif o==46: r[13]=(r[11]+r[15])&MASK; pc+=4
        elif o==50:
            ok,flow,x=request(3,r[16])
            if not ok: break
            r[16]=x; pc+=4
        elif o==54:
            if not profile: boundary=pc; flow=2; break
            ok,flow,x=request(3,r[13])
            if not ok: break
            r[13]=x; pc+=2
        else: raise ValueError(f'unknown pc {pc:#x}')
    else: raise ValueError('step limit')
    return (flow,operations,saved_mmio,return_value,boundary,known,restored,return_known,events)


class Request(C.Structure): _fields_=[('kind',C.c_int),('pc',C.c_uint32),('address',C.c_uint32),('value',C.c_uint32)]
INVOKE=C.CFUNCTYPE(C.c_int,C.c_void_p,C.POINTER(Request),C.POINTER(C.c_uint32))
class Backend(C.Structure): _fields_=[('context',C.c_void_p),('invoke',INVOKE)]
class Model(C.Structure): _fields_=[('backend',Backend),('last',Request),('operations',C.c_uint32),('max_operations',C.c_uint32),('saved_mmio',C.c_uint32),('return_value',C.c_uint32),('boundary_pc',C.c_uint32),('saved_known',C.c_uint),('restored',C.c_uint),('return_known',C.c_uint),('xwchc_profile',C.c_uint),('flow',C.c_int)]


def worker(dll):
    lib=C.CDLL(str(dll)); lib.mc_init.argtypes=[C.POINTER(Model),C.POINTER(Backend),C.c_uint]; lib.mc_compare.argtypes=[C.POINTER(Model),C.c_uint32,C.c_uint32,C.c_uint32]; lib.mc_compare.restype=C.c_int
    rng=random.Random(4160442)
    def check(n,s1,s2,length,saved,profile,limit,fail,read8):
        events=[]
        @INVOKE
        def invoke(ctx,ptr,out):
            req=ptr.contents; events.append((req.kind,req.pc,req.address,req.value))
            if len(events)==fail: return 0
            out[0]=saved if req.kind==0 else (read8(req.address) if req.kind==3 else 0)
            return 1
        backend=Backend(None,invoke); m=Model(); lib.mc_init(C.byref(m),C.byref(backend),profile); m.max_operations=limit
        flow=lib.mc_compare(C.byref(m),s1,s2,length)
        actual=(flow,m.operations,m.saved_mmio,m.return_value,m.boundary_pc,m.saved_known,m.restored,m.return_known,events)
        expected=machine(s1,s2,length,saved,profile,limit,fail,read8)
        if actual!=expected: raise ValueError(f'projection mismatch case {n}: {actual!r} != {expected!r}')
        return actual
    for n in range(20000):
        s1=rng.choice((0,0xfffffffc,rng.getrandbits(32))); s2=rng.choice((0,s1,rng.getrandbits(32))); length=rng.randrange(20); saved=rng.getrandbits(32); profile=n&1; limit=rng.randrange(0,16); fail=rng.randrange(0,18)
        check(n,s1,s2,length,saved,profile,limit,fail,lambda address: ((address^(address>>8))*37)&255)
    print('PASS: 20000 random C vs candidate-PC traces, backend failures, observation limits and conditional Xwchc',flush=True)
    # Independent synthetic memory: the right side differs at exactly one position.
    # Every byte value and every mismatch position is exercised with enough budget.
    for value in range(256):
        for mismatch in range(9):
            def memory(address):
                if 0x2000<=address<0x2008 and address-0x2000==mismatch: return value^1
                return value
            result=check(f'value={value} mismatch={mismatch}',0x1000,0x2000,8,0xa5a5a5a5,1,128,0,memory)
            reads=[event for event in result[-1] if event[0]==3]
            expected_reads=16 if mismatch==8 else 2*(mismatch+1)
            if result[0]!=0 or result[3]!=(1 if mismatch==8 else 0) or not result[6] or len(reads)!=expected_reads:
                raise ValueError('complete path expectation mismatch')
    print('PASS: 2304 deterministic complete traces, each byte value and all mismatch positions plus equality',flush=True)
    # Exercise every completed/failed event boundary for an eight-byte equality.
    for fail in range(0,22):
        for limit in range(0,22):
            check(f'fail={fail} limit={limit}',0x1000,0x2000,8,0x12345678,1,limit,fail,lambda _: 0x5a)
    print('PASS: 484 failure/observation-boundary combinations',flush=True)


def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--vcvars',type=Path); g.add_argument('--worker',type=Path); a=p.parse_args()
    if a.worker: worker(a.worker); return
    source=ROOT/'experiments/tsl9-wch-memcmp-contract/src/memcmp_contract.c'
    with tempfile.TemporaryDirectory(prefix='tsl9-mc-proof-') as tmp:
        tmp=Path(tmp); batch=tmp/'build.bat'
        for name,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            dll=tmp/(name+'.dll'); batch.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}" /link /EXPORT:mc_init /EXPORT:mc_compare\n@exit /b %errorlevel%\n',encoding='utf8')
            subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=tmp,check=True)
            subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)],check=True)
    print('Conditional candidate-byte semantics; no installed ROM or hardware claim.')

if __name__=='__main__': main()
