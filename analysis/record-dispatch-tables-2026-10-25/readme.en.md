# Bounded dispatch tables and field lookup DATA

[繁體中文](README.md)

Add five genuine readonly DATA objects totaling264B,no executable code. Four relative jump tables contain64 slots reaching49 distinct retained instruction entries. An eight-entry lookup uses unsigned_byte >> 5,bounded0..7.

- All four original/curated C11/C++17 data objects pass.128 typed ADD32/SUB32 relationships and every DATA byte match the official image after original-address encoding.
-149 C/H files,121 unchanged code units,two independent data units.246 source comparisons/492 objects;all prior242 function comparisons and1,453 artifact records retained.
- Resolve five prior providers without new dependencies;29 remain. Preserve all64,544 code bytes;DATA grows to2,911B with4,861 relocations.
- Original-coordinate coverage67,455/76,800B=87.83%. Static flow proof now covers11 guarded tables;the four new tables add64 proved slots and destinations,not64 physical features.

A read-only standard-library inspector lists bounds and actual compiled branch destinations. Tested on Windows;requires locally produced measurement ELFs/receipts. It never executes firmware or contacts hardware:

```sh
python3 experiments/tsl9-record-dispatch-tables/inspect-dispatch-tables.py --json --full
```

Byte coverage is not feature completion. Declared object extents,runtime indices,asynchronous ABI,installed ROM/RAM/IRQ/OTA and vehicle behavior remain unproved. No PT_LOAD or executable entry;no target/HOST-model/ISA execution,no backend access,no new BIN.

[Source](../../src/native/receive/record_dispatch_tables.c) · [Original DATA/bounds](evidence.json) · [Contracts](provider-contracts.json) · [Summary](summary.json) · [Next providers](next-providers.json) · [Implemented inspector](feature-candidates.json)

Replay requires pinned LLVM tools and local measurement receipts;set `LLVM_BIN` to the tool directory:

```sh
python3 experiments/tsl9-record-dispatch-tables/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-dispatch-tables/build/data-v1
python3 experiments/tsl9-original-layout/build-v55.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-dispatch-tables-v1
python3 experiments/tsl9-original-layout/verify-flow-v55.py --replay experiments/tsl9-original-layout/build/record-dispatch-tables-flow-v1
```
