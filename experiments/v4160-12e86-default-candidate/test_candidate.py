"""Offline static and Python event-model tests, not execution of C."""
import hashlib
from pathlib import Path
import re
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FW = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
RAW = bytes.fromhex('b70704004111bc4722c41794ff1f1304446006c6228513060010814582979307a005a30ff40eb717430b938727401cc0b717450d938747c45cc0b7370c2b9387a7c01cc4b7571f5ff9075cc4b727212a938707e21cc82244b24041016ff03ff7')
EXPECTED = [
    ('store', 0x2000c593, 1, 0x5a),
    ('store', 0x2000c494, 4, 0x0b431402),
    ('store', 0x2000c498, 4, 0x0d450c44),
    ('store', 0x2000c49c, 4, 0x2b0c2c0a),
    ('store', 0x2000c4a0, 4, 0x5f1f501e),
    ('store', 0x2000c4a4, 4, 0x2a211e20),
]


def parse_stores(source):
    pattern = r'h->store\(h->ctx, (0x[0-9a-f]+)u, ([14])u, (0x[0-9a-f]+)u\);'
    return [('store', int(a, 16), int(w), int(v, 16)) for a, w, v in re.findall(pattern, source)]


def model(slot, normal, stores):
    events = [('read', 0x40048, 4), ('call', slot & 0xfffffffe, 0x2000c494, 0, 256)]
    if normal:
        events.extend(stores)
        events.append(('tail', 0x12e54))
    return events


class Tests(unittest.TestCase):
    def test_pinned_image_and_whole_function(self):
        image = FW.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
        self.assertEqual(image[0x12e86-0x8000:0x12ee6-0x8000], RAW)
        self.assertNotEqual(image[0x12e86-0x8000:0x12ee6-0x8000], bytes(len(RAW)))

    def test_static_stores_and_negative_mutation(self):
        source = (HERE / 'candidate.c').read_text(encoding='utf-8')
        self.assertEqual(parse_stores(source), EXPECTED)
        self.assertNotEqual(parse_stores(source.replace('0x5au', '0x5bu')), EXPECTED)
        self.assertIn('if (!h->call(', source)
        self.assertIn('& ~1u', source)
        self.assertIn('h->tail(h->ctx, 0x12e54u)', source)

    def test_events_and_failure(self):
        stores = parse_stores((HERE / 'candidate.c').read_text(encoding='utf-8'))
        prefix = [('read', 0x40048, 4), ('call', 0x12345678, 0x2000c494, 0, 256)]
        self.assertEqual(model(0x12345679, True, stores), prefix + EXPECTED + [('tail', 0x12e54)])
        self.assertEqual(model(0x12345679, False, stores), prefix)
        self.assertEqual(model(0xffffffff, False, stores)[1][1], 0xfffffffe)
        self.assertNotEqual(model(0x12345679, True, stores), prefix + list(reversed(EXPECTED)) + [('tail', 0x12e54)])


if __name__ == '__main__':
    unittest.main()
