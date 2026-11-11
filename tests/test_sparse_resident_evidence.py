import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023'
spec = importlib.util.spec_from_file_location('sparse_resident_evidence', ROOT / 'scripts/sparse_resident_evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)

class SparseEvidenceTests(unittest.TestCase):
    def test_real_fixed_hex_and_all_segments(self):
        segments = evidence.validate(ROOT, REF.resolve())
        self.assertEqual((segments[-1]['start'], segments[-1]['end_exclusive'], segments[-1]['bytes']), (0x6eaa4, 0x6eb2c, 136))

    def test_corrupted_inputs_rejected(self):
        original = Path.read_bytes
        for target in ('wchble_rom.hex', 'source-map.json', 'REFERENCE-CANDIDATE-ONLY-0006EAA4-0006EB2C.bin'):
            def corrupt(path):
                data = original(path)
                return data[:-1] + bytes([data[-1] ^ 1]) if path.name == target else data
            with self.subTest(target=target), patch.object(Path, 'read_bytes', corrupt), self.assertRaises(ValueError):
                evidence.validate(ROOT, REF.resolve())

    def test_rehashed_contaminated_tail_rejected(self):
        original = Path.read_bytes
        m = json.loads(original(REF / 'source-map.json'))
        name = m['segments'][-1]['path']
        data = original(REF / name)
        contaminated = bytes([data[0] ^ 1]) + data[1:]
        m['segments'][-1]['sha256'] = evidence.hashlib.sha256(contaminated).hexdigest()
        forged = json.dumps(m).encode()
        def replace(path):
            if path.name == 'source-map.json': return forged
            if path.name == name: return contaminated
            return original(path)
        with patch.object(Path, 'read_bytes', replace), patch.object(evidence, 'MAP_SHA', evidence.hashlib.sha256(forged).hexdigest()), self.assertRaisesRegex(ValueError, 'differs from HEX'):
            evidence.validate(ROOT, REF.resolve())

    def test_forged_map_cannot_add_gap_or_reorder_overlap(self):
        original = Path.read_bytes
        raw_map = original(REF / 'source-map.json')
        for mutation in ('gap', 'overlap'):
            m = json.loads(raw_map)
            if mutation == 'gap':
                m['segments'][-1]['end_exclusive'] += 4
                m['segments'][-1]['bytes'] += 4
            else:
                m['segments'][1]['start'] = m['segments'][0]['start']
                m['segments'][1]['end_exclusive'] = m['segments'][0]['start'] + m['segments'][1]['bytes']
            forged = json.dumps(m).encode()
            def replace(path):
                return forged if path.name == 'source-map.json' else original(path)
            # Simulate a re-pinned but malicious manifest; semantic checks must still reject it.
            with self.subTest(mutation=mutation), patch.object(Path, 'read_bytes', replace), patch.object(evidence, 'MAP_SHA', evidence.hashlib.sha256(forged).hexdigest()), self.assertRaises(ValueError):
                evidence.validate(ROOT, REF.resolve())

if __name__ == '__main__':
    unittest.main()
