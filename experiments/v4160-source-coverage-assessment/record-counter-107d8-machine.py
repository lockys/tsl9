#!/usr/bin/env python3
"""Limited byte interpreter of the post-callback decision until first store."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('model',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def execute(code,ret,old,threshold,sp=0x1000,counter=0x2000,memory=None):
 r=[0]*32;r[10]=ret;r[8]=counter;r[2]=sp;mem={counter:old,**{(sp+12+i)&MASK:(threshold>>(8*i))&255 for i in range(4)}} if memory is None else memory;pc=0x107d8;events=[]
 for _ in range(12):
  if pc in (0x107ee,0x107fc):return pc,events
  hw=code[pc]|(code[pc+1]<<8)
  if hw&3!=3:
   if hw==0x45b2:
    addr=(r[2]+12)&MASK;r[11]=sum(mem[(addr+i)&MASK]<<(8*i) for i in range(4));events.append(('load32',addr,r[11]));pc+=2;continue
   if hw==0x0785:r[15]=(r[15]+1)&MASK;pc+=2;continue
   if hw==0xbfe9:pc=0x107ee;continue
   if hw&0xe003==0xc001:
    rs=8+((hw>>7)&7);off=((hw>>12&1)<<8)|((hw>>10&3)<<3)|((hw>>5&3)<<6)|((hw>>3&3)<<1)|((hw>>2&1)<<5);off=off-512 if off&256 else off
    pc=pc+off if r[rs]==0 else pc+2;continue
   raise ValueError('unsupported compressed')
  w=sum(code[pc+i]<<(8*i) for i in range(4));op=w&127;rd=w>>7&31;f=w>>12&7;rs1=w>>15&31;rs2=w>>20&31
  if op==3 and f==4:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;r[rd]=mem[addr];events.append(('load8',addr,r[rd]));pc+=4
  elif op==0x13 and f==7:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;r[rd]=r[rs1]&imm;pc+=4
  elif op==0x63 and f==7:
   off=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);off=off-8192 if off&4096 else off;pc=pc+off if r[rs1]>=r[rs2] else pc+4
  elif op==0x23 and f==0:
   imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;mem[addr]=r[rs2]&255;events.append(('store8',addr,mem[addr]));pc+=4
  else:raise ValueError(f'unsupported {pc:x} {w:08x}')
 raise ValueError('step limit')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);code={}
 for addr,hexbytes in m.WINDOWS:
  b=bytes.fromhex(hexbytes);code.update({addr+i:v for i,v in enumerate(b)})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump bytes');code.update({0x10814:0xe9,0x10815:0xbf})
 cases=0
 for old in range(256):
  for threshold in (*range(256),256,0x10000,0xffffffff):
   for ret in (0,1):
    pc,events=execute(code,ret,old,threshold);value,target=m.project(ret,old,threshold)
    expected=([('load8',0x2000,old),('load32',0x100c,threshold)] if ret else [])+[('store8',0x2000,value)]
    m.need((pc,events)==(target,expected),'differential');cases+=1
 print(f'PASS: {cases} decoded-original versus projection comparisons, including access order')
 print('LIMIT: limited decoder, successful accesses and fixed non-alias memory; no callback execution, interrupts, general ISA, target or hardware proof')
if __name__=='__main__':main()
