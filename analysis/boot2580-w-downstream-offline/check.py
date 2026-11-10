"""Pin the BOOT tail and independent resident event-slot candidates; no execution."""
import hashlib
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('provider', ROOT / 'analysis/boot2580-w-provider-offline/check.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
CASES = {
    'original-dec2023': (0x4354a, 'b747024083a6c72023a607200f100000373700200347d7196370e50237360020'),
    'original': (0x435d6, 'b747024083a6c72023a607200f100000373700200347d71e6370e50237360020'),
}
BOOT_SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
WRAPPER_SHA = 'e9e1e949d9ddde3636ccb3cbf144c7dfdff67c243aa7754fc24a59d4c832d5dd'

def boot_gate(data):
    if hashlib.sha256(data[0x848:0x92c]).hexdigest() != WRAPPER_SHA:
        raise ValueError('wrapper mismatch')

def resident_gate(mem, target, expected):
    if int.from_bytes(p.region(mem, 0x40050, 4), 'little') != target:
        raise ValueError('slot mismatch')
    if p.region(mem, target, 32) != bytes.fromhex(expected):
        raise ValueError('candidate entry mismatch')

class Evidence(unittest.TestCase):
    def test_boot(self):
        raw = p.BOOT.read_bytes()
        self.assertEqual(len(raw), 12288)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), BOOT_SHA)
        boot_gate(raw)
        for pc in (0x1852, 0x1868, 0x1874, 0x187e, 0x18a4, 0x18aa, 0x18b6, 0x18c6, 0x18ca, 0x18ce, 0x18d2, 0x1916, 0x191a):
            with self.subTest(pc=hex(pc)):
                mutant = bytearray(raw); mutant[pc - 0x1000] ^= 1
                with self.assertRaises(ValueError): boot_gate(mutant)

    def test_candidates(self):
        for name, (target, expected) in CASES.items():
            raw = (p.BASE / name / 'wchble_rom.hex').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), p.SPECS[name][0])
            mem = p.parse_hex(raw)
            resident_gate(mem, target, expected)
            for addr in (0x40050, 0x40051, target, target+4, target+8, target+12, target+16, target+20, target+24, target+28):
                with self.subTest(candidate=name, address=hex(addr)):
                    mutant = mem.copy(); mutant[addr] ^= 1
                    with self.assertRaises(ValueError): resident_gate(mutant, target, expected)

if __name__ == '__main__': unittest.main(verbosity=2)
