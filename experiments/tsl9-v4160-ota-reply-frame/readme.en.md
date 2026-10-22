# OTA reply frame: two bounded C compiler probes

[繁體中文](readme.zh-TW.md)

The shared algorithm, all eight register read/write operands, opaque boundaries and flags remain unchanged. A native identity port constrains the W offset lifetime; its HOST expansion is identity. No unchanged HOST matrix was rerun.

| Actual artifact | bytes / instructions | frame | owned reply bytes |
| --- | --- | --- | --- |
| Sealed compact baseline | 568 / 193 | 48 | SP+6,7 |
| Identity before quarter call | 560 / 190 | 48 | SP+6,7 |
| Identity after quarter call | 556 / 188 | 48 | SP+10,11 |

Both C11 and C++17 were actually compiled without new compiler flags. The final function saves RA and S0..S7. Its independent volatile two-byte IR object does not overlap saved S7 at SP+12..15. However, its address is entry SP-38; the original is entry SP-36. The pointer/frame repair goal therefore remains false. Borrowing saved S7 bytes is forbidden.

No third profile, link, BIN, fake provider, opcode patch, hardware operation or RV32/ISA execution occurred. The live sealed 568-byte model and delivered BIN remain unchanged. Full ABI, placement and OTA admission remain false.

## Reproduce

Python 3 and the existing pinned LLVM are required. The POSIX wrapper accepts PYTHON; Windows runs the same verify.py entry. Outputs are create-only under model/build; omitting build-root creates a UUID directory.

This round was measured with pinned Windows LLVM binaries. Portable Python/sh entries do not establish Linux/macOS compilation or admit different tool hashes.

```sh
sh experiments/tsl9-v4160-ota-reply-frame/verify.sh --project-root "$PWD" --tool-dir /path/to/llvm/bin --language both
```

Each mode contains the object, IR, complete disassembly, actual -MD closure, logs and verification.json. Nine real undefined symbols and twenty relocations remain unresolved. No original BIN is a code-generation input.

The case implementation/probe.py supports `--project-root ROOT --replay MODE/verification.json`. check.py defaults to metadata only. Repeated explicit `--receipt` arguments require actual sources, tools, resource header, recipes, dependencies and artifacts, failing on missing files. The case is analysis/v4160-allocator-callback-2026-10-22 when published, or apk-analysis/tsl9-v4160-allocator-callback-2026-10-22 in the workspace.

The first 560-byte source snapshot and receipts remain local under build/offset-lifetime-v1. Its historical source pins cannot be replayed as current-source identity using the later 556-byte source. Only metadata is published, without opaque objects. Smaller code does not prove original ABI compatibility.
