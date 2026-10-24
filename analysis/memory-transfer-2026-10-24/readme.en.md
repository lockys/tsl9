# Original19BF0 transfer reconstructed and integrated

[繁體中文](README.md)

The [selected C/C++ source](../../src/native/receive/memory_transfer.c) reproduces the complete original `0x19BF0–0x19CA6`: **182B/54 instructions**, including every path after the first return. All15 private regions and10 internal control relocations match in C11/C++17, with no external calls. Its genuine body now resolves `tsl9_callback_flow_external_19bf0` in the main component: **95 → 94 UND**, with no new dependencies.

Observed instructions implement forward byte/word transfer with a36B bulk path selected by alignment. The bulk path loads8 words,stores the first,loads the ninth,and completes the remaining stores in the original sequence. Original pointer updates,A0 retention and scratch registers are preserved. There are12 static load and12 static store sites and no added stack frame. This is static original/object evidence,not an execution trace or a standard memcpy ABI,overlap or buffer-bounds guarantee.

The original `0x129B0` caller transfers the96B constant block at `0x19CA8` to SP,then calls `0x128FE` at `0x129BA`. Field meanings and user-facing functionality remain unknown. [Caller evidence](../callback-flow-2026-10-24/evidence.json)

| Current main component | Result |
| --- | --- |
| Code/data | 14,046B/674B;1,211 sized code owners and71 retained aliases |
| Native partial link | 940 relocations,94 genuine UND;no ABS function providers or stubs |
| Original addresses | All **14,720B** match the official BIN after actual native linker placement |
| Static positions | 4,886 instructions/815 direct transfers;4,497 ordinary next and286 potential call-return positions are owned |
| Still unknown | 215 register-indirect transfers,10 MRET destinations,and breakpoint/debug resume at `0x8034` |
| Source organization | 99 C/H files,72 code units plus1 data unit;146 comparisons/292 objects total |

The layout remains a **non-loadable diagnostic ET_EXEC,entry0,PT_NULL only,zero PT_LOAD segments**, rather than an OTA BIN. The94 hidden local NOTYPE ABS constants represent original unknown-reference addresses,not function bodies. The full76,800B image,physical MCU,installed resident,private ABI,startup/RAM/IRQ and OTA remain unproved.

[Summary](summary.json) · [Static evidence](evidence.json) · [Source proof](../../experiments/tsl9-memory-transfer/build/source-proof-v1.json) · [Component receipt](../../experiments/tsl9-memory-transfer/build/component-v1/measurement.json) · [Original-address receipt](../../experiments/tsl9-original-layout/build/memory-transfer-v2/measurement.json) · [94 missing providers](next-providers.json)

Replay from the project root with the already-installed,pinned LLVM directory:

```sh
python3 experiments/tsl9-memory-transfer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-memory-transfer/build/component-v1
python3 experiments/tsl9-original-layout/build-v5.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/memory-transfer-v2
python3 experiments/tsl9-original-layout/verify-flow-v4.py --replay experiments/tsl9-original-layout/build/memory-transfer-flow-v2
```

Next: exact reconstruction of the complete clock `18834`,fields `1973C` and IRQ `9A42`. Existing inexact candidates stay unbound. Offline96B event-template comparison and read-only deferred-event diagnostics are extension candidates only;no new vehicle controls were added.

Only offline compilation and static checking were performed:no target/HOST-model execution,ISA emulation,hardware/network access,BIN generation,commit or push. Historical personal information remains unresolved. Earlier source receipts and layout diagnostics are preserved;their95-UND counts describe their historical stage.
