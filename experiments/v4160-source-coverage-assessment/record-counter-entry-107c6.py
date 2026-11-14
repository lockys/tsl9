#!/usr/bin/env python3
"""Fixed-byte projection of entry up to, not including, the indirect call."""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('counter',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CODE=bytes.fromhex('011122cc2a843a8526ca06ce2ec6b2848296')
def validate_entry(image):
 m.need(image[0x87c6:0x87d8]==CODE,'entry bytes')
def validate(image):
 m.validate(image);validate_entry(image)
def enter(sp,old_s0,old_s1,ra,a0,a1,a2,a3,a4,mem):
 sp=(sp-32)&MASK;events=[]
 def store(offset,value):
  addr=(sp+offset)&MASK;value&=MASK
  for i in range(4):mem[(addr+i)&MASK]=(value>>(8*i))&255
  events.append(('store32',addr,value))
 store(24,old_s0);store(20,old_s1);store(28,ra);store(12,a1)
 return {'sp':sp,'s0':a0,'s1':a2,'a0':a4,'a1':a1,'a2':a2,'a3':a3,'a4':a4,'ra':0x107d8,'target':a3&0xfffffffe,'events':events}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();validate(image)
 rng=random.Random(0x107c6)
 for i in range(65536):
  vals=[rng.getrandbits(32) for _ in range(9)];sp,x,y,ra,a0,a1,a2,a3,a4=vals;mem={};out=enter(*vals,mem)
  m.need(out['sp']==(sp-32)&MASK and out['s0']==a0 and out['s1']==a2 and out['a0']==a4 and out['ra']==0x107d8 and out['target']==(a3&~1),'registers')
  m.need(out['events']==[('store32',(sp-8)&MASK,x),('store32',(sp-12)&MASK,y),('store32',(sp-4)&MASK,ra),('store32',(sp-20)&MASK,a1)],'order')
  m.need(sum(mem[(sp-20+j)&MASK]<<(8*j) for j in range(4))==a1,'threshold save')
 for i in range(len(CODE)):
  b=bytearray(image);b[0x87c6+i]^=1
  try:validate_entry(b)
  except ValueError:continue
  raise ValueError('entry mutation survived')
 print('PASS: 65536 synthetic entry projections; 18 local-byte mutations detected')
 print('LIMIT: fixed-byte projection, successful stores and no concurrent effects; indirect callee not executed, alignment/ABI/hardware unverified')
if __name__=='__main__':main()
