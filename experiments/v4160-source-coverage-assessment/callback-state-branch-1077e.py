#!/usr/bin/env python3
"""Decode two full-width state branches after the 0x12b24/0x13d48 calls."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('m',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
WINDOWS=((0x1077e,bytes.fromhex('19c8')),(0x1079a,bytes.fromhex('9947631ef400')))
def validate_local(image):
 for pc,b in WINDOWS:m.need(image[pc-0x8000:pc-0x8000+len(b)]==b,'branch bytes')
def execute(s0):
 hw=int.from_bytes(WINDOWS[0][1],'little');m.need(hw&0xe003==0xc001 and ((hw>>7)&7)+8==8,'c.beqz encoding')
 off=((hw>>12&1)<<8)|((hw>>10&3)<<3)|((hw>>5&3)<<6)|((hw>>3&3)<<1)|((hw>>2&1)<<5);off=off-512 if off&256 else off
 first=0x1077e+off if s0==0 else 0x10780
 hw2=int.from_bytes(WINDOWS[1][1][:2],'little');m.need(hw2==0x4799,'li a5,6')
 w=int.from_bytes(WINDOWS[1][1][2:],'little');m.need(w&127==0x63 and (w>>12&7)==1 and (w>>15&31)==8 and (w>>20&31)==15,'bne operands')
 off=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);off=off-8192 if off&4096 else off
 second=0x1079c+off if s0!=6 else 0x107a0
 return first,second

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);validate_local(image)
 count=0
 for hi in range(256):
  for lo in range(256):
   value=(hi<<24)|lo;first,second=execute(value)
   m.need(first==(0x10794 if value==0 else 0x10780),'first branch');m.need(second==(0x107a0 if value==6 else 0x107b8),'second branch');count+=1
 for pc,b in WINDOWS:
  for i in range(len(b)):
   changed=bytearray(image);changed[pc-0x8000+i]^=1
   try:validate_local(changed)
   except ValueError:continue
   raise ValueError('mutation survived')
 print(f'PASS: {count} branch input cases and 8 local byte mutations')
 print('LIMIT: both points analyzed separately; assumes intervening calls return and preserve s0, no scheduling/provider or hardware proof')
if __name__=='__main__':main()
