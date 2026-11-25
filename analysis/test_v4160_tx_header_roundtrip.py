"""Original local fill -> TX packing -> synthetic replay -> original RX guard.

Starts at the local fill call boundary with synthetic SP/S0/S1. Execute the
11-byte clear, then TX packing; stop before the opaque copy provider. No transmit
routine executes. Replay is numeric frame transfer, not a wire model.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, QUEUE, STACK, PROVIDER, MASK, check
from test_v4160_ingress_queue_chain import ingress, INSERT, REJECT

IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class HeaderCPU(CPU):
    CODE_RANGES = ((0x8520, 0x8528), (0x854a, 0x8598), (0x16bd2, 0x16bfa))


def project(c, ident, length):
    c.reg = [0]*32
    c.reg[2], c.reg[8], c.reg[9] = STACK+0x800, QUEUE, length
    # Poison every frame byte before executing the actual local clear path.
    c.regions[2][1][:] = bytes([0xcc])*0x1000
    c.mem(QUEUE, 2, ident)
    c.writes.clear()
    sp = c.reg[2]
    c.reg[1] = 0x16bd2
    c.reg[10:13] = [sp+18, 0, 11]
    c.run(0x8520, {0x16bd2})
    fill_stores = [(sp+18+i, 1, 0) for i in range(10, -1, -1)]
    check(c.writes == fill_stores, 'local fill stores')
    check(c.reg[2] == sp and c.reg[8:10] == [QUEUE, length], 'local fill preserved state')
    check(c.run(0x16bd2, {PROVIDER}) == PROVIDER, 'TX provider entry')
    check(c.reg[10:13] == [sp+21, QUEUE+3, length], 'TX provider arguments')
    check(c.reg[1] == 0x16bfa, 'TX provider link')
    check(c.writes == fill_stores + [(sp+20, 1, length), (sp+17, 1, ident << 5 & 255),
                       (sp+16, 1, ident >> 3 & 255)], 'TX header stores')
    expected = bytearray([0xcc]*0x1000)
    expected[0x812:0x81d] = bytes(11)
    expected[0x810], expected[0x811], expected[0x814] = ident >> 3 & 255, ident << 5 & 255, length
    check(c.regions[2][1] == expected, 'TX frame footprint')
    # Reinterpret the frame at a separate RX guard boundary. Its saved tag is
    # synthetic and independent of TX S1; cleared payload has NOT been copied.
    c.reg[9] = 0x12345642
    result = ingress(c)
    if length:
        check(result == INSERT, 'RX replay rejected nonzero length')
        check(c.reg[10:14] == [ident & 2047, sp+21, length, 0x12345642], 'RX replay projection')
    else:
        check(result == REJECT, 'RX replay accepted zero length')
    check(not c.calls, 'opaque provider executed')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    c = HeaderCPU(image, bytes(384))
    counts = [0]*2048
    for ident in range(65536):
        project(c, ident, 8)
        counts[c.reg[10]] += 1
    check(counts == [32]*2048, '16-to-11-bit projection multiplicity')
    boundaries = 0
    for ident in (0, 1, 0x7ff, 0x800, 0xffff):
        for length in range(9):
            project(c, ident, length)
            boundaries += 1
    # Negative control: change SRLI A4,A5,3 to SRLI A4,A5,2 in a copy.
    mutant = bytearray(image)
    off = 0x16bdc-BASE
    check(mutant[off:off+4] == bytes.fromhex('13d73700'), 'packing mutation pin')
    mutant[off:off+4] = bytes.fromhex('13d72700')
    try:
        project(HeaderCPU(mutant, bytes(384)), 8, 8)
    except RuntimeError as exc:
        check(str(exc) == 'TX header stores', 'unexpected packing mutation failure')
    else:
        raise RuntimeError('packing mutation undetected')
    mutant = bytearray(image)
    off = 0x856a-BASE
    check(mutant[off:off+4] == bytes.fromhex('2305b700'), 'fill mutation pin')
    mutant[off:off+4] = bytes.fromhex('a304b700')  # SB offset 10 -> 9
    try:
        project(HeaderCPU(mutant, bytes(384)), 8, 8)
    except RuntimeError as exc:
        check(str(exc) == 'local fill stores', 'unexpected fill mutation failure')
    else:
        raise RuntimeError('fill mutation undetected')
    # Default queue interpreter must still reject entry to the TX slice.
    try:
        CPU(image, bytes(384)).run(0x16bd2, {PROVIDER})
    except RuntimeError as exc:
        check('execution outside bounded slices' in str(exc), 'unexpected scope failure')
    else:
        raise RuntimeError('default CPU scope expanded')
    print(f'PASS: 65536 local-fill/TX/RX ID cases (2048 IDs x 32); {boundaries} ID/length boundaries; zero length rejected on replay; 2 instruction mutations and default-scope guard detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
