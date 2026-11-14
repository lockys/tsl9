"""Instruction-step oracle against a compiled host model; no firmware execution."""
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('machine', HERE / 'machine.py')
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)
IMAGE = HERE.parents[1] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'

class Regs(ctypes.Structure):
    _fields_ = [(x, ctypes.c_uint32) for x in ('a0','a1','a2','a3','s0','sp','t1','t3')]

class Result(ctypes.Structure):
    _fields_ = [('r', Regs), ('pc', ctypes.c_uint32), ('read_addr', ctypes.c_uint32),
                ('write_addr', ctypes.c_uint32), ('write_value', ctypes.c_uint16), ('wrote', ctypes.c_int)]

NAMES = tuple(x[0] for x in Regs._fields_)
MASK = 0xffffffff

def oracle(values, loaded):
    # Each case corresponds to one instruction in the pinned 0x148b4 window.
    r = dict(zip(NAMES, values)); read_addr = write_addr = write_value = wrote = 0
    pc = 0x148b4
    while pc not in (0x148de, 0x1488e):
        if pc == 0x148b4: r['a2'] = (r['a2'] + 1) & MASK; pc += 2
        elif pc == 0x148b6: r['a1'] = (r['a2'] << 1) & MASK; pc += 4
        elif pc == 0x148ba: r['a1'] = (r['a1'] + r['s0']) & MASK; pc += 2
        elif pc == 0x148bc: read_addr = r['a1']; r['a1'] = loaded; pc += 4
        elif pc == 0x148c0: pc = 0x148de if r['a0'] < r['a1'] else pc + 4
        elif pc == 0x148c4: r['t1'] = (r['a3'] + 1) & MASK; pc += 4
        elif pc == 0x148c8: r['t3'] = (r['sp'] + 160) & MASK; pc += 4
        elif pc == 0x148cc: r['a3'] = (r['a3'] << 1) & MASK; pc += 2
        elif pc == 0x148ce: r['a3'] = (r['a3'] + r['t3']) & MASK; pc += 2
        elif pc == 0x148d0: write_addr = (r['a3'] - 112) & MASK; write_value = r['a1'] & 0xffff; wrote = 1; pc += 4
        elif pc == 0x148d4: r['a3'] = r['t1'] & 255; pc += 4
        elif pc == 0x148d8: r['a2'] &= 255; pc += 4
        elif pc == 0x148dc: pc = 0x1488e
        else: raise ValueError('unexpected instruction address')
    return tuple(r[n] for n in NAMES), pc, read_addr, write_addr, write_value, wrote

