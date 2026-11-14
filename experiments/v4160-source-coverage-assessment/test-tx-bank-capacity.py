#!/usr/bin/env python3
"""Negative tests for the conditional TX bank bound's actual verification path."""
import contextlib,hashlib,importlib.util,io,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('bound',HERE/'tx-bank-capacity-bound.py');bound=importlib.util.module_from_spec(spec);spec.loader.exec_module(bound)
class BankBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=(ROOT/bound.entry.BIN).read_bytes()
        if hashlib.sha256(cls.original).hexdigest()!=bound.entry.SHA:raise RuntimeError('original BIN identity mismatch')
    def invoke(self,data,rehash):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/bound.entry.BIN;target.parent.mkdir(parents=True);target.write_bytes(data)
            digest=hashlib.sha256(data).hexdigest() if rehash else bound.entry.SHA
            with patch.object(bound.entry,'SHA',digest),patch.object(sys,'argv',['bound','--root',d]),contextlib.redirect_stdout(io.StringIO()):bound.main()
    def test_windows_reject_even_when_identity_is_rehashed(self):
        for offset in list(range(0xace,0xb0a))+list(range(0xb14,0xb1a)):
            with self.subTest(offset=hex(offset)):
                b=bytearray(self.original);b[offset]^=1
                with self.assertRaises(ValueError):self.invoke(b,True)
    def test_identity_rejects_other_mutation(self):
        b=bytearray(self.original);b[0]^=1
        with self.assertRaisesRegex(ValueError,'image identity'):self.invoke(b,False)
    def test_original_passes(self):self.invoke(self.original,False)
if __name__=='__main__':unittest.main()
