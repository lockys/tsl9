"""Classify a shared uncovered numerical interval using ELF metadata only."""
import hashlib
import runpy
from pathlib import Path
root = Path(__file__).resolve().parents[2]
reader = root / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py'
layout = root / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/NONLOADABLE-ORIGINAL-LAYOUT.elf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(reader) != 'a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a' or sha(layout) != 'c79cc33284766865c77345a697c2a76b12b1ab79dbe3b996710f0b6e1ca4d8b0':
    raise SystemExit('Layout or reader changed')
elf = runpy.run_path(str(reader))['ELF'](layout)
gap = (0x1a6a0, 0x1a6b8); excluded = (0x1a69c, 0x1a6a0)
def intersects(a, b): return a[0] < b[1] and b[0] < a[1]
if any(s['flags'] & 2 and s['size'] and intersects((s['address'], s['address'] + s['size']), gap) for s in elf.sections):
    raise SystemExit('Gap has an allocated section')
modes = [(m, c) for m in range(256) for c in range(16) if gap[0] <= 0x1a078 + 16*m + c < gap[1]]
if modes != [(98, c) for c in range(8, 16)] + [(99, c) for c in range(16)]:
    raise SystemExit('Mode gap intersections changed')
seq = []
for channel in range(4):
    for state in range(256):
        start = 0x1a638 + 6*(2*channel + state); window = (start, start+6)
        if intersects(window, gap): seq.append((channel, state, intersects(window, excluded)))
if len(seq) != 20 or sum(int(ex) for _, _, ex in seq) != 4:
    raise SystemExit('Sequence gap intersections changed')
if [[s for ch, s, _ in seq if ch == c] for c in range(4)] != [list(range(17,22)), list(range(15,20)), list(range(13,18)), list(range(11,16))]:
    raise SystemExit('Per-channel state intersections changed')
print('Shared uncovered lookup interval classified from ELF metadata; no firmware payload read.')
