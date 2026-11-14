#!/usr/bin/env python3
"""Header projection regression: explicit byte layout and instruction identity."""
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('header',HERE/'tx-header-projection.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
class HeaderTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.image=(ROOT/h.entry.BIN).read_bytes()
  if hashlib.sha256(cls.image).hexdigest()!=h.entry.SHA:raise RuntimeError('original image identity mismatch')
 def test_fixed_instruction_mutations(self):
  raw=self.image[0xace:0xb0a];h.decode(raw)
  for i in range(len(raw)):
   b=bytearray(raw);b[i]^=1
   with self.subTest(i=i),self.assertRaises(ValueError):h.decode(b)
 def test_header_layout_and_order(self):
  base,writes,checksum=h.project(1,0x1234,0xab)
  self.assertEqual(base,0x2000b5b8)
  self.assertEqual(writes,((base,2,0x7f55),(base+4,1,0x34),(base+3,1,0x12),(base+2,1,0xab)))
  self.assertEqual(checksum,0xf1)
  mem={}
  for addr,width,value in writes:
   for i in range(width):mem[(addr+i)&0xffffffff]=(value>>(8*i))&255
  self.assertEqual(bytes(mem[base+i] for i in range(5)),bytes.fromhex('557fab1234'))
 def test_full_width_wrap(self):
  base,events,checksum=h.project(0xffffffff,0xffffffff,0xffffffff)
  self.assertEqual(base,(0x2000b192-1062)&0xffffffff)
  self.assertEqual(events[2][2],255);self.assertEqual(events[3][2],255);self.assertEqual(checksum,253)
if __name__=='__main__':unittest.main()
