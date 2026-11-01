"""Small bounded ELF32 little-endian RISC-V parser; no execution support."""
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


class ELF:
    def __init__(self, path):
        self.raw = path.read_bytes()
        require(self.raw[:7] == b"\x7fELF\x01\x01\x01", "ELF32 little-endian version1")
        self.kind, machine = struct.unpack_from("<HH", self.raw, 16)
        require(machine == 243, "RISC-V machine")
        self.flags = struct.unpack_from("<I", self.raw, 36)[0]
        shoff = struct.unpack_from("<I", self.raw, 32)[0]
        size, count, names = struct.unpack_from("<HHH", self.raw, 46)
        require(size == 40 and shoff + count * 40 <= len(self.raw), "bounded ELF section table")
        self.sections = []
        for i in range(count):
            fields = struct.unpack_from("<10I", self.raw, shoff + i * 40)
            section = dict(zip(("name_offset", "type", "flags", "address", "offset", "size", "link", "info", "alignment", "entry_size"), fields))
            section["index"] = i
            require(section["type"] == 8 or section["offset"] + section["size"] <= len(self.raw), "bounded section bytes")
            self.sections.append(section)
        require(names < count, "section names index")
        strings = self.data(self.sections[names])
        for section in self.sections:
            section["name"] = self.string(strings, section["name_offset"])
        self.byname = {s["name"]: s for s in self.sections}
        self.symbol_tables = {}
        self.symbols = []
        for section in self.sections:
            if section["type"] != 2:
                continue
            require(section["entry_size"] == 16 and section["size"] % 16 == 0 and section["link"] < count, "ELF32 symbol table")
            strings = self.data(self.sections[section["link"]])
            entries = []
            for offset in range(section["offset"], section["offset"] + section["size"], 16):
                name, value, length, info, other, index = struct.unpack_from("<IIIBBH", self.raw, offset)
                entries.append(dict(name=self.string(strings, name), value=value, size=length, info=info, other=other, index=index))
            self.symbol_tables[section["index"]] = entries
            self.symbols.extend(entries)
        self.relocations = []
        for section in self.sections:
            if section["type"] not in (4, 9):
                continue
            require(section["type"] == 4 and section["entry_size"] == 12 and section["size"] % 12 == 0, "RELA encoding only")
            require(section["link"] in self.symbol_tables and section["info"] < count, "relocation linkage")
            symbols = self.symbol_tables[section["link"]]
            for offset in range(section["offset"], section["offset"] + section["size"], 12):
                site, info, addend = struct.unpack_from("<IIi", self.raw, offset)
                require(info >> 8 < len(symbols), "relocation symbol index")
                self.relocations.append(dict(owner=self.sections[section["info"]]["name"], offset=site, type=info & 255, addend=addend, symbol=symbols[info >> 8]))

    def data(self, section):
        return self.raw[section["offset"]:section["offset"] + section["size"]]

    @staticmethod
    def string(data, offset):
        require(offset < len(data), "bounded string offset")
        end = data.find(b"\0", offset)
        require(end >= 0, "terminated string")
        return data[offset:end].decode("utf-8")

    def function_bytes(self, symbol):
        require(0 < symbol["index"] < len(self.sections), "function section owner")
        owner = self.sections[symbol["index"]]
        offset = symbol["value"] - owner["address"] if self.kind == 2 else symbol["value"]
        require(offset >= 0 and offset + symbol["size"] <= owner["size"], "function bounded inside actual section")
        return self.data(owner)[offset:offset + symbol["size"]]
