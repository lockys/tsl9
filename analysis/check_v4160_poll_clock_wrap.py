"""Conditional V1.31 wrap cases. Requires local slot-40058-offline interpreter."""
from check_v131_poll_clock_join import M, project, rom
from check_v4160_rtc_to_poll import divide


def need(ok):
    if not ok:
        raise ValueError('wrap case mismatch')


def quotient(x, d):
    lo, hi = divide(x * 1600, d, rom[0x2df1a:0x2e2ac], rom[0x2e95c:0x2ea5c])
    need((hi << 32 | lo) == (x * 1600) // d)
    return lo


def update(last, now, w, acc):
    writes, after, visible = project(True, last, now, w, acc)
    need(writes == ([('last', now)] if now != last else []) + [('acc', after)])
    return after, (visible - (((acc * 10) & M) >> 4)) & M


def main():
    # Nominal config: the full quotient cannot overflow; the input can restart at zero.
    last, w = quotient(M, 16000), quotient(M, 16000)
    need(last == 429496729)
    for acc in (0, 1, 8, 0x7fffffff, M):
        need(update(last, quotient(0, 16000), w, acc) == (acc, 0))
    acc = 0
    crossings = []
    for x in range(61):
        now = quotient(x, 16000)
        acc, _ = update(last, now, w, acc)
        last = now
        if ((acc * 10 & M) >> 4) > 2:
            crossings.append(x)
    need(crossings == list(range(50, 61)))
    # Distinct mechanism: input increases, but low quotient decreases.
    prev, now = quotient(2684354, 1), quotient(2684355, 1)
    need((prev, now) == (0xfffffc80, 0x2c0))
    need(update(prev, now, quotient(M, 1), 0) == (0, 0))
    need(update(prev, now, quotient(0, 1), 0) == (1600, 1000))
    print('PASS: 5 unchanged accumulator controls; 61 post-wrap samples; 2 wrap-word controls')

if __name__ == '__main__':
    main()
