"""Arithmetic only: partition 0x1a078 lookup addresses; never opens images."""
from collections import Counter

BASE = 0x1A078
APP_END = 0x1AC00
EXCLUDED = range(0x1A69C, 0x1A6A0)
counts = Counter()
excluded = []
outside = []
for mode in range(256):
    for column in range(16):
        address = BASE + 16 * mode + column
        if address in EXCLUDED:
            counts["excluded"] += 1
            excluded.append((mode, column))
        elif address >= APP_END:
            counts["outside"] += 1
            outside.append((mode, column))
        else:
            counts["inside_nonexcluded"] += 1
assert counts == {"excluded": 4, "outside": 1144, "inside_nonexcluded": 2948}
assert excluded == [(98, c) for c in range(4, 8)]
assert outside == [(184, c) for c in range(8, 16)] + [
    (mode, c) for mode in range(185, 256) for c in range(16)
]
print("4096 arithmetic combinations: 2948 inside nonexcluded, 4 excluded, 1144 outside")
