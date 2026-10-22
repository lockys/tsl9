# NV callback C/C++ and normal-return boundaries

[繁體中文](README.md)

This milestone connects original ID2966 V4.1.60 source to two conditional resident candidates and reconstructs the NV-read callback. Original chip, installed resident, memory ownership, IRQ and BLE OTA compatibility remain unproved. No new firmware BIN or native/MMIO/CPU/ISA/ESIL/hardware execution occurs.

## Actual C/C++ and independent inspection

Original `0x1979A..0x197B8` is 30 bytes / 13 instructions. Readable C11/C++17 both compile to 32 bytes / 14 instructions, one genuine global FUNC, UND0/RELA0/ABS0. Function bytes match, SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`. Each invocation freshly loads slot `0x4004C`, calls that value with `(entry A2, entry A0, uint32(entry A1<<2))`, ignores the callee result and normally returns zero. This conditional register-call surface is not a recovered original C prototype.

An independent reviewer reads ELF, all raw operands, LLVM text, complete IR def-use, successful logs and the entire `-MD` closure without using producer replay as its verdict. Each language rejects five raw-operand and three IR controls. The new function writes extra A3 and changes slot-load/frame and RA-restore/zero-return ordering. Full ABI, fault/IRQ equivalence, original extent fit and complete resident caller replacement remain unproved. [C/C++ source and compilation](implementation/readme.en.md); [independent native review](native-review/readme.en.md).

## ADC private scratch reconverges at normal callback exit

Three source ranges cover 470 bytes / 167 rows, with the prior full 946-byte / 352-row closure reread. The former is a subset, not additional coverage. Original call `0x198E6` dominates normal callback exit; `0x188E8` saves RA into callbackSP-4 as `0x198EA`, followed by no caller stack stores. Under existing valid private stack, disjointness, ordinary access, no-interference and eventual-return premises, that one word matches between original and ADC candidate at normal callback exit.

This does not prove equality immediately after the ADC callee, all RAM, faults or IRQs. Polling can remain zero forever, so callback return is not guaranteed. Six raw controls include a source CFG change bypassing the final overwrite while retaining the epilogue. [Exit dominance and premises](frame-review/readme.en.md).

## Config callbacks and numeric NV range

Original record+56 is `0x1979A`, +60 is `0x197BE`, and +8 is numeric `0x08077C00`. The resident's first read conditionally supplies that NV source, one word and destination tableSP+12, copying four bytes. If the fresh slot is the reviewed candidate copy and the value/stack/memory premises hold, its nonzero four-byte path overwrites A3 before reading it, eliminating the extra A3 difference for this specific call. Generic null/zero/shift-wrap-to-zero paths can still expose that difference.

The 50-byte write callback calls unlock, erase, program, lock and the `0x19764` SysTick-like polling routine. It always processes one 256-byte quarter; entry A1 does not control its length, and normal zero return does not establish controller success. Conditional table configuration yields three numeric 256-byte ranges in `0x08077C00..0x08077F00` (exclusive end), depending on the original record, defaults, fresh configuration, disjoint heap/stack/config and unknown callbacks. These addresses do not establish Flash ownership. Config+52 and fresh live S0+60 lifetime/effects remain conditional. [App bindings, complete callees and frontiers](binding-review/readme.en.md).

Proposed feature: offline NV compatibility diagnostics showing actual read/write lengths, alignment/range, callback premises and unresolved hardware requirements, preventing zero returns or numeric addresses from being treated as successful flashing. This remains a proposal, with no new physical-device feature.

The existing 78,848-byte `NOT-FLASH-VALIDATED-adc-caller-bank.bin` and all old seals remain unchanged; the new read callback is not integrated into that image. Default checkers inspect metadata only; actual modes require explicit firmware/candidate references or native folders/receipts. Python entry points are tested; denied Git Bash startup is not retried and shell runtime remains unverified.
