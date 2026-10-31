"""Bounded original instruction scan and arithmetic; no target execution."""
import hashlib
import runpy
from pathlib import Path

root = Path(__file__).resolve().parents[2]
reader = root / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py'
layout = root / 'experiments/tsl9-original-layout/build/lookup-data-v1/c/NONLOADABLE-ORIGINAL-LAYOUT.elf'
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if digest(reader) != 'a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a' or digest(layout) != '28360fab7c267bb635f1dfce1d3330903b2ebc113dd02872c9336d2d1264d0a7':
    raise SystemExit('Layout or ELF reader changed')
elf = runpy.run_path(str(reader))['ELF'](layout)
sections = [s for s in elf.sections if s['flags'] & 6 == 6 and s['size']]
if len(sections) != 6 or sum(s['size'] for s in sections) != 69412:
    raise SystemExit('Selected original code extent changed')
direct = []; aliases = []; instructions = 0
with image.open('rb') as f:
    for start, size, expected in ((0x12020, 0x8a, '1225b6a684484e6c5a3fc6b38f57214729a7e3d6029095e66784c9bb31841e82'), (0x186d0, 0x28, 'd4179f53fc2814a11c2d01a0bba1de7044c0e3d79cd47ae8a88c6f0fc5697d1e')):
        f.seek(start - 0x8000)
        if hashlib.sha256(f.read(size)).hexdigest() != expected:
            raise SystemExit('Sequence or reset window changed')
    for s in sections:
        start, size = s['address'], s['size']
        if start < 0x8000 or start + size > 0x1a69c or (start < 0x14c8a and start + size > 0x14056):
            raise SystemExit('Refusing excluded APP region')
        f.seek(start - 0x8000); data = f.read(size)
        if len(data) != size: raise SystemExit('Short instruction segment')
        at = 0
        while at < size:
            n = 4 if data[at] & 3 == 3 else 2
            if at + n > size: raise SystemExit('Truncated instruction')
            pc = start + at; word = int.from_bytes(data[at:at+n], 'little'); at += n; instructions += 1
            if n != 4 or (word >> 15) & 31 != 3: continue
            op, funct = word & 127, (word >> 12) & 7
            if op == 0x23 and funct in (0, 1, 2):
                offset = ((word >> 25) << 5) | ((word >> 7) & 31)
                offset -= 4096 if offset & 2048 else 0
                if offset < 336 and offset + (1 << funct) > 332: direct.append(pc)
            elif op == 0x13 and funct == 0:
                offset = word >> 20; offset -= 4096 if offset & 2048 else 0
                aliases.append((pc, offset))
if instructions != 23602 or direct or len(aliases) != 196 or [pc for pc, offset in aliases if offset == 332] != [0x1202e]:
    raise SystemExit('Selected direct GP accesses changed')
if not (0x20004080 <= 0x20004000 + 332 and 0x20004000 + 336 <= 0x2000c958):
    raise SystemExit('Reset zero range does not cover all four bytes')
source = root / 'src/native/receive/feature_state_records.c'
if digest(source) != '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3':
    raise SystemExit('Nearby pointer consumer source changed')
windows = ((0x107c6, 0x50, 'd307a4c26719324fd50c4917181ffdac93b5fcc9c99b6f75cff7e99a033eb19f'),
           (0x10b9c, 0x80, 'ace22d8800893dbbe38a89aa882222872b5db2fedb36247d3fb9d95783cc23be'))
near, stores = [], []
with image.open('rb') as f:
    for start, size, expected in windows:
        if start < 0x14c8a and start + size > 0x14056:
            raise SystemExit('Refusing excluded code')
        f.seek(start - 0x8000)
        data = f.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Nearby pointer consumer window changed')
        at = 0
        while at < size:
            n = 4 if data[at] & 3 == 3 else 2
            if at + n > size:
                raise SystemExit('Truncated instruction')
            pc = start + at
            word = int.from_bytes(data[at:at+n], 'little')
            at += n
            if n != 4:
                continue
            op, base, funct = word & 127, (word >> 15) & 31, (word >> 12) & 7
            if op == 0x13 and base == 3 and funct == 0:
                near.append((pc, (word >> 7) & 31, word >> 20))
            if op == 0x23 and base == 8:
                stores.append((pc, funct, ((word >> 25) << 5) | ((word >> 7) & 31)))
