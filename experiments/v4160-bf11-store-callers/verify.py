#!/usr/bin/env python3
"""Offline, narrowly scoped RV32 instruction-window verifier; no execution."""
import hashlib
import json
import sys

BASE = 0x8000
SIZE = 76800
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0xbd46: bytes.fromhex('17050020 1305b51c 8280'),
    0xef5c: bytes.fromhex('efc0bfde 23000500'),
    0xf034: bytes.fromhex('efc03fd1 8547 2300f500'),
}


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def add_address(pc, delta):
    require(0 <= pc <= 0xffffffff, 'address outside RV32 range')
    result = pc + delta
    require(0 <= result <= 0xffffffff, 'address arithmetic overflow')
    return result


def decode(data, offset=0):
    """Decode only the instruction forms needed here; reject other encodings."""
    require(0 <= offset <= len(data) and len(data) - offset >= 2, 'truncated instruction')
    half = int.from_bytes(data[offset:offset + 2], 'little')
    if half & 3 != 3:
        # C.JR: funct4=1000, rs1 != x0, rs2=0, quadrant 2.
        if half & 0xf07f == 0x8002 and (half >> 7) & 31:
            return ('jr', (half >> 7) & 31, 2)
        # C.LI: funct3=010, rd != x0, quadrant 1.
        if half & 0xe003 == 0x4001 and (half >> 7) & 31:
            imm = ((half >> 2) & 31) | (((half >> 12) & 1) << 5)
            return ('li', (half >> 7) & 31, signed(imm, 6), 2)
        raise VerificationError('unsupported compressed instruction')
    require(half & 0x1f != 0x1f, 'unsupported instruction width')
    require(len(data) - offset >= 4, 'truncated instruction')
    w = int.from_bytes(data[offset:offset + 4], 'little')
    opcode = w & 0x7f
    rd, rs1, rs2 = (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31
    if opcode == 0x17:
        return ('auipc', rd, signed(w & 0xfffff000, 32), 4)
    if opcode == 0x13 and (w >> 12) & 7 == 0:
        return ('addi', rd, rs1, signed(w >> 20, 12), 4)
    if opcode == 0x6f:
        imm = (((w >> 31) & 1) << 20 | ((w >> 12) & 0xff) << 12 |
               ((w >> 20) & 1) << 11 | ((w >> 21) & 0x3ff) << 1)
        return ('jal', rd, signed(imm, 21), 4)
    if opcode == 0x23 and (w >> 12) & 7 == 0:
        imm = ((w >> 25) << 5) | ((w >> 7) & 31)
        return ('sb', rs2, rs1, signed(imm, 12), 4)
    raise VerificationError('unsupported instruction')


def sequence(data, pc):
    require(0 <= pc <= 0xffffffff and pc % 2 == 0, 'invalid instruction address')
    result = []
    offset = 0
    while offset < len(data):
        inst = decode(data, offset)
        address = add_address(pc, offset)
        add_address(address, inst[-1] - 1)
        result.append((address, inst))
        offset += inst[-1]
    return result


def verify_windows(windows):
    """Check semantics before byte identity, independently of input pinning."""
    require(set(windows) == set(WINDOWS), 'unexpected windows')
    for pc, expected in WINDOWS.items():
        require(len(windows[pc]) == len(expected), 'incorrect window length')
    a = sequence(windows[0xbd46], 0xbd46)
    require(len(a) == 3, 'BD46 instruction count')
    first, second, third = (x[1] for x in a)
    require(first[:2] == ('auipc', 10) and first[-1] == 4, 'BD46 auipc a0')
    require(second[:3] == ('addi', 10, 10) and second[-1] == 4, 'BD46 addi a0,a0')
    require(third == ('jr', 1, 2), 'BD46 c.jr ra')
    address = add_address(add_address(0xbd46, first[2]), second[3])
    require(address == 0x2000bf11, 'BD46 computed address')

    details = []
    for pc, value in ((0xef5c, 0), (0xf034, 1)):
        seq = sequence(windows[pc], pc)
        require(len(seq) == (2 if value == 0 else 3), 'caller instruction count')
        jal = seq[0][1]
        require(jal[0] == 'jal' and jal[1] == 1 and jal[-1] == 4, 'caller jal ra')
        target = add_address(pc, jal[2])
        require(target == 0xbd46 and jal[2] < 0, 'caller jal target/direction')
        if value:
            require(seq[1][1] == ('li', 15, 1, 2), 'caller c.li a5,1')
        require(seq[-1][1] == ('sb', 15 if value else 0, 10, 0, 4), 'caller sb')
        details.append({'pc': f'0x{pc:x}', 'jal_displacement': jal[2],
                        'jal_target': f'0x{target:x}', 'store_pc': f'0x{seq[-1][0]:x}',
                        'store_value': value})
    for pc, expected in WINDOWS.items():
        require(windows[pc] == expected, f'window bytes differ at 0x{pc:x}')
    return {'bd46_address': f'0x{address:x}', 'callers': details}


def read_pinned(path):
    with open(path, 'rb') as f:
        data = f.read(SIZE + 1)
    require(len(data) == SIZE, f'input must be exactly {SIZE} bytes')
    require(hashlib.sha256(data).hexdigest() == SHA256, 'input SHA-256 mismatch')
    return data


def verify_file(path):
    data = read_pinned(path)
    windows = {pc: data[pc - BASE:pc - BASE + len(expected)]
               for pc, expected in WINDOWS.items()}
    result = verify_windows(windows)
    return {'passed': True, 'size': len(data), 'sha256': SHA256,
            'base': f'0x{BASE:x}', **result}


def main(argv):
    try:
        require(len(argv) == 2, 'usage: python verify.py BIN')
        result = verify_file(argv[1])
    except (OSError, VerificationError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
