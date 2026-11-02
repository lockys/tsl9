# Direct writes to the `GP+167` state byte

A scan of 69,412 bytes of selected code plus the 3,124-byte linearly decoded `[0x14056,0x14C8A)` window covers 24,610 instructions. Among standard RISC-V byte, halfword and word stores directly based on GP, the only overlap with `GP+167` is `sb a0,167(gp)` at `0x93A2`. Immediately before it, `0x939E` executes `seqz a0,a0`, so this particular explicit write stores 0 or 1 regardless of the previous value.

If reset clears the byte, all subsequent writes come only from this instruction, and GP, memory, control flow and asynchronous behavior satisfy their assumptions, each later read is 0 or 1. This is conditional induction: reset writes through another base, while indirect pointers, other encodings, unselected regions, resident, IRQ/DMA and exceptions remain open. It does not establish product meaning, execution on the device or the global value range.

Run `python experiments/tsl9-state167-writers/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER> --r2 <R2_EXECUTABLE>` to check pinned input hashes, the scan, writer instructions and four synthetic boundary cases. The target is not executed.
