#!/usr/bin/env python3
"""Host C/C++ differential with transformed storage binding, not target ABI."""
import argparse,ctypes,hashlib,importlib.util,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('decode',HERE/'decode_semantics.py');dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def worker(dll,mutant):
 lib=ctypes.CDLL(str(dll));put=lib.init_fixture;put.argtypes=[ctypes.c_ubyte,ctypes.c_ubyte,ctypes.c_ubyte];put.restype=None
 get=lib.read_fixture;get.argtypes=[ctypes.c_uint];get.restype=ctypes.c_ubyte
 invoke=lib.call_leaf;invoke.argtypes=[];invoke.restype=None
 mismatches=0
 for pattern in (0,1,0x55,0xff):
  for old in range(256):
   before={i:(pattern+i*37)&255 for i in range(7)};before[3]=old
   expected,_=dec.project(dec.EXPECTED,(3-175)&dec.MASK,before)
   put(pattern,old,0);invoke();actual={i:get(i) for i in range(7)}
   mismatches+=actual!=expected
 need((mismatches>0)==mutant,'unexpected candidate/mutant result')
 print(('mutant rejected' if mutant else 'candidate passed')+f': 1024 cases, {mismatches} mismatches',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--clang',type=Path);p.add_argument('--linker',type=Path);p.add_argument('--worker',type=Path);p.add_argument('--mutant',action='store_true');a=p.parse_args()
 if a.worker:worker(a.worker,a.mutant);return
 if not a.clang or not a.linker:p.error('--clang and --linker required')
 raw=dec.BIN.read_bytes();need(hashlib.sha256(raw).hexdigest()==dec.SHA,'image identity');need(raw[0x1f74:0x1f7a]==dec.EXPECTED,'leaf identity');dec.decode(dec.EXPECTED)
 file=HERE/'candidate.c';data=file.read_bytes()
 need(hashlib.sha256(data).hexdigest()=='5a32b3b1314dc0af8f61a6fe414df42a5eac5323a25e5ac3a904b26e0d1677ad','candidate identity')
 source=data.decode('utf-8')
 anchor='extern volatile unsigned char tsl9_9f74_data __attribute__((visibility("hidden")));'
 need(source.count(anchor)==1,'storage anchor');source=source.replace(anchor,'extern volatile unsigned char fixture[7];\n#define tsl9_9f74_data fixture[3]')
 statement='tsl9_9f74_data = 0;';need(source.count(statement)==1,'statement anchor')
 variants={'actual':source,'nonzero':source.replace(statement,'tsl9_9f74_data = 1;'),'no-store':source.replace(statement,'(void)0;'),'neighbor':source.replace(statement,'fixture[3] = 0; fixture[0] = 0;')}
 need(len(set(variants.values()))==4,'distinct mutations')
 fixture='''\n#ifdef __cplusplus\nextern "C" {\n#endif\nvolatile unsigned char fixture[7];\n__declspec(dllexport) void init_fixture(unsigned char a,unsigned char b,unsigned char c){unsigned int i;(void)c;for(i=0;i<7;i++)fixture[i]=(unsigned char)(a+i*37);fixture[3]=b;}\n__declspec(dllexport) unsigned char read_fixture(unsigned int i){return fixture[i];}\n__declspec(dllexport) void call_leaf(void){tsl9_9f74_candidate();}\n#ifdef __cplusplus\n}\n#endif\n'''
 with tempfile.TemporaryDirectory(prefix='tsl9-9f74-host-') as tmp:
  root=Path(tmp)
  for lang,std in [('c','c11'),('c++','c++17')]:
   for name,text in variants.items():
    unit=root/'unit.c';obj=root/'unit.obj';dll=root/'unit.dll';unit.write_text(text+fixture,encoding='utf-8')
    subprocess.run([str(a.clang.resolve()),'--target=x86_64-pc-windows-msvc','-c','-x',lang,'-std='+std,'-O2',str(unit),'-o',str(obj)],check=True,cwd=root)
    subprocess.run([str(a.linker.resolve()),'/nologo','/dll','/noentry','/nodefaultlib',str(obj),'/out:'+str(dll)],check=True,cwd=root)
    cmd=[sys.executable,*(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else []),'-B',str(Path(__file__).resolve()),'--worker',str(dll)]
    if name!='actual':cmd.append('--mutant')
    print(lang,name,flush=True);subprocess.run(cmd,check=True,cwd=root)
 need(hashlib.sha256(file.read_bytes()).digest()==hashlib.sha256(data).digest(),'candidate changed during test')
 print('LIMIT: transformed storage binding, host execution and seven fixture final bytes only; no claims on other memory, target ABI, transient writes, live GP or device')
if __name__=='__main__':main()
