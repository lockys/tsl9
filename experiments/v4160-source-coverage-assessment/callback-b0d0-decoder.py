#!/usr/bin/env python3
"""Limited original-instruction decoder for callback b0d0; synthetic RAM."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('m',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CODE=bytes.fromhex('93f71500014595c39387010c9386310c094603c717006365e6000507a380e7008507e398d7fe13c515008280')
def validate_local(image):m.need(image[0x30d0:0x30fc]==CODE,'callback bytes')
def execute(gp,a1,values):
 r=[0]*32;r[3]=gp;r[11]=a1;mem={(gp+193+i)&MASK:v for i,v in enumerate(values)};events=[];pc=0xb0d0
 for _ in range(40):
  off=pc-0xb0d0;m.need(0<=off<len(CODE),'pc out of bounds');hw=int.from_bytes(CODE[off:off+2],'little')
  if hw&3!=3:
   if hw==0x4501:r[10]=0
   elif hw==0xc395:
    if r[15]==0:pc=0xb0fa;continue
   elif hw==0x4609:r[12]=2
   elif hw==0x0705:r[14]=(r[14]+1)&MASK
   elif hw==0x0785:r[15]=(r[15]+1)&MASK
   elif hw==0x8082:return r[10],mem,events
   else:raise ValueError('unsupported compressed')
   pc+=2;continue
  w=int.from_bytes(CODE[off:off+4],'little');op=w&127;rd=w>>7&31;f=w>>12&7;rs1=w>>15&31;rs2=w>>20&31
  if op==0x13:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm
   if f==0:r[rd]=(r[rs1]+imm)&MASK
   elif f==7:r[rd]=r[rs1]&imm
   elif f==4:r[rd]=(r[rs1]^imm)&MASK
   else:raise ValueError('unsupported immediate')
  elif op==3 and f==4:
   imm=w>>20;imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;r[rd]=mem[addr];events.append(('read8',addr,r[rd]))
  elif op==0x23 and f==0:
   imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;mem[addr]=r[rs2]&255;events.append(('write8',addr,mem[addr]))
  elif op==0x63 and f in (1,6):
   imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm
   if (r[rs1]!=r[rs2] if f==1 else r[rs1]<r[rs2]):pc=(pc+imm)&MASK;continue
  else:raise ValueError('unsupported opcode')
  pc+=4
 raise ValueError('step limit')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);validate_local(image)
 for x in range(256):
  for flag in range(256):
   vals=[x,(x+1)&255,(x+2)&255];gp=(0xffffff40+x)&MASK;ret,mem,events=execute(gp,flag,vals);odd=flag&1
   m.need(ret==((flag^1) if odd else 0),'return')
   expected=[(v+1 if v<=2 else v) if odd else v for v in vals]
   m.need([mem[(gp+193+i)&MASK] for i in range(3)]==expected,'counter bytes')
   m.need(len([e for e in events if e[0]=='read8'])==(3 if odd else 0),'reads')
   m.need(len([e for e in events if e[0]=='write8'])==(sum(v<=2 for v in vals) if odd else 0),'writes')
 for i in range(len(CODE)):
  data=bytearray(image);data[0x30d0+i]^=1
  try:validate_local(data)
  except ValueError:continue
  raise ValueError('mutation accepted')
 print('PASS: 65536 input/counter patterns, modular gp; 44 local byte mutations rejected')
 print('LIMIT: finite decoder and synthetic memory, successful accesses; callback invocation and hardware not established')
if __name__=='__main__':main()
