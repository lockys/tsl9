"""Host differential for the bounded 0x148de classifier; not a CPU emulator."""
import ctypes
import hashlib
import importlib.util
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RAW = bytes.fromhex('33f30501630d030013031700130e010a06077297231cb7f61377f30ff9bf33f31501e30c03fc13831700130e010a8607f2972392b7f89377f30fc1b7')
NAMES = ('a1','a2','a4','a5','a6','a7','sp','t1','t3')
MASK = 0xffffffff
spec = importlib.util.spec_from_file_location('class_machine', Path(__file__).resolve().parent / 'class_machine.py')
class_machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(class_machine)
class Regs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in NAMES]
class Result(ctypes.Structure):
    _fields_ = [('r', Regs), ('pc', ctypes.c_uint32), ('write_addr', ctypes.c_uint32), ('write_value', ctypes.c_uint16), ('wrote', ctypes.c_int)]

def oracle(values):
    r = dict(zip(NAMES, values)); address = value = wrote = 0
    # Sequential effects at the pinned instruction addresses, including priorities.
    r['t1'] = r['a1'] & r['a6']
    if r['t1']:
        old = r['a4']; r['t1'] = (old + 1) & MASK; r['t3'] = (r['sp'] + 160) & MASK
        intermediate = ((old << 1) + r['t3']) & MASK
        address = (intermediate - 136) & MASK
        value = r['a1'] & 65535; wrote = 1; r['a4'] = r['t1'] & 255
    else:
        r['t1'] = r['a1'] & r['a7']
        if r['t1']:
            old = r['a5']; r['t1'] = (old + 1) & MASK; r['t3'] = (r['sp'] + 160) & MASK
            intermediate = ((old << 1) + r['t3']) & MASK
            address = (intermediate - 124) & MASK
            value = r['a1'] & 65535; wrote = 1; r['a5'] = r['t1'] & 255
    r['a2'] &= 255
    return tuple(r[n] for n in NAMES), 0x1488e, address, value, wrote

def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA or image[0x148de-0x8000:0x1491a-0x8000] != RAW:
        raise ValueError('firmware identity or classifier bytes mismatch')
    window = image[0x148d8-0x8000:0x1491a-0x8000]
    sample = [0x1000, 0, 0, 0, 0x1000, 0x2000, 0x100, 0, 0]
    mutated = bytearray(window); mutated[0x148f2 - 0x148d8] ^= 0x80
    if class_machine.run(window, sample)[2] != 0x118 or class_machine.run(mutated, sample)[2] != 0x119:
        raise ValueError('store immediate mutation not detected')
    tail_mutant = bytearray(window); tail_mutant[2] ^= 0x10
    tail_sample = [0, 255, 0, 0, 0x1000, 0x2000, 0x100, 0, 0]
    if class_machine.run(window, tail_sample)[0][1] != 255 or class_machine.run(tail_mutant, tail_sample)[0][1] != 254:
        raise ValueError('tail mask mutation not detected')
    branch_mutant = bytearray(window); branch_mutant[0x148e2 - 0x148d8 + 1] ^= 1
    branch_sample = [0x2000, 0, 0, 0, 0x1000, 0x2000, 0x100, 0, 0]
    if not class_machine.run(window, branch_sample)[4] or class_machine.run(branch_mutant, branch_sample)[4]:
        raise ValueError('classifier branch target mutation not detected')
    jump_mutant = bytearray(window); jump_mutant[4] ^= 4
    try:
        class_machine.run(jump_mutant, tail_sample)
    except ValueError as exc:
        if str(exc) != 'PC outside classifier window: 0x1486e':
            raise ValueError('tail jump mutation failed for unexpected reason') from exc
    else:
        raise ValueError('tail jump mutation not detected')
    invalid = bytearray(window); invalid[6:8] = b'\x00\x00'
    try:
        class_machine.run(invalid, sample)
    except ValueError as exc:
        if str(exc) != 'unsupported compressed instruction 0x0 at 0x148de':
            raise ValueError('invalid classifier instruction not rejected at entry') from exc
    else:
        raise ValueError('invalid classifier instruction accepted')
    dll = ctypes.CDLL(sys.argv[1])
    dll.class_layout.argtypes = [ctypes.c_uint]; dll.class_layout.restype = ctypes.c_size_t
    layout = [ctypes.sizeof(Regs), ctypes.sizeof(Result)] + [getattr(Regs, n).offset for n in NAMES] + [getattr(Result, n).offset for n, _ in Result._fields_]
    if [dll.class_layout(i) for i in range(len(layout))] != layout:
        raise ValueError('classifier C/ctypes ABI layout mismatch')
    dll.run_class.argtypes = [ctypes.POINTER(Regs), ctypes.POINTER(Result)]; dll.run_class.restype = None
    rand = random.Random(0x148de)
    for i in range(20000 + 65536):
        if i < 20000:
            values = [rand.getrandbits(32) for _ in NAMES]
            # Exercise first, second, neither and simultaneous matches deliberately.
            a1 = values[0]
            mode = i % 4
            values[4] = 0 if mode in (1, 2) else a1
            values[5] = 0 if mode in (0, 2) else a1
        else:
            values = [i - 20000, 0xffffffff, 0xffffffff, 0xff, 0x1000, 0x2000, 0xfffffff0, 0x123, 0x456]
        src = Regs(*values); out = Result(); dll.run_class(ctypes.byref(src), ctypes.byref(out))
        got = tuple(getattr(out.r, n) for n in NAMES), out.pc, out.write_addr, out.write_value, out.wrote
        expected = oracle(values)
        decoded = class_machine.run(window, values)
        if got != expected or got != decoded:
            raise ValueError(f'case {i}: values={values!r}, got={got!r}, expected={expected!r}, decoded={decoded!r}')
    print('PASS: classifier 85536 host comparisons with manual and byte-decoding oracles')
if __name__ == '__main__': main()
