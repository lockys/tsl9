# Conditional ADC caller compatibility and a new experimental BIN

[繁體中文](README.md)

The shared C algorithm and real volatile IO remain unchanged. One complete source-derived caller bank permitsx10..x16 and reserves otherx5..x31 registers. C11/C++17 selected code matches:110B/42instructions, whole five-function object266B/103instructions, UND0/RELA0/ABS0. A7/T/S/GP/TP are not written. A new16-byte frame saves/restores RA; A2/A6 still change.

An independent actual946B/352-row source read confirms A0..A6 are overwritten before later use after19896, while escaping preserved registers must remain intact. **Only this caller's normal effect/result/register projection is supported, under a valid aligned/private/nonwrapping144-byte stack, normal accesses, disjoint stack/code/config/MMIO, no asynchronous interference and exclusion of private callee-frame residue from observation.** Full original callee ABI, fault/IRQ prefixes and the original88-byte extent remain unproved. [Compiler sources](implementation/readme.en.md); [independent source/ABI evidence](abi-review/readme.en.md).

A separate [NOT-FLASH-VALIDATED candidate](../../artifacts/offline-images/ID2966-V4.1.60-adc-caller-bank/readme.en.md) contains78848bytes, SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`. LLVM assembler/lld wire the real19896 JAL to the real C definition at1B000, retaining RA1989A. Only three bytes differ in the inherited77824-byte image; the original88-byte ADC function remains. One appended page contains110bytes of C code and914bytes of explicit FF packaging data. No old tail or unknown hole is borrowed. Linker GC actually removes four unused genuine global functions; two exact LOADs remain.

C/C++ candidate files are identical. Independent review reads ELF/raw JAL/BIN and verifies the entire preimage, real C bytes, LOADs and GC instead of merely accepting builder replay. [Integration](integration/readme.en.md); [independent integration audit](integration-review/readme.en.md). Raw BIN encodes no hardware execute permissions;77pages only fit the existing numeric bound, not proven Flash ownership.

Both candidate resident postcallback main functions and necessary direct dependencies were read:8bodies/1056B/359rows each,2112B/718rows total, retaining sparse HEX without hole filling. The main function builds heap/table/function-pointer state. Allocation failure notification comes from slot400A4/config+52. Computed callbacks also use config+56 and fresh liveS0+60; the latter equals config+60 only if the earlier callback preserved S0. Callback effects, heap aliasing and loops remain open. Closed bounded source CFGs do not prove whole initialization return or config52 lifetime. [Source frontier and premises](continuation-review/readme.en.md).

Feature proposal: an offline compatibility report showing observable registers, stack bounds, callback/NV pairing and heap allocation diagnostics. This is not a new installed-device feature.

**This is not verified flashable firmware.** It inherits the older568-byte OTA component and ROM address-witness limits. Actual chip, installed ROM, BOOT, Flash/NV/RAM ownership, fault/interrupt and physical BLE OTA remain unproved. Old images/seals are preserved. No unchanged HOST matrix, native/MMIO/CPU/ISA/hardware execution or flashing occurred; work was static analysis, compilation, linking and candidate packaging.

Default checks read metadata; actual receipts/reference inputs must be explicit. Python entry points were verified; the previous Git Bash `NtCreateDirectoryObject0xC0000022` rejection was not retried, so shell runtime remains unverified.
