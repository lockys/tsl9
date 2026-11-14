#!/usr/bin/env python3
import hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('queue',HERE/'queue-clear-820c-decoder.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
class QueueTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.image=(ROOT/q.m.BIN).read_bytes();q.validate(cls.image);cls.code={0x820c+i:b for i,b in enumerate(q.PROVIDER)}
 def test_all_18_instruction_bytes_after_rehash(self):
  old=q.m.SHA
  try:
   for i in range(len(q.PROVIDER)):
    data=bytearray(self.image);data[0x20c+i]^=1;q.m.SHA=hashlib.sha256(data).hexdigest()
    with self.assertRaisesRegex(ValueError,'queue-clear bytes'):q.validate(data)
  finally:q.m.SHA=old
 def test_unknown_compressed_rejected(self):
  code=dict(self.code);code[0x820c]=0;code[0x820d]=0
  with self.assertRaisesRegex(ValueError,'unsupported compressed'):q.execute(code,0,0)
 def test_bounds_and_address_wrap(self):
  for index in (0,1,2,3,0xffffffff):
   ret,events=q.execute(self.code,index,0xffffffff)
   self.assertEqual((ret,events),(index,[('store8',(0xffffffff+193+index)&0xffffffff,0)] if index<=2 else []))
if __name__=='__main__':unittest.main()
