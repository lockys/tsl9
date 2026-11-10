"""Static byte anchors only; no device access, transport, or ISA execution."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
# Contiguous instruction sequences, based on retained radare2 disassembly.
ANCHORS = {
    0x227a: '13070040b38687009042b386f9009442e31cd6f49107e397e7fe81460146930570058da0',
    0x22fe: '2254b2500259f249624a2685925445616f002079',
    0x2aa0: '2a88ae88b287368711c299e6ba863e86c68542856fe05fd919bf',
}


def check_anchors(raw):
    for pc, encoded in ANCHORS.items():
        expected = bytes.fromhex(encoded)
        if raw[pc-0x1000:pc-0x1000+len(expected)] != expected:
            raise ValueError(f'anchor mismatch at {pc:#x}')


class ReplyEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = IMAGE.read_bytes()

    def test_pinned_image_and_anchors(self):
        self.assertEqual(len(self.raw), 12288)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), SHA)
        check_anchors(self.raw)

    def test_mutations_rejected_without_whole_file_hash(self):
        # compare/loop, response length, pointer, command, jump, wrapper
        # null-pointer branch, register forwarding, and final delegation.
        for pc in (0x228a, 0x2290, 0x2294, 0x2296, 0x2298, 0x229c,
                   0x2308, 0x230e, 0x2aa8, 0x2aaa, 0x2aac, 0x2aae, 0x2ab4):
            with self.subTest(pc=hex(pc)):
                altered = bytearray(self.raw)
                altered[pc-0x1000] ^= 1
                with self.assertRaises(ValueError):
                    check_anchors(altered)


if __name__ == '__main__':
    unittest.main(verbosity=2)
