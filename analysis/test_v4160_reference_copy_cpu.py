"""Candidate-only SDK copy instruction execution and conditional APP composition.

RAM body is a synthetic view of pinned local carrier bytes, not installed ROM.
FENCE.I is decoded/recorded, never implemented as host cache/hardware behavior.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_tx_entry_cpu import EntryCPU, probe, ENTRY_SP
from test_v4160_tx_direct_chain import DirectChain, plan, MMIO
from test_v4160_tx_tail_cpu import SP, SAVED
from test_v4160_zero_id_queue_cpu import IMAGE, QUEUE, STACK, RETURN, check

ROOT = Path(__file__).resolve().parent.parent
CARRIER = ROOT/'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
CARRIER_HASH = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
APP_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BODY_HASH = '558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
RAM, CONTROL = 0x20000332, 0x4002420c
FENCE = RAM+(0x405ae-0x405a2)
CONTROL_INITIAL = 0xa5a55a5a


class ReferenceCPU(EntryCPU):
    CODE_RANGES = EntryCPU.CODE_RANGES + DirectChain.CODE_RANGES + ((RAM, RAM+58),)
    transfer = DirectChain.transfer
    execute = DirectChain.execute

    def __init__(self, image, body):
        super().__init__(image)
        self.regions.extend(((RAM, bytearray(body), False),
                             (CONTROL, bytearray(CONTROL_INITIAL.to_bytes(4, 'little')), True)))
        for base, data, _ in self.regions:
            if base == 0x4004c:
                data[:] = RAM.to_bytes(4, 'little')
        self.reference_active = False
        self.effects = []
        self.fail_store = None
        self.byte_stores = 0

    def mem(self, address, size, value=None):
        tracked = self.reference_active and (address == CONTROL or size == 1)
        if tracked and size == 1 and value is not None:
            self.byte_stores += 1
            if self.byte_stores == self.fail_store:
                self.effects.append(('blocked_store', address, size, value & 255))
                raise RuntimeError('synthetic byte-store stop')
        result = super().mem(address, size, value)
        if tracked:
            self.effects.append(('read' if value is None else 'write', address, size,
                                 result if value is None else value & ((1 << (8*size))-1)))
        return result

    def run_reference(self, resume):
        before = self.reg.copy()
        self.effects.clear()
        self.byte_stores = 0
        self.reference_active = True
        # No cleanup on failure: the real instruction prefix may leave MMIO zero.
        pc = RAM
        while True:
            stop = self.run(pc, {FENCE, resume}, budget=5000)
            if stop == resume:
                self.reference_active = False
                check(all(self.reg[i] == before[i] for i in range(32) if i not in (13, 14, 15, 16)), 'reference preserved registers')
                return
            check(self.mem(FENCE, 4) == 0x0000100f, 'reference FENCE.I encoding')
            self.effects.append(('fence.i', FENCE))
            pc = FENCE+4


def standalone(image, body, count, source=QUEUE, destination=STACK+0x200):
    c = ReferenceCPU(image, body)
    initial = bytes((i*37+11) & 255 for i in range(384))
    c.regions[1][1][:] = initial
    c.regions[2][1][:] = bytes([0xcc])*0x1000
    c.reg = [(0x10100000+i*0x101) & 0xffffffff for i in range(32)]
    c.reg[0], c.reg[1], c.reg[2] = 0, RETURN, SP
    c.reg[10:13] = [destination, source, count]
    # Independent byte-at-a-time model, including live overlap, on fixture bytes.
    queue, stack = bytearray(initial), bytearray([0xcc])*0x1000
    expected = [('read', CONTROL, 4, CONTROL_INITIAL), ('write', CONTROL, 4, 0), ('fence.i', FENCE)]
    def get(address):
        return queue[address-QUEUE] if QUEUE <= address < QUEUE+384 else stack[address-STACK]
    def put(address, value):
        if QUEUE <= address < QUEUE+384:
            queue[address-QUEUE] = value
        else:
            stack[address-STACK] = value
    if source and destination:
        for i in range(count):
            value = get(source+i)
            expected += [('read', source+i, 1, value), ('write', destination+i, 1, value)]
            put(destination+i, value)
    expected.append(('write', CONTROL, 4, CONTROL_INITIAL))
    c.run_reference(RETURN)
    check(c.effects == expected, 'reference ordered effects')
    check(c.queue() == queue and c.regions[2][1] == stack, 'reference memory result')
    check(c.mem(CONTROL, 4) == CONTROL_INITIAL, 'reference normal restore')


def compose(image, body, tag, length, mask, final):
    c = ReferenceCPU(image, body)
    check(probe(c, tag, 0, length, target=RAM), 'candidate-bound TX entry')
    source_payload = bytes(range(0xa0, 0xa8))
    c.run_reference(0x16bfa)
    expected_effects = [('read', CONTROL, 4, CONTROL_INITIAL), ('write', CONTROL, 4, 0), ('fence.i', FENCE)]
    for i in range(length):
        expected_effects += [('read', QUEUE+3+i, 1, source_payload[i]), ('write', SP+21+i, 1, source_payload[i])]
    expected_effects.append(('write', CONTROL, 4, CONTROL_INITIAL))
    check(c.effects == expected_effects, 'candidate-bound TX copy effects')
    frame = bytes(c.mem(SP+16+i, 1) for i in range(13))
    check(frame[5:] == source_payload[:length]+bytes(8-length), 'candidate-bound payload')
    busy = tuple(8 if mask >> i & 1 else 0 for i in range(3))
    entries, outgoing, scenarios = plan(busy, final, tag, length, frame)
    c.regions.append((MMIO, bytearray(8), True))
    c.scenarios = iter(scenarios)
    c.trace, c.transfers, c.entries = [], [], []
    row = c.queue()
    c.execute()
    check(c.entries == entries and c.transfers == outgoing, 'candidate-bound TX call sequence')
    check(c.reg[10] == (4 if mask == 7 or final & 0x70 else 0), 'candidate-bound TX result')
    check(c.reg[1] == RETURN and c.reg[2] == ENTRY_SP and
          [c.reg[i] for i in (8, 9, 18, 19)] == list(SAVED), 'candidate-bound caller restoration')
    check(c.queue() == row and c.mem(CONTROL, 4) == CONTROL_INITIAL and not c.calls, 'candidate-bound final memory')


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'SDK candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'SDK candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'SDK candidate body')
    basic = 0
    for count in range(16):
        for source, destination in ((QUEUE, STACK+0x200), (QUEUE, QUEUE),
                                    (QUEUE, QUEUE+1), (QUEUE+1, QUEUE),
                                    (0, STACK+0x200), (QUEUE, 0)):
            standalone(image, body, count, source, destination)
            basic += 1
    full = 0
    for tag in (1, 2):
        for length in range(9):
            for mask in range(8):
                for final in (0, 0x10, 0x70, 0x80, 0xff):
                    compose(image, body, tag, length, mask, final)
                    full += 1
    # Simulated third destination-store failure: two completed bytes, no restore.
    c = ReferenceCPU(image, body)
    c.mem(QUEUE, 4, 0x44332211)
    c.reg[1], c.reg[10], c.reg[11], c.reg[12] = RETURN, STACK+0x200, QUEUE, 4
    c.fail_store = 3
    try:
        c.run_reference(RETURN)
    except RuntimeError as exc:
        check(str(exc) == 'synthetic byte-store stop', 'unexpected reference stop')
    else:
        raise RuntimeError('reference stop did not fire')
    c.reference_active = False
    check(c.mem(CONTROL, 4) == 0 and c.mem(STACK+0x200, 4) == 0x2211 and
          c.effects[-1][0] == 'blocked_store', 'reference interrupted prefix')
    # Mutation control: change payload LBU to read the next source byte instead.
    mutant = bytearray(body)
    check(mutant[0x26:0x2a] == bytes.fromhex('03c80600'), 'reference LBU mutation pin')
    mutant[0x26:0x2a] = bytes.fromhex('03c81600')
    try:
        standalone(image, mutant, 1)
    except RuntimeError as exc:
        check(str(exc) == 'reference ordered effects', 'unexpected reference mutation failure')
    else:
        raise RuntimeError('reference LBU mutation undetected')
    print(f'PASS: pinned SDK slot/body; {basic} reference copy/null/overlap cases; {full} candidate-bound TX cases; interrupted prefix remains un-restored; LBU mutation detected; installed binding UNPROVED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
