#!/usr/bin/env python3
"""Fixed-byte projection of threshold clear path around an unknown provider."""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('model',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CODE=bytes.fromhex('230004000145ef70ffa06244f2402685d24405616ff01ff4')
def validate_tail(image):m.need(image[0x87f8:0x8810]==CODE,'clear-tail bytes')
def jal(pc,word):
 m.need(word&127==0x6f,'jal opcode');off=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1);off=off-(1<<21) if off&(1<<20) else off
 return word>>7&31,(pc+off)&MASK
def after_provider(sp,s1,mem):
 def word(addr):return sum(mem[(addr+i)&MASK]<<(8*i) for i in range(4))
 return {'s0':word((sp+24)&MASK),'ra':word((sp+28)&MASK),'a0':s1,'s1':word((sp+20)&MASK),'sp':(sp+32)&MASK,'target':0x1074c}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);validate_tail(image)
 m.need(jal(0x107fe,int.from_bytes(CODE[6:10],'little'))==(1,0x820c),'provider target and link')
 m.need(jal(0x1080c,int.from_bytes(CODE[20:24],'little'))==(0,0x1074c),'tail target')
 rng=random.Random(0x10802)
 for i in range(65536):
  sp=rng.getrandbits(32);s1=rng.getrandbits(32);vals=[rng.getrandbits(32) for _ in range(3)];mem={}
  for off,val in zip((24,28,20),vals):
   for n in range(4):mem[(sp+off+n)&MASK]=(val>>(n*8))&255
  result=after_provider(sp,s1,mem);m.need((result['s0'],result['ra'],result['s1'],result['a0'],result['sp'],result['target'])==(*vals,s1,(sp+32)&MASK,0x1074c),'tail projection')
 for i in range(len(CODE)):
  b=bytearray(image);b[0x87f8+i]^=1
  try:validate_tail(b)
  except ValueError:continue
  raise ValueError('mutation survived')
 print('PASS: 65536 post-provider tail projections; 24 byte mutations rejected; call 0x820c and tail 0x1074c decoded')
 print('LIMIT: hand-written projection; assumes provider returns preserving sp/s1 and uses memory after its effects; no provider behavior, alignment, reachability or hardware proof')
if __name__=='__main__':main()
