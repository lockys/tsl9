#!/usr/bin/env python3
"""Decode b0fc local instructions between indirect-call boundaries.

Synthetic memory and successful accesses; no callee, actual control flow,
stack, fault, asynchronous or hardware execution modeled.
"""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');model=load('model','callback-provider-b0fc-boundaries.py')
def execute(ret,base,pointer):
 code=model.CODE;r=[0]*32;r[8]=base;r[9]=0x40000;mem={};events=[];pc=0xb116
 for _ in range(9):
  off=pc-0xb0fc;hw=int.from_bytes(code[off:off+2],'little')
  if hw&3!=3:
   if hw!=0x478d:raise ValueError('unexpected compressed opcode')
   r[15]=3;pc+=2;continue
  w=int.from_bytes(code[off:off+4],'little');op=w&127;rd=(w>>7)&31;f=(w>>12)&7;rs1=(w>>15)&31;rs2=(w>>20)&31
  if op==0x13 and f==0:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;r[rd]=(r[rs1]+imm)&MASK
  elif op==0x17:r[rd]=(pc+(w&0xfffff000))&MASK
  elif op==3 and f==2:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;m.need(addr==0x40080,'slot address');r[rd]=pointer;events.append(('load32',addr,pointer))
  elif op==0x23 and f in (0,1):
   imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;size=1<<f;v=r[rs2]&((1<<(8*size))-1)
   for i in range(size):mem[(addr+i)&MASK]=(v>>(8*i))&255
   events.append(('store'+str(size*8),addr,v))
  else:raise ValueError('unsupported opcode')
  pc+=4
  if pc==0xb130:break
 else:raise ValueError('boundary not reached')
 m.need((r[10],r[15])==(0xb0d0,pointer),'callback argument or pointer')
 # Execute the original post-call sb at 0xb132 separately; callback result
 # replaces a0 and is retained in full for the later tail boundary.
 w=int.from_bytes(code[0xb132-0xb0fc:0xb136-0xb0fc],'little');m.need(w&127==0x23 and (w>>12)&7==0 and (w>>15)&31==8 and (w>>20)&31==10,'return store encoding')
 imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;addr=(base+imm)&MASK;mem[addr]=ret&255;events.append(('store8',addr,ret&255))
 return mem,events

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);model.validate_local(image);rng=random.Random(0xb116)
 for i in range(65536):
  gp=rng.getrandbits(32);base=(gp+192)&MASK;ret=rng.getrandbits(32);ptr=rng.getrandbits(32);mem,e=execute(ret,base,ptr);projection=model.project(gp,ret,0,ptr,0,0)
  m.need(e==[projection[1],projection[2],('load32',0x40080,ptr),projection[4]],'events');m.need([mem[(base+j)&MASK] for j in range(4)]==[ret&255,3,3,3],'bytes')
 print('PASS: 65536 original-instruction local decodes agree with boundary projection, callback address and slot read')
 print('LIMIT: partial instruction decoder, successful accesses, independent call boundary; no actual callback/provider execution or hardware proof')
if __name__=='__main__':main()
