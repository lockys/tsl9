# State packing and notification C/C++ reconstruction

Selected [state_events.c](../../src/native/receive/state_events.c), from `src/state_events.v2.c`. It requires original placement, adjacency and architectural register contracts. It is not an independent ordinary C API or a flashable BIN.

| Original range,end exclusive | bytes | instructions |
|---|---:|---:|
| `137C0–13B4C` | 908 | 314 |
| `13B4C–13BA6` | 90 | 42 |
| `13BA6–13BD2` | 44 | 14 |
| `13BD2–13C4E` | 124 | 46 |
| `13C4E–13CDC` | 142 | 45 |

Actual C11/C++17 compilation matches all1308B/461i after data-only original-VA control and function-pointer relocation encoding. C implements free-bank bit,constant and ordinary memory operations; SP/GP/S registers,frame,PC and control remain explicit architecture ports. Every opaque call ends a region; following regions sample then-live physical registers.

- `author-v2.py` statically authors fixed source; no register/memory simulation or target execution.
- Normal version1 objects were1752B: LLVM added SP/GP moves, failing original-byte comparison. Failed sources/checker/artifacts remain retained; they are not selected in current `src/`.
- Genuine `integrate-v1.py` partial link:7346B code+60B tables,676 FUNC/498 RELA/93 UND. It resolves2old entries and exposes27new getter dependencies. FUNC counts architectural symbols,including the pre-existing zero-size alias,not676features.
- Reuses the actual complete26B81B0 C implementation. Every global/local relocation symbol,section and value is checked. No new ABS provider or alias substitute.

Replay from the repository root. `LLVM_BIN` selects existing hash-matched Windows LLVM18. Other hosts/toolchains are unverified; raw artifacts remain local:

```sh
python -B experiments/tsl9-state-events/build-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-events/build/trial-v2
python -B experiments/tsl9-state-events/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-events/build/graph-v1
python -B scripts/check-state-events-publication.py
```

No HOST/ISA/hardware execution,synthetic corruption cases,new BIN or push. [Evidence and unknowns](../../analysis/state-events-2026-10-23/readme.en.md) · [繁體中文](README.md)
