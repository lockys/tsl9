"""Negative checks for each independent verifier; no target code is run."""
import hashlib
import unittest
import audit


def mutate(data, offset):
    result = bytearray(data)
    result[offset] ^= 1
    return bytes(result)


def rejects(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise RuntimeError('expected ValueError from ' + fn.__name__)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = audit.OFFICIAL.read_bytes()
        cls.b = audit.CANDIDATE.read_bytes()

    def test_image_pins(self):
        audit.check_image(self.a, audit.SHA_OFFICIAL)
        audit.check_image(self.b, audit.SHA_CANDIDATE)
        rejects(audit.check_image, self.a[:-1], audit.SHA_OFFICIAL)
        rejects(audit.check_image, self.a[:-1], hashlib.sha256(self.a[:-1]).hexdigest())
        rejects(audit.check_image, mutate(self.a, 0), audit.SHA_OFFICIAL)
        rejects(audit.check_image, self.b, audit.SHA_OFFICIAL)
        rejects(audit.check_image, self.a, audit.SHA_CANDIDATE)

    def test_differences(self):
        audit.check_differences(self.a, self.b)
        rejects(audit.check_differences, self.a, self.b[:-1])
        rejects(audit.check_differences, self.a, self.a)
        rejects(audit.check_differences, self.a, mutate(self.b, 0))
        offset = 0x8a7f - audit.BASE
        restored = self.b[:offset] + self.a[offset:offset + 1] + self.b[offset + 1:]
        rejects(audit.check_differences, self.a, restored)
        rejects(audit.check_differences, self.a, mutate(self.b, 0x8a82 - audit.BASE))

    def test_range_and_outside(self):
        audit.check_range(audit.START, audit.END)
        audit.check_outside(self.a, self.b, audit.START, audit.END)
        for start, end in ((audit.START - 1, audit.END), (audit.START, audit.END - 1),
                           (audit.END, audit.START)):
            rejects(audit.check_range, start, end)
            rejects(audit.check_outside, self.a, self.b, start, end)
        rejects(audit.check_outside, self.a, mutate(self.b, 0), audit.START, audit.END)
        rejects(audit.check_outside, self.a, mutate(self.b, audit.END - audit.BASE), audit.START, audit.END)
        rejects(audit.check_outside, self.a, self.b[:-1], audit.START, audit.END)
        rejects(audit.check_outside, self.a[:-1], self.b[:-1], audit.START, audit.END)

    def test_swaps_both_directions(self):
        for dest, donor in ((self.a, self.b), (self.b, self.a)):
            audit.check_swap(dest, donor, donor, audit.START, audit.END)
            rejects(audit.check_swap, dest, donor, dest, audit.START, audit.END)
            rejects(audit.check_swap, mutate(dest, 0), donor, donor, audit.START, audit.END)
            rejects(audit.check_swap, dest, mutate(donor, audit.START - audit.BASE), donor, audit.START, audit.END)
            rejects(audit.check_swap, dest, donor, donor[:-1], audit.START, audit.END)
            rejects(audit.check_swap, dest[:-1], donor[:-1], donor[:-1], audit.START, audit.END)
            rejects(audit.check_swap, dest, donor, donor, audit.START + 1, audit.END)


if __name__ == '__main__':
    unittest.main()
