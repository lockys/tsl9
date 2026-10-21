# Compiler diagnostics for the TX entry

[繁體中文](README.md)

These C/C++ files are synthetic compiler diagnostics, not TSL9 feature implementations. They test proposed explanations for frame placement before further work on the real TX port. RV32 output is inspected as static data; it is never executed or emulated.

## Observed results

- `minimal_guard.c` compares a guard with a memory clobber against a register-only guard. Fresh C11 and C++17 builds emit 22-byte functions in both cases: unsigned guard at +4, frame allocation at +8, direct oversized-input RET at +20. A memory clobber alone therefore does not explain the full TX prologue placement. This does not prove that every ordinary C control-flow shape can produce the required ordering.
- `global_owned_s0.c` is accepted, but both languages emit a 16-byte function with SP−16, an S0 save, and an S0 restore before returning. Global register syntax does not establish ownership of the calling frame.
- Four actual branch-bit counterexamples are rejected. Each translation unit's `-MD` output is checked against its source and actual Clang `stdint.h`. The actual compiler/disassembler and immutable profile, ELF parser and source decoder are authenticated by SHA-256.

The immutable original TX decoder does not include the synthetic diagnostic's C.SW. The new runner decodes that instruction's fields locally without altering the old decoder. It does not implement CPU state, instruction execution or an emulator.

## Fresh verification

From the delivered project root, supply the authenticated LLVM directory:

```sh
python3 -B analysis/v4160-tx-register-abi-2026-10-22/entry-plan/verify-diagnostics.py --project-root . --tool-dir /absolute/llvm/bin
```

The research workspace uses `apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/entry-plan/` instead. Alternatively invoke this directory's `sh ./verify.sh --project-root /absolute/project --tool-dir /absolute/llvm/bin`; `PYTHON` selects Python. Each run creates new output and rejects an existing build directory.

`results.json` identifies the historical native Windows LLVM observation. It is not Linux/macOS execution evidence, a resident-ROM contract, or a hardware result. Only running the producer again performs fresh compilation and creates a new `verification.json`. The diagnostic makes no network calls, installs no packages and produces no flashable BIN.
