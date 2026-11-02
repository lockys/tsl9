# Direct GP scan of settings-pointer storage

Within the pinned layout's 69,412 bytes of selected code (23,602 instructions), plus the 3,124-byte linearly decoded window `[0x14056,0x14C8A)` (1,008 instructions), no standard RISC-V byte, halfword or word store directly based on GP overlaps `GP+[84,88)`. The scan also finds 74 ADDI instructions that form `GP+81..87`; 71 are immediately followed by a zero-offset word load through that register. In 57 of these the load overwrites the address register; in 14 it remains live and needs further tracing. The other three, at `0x12C82`, `0x133C0` and `0x18240`, require subsequent data-flow analysis.

The checker uses synthetic positive and negative boundary cases and pins candidate BIN, layout and ELF reader SHA-256. It only covers those encodings and selected windows and does not prove the pointer remains unchanged: reset writes through another base, while indirect pointers, other encodings, unselected code, resident, IRQ/DMA and runtime memory remain open.

Run with the pinned local inputs: `python experiments/tsl9-settings-pointer-gp-scan/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER>`. No target execution or hardware/OTA compatibility is established.
