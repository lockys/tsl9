import unittest

from model import initialize, step


def oracle(counter, a0):
    # Independent partition by counter, then by the numeric threshold.
    if counter == 0:
        return (0, 0x9FC8 if a0 >= 25 else None)
    return (counter - int(a0 < 25), None)


class CounterSequenceTests(unittest.TestCase):
    def test_initialized_sequence(self):
        counter = initialize()
        self.assertEqual(counter, 25)
        for expected in range(24, -1, -1):
            counter, tail = step(counter, 24)
            self.assertEqual((counter, tail), (expected, None))
        self.assertEqual(step(counter, 25), (0, 0x9FC8))

    def test_repeated_25_nonzero(self):
        counter = initialize()
        for _ in range(100):
            counter, tail = step(counter, 25)
            self.assertEqual((counter, tail), (25, None))

    def test_all_byte_pairs(self):
        for counter in range(256):
            for a0 in range(256):
                self.assertEqual(step(counter, a0), oracle(counter, a0),
                                 (counter, a0))

    def test_uint32_boundaries(self):
        for counter in range(256):
            for a0 in (0, 23, 24, 25, 26, 255, 256, 0x7FFFFFFF,
                       0x80000000, 0xFFFFFFFE, 0xFFFFFFFF):
                self.assertEqual(step(counter, a0), oracle(counter, a0),
                                 (counter, a0))

    def test_threshold_and_decrement_mutants_have_witnesses(self):
        # These deliberately incorrect alternatives must disagree with the model.
        def inclusive_25(counter, a0):
            if a0 <= 25:
                return (max(0, counter - 1), None)
            return (counter, 0x9FC8 if counter == 0 else None)

        def tail_on_decrement_to_zero(counter, a0):
            if a0 <= 24 and counter:
                counter -= 1
                return (counter, 0x9FC8 if counter == 0 else None)
            return (counter, 0x9FC8 if a0 > 24 and counter == 0 else None)

        self.assertNotEqual(inclusive_25(0, 25), step(0, 25))
        self.assertNotEqual(inclusive_25(25, 25), step(25, 25))
        self.assertNotEqual(tail_on_decrement_to_zero(1, 24), step(1, 24))

    def test_invalid_domains(self):
        for counter, a0 in ((-1, 0), (256, 0), (0, -1), (0, 0x100000000)):
            with self.assertRaises(ValueError):
                step(counter, a0)


if __name__ == "__main__":
    unittest.main()
