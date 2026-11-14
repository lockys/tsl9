import hashlib
import types
from pathlib import Path
import unittest

PATH = Path(__file__).with_name('check.py')
check = types.ModuleType('seam_check')
check.__file__ = str(PATH)
exec(compile(PATH.read_bytes(), str(PATH), 'exec'), check.__dict__)


class SeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with check.BIN.open('rb') as stream:
            cls.image = stream.read(76801)
        if len(cls.image) != 76800:
            raise ValueError('BIN length')

    def test_reference(self):
        result = check.verify(self.image)
        self.assertFalse(result['passed'])
        self.assertEqual(result['status'], 'INCOMPLETE_FAIL_CLOSED')
        self.assertEqual(len(result['anchors']), 9)
        self.assertEqual(len(result['jal_edges']), 8)

    def test_raw_scan(self):
        self.assertEqual(check.raw_jal_sites(self.image, check.BASE, 0xcf96), [(0x14dca, 0)])
        # Two literal JALs to their own PCs, including the final possible window.
        self.assertEqual(check.raw_jal_sites(bytes.fromhex('6f000000'), 0x1000, 0x1000), [(0x1000, 0)])
        self.assertEqual(check.raw_jal_sites(bytes.fromhex('00006f000000'), 0x1000, 0x1002), [(0x1002, 0)])
        self.assertEqual(check.raw_jal_sites(bytes.fromhex('006f000000'), 0x1000, 0x1001), [])
        # Fixed literal words: zero then -4, and the maximum positive JAL offset.
        self.assertEqual(check.raw_jal_sites(bytes.fromhex('6f0000006ff0dfff'), 0x1000, 0x1000),
                         [(0x1000, 0), (0x1004, 0)])
        self.assertEqual(check.raw_jal_sites(bytes.fromhex('6ff0ff7f'), 0x1000, 0x100ffe),
                         [(0x1000, 0)])
        for size in range(4):
            self.assertEqual(check.raw_jal_sites(bytes(size), 0x1000, 0x1000), [])
        for base, target, data in [(1, 0, b''), (0xfffffffe, 0, bytes(4)), (0, -1, b'')]:
            with self.assertRaisesRegex(ValueError, 'non-wrapping RV32 range'):
                check.raw_jal_sites(data, base, target)
        self.assertEqual(check.verify(self.image)['raw_jal_cf96'], [{'pc': '0x14dca', 'rd': 0}])

    def test_each_anchor_mutation(self):
        for name, (address, expected) in check.ANCHORS.items():
            for offset in range(len(bytes.fromhex(expected))):
                with self.subTest(name=name, offset=offset):
                    data = bytearray(self.image)
                    data[address - check.BASE + offset] ^= 1
                    with self.assertRaisesRegex(ValueError, 'anchor mismatch: ' + name):
                        check.verify(data, check_identity=False)

    def test_each_edge_target_and_register(self):
        for name, (address, _, _) in check.JALS.items():
            for bit in (7, 21):
                with self.subTest(name=name, bit=bit):
                    data = bytearray(self.image)
                    i = address - check.BASE
                    w = int.from_bytes(data[i:i+4], 'little') ^ (1 << bit)
                    data[i:i+4] = w.to_bytes(4, 'little')
                    with self.assertRaisesRegex(ValueError, 'edge mismatch: ' + name):
                        check.verify(data, check_identity=False)

    def test_identity_and_bounds(self):
        data = bytearray(self.image)
        data[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'BIN identity'):
            check.verify(data)
        with self.assertRaisesRegex(ValueError, 'BIN length'):
            check.verify(self.image[:-1])
        self.assertEqual(hashlib.sha256(self.image).hexdigest(), check.SHA)

    def test_fixed_jal_vectors(self):
        # Literal JAL words: zero, one bit in each immediate field, signed limits,
        # negative two, and RV32 PC wraparound. No test-side encoder is used.
        vectors = [
            (0x1000, 0x0000006f, 0x1000),
            (0x1000, 0x0020006f, 0x1002),
            (0x1000, 0x0010006f, 0x1800),
            (0x1000, 0x0000106f, 0x2000),
            (0x100000, 0x8000006f, 0),
            (0x1000, 0x7ffff06f, 0x100ffe),
            (0x1000, 0xfffff06f, 0x0ffe),
            (0xfffffffe, 0x0020006f, 0),
        ]
        for pc, word, target in vectors:
            with self.subTest(pc=pc, word=word):
                self.assertEqual(check.decode_jal(pc, word.to_bytes(4, 'little')), (target, 0))
        self.assertEqual(check.decode_jal(0x1000, bytes.fromhex('ef000000')), (0x1000, 1))

    def test_jal_negative_immediates_and_opcode(self):
        for address, destination, rd in check.JALS.values():
            self.assertEqual(check.decode_jal(address, self.image[address-check.BASE:address-check.BASE+4]), (destination, rd))
        with self.assertRaisesRegex(ValueError, 'JAL opcode'):
            check.decode_jal(0, bytes(4))
        with self.assertRaisesRegex(ValueError, 'JAL width'):
            check.decode_jal(0, bytes(2))


if __name__ == '__main__':
    unittest.main()
