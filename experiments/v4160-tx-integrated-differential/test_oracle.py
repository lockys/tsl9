"""Causal composition checks on one continuous original instruction run."""
import struct,unittest
from oracle import Whole
from verify import IMAGE,IMAGE_SHA,sha,fixture,action,materialize,corpus
B=0x2000b18c
def events(trace):return [struct.unpack_from('<4I',trace,i) for i in range(0,len(trace),16)]
def read(regions,address,width):
    for base,data in regions:
        if 0<=address-base and address-base+width<=len(data):
            return int.from_bytes(data[address-base:address-base+width],'little')
    raise ValueError('unmapped test read')
class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sha(IMAGE)!=IMAGE_SHA:raise ValueError('original identity')
        cls.engine=Whole(IMAGE.read_bytes())
    def run_case(self,c):return self.engine.run(materialize(c),c['registers'],c['actions'])
    def test_provider_writes_and_live_registers_survive_composition(self):
        c=next(c for c in corpus() if c['name']=='composed_live_state')
        mem,r,trace,pc,calls,domain=self.run_case(c)
        self.assertEqual((pc,calls,domain),(0x8b50,1,0))
        self.assertEqual([r[k] for k in (1,2,3,6,10,14)],
                         [0xdeadbeef,0x2000d060,0x20004100,0x87654321,0x5a,0x87])
        self.assertEqual(read(mem,B+11,1),0xaa)
        self.assertEqual(read(mem,B+2,2),9)
        self.assertEqual(read(mem,0x2000d01c,4),c['registers'][1])
        es=events(trace);j=next(i for i,e in enumerate(es) if e[0]==5)
        seam=[e[3] for e in es[j+1:j+33]]
        self.assertEqual([seam[k] for k in (2,3,8,9,19)],[0x2000d040,0x20004100,3,0x20020000,0x55])
    def test_first_provider_write_is_copied_after_second_accepts(self):
        c=fixture(actions=[action(0,{8:1,9:0x20020000,12:0xcafe,13:0xbeef},[(0x20020000,1,0xee)]),action(1)])
        mem,_,trace,pc,calls,domain=self.run_case(c)
        self.assertEqual((pc,calls,domain),(0x8b50,2,0))
        self.assertEqual(read(mem,B+1062+11,1),0xee)
        es=events(trace);j=[i for i,e in enumerate(es) if e[0]==3][1]
        self.assertEqual([e[3] for e in es[j+1:j+33]][12:14],[0xcafe,0xbeef])
    def test_forward_copy_observes_its_previous_write(self):
        c=fixture(n=4,actions=[action(1)]);c['registers'][12]=B+10
        mem,_,_,pc,_,domain=self.run_case(c)
        self.assertEqual((pc,domain),(0x8b50,0))
        self.assertEqual([read(mem,B+11+i,1) for i in range(4)],[4]*4)
        self.assertEqual(read(mem,B+15,1),0xbb)
    def test_checksum_alias_ra_and_metadata_alias_s0(self):
        sp=(B+8)-28
        c=fixture(n=0,actions=[action(1,{2:sp})]);_,r,trace,_,_,_=self.run_case(c)
        self.assertEqual((r[1],r[8]),(0xa70000a7,0x7f550000))
        es=events(trace)
        checksum=es.index((2,B+11,1,0xa7));ra=es.index((1,B+8,4,r[1]));zero=es.index((2,B+4,2,0));s0=es.index((1,B+4,4,r[8]))
        self.assertLess(checksum,ra);self.assertLess(ra,zero);self.assertLess(zero,s0)
    def test_ra_read_precedes_later_metadata_clear(self):
        c=fixture(n=0,actions=[action(1,{2:B-24})]);initial=materialize(c)
        mem,r,_,_,_,_=self.engine.run(initial,c['registers'],c['actions'])
        self.assertEqual(r[1],0x7f550000|read(initial,B+4,2))
        self.assertEqual(read(mem,B+4,4),0x7f550000)
        self.assertNotEqual(r[1],read(mem,B+4,4))
    def test_tail_word_is_raw_and_shared_by_s0_and_selector(self):
        c=fixture(actions=[action(1,{8:0,2:0x40038,3:0x40050-148},[(0x40050,4,0x13579bdf)])])
        _,r,_,pc,_,_=self.run_case(c)
        self.assertEqual((pc,r[8],r[6],r[10]),(0x8b50,0x13579bdf,0x13579bdf,0xdf))
    def test_metadata_wrap_after_a_real_entry_and_scripted_return(self):
        for n,value in ((65529,65535),(65530,0),(65535,5)):
            c=fixture(actions=[action(1,{8:n,9:0x20020000})]);mem,_,_,pc,_,domain=self.run_case(c)
            self.assertEqual((pc,domain,read(mem,B+2,2)),(0x8b50,0,value))
    def test_outside_domain_stops_before_bank_preparation(self):
        c=fixture(actions=[action(1,{8:65536})]);_,r,trace,pc,calls,domain=self.run_case(c)
        self.assertEqual((pc,calls,domain,r[8]),(0x8ace,1,6,65536))
        self.assertEqual(len([e for e in events(trace) if e[0]==2]),5)
        self.assertEqual(len([e for e in events(trace) if e[0]==5]),1)
    def test_rejection_has_no_composition_checkpoint(self):
        for c in (fixture(n=1040),fixture(handle=0xfffe)):
            _,_,trace,pc,calls,domain=self.run_case(c)
            self.assertIn(pc,(0x8aca,0x8b6c));self.assertEqual((calls,domain),(0,0))
            self.assertFalse(any(e[0]==5 for e in events(trace)))
    def test_budget_and_missing_actions_fail(self):
        c=fixture(actions=[])
        with self.assertRaises(ValueError):self.run_case(c)
        c=fixture()
        with self.assertRaises(ValueError):self.engine.run(materialize(c),c['registers'],c['actions'],budget=1)

if __name__=='__main__':unittest.main()
