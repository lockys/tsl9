#!/usr/bin/env python3
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('prefix',Path(__file__).with_name('counter-callee-prefix.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PrefixTest(unittest.TestCase):
    def test_every_window_byte_rejected_even_if_hash_recomputed(self):
        data=(m.ROOT/m.BIN).read_bytes()
        self.assertEqual(m.check(data),3)
        count=0
        original=m.SHA
        try:
            for start,hexbytes in m.WINDOWS:
                for offset in range(len(bytes.fromhex(hexbytes))):
                    bad=bytearray(data);bad[start-0x8000+offset]^=1
                    m.SHA=hashlib.sha256(bad).hexdigest()
                    with self.assertRaisesRegex(ValueError,'fixed instruction window'):m.check(bad)
                    count+=1
        finally:m.SHA=original
        self.assertEqual(count,86)
    def test_identity_rejects_truncation(self):
        with self.assertRaisesRegex(ValueError,'identity'):m.check(b'')
if __name__=='__main__':unittest.main()
