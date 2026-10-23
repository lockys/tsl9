# Mode 1 dispatch tree: offline C/C++ experiment

[繁體中文](README.md)

Reconstructs candidate original `[0x14D5E,0x1505C)`: 766 bytes / 229 instructions. Selected source `src/tree.v1.c` contains 96 genuine architectural regions. They require original-order placement and are not independently callable ordinary C ABI functions.

Actual C and C++ native builds in `build/trial-v2` passed: all nonrelocation bits match and all 95 relocation types and original destinations match. There are 63 genuine external symbols. Control immediates remain unresolved; this is not a flashable BIN or hardware-success claim. The trial is a bounded experiment, not a complete formal proof.

C owns constants and masks. Architectural ports express physical S0 loads, register moves, stack restoration and control transfers. Post-call use reads then-live SP/S0 without an ordinary callee ABI assumption. The common return keeps RA→S0→SP→RET order; external tails separately keep S0→RA→SP order.

`spec.json` records regions, typed edges and evidence hashes. Run a create-only trial with the pinned LLVM/profile:

```sh
python -B experiments/tsl9-feature-dispatch-tree/probe-v3.py --trial trial-new
```

Retained `trial-v1` compiled successfully but failed the old ELF reader's fewer-than-64-section bound. The actual tree object has 199 sections. The local reader changes only that bound to fewer than 512 and leaves the original reader intact. No target, ISA, HOST model, MMIO, hardware or network operations were executed.
