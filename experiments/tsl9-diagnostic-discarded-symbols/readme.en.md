# Undefined symbols in the sparse resident diagnostic ELF

Each C/C++ diagnostic ELF has 44 undefined symbol-table entries: 43 are defined in the input aggregate but belong to alternative `.text` or `.bss` sections discarded by the linker script; `tsl9_runtime_reset_stack_top` was already undefined in the aggregate. The input aggregate has 24 relocations to these 44 names across 10 source sections, and all 10 relocation-owner sections are discarded. The final ELF retains no relocations.

This explains why `--no-undefined` succeeds for this diagnostic layout despite undefined symbol-table entries. It **does not** establish complete source recovery, functionality of discarded alternatives, installed resident, RAM ownership or data bounds. These counts and classifications depend on this specific layout; indirect calls and runtime behavior are out of scope.

After the [sparse reference link](../tsl9-sparse-resident-link/readme.en.md), run `python scripts/verify-discarded-symbols.py --project-root . --conditional-dir <BUILD_DIR>/conditional-link --sparse-dir <SPARSE_OUTPUT_DIR>` to inspect the actual C and C++ ELFs, input relocations and `/DISCARD/` rules. A synthetic negative control is included; the target is not executed.
