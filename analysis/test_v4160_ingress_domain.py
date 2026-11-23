"""Negative controls for the pinned ingress-domain check (not a CPU test)."""
import contextlib
import io
import unittest
from unittest.mock import patch
import check_v4160_ingress_domain as subject

class Image:
    def __init__(self, data):
        self.data = data
    def read_bytes(self):
        return self.data

class Digest:
    def hexdigest(self):
        return '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'

class IngressDomainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = subject.IMAGE.read_bytes()

    def test_original(self):
        with contextlib.redirect_stdout(io.StringIO()):
            subject.main()

    def test_every_slice_byte_rejected_even_if_hash_gate_passes(self):
        start = 0x16acc - 0x8000
        for index in range(len(subject.EXPECTED)):
            data = bytearray(self.original)
            data[start + index] ^= 1
            with self.subTest(offset=index), patch.object(subject, 'IMAGE', Image(bytes(data))), patch.object(subject, 'sha256', return_value=Digest()):
                with self.assertRaisesRegex(ValueError, '^instruction slice$'):
                    subject.main()

    def test_outside_slice_mutation_rejected_by_hash(self):
        data = bytearray(self.original)
        data[0] ^= 1
        with patch.object(subject, 'IMAGE', Image(bytes(data))):
            with self.assertRaisesRegex(ValueError, '^image identity$'):
                subject.main()

if __name__ == '__main__':
    unittest.main()
