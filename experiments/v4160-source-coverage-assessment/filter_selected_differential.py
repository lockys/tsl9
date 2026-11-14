"""Compare portable C event projection with original-byte bounded decoder."""
import argparse,ctypes,importlib.util,random,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('machine',HERE/'filter_selected_machine.py')
machine=importlib.util.module_from_spec(spec); spec.loader.exec_module(machine)

def worker(dll,mutant):
    image=machine.projection.route.A.audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    machine.projection.route.flow.flow(image)
    u=ctypes.c_uint32; h=ctypes.c_uint16
    fn=ctypes.CDLL(str(dll)).filter_selected
    fn.argtypes=[u,ctypes.POINTER(h),ctypes.POINTER(u),ctypes.POINTER(u)]; fn.restype=None
    rng=random.Random(0x4160)
    mismatches=0
    for i in range(4096):
        index=i%14; fields=tuple(rng.randrange(65536) for _ in range(4)); reads=tuple(rng.getrandbits(32) for _ in range(7))
        expected,_=machine.run(image,index,fields,reads)
        out=(u*18)(); fn(index,(h*4)(*fields),(u*7)(*reads),out)
        actual=tuple((out[2*j],out[2*j+1]) for j in range(9))
        if actual!=expected:
            mismatches+=1
            if not mutant: raise ValueError(f'differential mismatch {i}')
            break
    if mutant and not mismatches: raise ValueError('mutant survived')
    print('PASS: mutant rejected' if mutant else 'PASS: 4096 C/decoded-instruction comparisons',flush=True)

def main():
    p=argparse.ArgumentParser(); group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); p.add_argument('--mutant',action='store_true'); args=p.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'filter_selected_model.c').read_text(encoding='utf-8'); variants=[('base',source)]
    for name,old,new in (('mask','1u << index','2u << index'),('field','fields[3]<<16','fields[2]<<16'),('read','reads[6]&~1u','reads[0]&~1u')):
        if source.count(old)!=1: raise ValueError('ambiguous mutant')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-selected-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Conditional synthetic event projection; not firmware ABI, MMIO or hardware execution.')
if __name__=='__main__': main()
