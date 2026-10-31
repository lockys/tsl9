"""Scan bounded original APP code for direct GP references into the candidate BLE pool."""
import hashlib
import runpy
from pathlib import Path
root = Path(__file__).resolve().parents[2]
reader = root / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py'
layout = root / 'experiments/tsl9-original-layout/build/lookup-data-v1/c/NONLOADABLE-ORIGINAL-LAYOUT.elf'
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(reader) != 'a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a' or sha(layout) != '28360fab7c267bb635f1dfce1d3330903b2ebc113dd02872c9336d2d1264d0a7':
    raise SystemExit('Selected layout or reader changed')
elf = runpy.run_path(str(reader))['ELF'](layout)
sections = [s for s in elf.sections if s['flags'] & 6 == 6 and s['size']]
if len(sections) != 6 or sum(s['size'] for s in sections) != 69412:
    raise SystemExit('Selected code extent changed')
pool = (0x2000418c, 0x2000b18c); gp = 0x20004000
direct = []; aliases = []; instructions = 0
with image.open('rb') as f:
    for s in sections:
        start, size = s['address'], s['size']
        if start < 0x8000 or start + size > 0x1a69c or (start < 0x14c8a and start + size > 0x14056):
            raise SystemExit('Refusing excluded APP region')
        f.seek(start - 0x8000); data = f.read(size)
        if len(data) != size: raise SystemExit('Short instruction section')
        at = 0
        while at < size:
            n = 4 if data[at] & 3 == 3 else 2
            if at + n > size: raise SystemExit('Truncated instruction')
            pc = start + at; word = int.from_bytes(data[at:at+n], 'little'); at += n; instructions += 1
            if n != 4 or (word >> 15) & 31 != 3: continue
            op, funct = word & 127, (word >> 12) & 7
            if op == 3 and funct in (0, 1, 2, 4, 5):
                imm = word >> 20; width = {0:1, 1:2, 2:4, 4:1, 5:2}[funct]
            elif op == 0x23 and funct in (0, 1, 2):
                imm = ((word >> 25) << 5) | ((word >> 7) & 31); width = 1 << funct
            elif op == 0x13 and funct == 0:
                imm = word >> 20; imm -= 4096 if imm & 2048 else 0
                if pool[0] <= gp + imm < pool[1]: aliases.append(pc)
                continue
            else: continue
            imm -= 4096 if imm & 2048 else 0
            address = gp + imm
            if address < pool[1] and pool[0] < address + width: direct.append(pc)
if instructions != 23602 or direct or aliases:
    raise SystemExit('Direct GP pool references changed')
states = ((gp+176,gp+177), (gp+332,gp+336), (gp+370,gp+371), (0x2000bf38,0x2000bf3c), (0x2000b9d8,0x2000bde8))
if any(a < pool[1] and pool[0] < b for a,b in states):
    raise SystemExit('A selected state interval intersects the pool')
print('Candidate BLE pool and selected direct GP references checked; indirect writes and physical RAM remain unverified.')
