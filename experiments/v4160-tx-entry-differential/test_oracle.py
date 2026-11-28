"""Causal entry/opaque-return examples; no resident code is executed."""
import struct,unittest
from oracle import Entry
from verify import IMAGE,IMAGE_SHA,sha,fixture,action

class EntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sha(IMAGE)!=IMAGE_SHA:raise ValueError('original identity')
        cls.engine=Entry(IMAGE.read_bytes())
    def run_case(self,c):return self.engine.run(c['regions'],c['registers'],c['actions'])
    def test_unsigned_guard_changes_only_a5(self):
        for n in (1040,65536,0xffffffff):
            c=fixture(n=n);mem,r,trace,pc,calls=self.run_case(c)
            expected=list(c['registers']);expected[15]=1039
            self.assertEqual((r,trace,pc,calls),(expected,b'',0x8b6c,0))
            self.assertEqual([(a,bytes(b)) for a,b in mem],c['regions'])
    def test_handle_is_compared_at_full_width_and_sentinel_rejected(self):
        for h in (0xfffe,0x10001,0x12341234):
            c=fixture(handle=h);_,_,_,pc,calls=self.run_case(c)
            self.assertEqual((pc,calls),(0x8aca,0))
    def test_only_exact_one_accepts(self):
        for v in (0,2,0xffffffff,0x10001):
            c=fixture(actions=[action(v),action(v)]);_,r,_,pc,calls=self.run_case(c)
            self.assertEqual((pc,calls,r[10]),(0x8aca,2,v))
            self.assertEqual(r[12],1) # second lane sets a2 before testing result
    def test_second_call_receives_live_inputs_and_link(self):
        c=fixture(actions=[action(0,{3:0x20004100,18:0x789a,12:0xcafebabe,13:0xfacefeed}),action(1)])
        _,_,trace,pc,calls=self.run_case(c)
        events=[struct.unpack_from('<4I',trace,i) for i in range(0,len(trace),16)]
        positions=[i for i,e in enumerate(events) if e[0]==3];self.assertEqual(len(positions),2)
        j=positions[1];snapshot=[e[3] for e in events[j+1:j+33]]
        self.assertEqual(events[j],(3,0x12345678,0x8ab6,1))
        self.assertEqual([snapshot[k] for k in (1,10,11,12,13)],
                         [0x8ab6,0x789a,0x20004180,0xcafebabe,0xfacefeed])
        self.assertEqual((pc,calls),(0x8ace,2))
    def test_provider_slot_is_loaded_again_and_jalr_masks_bit_zero(self):
        c=fixture(actions=[action(0,writes=[(0x4013c,4,0x2468ace1)]),action(1,target=0x2468ace0)])
        _,_,trace,_,_=self.run_case(c)
        events=[struct.unpack_from('<4I',trace,i) for i in range(0,len(trace),16)]
        self.assertEqual([e[1] for e in events if e[0]==3],[0x12345678,0x2468ace0])
        self.assertEqual([e[3] for e in events if e[:3]==(1,0x4013c,4)],[0x12345679,0x2468ace1])
    def test_post_provider_length_is_not_checked_again(self):
        c=fixture(actions=[action(1,{8:0xffffffff})]);_,r,_,pc,calls=self.run_case(c)
        self.assertEqual((pc,calls,r[8],r[12]),(0x8ace,1,0xffffffff,0))
    def test_rejection_restores_from_live_sp(self):
        c=fixture(actions=[action(0,{2:0x2000d040},[(0x2000d05c,4,0x87654321)]),action(0)])
        _,r,_,pc,_=self.run_case(c)
        self.assertEqual((pc,r[1],r[2]),(0x8aca,0x87654321,0x2000d060))
    def test_first_success_does_not_execute_unused_second_action(self):
        c=fixture(actions=[action(1),action(0,writes=[(0x4013c,4,0)])])
        _,r,trace,pc,calls=self.run_case(c)
        self.assertEqual((pc,calls,r[12]),(0x8ace,1,0))
        events=[struct.unpack_from('<4I',trace,i) for i in range(0,len(trace),16)]
        self.assertNotIn((2,0x4013c,4,0),events)
    def test_missing_or_invalid_actions_and_budget_fail_closed(self):
        c=fixture(actions=[])
        with self.assertRaises(ValueError):self.run_case(c)
        c=fixture(actions=[action(1,{10:2})])
        with self.assertRaises(ValueError):self.run_case(c)
        c=fixture()
        with self.assertRaises(ValueError):self.engine.run(c['regions'],c['registers'],c['actions'],budget=1)

if __name__=='__main__':unittest.main()
