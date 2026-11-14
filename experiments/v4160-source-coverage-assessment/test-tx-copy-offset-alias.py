#!/usr/bin/env python3
"""Regression tests for loop byte validation and forward overlap ordering."""
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('alias',HERE/'tx-copy-offset-alias.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class AliasTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  image=(ROOT/m.h.entry.BIN).read_bytes()
  if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=m.h.entry.SHA:raise RuntimeError('firmware identity')
  cls.code={}
  for address,hexbytes in m.machine.m.WINDOWS:
   b=bytes.fromhex(hexbytes)
   if image[address-0x8000:address-0x8000+len(b)]!=b:raise RuntimeError('copy bytes')
   cls.code.update({address+i:v for i,v in enumerate(b)})
 def test_forward_overlap_uses_latest_byte(self):
  r=[0]*32;r[8]=8;r[9]=0x1004;r[15]=0x1000;mem={0x1004+i:i+1 for i in range(9)}
  for i in range(8):
   pc,r,events=m.machine.execute(self.code,r,mem)
   self.assertEqual((pc,events),(0x8b0a,[('read',0x1004+i,1),('write',0x1005+i,1)]))
  self.assertEqual(r[14],8)
 def test_compressed_mutations_rejected_or_change_trace(self):
  r=[0]*32;r[8]=1;r[9]=0x1000;r[14]=255;r[15]=0x2000
  original=m.machine.execute(self.code,r,{0x1000:7})
  for address in (0x8b0e,0x8b5e,0x8b60,0x8b6a):
   bad=self.code.copy();bad[address]^=4
   with self.subTest(address=address):
    try: result=m.machine.execute(bad,r,{0x1000:7})
    except (ValueError,KeyError):continue
    self.assertNotEqual(result,original)
if __name__=='__main__':unittest.main()
