"""Original 82d2 filter, candidate copy and consumer return-branch composition.

8a56 stops at its boundary and gets an explicit synthetic normal return. Table,
snapshot, candidate binding and MMIO/CSR models are not installed-device proof.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_reference_copy_cpu import ReferenceCPU, CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL, CONTROL_INITIAL
from test_v4160_consumer_detach_cpu import Consumer, fixture, CALLBACK, FRAME_SP, S_REGS, S_VALUES
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, STACK, RETURN, MASK, check

TABLE, REQUEST = 0x2000c794, 0x8a56
SNAPSHOT, ENTRY_SP = STACK+0x300, STACK+0x800
FILTER_S = (8, 9, *range(18, 26))
FILTER_VALUES = tuple(0x12340000+i*0x101 for i in range(10))


def table_bytes(nodes):
    data = bytearray([0xcc]*10)
    for i, (handle, kind, flag) in enumerate(nodes):
        data[4*i+2:4*i+4] = handle.to_bytes(2, 'little')
        data[4*i+4], data[4*i+5] = flag, kind
    return data


def prediction(nodes, snapshot, sp):
    result, requests = 0, []
    ident, length, tag = int.from_bytes(snapshot[:2], 'little'), snapshot[2], snapshot[11]
    packet = bytes([((ident >> 8) | (tag << 4)) & 255, ident & 255])+snapshot[3:3+length]
    for handle, kind, flag in nodes:
        if handle == 0xfffe or kind != 2 or flag == 0:
            continue
        result = flag  # This assignment precedes the original length guard.
        if length <= 8:
            requests.append(([handle, 0xc0, sp-64+4, length+2], packet))
    return result, requests


def execute_filter(c, reply=MASK):
    resume = c.reg[1]
    pc = CALLBACK
    c.requests, c.filter_copies = [], []
    for _ in range(12):
        stop = c.run(pc, {RAM, REQUEST, resume})
        if stop == resume:
            return
        if stop == RAM:
            arguments = c.reg[10:13].copy()
            c.run_reference(0x8358)
            c.filter_copies.append((arguments, tuple(c.effects)))
            pc = 0x8358
        else:
            args = c.reg[10:14].copy()
            payload = c.mem(args[2], args[3]).to_bytes(args[3], 'little')
            c.requests.append((args, payload))
            pc = c.reg[1]
            for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                c.put(reg, 0xcafe0000+reg*0x101)
            c.put(10, reply)
    raise RuntimeError('filter budget exceeded')


class FilterCPU(ReferenceCPU):
    CODE_RANGES = ((RAM, RAM+58), (0x82d2, 0x838e))


class FilterConsumer(Consumer):
    CODE_RANGES = Consumer.CODE_RANGES+((0x82d2, 0x838e),)


def standalone(image, body, nodes, length, ident=0x123, tag=2, reply=MASK):
    c = FilterCPU(image, body)
    c.regions.append((TABLE, table_bytes(nodes), True))
    c.reg[1], c.reg[2], c.reg[10] = RETURN, ENTRY_SP, SNAPSHOT
    for reg, value in zip(FILTER_S, FILTER_VALUES):
        c.reg[reg] = value
    snapshot = ident.to_bytes(2, 'little')+bytes([length, *range(0xa0, 0xa8), tag])
    c.mem(SNAPSHOT, 12, int.from_bytes(snapshot, 'little'))
    expected_result, expected_requests = prediction(nodes, snapshot, ENTRY_SP)
    execute_filter(c, reply)
    check(c.reg[10] == expected_result, 'filter sticky result')
    check(c.requests == expected_requests, 'filter request packet')
    check(len(c.filter_copies) == len(expected_requests), 'filter copy count')
    for (args, effects), _ in zip(c.filter_copies, expected_requests):
        check(args == [ENTRY_SP-64+6, SNAPSHOT+3, length] and len(effects) == 4+2*length, 'filter candidate copy boundary')
    check(c.reg[1] == RETURN and c.reg[2] == ENTRY_SP and
          [c.reg[r] for r in FILTER_S] == list(FILTER_VALUES), 'filter caller restoration')
    check(c.mem(CONTROL, 4) == CONTROL_INITIAL and not c.calls and
          c.mem(SNAPSHOT, 12) == int.from_bytes(snapshot, 'little'), 'filter source/control preservation')


def consumer_compose(image, body, nodes, length):
    data = fixture([17], length=length)
    data[17*12+11] = 2
    c = FilterConsumer(image, body, data, 0)
    c.regions.append((TABLE, table_bytes(nodes), True))
    check(c.advance() == CALLBACK, 'filter consumer entry')
    snapshot = bytes(data[17*12:17*12+12])
    expected_result, expected_requests = prediction(nodes, snapshot, FRAME_SP)
    execute_filter(c)
    check(c.reg[10] == expected_result and c.requests == expected_requests, 'filter consumer result')
    check(c.reg[2] == FRAME_SP and c.reg[1] == 0x12cb4, 'filter consumer frame restoration')
    c.scan_start = 0x12cb4
    if expected_result:
        check(c.advance() == RETURN and c.reg[2] == STACK+0x800 and
              [c.reg[r] for r in S_REGS] == list(S_VALUES), 'filter consumer skip/restore')
    else:
        check(c.run(0x12cb4, {0x12cb6}) == 0x12cb6, 'filter consumer classification boundary')
    data[17*12:17*12+2] = bytes(2)
    check(c.queue() == data and c.csr == 0x88 and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'filter consumer released queue')


def nodes_for(mask0, mask1):
    return tuple((0x123+i if mask & 1 else 0xfffe,
                  2 if mask & 2 else 1, (0x21+i*0x91) if mask & 4 else 0)
                 for i, mask in enumerate((mask0, mask1)))


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'candidate body')
    cases = 0
    for m0 in range(8):
        for m1 in range(8):
            nodes = nodes_for(m0, m1)
            for length in range(256):
                standalone(image, body, nodes, length)
                cases += 1
            for length in (0, 8, 9, 255):
                consumer_compose(image, body, nodes, length)
    for flag in range(256):
        for length in (8, 9):
            standalone(image, body, ((0x123, 2, flag), (0xfffe, 2, 0)), length)
    headers = 0
    for ident in (0, 1, 0x7ff, 0x800, 0xffff):
        for tag in (0, 1, 2, 15, 255):
            for reply in (0, 1, MASK):
                standalone(image, body, nodes_for(7, 7), 8, ident, tag, reply)
                headers += 1
    # Change the length bound; and independently omit S4's pre-length assignment.
    for address, before, after, length, message in (
        (0x82fe, 'a14b', 'a54b', 9, 'filter request packet'),
        (0x832c, '3e8a', '0100', 9, 'filter sticky result'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+2] == bytes.fromhex(before), 'filter mutation pin')
        mutant[off:off+2] = bytes.fromhex(after)
        try:
            standalone(mutant, body, nodes_for(7, 0), length)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected filter mutation failure')
        else:
            raise RuntimeError('filter mutation undetected')
    print(f'PASS: {cases} table/length cases; 512 full-flag cases; {headers} header/return probes; 256 consumer compositions; sticky nonzero without request; 2 mutations; installed binding UNPROVED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
