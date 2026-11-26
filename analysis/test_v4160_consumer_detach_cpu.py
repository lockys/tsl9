"""Original consumer scan/copy/release prefix with candidate-only copy binding.

CSR 0x800 uses a synthetic bit model; no hardware/IRQ behavior is inferred.
82d2 is not executed: stop at its boundary, or supply nonzero normal returns to
continue scanning. Zero-return handlers are outside this test's allowed scope.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_reference_copy_cpu import (
    ReferenceCPU, CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL,
    CONTROL_INITIAL, FENCE,
)
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, QUEUE, STACK, RETURN, MASK, check

CALLBACK, CLEAR_CSR, SET_CSR = 0x82d2, 0x12c96, 0x12caa
INITIAL_SP, FRAME_SP = STACK+0x800, STACK+0x800-80
S_REGS = (8, 9, 18, 19, 20, 21, 22, 23)
S_VALUES = tuple(0x11220000+i*0x101 for i in range(8))


def fixture(indices, ident=0x123, length=8):
    data = bytearray((i*37+11) & 255 for i in range(384))
    for i in range(32):
        data[12*i:12*i+2] = bytes(2)
    for i in indices:
        data[12*i:12*i+2] = ident.to_bytes(2, 'little')
        data[12*i+2] = length
    return data


class Consumer(ReferenceCPU):
    CODE_RANGES = ((RAM, RAM+58), (0x12c58, 0x12cb6), (0x12cee, 0x12d0e))

    def __init__(self, image, body, data, csr):
        super().__init__(image, body)
        self.regions[1][1][:] = data
        self.regions[2][1][:] = bytes([0xcc])*0x1000
        self.reg[1], self.reg[2], self.reg[3] = RETURN, INITIAL_SP, 0x20004000
        for r, v in zip(S_REGS, S_VALUES):
            self.reg[r] = v
        self.csr = csr
        self.timeline, self.snapshots = [], []
        self.scan_start = 0x12c58

    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if value is not None and QUEUE <= address < QUEUE+384:
            self.timeline.append(('queue_store', address, size, value))
        return result

    def advance(self):
        pc = self.scan_start
        for _ in range(150):
            if pc == RETURN:
                self.scan_start = RETURN
                return RETURN
            if pc == CALLBACK:
                self.scan_start = pc
                return CALLBACK
            if pc in (CLEAR_CSR, SET_CSR):
                expected = 0x80093073 if pc == CLEAR_CSR else 0x80092073
                check(self.mem(pc, 4) == expected and self.reg[18] == 0x88, 'consumer CSR instruction')
                before = self.csr
                self.csr = before & ~0x88 if pc == CLEAR_CSR else before | 0x88
                self.csr &= MASK
                self.timeline.append(('csr_clear' if pc == CLEAR_CSR else 'csr_set', before, self.csr))
                pc += 4
            elif pc == RAM:
                slot = self.reg[8]
                check(self.reg[10:13] == [FRAME_SP+8, slot, 12] and self.reg[1] == 0x12ca6, 'consumer copy arguments')
                self.timeline.append(('copy_start', slot))
                self.run_reference(0x12ca6)
                self.timeline.append(('copy_end', slot))
                pc = 0x12ca6
            else:
                pc = self.run(pc, {CLEAR_CSR, SET_CSR, RAM, CALLBACK, RETURN})
        raise RuntimeError('consumer scan budget')

    def normal_callback_nonzero(self):
        # Only this response is modeled; preserve SP/S0-S7 and stack explicitly.
        resume = self.reg[1]
        for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
            self.put(reg, 0xbabe0000+reg*0x101)
        self.put(10, 0xdeadbeef)
        self.scan_start = resume


def scan(image, body, data, initial_csr):
    c = Consumer(image, body, data, initial_csr)
    expected = bytearray(data)
    indices = [i for i in range(32) if int.from_bytes(data[12*i:12*i+2], 'little')]
    cursor, expected_timeline = 0, []
    for index in indices:
        check(c.advance() == CALLBACK, 'consumer expected callback')
        slot = QUEUE+12*index
        row = bytes(data[12*index:12*index+12])
        check(c.reg[10] == FRAME_SP+8 and c.reg[1] == 0x12cb4, 'consumer callback arguments/link')
        snapshot = c.mem(FRAME_SP+8, 12).to_bytes(12, 'little')
        check(snapshot == row, 'consumer whole-row snapshot')
        expected[12*index:12*index+2] = bytes(2)
        check(c.queue() == expected, 'consumer released ID')
        expected_effects = [('read', CONTROL, 4, CONTROL_INITIAL), ('write', CONTROL, 4, 0), ('fence.i', FENCE)]
        for i, byte in enumerate(row):
            expected_effects += [('read', slot+i, 1, byte), ('write', FRAME_SP+8+i, 1, byte)]
        expected_effects.append(('write', CONTROL, 4, CONTROL_INITIAL))
        check(c.effects == expected_effects, 'consumer fixed-12 copy effects')
        before = initial_csr if cursor == 0 else initial_csr | 0x88
        expected_timeline += [('csr_clear', before, before & ~0x88), ('copy_start', slot),
                              ('copy_end', slot), ('queue_store', slot, 2, 0),
                              ('csr_set', before & ~0x88, before | 0x88)]
        check(c.timeline == expected_timeline, 'consumer detach order')
        check(c.csr == initial_csr | 0x88 and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'consumer control models')
        c.snapshots.append(snapshot)
        c.normal_callback_nonzero()
        cursor += 1
    check(c.advance() == RETURN, 'consumer scan return')
    check(c.queue() == expected and len(c.snapshots) == len(indices), 'consumer final queue')
    check(c.reg[1] == RETURN and c.reg[2] == INITIAL_SP and
          [c.reg[r] for r in S_REGS] == list(S_VALUES), 'consumer caller restoration')
    check(c.csr == (initial_csr | 0x88 if indices else initial_csr), 'consumer final CSR model')
    check(not c.calls and (bool(c.effects) == bool(indices)), 'consumer unexpected copy')
    return c


def interrupted(image, body):
    data = fixture([17])
    c = Consumer(image, body, data, MASK)
    c.fail_store = 3
    try:
        c.advance()
    except RuntimeError as exc:
        check(str(exc) == 'synthetic byte-store stop', 'unexpected consumer copy stop')
    else:
        raise RuntimeError('consumer copy stop absent')
    c.reference_active = False
    check(c.queue() == data and c.mem(CONTROL, 4) == 0 and c.csr == MASK & ~0x88, 'consumer interrupted controls/slot')
    check(c.mem(FRAME_SP+8, 2) == 0x123 and c.mem(FRAME_SP+10, 10) == int.from_bytes(bytes([0xcc])*10, 'little'), 'consumer interrupted snapshot')
    check(c.timeline == [('csr_clear', MASK, MASK & ~0x88), ('copy_start', QUEUE+17*12)] and
          c.reg[2] == FRAME_SP and not c.snapshots, 'consumer interrupted prefix')


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'candidate body')
    cases = 0
    for index in range(32):
        for ident in (1, 0x7ff, 0x800, 0xffff):
            for csr in (0, 0x88, MASK, 0x12345678):
                scan(image, body, fixture([index], ident), csr)
                cases += 1
    for length in range(256):
        scan(image, body, fixture([length % 32], length=length), 0)
    patterns = ([], list(range(32)), list(range(0, 32, 2)), list(range(1, 32, 2)), [0, 15, 31])
    for indices in patterns:
        scan(image, body, fixture(indices), 0)
    interrupted(image, body)
    for address, before, after, message in (
        (0x12ca6, '23100400', '23110400', 'consumer released ID'),
        (0x12c9e, '3146', '2d46', 'consumer copy arguments'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'consumer mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            scan(mutant, body, fixture([17]), 0)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected consumer mutation failure')
        else:
            raise RuntimeError('consumer mutation undetected')
    print(f'PASS: {cases} slot/ID/CSR cases; 256 length-byte cases; 5 scan patterns; copy-before-clear-before-callback; interrupted prefix; 2 mutations; installed binding UNPROVED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
