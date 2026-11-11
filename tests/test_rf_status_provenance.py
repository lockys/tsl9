import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rf_status_provenance', ROOT / 'scripts/verify-rf-status-provenance.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ProvenancePins(unittest.TestCase):
    def test_pins_and_mutations(self):
        for kind, path in (('app', mod.APP), ('sdk', mod.SDK)):
            data = path.read_bytes()
            mod.verify(kind, data)
            base, _, _, windows = mod.SPECS[kind]
            for start, end, _ in windows:
                for address in (start, end - 1):
                    changed = bytearray(data)
                    changed[address - base] ^= 1
                    with self.subTest(kind=kind, address=hex(address)):
                        with self.assertRaises(ValueError):
                            mod.check_windows(kind, changed)
                        with self.assertRaises(ValueError):
                            mod.verify(kind, changed)
            with self.assertRaises(ValueError):
                mod.verify(kind, data[:-1])
            changed = bytearray(data)
            changed[-1] ^= 1  # outside all selected windows
            mod.check_windows(kind, changed)
            with self.assertRaises(ValueError):
                mod.verify(kind, changed)


if __name__ == '__main__':
    unittest.main()
