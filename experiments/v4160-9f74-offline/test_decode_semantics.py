#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('decode',Path(__file__).with_name('decode_semantics.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class DecodeTest(unittest.TestCase):
 def test_field_mutations_rejected(self):
  base=int.from_bytes(m.EXPECTED[:4],'little')
  for bit in (0,7,12,15,20,25):
   with self.subTest(bit=bit),self.assertRaises(ValueError):m.decode((base^(1<<bit)).to_bytes(4,'little')+m.EXPECTED[4:])
  with self.assertRaises(ValueError):m.decode(m.EXPECTED[:-1]+b'\x00')
 def test_zero_write_wrap_and_neighbors(self):
  out,event=m.project(m.EXPECTED,0xffffff51,{0:3,1:4,0xffffffff:5})
  self.assertEqual(out,{0:0,1:4,0xffffffff:5});self.assertEqual(event,('write8',0,0))
 def test_unmapped_and_invalid_rejected(self):
  with self.assertRaises(ValueError):m.project(m.EXPECTED,0,{})
  with self.assertRaises(ValueError):m.project(m.EXPECTED,-1,{})
 def test_all_prior_bytes(self):
  for v in range(256):self.assertEqual(m.project(m.EXPECTED,0,{175:v})[0][175],0)
if __name__=='__main__':unittest.main()
