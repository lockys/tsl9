"""Synthetic parser checks only; no device, emulator or target execution."""
import unittest
from decode_probe import decode

def frame(arch, impl):
    return b'T9D\x01' + arch.to_bytes(4, 'little') + impl.to_bytes(4, 'little')

class DecodeProbeTests(unittest.TestCase):
    def test_manual_v4c_pattern(self):
        result = decode(frame(0xdc68d883, 0xdc688001))
        self.assertEqual(result['marchid'], '0xdc68d883')
        self.assertEqual(result['mimpid'], '0xdc688001')
        self.assertTrue(result['matches_wch_v4c_manual_pattern'])

    def test_other_values_not_attributed_to_v4c(self):
        for arch, impl in ((0xdc68d886, 0xdc688001), (0xdc68d883, 0), (0, 0)):
            self.assertFalse(decode(frame(arch, impl))['matches_wch_v4c_manual_pattern'])

    def test_invalid_framing_rejected(self):
        for data in (b'', b'X9D\x01'+bytes(8), b'T9D\x02'+bytes(8), frame(0,0)+b'\x00'):
            with self.assertRaises(ValueError): decode(data)

if __name__ == '__main__': unittest.main()
