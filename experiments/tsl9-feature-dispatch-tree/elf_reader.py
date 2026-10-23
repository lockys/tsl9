"""Local bounded ELF32 reader, derived from pinned SPI leaf reader.
Only section-count ceiling changes: <64 to <512 for 96 tree regions.
No target execution. Original reader is retained and not modified.
"""
import struct
from pathlib import Path

def require(ok, message):
    if not ok: raise ValueError(message)

class ELF:
    """Strict little-endian ELF32 reader. Accepts Path/str or actual bytes.

    Public API: header, sections, symbols, relocations, section(name), data(s).
    Parsed records retain actual section indices, ownership and symbol indices.
    No target execution and no dependency on another project parser.
    """
    def __init__(self, path_or_bytes):
        self.raw = bytes(path_or_bytes) if isinstance(path_or_bytes, (bytes, bytearray)) else Path(path_or_bytes).read_bytes()
        b = self.raw
        require(len(b) >= 52, 'ELF short header')
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', b)
        require(h[0] == b'\x7fELF\x01\x01\x01' + b'\0' * 9, 'ELF ident')
        require(h[2] == 243 and h[3] == 1 and h[8] == 52 and h[11] == 40, 'ELF architecture/header')
        require(0 < h[12] < 512 and h[13] < h[12], 'ELF section count')
        self.header = list(h[1:])
        self.program_headers = []
        if h[10]:
            require(h[9] == 32 and h[10] < 16, 'ELF program header shape')
            for i in range(h[10]):
                self.program_headers.append(list(self.unpack('<8I', h[5] + 32*i)))
        rows = [self.unpack('<10I', h[6] + 40*i) for i in range(h[12])]
        ns = rows[h[13]]
        names = self.slice(ns[4], ns[5])
        keys = ['name_offset', 'type', 'flags', 'address', 'offset', 'size', 'link', 'info', 'align', 'entsize']
        self.sections = []
        for i, r in enumerate(rows):
            s = dict(zip(keys, r)); s['index'] = i; s['name'] = self.string(names, r[0])
            if r[1] != 8:
                self.slice(r[4], r[5])
            self.sections.append(s)
        require(len({s['name'] for s in self.sections}) == len(rows), 'duplicate section names')
        tables = [s for s in self.sections if s['type'] == 2]
        require(len(tables) == 1, 'exactly one symbol table')
        table = tables[0]
        require(table['entsize'] == 16 and table['size'] % 16 == 0 and table['link'] < len(rows), 'symbol table shape')
        strings = self.data(self.sections[table['link']])
        self.symbols = []
        for i in range(table['size']//16):
            n, v, z, info, other, si = self.unpack('<IIIBBH', table['offset'] + 16*i)
            require(si < len(rows) or si == 0xfff1, 'symbol section index')
            self.symbols.append(dict(index=i, name=self.string(strings, n), value=v, size=z, info=info, other=other, section=si))
        self.relocations = []
        for s in self.sections:
            require(s['type'] != 9, 'REL records forbidden')
            if s['type'] == 4:
                require(s['entsize'] == 12 and s['size'] % 12 == 0 and s['link'] == table['index'] and s['info'] < len(rows), 'RELA shape')
                for i in range(s['size']//12):
                    offset, info, addend = self.unpack('<IIi', s['offset'] + 12*i)
                    require(info >> 8 < len(self.symbols), 'RELA symbol index')
                    self.relocations.append(dict(section=s['info'], offset=offset, type=info & 255, symbol=info >> 8, addend=addend))

    def slice(self, start, size):
        require(0 <= start <= len(self.raw) and 0 <= size <= len(self.raw)-start, 'ELF extent')
        return self.raw[start:start+size]

    def unpack(self, fmt, at):
        self.slice(at, struct.calcsize(fmt))
        return struct.unpack_from(fmt, self.raw, at)

    @staticmethod
    def string(buf, at):
        require(at < len(buf), 'ELF string offset')
        end = buf.find(b'\0', at)
        require(end >= at, 'ELF unterminated string')
        return buf[at:end].decode('ascii')

    def section(self, name):
        matches = [s for s in self.sections if s['name'] == name]
        require(len(matches) == 1, 'missing/duplicate section ' + name)
        return matches[0]

    def data(self, section):
        s = self.section(section) if isinstance(section, str) else section
        require(s['type'] != 8, 'NOBITS has no file bytes')
        return self.slice(s['offset'], s['size'])


