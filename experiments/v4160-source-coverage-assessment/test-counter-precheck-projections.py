#!/usr/bin/env python3
"""Controls for precheck projections; rehash altered APP to exercise pins."""
import contextlib,hashlib,importlib.util,io,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(filename,name):
    s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
active=load('counter-precheck-active.py','active');inactive=load('counter-precheck-inactive.py','inactive')
class Evidence(unittest.TestCase):
    def test_rehashed_instruction_mutations(self):
        image=(ROOT/active.BIN).read_bytes();oldargv=sys.argv[:]
        ranges={active:((0x8308,0x8332),(0x834e,0x836a),(0x836a,0x8374),(0x838a,0x838e)),inactive:((0x82ee,0x8300),(0x8308,0x8328),(0x836a,0x8374),(0x838a,0x838e))}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                f=Path(tmp)/active.BIN;f.parent.mkdir(parents=True);sys.argv=['test','--root',tmp]
                for module,spans in ranges.items():
                    original_hash=module.SHA
                    try:
                        for start,end in spans:
                            for addr in range(start,end):
                                altered=bytearray(image);altered[addr-0x8000]^=1;f.write_bytes(altered);module.SHA=hashlib.sha256(altered).hexdigest()
                                with self.subTest(module=module.__name__,addr=hex(addr)),contextlib.redirect_stdout(io.StringIO()):
                                    with self.assertRaises(ValueError):module.main()
                    finally:module.SHA=original_hash
        finally:sys.argv=oldargv
    def test_active_boundaries(self):
        self.assertEqual(active.project(((0,2,1),(1,2,255)),8),(255,(0,1)))
        self.assertEqual(active.project(((0,2,1),(1,2,255)),9),(255,()))
        self.assertEqual(active.project(((0xfffe,2,255),(0,0,255)),8),(0,()))
    def test_inactive_read_order(self):
        mem=bytearray(10);mem[2:4]=b'\xfe\xff';mem[6:8]=b'\xfe\xff'
        self.assertEqual(inactive.project(mem),(0,[(2,2),(6,2)]))
if __name__=='__main__':unittest.main()
