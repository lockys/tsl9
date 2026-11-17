import json
import unittest

from witness_inventory import exact_delta, inventory


class InventoryTests(unittest.TestCase):
    def test_exact_deltas_reject_replacement(self):
        baseline = {f'symbol{i}' for i in range(79)} | {'tsl9_ab72_data', 'tsl9_b3da_data'}
        for case, observed in [('extra-undefined', baseline | {'negative_extra'}),
                               ('missing-witness', baseline - {'tsl9_ab72_data'})]:
            self.assertTrue(exact_delta(baseline, observed, case))
            self.assertFalse(exact_delta(baseline, observed - {'symbol0'} | {'impostor'}, case))

    def test_strict_records(self):
        names = [f'symbol{i}' for i in range(81)]
        line = 'PROBE undefined c ' + json.dumps(names)
        self.assertEqual(inventory(line, 'PROBE undefined', 'c', 81), set(names))
        for text, mode in [('', 'c'), (line + '\n' + line, 'c'), (line, 'cpp'),
                           ('PROBE undefined c ' + json.dumps(names[:-1] + [names[0]]), 'c'),
                           ('PROBE undefined c ' + json.dumps(names[:-1]), 'c'),
                           ('PROBE undefined c ' + json.dumps({'names': names}), 'c')]:
            with self.subTest(text=text[:50], mode=mode), self.assertRaises(ValueError):
                inventory(text, 'PROBE undefined', mode, 81)


if __name__ == '__main__':
    unittest.main()
