"""Concrete causal alias and sequencing witnesses, separate from compiled C tests."""
import struct
import unittest

from oracle import BASE, Slice
from verify import ROOT, fixture, SIZE


class FinishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        image = (ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
        cls.oracle = Slice(image)
        cls.patterns = [bytes((i*37+seed*19)&255 for i in range(SIZE)) for seed in range(8)]

    def example(self, **changes):
        case = dict(base=100,bank=0,n=0,delta=0,stack='separate',selector='normal_GP',command=4)
        case.update(changes)
        regions, registers = fixture(case,self.patterns,0)
        memory, output, trace = self.oracle.run(regions,registers)
        return regions, registers, memory, output, trace

    @staticmethod
    def word(regions, address):
        for base,data in regions:
            if base <= address and address+4 <= base+len(data):
                return int.from_bytes(data[address-base:address-base+4],'little')
        raise ValueError('test word not mapped')

    def test_exact_finish_order(self):
        _,r,_,out,trace = self.example(n=3)
        suffix = [struct.unpack_from('<4I',trace,len(trace)-160+16*i) for i in range(10)]
        self.assertEqual([(a,c) for a,_,c,_ in suffix],
                         [(2,1),(1,4),(1,4),(1,4),(1,4),(2,2),(2,2),(1,4),(1,4),(1,1)])
        self.assertEqual(suffix[1][1],r[2]+28)
        self.assertEqual(suffix[8][1],0x40050)
        self.assertEqual(out[2],r[2]+32)

    def test_checksum_changes_saved_RA(self):
        before,r,_,out,_ = self.example(n=1,stack='checksum_RA')
        old = self.word(before,r[2]+28)
        self.assertEqual(out[1],(old&0xffffff00)|out[14])
        self.assertNotEqual(out[1],old)

    def test_RA_restored_before_metadata_clear(self):
        _,r,memory,out,_ = self.example(stack='metadata_S0')
        self.assertEqual(out[1]>>16,0x7f55)
        self.assertNotEqual(out[1],self.word(memory,r[2]+28))
        self.assertEqual(self.word(memory,r[2]+28)&65535,0)

    def test_S0_loaded_after_metadata(self):
        _,_,_,out,_ = self.example(n=31,stack='metadata_S0')
        self.assertEqual(out[8]>>16,37)

    def test_metadata_and_tail_selector_aliases(self):
        for bank in (0,1):
            self.assertEqual(self.example(bank=bank,selector='metadata')[3][10],6)
            out = self.example(bank=bank,selector='tail',stack='tail_S0')[3]
            self.assertEqual(out[10],out[6]&255)
            self.assertEqual(out[8],out[6])

    def test_metadata_wrap(self):
        for n,expected in ((65529,65535),(65530,0),(65535,5)):
            _,_,_,_,trace = self.example(n=n,delta=None)
            self.assertEqual(struct.unpack_from('<4I',trace,len(trace)-80),(2,BASE+2,2,expected))

    def test_invalid_domains_and_mapping(self):
        case=dict(base=100,bank=0,n=1,delta=0,stack='separate',selector='normal_GP',command=4)
        regions,r=fixture(case,self.patterns,0)
        for index,value in ((12,2),(8,65536),(0,1),(9,0xfffffff0)):
            bad=r[:];bad[index]=value
            with self.assertRaises(ValueError):self.oracle.run(regions,bad)
        with self.assertRaises(ValueError):self.oracle.run([regions[0],regions[0]],r)

    def test_budget(self):
        case=dict(base=100,bank=0,n=1,delta=0,stack='separate',selector='normal_GP',command=4)
        regions,r=fixture(case,self.patterns,0)
        with self.assertRaisesRegex(ValueError,'budget'):self.oracle.run(regions,r,budget=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
