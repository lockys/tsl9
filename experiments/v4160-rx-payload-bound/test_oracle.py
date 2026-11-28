"""Causal local RX payload-path tests; no callback, clock or router runs."""
import struct,unittest
from oracle import Payload
from verify import IMAGE,IMAGE_SHA,sha,fixture,RX
from layout import derive
def read(regions,a,w):
    base,data=regions[0];i=a-base
    return int.from_bytes(data[i:i+w],'little')
def events(trace):return [struct.unpack_from('<4I',trace,j) for j in range(0,len(trace),16)]
def case(**kwargs):
    c=dict(field='normal',count=0,length=2,byte=7,old_sum=255,source='GP_sum');c.update(kwargs);return c
class PayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sha(IMAGE)!=IMAGE_SHA:raise ValueError('original identity')
        cls.image=IMAGE.read_bytes();cls.engine=Payload(cls.image)
    def run_case(self,c):
        regions,r=fixture(c);return regions,r,self.engine.run(regions,r)
    def test_rejected_count_only_reads_count_and_clears_state(self):
        for count in (1040,65535):
            _,initial,(m,r,trace,pc)=self.run_case(case(count=count))
            gp=r[3];self.assertEqual(pc,0x897e)
            self.assertEqual(events(trace),[(1,gp+138,2,count),(2,gp+156,1,0)])
            expected=list(initial);expected[12]=count;expected[14]=1039
            self.assertEqual(r,expected);self.assertEqual(read(m,gp+138,2),count)
    def test_last_payload_byte_and_full_checksum_register(self):
        _,_,(m,r,_,_)=self.run_case(case(count=1039,length=1040,byte=255))
        self.assertEqual((read(m,RX+1039,1),read(m,r[3]+138,2),read(m,r[3]+156,1)),(255,1040,6))
        self.assertEqual((r[15],read(m,r[3]+165,1)),(510,254))
    def test_destination_uses_old_counter(self):
        initial,_,(m,_,_,_)=self.run_case(case(count=2,byte=255))
        self.assertEqual(read(m,RX+2,1),255)
        self.assertEqual(read(m,RX+3,1),read(initial,RX+3,1))
    def test_length_is_loaded_after_payload_store(self):
        _,_,(m,r,trace,_)=self.run_case(case(field='length',length=0,byte=255,old_sum=0))
        gp=r[3];self.assertEqual((read(m,gp+142,2),read(m,gp+156,1)),(255,5))
        es=events(trace);self.assertLess(es.index((2,RX,1,255)),es.index((1,RX,2,255)))
    def test_payload_overwrites_saved_new_counter(self):
        _,_,(m,r,_,_)=self.run_case(case(field='count',byte=255,source='count'))
        self.assertEqual((r[12],read(m,RX,2),r[15]),(0,255,510))
    def test_checksum_reads_the_fresh_payload(self):
        _,_,(m,r,_,_)=self.run_case(case(byte=127,source='payload',old_sum=0))
        self.assertEqual((r[15],read(m,r[3]+165,1)),(254,254))
    def test_checksum_can_read_new_state_six(self):
        _,_,(m,r,_,_)=self.run_case(case(length=0,byte=7,source='state'))
        self.assertEqual((r[14],r[15],read(m,r[3]+165,1)),(6,13,13))
    def test_state_transition_is_greater_or_equal(self):
        for length,state in ((0,6),(1,6),(2,5)):
            _,_,(m,r,_,_)=self.run_case(case(count=0,length=length))
            self.assertEqual(read(m,r[3]+156,1),state)
    def test_checksum_write_can_replace_aliased_payload(self):
        _,_,(m,r,_,_)=self.run_case(case(field='sum',count=1,byte=255))
        self.assertEqual((r[15],read(m,RX+1,1)),(510,254))
    def test_exhaustive_counter_image_and_nominal_adjacency(self):
        d=derive(self.image)
        self.assertEqual((d['counter_values_checked'],d['payload_write_counter_values'],d['over_limit_counter_values']),(65536,1040,64496))
        self.assertEqual((d['nominal_TX_end_exclusive'],d['nominal_RX_start'],d['nominal_RX_end_exclusive']),('0x2000b9d8','0x2000b9d8','0x2000bde8'))
        self.assertTrue(d['normal_GP_slice_writes_disjoint_from_TX'])
    def test_invalid_byte_and_budget_fail_before_success(self):
        regions,r=fixture(case());r[15]=256
        with self.assertRaises(ValueError):self.engine.run(regions,r)
        r[15]=1
        with self.assertRaises(ValueError):self.engine.run(regions,r,budget=1)
if __name__=='__main__':unittest.main()
