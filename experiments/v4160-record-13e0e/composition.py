"""Conditional composition of independent bounded byte interpreters, not a CPU run."""
import hashlib
import importlib.util
from pathlib import Path
import random
from verify import BIN, SHA, FIRST, SECOND, run as record

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    predicate = load('predicate_machine', HERE.parent / 'v4160-four-byte-match/machine.py')
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    code = image[0x14122-0x8000:0x1417a-0x8000]
    rng = random.Random(0x13e0e)
    fallback = b'AaBb'
    counts = {'length': 0, 'mismatch': 0, 'first': 0, 'second': 0, 'none': 0}
    for i in range(6000):
        config = rng.randbytes(4)
        input_data = bytearray(rng.choice((fallback[j], config[j])) for j in range(4))
        length = 3 if i % 6 == 0 else 4
        if i % 6 == 1:
            input_data[0] = next(x for x in range(256) if x not in (fallback[0], config[0]))
        source_handle = rng.randrange(65536) if i % 6 != 5 else 0x10000 + rng.randrange(65536)
        predicate_result, _, regs, _ = predicate.run(code, bytes(input_data), config, length, state=True, handle=source_handle)
        if length != 4:
            if predicate_result != 'length': raise ValueError('length exit mismatch')
            counts['length'] += 1
            continue
        if i % 6 == 1:
            if predicate_result != 'mismatch': raise ValueError('mismatch exit mismatch')
            counts['mismatch'] += 1
            continue
        if predicate_result != 'match': raise ValueError('unexpected predicate exit')
        # Reconstruct state across the call boundary: the predicate interpreter
        # has not executed JAL, and no callback or provider body is run.
        handle = regs[10]
        if handle != source_handle or regs[11] != 1:
            raise ValueError('first-call argument mismatch')
        low = handle & 0xffff
        case = i % 6
        first, second = ((low, low), (low ^ 1, low), (low, low ^ 1), (low ^ 1, low ^ 1))[case - 2]
        reads, writes = record(image, handle, first, second, mode=1)
        if handle > 0xffff:
            expected_reads, expected_writes, label = [FIRST, SECOND], [], 'none'
        elif first == handle:
            expected_reads, expected_writes, label = [FIRST], [(FIRST+2, 1), (FIRST+3, 0)], 'first'
        elif second == handle:
            expected_reads, expected_writes, label = [FIRST, SECOND], [(SECOND+2, 1), (SECOND+3, 0)], 'second'
        else:
            expected_reads, expected_writes, label = [FIRST, SECOND], [], 'none'
        if (reads, writes) != (expected_reads, expected_writes): raise ValueError('record mismatch')
        counts[label] += 1
    if any(not n for n in counts.values()): raise ValueError(f'missing cases: {counts}')
    print(f'PASS: conditional predicate/record projections: {counts}')
    print('Call boundary reconstructed; no callback, provider, concurrency, reachability or hardware execution.')


if __name__ == '__main__': main()
