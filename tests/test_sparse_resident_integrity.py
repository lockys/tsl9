import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('integrity', ROOT / 'scripts/audit_sparse_resident_integrity.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IntegrityTests(unittest.TestCase):
    def test_synthetic_complete_and_negative_cases(self):
        source = {p: p % 251 for p in range(0x100, 0x120)}
        copy = [(0x110, 0x120)]
        self.assertTrue(m.audit(source, dict(source), copy)['passed'])
        self.assertFalse(m.audit(source, {p: source[p] for p in range(0x100, 0x104)}, copy)['passed'])
        short = dict(source); del short[0x11c]; del short[0x11d]; del short[0x11e]; del short[0x11f]
        self.assertEqual(m.audit(short, short, copy)['missing_source'], [['0x11c', '0x120']])
        forged = dict(source); forged[0x120] = 0
        self.assertEqual(m.audit(source, forged, copy)['unproven_elf_bytes'], [['0x120', '0x121']])
        contaminated = dict(source); contaminated[0x11f] ^= 1
        self.assertEqual(m.audit(source, contaminated, copy)['mismatch'], [['0x11f', '0x120']])

    def test_real_reference_cannot_pass_even_with_all_recorded_bytes(self):
        ref = (ROOT / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023').resolve()
        segments = m.validate(ROOT, ref)
        source = {s['start'] + i: b for s in segments for i, b in enumerate((ref / s['path']).read_bytes())}
        result = m.audit(source, source)
        self.assertFalse(result['passed'])
        self.assertEqual(result['missing_source'], [['0x6eb2c', '0x6eb30']])


if __name__ == '__main__':
    unittest.main()
