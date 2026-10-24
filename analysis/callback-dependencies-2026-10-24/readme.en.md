# Callback dependencies: static C/C++ reconstruction

[繁體中文](README.md)

Three complete functions (`11356..11442`, `13CDC..13D48`, `16E88..16F00`) add464B /170 instructions to [src](../../src/native/receive/callback_dependencies.c). All original bytes and29 typed relocations pass C11/C++17 object checks. [Raw evidence](evidence.json) · [Address contracts](provider-contracts.json).

- **Confirmed:** 11356 scans up to42 records with6-byte stride, compares a32-bit key, and forwards a selected byte or255. 13CDC requests length+1 storage, writes a byte length prefix, copies the original full length, queues the buffer and conditionally calls cleanup. 16E88 preserves a status result and configures the selected channel only when that result is zero.
- **Inference:** allocator/copy/queue roles follow original argument flow and numeric ROM slots. Installed-ROM names, length bounds, ownership and physical register effects remain unproved.
- **Unknown:** new dependencies155D0,16B50 and callback-address candidate13EB4. Three old entries resolve while three further providers emerge;115 genuine undefined symbols remain. [Inventory](next-providers.json).

The complete proof covers120 C/H files,188 source comparisons /376 objects, preserving all119 prior C/H files and1105 artifact records. The native component has26,880B code +714B data /1,755 relocations. All27,594 selected bytes match the original nominal coordinates in a diagnostic ELF with entry0 and **no PT_LOAD**. Static checks cover9,248 instructions,1,555 direct transfers and611 call-return positions; no ordinary continuation gaps.474 indirect targets,10 MRET targets and the original EBREAK/vector boundary remain outside execution proof. [Summary](summary.json).

[Feature candidates](feature-candidates.json) describe diagnostic reporting and record-change explanations. They are proposals with explicit evidence gates; neither is implemented or hardware-validated.

No target,host model or ISA execution;no hardware,BLE/CAN/Flash or vendor network access. No BIN generated. Physical MCU,installed ROM,RAM ownership,complete startup/IRQ and OTA compatibility remain unproved.
