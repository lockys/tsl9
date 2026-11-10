"""Static source/HEX byte checks only. No target execution or device access."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOT = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
BASE = ROOT / 'analysis/wch-resident-candidate-2026-10-21'
SPECS = {
    'original-dec2023': ('11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5', 0x4b456, 0x4b2e4),
    'original': ('5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23', 0x4b4ee, 0x4b37c),
}
BOOT_BYTES = bytes.fromhex('03d7e107631ea702c167f917630af702b707040083a7c713411122c426c24ac006c6ae84938581063684328982978547e30cf5f2b240224492440249410182808280')
ENTRY = bytes.fromhex('411106c6eff0bfe809c52821b240410182800145e5bf')
HELPER = bytes.fromhex('b737002083c6573b814763e5d70001473a8582802e87910503d6c5ffe30aa6fe8507e5b7')


def parse_hex(raw):
    result, base, eof = {}, 0, False
    for line in raw.splitlines():
        if eof or not line.startswith(b':'):
            raise ValueError('invalid record order')
        b = bytes.fromhex(line[1:].decode('ascii'))
        if len(b) < 5 or len(b) != b[0] + 5 or sum(b) & 255:
            raise ValueError('invalid record')
        address, kind, data = int.from_bytes(b[1:3], 'big'), b[3], b[4:-1]
        if kind in (2, 4):
            if len(data) != 2 or address: raise ValueError('invalid base')
            base = int.from_bytes(data, 'big') << (4 if kind == 2 else 16)
        elif kind == 0:
            for i, value in enumerate(data):
                a = base + address + i
                if a in result and result[a] != value: raise ValueError('overlap')
                result[a] = value
        elif kind == 1:
            if data or address: raise ValueError('invalid EOF')
            eof = True
        elif kind not in (3, 5):
            raise ValueError('unsupported record')
    if not eof: raise ValueError('missing EOF')
    return result


def region(mem, addr, size):
    try: return bytes(mem[addr+i] for i in range(size))
    except KeyError as exc: raise ValueError('missing mapped byte') from exc


def gate_boot(data):
    if data[0x8ea:0x92c] != BOOT_BYTES: raise ValueError('BOOT caller mismatch')


def gate_resident(mem, entry, helper):
    if int.from_bytes(region(mem, 0x4013c, 4), 'little') != entry: raise ValueError('slot mismatch')
    if region(mem, entry, len(ENTRY)) != ENTRY: raise ValueError('entry mismatch')
    expected = HELPER if helper == 0x4b2e4 else HELPER[:7] + b'\x40' + HELPER[8:]
    if region(mem, helper, len(expected)) != expected: raise ValueError('helper mismatch')
    # JAL at entry+4, including signed immediate and destination register.
    w = int.from_bytes(region(mem, entry+4, 4), 'little')
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    if imm & (1 << 20): imm -= 1 << 21
    if w & 0xfff != 0xef or entry+4+imm != helper: raise ValueError('call mismatch')


class Evidence(unittest.TestCase):
    def test_boot_and_mutations(self):
        raw = BOOT.read_bytes()
        self.assertEqual(len(raw), 12288)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb')
        gate_boot(raw)
        for pc in (0x18ea, 0x18ee, 0x18f6, 0x18fa, 0x18fe, 0x190e, 0x1916, 0x1918, 0x191a, 0x1928):
            with self.subTest(pc=hex(pc)):
                mutant = bytearray(raw); mutant[pc-0x1000] ^= 1
                with self.assertRaises(ValueError): gate_boot(mutant)

    def test_candidate_rom_and_mutations(self):
        for name, (sha, entry, helper) in SPECS.items():
            raw = (BASE / name / 'wchble_rom.hex').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha)
            mem = parse_hex(raw)
            gate_resident(mem, entry, helper)
            for address in (0x4013c, entry+4, entry+8, entry+10, entry+18, helper, helper+4, helper+10, helper+24, helper+28):
                with self.subTest(candidate=name, address=hex(address)):
                    mutant = mem.copy(); mutant[address] ^= 1
                    with self.assertRaises(ValueError): gate_resident(mutant, entry, helper)


if __name__ == '__main__': unittest.main(verbosity=2)
