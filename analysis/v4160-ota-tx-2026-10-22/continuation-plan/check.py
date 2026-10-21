#!/usr/bin/env python3
"""Check static literal address pairs and ROM slots without a CPU model."""
import argparse
import hashlib
import json
from pathlib import Path

FIRMWARE_SHA = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
BSS = 0x2000B18C
PAIRS = [(0x86C0, 9), (0x876C, 25), (0x8AD6, 13), (0x8E9C, 10)]
SLOTS = [(0x8A82, 0x8A86, 15, 0x13C), (0x8AA6, 0x8AAA, 15, 0x13C),
         (0x8B42, 0x8B46, 6, 0x50)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def signed12(n):
    return n - 4096 if n & 2048 else n


def pcrel(raw, pc, rd):
    a, b = [int.from_bytes(raw[n:n + 4], "little") for n in (0, 4)]
    need(len(raw) == 8 and a & 127 == 0x17 and (a >> 7) & 31 == rd, "Actual AUIPC destination")
    need(b & 0x707F == 0x13 and (b >> 7) & 31 == rd and (b >> 15) & 31 == rd,
         "Actual paired ADDI same source/destination")
    address = (pc + (a & 0xFFFFF000) + signed12(b >> 20)) & 0xFFFFFFFF
    need(address == BSS, "Actual static PC-relative target")
    return dict(PC=pc, raw_hex=raw.hex(), GPR=rd, target=address)


def rom_pair(raw, pc, rd, offset):
    a, b = [int.from_bytes(raw[n:n + 4], "little") for n in (0, 4)]
    need(len(raw) == 8 and a == 0x000407B7, "Actual LUI A5,0x40")
    need(b & 0x707F == 0x2003 and (b >> 7) & 31 == rd and (b >> 15) & 31 == 15,
         "Actual LW target and base")
    need(signed12(b >> 20) == offset, "Actual ROM pointer slot offset")
    return dict(PC=pc, raw_hex=raw.hex(), target_GPR=rd, slot_address=0x40000 + offset,
                actual_pointer_word_known=False, callee_implementation_known=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    original = args.firmware.read_bytes()
    need(hashlib.sha256(original).hexdigest() == FIRMWARE_SHA, "Actual official original firmware")
    refs = [pcrel(original[pc - 0x8000:pc - 0x8000 + 8], pc, rd) for pc, rd in PAIRS]
    slots = [rom_pair(original[pc - 0x8000:pc - 0x8000 + 8], pc, rd, offset)
             for pc, _, rd, offset in SLOTS]
    controls = []
    for pc, rd in PAIRS:
        raw = bytearray(original[pc - 0x8000:pc - 0x8000 + 8])
        # Change the actual LO source register, independently of the whole-file hash.
        raw[5] ^= 0x80
        try:
            pcrel(raw, pc, rd)
        except ValueError:
            controls.append(dict(PC=pc, mutation="ADDI source register", rejected=True))
        else:
            raise ValueError("Static reference operand mutation was accepted")
    for pc, _, rd, offset in SLOTS:
        raw = bytearray(original[pc - 0x8000:pc - 0x8000 + 8])
        raw[6] ^= 0x10
        try:
            rom_pair(raw, pc, rd, offset)
        except ValueError:
            controls.append(dict(PC=pc, mutation="LW slot offset", rejected=True))
        else:
            raise ValueError("ROM pointer slot mutation was accepted")
    result = dict(schema="TSL9-TX-static-continuation-plan-v1", passed=True,
                  firmware_sha256=FIRMWARE_SHA, address_pairs=refs, nominal_ROM_slots=slots,
                  operand_controls=controls, complete_reference_inventory=False,
                  ROM_implementation=False, target_execution=False, ISA_emulation=False,
                  hardware=False, OTA_ready=False)
    if args.report:
        need(not args.report.exists(), "Create-only report")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, static_BSS_pairs=len(refs), nominal_ROM_pointer_slots=len(slots),
                          operand_controls=len(controls), target_execution=False, OTA_ready=False)))


if __name__ == "__main__":
    main()
