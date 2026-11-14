#!/usr/bin/env python3
"""Boundary and mutation checks for original callback b0d0."""
import importlib.util,os,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('TSL9_ROOT',HERE.parents[1]))
s=importlib.util.spec_from_file_location('cb',HERE/'callback-b0d0-decoder.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Tests(unittest.TestCase):
 def test_full_width_flag_and_return(self):
  for flag in (0,1,2,3,0x100,0x101,0xfffffffe,0xffffffff):
   with self.subTest(flag=flag):
    ret,mem,events=c.execute(0x20004000,flag,[0,2,3])
    self.assertEqual(ret,(flag^1) if flag&1 else 0)
    self.assertEqual([mem[0x200040c1+i] for i in range(3)],[1,3,3] if flag&1 else [0,2,3])
    if not flag&1:self.assertEqual(events,[])
 def test_reads_and_conditional_writes_in_order(self):
  ret,mem,events=c.execute(0x20004000,1,[0,3,2])
  self.assertEqual(ret,0)
  self.assertEqual(events,[('read8',0x200040c1,0),('write8',0x200040c1,1),('read8',0x200040c2,3),('read8',0x200040c3,2),('write8',0x200040c3,3)])
 def test_address_wrap(self):
  _,mem,events=c.execute(0xffffff3e,1,[1,2,255])
  self.assertEqual(mem,{0xffffffff:2,0:3,1:255})
  self.assertEqual([x[1] for x in events],[0xffffffff,0xffffffff,0,0,1])
 def test_every_local_byte_mutation(self):
  image=(ROOT/c.m.BIN).read_bytes();c.m.validate(image);c.validate_local(image)
  for i in range(len(c.CODE)):
   with self.subTest(index=i):
    changed=bytearray(image);changed[0x30d0+i]^=1
    with self.assertRaises(ValueError):c.validate_local(changed)
if __name__=='__main__':unittest.main()
