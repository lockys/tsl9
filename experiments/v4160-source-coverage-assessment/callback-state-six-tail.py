#!/usr/bin/env python3
"""Decode the state-six scheduler tail call and contrast normal return."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
branch=load('branch','callback-state-branch-1077e.py');tail=load('tail','record-counter-clear-tail.py');m=branch.m
CODE=bytes.fromhex('2244b24081465146854517050000130565e841016f801f97b240224441018280')
def validate_local(image):m.need(image[0x87a0:0x87c0]==CODE,'state tail bytes')
def decode():
 m.need(CODE[:10]==bytes.fromhex('2244b240814651468545'),'restore and compressed constants')
 au=int.from_bytes(CODE[10:14],'little');ad=int.from_bytes(CODE[14:18],'little');m.need(au&0xfff==0x517 and ad&0xfffff==0x50513,'address operands')
 imm=ad>>20;imm=imm-4096 if imm&2048 else imm;callback=(0x107aa+(au&0xfffff000)+imm)&MASK
 m.need(CODE[18:20]==bytes.fromhex('4101') and CODE[24:]==bytes.fromhex('b240224441018280'),'frame restore bytes')
 link,target=tail.jal(0x107b4,int.from_bytes(CODE[20:24],'little'))
 return callback,1,20,0,link,target

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);branch.validate_local(image);validate_local(image)
 m.need(decode()==(0x10630,1,20,0,0,0x9124),'tail arguments')
 for i in range(len(CODE)):
  changed=bytearray(image);changed[0x87a0+i]^=1
  try:validate_local(changed)
  except ValueError:continue
  raise ValueError('mutation survived')
 for value in range(65536):m.need((branch.execute(value)[1]==0x107a0)==(value==6),'full-width condition')
 print('PASS: full-width state-six selects tail jump 0x9124(0x10630,1,20,0); 32 byte mutations')
 print('LIMIT: static call/return boundary only; normal returns and stack loads assumed, no scheduler, target reachability or hardware proof')
if __name__=='__main__':main()
