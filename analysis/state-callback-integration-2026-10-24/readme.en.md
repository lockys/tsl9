# State-event and callback integration

[繁體中文](README.md)

Integrated complete state events, callbacks, nonduplicate state access and the 27 getters into the retained startup graph. **C11/C++17 produce identical objects: 12224B code + 516B data, 4276 original instructions, 807 relocations and 79 unresolved symbols.**

[Reader source](../../src/native/receive/state_leaf_reads.c) · [Integration checker](../../experiments/tsl9-state-callbacks/integrate-v1.py) · [Results/hashes](summary.json) · [Remaining providers](next-providers.json)

Added 294B state-access (20 regions), complete 314B feature-callback (31), complete 1308B state-events v2 (191), and 472B state readers/helpers (45): **2388B / 815 instructions / 287 regions**. The parent's duplicate 42B and two control references remain supplied by its genuine code. The full 13C4E notification path was retained.

All prior 9836B code and 516B data/table carriers remain unchanged. All 28 new aliases identify genuine nonzero code entries; no stubs or ABS substitutes were added. The audit checks 1070 real regions, 54 genuine aliases and every one of the 807 global/local/code/data relocation roles. Eight old gaps were resolved and five new gaps exposed: 82→79. Next entries: D272,B0FC,12B24,13D48,10630. Three existing clock/IRQ candidates remain unbound because their earlier original-code evidence was insufficient.

The collection remains 96 C/H files and 69 code units; independent pointer data brings it to 140 comparisons / 280 objects. Two additional selection objects come from the exact curated state-access C derivation. Earlier source-only receipts describe that historical phase; this integrated component has a separate proof.

Replay locally from the repository root:

```sh
python3 experiments/tsl9-state-callbacks/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-callbacks/build/component-v1
```

This is a **VMA-zero ET_REL partial object**, not flashable firmware. Final placement/fall-through, RAM ownership, private ABI, physical MCU/installed ROM/IRQ and OTA compatibility remain unproved. No target/model/ISA execution, hardware/network access, BIN generation, commit or push. Historical privacy findings remain unresolved.

A read-only state/provenance diagnostic view remains a proposal. Its prerequisite reader/event code is now integrated; the UI and physical field meanings are not established.
