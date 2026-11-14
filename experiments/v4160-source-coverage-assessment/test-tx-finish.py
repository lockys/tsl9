#!/usr/bin/env python3
"""Regression tests of TX finish projection, wrap and shared-memory ordering."""
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
metadata=load('metadata','tx-finish-metadata.py');tail=load('tail','tx-finish-tail.py');composition=load('composition','tx-finish-alias-composition.py')
class FinishTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.image=(ROOT/tail.entry.BIN).read_bytes()
  if hashlib.sha256(cls.image).hexdigest()!=tail.entry.SHA:raise RuntimeError('original BIN identity mismatch')
 def test_instruction_windows_and_each_mutation(self):
  for start,end,verify in ((0xb1a,0xb3a,metadata.window),(0xb3a,0xb52,tail.verify)):
   original=self.image[start:end];verify(original)
   for i in range(len(original)):
    mutated=bytearray(original);mutated[i]^=1
    with self.subTest(pc=hex(0x8000+start+i)),self.assertRaises(ValueError):verify(mutated)
 def test_wrap_and_width(self):
  self.assertEqual(metadata.events(0,0xffffffff,0xffffffff),((1,2,5),(3,2,0)))
  self.assertEqual(metadata.events(0,0xfffffffe,0xfffa),((0,2,0),(2,2,0)))
 def test_write_before_load_and_target_low_bit(self):
  mem={0x40050:0x77,0x40051:0x44,0x40052:0x33,0x40053:0x22}
  before=tail.project(mem,0,0,0,0)[0]
  composition.apply(mem,metadata.events(0,0x4004e,1))
  after=tail.project(mem,0,0,0,0)[0]
  self.assertEqual(before,0x22334476);self.assertEqual(after,6)
 def test_saved_ra_unchanged_by_tail_jump(self):
  mem={0x40050:1};self.assertEqual(tail.project(mem,0,0,0xffffffff,0x12345679)[3:5],(31,0x12345679))
if __name__=='__main__':unittest.main()
