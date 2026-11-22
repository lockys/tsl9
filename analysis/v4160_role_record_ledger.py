"""Verify post-allocation stores up to (not including) the first outer count load."""
P = 0x200048ac
IO = 0x4002420c


def records(pc, regs, mem, log):
    if pc != 0x4daf6 or regs['s4'] + 848 != 0x20003350:
        raise ValueError('unexpected stop or count address')
    expected = [(0x20003354, 4, P)] + [(P+i, 1, 0) for i in range(300)]
    for i in range(5):
        p = P + 60*i
        expected.extend([(p+2, 2, 65535), (p+4, 1, 0), (p+44, 4, 0)])
    expected.extend((0x20003358+i, 1, 0) for i in range(48))
    expected.append((0x20003314, 1, 6))
    expected.extend((0x20003320+i, 1, 0) for i in range(48))
    if any(p < 0x20003352 and p+w > 0x20003350 for p,w,_ in log):
        raise ValueError('store overlaps count pair')
    if [row for row in log if row[0] != IO] != expected:
        raise ValueError('RAM store order, width or value')
    if [(i,w) for i,(p,w,_) in enumerate(log) if p == IO] != [(i,4) for i in (1,302,318,367,369,418)]:
        raise ValueError('MMIO store order or width')
    if bytes(mem[P+i] for i in range(300)) != (bytes(2)+b'\xff\xff'+bytes(56))*5:
        raise ValueError('final records')
    return len(log)
