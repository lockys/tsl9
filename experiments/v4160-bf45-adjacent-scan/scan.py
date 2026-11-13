"""Scan raw halfword-aligned AUIPC + load/store patterns; no execution."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin"
SHA256 = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
BASE = 0x8000
TARGET = 0x2000BF45
MASK = 0xFFFFFFFF


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def scan(data, base=BASE, target=TARGET):
    """Yield (offset, pc, raw bytes, mnemonic, base register, immediate, address, width)."""
    for offset in range(0, len(data) - 7, 2):
        first = int.from_bytes(data[offset:offset + 4], "little")
        second = int.from_bytes(data[offset + 4:offset + 8], "little")
        if first & 0x7f != 0x17:
            continue
        rd = (first >> 7) & 31
        if not rd or (second >> 15) & 31 != rd:
            continue
        opcode = second & 0x7f
        funct3 = (second >> 12) & 7
        if opcode == 0x03:
            operations = {0: ("lb", 1), 1: ("lh", 2), 2: ("lw", 4),
                          4: ("lbu", 1), 5: ("lhu", 2)}
            immediate = signed(second >> 20, 12)
        elif opcode == 0x23:
            operations = {0: ("sb", 1), 1: ("sh", 2), 2: ("sw", 4)}
            immediate = signed(((second >> 25) << 5) | ((second >> 7) & 31), 12)
        else:
            continue
        if funct3 not in operations:
            continue
        mnemonic, width = operations[funct3]
        pc = (base + offset) & MASK
        address = (pc + signed(first & 0xfffff000, 32) + immediate) & MASK
        if any((address + i) & MASK == target for i in range(width)):
            yield offset, pc, data[offset:offset + 8], mnemonic, rd, immediate, address, width


def main():
    data = REFERENCE.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != 76800 or digest != SHA256:
        raise ValueError(f"reference pin mismatch: length={len(data)}, sha256={digest}")
    hits = list(scan(data))
    print(f"reference: {REFERENCE}\nlength: {len(data)} sha256: {digest}")
    print(f"base: 0x{BASE:08x} target: 0x{TARGET:08x}; raw adjacent patterns: {len(hits)}")
    for offset, pc, raw, mnemonic, rd, immediate, address, width in hits:
        print(f"offset=0x{offset:05x} pc=0x{pc:08x} bytes={raw.hex()} "
              f"{mnemonic} base=x{rd} imm={immediate:+d} address=0x{address:08x} width={width}")


if __name__ == "__main__":
    main()
