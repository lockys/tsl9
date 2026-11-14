#!/usr/bin/env python3
"""Test conditional V1.31 registration projection and its input gates."""
import hashlib,importlib.util,os,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('TSL9_ROOT',HERE.parents[1]))
s=importlib.util.spec_from_file_location('reg',HERE/'callback-b0fc-reference-registration.py');reg=importlib.util.module_from_spec(s);s.loader.exec_module(reg)
class Tests(unittest.TestCase):
 def test_full_and_last_slot(self):
  self.assertEqual(reg.register(254,255,0x20002000,0xb0d0),(254,255,(0x200023f8,0xb0d0)))
  self.assertEqual(reg.register(255,255,0x20002000,0xb0d0),(255,255,None))
  self.assertEqual(reg.register(0,0,0x20002000,0xb0d0),(255,0,None))
  self.assertEqual(reg.register(0,1,0x20002000,0xb0d0),(0,1,(0x20002000,0xb0d0)))
 def test_modular_table_address(self):
  self.assertEqual(reg.register(1,2,0xfffffffc,0xb0d0),(1,2,(0,0xb0d0)))
 def test_saved_failure_byte_and_callback_argument(self):
  ret,_,write=reg.register(255,255,0x20002000,0xb0d0)
  mem,events=reg.dec.execute(ret,0x200040c0,0x43c4e)
  self.assertEqual(write,None);self.assertEqual(mem[0x200040c0],255)
  self.assertEqual(events,[('store8',0x200040c1,3),('store16',0x200040c2,0x303),('load32',0x40080,0x43c4e),('store8',0x200040c0,255)])
 def test_body_mutations_with_rehashed_carrier(self):
  name,path,digest,copy,fill=reg.slots.ref.CANDIDATES[0];carrier=ROOT/path
  if not carrier.exists():self.fail('V1.31 reference unavailable')
  raw=carrier.read_bytes();reg.slots.verify(raw,digest,name,copy,fill);reg.check_body(raw)
  for i in range(len(reg.BODY)):
   with self.subTest(index=i):
    data=bytearray(raw);data[0x3c4e+i]^=1
    # Mutations outside pinned prefixes are caught by the full body check.
    newhash=hashlib.sha256(data).hexdigest()
    if i>=16:reg.slots.verify(data,newhash,name,copy,fill)
    with self.assertRaises(ValueError):reg.check_body(data)
if __name__=='__main__':unittest.main()
