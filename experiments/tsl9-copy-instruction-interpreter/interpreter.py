"""Bounded RV32 subset interpreter for the retained candidate sites."""
import hashlib

BASE = 0x20000332
RAM = 0x20001000
MMIO = 0x4002420c
BODY = bytes.fromhex('b747024003a7c72023a607200f10000001c599c1814711e6b747024023a6e7208280b386f50003c80600b306f500850723800601e317f6fec5b7')
assert len(BODY) == 58 and hashlib.sha256(BODY).hexdigest() == '558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
MASK = 0xffffffff
# The entry return is a host sentinel, not an executable guest address.
RETURN_LINK = 0xfffffffe
BOUNDARIES = frozenset((0, 4, 8, 12, 16, 18, 20, 22, 24, 28, 32,
                        34, 38, 42, 46, 48, 52, 56))

# Each retained site admits only its original instruction class, not arbitrary
# control transfers. Register and immediate fields are decoded at runtime.
SITE = dict(zip(sorted(BOUNDARIES), ('lui', 'lw', 'sw', 'fence', 'beqz', 'beqz',
                                    'li', 'bnez', 'lui', 'sw', 'jr', 'add', 'lbu',
                                    'add', 'addi', 'sb', 'bne', 'j')))

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

class Halt(Exception):
    pass

class Machine:
    def __init__(self, data, dst, src, count, code=BODY, unmapped_reads=(), unmapped_writes=()):
        self.data = bytearray(data)
        if len(self.data) > MASK + 1 - RAM:
            raise ValueError('RAM mapping exceeds address space')
        if any(not isinstance(v, int) or not 0 <= v <= MASK for v in (dst, src, count)):
            raise ValueError('register value outside 32-bit address space')
        self.code = bytes(code)
        self.r = [0] * 32
        self.r[1] = RETURN_LINK
        self.r[10:13] = [dst, src, count]
        self.pc = BASE
        self.return_link = RETURN_LINK
        self.mmio = 0x12345678
        self.effects = []
        self.steps = 0
        self.unmapped_reads = set(unmapped_reads)
        self.unmapped_writes = set(unmapped_writes)

    def byte_index(self, address, unmapped):
        i = address - RAM
        if not 0 <= address <= MASK or address in unmapped or not 0 <= i < len(self.data):
            raise Halt('unmapped data')
        return i

    def run(self, budget=1000):
        while True:
            if self.steps >= budget:
                raise Halt('budget')
            off = self.pc - BASE
            if off not in BOUNDARIES or off + 2 > len(self.code):
                raise Halt('unmapped fetch')
            width = 2 if self.code[off] & 3 != 3 else 4
            if off + width > len(self.code):
                raise Halt('unmapped fetch')
            raw = self.code[off:off + width]
            ins = int.from_bytes(raw, 'little')
            self.steps += 1
            pc = self.pc
            self.pc += width
            r = self.r
            kind = None
            rd = (ins >> 7) & 31
            rs1 = (ins >> 15) & 31
            rs2 = (ins >> 20) & 31
            funct3 = (ins >> 12) & 7
            if width == 4:
                op = ins & 127
                if op == 0x37: kind = 'lui'
                elif op == 0x03 and funct3 in (2, 4): kind = {2: 'lw', 4: 'lbu'}[funct3]
                elif op == 0x23 and funct3 in (0, 2): kind = {0: 'sb', 2: 'sw'}[funct3]
                elif op == 0x33 and funct3 == 0 and ins >> 25 == 0: kind = 'add'
                elif op == 0x63 and funct3 == 1: kind = 'bne'
                elif ins == 0x100f: kind = 'fence'
            else:
                quadrant, f = ins & 3, ins >> 13
                if quadrant == 1 and f in (6, 7): kind = 'beqz' if f == 6 else 'bnez'
                elif quadrant == 1 and f == 2 and rd: kind = 'li'
                elif quadrant == 1 and f == 0 and rd: kind = 'addi'
                elif quadrant == 1 and f == 5: kind = 'j'
                elif quadrant == 2 and (ins & 0xf07f) == 0x8002 and rd: kind = 'jr'
            if kind != SITE[off]:
                raise Halt('unsupported instruction at %#x: %s' % (pc, raw.hex()))
            if kind == 'lui': r[rd] = ins & 0xfffff000
            elif kind in ('lw', 'lbu'):
                address = (r[rs1] + signed(ins >> 20, 12)) & MASK
                if kind == 'lw':
                    if address != MMIO or any(address + j in self.unmapped_reads for j in range(4)): raise Halt('unmapped word read')
                    r[rd] = self.mmio; self.effects.append(('read32', address, self.mmio))
                else:
                    value = self.data[self.byte_index(address, self.unmapped_reads)]
                    r[rd] = value; self.effects.append(('read8', address, value))
            elif kind in ('sw', 'sb'):
                imm = signed(((ins >> 25) << 5) | ((ins >> 7) & 31), 12)
                address = (r[rs1] + imm) & MASK
                if kind == 'sw':
                    if address != MMIO or any(address + j in self.unmapped_writes for j in range(4)): raise Halt('unmapped word write')
                    self.mmio = r[rs2]; self.effects.append(('write32', address, self.mmio))
                else:
                    value = r[rs2] & 255
                    self.data[self.byte_index(address, self.unmapped_writes)] = value
                    self.effects.append(('write8', address, value))
            elif kind == 'fence': self.effects.append(('fence.i',))
            elif kind == 'add': r[rd] = (r[rs1] + r[rs2]) & MASK
            elif kind == 'bne':
                imm = ((ins >> 31) << 12) | (((ins >> 7) & 1) << 11) | (((ins >> 25) & 63) << 5) | (((ins >> 8) & 15) << 1)
                if r[rs1] != r[rs2]: self.pc = pc + signed(imm, 13)
            elif kind in ('li', 'addi'):
                imm = signed(((ins >> 2) & 31) | (((ins >> 12) & 1) << 5), 6)
                r[rd] = (imm if kind == 'li' else r[rd] + imm) & MASK
            elif kind in ('beqz', 'bnez'):
                imm = (((ins >> 12) & 1) << 8) | (((ins >> 10) & 3) << 3) | (((ins >> 5) & 3) << 6) | (((ins >> 3) & 3) << 1) | (((ins >> 2) & 1) << 5)
                if (r[8 + ((ins >> 7) & 7)] == 0) == (kind == 'beqz'): self.pc = pc + signed(imm, 9)
            elif kind == 'j':
                imm = (((ins >> 12) & 1) << 11) | (((ins >> 11) & 1) << 4) | (((ins >> 9) & 3) << 8) | (((ins >> 8) & 1) << 10) | (((ins >> 7) & 1) << 6) | (((ins >> 6) & 1) << 7) | (((ins >> 3) & 7) << 1) | (((ins >> 2) & 1) << 5)
                self.pc = pc + signed(imm, 12)
            elif kind == 'jr':
                target = r[rd] & ~1
                if target != self.return_link: raise Halt('unexpected return link')
                self.pc = target
                return
            r[0] = 0
