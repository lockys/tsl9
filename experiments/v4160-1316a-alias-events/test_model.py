import unittest
from model import BASE, MASK, IMAGE, Memory, check_image, check_window, events


class Tests(unittest.TestCase):
    def memory(self):
        m = Memory()
        for i, b in enumerate(bytes.fromhex('102030405060708090a0b0c0d0e0f000')):
            m.store(BASE + i, b, 1)
        m.store(0x40048, 0x1235, 4)
        m.store(0x4004c, 0xaaaa, 4)
        return m

    def test_binary_pin_and_mutations(self):
        data = IMAGE.read_bytes()
        check_image(data)
        for offset in (0x1316a - 0x8000, 0x13194 - 0x8000, 0x131a4 - 0x8000):
            mutant = bytearray(data)
            mutant[offset] ^= 1
            with self.assertRaises(ValueError):
                check_window(mutant)
            with self.assertRaises(ValueError):
                check_image(mutant)
        mutant = bytearray(data)
        mutant[0] ^= 1
        check_window(mutant)
        with self.assertRaises(ValueError):
            check_image(mutant)

    def test_overlap_and_callee_side_effects(self):
        # The callee changes both the later function slot and the pointer bytes.
        for addr, expected in ((BASE, 0x0fff2010), (BASE + 4, 0x80706001),
                               (BASE + 8, 0xc0b00101), (BASE + 12, 0x00f0e0d0)):
            with self.subTest(addr=hex(addr)):
                m = self.memory()
                m.store(addr, 0xdeadbeef, 4)
                def callee(mem):
                    # Install distinguishing pointer bytes before the direct stores.
                    for i, b in enumerate(bytes.fromhex('102030405060708090a0b0c0d0e0f000')):
                        mem.store(BASE + i, b, 1)
                    mem.store(0x4004c, 0x87654321, 4)
                result = events(m, (addr - 84) & MASK, callee)
                self.assertEqual(result, (0x1234, addr, expected, 0x87654320, (expected + 12) & MASK))

    def test_store_mutations_are_detected(self):
        # Each mutant changes one store or its endianness; literal oracles kill it.
        class Mutant(Memory):
            fault = None
            active = False
            def store(self, address, value, width):
                if self.active and (address, width) == self.fault[:2]:
                    if self.fault[2] == 'omit':
                        return
                    value = int.from_bytes(value.to_bytes(width, 'little'), 'big')
                super().store(address, value, width)
        for fault, addr, expected in [
            ((BASE + 2, 2, 'omit'), BASE, 0x0fff2010),
            ((BASE + 2, 2, 'endian'), BASE, 0x0fff2010),
            ((BASE + 4, 1, 'omit'), BASE + 4, 0x80706001),
            ((BASE + 8, 2, 'omit'), BASE + 8, 0xc0b00101),
        ]:
            m = Mutant()
            m.bytes.update(self.memory().bytes)
            m.fault = fault
            m.active = True
            self.assertNotEqual(events(m, addr - 84, lambda mem: None)[2], expected)

    def test_callee_changes_pointer_not_cached(self):
        m = self.memory()
        m.store(0x100, 0x11223344, 4)
        def callee(mem):
            mem.store(0x101, 0xaa, 1)
            mem.store(0x102, 0xbbcc, 2)
        self.assertEqual(events(m, 0xac, callee)[2], 0xbbccaa44)

    def test_order_and_byte_load_halfword_overlap(self):
        m = Memory()
        m.store(0xfffffffe, 0x1234, 2)
        self.assertEqual(m.load(0xffffffff, 1), 0x12)
        m.store(0xffffffff, 0xab, 1)
        self.assertEqual(m.load(0xfffffffe, 2), 0xab34)
        m.store(0xfffffffe, 0xcdef, 2)
        self.assertEqual(m.load(0xffffffff, 1), 0xcd)
        m.store(0x100000000, 0x89abcdef, 4)
        self.assertEqual(m.load(0, 4), 0x89abcdef)
        m.store(0xfffffffc, 0x01020304, 4)
        self.assertEqual(m.load(0x1fffffffc, 4), 0x01020304)
        with self.assertRaises(ValueError): m.load(1, 4)
        with self.assertRaises(ValueError): m.store(1, 0, 2)
        with self.assertRaises(ValueError): m.store(0, 256, 1)
        with self.assertRaises(KeyError): m.load(0x100, 1)

    def test_gp_read_failures_follow_stores(self):
        for gp, error in ((0xad, ValueError), (0xac, KeyError)):
            with self.subTest(gp=gp):
                m = self.memory()
                with self.assertRaises(error):
                    events(m, gp, lambda mem: None)
                self.assertEqual(m.load(BASE, 4), 0x0fff2010)
                self.assertEqual(m.load(BASE + 4, 4), 0x80706001)
                self.assertEqual(m.load(BASE + 8, 4), 0xc0b00101)

    def test_gp_and_pointer_addition_wrap(self):
        m = self.memory()
        m.store(0x20, 0xfffffffc, 4)
        self.assertEqual(events(m, (0x20 - 84) & MASK, lambda mem: None),
                         (0x1234, 0x20, 0xfffffffc, 0xaaaa, 8))


if __name__ == '__main__':
    unittest.main(verbosity=2)
