#!/usr/bin/env python3
"""Pin and decode nonzero state path call sites, without executing providers."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
branch=load('branch','callback-state-branch-1077e.py');tail=load('tail','record-counter-clear-tail.py');m=branch.m
CODE=bytes.fromhex('81461306401f85451795ffff1305e53aef805f990145ef30205b')
def validate_local(image):m.need(image[0x8780:0x879a]==CODE,'nonzero path bytes')
def decode():
 def word(off):return int.from_bytes(CODE[off:off+4],'little')
 m.need(int.from_bytes(CODE[:2],'little')==0x4681 and int.from_bytes(CODE[6:8],'little')==0x4585,'compressed argument constants')
 addi=word(2);m.need((addi&0xfffff)==0x00613,'a2 addi');a2=addi>>20
 au=word(8);ad=word(12);m.need((au&0xfff)==0x517 and (ad&0xfffff)==0x50513,'callback address operands');imm=ad>>20;imm=imm-4096 if imm&2048 else imm;callback=(0x10788+(au&0xfffff000)+imm)&MASK
 first=tail.jal(0x10790,word(16));m.need(int.from_bytes(CODE[20:22],'little')==0x4501,'zero argument');second=tail.jal(0x10796,word(22))
 return (callback,1,a2,0),first,second

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);branch.validate_local(image);validate_local(image)
 m.need(decode()==((0x9b36,1,500,0),(1,0x9124),(1,0x13d48)),'decoded call arguments')
 for i in range(len(CODE)):
  data=bytearray(image);data[0x8780+i]^=1
  try:validate_local(data)
  except ValueError:continue
  raise ValueError('mutation survived')
 for value in range(1,65536):m.need(branch.execute(value)[0]==0x10780,'nonzero path')
 m.need(branch.execute(0)[0]==0x10794,'zero skips first call')
 print('PASS: nonzero path calls 0x9124(0x9b36,1,500,0), then 0x13d48(0); 26 local byte mutations')
 print('LIMIT: static call arguments assuming intervening returns/preserved state; no proof scheduling succeeded, callee side effects, path reachability or hardware')
if __name__=='__main__':main()
