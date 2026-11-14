#!/usr/bin/env python3
"""Decode b0fc epilogue using shared synthetic byte-addressed memory."""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');model=load('model','callback-provider-b0fc-boundaries.py')
def execute(sp,s1,ret,mem):
 r=[0]*32;r[2]=sp;r[9]=s1;r[10]=ret;events=[];pc=0xb136
 def lw(addr):
  value=sum(mem.get((addr+i)&MASK,0)<<(8*i) for i in range(4));events.append(('load32',addr,value));return value
 for _ in range(9):
  off=pc-0xb0fc;hw=int.from_bytes(model.CODE[off:off+2],'little')
  if hw&3!=3:
   if hw==0x4422:r[8]=lw((r[2]+8)&MASK)
   elif hw==0x40b2:r[1]=lw((r[2]+12)&MASK)
   elif hw==0x4492:r[9]=lw((r[2]+4)&MASK)
   elif hw==0x4585:r[11]=1
   elif hw==0x0141:r[2]=(r[2]+16)&MASK
   elif hw==0x8302:return (r[6]&~1,r[10],r[11],r[12],r[1],r[2],r[8],r[9],events)
   else:raise ValueError('unsupported compressed')
   pc+=2;continue
  w=int.from_bytes(model.CODE[off:off+4],'little');op=w&127;rd=w>>7&31;f=w>>12&7;rs1=w>>15&31;imm=w>>20;imm=imm-4096 if imm&2048 else imm
  if op==3 and f==2:r[rd]=lw((r[rs1]+imm)&MASK)
  elif op==0x13 and f==0:r[rd]=(r[rs1]+imm)&MASK
  else:raise ValueError('unsupported opcode')
  pc+=4
 raise ValueError('step limit')
def put(mem,addr,value):
 for i in range(4):mem[(addr+i)&MASK]=(value>>(8*i))&255

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);model.validate_local(image);rng=random.Random(0xb136)
 for _ in range(65536):
  sp=rng.getrandbits(32)&~3;ra=rng.getrandbits(32);s0=rng.getrandbits(32);s1=rng.getrandbits(32);target=rng.getrandbits(32);ret=rng.getrandbits(32);mem={}
  for a,v in ((sp+4,s1),(sp+8,s0),(sp+12,ra),(0x4022c,target)):put(mem,a,v)
  # The sampled ranges are disjoint, explicitly checked rather than assumed.
  m.need(all(((sp+i)&MASK) not in range(0x4022c,0x40230) for i in range(4,16)),'unexpected alias')
  got=execute(sp,0x40000,ret,mem);m.need(got[:8]==(target&~1,ret,1,1600,ra,(sp+16)&MASK,s0,s1),'tail mismatch')
  m.need([x[1] for x in got[8]]==[(sp+8)&MASK,0x4022c,(sp+12)&MASK,(sp+4)&MASK],'load order')
 print('PASS: 65536 synthetic tail decodes with disjoint frame/slot; load order checked')
 print('LIMIT: finite decoder; successful synthetic reads and no interference; stack validity, target execution and hardware unknown')
if __name__=='__main__':main()
