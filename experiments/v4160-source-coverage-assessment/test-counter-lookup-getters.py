#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
p=Path(__file__).with_name('counter-lookup-getters.py')
s=importlib.util.spec_from_file_location('getters',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GetterTests(unittest.TestCase):
    def test_addresses(self):
        for pc,h,expected in m.WINDOWS:
            self.assertEqual(m.getter_address(pc,bytes.fromhex(h)),expected)
    def test_operand_and_return_mutations_rejected(self):
        pc,h,_=m.WINDOWS[0];raw=bytes.fromhex(h)
        for offset,bit in ((0,1),(0,0x80),(4,1),(4,0x80),(5,0x10),(6,0x01),(8,1),(9,1)):
            changed=bytearray(raw);changed[offset]^=bit
            with self.subTest(offset=offset,bit=bit):
                with self.assertRaises(ValueError):m.getter_address(pc,changed)
    def test_immediate_mutation_changes_address(self):
        pc,h,expected=m.WINDOWS[0];raw=bytearray.fromhex(h);raw[7]^=0x10
        self.assertNotEqual(m.getter_address(pc,raw),expected)
if __name__=='__main__':unittest.main()
