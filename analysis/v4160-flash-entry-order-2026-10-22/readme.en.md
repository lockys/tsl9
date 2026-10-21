# Original-size Flash program and entry-order reconstruction

[繁體中文](README.md)

Shared C11/C++17 source now compiles the program function to its original **100 bytes / 38 instructions**, replacing the previous 94-byte implementation. The six functions total **262 bytes / 99 instructions**, with individual sizes 64/8/30/14/46/100. There is no NOP padding, adjacent storage borrowing or six-byte fallback from a BIN. The final AND, store and return are part of the actual compiled function.

Three bounded source steps are retained separately. Binding only the aligned A0 result still produced 94 bytes and allowed ANDI before the initial CTLR read. A read-dependent A0 bridge plus the two original-stage A4 rematerializations produced 102 bytes. Binding the two initial poll mask results to their original A5 eliminated an extra `LI A5,0`, naturally reaching 100 bytes. Compiler profiles were not searched or changed. Failed-size diagnostic attempts are not treated as admitted results.

Actual code orders the initial read at `+4`, A0 ANDI at `+6`, and first CTLR store at `+14`. Original ANDI was at `+8`, so the old `+8` boundary lies inside a new four-byte instruction. Initial RMW uses A2 instead of original A5. Full GPR/fault prefixes, asynchronous interrupts and computed interior entries remain unproved.

The five recorded program loop targets remain at `+16/+26/+40/+56/+82`; erase's target remains at `+28`. Private branch roles must be admitted against actual new CFG evidence. Equal size or numeric address alone does not prove complete equivalence.

Each host language passes 481 cases / 247,191 assertions and six compiled behavior controls. The independent oracle is freshly compiled against this variant: 12 scenarios / 8,964 assertions and twelve compiled mutant rejections per language. Host executable format/architecture is checked before and after launch. Original and rebuilt RV32 are never executed or emulated. Live Linux/macOS results remain unavailable; macOS currently requires thin Mach-O Python.

```sh
python experiments/tsl9-v4160-flash-entry-order/verify.py --project-root . --language both
python analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/path/to/LLVM/bin --language both
```

Host entry requires Python and a C11/C++17 compiler; native entry also requires pinned local LLVM. POSIX wrappers are supplied. Windows Python/MSVC/LLVM evidence does not establish shell or other-OS execution.

See [source and independent tests](source-review/readme.en.md), [native ABI/order](ABI-review/readme.en.md), [implementation and receipts](implementation/readme.en.md), and [complete-image source plan](image-plan/readme.en.md).

The plan checks all 691 allocations, four filtered carrier units, 8,259 outside-owned RELA and twenty external entry references. Forty-two complete native compile units remain a plan. This milestone produces no new complete image or BIN and preserves all previous images.

Recorded updater differences also suggest local update-file checks and report export as possible future features; these are proposals, not implemented app update flows or new vehicle controls. Original chip, ROM, BOOT, physical Flash, interrupts and BLE OTA compatibility remain unproved. Nothing is verified flashable.
