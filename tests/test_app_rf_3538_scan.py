import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('appscan', ROOT / 'scripts/scan-app-rf-3538.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AppRFScanTests(unittest.TestCase):
    def test_fixed_image(self):
        data = m.APP.read_bytes()
        result = m.verify(data)
        self.assertEqual(result['counts']['origins'], 38400)
        self.assertEqual(result['hits'], [])
        # Real APP caller witness: AUIPC/ADDI, SP store, indirect call.
        self.assertEqual(data[0x17644-m.BASE:0x1765c-m.BASE].hex(),
                         '970700009387a7ea3ec89147a30cf1008327441c0a858297')
        with self.assertRaises(ValueError):
            m.verify(data[:-1])
        changed = bytearray(data)
        changed[0] ^= 1
        with self.assertRaises(ValueError):
            m.verify(changed)

    def test_synthetic_survival_and_unknown(self):
        # lui a5,0x20003; addi a5,a5,0x538; sw zero,0(a5)
        code = bytes.fromhex('b73700209387875323a00700')
        result = m.forward(code, 0x8000, [(0x8000, 0x800c)], 32)
        self.assertTrue(any(h['store_pc'] == '0x8008' for h in result['hits']))
        # Unsupported/control encoding kills the propagated value.
        broken = code[:4] + bytes.fromhex('0000') + code[4:]
        result = m.forward(broken, 0x8000, [(0x8000, 0x800e)], 32)
        self.assertEqual(result['hits'], [])

if __name__ == '__main__':
    unittest.main()
