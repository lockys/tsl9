import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit

HERE = Path(__file__).resolve().parent


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.root = Path(self.tmp.name)
        self.pins = audit.PINS.copy()
        for path in self.pins:
            dest = self.root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(audit.ROOT / path, dest)

    def tearDown(self):
        self.tmp.cleanup()

    def mutate(self, path, old, new, repin=False):
        p = self.root / path
        text = p.read_text(encoding='utf-8')
        self.assertEqual(text.count(old), 1)
        p.write_text(text.replace(old, new), encoding='utf-8', newline='')
        if repin:
            self.pins[path] = hashlib.sha256(p.read_bytes()).hexdigest()
            if path in (audit.EVENT, audit.LEAF):
                m = self.root / audit.MANIFEST
                manifest = json.loads(m.read_text(encoding='utf-8'))
                for entry in manifest['files']:
                    if entry['destination'] == path:
                        entry['sha256'] = self.pins[path]
                m.write_text(json.dumps(manifest), encoding='utf-8')
                self.pins[audit.MANIFEST] = hashlib.sha256(m.read_bytes()).hexdigest()

    def test_baseline(self):
        self.assertTrue(audit.audit(self.root, self.pins)['passed'])

    def test_each_input_hash_and_missing_fail_closed(self):
        for path in audit.PINS:
            with self.subTest(path=path):
                p = self.root / path
                original = p.read_bytes()
                p.write_bytes(original + b' ')
                with self.assertRaises(ValueError):
                    audit.audit(self.root, self.pins)
                p.unlink()
                with self.assertRaises(OSError):
                    audit.audit(self.root, self.pins)
                p.write_bytes(original)

    def test_repinned_fingerprint_changes_fail(self):
        cases = [
            (audit.EVENT, 'R_RISCV_JAL, ' + audit.ALIAS, 'R_RISCV_CALL, ' + audit.ALIAS),
            (audit.EVENT, 'jal ra, .Levent_control_13a54', 'jal ra, .Lother'),
            (audit.LEAF, 'REGION void ' + audit.TARGET + '(void)', 'REGION void changed_d472(void)'),
            (audit.LAYOUT, '"' + audit.ALIAS + '": "' + audit.TARGET + '"', '"' + audit.ALIAS + '": "wrong"'),
            (audit.AGG, "aliases = dict(compact['candidate_aliases']) if compact else {}", "aliases = {}"),
            (audit.AGG, "'--defsym=' + k + '=' + v", "'--wrong=' + k + '=' + v"),
            (audit.AGG, "symbols[k]['index'] not in (0, 0xfff1)", "symbols[k]['index'] in (0, 0xfff1)"),
            (audit.AGG, 'remaining != expected', 'remaining == expected'),
            (audit.AGG, "symbols[k]['index'] == symbols[v]['index']", "symbols[k]['index'] != symbols[v]['index']"),
            (audit.AGG, "symbols[k]['value'] == symbols[v]['value']", "symbols[k]['value'] != symbols[v]['value']"),
            (audit.MANIFEST, '"name": "state-events",\n      "profile": "ring-bank"', '"name": "state-events",\n      "profile": "wrong"'),
            (audit.MANIFEST, '"name": "state-leaf-reads",\n      "profile": "queue-consumer-a0-a5"', '"name": "state-leaf-reads",\n      "profile": "wrong"'),
        ]
        for path, old, new in cases:
            with self.subTest(path=path, old=old):
                self.tearDown()
                self.setUp()
                self.mutate(path, old, new, repin=True)
                with self.assertRaises((ValueError, KeyError)):
                    audit.audit(self.root, self.pins)

    def test_repinned_dead_condition_can_satisfy_fingerprint(self):
        # A syntactically valid but disabled condition still retains the text.
        self.mutate(audit.AGG, 'remaining != expected', '(False and remaining != expected)', repin=True)
        compile((self.root / audit.AGG).read_bytes(), audit.AGG, 'exec')
        self.assertTrue(audit.audit(self.root, self.pins)['passed'])

    def test_cli_rejects_drift_normal_and_optimized(self):
        script = self.root / 'experiments' / 'fixture' / 'audit.py'
        script.parent.mkdir(parents=True)
        shutil.copyfile(HERE / 'audit.py', script)
        event = self.root / audit.EVENT
        event.write_bytes(event.read_bytes() + b' ')
        for flags in ([], ['-O']):
            with self.subTest(flags=flags):
                p = subprocess.run([sys.executable, '-E', '-B', *flags, str(script)], capture_output=True, text=True)
                self.assertEqual(p.returncode, 1)
                self.assertIn('FAIL: hash mismatch: ' + audit.EVENT, p.stderr)
                self.assertEqual(p.stdout, '')

    def test_cli_normal_and_optimized(self):
        for flags in ([], ['-O']):
            p = subprocess.run([sys.executable, '-E', '-B', *flags, str(HERE / 'audit.py')], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue(json.loads(p.stdout)['passed'])


if __name__ == '__main__':
    unittest.main()
