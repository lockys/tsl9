"""Original 18ca4 handler against synthetic MMIO and record buffers only.
Optional dispatch composition uses the pinned SDK copy candidate, not installed ROM.
"""
import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, RETURN, MASK, check

HANDLER, MMIO, DATA = 0x18ca4, 0x40006400, 0x28000000
APP_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class TraceMemory:
    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if getattr(self, 'trace_active', False) and not BASE <= address < BASE+76800:
            if value is None and address == MMIO+8 and self.status_values is not None:
                result = next(self.status_values)
            self.effects.append(('r' if value is None else 'w', address, size,
                                 result if value is None else value & ((1 << (8*size))-1)))
        return result


class Peripheral(TraceMemory, CPU):
    CODE_RANGES = ((HANDLER, 0x18d78),)

    def __init__(self, image, record):
        super().__init__(image, bytes(384))
        self.regions.append((DATA, bytearray(record), True))
        self.reg = [0x11110000+i*0x101 for i in range(32)]
        self.reg[0], self.reg[1], self.reg[2] = 0, RETURN, 0x21000800
        self.reg[10:12] = [MMIO, DATA]


def initialize(c, status, r0=0xa5a55a5a, r1=0xc0decaff):
    c.regions.append((MMIO, bytearray((i*37+11) & 255 for i in range(512)), True))
    c.mem(MMIO+8, 4, status)
    for bank in range(3):
        c.mem(MMIO+0x180+16*bank, 4, r0)
        c.mem(MMIO+0x184+16*bank, 4, r1)
    c.writes.clear()


def record(mode=0):
    data = bytearray(range(32))
    data[0:4] = (0x01234567).to_bytes(4, 'little')
    data[4:8] = (0x89abcdef).to_bytes(4, 'little')
    data[8:11] = bytes([mode, 0x42, 0xa9])
    return data


def execute(c, status_plan=None):
    """Independent algebraic values plus explicit ordered data-access oracle."""
    regs = c.reg[:]
    target, source, resume = regs[10], regs[11], regs[1]
    check(target == MMIO, 'synthetic handler target')
    model = [(base, bytearray(data)) for base, data, _ in c.regions]
    expected = []
    def mem(address, size, value=None, override=None):
        for base, data in model:
            if base <= address and address+size <= base+len(data):
                offset = address-base
                if value is None:
                    result = int.from_bytes(data[offset:offset+size], 'little') if override is None else override
                    expected.append(('r', address, size, result))
                    return result
                value &= (1 << (size*8))-1
                data[offset:offset+size] = value.to_bytes(size, 'little')
                expected.append(('w', address, size, value))
                return
        raise RuntimeError('oracle unmapped access')
    bank = 4
    for index, bit in enumerate((26, 27, 28)):
        status = mem(target+8, 4, override=None if status_plan is None else status_plan[index])
        if status & (1 << bit):
            bank = index
            break
    if bank != 4:
        dest = target+0x180+bank*16
        low = mem(dest, 4) & 1
        mem(dest, 4, low)
        mode, raw = mem(source+8, 1), mem(source+9, 1)
        identifier = mem(source+(4 if mode else 0), 4)
        low = mem(dest, 4)
        header = ((identifier << (3 if mode else 21)) | raw | mode | low) & MASK
        mem(dest, 4, header)
        nibble = mem(source+10, 1) & 15
        mem(source+10, 1, nibble)
        upper = mem(dest+4, 4) & 0xfffffff0
        mem(dest+4, 4, upper)
        upper = mem(dest+4, 4)
        mem(dest+4, 4, upper | nibble)
        for offset, output in ((11, 8), (15, 12)):
            second, first = mem(source+offset+1, 1), mem(source+offset, 1)
            third, fourth = mem(source+offset+2, 1), mem(source+offset+3, 1)
            mem(dest+output, 4, first | second << 8 | third << 16 | fourth << 24)
        header = mem(dest, 4)
        mem(dest, 4, header | 1)
    c.effects, c.status_values = [], None if status_plan is None else iter(status_plan)
    c.trace_active = True
    mark = len(c.writes)
    check(c.run(HANDLER, {resume}) == resume, 'handler return edge')
    c.trace_active = False
    check(c.effects == expected, 'handler ordered data accesses')
    check(c.writes[mark:] == [(a, n, v) for kind, a, n, v in expected if kind == 'w'], 'handler exact stores')
    check(all(base == actual_base and data == actual for (base, data), (actual_base, actual, _) in zip(model, c.regions)),
          'handler full memory/canary')
    check(c.reg[10] == bank and c.reg[13] == bank, 'handler bank result')
    check(all(c.reg[i] == regs[i] for i in range(32) if i not in (10, 12, 13, 14, 15, 16)),
          'handler preserved registers')
    check(not c.calls, 'default provider unexpectedly executed')
    return bank


