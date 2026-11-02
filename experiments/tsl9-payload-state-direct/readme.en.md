# Limited state-address scan in the newly opened range

[繁體中文](README.md)

Run `python scripts/verify-payload-state-direct.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. Assuming GP is `0x20004000`, scan consecutive decoded rows from `0x14056..0x14C8A` for directly derivable accesses in a single linear segment to the counter, mode, phase or four sequence-state bytes.

Each C/C++ original carrier produces 1,008 decoded rows and no direct hits under this method. Synthetic positive controls cover GP-relative and PC-relative writes of different widths, plus a branch-barrier control. Not all rows are proven executable. The scan does not follow control-flow joins, indirect pointers, calls, interrupts, DMA or other address calculations. **No hits do not rule out other writers or establish global index bounds.** It does not print firmware operands or authentication material and does not execute the target.
