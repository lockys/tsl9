import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('registration_checker', ROOT / 'scripts/verify-901a-registration-static.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class RegistrationStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {k: (ROOT / p).read_bytes() for k, (p, _) in checker.INPUTS.items()}

    def test_original(self):
        checker.verify(self.data)

    def test_each_input_mutation_rejected_by_hash(self):
        for key, data in self.data.items():
            with self.subTest(key=key):
                changed = dict(self.data)
                changed[key] = bytes([data[0] ^ 1]) + data[1:]
                with self.assertRaises(ValueError):
                    checker.verify(changed)

    def test_opcode_and_slot_mutations_rejected_without_hash_gate(self):
        for key, offset in [('app', 0x907a-0x8000), ('app', 0x19b2e-0x8000), ('sdk', 0x80), ('sdk', 0x43c72-0x40000), ('sdk', 0x40b7a-0x40000)]:
            with self.subTest(key=key, offset=offset):
                changed = dict(self.data)
                raw = bytearray(changed[key]); raw[offset] ^= 1; changed[key] = bytes(raw)
                with self.assertRaises(ValueError):
                    checker.check_opcode_windows(changed['app'], changed['sdk'], changed)

    def test_scheduler_each_byte_mutation_without_hash_gate(self):
        for offset in range(0x9124-0x8000, 0x9250-0x8000):
            changed = dict(self.data)
            raw = bytearray(changed['app']); raw[offset] ^= 1; changed['app'] = bytes(raw)
            with self.subTest(pc=offset + 0x8000), self.assertRaises(ValueError):
                checker.check_opcode_windows(changed['app'], changed['sdk'], changed)

    def test_evidence_opcode_and_truncation_rejected(self):
        changed = dict(self.data)
        evidence = json.loads(changed['register_ops'])
        evidence['selected_functions'][0]['operations'][0]['bytes'] = '00000000'
        changed['register_ops'] = json.dumps(evidence).encode()
        with self.assertRaises(ValueError):
            checker.check_opcode_windows(changed['app'], changed['sdk'], changed)
        changed = dict(self.data); changed['sdk'] = changed['sdk'][:128]
        with self.assertRaises(ValueError):
            checker.check_opcode_windows(changed['app'], changed['sdk'], changed)


if __name__ == '__main__':
    unittest.main()
