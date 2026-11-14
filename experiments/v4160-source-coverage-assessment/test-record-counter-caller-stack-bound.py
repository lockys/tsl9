#!/usr/bin/env python3
"""Negative and exact boundary checks for caller/stack alias evidence."""
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('bound',HERE/'record-counter-caller-stack-bound.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b);m=b.m
class BoundTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.image=(ROOT/m.BIN).read_bytes();b.entry.validate(cls.image);b.validate_windows(cls.image)
 def test_all_window_bytes_after_rehash(self):
  original=m.SHA
  try:
   mutations=0
   for pc,window in b.WINDOWS:
    for i in range(len(window)):
     data=bytearray(self.image);data[pc-0x8000+i]^=1
     m.SHA=hashlib.sha256(data).hexdigest()
     # Entry identity validator succeeds after rehash; only the relevant
     # reset/caller window check is expected to reject this mutation.
     b.entry.validate(data)
     with self.assertRaisesRegex(ValueError,'window'):b.validate_windows(data)
     mutations+=1
   self.assertEqual(mutations,36)
  finally:m.SHA=original
 def test_full_counter_byte_overlap_and_adjacent_sp(self):
  counter=0x20004142;sp0=counter+17
  for sp in range(sp0-1,sp0+5):
   mem={counter:0x7a};b.entry.enter(sp,1,2,3,counter,0x44332211,1,5,6,mem)
   if sp0<=sp<=sp0+3:self.assertNotEqual(mem[counter],0x7a)
   else:self.assertEqual(mem[counter],0x7a)
 def test_aligned_witness_and_smaller_depths(self):
  reset=0x20010000;counter=0x20004142;witness=0x20004154;nearest=reset-witness
  self.assertEqual(nearest,48812)
  for depth in range(0,nearest,4):self.assertFalse(counter in range(reset-depth-20,reset-depth-16))
  self.assertIn(counter,range(witness-20,witness-16))
if __name__=='__main__':unittest.main()
