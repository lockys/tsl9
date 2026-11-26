"""Original 93aa leaf and 9454 -> 93aa composition, synthetic memory only.
Unknown free/allocate providers return explicitly supplied values; no device IO.
"""
from hashlib import sha256
from test_v4160_record_allocate_cpu import (Allocation, supply, GLOBAL, MAIN, AUX,
    HEAP, OLD, MMIO, FREE, ALLOC, APPLY, SP, S0, S1, IDENTITY)
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, RETURN, MASK, check

GP, CONFIG = 0x27000800, 0x26000000
FLAG, BYTE1, BYTE2 = GLOBAL+4, GLOBAL+5, GLOBAL+6


class Apply(Allocation):
    CODE_RANGES = ((0x93aa, 0x94ee),)

    def __init__(self, image, old=0, control=0xa5a4, config=0, flag=0):
        self.reads = []
        super().__init__(image, old, control)
        self.reg[3] = GP
        self.regions.extend(((GP+84, bytearray(CONFIG.to_bytes(4, 'little')), True),
                             (CONFIG, bytearray([0xcc, 0xcc, config, 0xcc]), True)))
        self.mem(FLAG, 1, flag)
        self.writes.clear()
        self.reads.clear()

    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if value is None and not BASE <= address < BASE+76800:
            self.reads.append((address, size))
        return result


def apply_leaf(c, config, flag, control):
    before_regs = c.reg[:]
    before = [(base, bytes(data)) for base, data, _ in c.regions]
    mark = len(c.writes)
    c.reads.clear()
    check(c.run(APPLY, {RETURN}) == RETURN, 'apply return')
    enabled = bool(config | flag)
    stores = [(BYTE2, 1, 0), (BYTE1, 1, 0), (GLOBAL, 4, 0),
              (MMIO+36, 2, 0), (MMIO, 2, control | 1)] if enabled else []
    check(c.writes[mark:] == stores, 'apply ordered stores')
    check(c.reads == [(GP+84, 4), (CONFIG+2, 1), (FLAG, 1)]+
          ([(MMIO, 2)] if enabled else []), 'apply exact reads')
    for (base, original), (same_base, actual, _) in zip(before, c.regions):
        check(base == same_base, 'apply region topology')
        expected = bytearray(original)
        for address, size, value in stores:
            if base <= address and address+size <= base+len(expected):
                expected[address-base:address-base+size] = value.to_bytes(size, 'little')
        check(actual == expected, 'apply memory/canary')
    check(all(c.reg[i] == before_regs[i] for i in range(32) if i not in (14, 15)),
          'apply preserved registers including A0/RA/SP')
    check(c.reg[14:16] == ([control | 1, 0x40000000] if enabled else [0, 0]),
          'apply scratch registers')
    check(not c.calls, 'actual provider executed')


def compose(image, parameter, old, success, config, flag):
    c = Apply(image, old, 0xa5a5, config, flag)
    c.reg[10] = parameter
    pc, calls = 0x9454, []
    for _ in range(3):
        stop = c.run(pc, {FREE, ALLOC, APPLY, RETURN})
        if stop not in (FREE, ALLOC):
            break
        resume = c.reg[1]
        calls.append((stop, c.reg[10], resume, c.reg[2]))
        supply(c, MASK if stop == FREE else (HEAP if success else 0))
        pc = resume
    else:
        raise RuntimeError('composed service budget')
    count = parameter+1 if parameter <= 19 else 2
    continuation = 0x9472 if parameter <= 19 else 0x94c2
    check(calls == ([(FREE, old, 0x942c, SP-32)] if old else [])+
          [(ALLOC, count*6, continuation, SP-16)], 'composed provider contract')
    check(stop == (APPLY if success else RETURN), 'composed apply reachability')
    check(c.reg[1] == RETURN and c.reg[2] == SP and c.reg[8:10] == [S0, S1],
          'composed caller restoration')
    check(c.mem(MAIN, 4) == (HEAP if success else 0) and
          c.mem(AUX, 4) == (0 if old else 0x12345678), 'composed pointers')
    check(c.mem(FLAG, 1) == flag and c.mem(CONFIG+2, 1) == config,
          'composed activation sources')
    check(not any(a in (GLOBAL, BYTE1, BYTE2, MMIO+36) for a, _, _ in c.writes),
          'apply effects before entry')
    if success:
        apply_leaf(c, config, flag, 0xa5a4 if old else 0xa5a5)
        check(c.reg[10] == HEAP, 'composed A0 remains provider pointer')
    else:
        check(c.reg[10] == 0, 'composed failed A0')
    return c


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'APP identity')
    for config in range(256):
        for flag in range(256):
            apply_leaf(Apply(image, config=config, flag=flag), config, flag, 0xa5a4)
    for control in range(65536):
        apply_leaf(Apply(image, control=control, config=1), 1, 0, control)
    for a0 in (0, 1, HEAP, MASK):
        for config, flag in ((0, 0), (1, 0), (0, 0x80), (0xff, 0xff)):
            c = Apply(image, config=config, flag=flag)
            c.reg[10] = a0
            apply_leaf(c, config, flag, 0xa5a4)
    for parameter in range(256):
        for old in (0, OLD):
            for success in (False, True):
                for config, flag in ((0, 0), (1, 0), (0, 0x80), (0xff, 0xff)):
                    compose(image, parameter, old, success, config, flag)
    # Both source reads are unconditional, even when the other byte is nonzero.
    c = Apply(image, flag=1)
    c.mem(GP+84, 4, 0)
    try:
        c.run(APPLY, {RETURN})
    except RuntimeError as exc:
        check(str(exc) == 'unmapped access 0x2 size 1', 'unexpected null-config failure')
    else:
        raise RuntimeError('invented null-config guard')
    for address, before, after, config, flag, message in (
        (0x93bc, 'd98f', 'dd8f', 1, 0, 'apply ordered stores'),  # ignore config byte
        (0x93e4, '13671700', '13672700', 1, 0, 'apply ordered stores'),  # bit 0 -> bit 1
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'apply mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            apply_leaf(Apply(mutant, config=config, flag=flag), config, flag, 0xa5a4)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected apply mutation failure: '+str(exc))
        else:
            raise RuntimeError('apply mutation undetected')
    print('PASS: 65536 activation pairs; 65536 control words; 16 A0 probes; '
          '4096 allocation/apply chains; null-config guard; 2 mutations; providers NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
