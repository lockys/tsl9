# Complete clock query and field update reconstructed

[繁體中文](README.md)

The [selected C/C++ source](../../src/native/clock/clock_original.c) reproduces the original `18834–188E2` query, **174B/58 instructions**, and `1973C–19764` field update, **40B/11 instructions**. All16 private regions and11 internal control relocations match in C11/C++17,with no external calls. Both genuine entries are integrated: **94 → 92 UND**,with no new dependencies.

The query preserves every fresh peripheral read,the GP+64 byte lookup,the GP+108 word stores/readback,and all paths after the first return. A2 is written to `0x00C00000` only at `188B6` on the original external-source path;no entry snapshot/restore is introduced. Fields preserve unsigned DIVU:divide the GP+108 word by8,000,000,mask to8 bits,store a byte atGP+382,multiply by1000,and store a halfword atGP+380. These are static instruction facts,not physical frequency measurements.

| Current evidence | Result |
| --- | --- |
| New code | 214B/69 instructions;10 static load and4 static store sites;no added frame or external calls |
| Main component | 14,260B code+674B data;1,227 sized code owners and71 retained aliases |
| Native partial link | 951 relocations/92 genuine UND;no ABS function providers or stubs |
| Original addresses | All **14,934B** match the official BIN after actual native linker placement |
| Static positions | 4,955 instructions/826 direct transfers;4,560 ordinary next and286 potential call-return positions are owned |
| Still unknown | 217 register-indirect transfers,10 MRET destinations,and breakpoint/debug handling and resume at8034 |
| Source organization | 100 C/H files,73 code units plus1 data unit;148 comparisons/296 objects total |

The196B `clock_query.c` and38B `clock_fields.c` candidates are preserved but remain outside the active component;the original scopes are174B and40B. The new layout is a **non-loadable diagnostic ET_EXEC,entry0,PT_NULL only,zero PT_LOAD segments**,rather than an OTA BIN. Its92 hidden local NOTYPE ABS constants preserve unknown-reference addresses without implementing function bodies.

[Summary](summary.json) · [Original static evidence](evidence.json) · [Source proof](../../experiments/tsl9-clock-original/build/source-proof-v1.json) · [Component receipt](../../experiments/tsl9-clock-original/build/component-v1/measurement.json) · [Original-address receipt](../../experiments/tsl9-original-layout/build/clock-original-v1/measurement.json) · [92 missing providers](next-providers.json)

Replay from the project root using the already-installed,pinned LLVM directory:

```sh
python3 experiments/tsl9-clock-original/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-clock-original/build/component-v1
python3 experiments/tsl9-original-layout/build-v6.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/clock-original-v1
python3 experiments/tsl9-original-layout/verify-flow-v5.py --replay experiments/tsl9-original-layout/build/clock-original-flow-v1
```

Next:the complete original `9A42` IRQ initializer;its180B candidate stays unbound. Read-only clock-configuration/computed-value diagnostics are an extension candidate only;no device feature or transport interface was added.

The full76,800B image,physical MCU/peripherals,GP/table/RAM ownership,installed resident,private ABI,IRQ and OTA remain unproved. No target/HOST-model execution,ISA emulation,hardware/network access,BIN generation,commit or push occurred. Historical personal information remains unresolved;earlier receipts and counts retain their historical scope.
