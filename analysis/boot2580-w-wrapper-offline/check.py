"""Offline byte pin and derived frame model; never executes target instructions."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
BODY = bytes.fromhex(
    '1307f040637fd7088280e17793c757f5178700202319f7849375f40f97870020'
    '238497849357840017870020230fb782a69517870020a309f7829786002093862682'
    'ae9793f7f70f0147368693150701c181850663ec850233078600a305f700190497770020'
    '239e877e97770020239b077e2244b7070400b2409244024903a3070503c5c1078545'
    '41010283b305e90083c505000507ae972385b60093f7f70f75b703d7e107631ea702'
    'c167f917630af702b707040083a7c713411122c426c24ac006c6ae84938581063684'
    '328982978547e30cf5f2b240224492440249410182808280')


def check_body(image):
    if image[0x848:0x92c] != BODY:
        raise ValueError('wrapper bytes mismatch')


def model(context, current, provider_result, command, payload):
    """Derived conditional model, not an emulator or a transmission."""
    if len(payload) > 1039 or context != current or current == 0xfffe or provider_result != 1:
        return None
    n = len(payload)
    checksum = (command + (n >> 8) + (n & 255) + sum(payload)) & 255
    return bytes((0x55, 0x7f, command, n >> 8, n & 255)) + payload + bytes((checksum,))


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = IMAGE.read_bytes()

    def test_image_and_complete_body(self):
        self.assertEqual(len(self.image), 12288)
        self.assertEqual(hashlib.sha256(self.image).hexdigest(), SHA)
        self.assertEqual(len(BODY), 228)
        check_body(self.image)

    def test_mutations_bypass_image_hash(self):
        for pc in (0x1848, 0x184c, 0x1852, 0x1854, 0x185c, 0x1868,
                   0x1874, 0x187e, 0x188c, 0x189c, 0x18a4, 0x18a8,
                   0x18ae, 0x18b6, 0x18c6, 0x18d2, 0x18e0, 0x18ea,
                   0x18ee, 0x18f6, 0x18fe, 0x1916, 0x191a):
            with self.subTest(pc=hex(pc)):
                b = bytearray(self.image)
                b[pc-0x1000] ^= 1
                with self.assertRaises(ValueError):
                    check_body(b)

    def test_derived_frame_and_gates(self):
        self.assertEqual(model(7, 7, 1, 0x57, b''), bytes.fromhex('55 7f 57 00 00 57'))
        self.assertEqual(model(7, 7, 1, 0x57, b'\x01\xff'), bytes.fromhex('55 7f 57 00 02 01 ff 59'))
        self.assertIsNone(model(7, 8, 1, 0x57, b''))
        self.assertIsNone(model(0xfffe, 0xfffe, 1, 0x57, b''))
        self.assertIsNone(model(7, 7, 0, 0x57, b''))
        self.assertIsNone(model(7, 7, 2, 0x57, b''))
        self.assertIsNotNone(model(7, 7, 1, 0x57, bytes(1039)))
        self.assertIsNone(model(7, 7, 1, 0x57, bytes(1040)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
