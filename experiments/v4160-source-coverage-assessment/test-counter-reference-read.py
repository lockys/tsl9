#!/usr/bin/env python3
"""Boundary and sensitivity checks for the conditional CCC reference projection."""
import importlib.util,unittest
from pathlib import Path
p=Path(__file__).with_name('counter-reference-read-ccc.py')
s=importlib.util.spec_from_file_location('reference_read',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReadProjection(unittest.TestCase):
    def test_first_duplicate_all_values(self):
        for x in range(256):
            for y in range(256):
                result,reads=m.project(3,[(3,x),(3,y)],2)
                self.assertEqual(result,x)
                self.assertEqual(reads,[('halfword',0x20004080),('byte',0x20004082)])
    def test_capacity_and_width(self):
        records=[(0xffff,1),(0xfffe,2)]
        self.assertEqual(m.project(0xffff,records,0),(0,[]))
        self.assertEqual(m.project(0x1ffff,records,2)[0],0)
        self.assertEqual(m.project(0xfffe,records,1)[0],0)
        self.assertEqual(m.project(0xfffe,records,2)[0],2)
    def test_stability_assumption_is_necessary(self):
        self.assertEqual(m.project(3,[(3,0)],1)[0],0)
        self.assertEqual(m.project(3,[(3,1)],1)[0],1)
    def test_null_and_modular_address(self):
        self.assertEqual(m.project(3,[(3,9)],1,0),(0,[('halfword',0)]))
        self.assertEqual(m.project(3,[(4,9),(3,7)],2,0xfffffffc),(0,[('halfword',0xfffffffc),('halfword',0)]))
if __name__=='__main__':unittest.main()