def standalone(image):
    counts = [0]*6
    noise = [0]+[1 << bit for bit in range(32) if bit not in (26, 27, 28)]
    def case(status, data=None, r0=0xa5a55a5a, r1=0xc0decaff, plan=None):
        c = Peripheral(image, record() if data is None else data)
        initialize(c, status, r0, r1)
        execute(c, plan)
    for selectors in range(8):
        for extra in noise:
            case(selectors << 26 | extra)
            counts[0] += 1
    for selectors in product(range(8), repeat=3):
        case(0, plan=tuple(value << 26 for value in selectors))
        counts[1] += 1
    for bank in range(3):
        status = 1 << (bank+26)
        for offset in (8, 9, 10):
            for value in range(256):
                data = record(1)
                data[offset] = value
                case(status, data)
                counts[2] += 1
        words = [0, MASK]+[1 << bit for bit in range(32)]
        for offset in (0, 4):
            for mode in (0, 1):
                for word in words:
                    data = record(mode)
                    data[offset:offset+4] = word.to_bytes(4, 'little')
                    case(status, data)
                    counts[3] += 1
        for offset in range(11, 19):
            for mode in (0, 1):
                for value in range(256):
                    data = record(mode)
                    data[offset] = value
                    case(status, data)
                    counts[4] += 1
        for field in (0, 1):
            for mode in (0, 1):
                for word in words:
                    values = [0xa5a55a5a, 0xc0decaff]
                    values[field] = word
                    case(status, record(mode), *values)
                    counts[5] += 1
    # With no selectable bank, no source dereference is allowed.
    c = Peripheral(image, record())
    initialize(c, 0)
    c.reg[11] = 0
    execute(c)
    for address, before, after in (
        (0x18ca6, '13975700', '13974700'),  # test bit27 in place of bit26
        (0x18cf4, '3d8b', '398b'),  # mask 14 instead of 15
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'handler mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            case_image = Peripheral(mutant, record())
            initialize(case_image, 1 << 26)
            execute(case_image)
        except RuntimeError as exc:
            check(str(exc) == 'handler ordered data accesses', 'unexpected handler mutation failure: '+str(exc))
        else:
            raise RuntimeError('handler mutation undetected')
    print('PASS: standalone selectors/volatile/meta/ID/payload/register cases '+str(counts)+
          '; null-source no-bank; 2 mutations; synthetic MMIO only')


def composition(image, carrier):
    from test_v4160_local_gate_dispatch import (LocalCPU, ROW, INITIAL_SP, STATE,
        SAVED_S0, GP, CONFIG, CARRIER_HASH, BODY_HASH, HW, DISPATCH, PROBE, RAM,
        CONTROL, CONTROL_INITIAL)
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'copy candidate identity')
    body = carrier[0x5a2:0x5dc]
    check(sha256(body).hexdigest() == BODY_HASH and carrier[0x4c:0x50] == (0x20000332).to_bytes(4, 'little'),
          'copy candidate body/slot')
    class Chained(TraceMemory, LocalCPU):
        CODE_RANGES = LocalCPU.CODE_RANGES+Peripheral.CODE_RANGES
    cases = handlers = 0
    for selectors, length, probe, ident, canary in product(range(8), range(9), (0, 1), (1, 0x123, 0xffff), (0, 0xcc)):
        c = Chained(image, body)
        c.regions[2][1][:] = bytes([canary])*0x1000
        c.reg[1], c.reg[2], c.reg[3], c.reg[8] = RETURN, INITIAL_SP, GP, SAVED_S0
        row = ident.to_bytes(2, 'little')+bytes([length, *range(0xa0, 0xa8), 0])
        c.mem(ROW, 12, int.from_bytes(row, 'little'))
        initialize(c, selectors << 26)
        c.reg[10] = ROW
        c.mem(STATE+1, 1, 0)
        c.mem(CONFIG+4, 1, 0)
        c.writes.clear()
        pc, probes, copies = DISPATCH, 0, 0
        for _ in range(4):
            stop = c.run(pc, {PROBE, RAM, HW, RETURN})
            if stop == PROBE:
                check(c.reg[1] == 0x12a14, 'composed probe continuation')
                for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                    c.put(reg, 0xcafe0000+reg*0x101)
                c.put(10, probe)
                probes += 1
                pc = 0x12a14
            elif stop == RAM:
                check(c.reg[10:13] == [INITIAL_SP-48+23, ROW+3, length], 'composed copy arguments')
                c.run_reference(0x12a50)
                copies += 1
                pc = 0x12a50
            else:
                break
        else:
            raise RuntimeError('composed dispatch budget')
        expected = HW if probe or ident == 1 else RETURN
        check(stop == expected and probes == 1 and copies == int(expected == HW), 'composed dispatch route')
        cases += 1
        if c.pc == HW:
            pointer = c.reg[11]
            check(c.reg[10] == MMIO and pointer == INITIAL_SP-48+12 and c.reg[1] == 0x12a5e,
                  'composed handler arguments/link')
            check(c.mem(pointer+8, 2) == 0 and c.mem(pointer+4, 4) == int.from_bytes(bytes([canary])*4, 'little'),
                  'dispatch mode zero and uninitialized hole')
            check(bytes(c.mem(pointer+11+i, 1) for i in range(8)) == bytes(range(0xa0, 0xa0+length))+bytes([canary])*(8-length),
                  'dispatch stale payload tail')
            bank = execute(c)
            check(c.run(0x12a5e, {RETURN}) == RETURN and c.reg[2] == INITIAL_SP and c.reg[8] == SAVED_S0 and c.reg[10] == bank,
                  'dispatch handler caller restoration/result')
            handlers += 1
        else:
            check(c.reg[2] == INITIAL_SP and c.reg[8] == SAVED_S0 and
                  c.writes == [(INITIAL_SP-8, 4, SAVED_S0), (INITIAL_SP-4, 4, RETURN)],
                  'rejected dispatch caller state')
        check(c.mem(ROW, 12) == int.from_bytes(row, 'little') and c.mem(CONTROL, 4) == CONTROL_INITIAL,
              'composed source/copy-control preserved')
    print(f'PASS: {cases} original dispatch routes; {handlers} handler/caller returns; two stack canaries; candidate-only copy binding')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone-only', action='store_true')
    parser.add_argument('--carrier', type=Path, default=Path(__file__).resolve().parent/'wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    standalone(image)
    if not args.standalone_only:
        composition(image, args.carrier.read_bytes())
