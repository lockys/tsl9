#!/usr/bin/env python3
"""Negative controls for conditional TX/reference composition identity and windows."""
import importlib.util,hashlib,os,unittest
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('TX_TEST_ROOT', H.parents[1]))
s=importlib.util.spec_from_file_location('composition',H/'tx-reference-bound-composition.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=(ROOT/c.entry.BIN).read_bytes();p=ROOT/c.ledger.refmod.REF
        if not p.exists():raise RuntimeError('reference carrier unavailable')
        cls.ref=p.read_bytes()
        if hashlib.sha256(cls.app).hexdigest()!=c.entry.SHA or hashlib.sha256(cls.ref).hexdigest()!=c.ledger.refmod.SHA:raise RuntimeError('input identity mismatch')
    def test_app_window_mutations_rejected_after_rehash(self):
        b=self.app[0xa56:0xa74];c.entry.decode(b)
        for i in range(len(b)):
            changed=bytearray(b);changed[i]^=1
            with self.subTest(i=i),self.assertRaises(ValueError):c.entry.decode(changed)
    def test_ref_window_mutations_rejected_after_rehash(self):
        c.ledger.validate(self.ref)
        for pc,h in c.ledger.refmod.WINDOWS:
            for i in range(len(bytes.fromhex(h))):
                changed=bytearray(self.ref);changed[pc-0x40000+i]^=1
                with self.subTest(pc=pc,i=i),self.assertRaises(ValueError):c.ledger.validate(changed)
    def test_copy_window_mutations_and_identity(self):
        for pc,h in c.m.WINDOWS:
            b=bytes.fromhex(h);self.assertEqual(self.app[pc-0x8000:pc-0x8000+len(b)],b)
            for i in range(len(b)):
                x=bytearray(b);x[i]^=1;self.assertNotEqual(bytes(x),b)
        for image in (self.app,self.ref):
            altered=bytearray(image);altered[-1]^=1;self.assertNotEqual(hashlib.sha256(altered).digest(),hashlib.sha256(image).digest())
if __name__=='__main__':unittest.main()
