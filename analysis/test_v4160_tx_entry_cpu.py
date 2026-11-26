"""Original TX entry through local fill to opaque copy boundary, never provider.

Synthetic row/config/stack only. Data-read traces verify rejection ordering and
exact pre-provider stores. No peripheral code or target firmware is executed.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, QUEUE, STACK, PROVIDER, RETURN, check
from test_v4160_tx_tail_cpu import SP, SAVED
from test_v4160_tx_direct_chain import DirectChain, plan, MMIO

GP, CONFIG, SLOT = 0x20004000, 0x23000000, 0x4004c
ENTRY_SP = SP+64
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class EntryCPU(CPU):
    CODE_RANGES = ((0x8520, 0x8528), (0x854a, 0x8598), (0x16b7c, 0x16bfa), (0x16c52, 0x16c72))

    def __init__(self, image):
        super().__init__(image, bytes(384))
        self.regions.extend(((GP+84, bytearray(CONFIG.to_bytes(4, 'little')), False),
                             (CONFIG, bytearray(5), True)))
        self.reads = []

    def mem(self, address, size, value=None):
        if value is None and (QUEUE <= address < QUEUE+12 or address in (GP+84, CONFIG+4, SLOT)):
            self.reads.append((address, size))
        return super().mem(address, size, value)


class ConditionalWhole(EntryCPU):
    CODE_RANGES = EntryCPU.CODE_RANGES + DirectChain.CODE_RANGES
    transfer = DirectChain.transfer
    execute = DirectChain.execute


def conditional_whole(image, tag, length, mask, final):
    c = ConditionalWhole(image)
    check(probe(c, tag, 0, length), 'conditional whole entry')
    frame = bytes(c.mem(SP+16+i, 1) for i in range(13))
    check(frame[5:] == bytes(8), 'conditional payload must remain local-fill zeros')
    busy = tuple(8 if mask >> i & 1 else 0 for i in range(3))
    entries, outgoing, scenarios = plan(busy, final, tag, length, frame)
    c.regions.append((MMIO, bytearray(8), True))
    c.scenarios = iter(scenarios)
    c.trace, c.transfers, c.entries = [], [], []
    before_row = c.queue()
    # Explicit normal-return/no-memory-effects hypothesis for the unknown copy
    # provider. It does NOT copy row payload, and no provider code executes.
    c.put(10, 0xdeadbeef)
    c.execute()
    check(c.entries == entries and c.transfers == outgoing, 'conditional whole call sequence')
    check(next(c.scenarios, None) is None, 'conditional whole unused status inputs')
    expected_result = 4 if mask == 7 or final & 0x70 else 0
    check(c.reg[10] == expected_result, 'conditional whole return')
    check(c.reg[2] == ENTRY_SP and c.reg[1] == RETURN, 'conditional whole SP/RA')
    check([c.reg[i] for i in (8, 9, 18, 19)] == list(SAVED), 'conditional whole S registers')
    check(c.queue() == before_row and
          bytes(c.mem(SP+16+i, 1) for i in range(13)) == frame, 'conditional whole row/frame changed')
    check(not c.calls, 'conditional whole provider executed')


def probe(c, tag, flags, length, ident=0x123, target=PROVIDER):
    c.reg = [0]*32
    c.reg[1], c.reg[2], c.reg[3], c.reg[10] = RETURN, ENTRY_SP, GP, QUEUE
    for reg, value in zip((8, 9, 18, 19), SAVED):
        c.reg[reg] = value
    c.regions[2][1][:] = bytes([0xcc])*0x1000
    c.mem(QUEUE, 2, ident)
    c.mem(QUEUE+2, 1, length)
    c.mem(QUEUE+3, 8, int.from_bytes(bytes(range(0xa0, 0xa8)), 'little'))
    c.mem(QUEUE+11, 1, tag)
    c.mem(CONFIG+4, 1, flags)
    # An invalid tag must not even read the GP slot, much less dereference it.
    for base, data, _ in c.regions:
        if base == GP+84:
            data[:] = (CONFIG if tag in (1, 2) else 0xfffffff0).to_bytes(4, 'little')
    before_row = c.queue()
    c.writes.clear()
    c.reads.clear()
    stop = c.run(0x16b7c, {target, RETURN})
    expected_reads = [(QUEUE+11, 1)]
    expected_stores = []
    valid_tag = tag in (1, 2)
    if valid_tag:
        expected_reads += [(GP+84, 4), (CONFIG+4, 1)]
    allocated = valid_tag and not flags & 8
    if allocated:
        expected_reads += [(QUEUE+2, 1)]
        expected_stores += [(SP+60, 4, RETURN)] + [(SP+o, 4, v) for o, v in zip((56, 52, 48, 44), SAVED)]
    accepted = allocated and length <= 8
    if accepted:
        expected_reads += [(QUEUE, 2), (SLOT, 4)]
        expected_stores += [(SP+12, 2, 0x4030), (SP+14, 1, 0x50)]
        expected_stores += [(SP+18+i, 1, 0) for i in range(10, -1, -1)]
        expected_stores += [(SP+20, 1, length), (SP+17, 1, ident << 5 & 255), (SP+16, 1, ident >> 3 & 255)]
        check(stop == target, 'entry should reach copy boundary')
        check(c.reg[10:13] == [SP+21, QUEUE+3, length], 'entry copy arguments')
        check(c.reg[1] == 0x16bfa and c.reg[2] == SP, 'entry provider frame/link')
    else:
        check(stop == RETURN and c.reg[10] == 4, 'entry rejection')
        check(c.reg[2] == ENTRY_SP and c.reg[1] == RETURN, 'rejected caller SP/RA')
        check([c.reg[i] for i in (8, 9, 18, 19)] == list(SAVED), 'rejected caller S registers')
    check(c.reads == expected_reads, 'entry data-read order')
    check(c.writes == expected_stores, 'entry store footprint')
    check(c.queue() == before_row and not c.calls, 'row changed or provider executed')
    return accepted


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    c = EntryCPU(image)
    accepted_tag_flags = 0
    for tag in range(256):
        for flags in range(256):
            accepted_tag_flags += probe(c, tag, flags, 8)
    check(accepted_tag_flags == 256, 'tag/flags acceptance count')
    accepted_flags_length = 0
    for flags in range(256):
        for length in range(256):
            accepted_flags_length += probe(c, 1, flags, length)
    check(accepted_flags_length == 1152, 'flags/length acceptance count')
    boundaries = 0
    for ident in (0, 1, 0x7ff, 0x800, 0xffff):
        for tag in (1, 2):
            for length in range(9):
                probe(c, tag, 0, length, ident)
                boundaries += 1
    whole = 0
    for tag in (1, 2):
        for length in range(9):
            for mask in range(8):
                for final in (0, 0x10, 0x70, 0x80, 0xff):
                    conditional_whole(image, tag, length, mask, final)
                    whole += 1
    # Wrong config mask must reverse the decision for a fixture with bit 3 set.
    mutant = bytearray(image)
    off = 0x16b98-BASE
    check(mutant[off:off+2] == bytes.fromhex('218b'), 'config mask mutation pin')
    mutant[off:off+2] = bytes.fromhex('118b')  # C.ANDI A4,8 -> 4
    try:
        probe(EntryCPU(mutant), 1, 8, 8)
    except RuntimeError as exc:
        check(str(exc) == 'entry rejection', 'unexpected config mutation failure')
    else:
        raise RuntimeError('config mask mutation undetected')
    # Wrong unsigned length bound allows 9 into fill/copy preparation.
    mutant = bytearray(image)
    off = 0x16bac-BASE
    check(mutant[off:off+2] == bytes.fromhex('2147'), 'length bound mutation pin')
    mutant[off:off+2] = bytes.fromhex('2547')  # C.LI A4,8 -> 9
    try:
        probe(EntryCPU(mutant), 1, 0, 9)
    except RuntimeError as exc:
        check(str(exc) == 'entry rejection', 'unexpected length mutation failure')
    else:
        raise RuntimeError('length bound mutation undetected')
    print(f'PASS: 65536 tag/config pairs ({accepted_tag_flags} accepted); 65536 config/length pairs ({accepted_flags_length} accepted); {boundaries} ID/tag/length boundaries; {whole} conditional whole-TX cases; ordered reads/stores; 2 guard mutations')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
