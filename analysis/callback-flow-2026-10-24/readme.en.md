# Callback-flow and state-builder integration

[繁體中文](README.md)

Completed seven roots and two literal function-address targets: **1082B /368 instructions plus96B readonly data** in [src/](../../src/native/receive/callback_flow.c). The entire672B13346 state builder and its post-return paths remain intact; unknown behavior is not replaced by constants.

C11/C++17 objects are identical. Integrated component: **13864B code +674B data,4832 original instructions,930 relocations,95 unresolved symbols**. All prior12782B code and578B data carriers are unchanged. Seven new aliases bind genuine code; no stubs or ABS providers.

[Evidence](evidence.json) · [Results/hashes](summary.json) · [Pending providers](next-providers.json) · [Integration checker](../../experiments/tsl9-callback-flow/integrate-v1.py)

Preserves1070A/1061C clear/cancellation paths;1299E's96B source reference,129C4's14-iteration loop and12AA0 branches;complete13346 packing;135E6/1333C deferred flag references;and16DD4's two payload branches. Static address arithmetic shows1364E's store and13340's clear select the same original RAM address2000C794.1333C is passed with300 to9124;time units and field meanings remain unknown.19BF0's implementation remains unresolved.

Intermediate registered-callback labels mean literal function-address references only.1061C is passed to90B0's cancellation path and1333C to9124's scheduling path;no runtime registration or execution was observed. Existing symbol names are reused only at identical original PCs;unknown implementations remain UND. Seven old gaps closed and21 new entries exposed: **81→95**;symbol count is not completion coverage.

The collection has98 C/H files and71 code units. Including independent pointer data,144 comparisons/288 objects pass. All prior140 results and841 artifact records are unchanged;the manifest is an exact97-to98 extension. Frozen checkers were not changed;old whole-manifest replay on the new manifest is not claimed.

```sh
python3 experiments/tsl9-callback-flow/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-flow/build/component-v1
```

Next:prove original-address layout/fall-through for retained code/data before expanding new providers. This remains a VMA-zero ET_REL partial object,not flashable firmware. Full placement,RAM ownership,private ABI,physical MCU/installed ROM/IRQ and OTA compatibility remain unproved. No target/model/ISA execution,network/hardware access,BIN generation,commit or push. Historical privacy findings remain unresolved.

Feature candidate:read-only deferred-flag/state-source diagnostics. The shared-address evidence is useful,but no UI or control-policy changes were implemented.
