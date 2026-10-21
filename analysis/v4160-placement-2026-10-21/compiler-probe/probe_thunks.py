"""Synthetic jump-width/static range witnesses only; never patches an image."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
DEP = Path("apk-analysis/tsl9-v4160-reset-memory-2026-10-21/compiler-review")
PARSER = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"
VERIFIER = "6d5d0e43a1a909e8dbaa6a63027c0db7fc14b295c934b979b3d3169bdd38d456"
FIRMWARE = Path("exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin")
IMAGE = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def jump(raw, pc):
    """Decode only direct J immediate and destination fields, without execution."""
    word = int.from_bytes(raw, "little")
    if len(raw) == 2 and word & 3 == 1 and word >> 13 == 5:
        immediate = ((word >> 12) & 1)*2048 + ((word >> 11) & 1)*16 + ((word >> 9) & 3)*256 + ((word >> 8) & 1)*1024 + ((word >> 7) & 1)*64 + ((word >> 6) & 1)*128 + ((word >> 3) & 7)*2 + ((word >> 2) & 1)*32
        return dict(encoding="C.J", bytes=2, rd=0, displacement=sx(immediate, 12), target=pc + sx(immediate, 12))
    if len(raw) == 4 and word & 127 == 0x6f:
        immediate = ((word >> 31) & 1)*1048576 + ((word >> 21) & 1023)*2 + ((word >> 20) & 1)*2048 + ((word >> 12) & 255)*4096
        return dict(encoding="JAL", bytes=4, rd=(word >> 7) & 31, displacement=sx(immediate, 21), target=pc + sx(immediate, 21))
    raise ValueError("not a supported direct no-link jump")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path, required=True)
    a = p.parse_args()
    root = a.project_root.resolve()
    dep = root / DEP
    if sha(dep / "verify_native.py") != VERIFIER or sha(dep / "elf32.py") != PARSER:
        raise ValueError("immutable verifier dependencies changed")
    spec = importlib.util.spec_from_file_location("thunk_native", dep / "verify_native.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    tools = {key: v.tool(None, a.tool_dir, name) for key, name in (("clang", "clang"), ("linker", "ld.lld"), ("objdump", "llvm-objdump"))}
    folder = HERE / "build" / ("thunks-" + uuid.uuid4().hex)
    folder.mkdir(parents=True)
    cases = [
        dict(name="local_forward_CJ_max", base=0x1000, prefix="", instruction="c.j .Ltarget", suffix=".space 2044\n.Ltarget:\nret\n", target=0x17fe),
        dict(name="local_backward_CJ_min", base=0x1000, prefix=".Ltarget:\nret\n.space 2046\n", instruction="c.j .Ltarget", suffix="", target=0x1000),
        dict(name="external_near_CJ_spelling", base=0x186ba, prefix="", instruction="c.j external_target", suffix="", target=0x18834),
        dict(name="external_far_JAL_x0", base=0x186ba, prefix="", instruction="jal zero, external_target", suffix="", target=0x9ab8),
    ]
    reports = []
    for case in cases:
        build = folder / case["name"]
        build.mkdir()
        src, obj, linked = build / "thunk.s", build / "thunk.o", build / "NUMERIC-WIDTH-WITNESS-ONLY.elf"
        src.write_text(".option rvc\n.option norelax\n.text\n" + case["prefix"] + ".global probe_entry\n.type probe_entry,@function\nprobe_entry:\n" + case["instruction"] + "\n.size probe_entry,.-probe_entry\n" + case["suffix"], encoding="utf-8")
        commands = []
        record, _ = v.run([tools["clang"], "--target=riscv32-unknown-elf", "-march=rv32imac", "-mabi=ilp32", "-mno-relax", "-c", src, "-o", obj], build, "compile")
        commands.append(record)
        numeric = ["--defsym=external_target=" + hex(case["target"])] if "external_target" in case["instruction"] else []
        record, _ = v.run([tools["linker"], "--no-relax", "--no-undefined", "--entry=probe_entry", "-Ttext=" + hex(case["base"]), *numeric, obj, "-o", linked], build, "link")
        commands.append(record)
        record, _ = v.run([tools["objdump"], "--disassemble", linked], build, "disassembly")
        commands.append(record)
        elf = v.ELF(linked)
        symbol = next(s for s in elf.symbols if s["name"] == "probe_entry")
        raw = elf.function_bytes(symbol)
        decoded = jump(raw, symbol["value"])
        v.require(decoded["rd"] == 0 and decoded["target"] == case["target"], "actual raw jump target and no-link destination")
        v.require(len(raw) == (2 if case["name"].startswith("local_") else 4), "actual local compressed versus unresolved expanded widths")
        reports.append(dict(case=case["name"], source_sha256=sha(src), object_sha256=sha(obj), ELF_sha256=sha(linked), symbol_address=symbol["value"], raw_bytes=raw.hex(), decoded=decoded, commands=commands))
    firmware = root / FIRMWARE
    data = firmware.read_bytes()
    v.require(len(data) == 76800 and sha(firmware) == IMAGE, "exact original used only for prefix instruction framing")
    prefixes = []
    for name, entry in (("reset", 0x186ba), ("query", 0x18834), ("fields", 0x1973c), ("irq", 0x9a42)):
        offset = entry - 0x8000
        widths, extent = [], 0
        while extent < 4:
            size = 4 if data[offset + extent] & 3 == 3 else 2
            widths.append(size)
            extent += size
        prefixes.append(dict(name=name, entry=entry, first_instruction_bytes=widths[0], complete_prefix_for_4byte_thunk=extent, prefix_instruction_widths=widths, original_prefix=data[offset:offset + extent].hex(), two_byte_thunk_can_replace_whole_first_instruction=widths[0] == 2))
    # These are geometry examples, not established free storage or an integration plan.
    candidates = []
    for entry in (0x186ba, 0x18834, 0x1973c, 0x9a42):
        for destination in (0x9ab8, 0x1913a, 0x19762):
            delta = destination - entry
            candidates.append(dict(entry=entry, hypothetical_target=destination, displacement=delta, aligned=delta % 2 == 0,
                                   CJ_geometry_fits=delta % 2 == 0 and -2048 <= delta <= 2046,
                                   JAL_x0_geometry_fits=delta % 2 == 0 and -1048576 <= delta <= 1048574,
                                   target_storage_owned_and_free_proved=False))
    result = dict(schema="TSL9-synthetic-thunk-width-static-witness-v1", passed=True, runner_sha256=sha(Path(__file__)),
                  immutable_dependencies={"verify_native.py": VERIFIER, "elf32.py": PARSER}, tools={key: dict(path=str(path), sha256=sha(path)) for key, path in tools.items()},
                  witnesses=reports, original_sha256=IMAGE, original_prefixes=prefixes, geometry_examples=candidates,
                  encoded_immediate_ranges=dict(CJ=dict(bytes=2, minimum=-2048, maximum=2046, alignment=2), JAL_x0=dict(bytes=4, minimum=-1048576, maximum=1048574, alignment=2)),
                  candidate_slack_is_assumed=False, actual_original_entry_thunk_installed=False, original_image_changed=False, BIN_produced=False,
                  original_layout_integration_proved=False, source_original_ABI_proved=False, RV32_executed=False, ISA_emulation=False, network=False, hardware=False)
    receipt = folder / "verification.json"
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, receipt=str(receipt), sha256=sha(receipt), witnesses=[dict(case=r["case"], **r["decoded"]) for r in reports], original_prefixes=prefixes)))


if __name__ == "__main__":
    main()
