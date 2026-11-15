#!/usr/bin/env python3
"""Bounded original-instruction model: 0x103ae to the next call or 0x103ca.

Models successful byte stores to synthetic ordinary RAM, with no asynchronous
changes. Stops before 0x167a6 and before unrelated code at 0x103ca. This is
not a CPU, provider, hardware, reachability, or whole-function proof.
"""
import hashlib
import caller_threshold_projection as prefix

SEGMENTS = {
    0x103ae: bytes.fromhex('15ef63fd87009307b00363f9a7008547238af1121305f009ef60003e'),
    0x103ea: bytes.fromhex('e3e087fe238a01121305e009c1bf'),
}
MASK = 0xffffffff


def verify_image(image):
    if hashlib.sha256(image).hexdigest() != prefix.SHA:
        raise ValueError('image identity')
    for address, data in SEGMENTS.items():
        if image[address - 0x8000:address - 0x8000 + len(data)] != data:
            raise ValueError('instruction identity')


def run(threshold, state, s0, gp):
    if not 0 <= threshold <= 255 or not 0 <= state <= 255:
        raise ValueError('byte input')
    r = [0] * 32
    r[3], r[8], r[10], r[14], r[15] = gp & MASK, s0 & MASK, threshold, state, threshold
    memory, events, pc = {(gp + 308) & MASK: state}, [], 0x103ae
    for _ in range(16):
        if pc == 0x103ca:
            return pc, None, memory, events
        section = next((base for base, data in SEGMENTS.items() if base <= pc < base + len(data)), None)
        if section is None:
            raise ValueError(f'unexpected pc {pc:#x}')
        data, off = SEGMENTS[section], pc - section
        half = int.from_bytes(data[off:off+2], 'little')
        if half & 3 != 3:
            if half == 0xef15:  # c.bnez a4, 0x103ea
                pc = 0x103ea if r[14] else pc + 2
            elif half == 0x4785:  # c.li a5, 1
                r[15], pc = 1, pc + 2
            elif half == 0xbfc1:  # c.j 0x103c6
                pc = 0x103c6
            else:
                raise ValueError('unsupported compressed instruction')
            continue
        word = int.from_bytes(data[off:off+4], 'little')
        op, rd, f3, rs1, rs2 = word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31
        if op == 0x63 and f3 in (6, 7):
            imm = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            if imm & 0x1000:
                imm -= 0x2000
            take = r[rs1] < r[rs2] if f3 == 6 else r[rs1] >= r[rs2]
            pc = (pc + (imm if take else 4)) & MASK
        elif op == 0x13 and f3 == 0:
            imm = word >> 20
            r[rd] = (r[rs1] + (imm - 4096 if imm & 2048 else imm)) & MASK
            pc += 4
        elif op == 0x23 and f3 == 0:
            imm = ((word >> 25) << 5) | ((word >> 7) & 31)
            addr = (r[rs1] + (imm - 4096 if imm & 2048 else imm)) & MASK
            value = r[rs2] & 255
            memory[addr] = value
            events.append(('write', addr, value))
            pc += 4
        elif op == 0x6f and pc == 0x103c6 and word == 0x3e0060ef:
            return pc, (0x167a6, r[10]), memory, events
        else:
            raise ValueError(f'unsupported instruction at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget')


def main():
    verify_image(prefix.BIN.read_bytes())
    count = 0
    for threshold in range(256):
        for s0 in range(256):
            for state in (0, 1, 255):
                gp = 0x20004000 if state != 255 else 0xfffffecc
                addr = (gp + 308) & MASK
                changed = (state == 0 and s0 > threshold and threshold > 59) or (state != 0 and s0 <= threshold)
                value = 1 if state == 0 else 0
                expected = ((0x103c6, (0x167a6, 159 if state == 0 else 158), {addr: value}, [('write', addr, value)])
                            if changed else (0x103ca, None, {addr: state}, []))
                if run(threshold, state, s0, gp) != expected:
                    raise ValueError((threshold, state, s0))
                count += 1
    print(f'PASS: {count} instruction-path / oracle cases')
    print('LIMIT: synthetic RAM; stops before provider or unrelated continuation')


if __name__ == '__main__':
    main()
