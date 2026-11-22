"""Conditional composition, not continuous CPU execution. Run from repo root."""
import sys
from pathlib import Path
from hashlib import sha256
from check_v4160_rtc_pairs import APP, HI, LO, run as sample

sys.path.insert(0, str(Path(__file__).resolve().parent / 'slot-40058-offline'))
from rv32_helper import run as divide


def need(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    app = APP.read_bytes()
    rom = Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
    need(sha256(app).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'APP')
    need(sha256(rom).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'reference')
    body, table = rom[0x2df1a:0x2e2ac], rom[0x2e95c:0x2ea5c]
    mask = 0xffffffff
    def q(x, d):
        lo, hi = divide(x * 1600, d, body, table)
        need((hi << 32 | lo) == x * 1600 // d, 'division')
        return lo
    def read(x, changed):
        hi, lo = x >> 16, x & 65535
        reads = [(HI, hi ^ int(changed))]*2 + [(LO, lo ^ int(changed))]*2 + [(HI, hi)]*2
        if changed: reads += [(LO, lo)]*2
        got = sample(app[0x111c6:0x11220], reads)
        need(got == x, 'sampler'); return got
    count = 0
    for x in [*range(101), 65535, 65536, 2684354, 2684355, mask]:
        for changed in (False, True):
            raw = read(x, changed)
            for d in (1, 1600, 16000, 65535):
                q(raw, d); count += 1
    # First series starts with last=acc=0, divisor=16000; no concurrent writes.
    last = acc = 0
    timeouts = []
    for x in range(101):
        current = q(read(x, False), 16000)
        need(current >= last, 'monotone low quotient')
        acc = (acc + current - last) & mask
        last = current
        visible = ((10 * acc) & mask) >> 4
        if visible > 2: timeouts.append(x)
    need(timeouts == list(range(50, 101)), 'first crossing')
    print(f'PASS: {count} RTC/division pairs; first crossing at sample 50 (base 0, divisor 16000)')

if __name__ == '__main__':
    main()
