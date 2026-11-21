"""Check the incoming-a4 first touch; inputs are reference carriers, not devices."""
import hashlib
from pathlib import Path
import sys

REFS = {
    '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22': ('1.31', 0x5a2),
    'b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941': ('1.40', 0x5e2),
}


def first_touch(hi, ld):
    if hi & 0xfff != (15 << 7 | 0x37): return False  # LUI a5: no source
    if ld & 0x7f != 3 or (ld >> 12) & 7 != 2: return False  # LW
    rd, rs = (ld >> 7) & 31, (ld >> 15) & 31
    imm = (ld >> 20 ^ 2048) - 2048
    return rd == 14 and rs == 15 and ((hi & 0xfffff000) + imm) & 0xffffffff == 0x4002420c


def check(path):
    raw = Path(path).read_bytes()
    version, off = REFS[hashlib.sha256(raw).hexdigest()]
    def word(i): return int.from_bytes(raw[i:i+4], 'little')
    if word(0x4c) != 0x20000332: raise ValueError('slot')
    hi, ld = word(off), word(off+4)
    if not first_touch(hi, ld): raise ValueError('first touch')
    # Legal LW variants: base a4 reads the incoming value; destination a5 leaves it live.
    for changed in (ld ^ (1 << 15), ld ^ (1 << 7)):
        if first_touch(hi, changed): raise ValueError('operand control')
    return version


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit('supply at least one reference carrier')
    for path in sys.argv[1:]: print(f'PASS V{check(path)}: incoming a4 not read; first write = LW from 0x4002420c')
