"""Synthetic overlap witness, not a device reachability or CPU test."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'd14a_projection', Path(__file__).with_name('d14a-offline-projection.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AliasOrderTest(unittest.TestCase):
    def test_source_is_read_before_overlapping_destination_is_written(self):
        gp = 0x20004000
        destination = gp + 232
        p = destination - 5
        memory = {destination - 2: 10, destination: 20,
                  destination + 1: 21, destination + 2: 30,
                  destination + 3: 31, destination + 4: 40}
        target, updated, trace = m.run(m.CODE, p, gp, memory)
        self.assertEqual(target, 0x13c4e)
        self.assertEqual([updated[destination + i] for i in range(4)], [10, 20, 30, 40])
        self.assertEqual(trace, [
            ('read', destination - 2, 10), ('read', destination, 20),
            ('read', destination, 20), ('read', destination + 2, 30),
            ('read', destination + 4, 40),
            ('write', destination, 10), ('write', destination + 1, 20),
            ('write', destination + 2, 30), ('write', destination + 3, 40),
        ])
        # A streaming copy would use the overwritten value for source[1].
        self.assertNotEqual(updated[destination + 1], updated[destination])


if __name__ == '__main__':
    unittest.main()
