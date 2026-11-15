import hashlib
import importlib.util
import os
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('d14a_projection', Path(__file__).with_name('d14a-offline-projection.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ProjectionTests(unittest.TestCase):
    def test_firmware_identity_if_available(self):
        default = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
        path = Path(os.environ.get('TSL9_V4160_BIN', str(default)))
        if not path.is_file() and 'TSL9_V4160_BIN' not in os.environ:
            self.skipTest('firmware fixture not present; set TSL9_V4160_BIN')
        image = path.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), m.SHA256)
        self.assertEqual(image[m.PC-m.BASE:m.END-m.BASE], m.CODE)

    def test_each_compare_branch_and_access_order(self):
        gp, p = 0x20004000, 0x20005000
        source = (11, 22, 33, 44)
        for mismatch in range(5):
            memory = {p + offset: value for offset, value in zip((3, 5, 7, 9), source)}
            memory.update({gp + 232 + i: value ^ (1 if i == mismatch else 0) for i, value in enumerate(source)})
            target, updated, trace = m.run(m.CODE, p, gp, memory)
            self.assertEqual(target, 'return' if mismatch == 4 else 0x13c4e)
            read_addresses = [item[1] for item in trace if item[0] == 'read']
            expected = [p+3, gp+232, p+5, p+7, p+9]
            expected += [gp+232+i for i in range(1, 4 if mismatch == 4 else mismatch+1)]
            self.assertEqual(read_addresses, expected)
            writes = [item for item in trace if item[0] == 'write']
            self.assertEqual(writes, [] if mismatch == 4 else [('write', gp+232+i, v) for i, v in enumerate(source)])
            self.assertEqual(updated, m.reference(p, gp, memory)[1])

    def test_shared_memory_and_wrap(self):
        for gp in (0xffffff70, 0x20004000):
            for delta in range(-12, 13):
                p = (gp + 232 + delta) & m.MASK
                addresses = {(p+k) & m.MASK for k in (3,5,7,9)} | {(gp+k) & m.MASK for k in range(232,236)}
                memory = {address: (address * 17 + delta) & 255 for address in addresses}
                self.assertEqual(m.run(m.CODE, p, gp, memory), m.reference(p, gp, memory))

    def test_semantic_mutants_even_when_identity_is_replaced(self):
        gp, p = 0x20004000, 0x20005000
        memory = {p + k: v for k, v in zip((3, 5, 7, 9), (1, 2, 3, 4))}
        memory.update({gp + 232 + i: v for i, v in enumerate((1, 2, 3, 4))})
        original = m.CODE
        try:
            # Replacing the identity pin is deliberate: the interpreter must
            # execute each changed word rather than merely compare a checksum.
            for offset, xor in ((0x14, 0x1000), (0x2c, 0x1000), (0x30, 1 << 20)):
                bad = bytearray(original)
                word = int.from_bytes(bad[offset:offset + 4], 'little') ^ xor
                bad[offset:offset + 4] = word.to_bytes(4, 'little')
                m.CODE = bytes(bad)
                case = dict(memory)
                if offset == 0x30:
                    case[gp + 232] ^= 1
                self.assertNotEqual(m.run(m.CODE, p, gp, case), m.reference(p, gp, case), hex(offset))
        finally:
            m.CODE = original

    def test_code_identity_and_unmapped_read(self):
        for offset in range(len(m.CODE)):
            bad = bytearray(m.CODE)
            bad[offset] ^= 1
            with self.assertRaises(ValueError):
                m.run(bad, 0, 0, {})
        with self.assertRaisesRegex(ValueError, 'unmapped'):
            m.run(m.CODE, 0, 0, {})


if __name__ == '__main__':
    unittest.main()
