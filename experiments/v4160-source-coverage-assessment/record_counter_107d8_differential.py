#!/usr/bin/env python3
"""Compare host C projection to limited original-byte interpreter."""
import argparse,ctypes,importlib.util,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('machine',HERE/'record-counter-107d8-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m
def worker(dll,root,mutant):
 image=(root/m.BIN).read_bytes();m.validate(image);code={}
 for addr,hexbytes in m.WINDOWS:
  data=bytes.fromhex(hexbytes);code.update({addr+i:v for i,v in enumerate(data)})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf})
 u=ctypes.c_uint32;f=ctypes.CDLL(str(dll)).record_counter;f.argtypes=[u,u,u,ctypes.POINTER(u)];f.restype=None
 def compare(ret,old,limit):
  pc,events=machine.execute(code,ret,old,limit);out=(u*2)();f(ret,old,limit,out);return list(out)==[pc,events[-1][2]]
 if mutant:
  cases=((0,10,20),(1,255,1),(1,4,5),(0x100,2,3),(1,255,256))
  m.need(not all(compare(*x) for x in cases),'mutant survived');print('PASS: mutant rejected');return
 count=0
 for old in range(256):
  for limit in (*range(256),256,0x10000,0xffffffff):
   for ret in (0,1):m.need(compare(ret,old,limit),'C mismatch');count+=1
 print(f'PASS: {count} C versus original-byte decoder comparisons')
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--vcvars',type=Path);g.add_argument('--worker',type=Path);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--mutant',action='store_true');a=p.parse_args()
 if a.worker:worker(a.worker,a.root,a.mutant);return
 src=(HERE/'record_counter_107d8_model.c').read_text();variants=[('base',src)]
 for name,old,new in (('return','result == 0u','result != 0u'),('mask','& 255u','& 254u'),('bound','threshold <= next','threshold < next'),('width','threshold <= next','(threshold & 255u) <= next')):
  m.need(src.count(old)==1,'mutant pattern');variants.append((name,src.replace(old,new)))
 with tempfile.TemporaryDirectory(prefix='tsl9-counter-') as tmp:
  d=Path(tmp)
  for lang,flags in (('C','/TC /std:c11'),('C++','/TP /std:c++17')):
   for name,text in variants:
    source=d/(name+'.c');dll=d/(name+'.dll');bat=d/'build.bat';source.write_text(text)
    bat.write_text(f'@call "{a.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n@cl /nologo /W4 /LD {flags} "{source}" /Fe:"{dll}"\n@exit /b %errorlevel%\n')
    subprocess.run(['cmd.exe','/d','/c',str(bat)],cwd=d,check=True)
    cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(dll),'--root',str(a.root)]
    if name!='base':cmd.append('--mutant')
    subprocess.run(cmd,check=True);print(lang,name,'done',flush=True)
 print('LIMIT: restricted decoder and successful accesses; no callback, exceptions, alias, target ABI or hardware execution')
if __name__=='__main__':main()
