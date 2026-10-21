"""Read-only ELF/source audit for a future readable 9A42 native component.

The only writes are this script's explicit report inside its own directory.
No compiler, target, simulator, device, shell child, or network is launched.
"""
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[2]
NATIVE = WORK / "experiments/tsl9-v4160-startup"
IMAGE = NATIVE / "build/image-fidelity-999d8125159a4d80bd6df9153f267002"
FW = WORK / "exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin"
TOOLBIN = Path("C:/Users/locky/AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


class ELF:
    def __init__(self, path):
        self.path = path
        self.raw = path.read_bytes()
        require(self.raw[:7] == b"\x7fELF\x01\x01\x01", "ELF32 little endian")
        self.kind, machine = struct.unpack_from("<HH", self.raw, 16)
        require(machine == 243, "RISC-V ELF")
        self.flags = struct.unpack_from("<I", self.raw, 36)[0]
        shoff = struct.unpack_from("<I", self.raw, 32)[0]
        shsize, count, names = struct.unpack_from("<HHH", self.raw, 46)
        require(shsize == 40 and shoff + count * 40 <= len(self.raw), "bounded sections")
        self.sections = []
        for i in range(count):
            fields = struct.unpack_from("<10I", self.raw, shoff + i * 40)
            item = dict(zip(("name_index", "type", "flags", "address", "offset", "size", "link", "info", "alignment", "entry_size"), fields))
            item["index"] = i
            if item["type"] != 8:
                require(item["offset"] + item["size"] <= len(self.raw), "bounded section bytes")
            self.sections.append(item)
        self.strings = self.data(self.sections[names])
        for section in self.sections:
            section["name"] = self.string(self.strings, section["name_index"])
        self.byname = {s["name"]: s for s in self.sections}
        self.symbols = {}
        for section in self.sections:
            if section["type"] != 2:
                continue
            require(section["entry_size"] == 16 and section["size"] % 16 == 0, "ELF32 symbols")
            strings = self.data(self.sections[section["link"]])
            entries = []
            for off in range(section["offset"], section["offset"] + section["size"], 16):
                name, value, size, info, other, index = struct.unpack_from("<IIIBBH", self.raw, off)
                entries.append(dict(name=self.string(strings, name), value=value, size=size, info=info, other=other, index=index))
            self.symbols[section["index"]] = entries
        self.relocations = []
        for section in self.sections:
            if section["type"] not in (4, 9):
                continue
            require(section["type"] == 4 and section["entry_size"] == 12 and section["size"] % 12 == 0, "RELA only")
            for off in range(section["offset"], section["offset"] + section["size"], 12):
                site, info, addend = struct.unpack_from("<IIi", self.raw, off)
                symbols = self.symbols[section["link"]]
                require(info >> 8 < len(symbols), "bounded relocation symbol")
                self.relocations.append(dict(owner=self.sections[section["info"]]["name"], offset=site, type=info & 255, addend=addend, symbol=symbols[info >> 8]))

    @staticmethod
    def string(data, offset):
        require(offset < len(data), "bounded string")
        end = data.find(b"\0", offset)
        require(end >= 0, "terminated string")
        return data[offset:end].decode("utf-8")

    def data(self, section):
        return self.raw[section["offset"]:section["offset"] + section["size"]]


def main():
    receipt_path = IMAGE / "verification.json"
    require(sha(receipt_path) == "2e6585594c1b02de058e2fbb5838f591a5915efed7bc461b9083e99a2e97b8bd", "immutable latest image receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    require(receipt["passed"] and not receipt["original_C_ABIs_proved"] and not receipt["IRQ_ABI_proved"], "actual baseline limitations")
    require(sha(FW) == "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667", "original ID2966 bytes")
    raw = FW.read_bytes()
    mode_reports = {}
    for mode in ("c", "cpp"):
        recorded = receipt["modes"][mode]
        objpath = Path(recorded["integrated_object"])
        require(sha(objpath) == recorded["integrated_sha256"], "actual merged object digest")
        obj = ELF(objpath)
        require(obj.kind == 1, "relocatable native baseline")
        # Existing gate counts nonempty allocations; the linker also retains an
        # empty SHF_ALLOC .text marker, which supplies no bytes or runtime body.
        allocated = [s for s in obj.sections if s["flags"] & 2 and s["size"]]
        require(len(allocated) == 691 and len(obj.relocations) == 8280, "actual 691 allocations and 8280 RELA")
        undefined = sorted({s["name"] for entries in obj.symbols.values() for s in entries if s["name"] and s["index"] == 0})
        require(undefined == ["__tsl9v4160_rom_entry"], "one real native unresolved resident entry")
        target = obj.byname[".text.tsl9v4160.init_9a42"]
        require(target["size"] == 144 and obj.data(target) == raw[0x9A42 - 0x8000:0x9AD2 - 0x8000], "exact 144-byte original 9A42 capture")
        inbound = []
        outbound = []
        for relocation in obj.relocations:
            sym = relocation["symbol"]
            if sym["index"] == target["index"] and relocation["owner"] != target["name"]:
                inbound.append({k: relocation[k] for k in ("owner", "offset", "type", "addend") } | {"target_name": sym["name"], "target_offset": sym["value"] + relocation["addend"]})
            if relocation["owner"] == target["name"]:
                outbound.append({k: relocation[k] for k in ("offset", "type", "addend")} | {"target_name": sym["name"]})
        require(inbound == [dict(owner=".text.tsl9v4160.core_flow_9250", offset=8, type=17, addend=0, target_name="__tsl9v4160_call_9a42", target_offset=0)], "actual sole direct relocation inbound 9258 to 9A42")
        require(len(outbound) == 6 and all(r["type"] == 17 and r["addend"] == 0 for r in outbound), "six direct native JAL references")
        callees = {}
        for address in (0x19124, 0x19142, 0x19160, 0x1917E):
            owner = obj.byname[".text.tsl9v4160.frontier_" + format(address, "x")]
            require(owner["size"] == 30 and obj.data(owner) == raw[address - 0x8000:address + 30 - 0x8000], "exact original helper leaf")
            rels = [r for r in obj.relocations if r["owner"] == owner["name"]]
            require(len(rels) == 1 and rels[0]["type"] == 44 and rels[0]["symbol"]["index"] == owner["index"], "helper contains only local compressed branch relocation")
            callees[format(address, "x")] = dict(bytes=30, sha256=hashlib.sha256(obj.data(owner)).hexdigest(), no_external_relocations=True)
        mode_reports[mode] = dict(object=objpath.relative_to(WORK).as_posix(), object_sha256=sha(objpath), allocations=len(allocated), raw_RELA=len(obj.relocations), undefined_symbols=undefined, flags=obj.flags, inbound_direct_relocations=inbound, outbound_direct_relocations=outbound, helpers=callees)
    entry_path = WORK / "apk-analysis/tsl9-v4160-core-flow-2026-10-20/initialization-review/entry-09a42.json"
    require(sha(entry_path) == "d9ccffbc52416493a12f83b28db16032c70f06f1827b63c8be6331f355eb02af", "recorded 46-instruction bounded source entry")
    entry = json.loads(entry_path.read_text(encoding="utf-8-sig"))
    require(entry["instruction_count"] == 46 and entry["reachable_bytes"] == 144 and not entry["budget_or_decode_limits"], "complete bounded local entry capture")
    tool_expect = {"clang.exe": "047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6", "ld.lld.exe": "fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f", "llvm-objcopy.exe": "e5590a8f45e93f322f0829b91dbddb74e8c1eb91436d13161abc773aebf64469", "llvm-objdump.exe": "de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa"}
    for name, digest in tool_expect.items():
        require(sha(TOOLBIN / name) == digest, "current executable pin: " + name)
    report = dict(schema="TSL9-9A42-native-replacement-plan-audit-v1", passed=True,
                  original_sha256=sha(FW), old_image_receipt_sha256=sha(receipt_path), entry_capture_sha256=sha(entry_path),
                  modes=mode_reports, current_tool_directory=str(TOOLBIN), current_tool_sha256=tool_expect,
                  historical_receipt_records_tool_hashes=False,
                  intended_csr_sequence=[dict(operation="clear", csr=0x800, mask=0x88), dict(operation="set", csr=0x800, mask=0x88)],
                  intended_RMW_sequence=[dict(address=0x4002101C, operation="OR", mask=0x02020006), dict(address=0x40021018, operation="OR", mask=0x101D), dict(address=0x40021010, operation="OR", mask=0x02020006), dict(address=0x40021010, operation="AND_NOT", mask=0x02020006), dict(address=0x4002100C, operation="OR", mask=0x101D), dict(address=0x4002100C, operation="AND_NOT", mask=0x101D)],
                  intended_store_sequence=[dict(address=0xE000E42D, width=8, value=0), dict(address=0xE000E104, width=32, value=0x2000), dict(address=0xE000E424, width=8, value=0x20), dict(address=0xE000E104, width=32, value=0x10), dict(address=0xE000E427, width=8, value=0x30), dict(address=0xE000E104, width=32, value=0x80)],
                  original_extent_bytes=144, original_C_ABI_proved=False, native_replacement_compiled=False,
                  native_replacement_fits_original_extent=None, original_RV32_executed=False, rebuilt_RV32_executed=False,
                  emulation=False, network=False, hardware=False, physical_OTA_proved=False, goal_complete=False)
    (HERE / "audit-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, modes=list(mode_reports), allocations=691, raw_RELA=8280, UND=1, report=str(HERE / "audit-report.json"), native_replacement_compiled=False)))


if __name__ == "__main__":
    main()
