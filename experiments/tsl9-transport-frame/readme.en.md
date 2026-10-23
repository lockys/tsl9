# Transport framing, copy and checksum

[繁體中文](README.md) · [Current C source](src/transport_frame.v6.c) · [Curated copy](../../src/native/receive/transport_frame.c) · [Original instruction contract](../../analysis/transport-frame-2026-10-23/original-contract.en.md)

This reconstructs official V4.1.60 `[0x8A56,0x8B6E)`: 280B and 96 instructions, including the reachable post-RET copy loop. The 13 FUNC symbols are adjacent private architectural regions, not independent ordinary C ABI entries. C owns free-register unsigned arithmetic, checksum and volatile memory. Physical S-register operations, frames, branches, opaque calls and the tail transfer use explicit architecture ports.

Only **v6** is current. Actual C11/C++17 native and partial ELFs contain 280B/96 instructions. All 246 complete noncontrol instruction bytes and 2133 retained bits match the original BIN. Nine local RELAs remain pending. Zero UND does not identify either admission provider or the tail provider. The diagnostic VMA is zero; original AUIPC placement is a separate obligation.

Both admissions freshly read `0x4013C`: original `LUI 0x40` gives `0x40000`, plus 316. The earlier `0x40013C` note was an address-scale error. The initial unsigned A3≤1039 guard precedes opaque calls and does not bound post-call S0. Only the comparison temporary is narrowed to uint16; source/destination addresses retain the full 32-bit A1 index. Zero-copy preserves inherited A6. The success path restores RA/S registers and SP before a non-linking `JR T1` through fresh `[0x40050]`.

The formal checker rejects 263 mutations per language: 216 reparsed raw ELF, 11 typed rows, 31 SSA/port, two complete IR and three MD controls. All disable whole-ELF pins; 261 also disable complete IR pins. Actual source/tool/header identities, five producer recipes and two MD dependencies are checked together.

```sh
# Existing pinned Windows LLVM only; output must be a new directory.
python3 -B experiments/tsl9-transport-frame/probe.py --version 6 --out-dir experiments/tsl9-transport-frame/build/my-new-probe
python3 -B experiments/tsl9-transport-frame/verify.py --replay experiments/tsl9-transport-frame/build/verified-v1/c/verification.json
```

Formal local receipts are `build/verified-v1/{c,cpp}/verification.json`. Adding `--require-firmware-ready` must reject with exit 1. This milestone used only the existing hash-bound Windows LLVM; other operating systems were not tested and no tools were downloaded.

[source-history.json](source-history.json) records six source revisions and hashes of original local outputs: v1/v3 failed compilation, v2/v4 failed placement checks, v5 failed the ANDI/store ordering gate, and v6 passed the unchanged profile. Earlier versions contain incorrect addresses or instruction ordering, remain audit material and were not promoted to `src/`.

This is offline compiler/link/static evidence. No target, ISA, MMIO or HOST behavior was executed; no full firmware BIN, Bluetooth operation or hardware test was performed. Resident identity, complete IRQ/memory/ROM/silicon/OTA compatibility and seat/DND attribution remain unproved. Safe flashing is not established.
