# Action dispatcher: complete static C/C++ reconstruction

[繁體中文](README.md)

Four complete functions10DCC,13EB4,155D0,16B50 add3,904B /1,571 instructions and a1,012B readonly relative table to [action_dispatch.c](../../src/native/receive/action_dispatch.c). The separate legacy record_dispatch.c is retained unchanged. C11/C++17 checks cover all original code/table bytes and252 relocations. [Evidence](evidence.json) · [Contracts](provider-contracts.json).

- **Confirmed:** 155D0 uses253 signed relative words and174 genuine instruction targets;39 slots select its restore/return block. Initial state gates and a pending-byte path precede this table,so an excluded selector is not necessarily a no-op. [Numeric map](case-map.json).
- **Confirmed:** 13EB4 checks two descriptor slots,sends the length-prefixed payload when each condition holds,and tails to the original cleanup slot. 16B50 selects0x20/0x24 for the proven caller indices and passes payload FF E0 00 00. ROM/physical meanings remain unproved.
- **New evidence:**9508 now has both an address reference and a direct control reference; its body is still unprovided.
- **Unknown:** four old entries resolve and74 further dependencies emerge;185 true imports remain. [Inventory](next-providers.json). Product action names are not guessed from numbers.

Complete source proof:121 C/H files,190 comparisons /380 objects;all prior120 C/H files and1117 artifact records are unchanged. The component has30,784B code +1,726B data /2,007 relocations. All32,510 selected bytes match original nominal coordinates in a diagnostic ELF with **no PT_LOAD**,entry0. Static checks cover10,819 instructions,1,801 direct transfers and654 call-return positions without ordinary continuation gaps. The table guard/253 candidates are checked against actual linked bytes; runtime targets,482 indirect transfers,10 MRET and trap resumption remain unproved. [Summary](summary.json).

[Feature candidates](feature-candidates.json) cover an offline numeric action inventory and two-slot payload diagnostics. These do not claim a working device feature. No target/host/ISA execution,hardware,BLE/CAN/Flash or vendor network access;no BIN generated. MCU,installed ROM,RAM/IRQ/startup and OTA compatibility remain unproved.
