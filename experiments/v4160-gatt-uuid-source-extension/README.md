# GATT UUID curated source extension

The two-byte value read through the initialized `GP+36` pointer is now available
as `src/native/receive/gatt_write_uuid.c`. This is a byte-for-byte curation of
the prior `write_UUID.c` experiment, with a separate, pinned extension manifest.
The main source manifest and frozen parent proofs are unchanged; this extension
has its own build and verification entry point.

Both C11 and C++17 builds emit precisely one readonly, aligned, two-byte OBJECT
containing `F1 FF`. Real partial links retain every parent allocated section,
global/weak defined symbol, unresolved provider and relocation. Local symbol
metadata is not compared by this check. Original-coordinate diagnostic links retain
all 73,538 parent bytes and add exactly two bytes at `[0x1AB44,0x1AB46)`;
the extended diagnostic has **73,540 bytes**. The C/C++ diagnostic ELF files
are identical. A strict link without numerical reference witnesses still fails
with exactly the six inherited providers. No provider is stubbed or aliased.

This is an additive source extension, not a replay or replacement of the
unified 164-source proof. The previous formal aggregate remains 73,538/76,800
bytes (95.75%); the extension's 73,540-byte diagnostic is a separate result.
The parent object was verified by hash and preservation checks, not recompiled.

## Offline reproduction

From the repository root, using Python 3.10+ and the pinned LLVM 18.0.2 tools:

```sh
python -B experiments/v4160-gatt-uuid-source-extension/verify.py --tool-dir /path/to/llvm/bin --output-dir /existing/parent/new-build
python -B experiments/v4160-gatt-uuid-source-extension/test_unit.py --tool-dir /path/to/llvm/bin
```

Repeat with `python -O -B` for optimized-mode checking. The build output must
not already exist. `receipt.json` is written there; `verification.json` here
retains this round's actual normal/optimized receipts and mutation results.
All checks use explicit exceptions and remain active under `-O`.

The build requires the frozen parent component, layout ELF/script, numerical
reference object, and split payload at the paths and hashes in `verify.py`.
Those local artifacts are not bundled. Their absence is a failure, not a skip.
The original decoded BIN is required and checked by its full SHA-256; the
two-byte UUID is then compared with its original coordinates. The local ELF32
reader is preserved from the existing v7 reader, whose hash is pinned.
The unit mutation tests need only the curated source, reader and compiler:
both languages accept the original and reject altered value, width, owner,
section and alignment. All compiler outputs are temporary; no target is run.

## Consumer evidence and limits

Existing local analysis establishes the conditional provenance:
reset copies the word at `0x1AB84` into `GP+36`, yielding pointer `0x1AB44`.
At `0x88CE/0x88D0`, the callback loads that pointer and reads its halfword;
`0x88D4` compares it with an incoming field. This is not a direct transmission.
The source extension does not replay that consumer proof or establish pointer
stability. Aliases, resident registration, interrupts and other indirect writers
remain relevant. It does not reconstruct a complete GATT table or bind a
provider to this two-byte object.

The diagnostic ELF has entry zero and no `PT_LOAD`; it is not loadable firmware.
Installed ROM identity, ABI, RAM ownership, startup, IRQ, BLE operation, OTA and
hardware behavior remain unproved. No BIN is generated and no hardware or
network is used during analysis. GitHub publication is separate from analysis.
