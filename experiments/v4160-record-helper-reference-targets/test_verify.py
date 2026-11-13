#!/usr/bin/env python3
"""Synthetic decoder and ledger tests, plus real pinned-input integration."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

module = importlib.util.spec_from_file_location('verify', Path(__file__).with_name('verify.py'))
v = importlib.util.module_from_spec(module)
module.loader.exec_module(v)


def word(n, width=4):
    return n.to_bytes(width, 'little')


def jal(d, rd=1):
    u = d & 0x1fffff
    return word(((u >> 20) & 1) << 31 | ((u >> 1) & 1023) << 21 | ((u >> 11) & 1) << 20 | ((u >> 12) & 255) << 12 | rd << 7 | 0x6f)


def branch(d, funct=0, rs1=1, rs2=2):
    u = d & 0x1fff
    return word(((u >> 12) & 1) << 31 | ((u >> 5) & 63) << 25 | rs2 << 20 | rs1 << 15 | funct << 12 | ((u >> 1) & 15) << 8 | ((u >> 11) & 1) << 7 | 0x63)


def cj(d, funct=5):
    u = d & 0xfff
    return word(funct << 13 | ((u >> 11) & 1) << 12 | ((u >> 4) & 1) << 11 | ((u >> 8) & 3) << 9 | ((u >> 10) & 1) << 8 | ((u >> 6) & 1) << 7 | ((u >> 7) & 1) << 6 | ((u >> 1) & 7) << 3 | ((u >> 5) & 1) << 2 | 1, 2)


def cb(d, funct=6, rs=0):
    u = d & 0x1ff
    return word(funct << 13 | ((u >> 8) & 1) << 12 | ((u >> 3) & 3) << 10 | rs << 7 | ((u >> 6) & 3) << 5 | ((u >> 1) & 3) << 3 | ((u >> 5) & 1) << 2 | 1, 2)


def pair(upper, lower, rd=10, rs=10, dest=10):
    return word((upper & 0xfffff000) | rd << 7 | 0x17) + word((lower & 0xfff) << 20 | rs << 15 | dest << 7 | 0x13)


def fixture():
    base = 0x1000
    image = jal(0x100) + jal(0xfc, 0) + pair(0, -16) + b'\x01\x00' * 4
    region = {'name': 'owner', 'start': base, 'end': base + len(image), 'bytes': len(image), 'original_sha256': v.digest(image)}
    refs = [dict(owner='owner', offset=o, PC=base+o, size=4, type=17, target='external', target_PC=0x1100) for o in (0, 4)]
    pairs = [dict(owner='owner', offset=8, PC=base+8, target='another', target_PC=0xff8, reference_kind='callback-address', data_contents_provided=False)]
    return {'regions': [region], 'controls': refs, 'PC_relative_pairs': pairs, 'undefined': ['external', 'another']}, image, base


class DecoderTests(unittest.TestCase):
    def test_jal_and_branch_displacements_and_registers(self):
        pc = 0x200000
        for d in (-1048576, -4098, -2, 0, 2, 4094, 1048574):
            for rd in (0, 1):
                self.assertEqual(v.decode_control(jal(d, rd), pc, 17), pc + d)
        for d in (-4096, -258, -2, 0, 2, 254, 4094):
            for funct in (0, 1, 4, 5, 6, 7):
                for rs in (0, 1, 31):
                    self.assertEqual(v.decode_control(branch(d, funct, rs, rs), pc, 16), pc + d)
        for invalid in (2, 3):
            with self.assertRaises(ValueError): v.decode_control(branch(4, invalid), pc, 16)
        for rd in (2, 5, 31):
            with self.assertRaises(ValueError): v.decode_control(jal(4, rd), pc, 17)
        for raw, kind in ((branch(2), 17), (jal(2), 16), (jal(2)[:2], 17), (b'\x7f\x00\x00\x00', 17)):
            with self.assertRaises(ValueError): v.decode_control(raw, pc, kind)

    def test_compressed(self):
        pc = 0x10000
        for d in (-2048, -258, -2, 0, 2, 254, 2046):
            self.assertEqual(v.decode_control(cj(d), pc, 45), pc+d)
        for d in (-256, -128, -2, 0, 2, 126, 254):
            for funct in (6, 7):
                for reg in range(8):
                    self.assertEqual(v.decode_control(cb(d, funct, reg), pc, 44), pc+d)
        for raw, kind in ((cj(2, 1), 45), (cb(2), 45), (cj(2), 44), (b'\x00\x00', 44), (cj(2), 99)):
            with self.assertRaises(ValueError): v.decode_control(raw, pc, kind)

    def test_exhaustive_short_immediates(self):
        pc = 0x20000
        for displacement in range(-4096, 4096, 2):
            self.assertEqual(v.decode_control(branch(displacement), pc, 16), pc + displacement)
        for displacement in range(-2048, 2048, 2):
            self.assertEqual(v.decode_control(cj(displacement), pc, 45), pc + displacement)
        for displacement in range(-256, 256, 2):
            self.assertEqual(v.decode_control(cb(displacement), pc, 44), pc + displacement)
        for bit in range(1, 21):
            for displacement in (1 << bit, -(1 << bit)):
                if -1048576 <= displacement <= 1048574:
                    self.assertEqual(v.decode_control(jal(displacement), 0x200000, 17), 0x200000 + displacement)

    def test_pair_signed_register_chain(self):
        for upper, low in ((0, -2048), (0, 2047), (0x1000, -1), (-0x1000, 1), (0x7ffff000, -2048), (-0x80000000, 2047)):
            pc = 0x80000000
            for reg in (1, 10, 31):
                self.assertEqual(v.decode_pair(pair(upper, low, reg, reg, reg), pc), pc + upper + low)
        for raw in (pair(0, 0, 10, 11), pair(0, 0, 10, 10, 11), pair(0, 0, 0, 0), pair(0, 0, 1, 1, 0), pair(0, 0)[:6], word(0x37) + pair(0, 0)[4:], pair(0, 0)[:4] + word(0x1013)):
            with self.assertRaises(ValueError): v.decode_pair(raw, 0x1000)

    def test_pc_change_and_overflow(self):
        for raw, kind in ((jal(2), 17), (branch(2), 16), (cj(2), 45), (cb(2), 44)):
            self.assertEqual(v.decode_control(raw, 0x1002, kind), v.decode_control(raw, 0x1000, kind)+2)
            with self.assertRaises(ValueError): v.decode_control(raw, 0xfffffffe, kind)
        with self.assertRaises(ValueError): v.decode_control(cj(-2), 0, 45)
        with self.assertRaises(ValueError): v.decode_pair(pair(0, -1), 0)
        with self.assertRaises(ValueError): v.decode_pair(pair(0, 2), 0xfffffffe)
        with self.assertRaises(ValueError): v.decode_pair(pair(0, 0), 1)
        for bad in (True, -1, 0x100000000):
            with self.assertRaises(ValueError): v.decode_control(jal(2), bad, 17)


def region(name, start, data):
    return dict(name=name, start=start, end=start + len(data), bytes=len(data), original_sha256=v.digest(data))


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.s, self.image, self.base = fixture()

    def check(self, s=None, image=None, counts=None):
        return v.validate_references(self.s if s is None else s, self.image if image is None else image, self.base, counts)

    def fail_mutation(self, mutate):
        s = copy.deepcopy(self.s)
        mutate(s)
        with self.assertRaises(ValueError): self.check(s)

    def test_success(self):
        result = self.check(counts=(1, 2, 1, 2))
        self.assertEqual(result['external_targets']['external'], {'address': 0x1100, 'count': 2, 'reference_PCs': [0x1000, 0x1004]})
        self.assertEqual(len(result['references']), 3)

    def test_missing_duplicate_extra(self):
        self.fail_mutation(lambda s: s['controls'].append(copy.deepcopy(s['controls'][0])))
        self.fail_mutation(lambda s: s['undefined'].append('extra'))
        self.fail_mutation(lambda s: s['undefined'].append('external'))
        self.fail_mutation(lambda s: s['undefined'].remove('external'))
        s = copy.deepcopy(self.s); s['controls'].pop()
        with self.assertRaises(ValueError): self.check(s, counts=(1, 2, 1, 2))
        self.fail_mutation(lambda s: s['regions'].append(copy.deepcopy(s['regions'][0])))

    def test_target_collisions_and_mismatch(self):
        def collide(s):
            s['controls'][1]['target'] = 'another'
            s['PC_relative_pairs'][0]['target'] = 'external'
            s['PC_relative_pairs'][0]['target_PC'] = 0xff8
        self.fail_mutation(collide)
        def collision(s):
            s['controls'][1]['target'] = 'third'
            s['undefined'].append('third')
        self.fail_mutation(collision)
        self.fail_mutation(lambda s: s['controls'][0].update(target_PC=0x1102))
        self.fail_mutation(lambda s: s['controls'][0].update(target='owner'))
        self.fail_mutation(lambda s: s['controls'][0].update(target='missing'))

    def test_entry_bounds_and_types(self):
        for field in ('offset', 'PC', 'size', 'type', 'target_PC'):
            self.fail_mutation(lambda s, f=field: s['controls'][0].update({f: True}))
        self.fail_mutation(lambda s: s['controls'][0].update(PC=0x1002))
        self.fail_mutation(lambda s: s['controls'][0].update(offset=2, PC=0x1002))
        self.fail_mutation(lambda s: s['controls'][0].update(offset=22, PC=0x1016))
        self.fail_mutation(lambda s: s['PC_relative_pairs'][0].update(data_contents_provided=0))
        self.fail_mutation(lambda s: s['controls'][0].update(extra=1))
        self.fail_mutation(lambda s: s['regions'][0].update(start=True))
        self.fail_mutation(lambda s: s['regions'][0].update(end=0x1020))
        def overlap(s):
            r = copy.deepcopy(s['regions'][0]); r['name'] = 'overlap'; s['regions'].append(r)
        self.fail_mutation(overlap)

    def test_internal_target_and_boundaries(self):
        image = jal(4, 0) + b'\x01\x00'
        first = dict(name='first', start=0x1000, end=0x1004, bytes=4, original_sha256=v.digest(image[:4]))
        second = dict(name='second', start=0x1004, end=0x1006, bytes=2, original_sha256=v.digest(image[4:]))
        ref = dict(owner='first', offset=0, PC=0x1000, size=4, type=17, target='second', target_PC=0x1004)
        spec = dict(regions=[first, second], controls=[ref], PC_relative_pairs=[], undefined=[])
        self.assertEqual(len(v.validate_references(spec, image, 0x1000)['references']), 1)
        ref['target'] = 'first'
        with self.assertRaises(ValueError): v.validate_references(spec, image, 0x1000)
        ref['target'] = 'outside'; spec['undefined'] = ['outside']
        with self.assertRaises(ValueError): v.validate_references(spec, image, 0x1000)

    def test_cross_region_fake_compressed_reference(self):
        # 0x1000 starts a 32-bit instruction; its high half looks like C.J.
        image = b'\x6f\x00' + cj(0)
        self.assertEqual(v.decode_control(image[2:], 0x1002, 45), 0x1002)
        spec = dict(regions=[region('first', 0x1000, image[:2]), region('second', 0x1002, image[2:])],
                    controls=[dict(owner='second', offset=0, PC=0x1002, size=2, type=45, target='second', target_PC=0x1002)],
                    PC_relative_pairs=[], undefined=[])
        with self.assertRaisesRegex(ValueError, 'crosses region boundary'):
            v.validate_references(spec, image, 0x1000)

    def test_mixed_width_groups_and_gap(self):
        first = cj(6) + jal(2)
        second = branch(-6) + cj(-10)
        third = cj(-14)
        image = first + second + b'\xff\xff' + third
        spec = dict(regions=[region('third', 0x100e, third), region('second', 0x1006, second), region('first', 0x1000, first)],
                    controls=[dict(owner='first', offset=0, PC=0x1000, size=2, type=45, target='second', target_PC=0x1006),
                              dict(owner='second', offset=0, PC=0x1006, size=4, type=16, target='first', target_PC=0x1000),
                              dict(owner='third', offset=0, PC=0x100e, size=2, type=45, target='first', target_PC=0x1000)],
                    PC_relative_pairs=[], undefined=[])
        result = v.validate_references(spec, image, 0x1000)
        self.assertEqual(result['assumed_boundary_groups'], [[0x1000, 0x100c], [0x100e, 0x1010]])
        self.assertEqual(len(result['references']), 3)

    def test_unreferenced_truncation_and_long_instruction(self):
        for raw, message in ((b'\x01\x00\x6f\x00', 'crosses region boundary'),
                             (b'\x01\x00\x1f\x00\x00\x00', 'unsupported instruction width')):
            spec = dict(regions=[region('first', 0x1000, raw)], controls=[], PC_relative_pairs=[], undefined=[])
            with self.assertRaisesRegex(ValueError, message):
                v.validate_references(spec, raw, 0x1000)

    def test_tampering_and_pins(self):
        with self.assertRaises(ValueError): self.check(image=bytes([self.image[0] ^ 1]) + self.image[1:])
        with self.assertRaises(ValueError): self.check(image=self.image[:-2])
        with self.assertRaises(ValueError): v.verify(b'{}', self.image)
        with self.assertRaises(ValueError): v.parse_spec(b'{"x":1,"x":2}')

    def test_real_input_and_image_tamper(self):
        spec, image = v.SPEC_PATH.read_bytes(), v.BIN_PATH.read_bytes()
        result = v.verify(spec, image)
        self.assertEqual(len(result['references']), 62)
        self.assertEqual(len(result['external_targets']), 18)
        self.assertEqual(result['jal_rd'], {'ra_x1_call': 16, 'x0_jump_no_link': 10})
        self.assertEqual(sum(x['count'] for x in result['external_targets'].values()), 35)
        with self.assertRaises(ValueError): v.verify(spec, image[:-1] + bytes([image[-1] ^ 1]))
        with self.assertRaises(ValueError): v.verify(spec + b' ', image)

    def test_runner_rejects_empty_selection_in_both_modes(self):
        for opt in ([], ['-O']):
            p = subprocess.run([sys.executable, '-I', '-S', '-B', *opt, str(Path(__file__)), '-k', 'no_such_test_9391'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn(b'no tests selected', p.stderr)

    def test_cli_failure_nonzero(self):
        for opt in ([], ['-O']):
            p = subprocess.run([sys.executable, '-I', '-S', '-B', *opt, str(v.Path(v.__file__)), '--spec', str(v.Path(v.__file__))], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertNotEqual(p.returncode, 0)
            self.assertNotIn(b'"passed"', p.stdout)


class NonemptyResult(unittest.TextTestResult):
    def stopTestRun(self):
        super().stopTestRun()
        if self.testsRun == 0:
            self.stream.writeln('ERROR: no tests selected')

    def wasSuccessful(self):
        return self.testsRun > 0 and super().wasSuccessful()


if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(resultclass=NonemptyResult))
