#!/usr/bin/env python3
"""Three pinned address-passing sites, not evidence of callback execution."""
import hashlib
from pathlib import Path
from decode_semantics import BIN,SHA,MASK
SITES=((0xa0b8,'170500001305c5ebeff04f86',0xa0c0,0x9124,1),
       (0xa1b8,'170500001305c5db2385010aefe0dfee',0xa1c4,0x90b0,1),
       (0xa356,'170500001305e5c141016fe05fdc',0xa360,0x9124,0))

def sign(x,bits):return x-(1<<bits) if x&(1<<(bits-1)) else x

def decode_address(pc,code):
 if len(code)<8:raise ValueError('short materialization')
 upper=int.from_bytes(code[:4],'little');lower=int.from_bytes(code[4:8],'little')
 if (upper&127,(upper>>7)&31,lower&127,(lower>>7)&31,(lower>>12)&7,(lower>>15)&31)!=(0x17,10,0x13,10,0,10):raise ValueError('bad address instruction')
 return (pc+(upper&0xfffff000)+sign(lower>>20,12))&MASK

def decode_jal(pc,code,rd):
 if len(code)!=4:raise ValueError('short jal')
 w=int.from_bytes(code,'little')
 if w&127!=0x6f or (w>>7)&31!=rd:raise ValueError('bad jal')
 imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 return (pc+sign(imm,21))&MASK

def inspect(image):
 if hashlib.sha256(image).hexdigest()!=SHA:raise ValueError('image identity')
 results=[]
 for pc,expected,jal_pc,target,rd in SITES:
  code=image[pc-0x8000:pc-0x8000+len(bytes.fromhex(expected))]
  if code!=bytes.fromhex(expected):raise ValueError('site identity')
  addr=decode_address(pc,code)
  direct=decode_jal(jal_pc,code[jal_pc-pc:jal_pc-pc+4],rd)
  if addr!=0x9f74 or direct!=target:raise ValueError('site targets')
  results.append((pc,addr,jal_pc,direct,rd))
 return results

def main():
 for pc,addr,jal,target,rd in inspect(BIN.read_bytes()):print(f'PASS: {pc:#x} materializes {addr:#x}; JAL {jal:#x} -> {target:#x}, rd=x{rd}')
 print('LIMIT: static address passing only; not evidence of registration, callback execution or GP preservation')
if __name__=='__main__':main()
