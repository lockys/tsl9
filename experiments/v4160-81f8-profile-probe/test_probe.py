#!/usr/bin/env python3
"""Mutation checks for ELF evidence used by the 0x81f8 profile probe."""
import importlib.util,struct,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('probe.py'))
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)

def sample():
 data=bytearray(256)
 struct.pack_into('<16sHHIIIIIHHHHHH',data,0,b'\x7fELF\x01\x01\x01',2,243,1,0,52,84,0,52,32,1,40,1,0)
 struct.pack_into('<8I',data,52,1,124,0x81f8,0x81f8,10,10,5,1)
 struct.pack_into('<10I',data,84,0,1,6,0x81f8,124,10,0,0,2,0)
 data[124:134]=bytes.fromhex('17450020034525cf8280')
 return data

def change(data,offset,value):
 struct.pack_into('<I',data,offset,value)
 return data

class Evidence(unittest.TestCase):
 def test_valid(self):
  self.assertEqual(probe.section(sample()).hex(),'17450020034525cf8280')
 def test_truncation_and_identity(self):
  for data in (b'',sample()[:51],sample()[:100],b'X'+sample()[1:]):
   with self.subTest(size=len(data)),self.assertRaises(ValueError):probe.section(data)
 def test_section_mutations(self):
  for offset,value in ((84+4,8),(84+8,2),(84+12,0x81fa),(84+16,255),(84+20,0),(84+20,0xffffffff)):
   with self.subTest(offset=offset,value=value),self.assertRaises(ValueError):probe.section(change(sample(),offset,value))
 def test_segment_mutations(self):
  for offset,value in ((52,0),(56,125),(60,0x81f9),(68,9),(72,9),(76,4)):
   with self.subTest(offset=offset,value=value),self.assertRaises(ValueError):probe.section(change(sample(),offset,value))
if __name__=='__main__':unittest.main()
