# Static wiring of the real C function to the original caller

[繁體中文](README.md)

This is an offline experimental candidate, not verified flashable firmware. The existing77824-byte source-wired image has SHA256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`; its original4-byte JAL at `0x19896` was unchanged. A small assembler source references the real C symbol; LLVM assembler/lld produce and resolve an actual `R_RISCV_JAL`, without hand-encoded opcodes or numeric ABS providers.

Independent ABI evidence supports only the19896 normal caller projection under a valid aligned/private/nonwrapping144-byte stack, normal accesses, disjoint stack/code/config/MMIO, no asynchronous interference and exclusion of private callee-frame residue from observable outputs. Full original callee ABI, fault/IRQ and physical equivalence remain unproved.

Two exact RX LOADs own `0x19896/4B` and `0x1B000/110B`; no borrowed headers, holes or NOBITS. The110-byte real C function equals its native.o definition byte-for-byte. Linker GC actually removes the other four genuine global functions. Caller RA remains `0x1989A`.

Only offsets71831/71832/71833 change in the inherited77824bytes; the old88-byte ADC body remains. One appended page contains110bytes of genuine C code and914bytes of explicit FF packaging data. Raw BIN encodes no hardware execute permissions. Total78848bytes/77pages only fits the existing numeric page range; it does not prove Flash ownership.

C11/C++17 candidates share SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`. Four actual image controls mutate inherited data, caller, C payload or page tail and reject. Default checks read metadata; explicit replay rereads ELF/native/BIN/ABI receipts, tools, actual LOADs and full preimage differences without compilation or execution.

The candidate inherits the older568-byte OTA component and its ROM address-witness limits. New ADC wiring does not prove whole-image provenance, ROM identity, BOOT, interrupts, memory ownership or BLE OTA. Old/new candidates are separate. No native, MMIO, ISA or hardware execution occurred.
