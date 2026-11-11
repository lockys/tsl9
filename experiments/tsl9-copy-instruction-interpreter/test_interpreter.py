import importlib.util
import pathlib
import os
import subprocess
import runpy
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
spec = importlib.util.spec_from_file_location('interpreter', HERE / 'interpreter.py')
i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)
copy = runpy.run_path(str(ROOT / 'scripts/rf_tx_copy_model.py'))['tx_copy']

class InterpreterTest(unittest.TestCase):
    def test_copy_against_existing_python_model(self):
        for dst, src, n in [(12, 24, 5), (13, 12, 5), (12, 13, 5), (12, 12, 5), (12, 24, 0)]:
            with self.subTest(dst=dst, src=src, n=n):
                initial = bytearray(range(64))
                # RF model writes its header before calling the copy helper.
                initial[dst-2:dst] = bytes((0xa5, n))
                m = i.Machine(initial, i.RAM+dst, i.RAM+src, n)
                m.run()
                memory = {i.RAM+k: v for k, v in enumerate(initial)}
                expected = copy(memory, i.RAM+dst-2, i.RAM+src, n, 0xa5)
                self.assertEqual(m.data, bytes(expected[i.RAM+k] for k in range(64)))
                self.assertEqual(m.mmio, 0x12345678)
                self.assertEqual(m.r[10:13], [i.RAM+dst, i.RAM+src, n])
                self.assertEqual(sum(e[0] == 'write8' for e in m.effects), n)
                self.assertEqual(m.effects[2], ('fence.i',))

    @unittest.skipUnless(os.environ.get('COPY_C_ORACLE'), 'set COPY_C_ORACLE to compiled c_oracle executable')
    def test_existing_c_reference(self):
        cases = [(i.RAM+12, i.RAM+24, 5, 0, 0),
                 (i.RAM+13, i.RAM+12, 5, 0, 0),
                 (i.RAM+12, i.RAM+13, 5, 0, 0),
                 (i.RAM+12, i.RAM+12, 5, 0, 0),
                 (i.RAM+12, i.RAM+24, 0, 0, 0),
                 (0, i.RAM+24, 5, 0, 0), (i.RAM+12, 0, 5, 0, 0),
                 (0, 0, 0, 0, 0),
                 (i.RAM+12, i.RAM+24, 5, i.RAM+26, 0),
                 (i.RAM+12, i.RAM+24, 5, 0, i.RAM+14),
                 (i.RAM+12, i.RAM+63, 2, 0, 0),
                 (i.RAM+63, i.RAM+24, 2, 0, 0)]
        # Bounded deterministic corpus: both overlap directions, self-copy and
        # disjoint ranges, plus a failure at every byte of each copy.
        for n in range(17):
            for delta in (-16, -4, -1, 0, 1, 4, 16):
                cases.append((i.RAM+24, i.RAM+24+delta, n, 0, 0))
            for pos in range(n):
                cases.append((i.RAM+24, i.RAM+20, n, i.RAM+20+pos, 0))
                cases.append((i.RAM+24, i.RAM+20, n, 0, i.RAM+24+pos))
        self.assertEqual(len(cases), 403)
        for dst, src, n, fail_read, fail_write in cases:
            with self.subTest(dst=dst, src=src, n=n, fail_read=fail_read, fail_write=fail_write):
                m = i.Machine(bytes(range(64)), dst, src, n,
                              unmapped_reads={fail_read}, unmapped_writes={fail_write})
                try:
                    m.run(); status = 'returned'
                except i.Halt as exc:
                    self.assertEqual(str(exc), 'unmapped data'); status = 'halt'
                lines = subprocess.check_output([os.environ['COPY_C_ORACLE'],
                    *map(str, (dst, src, n, fail_read, fail_write))], text=True, timeout=5).splitlines()
                events = [tuple([p[0]] + [int(x) for x in p[1:]])
                          for p in (line.split() for line in lines[:-3])]
                self.assertEqual(m.effects, events)
                fields = lines[-3].split()
                self.assertEqual(fields[1], status)
                if status == 'halt':
                    self.assertEqual(int(fields[2]), 3)  # RP_PROVIDER_STOP
                    self.assertEqual(int(fields[3]), m.pc - 4)
                    self.assertEqual(m.mmio, 0)
                else:
                    self.assertEqual(fields[2:], ['0', '0'])
                    self.assertEqual(m.mmio, 0x12345678)
                self.assertEqual(int(lines[-2].split()[1]), m.mmio)
                self.assertEqual(lines[-1], 'data ' + m.data.hex())

    def test_unknown_instruction_at_every_boundary(self):
        offset = 0
        boundaries = []
        while offset < len(i.BODY):
            boundaries.append(offset)
            offset += 2 if i.BODY[offset] & 3 != 3 else 4
        self.assertEqual(offset, len(i.BODY))
        self.assertEqual(len(boundaries), 18)
        for offset in boundaries:
            with self.subTest(offset=offset):
                code = bytearray(i.BODY)
                code[offset:offset+2] = b'\x00\x00'  # unsupported 16-bit encoding
                m = i.Machine(bytes(64), i.RAM, i.RAM, 1, code)
                m.pc = i.BASE + offset
                with self.assertRaisesRegex(i.Halt, 'unsupported instruction'):
                    m.run()
                self.assertEqual(m.effects, [])
                self.assertEqual(m.steps, 1)

    def test_hand_encoded_registers_and_offsets(self):
        def step(off, ins, width, registers):
            code = bytearray(i.BODY)
            code[off:off+width] = ins.to_bytes(width, 'little')
            m = i.Machine(bytes(range(64)), i.RAM, i.RAM, 1, code)
            for reg, value in registers.items(): m.r[reg] = value
            m.pc = i.BASE + off
            with self.assertRaisesRegex(i.Halt, 'budget'): m.run(1)
            return m
        # lbu x5,-3(x6); sb x5,7(x6)
        m = step(38, (0xffd << 20) | (6 << 15) | (4 << 12) | (5 << 7) | 3, 4, {6: i.RAM+10})
        self.assertEqual(m.r[5], 7)
        m = step(48, (5 << 20) | (6 << 15) | (7 << 7) | 0x23, 4, {5: 0x1ab, 6: i.RAM+10})
        self.assertEqual(m.data[17], 0xab)
        # lw x4,-4(x6); sw x5,-4(x6)
        m = step(4, (0xffc << 20) | (6 << 15) | (2 << 12) | (4 << 7) | 3, 4, {6: i.MMIO+4})
        self.assertEqual(m.r[4], 0x12345678)
        m = step(28, (0x7f << 25) | (5 << 20) | (6 << 15) | (2 << 12) | (28 << 7) | 0x23, 4, {5: 42, 6: i.MMIO+4})
        self.assertEqual(m.mmio, 42)
        # c.li x9,-1; c.addi x9,1; c.beqz x9,+8
        self.assertEqual(step(20, 0x54fd, 2, {}).r[9], 0xffffffff)
        self.assertEqual(step(46, 0x0485, 2, {9: 5}).r[9], 6)
        self.assertEqual(step(16, 0xc481, 2, {9: 0}).pc, i.BASE+24)
        code = bytearray(i.BODY); code[38:42] = ((1 << 20) | (6 << 15) | (4 << 12) | (5 << 7) | 3).to_bytes(4, 'little')
        m = i.Machine(bytes(8), i.RAM, i.RAM, 1, code); m.pc = i.BASE+38; m.r[6] = i.RAM+7
        with self.assertRaisesRegex(i.Halt, 'unmapped data'): m.run()

    def test_hand_encoded_control_and_alu(self):
        def run_one(off, ins, width, regs=None):
            code = bytearray(i.BODY)
            code[off:off+width] = ins.to_bytes(width, 'little')
            m = i.Machine(bytes(64), i.RAM, i.RAM, 1, code)
            m.pc = i.BASE + off
            for reg, value in (regs or {}).items(): m.r[reg] = value
            with self.assertRaisesRegex(i.Halt, 'budget'): m.run(1)
            return m
        # add x7,x8,x9; wrap at 32 bits, not a fixed helper expression.
        m = run_one(34, (9 << 20) | (8 << 15) | (7 << 7) | 0x33, 4, {8: 0xffffffff, 9: 3})
        self.assertEqual(m.r[7], 2)
        # bne x5,x6,-4 (and not taken); c.bnez x9,+8; c.j -2.
        bne = (1 << 31) | (0x3f << 25) | (6 << 20) | (5 << 15) | (1 << 12) | (14 << 8) | (1 << 7) | 0x63
        self.assertEqual(run_one(52, bne, 4, {5: 1, 6: 2}).pc, i.BASE+48)
        self.assertEqual(run_one(52, bne, 4, {5: 1, 6: 1}).pc, i.BASE+56)
        self.assertEqual(run_one(22, 0xe481, 2, {9: 1}).pc, i.BASE+30)
        self.assertEqual(run_one(22, 0xe481, 2, {9: 0}).pc, i.BASE+24)
        self.assertEqual(run_one(56, 0xbffd, 2).pc, i.BASE+54)
        # c.jr x5 uses the encoded register and clears target bit zero.
        code = bytearray(i.BODY); code[32:34] = (0x8282).to_bytes(2, 'little')
        m = i.Machine(bytes(64), i.RAM, i.RAM, 1, code); m.pc = i.BASE+32
        m.r[5] = i.RETURN_LINK | 1; m.run()
        m = i.Machine(bytes(64), i.RAM, i.RAM, 1, code); m.pc = i.BASE+32
        m.r[5] = i.RETURN_LINK - 2
        with self.assertRaisesRegex(i.Halt, 'unexpected return link'): m.run()
        # Wrong funct fields, link-form c.jalr, and noncanonical FENCE.I fail closed.
        for off, ins, width in [(34, 0x409403b3, 4), (52, bne ^ (1 << 12), 4),
                                (32, 0x9282, 2), (12, 0x0010100f, 4)]:
            code = bytearray(i.BODY); code[off:off+width] = ins.to_bytes(width, 'little')
            m = i.Machine(bytes(64), i.RAM, i.RAM, 1, code); m.pc = i.BASE+off
            with self.subTest(off=off), self.assertRaisesRegex(i.Halt, 'unsupported instruction'): m.run()
            self.assertEqual(m.effects, [])

    def test_control_flow_and_mapping_fail_closed(self):
        m = i.Machine(bytes(8), i.RAM, i.RAM, 0)
        m.pc = i.BASE + 2  # inside a valid 32-bit instruction
        with self.assertRaisesRegex(i.Halt, 'unmapped fetch'): m.run()
        m = i.Machine(bytes(8), i.RAM, i.RAM, 0)
        m.r[1] = i.BASE + 24
        with self.assertRaisesRegex(i.Halt, 'unexpected return link'): m.run()
        self.assertEqual(m.mmio, 0x12345678)
        # A valid RET transplanted to another site must not terminate execution.
        code = bytearray(i.BODY); code[16:18] = bytes.fromhex('8280')
        m = i.Machine(bytes(8), i.RAM, i.RAM, 0, code)
        with self.assertRaisesRegex(i.Halt, 'unsupported instruction'): m.run()
        for address in (i.RAM - 1, i.RAM + 8, -1, 1 << 32):
            with self.subTest(address=address):
                with self.assertRaisesRegex(i.Halt, 'unmapped data'):
                    m.byte_index(address, set())
        with self.assertRaises(ValueError):
            i.Machine(bytes(8), 1 << 32, i.RAM, 0)

    def test_negative(self):
        code = bytearray(i.BODY); code[0] ^= 4
        m = i.Machine(bytes(16), i.RAM, i.RAM, 1, code)
        with self.assertRaisesRegex(i.Halt, 'unsupported'): m.run()
        self.assertEqual(m.effects, [])
        m = i.Machine(bytes(16), i.RAM, i.RAM+16, 1)
        with self.assertRaisesRegex(i.Halt, 'unmapped data'): m.run()
        self.assertEqual(m.mmio, 0)  # no invented cleanup
        m = i.Machine(bytes(16), i.RAM, i.RAM, 1)
        with self.assertRaisesRegex(i.Halt, 'budget'): m.run(3)
        self.assertEqual(m.mmio, 0)
        m = i.Machine(bytes(16), i.RAM, i.RAM, 1, i.BODY[:2])
        with self.assertRaisesRegex(i.Halt, 'unmapped fetch'): m.run()

if __name__ == '__main__': unittest.main()
