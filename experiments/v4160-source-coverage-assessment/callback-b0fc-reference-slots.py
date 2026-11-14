#!/usr/bin/env python3
"""Identify optional reference slots used by b0fc; no target execution."""
import argparse,hashlib,importlib.util,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');ref=load('ref','filter_reference_providers.py');b=load('b','callback-provider-b0fc-boundaries.py')
EXPECTED={'V1.31':(0x43c4e,0x43932,bytes.fromhex('373700201307c7191c33342363ffd700')),'V1.40':(0x43cda,0x439be,bytes.fromhex('373700201307c71e1c33342363ffd700'))}
TAIL=bytes.fromhex('011122cc26ca4ac84ec6b747024006ce')
def verify(raw,digest,name,copy,fill):
 ref.check(raw,digest,copy,fill);first,tail,prefix=EXPECTED[name]
 for address,want in ((0x40048,0x2000039c),(0x40080,first),(0x4022c,tail)):
  if struct.unpack_from('<I',raw,address-0x40000)[0]!=want:raise ValueError('slot mismatch')
 for address,want in ((first,prefix),(tail,TAIL)):
  if raw[address-0x40000:address-0x40000+len(want)]!=want:raise ValueError('target prefix mismatch')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root;image=(root/m.BIN).read_bytes();m.validate(image);b.validate_local(image);found=0
 for name,path,digest,copy,fill in ref.CANDIDATES:
  carrier=root/path
  if not carrier.exists():print('SKIP',name,'carrier unavailable');continue
  raw=carrier.read_bytes();verify(raw,digest,name,copy,fill);found+=1
  for addr in (0x40080,0x4022c,*range(EXPECTED[name][0],EXPECTED[name][0]+16),*range(EXPECTED[name][1],EXPECTED[name][1]+16)):
   altered=bytearray(raw);altered[addr-0x40000]^=1
   # Update digest to ensure rejection is due to slot/prefix check itself.
   try:verify(altered,hashlib.sha256(altered).hexdigest(),name,copy,fill)
   except ValueError:continue
   raise ValueError('mutation accepted')
  print('PASS',name,': slots 0x40080=',hex(EXPECTED[name][0]),'0x4022c=',hex(EXPECTED[name][1]),'; 34 byte mutations rejected after rehash')
 if not found:raise SystemExit('No reference carrier available')
 print('LIMIT: candidate identity and prefixes only, not resident installation, target semantics, callback invocation, or device execution')
if __name__=='__main__':main()
