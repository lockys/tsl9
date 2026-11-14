#!/usr/bin/env python3
import copy
import hashlib
import json
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
