"""A single RV32 AUIPC / S-store immediate pair, not an ELF linker."""

MASK32 = 0xffffffff
S_MASK = 0xfe000f80


def word(value):
    if not isinstance(value, int) or not 0 <= value <= MASK32:
        raise ValueError('instruction must be a 32-bit unsigned integer')
    return value


def signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def check_store(insn):
    word(insn)
    if insn & 0x7f != 0x23:
        raise ValueError('not an S-format integer store opcode')


def patch_s(insn, immediate):
    check_store(insn)
    if not isinstance(immediate, int) or not -2048 <= immediate <= 2047:
        raise ValueError('S immediate must fit signed 12 bits')
    value = immediate & 0xfff
    return (insn & ~S_MASK) | ((value >> 5) << 25) | ((value & 31) << 7)


def decode_s(insn):
    check_store(insn)
    return signed(((insn >> 25) << 5) | ((insn >> 7) & 31), 12)


def split_delta(hi_pc, target, addend=0):
    """Return encoded HI20 and signed LO12 after RV32 modular subtraction."""
    word(hi_pc)
    word(target)
    if not isinstance(addend, int):
        raise ValueError('addend must be an integer')
    delta = signed(target + addend - hi_pc, 32)
    hi = ((delta + 0x800) >> 12) & 0xfffff
    return hi, signed(delta, 12)


def patch_pair(auipc, store, hi_pc, target, addend=0):
    word(auipc)
    if auipc & 0x7f != 0x17:
        raise ValueError('HI instruction is not AUIPC')
    hi, lo = split_delta(hi_pc, target, addend)
    return (auipc & 0xfff) | (hi << 12), patch_s(store, lo)


def decode_target(auipc, store, hi_pc):
    word(auipc)
    word(hi_pc)
    if auipc & 0x7f != 0x17:
        raise ValueError('HI instruction is not AUIPC')
    return (hi_pc + signed(auipc & 0xfffff000, 32) + decode_s(store)) & MASK32
