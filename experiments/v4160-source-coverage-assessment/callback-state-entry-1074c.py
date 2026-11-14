#!/usr/bin/env python3
"""Pin state routine entry and its first four direct call sites."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('model','record-counter-107d8.py');tail=load('tail','record-counter-clear-tail.py');queue=load('queue','queue-clear-820c-decoder.py')
CODE=bytes.fromhex('411106c622c42a84efc0ffb1efa05f9a0145ef70ffaaeff01f8d')
def validate_local(image):m.need(image[0x874c:0x8766]==CODE,'state entry bytes')
def calls():
 m.need(CODE[:8]==bytes.fromhex('411106c622c42a84') and CODE[16:18]==bytes.fromhex('0145'),'entry prologue or zero argument')
 return tuple(tail.jal(pc,int.from_bytes(CODE[off:off+4],'little')) for pc,off in ((0x10754,8),(0x10758,12),(0x1075e,18),(0x10762,22)))
def enter(sp,ra,s0,a0,mem):
 sp=(sp-16)&MASK
 for offset,value in ((12,ra),(8,s0)):
  for i in range(4):mem[(sp+offset+i)&MASK]=(value>>(i*8))&255
 return sp,a0

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);queue.validate(image);validate_local(image)
 m.need(calls()==((1,0xd272),(1,0xb0fc),(1,0x820c),(1,0x10032)),'call sequence')
 qcode={0x820c+i:b for i,b in enumerate(queue.PROVIDER)}
 for value in range(65536):
  sp,s0=enter(0x20010000,0x12345678,0xabcdef01,value,{})
  ret,events=queue.execute(qcode,0,0x20004000);m.need((sp,s0,ret,events)==(0x2000fff0,value,0,[('store8',0x200040c1,0)]),'entry or queue call')
 for i in range(len(CODE)):
  changed=bytearray(image);changed[0x874c+i]^=1
  try:validate_local(changed)
  except ValueError:continue
  raise ValueError('mutation survived')
 print('PASS: direct calls d272,b0fc,820c(0),10032; 65536 frame/queue cases; 26 local byte mutations')
 print('LIMIT: calls treated as separate boundaries; assumes prior calls return, preserve gp/s0/sp, and successful writes; no callee or hardware proof')
if __name__=='__main__':main()
