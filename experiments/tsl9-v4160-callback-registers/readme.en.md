# Callback registers and live-GP native experiment

[繁體中文](readme.zh-TW.md)

This readable C11/C++17 component is checked against the original 632-byte callback at 0x8614. The measured candidate has **624 bytes and 223 instructions**. It is not a replacement firmware BIN.

| Layer | Function bytes / instructions | GP use sites | Frame / saved registers |
| --- | --- | --- | --- |
| Previously sealed component | 658 / 241 | 16 snapshots | 48 bytes / 12, including S10 at SP+0 |
| Reserved S10/S11 diagnostic | 656 / 240 | 16 snapshots | 48 bytes / 11, no SP+0 |
| Current live-GP candidate | 624 / 223 | 6 actual live uses | 48 bytes / 11, no SP+0 |
| Explicit save-order output | 624 / 223 | unchanged | Only two existing C.SWSP words exchanged |

The immutable native profile adds only `-ffixed-x26 -ffixed-x27`. Source changes replace six `s->gp` uses with `CB_GP(h)` and remove native entry/post-call snapshots. HOST expansion remains the same mutable `values.gp` field. The source identity proof establishes unchanged shared algorithm semantics; unchanged HOST suites were not rerun.

The separate `postpass/frame.py` explicitly swaps the two existing 2-byte RA@44/S0@40 saves into S0, RA order. It emits no opcode, reads no original BIN and leaves every other ELF byte unchanged. The final pipeline is **C/C++ compilation plus explicit save ordering plus the standard linker**, not compiler output alone.

## Run

Python 3 and a local LLVM directory matching the recorded SHA-256 pins are required. Windows NDK LLVM was actually tested. Python/shell interfaces are portable; Linux/macOS compiler runs and equivalent cross-platform tool identities are not claimed. A different compiler hash is rejected.

```sh
python3 -B experiments/tsl9-v4160-callback-registers/verify.py --tool-dir /path/to/pinned/llvm/bin --language both
sh experiments/tsl9-v4160-callback-registers/verify.sh --tool-dir /path/to/pinned/llvm/bin --language both
python3 -B experiments/tsl9-v4160-callback-registers/verify.py --replay /absolute/path/to/ordered/c/verification.json
```

On Windows, use `python -B`. `--project-root ROOT` selects the checkout. Optional `--build-root NEW` must be a nonexistent child of this model's build directory; overwrites are rejected. The default uses a UUID. Read-only replay invokes neither compilers nor the component and rejects fresh-build options.

Outputs are `build/NEW/pre/{c,cpp}` and `build/NEW/ordered/{c,cpp}`. The former retains raw compiler object/IR/MD/ELF/disassembly and its probe receipt. The latter retains ordered object/receipt, standard link and formal verification receipt. Generated objects, ELF, IR and logs remain local build archives. Only source, text and selected receipt metadata are published.

## Evidence and limits

Actual instruction fields and LLVM text show no x26/x27 operand, no GP write, six live GP operands, 15 opaque JALRs, eleven 32-bit save/load pairs, no SP+0/replacement spill/undefined symbol/extra allocation. MD covers three project files and one actual Clang resource `stdint.h`. Formal receipts bind stable source/tool identities, eight explicit tool stages, complete artifacts, raw/ordered machine and IR checks, five artifact controls, four ordering controls, three disassembly controls and four recipe/MD controls.

Only the **relative order of eleven stack stores** is repaired. Original entry SLLI timing, opaque-call return addresses, physical scratch/S-register mappings and unknown ROM preservation remain unproved. Numerical size fits, but **eight original tail bytes have no established ownership**. No padding, old-byte reuse, fixed-placement claim or whole-image update is made.

No RV32 execution, ISA emulation or hardware I/O occurred. No BIN was produced; the existing whole-image artifact is unchanged. Full ABI, board compatibility, physical programming, BLE/OTA and safe hardware operation remain unproved.
