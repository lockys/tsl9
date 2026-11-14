#!/usr/bin/env python3
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
import reference_free_a1_cfg as cfg

class ControlFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(cfg.ROOT/cfg.LEDGER).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=cfg.LEDGER_SHA:raise ValueError('ledger hash')
        cls.rows=json.loads(raw)['candidates']['carrier']['groups']['free']
    def test_unmodified(self):
        self.assertEqual(cfg.analyze(self.rows),(77,5,2))
    def test_tablegen_and_all_halfword_operands(self):
        self.assertEqual(cfg.decode_xwch_halfword(bytes.fromhex('ce23')),('qk.c.lhu',15,11,4))
        for opcode,op in ((0x2002,'qk.c.lhu'),(0xa002,'qk.c.sh')):
            for base in range(8,16):
                for reg in range(8,16):
                    for offset in range(0,64,2):
                        word=opcode|((base-8)<<7)|((reg-8)<<2)|((offset>>3)<<10)|(((offset>>1)&3)<<5)
                        self.assertEqual(cfg.decode_xwch_halfword(word.to_bytes(2,'little')),(op,base,reg,offset))
        for word in (0,0x2000,0x6002):
            with self.assertRaisesRegex(ValueError,'Xwchc opcode'):cfg.decode_xwch_halfword(word.to_bytes(2,'little'))
    def test_tablegen_reference(self):
        root=Path(os.environ.get('TSL9_REFERENCE_ROOT',str(cfg.ROOT)))
        path=root/'analysis/wch-resident-candidate-2026-10-21/instruction-reference/RISCVInstrInfoXwch.td'
        if not path.is_file():self.skipTest('external WCH TableGen reference absent')
        td=path.read_bytes()
        self.assertEqual(hashlib.sha256(td).hexdigest(),'d18a5c4d0722e20d3d0398f180931118a5125c9ada56a64d32c602ad5bd71490')
        self.assertIn(b'let Inst{12-10} = imm{5-3};',td)
        self.assertIn(b'let Inst{6-5} = imm{2-1};',td)
    def test_bad_operand_rejected(self):
        row=copy.deepcopy(next(r for r in self.rows if r['PC']==0x20000174))
        row['rd']=10
        with self.assertRaisesRegex(ValueError,'Xwchc load register'):cfg.check_halfword_row(row)
    def test_missing_kill_rejected(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['PC']==0x20000174)['rd']=12
        with self.assertRaisesRegex(ValueError,'incoming a1 read'):cfg.analyze(rows)
    def test_early_read_rejected(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['PC']==0x20000110)['rs1']=11
        with self.assertRaisesRegex(ValueError,'incoming a1 read'):cfg.analyze(rows)
    def test_unknown_op_rejected(self):
        rows=copy.deepcopy(self.rows);rows[0]['op']='unknown'
        with self.assertRaisesRegex(ValueError,'unknown opcode'):cfg.analyze(rows)
    def test_cfg_escape_rejected(self):
        rows=copy.deepcopy(self.rows)
        next(r for r in rows if r['op']=='beq')['target']=0
        with self.assertRaisesRegex(ValueError,'CFG escape'):cfg.analyze(rows)

if __name__=='__main__':unittest.main()