def main():
    firmware = IMAGE.read_bytes()
    if len(firmware) != 76800 or hashlib.sha256(firmware).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    window = firmware[0x148b4 - 0x8000:0x148de - 0x8000]
    # Check that two independent decoded immediates actually affect the result.
    sample = [5, 0, 0, 0, 0, 0, 0, 0]
    baseline = machine.run(window, sample, 5)
    altered_add = bytearray(window)
    altered_add[0:2] = bytes.fromhex('0906')  # C.ADDI a2, 2 instead of 1
    altered_load = bytearray(window)
    altered_load[11] ^= 1  # LHU immediate changes from 0 to 16
    if baseline[2] != 2 or machine.run(altered_add, sample, 5)[2] != 4 or machine.run(altered_load, sample, 5)[2] != 18:
        raise ValueError('decoded instruction immediate mutation not detected')
    invalid = bytearray(window)
    invalid[0:2] = b'\x00\x00'
    try:
        machine.run(invalid, [0] * 8, 0)
    except ValueError as exc:
        if str(exc) != 'unsupported compressed instruction 0x0 at 0x148b4':
            raise ValueError('invalid instruction was not rejected at the first PC') from exc
    else:
        raise ValueError('invalid instruction accepted')
    for bad_values, bad_loaded in (([0] * 7, 0), ([0] * 7 + [-1], 0), ([0] * 8, 65536)):
        try:
            machine.run(window, bad_values, bad_loaded)
        except ValueError:
            pass
        else:
            raise ValueError('invalid emulator input accepted')
    dll = ctypes.CDLL(sys.argv[1])
    dll.run_step.argtypes = [ctypes.POINTER(Regs), ctypes.c_uint16, ctypes.POINTER(Result)]
    dll.run_step.restype = None
    randomizer = random.Random(0x148b4)
    edge = (0, 1, 2, 0xfe, 0xff, 0x100, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff)
    inst = int.from_bytes(firmware[0x1488e - 0x8000:0x14892 - 0x8000], 'little')
    if (inst & 0x7f, (inst >> 12) & 7, (inst >> 15) & 31, (inst >> 20) & 31) != (0x63, 6, 12, 18):
        raise ValueError('unexpected loop-gate branch encoding')
    offset = (((inst >> 31) & 1) << 12 | ((inst >> 7) & 1) << 11 |
              ((inst >> 25) & 0x3f) << 5 | ((inst >> 8) & 0xf) << 1)
    if offset & 0x1000: offset -= 0x2000
    dll.run_gate.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    dll.run_gate.restype = ctypes.c_uint32
    for a2 in edge:
        for s2 in edge:
            expected_pc = (0x1488e + offset) if a2 < s2 else 0x14892
            if dll.run_gate(a2, s2) != expected_pc:
                raise ValueError(f'gate case a2={a2} s2={s2}')
    # Compose the gate and accepted-value continuation without modeling memory.
    # Each successful continuation masks a2 to a byte before returning to the gate.
    for bound in (*range(261), 0x7fff, 0xffff):
        state = Regs(2047, 0, 0, 0, 0x1000, 0x2000, 0, 0)
        for count in range(257):
            gate = dll.run_gate(state.a2, bound)
            if bound <= 255 and count == bound:
                if gate != 0x14892:
                    raise ValueError(f'loop bound {bound}: expected exit')
                break
            if gate != 0x148b4:
                raise ValueError(f'loop bound {bound}: unexpected exit at {count}')
            if count == 256:
                if state.a2 != 0 or state.a3 != 0:
                    raise ValueError(f'loop bound {bound}: expected masked counter cycle')
                break
            result = Result()
            dll.run_step(ctypes.byref(state), 0, ctypes.byref(result))
            if (result.pc != 0x1488e or not result.wrote or
                result.read_addr != 0x1000 + 2 * ((count & 255) + 1) or
                result.write_addr != 0x2000 + 48 + 2 * (count & 255) or
                result.r.a2 != ((count + 1) & 255) or result.r.a3 != ((count + 1) & 255)):
                raise ValueError(f'case loop bound {bound}: bad transition at {count}')
            state = result.r
    for i in range(20000 + 3 * 65536):
        if i < 20000:
            values = [randomizer.getrandbits(32) if i % 2 else randomizer.choice(edge) for _ in NAMES]
            loaded = randomizer.randrange(65536)
            if i % 4 == 0: values[0] = loaded
            elif i % 4 == 1 and loaded: values[0] = loaded - 1
        else:
            loaded, relation = divmod(i - 20000, 3)
            # Each LHU value with equality, lower (saturating at zero), and greater.
            values = [0, 0, edge[loaded % len(edge)], edge[(loaded // 3) % len(edge)],
                      0xfffffffe, 0xfffffff0, 0x12345678, 0x87654321]
            values[0] = (loaded if relation == 0 else max(0, loaded - 1) if relation == 1 else loaded + 1)
        actual = Result(); source = Regs(*values)
        dll.run_step(ctypes.byref(source), loaded, ctypes.byref(actual))
        got = (tuple(getattr(actual.r, n) for n in NAMES), actual.pc, actual.read_addr,
               actual.write_addr, actual.write_value, actual.wrote)
        expected = oracle(values, loaded)
        decoded = machine.run(window, values, loaded)
        if got != expected or got != decoded:
            raise ValueError(f'case {i}: inputs={values!r} loaded={loaded}, got={got!r}, manual={expected!r}, decoded={decoded!r}')
    print('PASS: 144 gate comparisons, 263 composed loop cases, 216608 continuation comparisons per language')

if __name__ == '__main__': main()
