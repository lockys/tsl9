"""Causal counter-source examples from explicit post-copy snapshots."""
import struct,unittest
from oracle import Counter
from verify import IMAGE,IMAGE_SHA,sha,fixture
from audit import derive
def events(trace):return [struct.unpack_from('<4I',trace,j) for j in range(0,len(trace),16)]
def read(regions,a,w):
    for base,data in regions:
        if 0<=a-base and a-base+w<=len(data):return int.from_bytes(data[a-base:a-base+w],'little')
    raise ValueError('test read unmapped')
def case(**kw):
    c=dict(cached=1,current=1,flag=0,field=2050,mode=0,index=0);c.update(kw);return c
class CounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sha(IMAGE)!=IMAGE_SHA:raise ValueError('original identity')
        cls.image=IMAGE.read_bytes();cls.engine=Counter(cls.image)
    def run_case(self,c):
        regions,r=fixture(c,self.image);return r,self.engine.run(regions,r)
    def test_nonzero_unchanged_status_reaches_lookup_without_counter_write(self):
        for index,value in enumerate((2200,2230,1900,1870)):
            _,(m,r,trace,pc,calls,window)=self.run_case(case(index=index))
            self.assertEqual((pc,calls,window,r[15]),(0xa168,2,0,value))
            self.assertEqual(read(m,0x200040b0,1),index)
            self.assertFalse(any(e[0]==2 for e in events(trace)))
            self.assertEqual([(e[1],e[2]) for e in events(trace) if e[0]==3],[(0x81f8,0xa0e6),(0x81ee,0xa136)])
    def test_zero_unchanged_status_needs_nonzero_flag(self):
        for flag,pc in ((0,0xa1e8),(1,0xa168),(255,0xa168)):
            _,(_,_,_,actual,_,window)=self.run_case(case(cached=0,current=0,flag=flag))
            self.assertEqual((actual,window),(pc,0))
    def test_changed_nonzero_status_stops_before_registration_call(self):
        _,(m,r,trace,pc,calls,window)=self.run_case(case(cached=1,current=255,index=3))
        self.assertEqual((pc,calls,window),(0xa110,1,0))
        self.assertEqual([r[k] for k in (1,10,11,12,13)],[0xa0e6,0xa2ea,1,2000,0])
        self.assertEqual((read(m,0x200040aa,1),read(m,0x200040b0,1)),(255,0))
        self.assertFalse(any(e[0]==1 and 0x1ab48<=e[1]<0x1ab50 for e in events(trace)))
    def test_changed_zero_status_stops_before_cancellation_call(self):
        initial,(m,r,_,pc,calls,_)=self.run_case(case(cached=255,current=0,index=255))
        self.assertEqual((pc,calls,r[1],r[10]),(0xa1de,1,0xa0e6,0xa2ea))
        self.assertEqual([r[k] for k in (11,12,13)],[initial[k] for k in (11,12,13)])
        self.assertEqual(read(m,0x200040b0,1),0)
    def test_fixed_modes_do_not_read_the_counter_or_table(self):
        for mode,value in ((1,1960),(2,2140)):
            _,(_,r,trace,pc,_,window)=self.run_case(case(mode=mode,index=255))
            self.assertEqual((pc,window,r[15]),(0xa168,0,value))
            self.assertFalse(any(e[0]==1 and (e[1]==0x200040b0 or 0x1ab48<=e[1]<0x1ab50) for e in events(trace)))
    def test_outside_window_is_an_analysis_stop_before_read(self):
        for index in (4,91,92,255):
            _,(_,r,trace,pc,calls,window)=self.run_case(case(index=index))
            self.assertEqual((pc,calls,window,r[15]),(0xa158,2,1,0x1ab48+2*index))
            self.assertFalse(any(e[0]==1 and 0x1ab48<=e[1]<0x1ad48 for e in events(trace)))
    def test_geometry_edges_precede_mode_getter(self):
        for field in (1960,2140):
            _,(_,_,trace,pc,calls,_)=self.run_case(case(field=field))
            self.assertEqual((pc,calls),(0xa1e8,1))
            self.assertFalse(any(e[0]==1 and e[1]==0x2000bed5 for e in events(trace)))
        for field in (1961,2139):
            _,(_,_,_,pc,calls,_)=self.run_case(case(field=field))
            self.assertEqual((pc,calls),(0xa168,2))
    def test_all_old_bytes_produce_masked_state_before_unknown_call(self):
        for index in range(256):
            _,(m,_,_,pc,_,_)=self.run_case(case(cached=0,current=1,index=index))
            self.assertEqual((pc,read(m,0x200040b0,1)),(0xa110,(index+1)&3))
    def test_origin_and_address_envelopes_are_conditional(self):
        d=derive(self.image)
        self.assertEqual(d['masked_result_histogram'],[64]*4)
        self.assertEqual((d['envelope_bytes'],d['envelope_bytes_beyond_APP']),(512,328))
        self.assertEqual(d['accepted_geometry_fields'],[1961,2139])
        self.assertFalse(d['global_index_invariant_proved'])
    def test_budget_is_not_a_successful_return(self):
        regions,r=fixture(case(),self.image)
        with self.assertRaises(ValueError):self.engine.run(regions,r,budget=1)
if __name__=='__main__':unittest.main()
