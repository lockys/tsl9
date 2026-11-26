"""Original 9454/9410 allocation request and record initialization.
Free/allocate providers are synthetic normal returns; stop before 93aa apply.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, STACK, RETURN, MASK, check

GLOBAL, MAIN, AUX = 0x2000bebc, 0x2000becc, 0x2000bec8
HEAP, OLD, MMIO = 0x25000000, 0x25001000, 0x40000400
FREE, ALLOC, APPLY = 0x30000300, 0x30000304, 0x93aa
SP = STACK+0x800
S0, S1 = 0x11223344, 0x55667788
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class Allocation(CPU):
    CODE_RANGES = ((0x93ee, 0x94ee),)

    def __init__(self, image, old, control):
        super().__init__(image, bytes(384))
        self.regions.extend(((GLOBAL, bytearray([0xcc])*32, True),
                             (HEAP, bytearray([0xcc])*128, True),
                             (MMIO, bytearray([0xcc])*64, True),
                             (0x40068, bytearray(FREE.to_bytes(4, 'little')), False),
                             (0x40070, bytearray(ALLOC.to_bytes(4, 'little')), False)))
        self.reg[1], self.reg[2], self.reg[8], self.reg[9] = RETURN, SP, S0, S1
        self.mem(MAIN, 4, old)
        self.mem(AUX, 4, 0x12345678)
        self.mem(MMIO, 2, control)
        self.writes.clear()


def supply(c, value):
    for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
        c.put(reg, 0xcafe0000+reg*0x101)
    c.put(10, value)


def run_case(image, parameter, old, success, control=0xa5a5, free_reply=MASK):
    c = Allocation(image, old, control)
    c.reg[10] = parameter
    small = parameter <= 19
    count = parameter+1 if small else 2
    continuation = 0x9472 if small else 0x94c2
    pc, calls = 0x9454, []
    for _ in range(3):
        stop = c.run(pc, {FREE, ALLOC, APPLY, RETURN})
        if stop not in (FREE, ALLOC):
            break
        resume = c.reg[1]
        calls.append((stop, c.reg[10], resume, c.reg[2]))
        if stop == FREE:
            check(resume == 0x942c, 'free continuation')
            check(c.mem(MAIN, 4) == old and c.mem(AUX, 4) == 0x12345678 and c.mem(MMIO, 2) == control, 'free boundary state')
            supply(c, free_reply)
        else:
            check(resume == continuation and c.reg[2] == SP-16, 'allocation tail continuation/frame')
            check(c.mem(MAIN, 4) == 0 and c.mem(AUX, 4) == (0 if old else 0x12345678) and
                  c.mem(MMIO, 2) == (control & 0xfffe if old else control), 'allocation pre-provider state')
            supply(c, HEAP if success else 0)
        pc = resume
    else:
        raise RuntimeError('allocation service budget')
    expected_calls = ([(FREE, old, 0x942c, SP-32)] if old else [])+[(ALLOC, count*6, continuation, SP-16)]
    check(calls == expected_calls, 'allocation request order/size')
    check(stop == (APPLY if success else RETURN), 'allocation completion route')
    check(c.reg[1] == RETURN and c.reg[2] == SP and c.reg[8:10] == [S0, S1], 'allocation caller restoration')
    check(c.mem(MAIN, 4) == (HEAP if success else 0), 'allocation published pointer')
    check(c.mem(AUX, 4) == (0 if old else 0x12345678), 'allocation auxiliary clear')
    reset = [(MAIN, 4, 0), (AUX, 4, 0), (MMIO+44, 2, 0xffff),
             (MMIO+60, 2, 0), (MMIO, 2, control & 0xfffe)] if old else []
    observed = [(a, n, v) for a, n, v in c.writes if GLOBAL <= a < GLOBAL+32 or MMIO <= a < MMIO+64]
    check(observed == reset+[(MAIN, 4, HEAP if success else 0)], 'allocation reset/publish order')
    expected_heap, stores = bytearray([0xcc])*128, []
    def half(offset, value):
        expected_heap[offset:offset+2] = (value & 0xffff).to_bytes(2, 'little')
        stores.append((HEAP+offset, 2, value & 0xffff))
    if success:
        if small:
            for i in range(parameter):
                for offset, value in ((0, 3000), (2, 40), (4, 80)):
                    half(i*6+offset, value)
            half(parameter*6, 0)
        else:
            for offset, value in ((0, 3000), (2, parameter), (4, 0), (6, 0)):
                half(offset, value)
    actual_heap = next(data for base, data, _ in c.regions if base == HEAP)
    check(actual_heap == expected_heap and [(a, n, v) for a, n, v in c.writes if HEAP <= a < HEAP+128] == stores, 'allocation initialized records')
    check(not c.calls, 'actual provider executed')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'APP identity')
    cases = 0
    for parameter in range(256):
        for old in (0, OLD):
            for success in (False, True):
                run_case(image, parameter, old, success)
                cases += 1
    for parameter in (0x10000, 0x10001, MASK):
        for old in (0, OLD):
            for success in (False, True):
                run_case(image, parameter, old, success)
    for parameter in (0, 19, 20, 255):
        for control in (0, 1, 0xffff, 0xa5a5):
            run_case(image, parameter, OLD, True, control)
    for free_reply in (0, 1, MASK):
        run_case(image, 19, OLD, True, free_reply=free_reply)
    for address, before, after, parameter, message in (
        (0x943e, '1945', '1545', 0, 'allocation request order/size'),
        (0x9486, '13068002', '13069002', 1, 'allocation initialized records'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'allocation mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            run_case(mutant, parameter, 0, True)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected allocation mutation failure')
        else:
            raise RuntimeError('allocation mutation undetected')
    print(f'PASS: {cases} parameter/old-pointer/allocation cases; 12 full-width cases; 16 reset-word probes; 3 free-return probes; 2 mutations; providers/apply NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
