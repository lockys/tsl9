"""Run the V1.31 0x4efe2 leaf on all empty/occupied layouts (synthetic RAM)."""
import hashlib
import sys
from pathlib import Path


def check(ok):
    if not ok:
        raise ValueError('side-table check failed')


def run(image, mask, arg):
    base = 0x20003358
    ram = {base + 4*i: int(bool(mask & (1 << i))) for i in range(12)}
    r = [0]*32
    r[10] = arg
    writes = []
    pc = 0x4efe2
    for _ in range(100):
        off = pc - 0x40000
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 == 3:
            x = int.from_bytes(image[off:off+4], 'little')
            if x == 0x20003737: r[14] = 0x20003000
            elif x in (0x35870693, 0x35870713): r[(x >> 7) & 31] = r[14] + (x >> 20)
            elif x == 0xfec797e3:
                if r[15] != r[12]:
                    pc -= 18
                    continue
            else: raise ValueError(hex(pc))
            pc += 4
            continue
        if h == 0x4781: r[15] = 0
        elif h == 0x4631: r[12] = 12
        elif h == 0x428c: r[11] = ram[r[13]]
        elif h == 0xe591:
            if r[11]:
                pc += 12
                continue
        elif h == 0x078a: r[15] <<= 2
        elif h == 0x97ba: r[15] += r[14]
        elif h == 0xc388:
            check(r[15] in ram)
            ram[r[15]] = r[10]
            writes.append((r[15], r[10]))
        elif h == 0x4501: r[10] = 0
        elif h == 0x454d: r[10] = 19
        elif h == 0x0785: r[15] += 1
        elif h == 0x0691: r[13] += 4
        elif h == 0x8082: return r[10], writes
        else: raise ValueError(hex(pc))
        pc += 2
    raise ValueError('step budget')


if __name__ == '__main__':
    data = Path(sys.argv[1]).read_bytes()
    check(hashlib.sha256(data).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    for arg in (0x4f516, 0x4cff6):
        for mask in range(4096):
            i = next((i for i in range(12) if not mask & (1 << i)), None)
            expected = (19, []) if i is None else (0, [(0x20003358 + 4*i, arg)])
            check(run(data, mask, arg) == expected)
    print('PASS: 8192 layouts/arguments; first empty word only; full table returns 19')
