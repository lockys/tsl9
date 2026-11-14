#!/usr/bin/env python3
"""Conditional checksum predicate at the 0x1069e callback boundary."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('checksum',HERE/'counter-input-checksum-witness.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def validate(image):
 c.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==c.SHA,'firmware identity')
 for pc,h in c.WINDOWS:
  data=bytes.fromhex(h);c.need(image[pc-0x8000:pc-0x8000+len(data)]==data,'instruction bytes')
def predicate(src):return int(c.checksum(src)==src[10])
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);validate((p.parse_args().root/c.BIN).read_bytes())
 cases=0
 for n in range(256):
  # Fixed 258-byte buffer is large enough even when length is 255.
  src=bytearray((i*37+11)&255 for i in range(258));src[2]=n
  # Position 10 is excluded when present; length <= 7 does not read it.
  checksum=c.checksum(src)
  for value in range(256):
   src[10]=value;c.need(c.checksum(src)==checksum,'checksum byte independence');c.need(predicate(src)==int(value==checksum),'predicate');cases+=1
  for i in range(258):
   if i in (2,10):continue
   old=src[i];src[i]=(old+1)&255;delta=(c.checksum(src)-checksum)&255;src[i]=old
   expected=1 if i in (0,1) or 3<=i<3+n else 0
   c.need(delta==expected,'input dependence')
 print(f'PASS: {cases} length/checksum-value pairs; 65536 byte-position influence checks')
 print('LIMIT: fixed-byte callback and hand-written checksum projection; assumes stable successful reads, normal returns and adequate input, not CPU/ABI or hardware proof')
if __name__=='__main__':main()
