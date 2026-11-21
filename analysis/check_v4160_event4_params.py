"""Offline APP event-4 sender/receiver constants. No scheduler, ROM or radio execution."""
from hashlib import sha256
from pathlib import Path
import sys


def check(image):
    def need(ok, msg):
        if not ok:
            raise ValueError(msg)
    need(sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'APP identity')
    def read(pc, n):
        return int.from_bytes(image[pc-0x8000:pc-0x8000+n], 'little')
    def sx(v, bits):
        return (v ^ (1 << (bits-1))) - (1 << (bits-1))
    def ci(pc, base, rd):
        h = read(pc, 2)
        need(h & 0xef83 == base | rd << 7, hex(pc))
        return sx((h >> 2 & 31) | (h >> 7 & 32), 6)
    def imm(pc, template):
        w = read(pc, 4)
        need(w & 0xfffff == template, hex(pc))
        return sx(w >> 20, 12)
    # Independent immediates: callback checks (u16)(interval+delta)<=span;
    # receiver populates a1/a2/a3/a4 at different PCs for slot 93.
    delta = ci(0x85da, 1, 11)
    span = ci(0x85e0, 0x4001, 14)
    lo, hi, latency = [ci(p, 0x4001, rd) for p, rd in ((0x8866,11),(0x8864,12),(0x8862,13))]
    timeout = imm(0x885c, 0x713)
    need(read(0x85e6,2) == 0xe609 and latency == 0 and imm(0x85e8,0x713) == timeout == 200, 'latency/timeout')
    need((lo,hi) == (12,24) and all((((v+delta)&65535)<=span) == (lo<=v<=hi) for v in range(65536)), 'interval')
    need(imm(0x8858,0x7a803) == 424 and [read(p,2) for p in (0x8860,0x8868,0x886a)] == [0x87d2,0x8556,0x9802], 'slot / task and handle registers')
    bits = [imm(p,t) for p,t in ((0x8686,0x5f793),(0x86b2,0x47793),(0x875e,0x47793),(0x884a,0x47793))]
    need(bits == [8,1,2,4] and ci(0x860a,0x4001,11) == ci(0x8bfc,0x4001,11) == imm(0x886c,0x44513) == 4, 'event masks')
    # Valid matching task, normal branches, u16 events. Sign test has priority.
    selected = [m for m in range(65536) if not m & (0x8000|bits[0]|bits[1]|bits[2]) and m & bits[3]]
    need(len(selected) == 2048 and all((m^4) == (m & ~4) for m in selected), 'mask projection')
    print('PASS: 65536 intervals; request 12..24/0/200; 2048 of 65536 masks select event 4 for a matching task')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
