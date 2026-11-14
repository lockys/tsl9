#!/usr/bin/env python3
"""Pinned 0xb0fc call-boundary projection, not instruction emulation.

Assumes both indirect calls return, gp/s0/s1/sp and their saved frame remain
intact and local accesses succeed. Unknown callees and MMIO are not executed.
"""
import argparse,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
s=importlib.util.spec_from_file_location('m',HERE/'record-counter-107d8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CODE=bytes.fromhex('411126c2b7040400bc4422c41384010c06c611468145228582978d47a300f400930730302311f40083a7040817050000130585fa82972300a400224403a3c422b240924413060064854541010283')
def validate_local(image):m.need(image[0x30fc:0x314a]==CODE,'b0fc bytes')
def project(gp,ret,p1,p2,p3,ra):
 base=(gp+192)&MASK
 return [('call',p1&~1,base,0,4,0xb116),('store8',(base+1)&MASK,3),('store16',(base+2)&MASK,0x303),('call',p2&~1,0xb0d0,None,None,0xb132),('store8',base,ret&255),('tail',p3&~1,ret,1,1600,ra)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);validate_local(image);rng=random.Random(0xb0fc)
 for i in range(65536):
  gp=rng.getrandbits(32);ret=rng.getrandbits(32);p1=rng.getrandbits(32);p2=rng.getrandbits(32);p3=rng.getrandbits(32);ra=rng.getrandbits(32);e=project(gp,ret,p1,p2,p3,ra);base=(gp+192)&MASK
  m.need(e[0]==('call',p1&~1,base,0,4,0xb116) and e[1:3]==[('store8',(base+1)&MASK,3),('store16',(base+2)&MASK,0x303)] and e[3]==('call',p2&~1,0xb0d0,None,None,0xb132) and e[4]==('store8',base,ret&255) and e[5]==('tail',p3&~1,ret,1,1600,ra),'projection mismatch')
 for i in range(len(CODE)):
  data=bytearray(image);data[0x30fc+i]^=1
  try:validate_local(data)
  except ValueError:continue
  raise ValueError('mutation survived')
 print('PASS: 65536 call-boundary projections; 78 local byte mutations rejected')
 print('LIMIT: pinned hand projection; unknown indirect callees, stack alias, faults, callback invocation, reachability and hardware not established')
if __name__=='__main__':main()
