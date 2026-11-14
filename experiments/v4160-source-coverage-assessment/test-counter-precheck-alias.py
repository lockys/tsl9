#!/usr/bin/env python3
"""Mutation controls for the queue/precheck stack alias witnesses."""
import contextlib,hashlib,importlib.util,io,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(filename,name):
    s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
alias=load('counter-precheck-copy-alias.py','alias');stack=load('counter-precheck-stack-separation.py','stack')
class Evidence(unittest.TestCase):
    def test_instruction_pins_after_rehash(self):
        image=(ROOT/alias.BIN).read_bytes();oldargs=sys.argv[:]
        spans={alias:((0x8332,0x835c),(0x82fe,0x8304)),stack:((0x12c58,0x12c5a),(0x12cae,0x12cb4),(0x82d2,0x82d4),(0x8300,0x8304),(0x8352,0x8358))}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                f=Path(tmp)/alias.BIN;f.parent.mkdir(parents=True);sys.argv=['test','--root',tmp]
                for module,ranges in spans.items():
                    sha=module.SHA
                    try:
                        for start,end in ranges:
                            for addr in range(start,end):
                                data=bytearray(image);data[addr-0x8000]^=1;f.write_bytes(data);module.SHA=hashlib.sha256(data).hexdigest()
                                with self.subTest(module=module.__name__,addr=hex(addr)),contextlib.redirect_stdout(io.StringIO()):
                                    with self.assertRaisesRegex(ValueError,'instruction mismatch'):module.main()
                    finally:module.SHA=sha
        finally:sys.argv=oldargs
    def test_alias_control(self):
        for b in (0,8,255):
            self.assertEqual(alias.run(b,True)[:2],(b,b+2));self.assertEqual(alias.run(b,False)[:2],(8,10))
    def test_wrap(self):
        self.assertEqual(stack.addr(0xffffffff,72),71)
if __name__=='__main__':unittest.main()
