#!/usr/bin/env python3
"""Conditional composition of wrapper outputs and a reference fill projection.

Not a CPU emulation: the fill is a byte-wise model only. Provider peripheral
side effects, startup, faults, asynchronous writes and installed ROM are not
modeled; wrapper return is assumed. Arbitrary gp cases are synthetic aliases.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');ref=load('ref','filter_reference_providers.py');first=load('first','callback-provider-d272-decoder.py');second=load('second','callback-provider-10032-decoder.py')
def fill(mem,addr,value,n):
 for i in range(n):mem[(addr+i)&MASK]=value&255

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root;image=(root/m.BIN).read_bytes();m.validate(image);first.validate_local(image);second.validate_local(image)
 count=0
 for name,path,digest,copy,fill_addr in ref.CANDIDATES:
  carrier=root/path
  if not carrier.exists():print('SKIP',name,'carrier unavailable');continue
  ref.check(carrier.read_bytes(),digest,copy,fill_addr);count+=1
  for delta in range(-24,25):
   gp=(0x2000bf48-300+delta)&MASK
   for seed in range(256):
    mem={(0x2000bf48+i)&MASK:seed for i in range(-24,43)}
    a,b,n,target,ra,_=first.execute(first.CODE,0x2000039c,0x10758);m.need((a,b,n,target,ra)==(0x2000bf48,0,19,0x2000039c,0x10758),'first wrapper');fill(mem,a,b,n)
    a,b,n,target,ra,_=second.execute(second.CODE,gp,0x2000039c,0x10766);m.need((a,b,n,target,ra)==((gp+300)&MASK,0,3,0x2000039c,0x10766),'second wrapper');fill(mem,a,b,n)
    for i in range(-24,43):
     expected=0 if 0<=i<19 or delta<=i<delta+3 else seed
     m.need(mem[0x2000bf48+i]==expected,'ordered fill composition')
  # Under reset gp, the two requested ranges do not overlap.
  start=(0x20004000+300)&MASK;m.need(start+3<=0x2000bf48,'reset gp disjoint')
  print('PASS',name,': 12544 synthetic ordered-fill cases; reset-gp ranges disjoint')
 if not count:raise SystemExit('No reference carrier available')
 print('LIMIT: reference carrier conditional on installation and successful startup; byte-fill projection, not execution or hardware evidence')
if __name__=='__main__':main()
