# Ring and receive chain at original addresses

[繁體中文](README.md)

[ring_insert.v3.c](src/ring_insert.v3.c) reconstructs official ID2966 `[0x12BC8,0x12C24)`. C11/C++17 nominal links match all92B/32instructions. C expresses index/stride/zero-extension arithmetic and the fresh provider read; explicit machine ports retain frame,slot memory and physicalS0/S1. **These are not ordinary C ABI functions.**

```sh
python3 -B experiments/tsl9-ring-insert/verify.py --language c --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-insert/build/my-check/c
python3 -B experiments/tsl9-ring-insert/verify.py --language cpp --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-insert/build/my-check/cpp
python3 -B experiments/tsl9-ring-insert/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/my-check/c/verification.json
```

Use new output directories. `LLVM_BIN` selects existing local tools. Only the recorded Windows NDK LLVM18 producer is verified; other toolchains are unverified. Windows can use`python`. No automatic tool downloads or flag search occur. Each language passes40negative controls; `--require-firmware-ready` must exit1.

Evidence boundaries:

- Five genuine FUNCs are8/16/50/10/8B. Three native relocations target real definitions; the nominal ELF resolves them without UND/RELA.
- AUIPC atPC`0x12BD2` plusADDI derives`0x2000C038`. Arbitrary rebasing changes this result; nominal evidence does not establish arbitrary placement.
- The queue has32slots×12B. It writesID16/length8,then freshly reads`LW32[0x0004004C]` and calls via`JALR A5`. A1/fullA2 remain inputs; ring does not validate the pointer or bound length.
- Post-call`SB S1,11(S0)` uses then-live physical registers. Success retains residentA0; full-table return retains inputA0. Fresh frame restore order is preserved.
- v1 required a compiler-managed reservedSP and emitted no object. v2 emitted92B but usedA0 for the provider address. v3 adds theA5 base port. Failed sources and raw local evidence remain unchanged.

[receive_graph.ld](receive_graph.ld) places seven reconstructed regions at original addresses,covering586 noncontiguous code bytes. The ELF container has additional headers/gaps and is not a complete APP or BIN. See [current analysis](../../analysis/ring-and-receive-graph-2026-10-23/README.md) for formal checks,source curation and receipts.

**Not flashable.** Dynamic resident pointer value/identity/preservation,other callers,IRQ/fault,memory ownership,physical chip and full OTA compatibility remain unproved. No target,ISA/MMIO emulation or hardware operation occurred; no complete firmware BIN was produced.
