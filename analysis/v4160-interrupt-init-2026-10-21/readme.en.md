# Interrupt initialization evidence

The [readable C/C++ component](../../experiments/tsl9-v4160-interrupt-init/readme.en.md) reconstructs the ordinary-call MMIO/CSR effects of original `0x9A42` and four helpers. Source proof is in `source/`; full original register/stack constraints are in `abi-review/`; independent C tests are in `code-review/`; native compiler/ELF checks are in `native-plan/`.

The current native entry is `native-plan/verify_native_v2.py --project-root <checkout> --language both`, with LLVM executables on PATH or supplied through `--tool-dir`, `--clang`, `--linker` and `--objdump`. V2 checks every disassembled byte against the full ELF function and rejects missing, changed or unparsed instruction rows. V1 is retained unchanged as historical evidence. Full local build receipts and binaries are excluded from the published snapshot; use the fresh verification command to reproduce component checks.

These evidence types answer separate questions. An ordinary C return value and an unresolved-free standalone native component do not prove original register residue, fixed placement, complete startup, installed ROM, interrupt dispatch or BLE OTA compatibility. Original firmware is read only as data. No RV32 code is executed or emulated and no physical I/O is performed.
