#!/usr/bin/env python3
"""Limited decoder of APP queue-clear helper at 0x820c; no full CPU."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('model',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
PROVIDER=bytes.fromhex('894763e7a7009387010caa97a38007008280')
def validate(image):
 m.validate(image);m.need(image[0x20c:0x21e]==PROVIDER,'queue-clear bytes')
def execute(code,index,gp):
 r=[0]*32;r[10]=index;r[3]=gp;pc=0x820c;events=[]
 for _ in range(10):
  hw=code[pc]|code[pc+1]<<8
  if hw&3!=3:
   if hw==0x4789:r[15]=2;pc+=2;continue
   if hw==0x97aa:r[15]=(r[15]+r[10])&MASK;pc+=2;continue
   if hw==0x8082:return r[10],events
   raise ValueError(f'unsupported compressed {pc:x}')
  w=sum(code[pc+i]<<(8*i) for i in range(4));op=w&127;rd=w>>7&31;f=w>>12&7;rs1=w>>15&31;rs2=w>>20&31
  if op==0x63 and f==6:
   off=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);off=off-8192 if off&4096 else off;pc=pc+off if r[rs1]<r[rs2] else pc+4
  elif op==0x13 and f==0:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;r[rd]=(r[rs1]+imm)&MASK;pc+=4
  elif op==0x23 and f==0:
   imm=(w>>25<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;events.append(('store8',(r[rs1]+imm)&MASK,r[rs2]&255));pc+=4
  else:raise ValueError(f'unsupported instruction {pc:x}')
 raise ValueError('step limit')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();validate(image);code={0x820c+i:b for i,b in enumerate(PROVIDER)}
 count=0
 for index in (*range(65536),0x7fffffff,0x80000000,0xfffffffe,0xffffffff):
  for gp in (0,0x20004000,0xffffffff):
   ret,events=execute(code,index,gp);expected=[('store8',(gp+193+index)&MASK,0)] if index<=2 else []
   m.need((ret,events)==(index,expected),'decoder mismatch');count+=1
 print(f'PASS: {count} decoded queue-clear cases against projection, including wrap and unsigned boundaries')
 print('LIMIT: compressed opcodes fixed, bounded decoder, successful accesses; not target CPU, ABI, concurrency or hardware proof')
if __name__=='__main__':main()
