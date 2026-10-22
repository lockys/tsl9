# Independent fixed-register ABI review

[繁體中文](README.md) | [English](readme.en.md)

All three complete fixed-register recipes compiled, but none satisfies the original resident leaf ABI. The actual selected C/C++ entries are compare 60 B / 23 instructions, fill 68 B / 24 instructions and copy 64 B / 22 instructions. Both languages produce identical complete objects for each mask.

Each mask reserves x5–x31 outside the original leaf's own-written registers plus A0/A1/A2. The compiler help explicitly advertises every used option for RISC-V. No adaptive mask changes were tried. The old extra writes (compare A6, fill A3/A6/A7, copy T0/A7) disappear, but every selected entry gains a 16 B stack frame, RA save/restore and RA/SP writes. Fill also temporarily writes A2. Advertised flags and successful compilation do not establish ABI preservation.

Each actual ET_REL contains eleven genuine global FUNC definitions, ten outside its selected entry. Whole code sizes are 454 / 492 / 418 B. Review accounts for every allocation and unused function, UND0, RELA0, actual volatile I/O, FENCE.I and the selected three-u32/u32 signature without a hidden context or sret argument. Raw operand decoding is cross-checked against complete LLVM static disassembly; the native functions are never executed.

Original compare requires A4=guard base, A5=saved guard word, and A3=last loaded byte or unchanged input when skipped. New compare leaves A3=result and A4=last byte or unchanged input. Original copy requires A5=base, A4=saved word and A3=last destination byte address; new copy leaves A3=base and, after a nonempty loop, A4/A5=end address. Fill's normal A4/A5 now match, but transient A2/A4 writes and stack spills differ. See `semantic-deltas.json` for precise facts.

Original compare/fill advance A0 before a potentially faulting byte access; the new entries advance it afterward. New stack stores precede the original guard READ32. Restoring normal RA/SP/A2 values cannot erase faults, asynchronous observations or alias effects. Conditional normal data/result projection additionally requires a valid private nonaliasing stack. Compare being 2 B shorter does not establish tail ownership; fill exceeds its original extent by 22 B and copy by 6 B. No placement is admitted.

`review.py --project-root ROOT --folder ACTUAL_LEAF_LANGUAGE_FOLDER --receipt NEW.json` creates an actual-object review receipt; `--replay NEW.json` rereads those artifacts. Each object has two real raw operand controls and one selected IR volatility control, all rejected. `check.py --project-root ROOT` verifies sealed source and retained summaries only. `selected-kernels.json` is a complete measured operand/CFG inventory, not an instruction executor.

No unchanged HOST matrix, baseline rebuild, native MMIO, RV32/ISA/ESIL execution, linking, BIN, hardware or network operation occurred. Previous seals and images remain unchanged. This candidate is not promoted to flashable firmware.

Delivery exposed a path-only issue: source pins use `apk-analysis/tsl9-*`, while D/P copies use `analysis/*`. The new reviewer now resolves both layouts with the existing `case()` rule. Native contracts, masks, operand inventories and acceptance conditions are unchanged. The original reviewer, original seal `9df1696d…` and historical actual receipts are preserved by `repair-history/path-resolution-2026-10-22` and their original receipt locations. Fresh receipts and replays use the same six existing objects; no recompilation or additional profile occurred.
