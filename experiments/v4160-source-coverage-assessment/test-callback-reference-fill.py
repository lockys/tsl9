#!/usr/bin/env python3
"""Regression tests for provider wrappers and bounded fill projection."""
import hashlib,importlib.util,os,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('TSL9_ROOT',HERE.parents[1]))
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
c=load('composition','callback-reference-fill-composition.py')
class Tests(unittest.TestCase):
 def test_instruction_mutations(self):
  image=(ROOT/c.m.BIN).read_bytes();c.m.validate(image)
  for module,offset in ((c.first,0x5272),(c.second,0x8032)):
   module.validate_local(image)
   for i in range(len(module.CODE)):
    with self.subTest(offset=offset,i=i):
     changed=bytearray(image);changed[offset+i]^=1
     with self.assertRaises(ValueError):module.validate_local(changed)
 def test_candidate_code_mutations_even_with_new_hash(self):
  found=0
  for name,path,digest,copy,fill in c.ref.CANDIDATES:
   p=ROOT/path
   if not p.exists():continue
   found+=1;original=p.read_bytes();c.ref.check(original,digest,copy,fill)
   for address in (0x40048,0x4004c,*range(copy,copy+len(c.ref.COPY)),*range(fill,fill+len(c.ref.FILL))):
    with self.subTest(candidate=name,address=address):
     changed=bytearray(original);changed[address-0x40000]^=1
     with self.assertRaises(ValueError):c.ref.check(changed,hashlib.sha256(changed).hexdigest(),copy,fill)
  if not found:self.fail('No reference carrier available')
 def test_fill_order_and_wrap(self):
  mem={};c.fill(mem,0xfffffffe,0x1aa,4)
  self.assertEqual(mem,{0xfffffffe:0xaa,0xffffffff:0xaa,0:0xaa,1:0xaa})
  c.fill(mem,0xffffffff,0,2)
  self.assertEqual(mem,{0xfffffffe:0xaa,0xffffffff:0,0:0,1:0xaa})
 def test_wrapper_indirect_slot_and_ra(self):
  self.assertEqual(c.first.execute(c.first.CODE,0x12345679,0xaabbccdd)[:5],(0x2000bf48,0,19,0x12345678,0xaabbccdd))
  self.assertEqual(c.second.execute(c.second.CODE,0xffffff00,0x98765433,0x11223344)[:5],(44,0,3,0x98765432,0x11223344))
if __name__=='__main__':unittest.main()
