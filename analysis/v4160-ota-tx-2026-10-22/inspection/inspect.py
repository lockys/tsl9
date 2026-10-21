#!/usr/bin/env python3
"""Read-only inputs and static LLVM decoding; never execute target instructions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ENTRY = 0x8A56
SIZE = 280
IMAGE_BASE = 0x8000
OWNER = ".text.tsl9v4160.code_continuation_8a56"
FIRMWARE_SHA = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
BODY_SHA = "3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b"
PARSER_SHA = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"
OBJDUMP_SHA = "de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", required=True, type=Path)
    p.add_argument("--firmware", required=True, type=Path)
    p.add_argument("--object", required=True, type=Path)
    p.add_argument("--elf", required=True, type=Path)
    p.add_argument("--objdump", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    root = args.project_root.resolve()
    candidates = [root / "apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py",
                  root / "analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py"]
    parser = next(path for path in candidates if path.is_file())
    assert sha(parser.read_bytes()) == PARSER_SHA
    assert sha(args.objdump.read_bytes()) == OBJDUMP_SHA
    raw = args.firmware.read_bytes()
    assert sha(raw) == FIRMWARE_SHA and len(raw) == 76800
    spec = importlib.util.spec_from_file_location("tx_inspection_elf32", parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    obj, elf = module.ELF(args.object), module.ELF(args.elf)
    section = obj.byname[OWNER]
    linked_section = elf.byname[OWNER]
    body = obj.data(section)
    assert len(body) == SIZE and sha(body) == BODY_SHA
    assert linked_section["address"] == ENTRY and linked_section["size"] == SIZE
    assert body == elf.data(linked_section) == raw[ENTRY - IMAGE_BASE:ENTRY - IMAGE_BASE + SIZE]
    symbols = [s for s in obj.symbols if s["index"] == section["index"]]
    outgoing = [r for r in obj.relocations if r["owner"] == OWNER]
    section_references = [r for r in obj.relocations if r["symbol"]["index"] == section["index"]]
    incoming = [r for r in section_references if r["owner"] != OWNER]
    internal = [r for r in section_references if r["owner"] == OWNER]
    assert len(incoming) == 9 and len(internal) == 10 and len(outgoing) == 11
    result = subprocess.run(
        [str(args.objdump), "--disassemble", "--section=" + OWNER, str(args.elf)],
        capture_output=True, check=True,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "tx-llvm-disassembly.txt").write_bytes(result.stdout)
    record = {
        "schema": "TSL9-TX-static-inspection-v1",
        "target_entry": ENTRY, "image_mapping_base": IMAGE_BASE,
        "firmware_file_offset": ENTRY - IMAGE_BASE,
        "bytes": SIZE, "body_sha256": BODY_SHA,
        "firmware_sha256": FIRMWARE_SHA,
        "input_object_sha256": sha(args.object.read_bytes()),
        "address_witness_sha256": sha(args.elf.read_bytes()),
        "objdump_sha256": OBJDUMP_SHA, "parser_sha256": PARSER_SHA,
        "original_object_section": section, "linked_section": linked_section,
        "symbols": symbols, "outgoing_relocations": outgoing,
        "incoming_relocations": incoming, "internal_relocations": internal,
        "static_disassembly_sha256": sha(result.stdout),
        "static_only": True, "target_executed": False,
        "limits": [
            "Object symbols are reconstruction anchors, not recovered vendor symbol names.",
            "Recorded incoming RELA is bounded by the current object; unknown indirect callers remain unknown.",
            "ROM table implementations, physical SRAM and hardware behavior are not supplied or executed.",
        ],
    }
    (args.output / "inspection.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": True, "bytes": SIZE, "incoming_RELA": len(incoming),
                      "outgoing_RELA": len(outgoing), "body_sha256": BODY_SHA,
                      "firmware_file_offset": ENTRY - IMAGE_BASE,
                      "target_executed": False}))


if __name__ == "__main__":
    main()
