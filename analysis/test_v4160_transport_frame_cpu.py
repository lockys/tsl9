"""Original 8a56 transport framing; stop before all unknown service bodies.

Lookup services return explicitly chosen values preserving SP/S/GP and memory,
except one declared secondary-handle mutation probe. Event service is not run.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, STACK, RETURN, MASK, check

GP, BUFFER, STRIDE, SOURCE = 0x20004000, 0x2000b18c, 1062, 0x24000000
LOOKUP, POST = 0x30000200, 0x30000204
INITIAL_SP = STACK+0x800
S_REGS, S_VALUES = (8, 9, 18, 19), (0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00)
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class Transport(CPU):
    CODE_RANGES = ((0x8a56, 0x8b6e),)

    def __init__(self, image, handles, length):
        self.reads = []
        super().__init__(image, bytes(384))
        self.regions.extend(((GP+128, bytearray(32), True),
                             (BUFFER, bytearray([0xcc])*(STRIDE*2), True),
                             (SOURCE, bytearray((i*37+11) & 255 for i in range(max(1, min(length, 1040)))), False),
                             (0x4013c, bytearray(LOOKUP.to_bytes(4, 'little')), False),
                             (0x40050, bytearray(POST.to_bytes(4, 'little')), False)))
        self.reg[1], self.reg[2], self.reg[3] = RETURN, INITIAL_SP, GP
        for reg, value in zip(S_REGS, S_VALUES):
            self.reg[reg] = value
        for bank, handle in enumerate(handles):
            self.mem(GP+150+4*bank, 2, handle)
            self.mem(GP+148+4*bank, 1, 7+bank*4)
        self.query_calls = []
        self.writes.clear()

    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if value is None and (GP+128 <= address < GP+160 or
                              address in (0x4013c, 0x40050) or SOURCE <= address < SOURCE+1040):
            self.reads.append((address, size))
        return result


def run_case(image, handle, handles, replies, length, command=0xc0, fresh_second=None):
    c = Transport(image, handles, length)
    c.reg[10:14] = [handle, command, SOURCE, length]
    expected_calls, expected_bank, expected_return = [], None, handle
    expected_reads = []
    live_handles = list(handles)
    if length <= 1039:
        expected_reads.append((GP+150, 2))
        for bank in range(2):
            if bank == 1:
                expected_reads.append((GP+154, 2))
            if live_handles[bank] == handle and handle != 0xfffe:
                expected_reads.append((0x4013c, 4))
                expected_calls.append((0x8a90 if bank == 0 else 0x8ab6, handle, GP+128))
                expected_return = replies[bank]
                if bank == 0 and fresh_second is not None:
                    live_handles[1] = fresh_second
                if expected_return == 1:
                    expected_bank = bank
                    break
    pc = 0x8a56
    for _ in range(4):
        stop = c.run(pc, {LOOKUP, POST, RETURN}, budget=30000)
        if stop != LOOKUP:
            break
        resume, a0, a1 = c.reg[1], c.reg[10], c.reg[11]
        check(resume in (0x8a90, 0x8ab6), 'transport lookup continuation')
        bank = 0 if resume == 0x8a90 else 1
        c.query_calls.append((resume, a0, a1))
        if bank == 0 and fresh_second is not None:
            c.mem(GP+154, 2, fresh_second)
        for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
            c.put(reg, 0xcafe0000+reg*0x101)
        c.put(10, replies[bank])
        pc = resume
    else:
        raise RuntimeError('transport service budget')
    check(c.query_calls == expected_calls, 'transport lookup sequence')
    check(c.reg[1] == RETURN and c.reg[2] == INITIAL_SP and
          [c.reg[r] for r in S_REGS] == list(S_VALUES), 'transport restored caller')
    expected_buffer = bytearray([0xcc])*(STRIDE*2)
    if expected_bank is None:
        check(stop == RETURN and c.reg[10] == expected_return, 'transport reject return')
    else:
        check(stop == POST, 'transport event boundary')
        offset = expected_bank*STRIDE
        payload = bytes((i*37+11) & 255 for i in range(length))
        high, low = length >> 8, length & 255
        checksum = (command+high+low+sum(payload)) & 255
        expected_buffer[offset+2:offset+6] = (length+6).to_bytes(2, 'little')+bytes(2)
        expected_buffer[offset+6:offset+11] = bytes([0x55, 0x7f, command & 255, high, low])
        expected_buffer[offset+11:offset+11+length] = payload
        expected_buffer[offset+11+length] = checksum
        check(c.reg[10:13] == [7+4*expected_bank, 1, GP+148+4*expected_bank], 'transport tail service arguments')
        expected_reads += [(SOURCE+i, 1) for i in range(length)]
        expected_reads += [(0x40050, 4), (GP+148+4*expected_bank, 1)]
        buffer = BUFFER+offset
        stores = [(a, n, v) for a, n, v in c.writes if BUFFER <= a < BUFFER+STRIDE*2]
        expected_stores = [(buffer+6, 2, 0x7f55), (buffer+10, 1, low), (buffer+9, 1, high), (buffer+8, 1, command & 255)]
        expected_stores += [(buffer+11+i, 1, v) for i, v in enumerate(payload)]
        expected_stores += [(buffer+11+length, 1, checksum), (buffer+2, 2, length+6), (buffer+4, 2, 0)]
        check(stores == expected_stores, 'transport ordered frame stores')
    actual_buffer = next(data for base, data, _ in c.regions if base == BUFFER)
    check(c.reads == expected_reads, 'transport ordered data reads')
    check(actual_buffer == expected_buffer, 'transport whole buffer')
    if length > 1039:
        check(not c.writes, 'oversized transport touched memory')
    check(not c.calls, 'transport unknown service executed')
    return c


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'APP identity')
    cases = 0
    for handle in (0, 1, 0xfffd, 0xfffe, 0xffff, 0x10001, MASK):
        for match in range(4):
            handles = tuple(handle & 0xffff if match >> i & 1 else (handle+1) & 0xffff for i in range(2))
            for first in (0, 1, 2, MASK):
                for second in (0, 1, 2, MASK):
                    for length in (0, 8):
                        run_case(image, handle, handles, (first, second), length)
                        cases += 1
    for length in range(1040):
        handles = (0x123, 0x124) if length % 2 == 0 else (0x124, 0x123)
        run_case(image, 0x123, handles, (1, 1), length)
    for length in (1040, 0xffff, 0x10000, MASK):
        run_case(image, 0x123, (0x123, 0x123), (1, 1), length)
    for command in (0, 1, 0xff, 0x100, MASK):
        run_case(image, 0x123, (0x123, 0x124), (1, 0), 8, command)
    run_case(image, 0x123, (0x123, 0x124), (0, 1), 8, fresh_second=0x123)
    # Marker immediate mutation and an admission value mutation in memory only.
    for address, before, after, replies, message in (
        (0x8ae0, '134757f5', '134767f5', (1, 0), 'transport ordered frame stores'),
        (0x8a90, '8547', '8947', (2, 0), 'transport reject return'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'transport mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            run_case(mutant, 0x123, (0x123, 0x124), replies, 8)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected transport mutation failure')
        else:
            raise RuntimeError('transport mutation undetected')
    print(f'PASS: {cases} handle/admission cases; 1040 admitted lengths; 4 oversized lengths; 5 command probes; fresh secondary lookup; 2 mutations; unknown services NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
