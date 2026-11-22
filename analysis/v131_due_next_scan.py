"""Timer return gate vs. a later scan; do not equate the two PCs."""
from collections import ChainMap
from v131_id7_scheduler_selection import bind, load, put, scan


def bind_due(image):
    bind(image)  # Check the separate scan instruction windows, too.
    raw = bytes.fromhex('b7370020 83a74721 e9cb')
    if image[0x270+0x874:0x270+0x87e] != raw:
        raise ValueError('timer return gate mismatch')

    def gate(m):
        return 0x2000094e if load(m, 0x20003214, 4) == 0 else 0x2000087e

    def verify(end):
        def ck(x):
            if not x: raise ValueError('unexpected post-timer scan state')
        m = ChainMap({}, end)
        ck(gate(m) == 0x2000094e)
        put(m, 0x20003214, 4, 1)
        ck(gate(m) == 0x2000087e)
        # Independent entry at 0x20000828; no claim about intervening calls.
        m = ChainMap({}, end)
        base = load(m, 0x200031e4, 4)
        seen, args = scan(m)
        ck(seen == [0, 1, 2, 3] and args == (3, 8192, 0x1995c))
        ck(load(m, base+6, 2) == 0 and load(m, base+14, 2) == load(end, base+14, 2))
        m = ChainMap({}, end)
        put(m, base+4, 2, 1)
        earlier, other = scan(m)
        ck(earlier == [0, 1, 2] and other[:2] == (2, 1) and load(m, base+6, 2) == 8192)
        return gate(end), tuple(seen), args
    return verify
