#!/usr/bin/env python3
"""Negative controls for the bounded counter writer byte projection."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).with_name('counter-masked-writers.py')
spec=importlib.util.spec_from_file_location('counter_masked_writers',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CounterWriterTest(unittest.TestCase):
    def test_original_events_and_boundaries(self):
        for start,code in m.WINDOWS:
            for gp in (0,0x20004000,0xffffff50,0xffffffff):
                for v in range(256):
                    events=m.execute(code,gp,v,0x12345678)
                    self.assertEqual(events[0],('read',(gp+176)&m.MASK,1,v))
                    self.assertEqual(events[-1],('write',(gp+176)&m.MASK,1,(v+1)&3))
                    self.assertEqual(len(events),3 if start==0xa33a else 2)
    def test_mutation_must_reject_or_change_events(self):
        caught=0
        for _,code in m.WINDOWS:
            for i in range(len(code)):
                changed=bytearray(code);changed[i]^=1
                for value in (0,1,2,3,254,255):
                    try: got=m.execute(changed,0x20004000,value,0x12345678)
                    except (ValueError,IndexError):caught+=1;break
                    if got!=m.execute(code,0x20004000,value,0x12345678):caught+=1;break
                else:self.fail('mutation went undetected at byte '+str(i))
        self.assertEqual(caught,26)
    def test_unsupported_instructions_rejected(self):
        for code in (b'\x01\x00',b'\x13\x00\x00\x00'):
            with self.assertRaises(ValueError):m.execute(code,0,0,0)

if __name__=='__main__':unittest.main()
