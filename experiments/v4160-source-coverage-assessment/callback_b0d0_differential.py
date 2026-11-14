#!/usr/bin/env python3
"""Compare a host C/C++ callback model to the bounded original-byte decoder."""
import argparse,ctypes,importlib.util,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('decoder',HERE/'callback-b0d0-decoder.py');dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec);m=dec.m
def worker(dll,root,mutant):
 image=(root/m.BIN).read_bytes();m.validate(image);dec.validate_local(image)
 u=ctypes.c_uint32;byte=ctypes.c_uint8;f=ctypes.CDLL(str(dll)).callback_b0d0;f.argtypes=[u,ctypes.POINTER(byte)];f.restype=u
 def compare(flag,vals):
  result,mem,_=dec.execute(0x20004000,flag,vals);out=(byte*3)(*vals);actual=f(flag,out)
  return (actual,list(out))==(result,[mem[0x200040c1+i] for i in range(3)])
 if mutant:
  m.need(not all(compare(flag,[0,2,3]) for flag in (0,1,2,3,0x101)),'mutant survived');print('PASS: mutant rejected');return
 count=0
 for value in range(256):
  for flag in (*range(256),0x100,0x101,0xfffffffe,0xffffffff):
   m.need(compare(flag,[value,(value+1)&255,(value+2)&255]),'C mismatch');count+=1
 print('PASS:',count,'C vs original-byte decoder cases')
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--vcvars',type=Path);g.add_argument('--worker',type=Path);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--mutant',action='store_true');a=p.parse_args()
 if a.worker:worker(a.worker,a.root,a.mutant);return
 src=(HERE/'callback_b0d0_model.c').read_text();variants=[('base',src)]
 for name,old,new in (('flag','(flag & 1u) == 0u','(flag & 1u) != 0u'),('threshold','<= 2u','< 2u'),('return','flag ^ 1u','(flag ^ 1u) & 255u')):
  m.need(src.count(old)==1,'mutation pattern');variants.append((name,src.replace(old,new)))
 with tempfile.TemporaryDirectory(prefix='tsl9-b0d0-') as tmp:
  d=Path(tmp)
  for lang,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
   for name,text in variants:
    source=d/(name+'.c');dll=d/(name+'.dll');bat=d/'build.bat';source.write_text(text)
    bat.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
    subprocess.run(['cmd.exe','/d','/c',str(bat)],cwd=d,check=True)
    cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll),'--root',str(a.root)]
    if name!='base':cmd.append('--mutant')
    subprocess.run(cmd,check=True);print(lang,name,'done',flush=True)
 print('LIMIT: host C model and partial decoder assume valid distinct memory, no exceptions or concurrency; not target ABI or hardware')
if __name__=='__main__':main()
