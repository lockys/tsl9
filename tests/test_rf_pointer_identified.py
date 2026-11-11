import runpy
import unittest
from pathlib import Path

scan = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/scan-rf-pointer-identified.py'))
forward = scan['forward']['scan']


class IdentifiedScanTests(unittest.TestCase):
    def test_pinned_and_mutation(self):
        direct = scan['direct']
        data = direct['IMAGE'].read_bytes()
        result = scan['verify'](data)
        self.assertEqual(result['counts'], {'origins': 261, 'instructions_examined': 471,
                         'unknown_stop_paths': 261, 'range_end_paths': 0, 'budget_stop_paths': 0})
        self.assertEqual(result['hits'], [])
        self.assertEqual(result['unsupported_or_control_stops'], 149)
        for i in (0, 0x645dc - direct['BASE'], len(data) - 1):
            changed = bytearray(data)
            changed[i] ^= 1
            with self.assertRaises(ValueError):
                scan['verify'](changed)
        with self.assertRaises(ValueError):
            scan['verify'](data[:-1])

    def test_alias_source_and_kill(self):
        # lui a4,0x20003; addi a4,a4,0x514; li a5,7; c.sw a5,36(a4)
        code = bytes.fromhex('37370020130747519d47 5cd3'.replace(' ', ''))
        result = forward(code, 0, [(0, len(code))])
        hit = result['hits'][0]
        self.assertEqual((hit['address'], hit['base_value'], hit['offset'], hit['source_value']),
                         ('0x20003538', '0x20003514', 36, '0x7'))
        changed = bytearray(code)
        changed[4] ^= 0x80
        self.assertEqual(forward(changed, 0, [(0, len(code))])['hits'], [])
        # An unsupported instruction before the store must not preserve facts.
        changed = code[:8] + b'\x00\x00' + code[8:]
        self.assertEqual(forward(changed, 0, [(0, len(changed))])['hits'], [])
        self.assertEqual(forward(code[:-2], 0, [(0, len(code)-2)])['hits'], [])


if __name__ == '__main__':
    unittest.main()
