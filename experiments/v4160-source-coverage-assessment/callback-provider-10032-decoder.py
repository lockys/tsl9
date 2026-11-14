#!/usr/bin/env python3
"""Bounded 0x10032 wrapper decoder; indirect callee is not executed."""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('m',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CODE=bytes.fromhex('b707040003a387040d4681451385c1120283')
def validate_local(image):m.need(image[0x8032:0x8044]==CODE,'wrapper bytes')
def execute(code,gp,pointer,ra):
 r=[0]*32;r[1]=ra;r[3]=gp;pc=0x10032;events=[]
 for _ in range(7):
  off=pc-0x10032;hw=int.from_bytes(code[off:off+2],'little')
  if hw&3!=3:
   if hw==0x460d:r[12]=3
   elif hw==0x4581:r[11]=0
   elif hw==0x8302:return r[10],r[11],r[12],r[6]&~1,r[1],events
   else:raise ValueError('unsupported compressed')
   pc+=2;continue
  w=int.from_bytes(code[off:off+4],'little');op=w&127;rd=w>>7&31;f=w>>12&7;rs1=w>>15&31
  if op==0x37:r[rd]=w&0xfffff000
  elif op==0x13 and f==0:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;r[rd]=(r[rs1]+imm)&MASK
  elif op==3 and f==2:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;m.need(addr==0x40048,'pointer address');r[rd]=pointer;events.append(('load32',addr,pointer))
  else:raise ValueError('unsupported instruction')
  pc+=4
 raise ValueError('step limit')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);validate_local(image);rng=random.Random(0x10032)
 for i in range(65536):
  gp=rng.getrandbits(32);ptr=rng.getrandbits(32);ra=rng.getrandbits(32)
  m.need(execute(CODE,gp,ptr,ra)==((gp+300)&MASK,0,3,ptr&~1,ra,[('load32',0x40048,ptr)]),'wrapper result')
 for i in range(len(CODE)):
  data=bytearray(image);data[0x8032+i]^=1
  try:validate_local(data)
  except ValueError:continue
  raise ValueError('mutation survived')
 print('PASS: 65536 gp/pointer/return-address cases; 18 local byte mutations rejected')
 print('LIMIT: successful pointer read and preserved initial gp assumed; indirect target semantics, returns, reachability and hardware unproven')
if __name__=='__main__':main()
