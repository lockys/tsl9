#!/usr/bin/env python3
"""Check provider instruction pin failures independently of whole-image hash."""
import contextlib,hashlib,importlib.util,io,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(file,name):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
modules=[(load('counter-precheck-provider-8a82.py','first'),0x8a82,0x8a96),(load('counter-precheck-provider-next-8a96.py','gate'),0x8a96,0x8a9e),(load('counter-precheck-second-provider.py','second'),0x8a9e,0x8abe)]
class Evidence(unittest.TestCase):
    def test_rehashed_instruction_mutations(self):
        image=(ROOT/modules[0][0].BIN).read_bytes();saved=sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                f=Path(tmp)/modules[0][0].BIN;f.parent.mkdir(parents=True);sys.argv=['test','--root',tmp]
                for module,start,end in modules:
                    sha=module.SHA
                    try:
                        for address in range(start,end):
                            data=bytearray(image);data[address-0x8000]^=1;f.write_bytes(data);module.SHA=hashlib.sha256(data).hexdigest()
                            with self.subTest(module=module.__name__,address=hex(address)),contextlib.redirect_stdout(io.StringIO()):
                                with self.assertRaisesRegex(ValueError,'instruction mismatch'):module.main()
                    finally:module.SHA=sha
        finally:sys.argv=saved
    def test_full_width_sentinel(self):
        m=modules[2][0];self.assertIsNone(m.project(0,0xfffe,0,0)[0]);self.assertIsNotNone(m.project(0,0x1fffe,0,0)[0])
    def test_live_full_width_compare(self):
        m=modules[1][0];self.assertEqual(m.project(0,0x1ffff,0xffff)[2],0x8abe)
if __name__=='__main__':unittest.main()
