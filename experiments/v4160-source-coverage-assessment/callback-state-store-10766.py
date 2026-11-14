#!/usr/bin/env python3
"""Decode state byte writes after prior 0x1074c external calls return."""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
model=load('model','record-counter-107d8.py');tail=load('tail','record-counter-clear-tail.py')
CODE=bytes.fromhex('1375f40f97c7ff1f2385078497c7ff1fa381a784ef20a03a')
def validate(image):model.validate(image);model.need(image[0x8766:0x877e]==CODE,'state-store instructions')
def execute(code,s0):
 r=[0]*32;r[8]=s0;pc=0x10766;events=[]
 for _ in range(6):
  w=int.from_bytes(code[pc-0x10766:pc-0x10766+4],'little');op=w&127;rd=w>>7&31;funct=w>>12&7;rs1=w>>15&31;rs2=w>>20&31
  if op==0x13 and funct==7:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;r[rd]=r[rs1]&imm
  elif op==0x17:r[rd]=(pc+(w&0xfffff000))&MASK
  elif op==0x23 and funct==0:
   imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;events.append(('store8',(r[rs1]+imm)&MASK,r[rs2]&255))
  elif op==0x6f:
   link,target=tail.jal(pc,w);return r[10],events,link,target
  else:raise ValueError(f'unsupported opcode at {pc:x}')
  pc+=4
 raise ValueError('missing call')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/model.BIN).read_bytes();validate(image);rng=random.Random(0x10766)
 for i in range(65536):
  value=rng.getrandbits(32);a0,events,link,target=execute(CODE,value)
  model.need((a0,events,link,target)==(value&255,[('store8',0x2000bfb4,0),('store8',0x2000bfb5,value&255)],1,0x12b24),'decoded result')
 print('PASS: 65536 decoded state-store cases; call target 0x12b24')
 print('LIMIT: assumes earlier calls return and preserve s0; successful writes; stops before provider, no global reachability or hardware proof')
if __name__=='__main__':main()
