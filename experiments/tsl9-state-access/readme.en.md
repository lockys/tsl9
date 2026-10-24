# State-access C/C++ reconstruction

Source: [state_access.c](../../src/native/receive/state_access.c). Complete original spans `82A8–82D2` and `10032–10158`: 336B/108 instructions in 24 architectural regions. Actual C11 and C++17 compilation matches every byte after data-only original-VA control relocation encoding.

These regions require original placement and adjacency; they are not independent ordinary C ABI functions. C implements memory/arithmetic; PC, control and register handoff remain explicit architecture ports. ROM, bounds, IRQ, field meanings and physical hardware remain unproved.

- `build-v1.py`: normal compilation/read-only replay; both languages pass `trial-v1`.
- `integrate-v2.py`: genuine partial link and complete input/symbol/relocation checks: 6038B code+60B tables,485 FUNC,435 RELA,68 UND.
- FUNC count includes a size0 linker alias to the existing, proved24B C provider. It is not an additional implementation. Version1 expected size24; its failed checker and `build/graph-v1` artifacts remain retained.
- No synthetic corruption cases, HOST model, ISA execution, hardware access or new BIN.

Replay from the repository root. `LLVM_BIN` selects existing hash-matched Windows LLVM18; no tool downloads or other-host validation:

```sh
python -B experiments/tsl9-state-access/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-access/build/trial-v1
python -B experiments/tsl9-state-access/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-access/build/graph-v2
python -B scripts/check-state-access-publication.py
```

[Evidence and unknowns](../../analysis/state-access-2026-10-23/readme.en.md) · [繁體中文](README.md)
