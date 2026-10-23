# Queue packaging/forwarding filter

[繁體中文](README.md) · [C source](src/queue_filter.v1.c) · [Curated copy](../../src/native/receive/queue_filter.c)

This reconstructs official V4.1.60 `[0x82D2,0x838E)`:188B/69 instructions, including the post-RET cold path. C owns masks, shifts, OR and length arithmetic. Explicit ports preserve the frame, physical S registers/SP, fresh reads and calls. Seven FUNC symbols denote adjacent private regions rather than seven independent C ABI entries.

Both first-profile C11/C++17 builds produce188B/69 instructions. All166 whole noncontrol instruction bytes and1426 retained bits match the original. Actual ET_REL files retain seven relocations and one genuine8A56 UND. The2-byte C.JAL at8368 writes RA=836A; a non-linking C.J is different. S4 is updated before the length rejection, so a nonzero return does not prove forwarding.

```sh
# Output must be a new directory. Existing pinned local LLVM only.
python3 -B experiments/tsl9-queue-filter/probe.py --version 1 --out-dir experiments/tsl9-queue-filter/build/my-new-probe
python3 -B experiments/tsl9-queue-filter/verify.py --replay experiments/tsl9-queue-filter/build/verified-v1/c/verification.json
```

Formal receipts are `build/verified-v1/{c,cpp}/verification.json`. Public [C](../../analysis/queue-filter-2026-10-23/receipts/filter-c.json)/[C++](../../analysis/queue-filter-2026-10-23/receipts/filter-cpp.json) copies retain original portable LF bytes. Each language rejects186 controls:152 reparsed raw ELF,9 typed rows,20 SSA/port,2 full-IR and3 MD. Every control disables the whole-ELF pin;184 also disable the full-IR pin. `--require-firmware-ready` rejects with exit1.

The diagnostic link uses VMA0. The PC-derived table, original caller and full opaque-call/IRQ/memory/silicon/OTA compatibility remain unproved. Two-record processing, memcpy identity and forwarding success are not assumed. No download, target/ISA/MMIO execution or firmware BIN generation occurred.
