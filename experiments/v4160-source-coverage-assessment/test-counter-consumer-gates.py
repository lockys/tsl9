#!/usr/bin/env python3
"""Negative controls for the consumer-gate evidence, including rehashed images."""
import contextlib, hashlib, importlib.util, io, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('consumer',HERE/'counter-consumer-gates.py');consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)
ROOT=Path(__file__).resolve().parents[2]
class ConsumerEvidence(unittest.TestCase):
    def test_instruction_and_table_mutations(self):
        original=(ROOT/consumer.BIN).read_bytes(); original_hash=consumer.SHA; oldargv=sys.argv[:]
        offsets=list(range(0x12cae,0x12cbe))+list(range(0x12d78,0x12d90))+list(range(0x81aa,0x81b0))+list(range(0x829e,0x82a8))+list(range(0x14d2e,0x14d52))+list(range(0x14d5e,0x14d62))+list(range(0x1a6bc,0x1a6c0))
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp)/consumer.BIN;out.parent.mkdir(parents=True);sys.argv=['test','--root',tmp]
                for address in offsets:
                    changed=bytearray(original);changed[address-0x8000]^=1;out.write_bytes(changed)
                    consumer.SHA=hashlib.sha256(changed).hexdigest()
                    with self.subTest(address=hex(address)),contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(ValueError):consumer.main()
        finally:
            consumer.SHA=original_hash;sys.argv=oldargv
    def test_unrelated_image_change_rejected_by_identity(self):
        original=bytearray((ROOT/consumer.BIN).read_bytes());original[0]^=1; oldargv=sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp)/consumer.BIN;out.parent.mkdir(parents=True);out.write_bytes(original);sys.argv=['test','--root',tmp]
                with self.assertRaisesRegex(ValueError,'APP identity'):consumer.main()
        finally:sys.argv=oldargv
if __name__=='__main__':unittest.main()
