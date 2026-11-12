import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import verify as v


FIXED_EDGES = {
    0x18f06: (0x18f02, 15, 0, 'c.bnez'),
    0x18f10: (0x18f0c, 15, 0, 'c.bnez'),
    0x18f2e: (0x18f2a, 13, 0, 'c.bnez'),
    0x18f32: (0x18f1a, 15, 12, 'bne'),
    0x18f48: (0x18f44, 14, 0, 'c.bnez'),
}


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.IMAGE.read_bytes()

    def test_image_and_edges(self):
        self.assertEqual(v.EDGES, FIXED_EDGES)
        self.assertEqual(v.verify(self.data), v.WINDOW)
        for pc, expected in FIXED_EDGES.items():
            self.assertEqual(v.direct(pc, v.WINDOW[pc-v.START:]), expected)

    def test_mutations_and_truncations(self):
        start = v.START - 0x8000
        for i in range(len(v.WINDOW)):
            for bit in range(8):
                data = bytearray(self.data)
                data[start+i] ^= 1 << bit
                with self.subTest(byte=i, bit=bit), patch.object(v, 'PIN', hashlib.sha256(data).hexdigest()):
                    with self.assertRaisesRegex(ValueError, '^window mismatch$'):
                        v.verify(data)
        for n in (0, start, start+1, start+len(v.WINDOW)-1, len(self.data)-1):
            with self.assertRaises(ValueError):
                v.verify(self.data[:n])
        data = bytearray(self.data)
        data[0] ^= 1
        with self.assertRaises(ValueError):
            v.verify(data)

    def test_branch_field_mutations(self):
        # Instruction-bit -> signed displacement contribution. Sign bits have
        # negative weight; using the original bit gives the exact target delta.
        compressed_imm = {12: -256, 11: 16, 10: 8, 6: 128, 5: 64,
                          4: 4, 3: 2, 2: 32}
        branch_imm = {31: -4096, 7: 2048, 30: 1024, 29: 512,
                      28: 256, 27: 128, 26: 64, 25: 32,
                      11: 16, 10: 8, 9: 4, 8: 2}
        for pc, expected in FIXED_EDGES.items():
            compressed = expected[3] == 'c.bnez'
            size = 2 if compressed else 4
            raw = v.WINDOW[pc-v.START:pc-v.START+size]
            original = int.from_bytes(raw, 'little')
            imm_bits = compressed_imm if compressed else branch_imm
            fields = {bit: ('target', weight) for bit, weight in imm_bits.items()}
            fields.update({bit: ('rs1', 1 << (bit - (7 if compressed else 15)))
                           for bit in range(7, 10) if compressed})
            if not compressed:
                fields.update({bit: ('rs1', 1 << (bit-15)) for bit in range(15, 20)})
                fields.update({bit: ('rs2', 1 << (bit-20)) for bit in range(20, 25)})
            fields[13 if compressed else 12] = ('type', 0)
            fields[0 if compressed else 2] = ('opcode', 0)
            for bit, (field, value) in fields.items():
                with self.subTest(pc=hex(pc), field=field, bit=bit):
                    mutated = (original ^ (1 << bit)).to_bytes(size, 'little')
                    data = bytearray(self.data)
                    offset = pc - 0x8000
                    data[offset:offset+size] = mutated
                    window = data[v.START-0x8000:v.END-0x8000]
                    with patch.object(v, 'PIN', hashlib.sha256(data).hexdigest()), patch.object(v, 'WINDOW', bytes(window)):
                        message = 'not compressed branch|not supported direct edge' if field == 'opcode' else f'edge mismatch at {pc:#x}'
                        with self.assertRaisesRegex(ValueError, message):
                            v.verify(data)
                    if field == 'opcode':
                        with self.assertRaises(ValueError):
                            v.direct(pc, mutated)
                        continue
                    target, rs1, rs2, kind = expected
                    if field == 'target':
                        target += -value if original & (1 << bit) else value
                    elif field == 'rs1':
                        rs1 ^= value
                    elif field == 'rs2':
                        rs2 ^= value
                    else:
                        kind = 'c.beqz' if compressed else 'beq'
                    self.assertEqual(v.direct(pc, mutated), (target, rs1, rs2, kind))
                    self.assertNotEqual((target, rs1, rs2, kind), expected)

    def test_decoder(self):
        self.assertEqual(v.direct(0x100, bytes.fromhex('ef004000')), (0x104, 1, 0, 'jal'))
        self.assertEqual(v.direct(0x100, bytes.fromhex('eff0dfff')), (0xfc, 1, 0, 'jal'))
        for raw in (b'', b'\x63\x00', b'\x01\x00', b'\x73\x00\x00\x00'):
            with self.assertRaises(ValueError):
                v.direct(0, raw)

    def test_cli_missing(self):
        for opt in ([], ['-O']):
            with self.subTest(opt=opt):
                result = subprocess.run([sys.executable, '-B', *opt, str(Path(v.__file__))], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('OK: pinned image, fixed window, five direct branch edges', result.stdout)
                result = subprocess.run([sys.executable, '-B', *opt, str(Path(v.__file__)), str(v.IMAGE) + '.missing'], capture_output=True)
                self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
