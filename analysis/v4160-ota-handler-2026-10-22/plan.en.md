# OTA command-handler implementation scope

Replace the raw representation of original `0x9C4A..0x9E5C` (530 bytes) with readable shared HOST/native C/C++. Official ID2966 SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; the body slice is `693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5`. The current complete image still retains original instructions here. The existing high-level HOST model is not integrated native C.

## Behavior to preserve

- U clears active before UID comparison, passes `(length-1)&255`, schedules both transition callbacks only for mode 1, then replies.
- S replies with the mode saved before UID comparison, rereads live mode after a successful comparison to decide active, and includes capability 1.
- W checks active, length 1026, BE16 page and original range in order. Preserve alignment copy, four 256-byte primitives, and per-word Flash-before-live-RAM readback. Readback comparison is not CRC/signature validation.
- R checks active, exact length 16 and UID14 before BE16 page and page reply. Do not add W's page limit.
- E checks active, exact length 15, mode 0 and UID14 before clearing active, scheduling and empty reply.
- Original `0x9DF4` is a linking `C.JAL`, not a tail jump. Halt/transfer stops later effects without rolling back earlier writes/schedules.

This W path writes the numeric BOOT alias `0x08001000 + page*1024`; it is not a proved way to self-flash a new Runtime.

## Implementation and validation

Keep branches and numeric arithmetic in shared readable C. Narrow ports provide synthetic HOST effects and native volatile memory/explicit opaque calls. Unknown HOST inputs and callee effects must stop rather than become zeros or success. Named C state does not prove equality of physical registers or caller prefixes; those remain additional ABI obligations.

First compile actual C11/C++17 ET_REL, LLVM IR, full MD and disassembly. Measure real FUNC extents and external relocations. Missing callee/callback providers remain true UND, without ABS/numeric providers, stubs, fake FUNC sizes or original BIN code fallback. Linking and replacement admission require actual source, providers, CFG/ingress and layout evidence. Report excess size rather than invent padding or search flags for a passing result.

Implementation and independent HOST fixtures focus on command gates, effect order, live rereads and selected stop boundaries, without rerunning the old 427,249-check matrix. Only machine-guarded local HOST programs may execute. Separate scopes review original operands and actual native outputs. No RISC-V execution/emulation, hardware operation or vendor service access is allowed.

MCU/ISA, installed resident/BOOT, RAM/GP/stack/IRQ, Flash/update acceptance and failure recovery remain unproved. This implementation scope does not replace the full goal; no rebuilt BIN is called flashable before those requirements pass.
