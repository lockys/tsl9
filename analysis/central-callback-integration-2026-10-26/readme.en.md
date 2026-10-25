# Central callbacks: curated source and original-coordinate integration

Three verified translation units are now in `src/`: three callbacks, five helpers, and one event body add **2,056 CODE bytes / 686 instructions**; three readonly tables add **92 DATA bytes**.

- Full source scope: **156 C/H files, 123 CODE units, seven DATA units; 260 comparisons / 520 actual objects**. All previous 242 CODE results and 1,453 artifact records remain intact.
- Original coordinates: **70,522/76,800 bytes (91.83%)**, comprising 66,600B CODE and 3,922B DATA. All 4,972 relocation roles, 71 CODE aliases, and six real DATA labels remain.
- Static flow: 22,624 instructions, 4,347 direct transfers, 1,336 call-return positions, and 12 guarded tables. Ordinary continuation positions have no gaps. The 886 register-indirect transfers include returns; their complete runtime targets remain unproved.
- Tables: all 17 event cells and five non-null callbacks reach real positive-size CODE; three HI/LO arguments reach actual DATA. The four previously identified candidate callback CODE gaps now have bodies.

Six compiler-undefined symbols remain: two unprovided CODE targets and four DATA addresses. That count does not enumerate all runtime gaps. Installed callback/ROM ABI, original declaration extents, global RAM/index/async conditions, and physical compatibility remain unproved.

Outputs remain **diagnostic ELFs with entry=0 and PT_LOAD=0**, retaining the original EBREAK boundary and ten privileged returns. No BIN generation, target execution, hardware access, or vendor API calls. The 91.83% figure measures original-coordinate bytes, not feature completion, full source recovery, or flash readiness.

## Sources and replay

[Callback source](../../src/native/receive/central_callback_leaves.c) · [Event/helper source](../../src/native/receive/central_event_callbacks.c) · [Table source](../../src/native/receive/central_callback_tables.c)

With the pinned tools and retained artifacts available, run from the repository root with `LLVM_BIN`:

```sh
python experiments/tsl9-central-callback-tables/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-central-callback-tables/build/component-v2
python experiments/tsl9-original-layout/build-v62.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/central-callbacks-v2
python experiments/tsl9-original-layout/verify-flow-v62.py --replay experiments/tsl9-original-layout/build/central-callbacks-flow-v2
```

The source proof's `build/source-proof-v2.json` is create-only. Use `integrate-v2.py --replay` to check an existing source receipt as well. See the [src instructions](../../src/readme.en.md) for object organization. Only Windows with the pinned NDK LLVM is verified; other platforms require equivalent evidence.

Continue tracing remaining dependencies and original-device contracts. RSSI diagnostics, event tracing, and field-parser diagnostics are potential additions, not implemented features.

[繁體中文](README.md) · [Summary](summary.json) · [Evidence index](evidence.json) · [Provider contracts](provider-contracts.json)