if near != [(0x10ba8,10,325),(0x10bba,10,322),(0x10bd4,10,326),
            (0x10bf0,10,327),(0x10c04,10,323),(0x10c16,10,324)]:
    raise SystemExit('Nearby GP address formation changed')
if stores != [(0x107ea,0,0),(0x107f8,0,0),(0x10810,0,0)]:
    raise SystemExit('Nearby standard byte stores changed')
if any(offset in range(332, 336) for _, _, offset in near):
    raise SystemExit('Nearby scalar destination overlaps sequence bytes')
callback_source = root / 'src/native/receive/callback_providers.c'
if digest(callback_source) != 'daaf2f45bed63cb62eea82a981f03a79f8c5b25ea5e3b79941b223818f3c4e3f':
    raise SystemExit('Adjacent callback source changed')
with image.open('rb') as f:
    f.seek(0x10630 - 0x8000)
    data = f.read(0x6e)
if hashlib.sha256(data).hexdigest() != '18a4a2f47fd955f2aaf23d032a9286489b0aac9abde873d9b18892fc5a584dcb':
    raise SystemExit('Adjacent callback instruction window changed')
for pc, expected in ((0x1065c, '93868114'), (0x10676, '83c70600'),
                     (0x1067c, '03471700'), (0x10686, 'bd8b'),
                     (0x10690, '2380f600'), (0x10694, 'ef204037')):
    value = bytes.fromhex(expected)
    if data[pc-0x10630:pc-0x10630+len(value)] != value:
        raise SystemExit('Adjacent callback instruction changed')
if not (0x1a4f4 + 17 + 255 + 1 == 0x1a605 < 0x1a638):
    raise SystemExit('Adjacent callback source-address bound changed')
if any(((x + 1) & 15) not in range(16) for x in range(256)):
    raise SystemExit('Adjacent byte update range changed')
dispatcher = root / 'src/native/receive/record_dispatch.c'
if digest(dispatcher) != '6d90475b039233f5bea21aa3f7a3af3938f06e4c9ac4a293c1c5f43f6bc3cd1b':
    raise SystemExit('Record dispatcher source changed')
with image.open('rb') as f:
    f.seek(0x12a08 - 0x8000)
    dispatch = f.read(0x66)
if hashlib.sha256(dispatch).hexdigest() != '334494853a765e550af99f0e8dd95523efaf7cbb86d392e0340a5d5f004940c9':
    raise SystemExit('Record dispatcher original window changed')
for pc, expected in ((0x10632,'9307c021'), (0x10636,'2312f100'),
                     (0x10642,'a147'), (0x10644,'2303f100'), (0x10668,'a3070100')):
    value = bytes.fromhex(expected)
    if data[pc-0x10630:pc-0x10630+len(value)] != value:
        raise SystemExit('Caller record construction changed')
for pc, expected in ((0x12a16,'03570400'), (0x12a1c,'6311f704'),
                     (0x12a28,'8347b400'), (0x12a32,'03462400'),
                     (0x12a46,'93053400'), (0x12a4a,'13057101')):
    value = bytes.fromhex(expected)
    if dispatch[pc-0x12a08:pc-0x12a08+len(value)] != value:
        raise SystemExit('Dispatcher guard or copy arguments changed')
if 540 == 1 or (23 + 8, 40, 44) != (31, 40, 44):
    raise SystemExit('Record identifier or frame arithmetic changed')
print('Sequence state reset range and selected direct GP-store scan verified; aliases and concurrency remain unresolved.')
