#!/usr/bin/env python3
"""Negative and edge-case tests for the bounded record counter interpreter."""
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('machine',HERE/'record-counter-107d8-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m
class CounterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.image=(ROOT/m.BIN).read_bytes();m.validate(cls.image);cls.code={}
  for pc,h in m.WINDOWS:
   cls.code.update({pc+i:b for i,b in enumerate(bytes.fromhex(h))})
  cls.code.update({0x10814:0xe9,0x10815:0xbf})
 def test_each_window_byte_rejected_after_rehash(self):
  old=m.SHA
  try:
   count=0
   for pc,h in m.WINDOWS:
    for i in range(len(bytes.fromhex(h))):
     b=bytearray(self.image);b[pc-0x8000+i]^=1;m.SHA=hashlib.sha256(b).hexdigest()
     with self.assertRaisesRegex(ValueError,'instructions at'):m.validate(b)
     count+=1
   self.assertEqual(count,30)
  finally:m.SHA=old
 def test_unsupported_instruction_rejected_by_interpreter(self):
  code=dict(self.code);code[0x107da]=0xff;code[0x107db]=0xff;code[0x107dc]=0xff;code[0x107dd]=0xff
  with self.assertRaisesRegex(ValueError,'unsupported'):machine.execute(code,1,4,5)
 def test_shared_memory_reads_before_writes(self):
  # Counter aliases the high threshold byte: old=1 yields threshold 0x01000000.
  mem={0x100c:0,0x100d:0,0x100e:0,0x100f:1}
  pc,events=machine.execute(self.code,1,1,0,sp=0x1000,counter=0x100f,memory=mem)
  self.assertEqual((pc,events),(0x107ee,[('load8',0x100f,1),('load32',0x100c,0x01000000),('store8',0x100f,2)]))
  self.assertEqual(mem[0x100f],2)
 def test_zero_return_never_reads_threshold(self):
  mem={0x2000:123};pc,events=machine.execute(self.code,0,123,0,memory=mem)
  self.assertEqual((pc,events),(0x107ee,[('store8',0x2000,0)]))
 def test_full_width_boundaries(self):
  for old in range(256):
   for threshold in (0,1,255,256,65535,65536,0xffffffff):
    pc,events=machine.execute(self.code,1,old,threshold);value,target=m.project(1,old,threshold)
    self.assertEqual((pc,events[-1][2]),(target,value))
if __name__=='__main__':unittest.main()
