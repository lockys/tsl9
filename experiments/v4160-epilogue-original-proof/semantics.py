"""Bounded RV32C decoder for the pinned epilogue; successful loads only."""
import hashlib
import random
from verify import BIN, SHA, START, END, BASE

MASK = 0xffffffff


def execute(code, regs, memory):
    if len(code) % 2:
        raise ValueError('truncated instruction')
    regs = regs[:]
    reads = []
    pc = START
    for offset in range(0, len(code), 2):
        inst = int.from_bytes(code[offset:offset + 2], 'little')
        quadrant, funct3 = inst & 3, inst >> 13
        if quadrant == 2 and funct3 == 2:  # C.LWSP
            rd = (inst >> 7) & 31
            if rd == 0:
                raise ValueError('reserved C.LWSP')
            imm = (((inst >> 12) & 1) << 5) | (((inst >> 4) & 7) << 2) | (((inst >> 2) & 3) << 6)
            address = (regs[2] + imm) & MASK
            if address not in memory:
                raise ValueError('unmodelled load')
            reads.append(address)
            regs[rd] = memory[address]
        elif quadrant == 1 and funct3 == 3 and ((inst >> 7) & 31) == 2:  # C.ADDI16SP
            imm = (((inst >> 12) & 1) << 9) | (((inst >> 6) & 1) << 4) | (((inst >> 5) & 1) << 6) | (((inst >> 3) & 3) << 7) | (((inst >> 2) & 1) << 5)
            if imm == 0:
                raise ValueError('reserved C.ADDI16SP')
            regs[2] = (regs[2] + (imm - 1024 if imm & 512 else imm)) & MASK
        elif (inst & 0xf07f) == 0x8002:  # C.JR
            source = (inst >> 7) & 31
            if source == 0:
                raise ValueError('reserved C.JR')
            if offset != len(code) - 2:
                raise ValueError('early jump')
            pc = regs[source] & ~1
            return regs, reads, pc
        else:
            raise ValueError(f'unsupported instruction {inst:04x}')
        pc += 2
    raise ValueError('missing jump')


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    code = image[START-BASE:END-BASE]
    rng = random.Random(0x14098)
    for case in range(10000):
        regs = [rng.getrandbits(32) for _ in range(32)]
        regs[0] = 0
        regs[2] = [0, 0xffffffc0, rng.getrandbits(30) << 2][case % 3]
        original = regs[:]
        addresses = [(regs[2] + n) & MASK for n in (188, 184, 180, 176, 172)]
        memory = {address: rng.getrandbits(32) for address in addresses}
        actual, reads, pc = execute(code, regs, memory)
        expected = original[:]
        for register, address in zip((1, 8, 9, 18, 19), addresses):
            expected[register] = memory[address]
        expected[2] = (original[2] + 192) & MASK
        if actual != expected or reads != addresses or pc != (expected[1] & ~1):
            raise ValueError(f'semantic mismatch case {case}')
    # Distinct words expose wrong load offsets/registers; include alternate aligned
    # addresses so an erroneous C.LWSP is not rejected merely for missing data.
    regs = [0] * 32
    regs[2] = 0x1000
    memory = {0x1000 + offset: offset | 1 for offset in range(0, 256, 4)}
    reference = execute(code, regs, memory)
    for offset, bit in ((0, 0x10), (2, 0x80), (10, 0x04), (12, 0x80)):
        mutant = bytearray(code)
        mutant[offset] ^= bit
        try:
            result = execute(mutant, regs, memory)
        except ValueError:
            continue
        if result == reference:
            raise ValueError(f'mutation at byte {offset} survived')
    # Synthetic negative ADDI16SP followed by a return: 0x7101 is -512.
    negative, _, _ = execute(bytes.fromhex('01 71 82 80'), regs, memory)
    if negative[2] != (regs[2] - 512) & MASK:
        raise ValueError('negative ADDI16SP sign extension')
    for bad, bad_memory in ((b'\x82', memory), (bytes.fromhex('02 40 82 80'), memory),
                            (bytes.fromhex('01 61 82 80'), memory),
                            (bytes.fromhex('02 80'), memory), (code, {})):
        try:
            execute(bad, regs, bad_memory)
        except ValueError:
            continue
        raise ValueError('invalid or incomplete synthetic input accepted')
    print('PASS: 10000 decoded epilogue cases, SP wrap, negative immediate, 4 mutations and 5 invalid inputs')
    print('Synthetic successful aligned RAM reads only; no traps, interrupts or hardware execution.')


if __name__ == '__main__': main()
