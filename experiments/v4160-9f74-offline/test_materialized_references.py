#!/usr/bin/env python3
import unittest
import materialized_references as m
class MaterializationTest(unittest.TestCase):
 def test_original(self):
  rows=m.inspect(m.BIN.read_bytes());self.assertEqual(len(rows),3)
  self.assertEqual([r[1] for r in rows],[0x9f74]*3)
  self.assertEqual([r[3] for r in rows],[0x9124,0x90b0,0x9124])
 def test_address_and_jal_mutations(self):
  for pc,h,jpc,target,rd in m.SITES:
   code=bytearray.fromhex(h);self.assertEqual(m.decode_address(pc,code),0x9f74)
   code[0]^=0x80
   with self.subTest(pc=pc),self.assertRaises(ValueError):m.decode_address(pc,code)
   j=bytearray.fromhex(h)[jpc-pc:jpc-pc+4]
   with self.subTest(jpc=jpc),self.assertRaises(ValueError):m.decode_jal(jpc,j,1-rd)
   j[3]^=0x80;self.assertNotEqual(m.decode_jal(jpc,j,rd),target)
 def test_identity_pinned(self):
  image=bytearray(m.BIN.read_bytes());image[0x20b8]^=1
  with self.assertRaises(ValueError):m.inspect(image)
if __name__=='__main__':unittest.main()
