"""Adversarial checks for the bounded slice, retaining checks under python -O."""
import unittest

from verify import CPU, GP, IMAGE, MASK, SP, check_image


class SliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = IMAGE.read_bytes()
        check_image(cls.image)

    def mutated(self, pc, value, width):
        data = bytearray(self.image)
        data[pc - 0x8000:pc - 0x8000 + width] = value.to_bytes(width, 'little')
        return data

    def test_identity_rejects_change(self):
        with self.assertRaises(ValueError):
            check_image(self.mutated(0xa14a, 0x00279713, 4))

    def test_instruction_shift_mutation_changes_address(self):
        # SLLI a4,a5,2 in place of SLLI a4,a5,1.
        cpu = CPU(self.mutated(0xa14a, 0x00279713, 4))
        self.assertEqual(cpu.run(), {'edge': 'read', 'address': 0x1ab58, 'width': 2})

    def test_branch_mutation_reaches_unequal_stop(self):
        # Invert the original BEQ at a0ea to BNE.
        w = int.from_bytes(self.image[0x20ea:0x20ee], 'little')
        cpu = CPU(self.mutated(0xa0ea, w ^ 0x1000, 4))
        self.assertEqual(cpu.run(), {'edge': 'unequal'})

    def test_terminal_load_mutation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'terminal LHU'):
            CPU(self.mutated(0xa158, 0x0007c783, 4)).run()

    def test_missing_data_fails(self):
        cpu = CPU(self.image)
        del cpu.memory[SP + 11]
        with self.assertRaisesRegex(ValueError, 'unmapped'):
            cpu.run()

    def test_budget_fails(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            CPU(self.image).run(budget=2)

    def test_invalid_input_rejected(self):
        for values in ({'counter': 256}, {'selector': -1}, {'x': 4096}):
            with self.assertRaises(ValueError):
                CPU(self.image, **values)

    def test_unsupported_opcode_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported RV32'):
            CPU(self.mutated(0xa14a, 0xffffffff, 4)).run()

    def test_unexpected_control_fails(self):
        cpu = CPU(self.image)
        cpu.pc = 0xa0d4
        with self.assertRaisesRegex(ValueError, 'unexpected instruction'):
            cpu.run()

    def test_register_wrap_and_zero(self):
        cpu = CPU(self.image)
        cpu.put(0, 123)
        cpu.put(5, MASK + 2)
        cpu.put(6, -1)
        self.assertEqual((cpu.r[0], cpu.r[5], cpu.r[6]), (0, 1, MASK))

    def test_little_endian_stack_and_leaf_reads(self):
        cpu = CPU(self.image)
        cpu.run()
        self.assertEqual(cpu.r[2:4], [SP, GP])
        self.assertIn((0x81fc, 0x2000beea, 1), cpu.reads)
        self.assertIn((0x81f2, 0x2000bed5, 1), cpu.reads)
        self.assertIn((0xa114, SP + 8, 4), cpu.reads)
        self.assertEqual(cpu.memory[GP + 176], 4)
        self.assertFalse(any(a == 0x1ab50 for _, a, _ in cpu.reads))

    def test_range_and_both_zero_edges(self):
        for x, edge in ((1960, 'exit'), (1961, 'read'), (2139, 'read'), (2140, 'exit')):
            self.assertEqual(CPU(self.image, x=x).run()['edge'], edge)
        for af, edge in ((0, 'exit'), (1, 'read'), (255, 'read')):
            self.assertEqual(CPU(self.image, aa=0, leaf=0, af=af).run()['edge'], edge)


if __name__ == '__main__':
    unittest.main()
