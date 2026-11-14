import ctypes
import random
import sys
from machine import run, sx
from verify import IMAGE, WINDOW


def main():
    code = IMAGE.read_bytes()[0x14122-0x8000:0x1417a-0x8000]
    if code != WINDOW: raise ValueError('instruction mismatch')
    dll = ctypes.CDLL(sys.argv[1])
    byte = ctypes.c_uint8
    dll.v4160_four_byte_match.argtypes = [ctypes.POINTER(byte), ctypes.POINTER(byte)]
    dll.v4160_four_byte_match.restype = ctypes.c_int
    rng = random.Random(0x14122)
    cases = []
    fallback = b'AaBb'
    configured = b'\x10\x20\x30\x40'
    for mask in range(16):
        base = bytes(fallback[i] if mask >> i & 1 else configured[i] for i in range(4))
        cases.append((base, configured))
        for i in range(4):
            for value in range(256):
                data = bytearray(base)
                data[i] = value
                cases.append((bytes(data), configured))
    for _ in range(1000):
        cases.append((rng.randbytes(4), rng.randbytes(4)))
    for index, (data, config) in enumerate(cases):
        c_result = dll.v4160_four_byte_match((byte*4).from_buffer_copy(data), (byte*4).from_buffer_copy(config))
        machine, reads, registers = run(code, data, config, state=True)
        if machine != ('match' if c_result else 'mismatch'):
            raise ValueError(f'differential mismatch at {index}')
        expected_reads = [(0x2054, 4)]
        for i in range(4):
            expected_reads.extend(((0x3000 + i, 1), (0x400c + i, 1)))
            if data[i] != config[i]:
                expected_reads.append((0x1030 + i, 1))
                if data[i] != fallback[i]:
                    break
        if reads != expected_reads:
            raise ValueError(f'read trace mismatch at {index}: {reads!r}')
        if machine == 'match' and (registers[10], registers[11]) != (0x1234abcd, 1):
            raise ValueError('first success-call arguments mismatch')
        if machine == 'mismatch' and (registers[11], registers[12]) != (168, 0):
            raise ValueError('failure-exit arguments mismatch')
    for length in (0, 1, 3, 5, 255, 0xffffffff):
        if run(code, fallback, configured, length, trace=True) != ('length', []): raise ValueError('length guard')
    for pc, expected in ((0x1416e, 0x13e0e), (0x14174, 0x13dd4)):
        word = int.from_bytes(code[pc-0x14122:pc-0x14122+4], 'little')
        if word & 127 != 0x6f or (word >> 7) & 31 != 1:
            raise ValueError(f'expected JAL ra at {pc:#x}')
        imm = ((word >> 31 & 1) << 20 | (word >> 12 & 255) << 12 |
               (word >> 20 & 1) << 11 | (word >> 21 & 1023) << 1)
        if (pc + sx(imm, 21)) & 0xffffffff != expected:
            raise ValueError(f'wrong JAL target at {pc:#x}')
    if code[0x14172-0x14122:0x14174-0x14122] != bytes.fromhex('01 45'):
        raise ValueError('second-call a0 setup mismatch')
    reference = run(code, fallback, configured, trace=True)
    for offset, bit in ((0x08, 1), (0x2a, 0x10), (0x36, 0x10), (0x42, 4), (0, 0xff)):
        mutated = bytearray(code)
        mutated[offset] ^= bit
        try:
            observed = run(mutated, fallback, configured, trace=True)
        except ValueError:
            continue
        if observed == reference:
            raise ValueError(f'instruction mutant at {offset:#x} survived')
    print(f'PASS: {len(cases)} C vs original-byte-decoder comparisons and read traces; six wrong lengths read nothing; first-call/failure arguments, two JAL targets and five byte mutants checked')


if __name__ == '__main__': main()
