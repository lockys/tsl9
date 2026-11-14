#!/usr/bin/env python3
"""Conditional TX header event projection; fixed encoding, not CPU emulation."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
s=importlib.util.spec_from_file_location('entry',HERE/'tx-entry-length-guard.py');entry=importlib.util.module_from_spec(s);s.loader.exec_module(entry)
RAW=bytes.fromhex('93076042b307f602972600209386666b6177134757f59375f40f9907b6972390e7002382b70013578400ce95a381e7002e97238137011377f70f8145')
def decode(b):entry.need(b==RAW,'header window')
def project(a2,s0,s3):
    base=(0x2000b18c+((a2*1062)&M)+6)&M
    low=s0&255;high=s0>>8
    writes=((base,2,0x7f55),((base+4)&M,1,low),((base+3)&M,1,high&255),((base+2)&M,1,s3&255))
    return base,writes,(high+low+s3)&255

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/entry.BIN).read_bytes();entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==entry.SHA,'identity');raw=img[0xace:0xb0a];decode(raw)
 for i in range(len(raw)):
  b=bytearray(raw);b[i]^=1
  try:decode(b)
  except ValueError:continue
  raise ValueError('mutation accepted')
 for n in range(65536):
  for bank in (0,1):
   base,writes,checksum=project(bank,n,0x123456ab)
   entry.need(base==(0x2000b192+1062*bank)&M and writes[0][2]==0x7f55 and checksum==((n&255)+(n>>8)+0xab)&255,'projection')
 for n in (0x10000,0x10001,0xffffffff):
  entry.need(project(0,n,0)[2]==((n>>8)+(n&255))&255,'wide length')
 print(f'PASS: 131072 header projections, 3 wide lengths, {len(raw)} byte mutations rejected')
 print('LIMIT: fixed encoding projection; assumes successful writes, no interrupts or concurrency; no reachability, provider or hardware claim')
if __name__=='__main__':main()
