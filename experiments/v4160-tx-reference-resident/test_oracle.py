"""Causal reference-backed provider/tail examples under synthetic memory."""
import struct,unittest
from oracle import Whole
from verify import fixture,load_inputs
from profiles import PROFILES
from layout import derive
B=0x2000b18c
def read(regions,a,w):
    for base,data in regions:
        if 0<=a-base and a-base+w<=len(data):return int.from_bytes(data[a-base:a-base+w],'little')
    raise ValueError('unmapped test read')
def events(trace):return [struct.unpack_from('<4I',trace,j) for j in range(0,len(trace),16)]
class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.residents=load_inputs()
    def run_case(self,**changes):
        c=dict(n=4,lane='first',table='one',task=0,tasks=1,name='matrix');c.update(changes)
        for label,rom in self.residents.items():
            cfg=PROFILES[label]['cfg'];regions,r=fixture(c,rom,cfg);engine=Whole(self.image,rom,cfg)
            yield label,cfg,regions,r,engine,engine.run(regions,r)
    def test_real_query_and_event_post(self):
        for _,cfg,_,initial,_,(m,r,trace,pc,calls) in self.run_case():
            self.assertEqual((pc,calls,r[10]),(cfg[3]+54,1,0))
            self.assertEqual(read(m,0x20006000,2),0xa5a5)
            self.assertEqual(read(m,0x4002420c,4),0x12345678)
            self.assertEqual((r[1],r[2]),(initial[1],initial[2]))
            self.assertEqual(read(m,B+2,2),10)
            self.assertEqual(len([e for e in events(trace) if e[0]==8]),1)
    def test_second_lane_uses_same_query_function(self):
        for _,cfg,_,_,_,(m,_,trace,pc,calls) in self.run_case(lane='second',task=1,tasks=3):
            self.assertEqual((pc,calls),(cfg[3]+54,1))
            self.assertEqual(read(m,B+1062+2,2),10)
            self.assertIn((3,cfg[0],0x8ab6,0),events(trace))
    def test_first_duplicate_wins(self):
        for _,cfg,_,_,_,(_,r,_,pc,_) in self.run_case(table='duplicate'):
            self.assertEqual((pc,r[10]),(cfg[3]+54,0))
    def test_non_one_byte_status_is_not_bit_zero_test(self):
        for _,_,_,_,_,(_,r,trace,pc,calls) in self.run_case(lane='both',table='ff'):
            self.assertEqual((pc,calls,r[10]),(0x8aca,2,255))
            self.assertFalse(any(e[0]==8 for e in events(trace)))
    def test_missing_and_empty_query_cannot_reach_event_post(self):
        for table in ('empty','missing'):
            for _,_,_,_,_,(_,r,_,pc,calls) in self.run_case(lane='both',table=table):
                self.assertEqual((pc,calls,r[10]),(0x8aca,2,0))
    def test_event_id_equal_count_rejects_after_packet_writes(self):
        for _,cfg,_,_,_,(m,r,_,pc,_) in self.run_case(task=1,tasks=1):
            self.assertEqual((pc,r[10]),(cfg[3]+62,3))
            self.assertEqual(read(m,0x20006002,2),0xa5a4)
            self.assertEqual(read(m,B+2,2),10)
    def test_setting_event_bit_twice_does_not_count(self):
        for _,_,_,initial,engine,(m,_,_,_,_) in self.run_case():
            again=engine.run(m,initial)[0]
            self.assertEqual((read(m,0x20006000,2),read(again,0x20006000,2)),(0xa5a5,0xa5a5))
    def test_control_alias_write_is_overwritten_by_restore(self):
        for _,cfg,_,_,_,(m,r,trace,pc,_) in self.run_case(name='event_control_alias'):
            self.assertEqual((pc,r[10],read(m,0x4002420c,4)),(cfg[3]+54,0,0x12345678))
            accesses=[e for e in events(trace) if e[0] in (1,2) and e[1]==0x4002420c]
            self.assertEqual(accesses,[(1,0x4002420c,4,0x12345678),(2,0x4002420c,4,0),
                (1,0x4002420c,2,0),(2,0x4002420c,2,1),(2,0x4002420c,4,0x12345678)])
    def test_late_slot_write_does_not_change_already_loaded_target(self):
        for _,cfg,_,_,_,(m,r,trace,pc,_) in self.run_case(name='event_tail_slot_alias'):
            self.assertEqual((pc,r[6]),(cfg[3]+54,cfg[3]))
            self.assertEqual(read(m,0x40050,4),cfg[3]|1)
            self.assertIn((8,cfg[3],r[1],0),events(trace))
    def test_capacity_255_and_forward_alias(self):
        for _,cfg,_,_,_,(_,_,trace,pc,_) in self.run_case(name='max_count'):
            self.assertEqual(pc,cfg[3]+54)
            self.assertIn((1,0x20004080+254*4,2,0x1234),events(trace))
        for _,_,_,_,_,(m,_,_,_,_) in self.run_case(name='forward_alias'):
            self.assertEqual([read(m,B+11+i,1) for i in range(4)],[4]*4)
    def test_original_reset_and_setup_nominal_range(self):
        d=derive(self.image)
        self.assertEqual((d['nominal_TX_bytes'],d['nominal_TX_end_exclusive']),(2124,'0x2000b9d8'))
        self.assertTrue(d['reset_covers_every_TX_byte'])
        self.assertFalse(d['exclusive_RAM_ownership_proved'])
    def test_budget_fails_closed(self):
        for _,_,regions,r,engine,_ in self.run_case():
            with self.assertRaises(ValueError):engine.run(regions,r,budget=1)
if __name__=='__main__':unittest.main()
