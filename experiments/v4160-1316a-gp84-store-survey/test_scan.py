import hashlib
import unittest

import scan


def store(imm, funct3, base=3, source=7):
    imm &= 0xfff
    word = ((imm >> 5) << 25) | (source << 20) | (base << 15) | (funct3 << 12) | ((imm & 31) << 7) | 0x23
    return word.to_bytes(4, 'little')


class SurveyTests(unittest.TestCase):
    def test_all_immediates_and_widths(self):
        for f, width in enumerate((1, 2, 4)):
            for imm in range(-2048, 2048):
                hits = scan.candidates(store(imm, f))
                expected = imm < 88 and imm + width > 84
                self.assertEqual(bool(hits), expected, (f, imm))
                if expected:
                    self.assertEqual((hits[0]['immediate'], hits[0]['width'], hits[0]['source_register']), (imm, width, 7))

    def test_alignment_tail_and_rejections(self):
        insn = store(84, 2, source=31)
        self.assertEqual(scan.candidates(b'\0\0' + insn)[0]['file_offset'], 2)
        self.assertEqual(scan.candidates(b'\0' + insn), [])
        self.assertEqual(scan.candidates(insn[:3]), [])
        self.assertEqual(scan.candidates(store(84, 2, base=4)), [])
        self.assertEqual(scan.candidates(store(84, 3)), [])
        self.assertEqual(scan.candidates(bytes([insn[0] ^ 1]) + insn[1:]), [])
        self.assertEqual(scan.candidates(store(84, 2, source=0))[0]['source_register'], 0)

    def test_pin_and_mutation(self):
        image = scan.IMAGE.read_bytes()
        report = scan.report(image)
        self.assertEqual(hashlib.sha256(image).hexdigest(), scan.SHA256)
        self.assertFalse(report['global_writers_complete'])
        for index in (0, len(image) // 2, len(image) - 1):
            mutated = bytearray(image)
            mutated[index] ^= 1
            with self.assertRaises(ValueError):
                scan.report(mutated)
        with self.assertRaises(ValueError):
            scan.report(image[:-1])


if __name__ == '__main__':
    unittest.main()
