"""Synthetic successful-access trace through gate, load and classifier models."""
import ctypes
import hashlib
import importlib.util
import random
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
cont = load('cont', 'differential.py')
cls = load('classifier', 'classification.py')

def main():
    image = cont.IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != cont.SHA:
        raise ValueError('firmware identity mismatch')
    w1 = image[0x148b4-0x8000:0x148de-0x8000]
    w2 = image[0x148d8-0x8000:0x1491a-0x8000]
    dll = ctypes.CDLL(sys.argv[1])
    dll.run_gate.argtypes = [ctypes.c_uint32, ctypes.c_uint32]; dll.run_gate.restype = ctypes.c_uint32
    dll.run_step.argtypes = [ctypes.POINTER(cont.Regs), ctypes.c_uint16, ctypes.POINTER(cont.Result)]; dll.run_step.restype = None
    dll.run_class.argtypes = [ctypes.POINTER(cls.Regs), ctypes.POINTER(cls.Result)]; dll.run_class.restype = None
    # Conditional predecessor witness: sentinel 0x0800 is nonzero, neither
    # dispatch-special halfword, and enters the classifier without a store.
    # This checks the examined static conditions, not call/ingress reachability.
    for pc, raw in ((0x14486, '9307000ce397f5c00547834704006318e934'),
                    (0x147e4, '1307f00f6399e712034714006315f712'),
                    (0x14800, '8357240005676384e70209676386e702'),
                    (0x1486a, '7919314648108145420982971359090113591900')):
        expected = bytes.fromhex(raw)
        if image[pc-0x8000:pc-0x8000+len(expected)] != expected:
            raise ValueError(f'predecessor bytes mismatch at {pc:#x}')
    values = [0x0800] + [0x1000] * 6 + [0x2000, 0x3001]
    payload = b'\xff\xff' + b''.join(v.to_bytes(2, 'little') for v in values)
    incoming_length = len(payload)
    bound = ((incoming_length - 2) & 0xffff) >> 1
    if incoming_length != 20 or bound != 9 or payload[:2] != b'\xff\xff' or values[0] in (0, 0x1000, 0x2000):
        raise ValueError('predecessor static constraints not met')
    state = cont.Regs(2047, 0, 0, 0, 0x10000, 0x2000, 0, 0)
    a4 = a5 = 0; writes = []; memory = {}
    for i, loaded in enumerate(values):
        if dll.run_gate(state.a2, len(values)) != 0x148b4:
            raise ValueError(f'gate ended before iteration {i}')
        decoded1 = cont.machine.run(w1, [getattr(state, n) for n in cont.NAMES], loaded)
        r1 = cont.Result(); dll.run_step(ctypes.byref(state), loaded, ctypes.byref(r1))
        actual1 = (tuple(getattr(r1.r, n) for n in cont.NAMES), r1.pc, r1.read_addr, r1.write_addr, r1.write_value, r1.wrote)
        if actual1 != decoded1 or r1.pc != 0x148de or r1.read_addr != 0x10000 + 2 * (i + 1):
            raise ValueError(f'continuation mismatch at {i}')
        current = cls.Regs(r1.r.a1, r1.r.a2, a4, a5, 0x1000, 0x2000, r1.r.sp, r1.r.t1, r1.r.t3)
        decoded2 = cls.class_machine.run(w2, [getattr(current, n) for n in cls.NAMES])
        r2 = cls.Result(); dll.run_class(ctypes.byref(current), ctypes.byref(r2))
        actual2 = (tuple(getattr(r2.r, n) for n in cls.NAMES), r2.pc, r2.write_addr, r2.write_value, r2.wrote)
        if actual2 != decoded2 or bool(r2.wrote) != (i != 0):
            raise ValueError(f'classifier mismatch at {i}')
        if r2.wrote:
            writes.append((r2.write_addr, r2.write_value))
            for j in range(2): memory[(r2.write_addr + j) & 0xffffffff] = (r2.write_value >> (8 * j)) & 255
        state = r1.r; state.a2 = r2.r.a2; state.t1 = r2.r.t1; state.t3 = r2.r.t3
        a4, a5 = r2.r.a4, r2.r.a5
    if dll.run_gate(state.a2, len(values)) != 0x14892 or (a4, a5) != (7, 1):
        raise ValueError('unexpected final loop/counters')
    if writes[-2:] != [(0x2024, 0x2000), (0x2024, 0x3001)] or (memory[0x2024], memory[0x2025]) != (1, 0x30):
        raise ValueError(f'expected synthetic overlapping writes, got {writes!r}')
    # Mixed synthetic traces cover the low-value store and all classifier routes.
    rng = random.Random(0x148de)
    route_counts = [0, 0, 0, 0]  # low, first mask, second mask, neither
    for sequence in range(128):
        state = cont.Regs(2047, 0, 0, 0, 0x10000, 0x2000, 0, 0)
        a4 = a5 = 0
        for i in range(32):
            if dll.run_gate(state.a2, 32) != 0x148b4:
                raise ValueError(f'mixed sequence {sequence}: premature gate exit')
            # Force each route while varying all non-routing data bits.
            kind = (sequence + i) % 4
            loaded = ((rng.randrange(2048)) if kind == 0 else
                      (0x1000 | rng.randrange(4096)) if kind == 1 else
                      (0x2000 | rng.randrange(4096)) if kind == 2 else
                      (0x0800 | rng.randrange(2048)))
            expected1 = cont.machine.run(w1, [getattr(state, n) for n in cont.NAMES], loaded)
            r1 = cont.Result(); dll.run_step(ctypes.byref(state), loaded, ctypes.byref(r1))
            actual1 = (tuple(getattr(r1.r, n) for n in cont.NAMES), r1.pc, r1.read_addr, r1.write_addr, r1.write_value, r1.wrote)
            if actual1 != expected1 or r1.read_addr != 0x10000 + 2 * (i + 1):
                raise ValueError(f'mixed sequence {sequence} continuation {i}')
            state = r1.r
            if kind == 0:
                if r1.pc != 0x1488e or not r1.wrote:
                    raise ValueError('expected low-value store')
            else:
                if r1.pc != 0x148de or r1.wrote:
                    raise ValueError('expected classifier entry')
                current = cls.Regs(state.a1, state.a2, a4, a5, 0x1000, 0x2000, state.sp, state.t1, state.t3)
                expected2 = cls.class_machine.run(w2, [getattr(current, n) for n in cls.NAMES])
                r2 = cls.Result(); dll.run_class(ctypes.byref(current), ctypes.byref(r2))
                actual2 = (tuple(getattr(r2.r, n) for n in cls.NAMES), r2.pc, r2.write_addr, r2.write_value, r2.wrote)
                if actual2 != expected2 or r2.wrote != (kind != 3):
                    raise ValueError(f'mixed sequence {sequence} classifier {i}')
                state.a2, state.t1, state.t3 = r2.r.a2, r2.r.t1, r2.r.t3
                a4, a5 = r2.r.a4, r2.r.a5
            route_counts[kind] += 1
        if dll.run_gate(state.a2, 32) != 0x14892 or (state.a3, a4, a5) != (8, 8, 8):
            raise ValueError(f'mixed sequence {sequence}: bad final counters')
    if route_counts != [1024] * 4:
        raise ValueError(f'missing mixed routes: {route_counts}')
    print('PASS: nine-step conditional predecessor witness and 128 mixed 32-step traces (1024 per route)')
if __name__ == '__main__': main()
