"""Narrow, read-only ELF32 ET_REL inspection; not a linker."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
OBJECT = ROOT / 'analysis/v4160-platform-2026-10-20/vector-native-stage/build/5a7dfa2b070144d389a62e9c89b9f9d1/c/vector-native.o'
OBJECT_HASH = '62ff2fa9dde7e667280b945cb901484ea5829047c88c4d058da2c00db40ef784'
SOURCE = ROOT / 'analysis/v4160-platform-2026-10-20/vector-native-stage/vector_native.c'
SOURCE_HASH = 'bcbb0a67e1f473c1f92ed44a67ca4fa64a86f12d53a9786302fc3fa34ff322dd'

class Invalid(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Invalid(message)

def span(data, off, size):
    require(off >= 0 and size >= 0 and off <= len(data) and size <= len(data) - off, 'out of bounds')
    return data[off:off + size]

def name(data, off):
    require(off < len(data), 'string offset')
    end = data.find(b'\0', off)
    require(end >= 0, 'unterminated string')
    return data[off:end].decode('ascii', errors='backslashreplace')

def inspect(data):
    h = struct.unpack('<16sHHIIIIIHHHHHH', span(data, 0, 52))
    ident, typ, machine, version, entry, phoff, shoff, flags, ehsize, phentsize, phnum, shentsize, shnum, shstr = h
    require(ident[:7] == b'\x7fELF\x01\x01\x01' and typ == 1 and machine == 243 and version == 1, 'ELF identity')
    require(phoff == 0 and phentsize == 0 and phnum == 0, 'unsupported program headers')
    require(ehsize == 52 and shentsize == 40 and shnum > 0 and 0 < shstr < shnum, 'section header format')
    span(data, shoff, shnum * 40)
    sections = [struct.unpack('<10I', span(data, shoff + i * 40, 40)) for i in range(shnum)]
    require(sections[0] == (0,) * 10, 'null section')
    for s in sections:
        if s[1] != 8:
            span(data, s[4], s[5])
    require(sections[shstr][1] == 3, 'section string table')
    strings = span(data, sections[shstr][4], sections[shstr][5])
    names = [name(strings, s[0]) for s in sections]
    wanted = '.text.tsl9v4160.handler_979e'
    require(names.count(wanted) == 1, 'target section')
    target = names.index(wanted)
    sec = sections[target]
    require(sec[1] == 1 and sec[2] & 4, 'target section type')
    rels = [s for s in sections if s[1] == 4 and s[7] == target]
    require(len(rels) == 1, 'target rela section')
    rela = rels[0]
    require(rela[9] == 12 and rela[5] % 12 == 0 and 0 < rela[6] < shnum, 'rela format')
    sym = sections[rela[6]]
    require(sym[1] == 2 and sym[9] == 16 and sym[5] % 16 == 0 and 0 < sym[6] < shnum, 'symtab format')
    strsec = sections[sym[6]]
    require(strsec[1] == 3, 'symbol strings')
    strdata = span(data, strsec[4], strsec[5])
    syms = [struct.unpack('<IIIBBH', span(data, sym[4] + i, 16)) for i in range(0, sym[5], 16)]
    require(len(syms) > 0 and syms[0] == (0,) * 6, 'null symbol')
    require(1 <= sym[7] <= len(syms), 'symtab sh_info')
    require(all((s[3] >> 4 == 0) == (i < sym[7]) for i, s in enumerate(syms)), 'symbol binding boundary')
    records = []
    for i in range(0, rela[5], 12):
        off, info, addend = struct.unpack('<IIi', span(data, rela[4] + i, 12))
        idx, kind = info >> 8, info & 255
        require(idx < len(syms) and off < sec[5], 'relocation bounds')
        records.append((off, kind, idx, addend))
    for selected in (0xe6, 0xea):
        relax = [r for r in records if r[0] == selected and r[1] == 51]
        require(len(relax) <= 1 and all(r[2] == 0 and r[3] == 0 for r in relax), 'invalid type 51')
    lo = [r for r in records if r[0] == 0xea and r[1] != 51]
    require(len(lo) == 1 and lo[0][1] == 25, 'selected LO type/uniqueness')
    anchor = syms[lo[0][2]]
    require(lo[0][3] == 0, 'nonzero LO addend')
    require(lo[0][2] != 0 and lo[0][2] < sym[7] and anchor[3] >> 4 == 0, 'anchor must be local')
    require(anchor[5] == target and anchor[1] == 0xe6, 'anchor section/offset')
    hi = [r for r in records if r[0] == anchor[1] and r[1] != 51]
    require(len(hi) == 1 and hi[0][1] == 23, 'HI type/uniqueness')
    dest = syms[hi[0][2]]
    require(dest[5] < shnum or dest[5] in (0xfff1, 0xfff2), 'target symbol section')
    hi_bytes = span(data, sec[4] + anchor[1], 4)
    lo_bytes = span(data, sec[4] + lo[0][0], 4)
    require(anchor[1] + 4 <= sec[5] and lo[0][0] + 4 <= sec[5], 'instruction section bounds')
    hw, lw = struct.unpack('<I', hi_bytes)[0], struct.unpack('<I', lo_bytes)[0]
    rd, rs1 = (hw >> 7) & 31, (lw >> 15) & 31
    require(hw & 127 == 0x17 and rd != 0, 'AUIPC opcode/rd')
    require(lw & 127 == 0x23 and (lw >> 12) & 7 in (0, 1, 2) and rs1 == rd, 'store opcode/rs1')
    return {'section': wanted, 'hi_offset': anchor[1], 'lo_offset': lo[0][0], 'anchor': name(strdata, anchor[0]), 'hi_symbol': name(strdata, dest[0]), 'hi_symbol_section': dest[5], 'hi_addend': hi[0][3], 'lo_addend': lo[0][3], 'hi_bytes': hi_bytes.hex(), 'lo_bytes': lo_bytes.hex(), 'rd_rs1': rd}

def pinned(path, digest):
    try:
        data = path.read_bytes()
    except OSError as e:
        raise Invalid('required evidence unavailable: ' + str(path)) from e
    require(hashlib.sha256(data).hexdigest() == digest, 'identity mismatch: ' + str(path))
    return data

def main():
    import sys
    try:
        data = pinned(OBJECT, OBJECT_HASH)
        pinned(SOURCE, SOURCE_HASH)
        result = inspect(data)
        require(result == {'section': '.text.tsl9v4160.handler_979e', 'hi_offset': 0xe6, 'lo_offset': 0xea, 'anchor': '.Lvec_00009884', 'hi_symbol': '__tsl9v4160_data_2000bebc', 'hi_symbol_section': 0, 'hi_addend': 0, 'lo_addend': 0, 'hi_bytes': '97270020', 'lo_bytes': '23aca762', 'rd_rs1': 15}, 'selected evidence mismatch')
        print(json.dumps(result, indent=2))
    except Invalid as e:
        print('FAIL: ' + str(e), file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
