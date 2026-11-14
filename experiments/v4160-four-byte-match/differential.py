import ctypes
import random
import sys
from machine import run
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
        machine, reads = run(code, data, config, trace=True)
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
    for length in (0, 1, 3, 5, 255, 0xffffffff):
        if run(code, fallback, configured, length, trace=True) != ('length', []): raise ValueError('length guard')
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
    print(f'PASS: {len(cases)} C vs original-byte-decoder comparisons and read traces; six wrong lengths read nothing; five byte mutants detected')


if __name__ == '__main__': main()
