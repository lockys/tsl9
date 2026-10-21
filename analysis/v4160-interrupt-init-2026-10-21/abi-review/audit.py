#!/usr/bin/env python3
"""Read-only ID2966 ABI/source audit; never execute the firmware."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess

IMAGE_SHA256 = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
SPANS = (
    (0x9A42, 0x9AD2, 46, "3d86f7124c682f02bbcc3b85162bfc37ebebbcd2631bbc3f5b2dfacf5e4c36c4"),
    (0x19124, 0x19142, 12, "ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864"),
    (0x19142, 0x19160, 12, "e74e208ea699962ecf8c71269627881ab8edfd64787710b410c6c74a3607d6d5"),
    (0x19160, 0x1917E, 12, "a5541a42d8ec2844fcd1d2df5492c90e2b140ce22ae79b02f50e330277c31b60"),
    (0x1917E, 0x1919C, 12, "bec2619b2d742c8bfa1b82087f6cea1ed8a133adb89b25258a487ef2e2d2648e"),
)
CALLS = (
    (0x9A5E, 0x19142, 0x9A62, 0x02020006, 1, 0x4002101C),
    (0x9A6A, 0x19124, 0x9A6E, 0x0000101D, 1, 0x40021018),
    (0x9A74, 0x1917E, 0x9A78, 0x02020006, 1, 0x40021010),
    (0x9A7E, 0x1917E, 0x9A82, 0x02020006, 0, 0x40021010),
    (0x9A88, 0x19160, 0x9A8C, 0x0000101D, 1, 0x4002100C),
    (0x9A92, 0x19160, 0x9A96, 0x0000101D, 0, 0x4002100C),
)
TAIL_WRITES = (
    (0x9A9A, 1, 0xE000E42D, 0),
    (0x9AA0, 4, 0xE000E104, 0x2000),
    (0x9AA8, 1, 0xE000E424, 0x20),
    (0x9AAE, 4, 0xE000E104, 0x10),
    (0x9AB6, 1, 0xE000E427, 0x30),
    (0x9ABE, 4, 0xE000E104, 0x80),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(image: pathlib.Path, r2: pathlib.Path, native: pathlib.Path) -> dict:
    data = image.read_bytes()
    assert len(data) == 76800 and digest(data) == IMAGE_SHA256, "wrong source image"
    commands = ";".join("pdj 60 @ " + hex(a) for a, _, _, _ in SPANS)
    proc = subprocess.run([str(r2), "-2", "-a", "riscv", "-b", "32", "-m", "0x8000", "-q", "-c", commands, str(image)], capture_output=True, text=True, check=True, timeout=60)
    groups = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("[")]
    assert len(groups) == len(SPANS), "missing disassembly group"
    retained = []
    by_pc = {}
    native_text = native.read_text(encoding="utf-8")
    captured = {int(pc, 16): (int(width), int(word, 16)) for width, word, pc in re.findall(r"\.(2|4)byte 0x([0-9a-f]+) # sourceVA([0-9a-f]+)", native_text)}
    native_matches = 0
    for (start, end, count, expected), group in zip(SPANS, groups):
        part = data[start - 0x8000:end - 0x8000]
        assert digest(part) == expected, "source span changed"
        rows = [row for row in group if start <= row["addr"] < end]
        assert len(rows) == count and sum(row["size"] for row in rows) == end - start
        cursor = start
        for row in rows:
            pc, size = row["addr"], row["size"]
            assert pc == cursor
            raw = data[pc - 0x8000:pc - 0x8000 + size]
            assert raw.hex() == row["bytes"]
            if start == 0x9A42:
                assert captured[pc] == (size, int.from_bytes(raw, "little")), "native capture differs"
                native_matches += 1
            cursor += size
            by_pc[pc] = row
        assert cursor == end
        retained.append({"start": start, "end_exclusive": end, "byte_count": len(part), "instruction_count": count, "sha256": expected, "rows": [{k: row[k] for k in ("addr", "size", "bytes", "opcode", "jump", "fail") if k in row} for row in rows]})
    assert by_pc[0x9A50]["opcode"] == "csrc 0x800, s2"
    assert by_pc[0x9AC2]["opcode"] == "csrs 0x800, s2"
    assert by_pc[0x9A4C]["opcode"] == "li s2, 136"
    for pc, target, continuation, _, _, _ in CALLS:
        assert by_pc[pc]["jump"] == target and by_pc[pc]["fail"] == continuation
    assert [by_pc[pc]["opcode"] for pc in (0x9A42,0x9A44,0x9A46,0x9A48,0x9A4A)] == ["addi sp, sp, -16","sw s2, 0(sp)","sw ra, 12(sp)","sw s0, 8(sp)","sw s1, 4(sp)"]
    assert [by_pc[pc]["opcode"] for pc in (0x9AC6,0x9AC8,0x9ACA,0x9ACC,0x9ACE,0x9AD0)] == ["lw ra, 12(sp)","lw s0, 8(sp)","lw s1, 4(sp)","lw s2, 0(sp)","addi sp, sp, 16","ret"]
    return {
        "schema": "TSL9-ID2966-interrupt-init-ABI-review-v1", "passed": True,
        "source_sha256": IMAGE_SHA256, "source_bytes": len(data), "source_base": 0x8000,
        "tool_sha256": digest(r2.read_bytes()), "native_capture_sha256": digest(native.read_bytes()),
        "native_capture_9a42_instruction_matches": native_matches,
        "byte_count": 264, "instruction_count": 94, "ranges": retained,
        "calls": [dict(zip(("pc", "target", "continuation", "mask", "nonzero_branch", "address"), call)) for call in CALLS],
        "tail_writes": [dict(zip(("pc", "width", "address", "value"), write)) for write in TAIL_WRITES],
        "normal_path_effect_counts": {"fresh_read32": 6, "write32": 9, "write8": 3, "csr_read_modify_write": 2},
        "normal_return": {"a0": "last fresh READ32(0x4002100C) & 0xFFFFEFE2", "a1": 0, "a4": 128, "a5": 0xE000E000, "s0_s1_s2_ra": "fresh original stack reloads", "sp": "current SP + 16 after fresh reloads"},
        "source_executed": False, "ISA_emulated": False, "hardware_accessed": False,
        "native_C_ABI_equivalence_proved": False, "interrupt_ABI_proved": False, "OTA_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=pathlib.Path, required=True)
    parser.add_argument("--r2", type=pathlib.Path, required=True)
    parser.add_argument("--native-capture", type=pathlib.Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.image.resolve(), args.r2.resolve(), args.native_capture.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
