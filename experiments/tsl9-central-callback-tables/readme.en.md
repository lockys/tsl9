> Historical experiment snapshot. Current curated source/original-coordinate proof: [analysis/central-callback-integration-2026-10-26](../../analysis/central-callback-integration-2026-10-26/readme.en.md).

# Central-role tables and original-coordinate diagnostics

Reconstruct three observed readonly windows in C/C++, totaling **92 bytes**: the 17-cell relative event table at `0x1A548` and callback tables at `0x1A668` and `0x1A674`. Five non-null callbacks use genuine `R_RISCV_32` function references; one original null cell remains. These are selected windows. Original declaration extents and installed ROM read contracts remain unproved.

Verified results:

- C and C++ produce identical DATA objects: three positive-size OBJECTs, 92 bytes, and five relocations match the original BIN.
- Partial linking retains **66,600 CODE bytes, 3,922 DATA bytes, and 4,972 relocations**. Three DATA dependencies resolve; six undefined symbols remain. That count does not enumerate every runtime gap.
- The original-coordinate diagnostic ELF matches **70,522 original bytes**. All 17 event cells and five non-null callbacks reach real positive-size FUNC providers. Three HI/LO pointer materializations reach their actual DATA VMAs.
- All 71 CODE aliases and six real DATA labels remain. Ordinary continuations have no gaps; the conservative classifier retains the original `EBREAK` trap exception at `0x8034`.

The diagnostic ELF has **entry=0 and PT_LOAD=0**. No BIN, target execution, or hardware access. The six unprovided items are explicit reference-only constants, with no ABS FUNC providers or replacement bodies. Installed MCU/ROM/RAM/IRQ/BLE OTA contracts and global state bounds remain unproved.

**Not yet curated into `src/`; formal coverage stays at 89.03%.** Next, include the previous two CODE sources and this DATA source in the formal source proof, manifest, and original-coordinate flow. These results do not establish complete original-source recovery or flashability.

## Local verification

First build the existing component following the [event/helper instructions](../tsl9-central-event-callbacks/readme.en.md). Set `LLVM_BIN` to the NDK LLVM directory matching the spec hashes. Trial directories are create-only.

```sh
python experiments/tsl9-central-callback-tables/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-central-callback-tables/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
python experiments/tsl9-original-layout/build-v61.py --tool-dir "$LLVM_BIN" --trial central-callback-tables-v1
python experiments/tsl9-central-callback-tables/audit-layout-v1.py
```

Existing DATA/layout trials can be checked with the respective build script's `--replay` and full trial path. Use a fresh trial name for partial linking; retained receipts are preserved. No product feature was added. RSSI diagnostics, event tracing, and field-parser diagnostics remain future candidates.

[繁體中文](README.md) · [C source](src/central_callback_tables.v1.c) · [Evidence summary](summary.json)
