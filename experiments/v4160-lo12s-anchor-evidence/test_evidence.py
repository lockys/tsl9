import struct
import unittest
import evidence as e


def fixture(relax_offsets=(0xe6,)):
    names = b'\0.shstrtab\0.text.tsl9v4160.handler_979e\0.rela.text\0.symtab\0.strtab\0'
    strings = b'\0anchor\0target\0'
    text = bytearray(0xee)
    struct.pack_into('<I', text, 0xe6, 0x00000797)
    struct.pack_into('<I', text, 0xea, 0x00f7a023)
    symbols = b'\0' * 16 + struct.pack('<IIIBBH', 1, 0xe6, 0, 0, 0, 2) + struct.pack('<IIIBBH', 8, 0, 0, 16, 0, 0)
    rel = struct.pack('<IIiIIi', 0xe6, (2 << 8) | 23, 0, 0xea, (1 << 8) | 25, 0)
    rel += b''.join(struct.pack('<IIi', off, 51, 0) for off in relax_offsets)
    data = bytearray(52)
    offsets = []
    for part in (names, text, rel, symbols, strings):
        offsets.append(len(data)); data.extend(part)
    shoff = len(data)
    sections = [(0,) * 10,
        (1, 3, 0, 0, offsets[0], len(names), 0, 0, 1, 0),
        (11, 1, 6, 0, offsets[1], len(text), 0, 0, 2, 0),
        (names.index(b'.rela.text'), 4, 0, 0, offsets[2], len(rel), 4, 2, 4, 12),
        (names.index(b'.symtab'), 2, 0, 0, offsets[3], len(symbols), 5, 2, 4, 16),
        (names.index(b'.strtab'), 3, 0, 0, offsets[4], len(strings), 0, 0, 1, 0)]
    for s in sections: data.extend(struct.pack('<10I', *s))
    struct.pack_into('<16sHHIIIIIHHHHHH', data, 0, b'\x7fELF\x01\x01\x01', 1, 243, 1, 0, 0, shoff, 0, 52, 0, 0, 40, 6, 1)
    return data, offsets, shoff

class Tests(unittest.TestCase):
    def test_synthetic_positive(self):
        d, _, _ = fixture()
        self.assertEqual(e.inspect(d)['hi_symbol'], 'target')

    def test_negative_matrix(self):
        for case in ('type24', 'type28', 'missing_hi', 'duplicate_hi', 'anchor_section', 'anchor_offset', 'hi_opcode', 'lo_opcode', 'rd', 'rs1', 'lo_addend', 'sym_index', 'sym_section', 'zero_rela_entsize', 'zero_sym_entsize', 'section_bounds', 'truncated', 'wrong_machine', 'string_bounds', 'instruction_bounds'):
            with self.subTest(case=case):
                d, o, sh = fixture()
                def put(off, val): struct.pack_into('<I', d, off, val)
                if case == 'type24': put(o[2]+16, 0x118)
                if case == 'type28': put(o[2]+4, 0x21c)
                if case == 'missing_hi': put(o[2], 0xe2)
                if case == 'duplicate_hi': put(o[2]+28, 0x217)
                if case == 'anchor_section': struct.pack_into('<H', d, o[3]+30, 1)
                if case == 'anchor_offset': put(o[3]+20, 0xe4)
                if case == 'hi_opcode': put(o[1]+0xe6, 0x13)
                if case == 'lo_opcode': put(o[1]+0xea, 0x13)
                if case == 'rd': put(o[1]+0xe6, 0x17)
                if case == 'rs1': put(o[1]+0xea, 0x00f72023)
                if case == 'lo_addend': put(o[2]+20, 1)
                if case == 'sym_index': put(o[2]+16, 0xffff19)
                if case == 'sym_section': struct.pack_into('<H', d, o[3]+46, 99)
                if case == 'zero_rela_entsize': put(sh+3*40+36, 0)
                if case == 'zero_sym_entsize': put(sh+4*40+36, 0)
                if case == 'section_bounds': put(sh+2*40+20, 0xffffffff)
                if case == 'truncated': del d[-1:]
                if case == 'wrong_machine': struct.pack_into('<H', d, 18, 3)
                if case == 'string_bounds': put(o[3]+16, 0xffffffff)
                if case == 'instruction_bounds': put(sh+2*40+20, 0xed)
                with self.assertRaises(e.Invalid): e.inspect(d)

    def test_narrow_format_mutations(self):
        for case in ('null_anchor', 'null_nonzero', 'global_anchor', 'local_after_boundary',
                     'sh_info_99', 'sh_info_zero', 'type51_sym',
                     'type51_addend', 'type51_only_hi', 'type51_only_lo',
                     'phnum', 'phoff', 'phentsize'):
            with self.subTest(case=case):
                d, o, sh = fixture()
                def put(off, val): struct.pack_into('<I', d, off, val)
                if case == 'null_anchor':
                    put(o[2]+16, 25)
                    put(o[3]+4, 0xe6)
                    struct.pack_into('<H', d, o[3]+14, 2)
                if case == 'null_nonzero': put(o[3]+8, 1)
                if case == 'global_anchor':
                    d[o[3]+28] = 16
                    put(sh+4*40+28, 1)
                if case == 'local_after_boundary': d[o[3]+44] = 0
                if case == 'sh_info_99': put(sh+4*40+28, 99)
                if case == 'sh_info_zero': put(sh+4*40+28, 0)
                if case == 'type51_sym': put(o[2]+28, 0x133)
                if case == 'type51_addend': put(o[2]+32, 1)
                if case == 'type51_only_hi': put(o[2]+4, 51)
                if case == 'type51_only_lo': put(o[2]+16, 51)
                if case == 'phnum': struct.pack_into('<H', d, 44, 1)
                if case == 'phoff': put(28, 52)
                if case == 'phentsize': struct.pack_into('<H', d, 42, 32)
                with self.assertRaises(e.Invalid): e.inspect(d)

    def test_duplicate_type51_at_each_selected_offset(self):
        for offset in (0xe6, 0xea):
            with self.subTest(offset=hex(offset)):
                d, _, _ = fixture((offset,))
                result = e.inspect(d)
                self.assertEqual((result['hi_offset'], result['lo_offset'], result['anchor'],
                                  result['hi_symbol'], result['rd_rs1']),
                                 (0xe6, 0xea, 'anchor', 'target', 15))
                d, _, _ = fixture((offset, offset))
                with self.assertRaisesRegex(e.Invalid, '^invalid type 51$'):
                    e.inspect(d)

    def test_hi_addend_is_preserved(self):
        d, o, _ = fixture(); struct.pack_into('<i', d, o[2]+8, -7)
        self.assertEqual(e.inspect(d)['hi_addend'], -7)

    def test_optional_local_evidence(self):
        if not e.OBJECT.exists() or not e.SOURCE.exists():
            self.skipTest('local untracked evidence unavailable; CLI fails closed')
        self.assertEqual(e.main(), 0)

    def test_pin_rejects_mismatch_and_missing(self):
        with self.assertRaises(e.Invalid): e.pinned(e.Path(__file__), '0' * 64)
        with self.assertRaises(e.Invalid): e.pinned(e.Path(__file__).parent / 'missing', '0' * 64)

if __name__ == '__main__': unittest.main()
