# Native component proof, revision 2

Revision 2 preserves the sealed v1 files as historical evidence and strengthens machine-code coverage. Use `verify_native_v2.py` for fresh native compilation and `check_native_v2.py` for a read-only archive replay. The original v1 guides describe the component, source effects, ABI/layout limitations, and toolchain; their v1 command is superseded by the revision 2 command below.

The C11 and C++17 builds still emit the same 118-byte, 43-instruction initializer and four 22-byte helpers. Each mode passes the 20-effect IR proof and 20-effect machine proof, with no unresolved symbols or writable data. Revision 2 now binds every disassembly row directly to the actual linked ELF symbol: exact entry address, contiguous instruction addresses, exact raw instruction bytes, complete instruction framing, and complete 118-byte extent. It rejects unknown interior/trailing instruction lines and interior labels. No instruction or byte can be silently skipped by a parser.

Each fresh mode actually compiles and rejects the four source mutations from v1. Six additional transcript controls per mode reject a missing first row, missing interior row, truncated final row, modified raw instruction byte, unparsed interior line, and unparsed trailing line. These transcript controls are static proof-parser tests, not target execution tests.

From a published checkout, run:

```sh
python3 analysis/v4160-interrupt-init-2026-10-21/native-plan/verify_native_v2.py \
  --project-root . \
  --clang /path/to/clang \
  --linker /path/to/ld.lld \
  --objdump /path/to/llvm-objdump \
  --language both
```

`--tool-dir /path/to/llvm/bin` is an alternative to the three executable options. The investigation workspace uses `apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/` instead of the published `analysis/v4160-interrupt-init-2026-10-21/` prefix. Python 3.10+, the new model C/header, the shipped verifier Python files, and local LLVM tools are sufficient. The fresh compile does not require old ignored 691-section build archives. Each run creates a new local `build/native-.../` directory and a real receipt. The verified compiler profile remains Clang 18.0.2 from Android NDK 27.1.12297006.

For the retained original verification archives:

```sh
python3 analysis/v4160-interrupt-init-2026-10-21/native-plan/check_native_v2.py \
  --project-root . --require-local-builds
```

Without `--require-local-builds`, the read-only checker verifies sealed metadata and current C/header identity while explicitly listing absent local archive receipts. Such a metadata check is not a new compilation. Generated ELF/object/IR/log archives are retained locally and excluded from source publication.

This is a standalone native component. The 118-versus-144-byte comparison is size evidence only. No replacement was placed at original `0x9A42`; the original stack/call boundaries and caller-saved register residues differ. Original C/IRQ ABI, installed ROM, physical peripheral behavior, complete original-image integration, and Bluetooth OTA remain unproved. The old 691-allocation / 8,280-RELA image gate remains immutable and still has its real unresolved resident entry. No firmware BIN is generated, no original or rebuilt RV32 code is executed or emulated, and no device I/O occurs.
