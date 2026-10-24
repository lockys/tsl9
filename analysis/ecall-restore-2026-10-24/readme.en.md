# ECALL context restore: offline reconstruction

[繁體中文](README.md) · [Structured evidence](summary.json) · [C/C++ source](../../src/native/irq/ecall_restore.c)

The original **8448–8496 span, 78 bytes / 35 instructions**, is reconstructed and compiled as C11 and C++17. Both native outputs match every original byte. Explicit CSR, physical SP and register assembly ports remain; an ordinary C trap ABI is not established.

- The 14-byte entry uses `CSRS 0x804` with mask32 and obtains MEPC from then-live `SP+0`. The mask is not the full CSR value.
- The 64-byte suffix loads29 registers, adds128 to SP and executes MRET. It consumes an existing frame without allocating one or explicitly loading GP.
- The following two zero bytes remain separate data. [Frame correspondence](frame-correspondence.json) shows that this suffix and the LLE exit share identical64 bytes; it does not identify the frame creator or establish an IRQ ABI.

The genuine partial link contains **1168B code +456B data,153 RELA and4 UND**. Its parent1090B code and all data are unchanged. Vectors5 and8 own the true14-byte entry.60 nonzero slots bind to real code;2 vector slots remain external. These are component metrics, not whole-firmware completion.

Current `src/` has82 C/H files,55 code units and1 independently verified pointer-data unit.110 function-source comparisons cover220 objects;2 independent data comparisons cover4 more objects: **112 comparisons /224 objects**. Prior108 results and649 artifact records are unchanged.

[Four public receipts](publication-provenance.json) retain their original portable bytes; the complete curation receipt remains local. See the [experiment](../../experiments/tsl9-ecall-restore/readme.en.md) for normal read-only replays. Historical negative matrices were not executed.

Next: vector57 entry19BD4 and its three real providers. The [RTC candidate contract](next-rtc-candidate.json) separates a28B entry and10/16/20/4B helper regions, totaling78B/23 instructions.19296 tail-jumps19282;19272 retains status polling. Addresses,halfword widths and masks match the saved WCH RTC header, but this candidate has not been compiled and does not identify the physical MCU. The [bounded vector prefixes](remaining-vector-frontier.json) show979E branching beyond its first MRET; that return is not a whole-function boundary.

A worthwhile future feature is read-only trap/frame diagnostics. Only offline layout evidence exists today; hardware diagnostics require proven frame/CSR/RAM contracts and a safe readout path.

**No new firmware BIN, target/HOST/ISA execution, hardware or network access.** Main9008, resident40000, dynamic callbacks, physical MCU/ROM, final placement, full boot and BLE OTA remain unproved. Historical personal information remains in Git; no commit/push was performed.
