#!/usr/bin/env python3
"""155f6 guard and synthetic entry alias; successful byte RAM only, not a CPU."""
import unittest
import test_155d0_entry_order as entry
import test_155d0_machine as machine
import test_155e8_guard as previous

CODE = bytes.fromhex('83c7611691cb')
MASK = 0xffffffff


def guard(code, gp, mem):
    if len(code) != 6:
        raise ValueError('wrong window size')
    word = int.from_bytes(code[:4], 'little')
    if (word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31) != (3, 15, 4, 3):
        raise ValueError('unsupported load')
    imm = (word >> 20) & 4095
    imm -= 4096 if imm & 2048 else 0
    address = (gp + imm) & MASK
    value = mem[address]
    if code[4:] != b'\x91\xcb':
        raise ValueError('unsupported compressed branch')
    return value, 0x1560e if value == 0 else 0x155fc, address


class Guard(unittest.TestCase):
    def test_binary_identity(self):
        import hashlib
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        self.assertEqual(image[0x155f6 - 0x8000:0x155fc - 0x8000], CODE)

    def test_all_values_and_wrap(self):
        for gp in (0, 0x20004000, 0xffffff00):
            address = (gp + 358) & MASK
            for byte in range(256):
                mem = {address: byte}
                self.assertEqual(guard(CODE, gp, mem), (byte, 0x155fc if byte else 0x1560e, address))
                self.assertEqual(mem, {address: byte})
        with self.assertRaises(KeyError):
            guard(CODE, 0, {})

    def test_entry_stack_alias_changes_guard(self):
        # saved s2 is written to the later guard byte before that guard reads it.
        gp = 0x1000
        address = gp + 358
        sp = address + 16
        for flag in (0, 8):
            for saved in (0, 1, 0x100):
                mem = {0x3004: flag, address: 0x55}
                entry.store(mem, gp + 84, 0x3000)
                regs, pc = machine.run(entry.CODE, mem, gp, sp, 1, 2, 3, saved)
                if pc == 0x155e8:
                    # For a0 low byte 250 the intervening guard falls through.
                    self.assertEqual(previous.run(previous.CODE, 250)[2], 0x155f6)
                else:
                    self.assertEqual(pc, 0x155f6)
                value, target, observed = guard(CODE, gp, mem)
                self.assertEqual((value, observed), (saved & 255, address))
                self.assertEqual(target, 0x155fc if saved & 255 else 0x1560e)
                self.assertEqual(regs[2], sp - 16)

    def test_mutations(self):
        changed = bytearray(CODE)
        changed[2] ^= 0x10  # load offset 358 -> 359
        self.assertEqual(guard(changed, 0, {358: 0, 359: 1})[:2], (1, 0x155fc))
        changed = bytearray(CODE)
        changed[4] ^= 1
        with self.assertRaises(ValueError):
            guard(changed, 0, {358: 0})
        with self.assertRaises(ValueError):
            guard(CODE[:-1], 0, {})


if __name__ == '__main__':
    unittest.main()
