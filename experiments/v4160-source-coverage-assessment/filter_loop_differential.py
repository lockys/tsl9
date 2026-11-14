"""Compare C event projection to the fixed-PC filter loop event projection."""
import argparse
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('loop',HERE/'filter_loop_step.py')
loop=importlib.util.module_from_spec(spec); spec.loader.exec_module(loop)


def worker(dll,mutant):
    image=loop.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=loop.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    u=ctypes.c_uint32; h=ctypes.c_uint16
    fn=ctypes.CDLL(str(dll)).tsl9_filter_iteration
    fn.argtypes=[u,u,u,u,u,ctypes.POINTER(h),ctypes.POINTER(u)]; fn.restype=None
    def check(value,s1,s3,s4):
        # This compare uses non-overlapping addresses; alias ordering is tested
        # in the separately retained event-level projection.
        inputs=[value,(value+1)&65535,(value^0xffff),((value*31)&65535)]
        mem={0x1000+2*i+j:(x>>(8*j))&255 for i,x in enumerate(inputs) for j in range(2)}
        result=loop.step(image,mem,0x2000,0x1000,s1,s3,s4)
        want=[*result[:5],s1&255,s4&255,s3]+[mem[0x200c+2*i]|mem[0x200d+2*i]<<8 for i in range(4)]
        out=(u*12)(); fn(0x2000,0x1000,s1,s3,s4,(h*4)(*inputs),out)
        return list(out)==want
    if mutant:
        if all(check(*x) for x in ((1,0xff,7,0x101),(65535,0xffffffff,7,0x1ff),(3,1,8,0))): raise ValueError('mutant accepted')
        print('PASS: mutant rejected',flush=True); return
    for value in range(65536):
        if not check(value,value,0xdeadbeef,value^0xff): raise ValueError('comparison mismatch')
    print('PASS: 65536 C/PC projection comparisons',flush=True)


def main():
    p=argparse.ArgumentParser(); group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--vcvars',type=Path); group.add_argument('--worker',type=Path); p.add_argument('--mutant',action='store_true'); args=p.parse_args()
    if args.worker: worker(args.worker,args.mutant); return
    source=(HERE/'filter_loop_model.c').read_text(encoding='utf-8'); variants=[('base',source)]
    for name,old,new in (('shift','<<5','<<4'),('counter','(s1+1u)&255u','(s1+2u)&255u'),('pointer','s0+8u','s0+4u'),('byte','s4&255u','s4&127u')):
        if source.count(old)!=1: raise ValueError('ambiguous mutation')
        variants.append((name,source.replace(old,new)))
    with tempfile.TemporaryDirectory(prefix='tsl9-loop-') as temp:
        folder=Path(temp)
        for label,flags in (('C','/TC /std:c11'),('Cpp','/TP /std:c++17')):
            for name,text in variants:
                src=folder/(label+name+'.c'); dll=folder/(label+name+'.dll'); batch=folder/'build.bat'; src.write_text(text,encoding='utf-8')
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{src}" /Fe:"{dll}"\n@exit /b %errorlevel%\n',encoding='utf-8')
                subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=folder,check=True)
                cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll)]
                if name!='base': cmd.append('--mutant')
                subprocess.run(cmd,check=True)
    print('Synthetic event projection; no memory faults, provider or hardware execution.')

if __name__=='__main__': main()
