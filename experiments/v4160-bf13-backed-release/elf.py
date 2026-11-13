"""Bounded ELF32 LE RISC-V reader for this experiment, not a general ELF validator."""
import struct

def require(condition, text):
    if not condition: raise ValueError(text)

class ELF:
    def __init__(self, raw):
        self.raw = bytes(raw)
        require(len(raw) >= 52, 'short ELF header')
        h = self.unpack('<16sHHIIIIIHHHHHH', 0)
        require(h[0] == b'\x7fELF\x01\x01\x01' + bytes(9), 'ELF ident')
        require(h[2] == 243 and h[3] == 1 and h[8] == 52 and h[11] == 40, 'ELF architecture/header')
        require(0 < h[12] < 1024 and h[13] < h[12], 'ELF section count')
        self.header = list(h[1:])
        self.program_headers = []
        if h[10]:
            require(h[9] == 32 and h[10] < 16, 'program headers')
            self.program_headers = [list(self.unpack('<8I', h[5]+32*i)) for i in range(h[10])]
        rows = [self.unpack('<10I', h[6]+40*i) for i in range(h[12])]
        require(rows[h[13]][1] == 3, 'section name string table type')
        strings = self.slice(rows[h[13]][4], rows[h[13]][5])
        keys = ('name_offset','type','flags','address','offset','size','link','info','align','entsize')
        self.sections = []
        for i,row in enumerate(rows):
            sec = dict(zip(keys,row)); sec['index'] = i; sec['name'] = self.string(strings,row[0])
            # Only section types understood by this bounded reader; RELR and
            # other unsupported relocation encodings must not be skipped.
            require(sec['type'] in (0, 1, 2, 3, 4, 8, 0x70000003, 0x6fff4c03), 'unsupported section type')
            if sec['type'] != 8: self.slice(sec['offset'],sec['size'])
            self.sections.append(sec)
        require(len({s['name'] for s in self.sections}) == len(rows), 'duplicate section')
        tables = [s for s in self.sections if s['type'] == 2]
        require(len(tables) == 1, 'symbol table count')
        table = tables[0]
        require(table['entsize'] == 16 and table['size'] % 16 == 0 and table['link'] < len(rows), 'symbol table shape')
        require(self.sections[table['link']]['type'] == 3, 'symbol string table type')
        strings = self.data(self.sections[table['link']])
        count = table['size']//16
        require(count > 0 and 1 <= table['info'] <= count, 'symbol local boundary')
        require(self.slice(table['offset'],16) == bytes(16), 'symbol zero entry')
        self.symbols = []
        for i in range(count):
            n,v,z,info,other,sec = self.unpack('<IIIBBH',table['offset']+16*i)
            require(sec < len(rows) or sec == 0xfff1, 'symbol index')
            require((info >> 4 == 0) == (i < table['info']), 'symbol local boundary')
            if info & 15 == 3:
                require(info == 3 and n == 0 and z == 0 and other == 0 and
                        0 < sec < len(rows) and v == rows[sec][3], 'SECTION symbol metadata')
            self.symbols.append({'index':i,'name':self.string(strings,n),'value':v,'size':z,'info':info,'other':other,'section':sec})
        self.relocations = []
        for sec in self.sections:
            require(sec['type'] != 9, 'REL unsupported')
            if sec['type'] == 4:
                require(sec['entsize'] == 12 and sec['size'] % 12 == 0 and sec['link'] == table['index'] and sec['info'] < len(rows), 'RELA shape')
                for i in range(sec['size']//12):
                    off, info, addend = self.unpack('<IIi',sec['offset']+12*i)
                    require(info >> 8 < len(self.symbols), 'RELA symbol index')
                    self.relocations.append({'section':sec['info'],'offset':off,'type':info & 255,'symbol':info >> 8,'addend':addend})

    def slice(self, start, size):
        require(0 <= start <= len(self.raw) and 0 <= size <= len(self.raw)-start, 'ELF extent')
        return self.raw[start:start+size]
    def unpack(self, fmt, offset):
        self.slice(offset, struct.calcsize(fmt))
        return struct.unpack_from(fmt,self.raw,offset)
    @staticmethod
    def string(b, off):
        require(off < len(b), 'string offset')
        end = b.find(b'\0',off)
        require(end >= off, 'unterminated string')
        return b[off:end].decode('ascii')
    def section(self, name):
        rows = [s for s in self.sections if s['name'] == name]
        require(len(rows) == 1, 'missing/duplicate section: '+name)
        return rows[0]
    def data(self, sec):
        if isinstance(sec,str): sec = self.section(sec)
        require(sec['type'] != 8, 'NOBITS')
        return self.slice(sec['offset'],sec['size'])
