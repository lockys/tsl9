# V4.1.60 source-integrated image with original storage identity

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Fresh C11 and C++17 builds compile 42 translation units: 34 raw carriers, two IRQ typed TUs and
six Flash typed TUs. Eleven readable functions occupy 526 bytes; 680 other sections remain raw
carriers. This is a partial readable reconstruction, not recovered source for the whole firmware.

Both actual 76800-byte exports match the original pinned ID2966 V4.1.60 SHA-256:

`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`

There are zero original-image differences, resolving the previous de159...68be1 image's 70 differences
and the earlier IRQ-only image's eight. The output remains
`NOT-FLASH-VALIDATED-register-scheduled.bin`. Storage identity does not prove physical flashing or OTA.

```text
42 fresh source TUs
  -> raw-carriers.o + typed-providers.o
  -> compiler-integrated.o
  -> explicit Python ABI frame scheduling
  -> source-integrated.o + frame-scheduling.json
  -> strict missing-ROM rejection
  -> numeric-ROM ADDRESS-WITNESS-ONLY.elf
  -> NOT-FLASH-VALIDATED-register-scheduled.bin
```

A separately validated source policy reorders only existing freshly compiled C.SWSP words in IRQ
and quarter: eight plus six changed file bytes. No opcode is manufactured, no padding is inserted,
no original BIN supplies generated code, and the final BIN is not patched. Whole pre/post ELF section
metadata, symbols and RELA are identical. Both objects and the complete scheduling receipt are retained.
This pipeline is explicitly C/C++ compilation followed by validated ABI save scheduling, not an assertion
that the stock compiler emitted the final save order. The original BIN is a fixed offline validation reference.

The scheduler is pinned to SHA
`dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d`,
with policy SHA
`2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d`.
All ten scheduler-model files are checked before and after use. All eleven final linked bodies match the
original. Five Flash leaves already match exactly in compiler output before scheduling.

```sh
python3 -B experiments/tsl9-v4160-register-image-integration/verify.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B experiments/tsl9-v4160-register-image-integration/verify.py --project-root . --replay /path/to/c/verification.json
python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/check_image.py --project-root . --require-local-builds
```

Python 3.9+ and installed local LLVM tools are required; no downloads occur. Working analysis paths use
apk-analysis/tsl9-v4160-..., published paths use analysis/v4160-.... Shell wrappers accept the same arguments
and honor PYTHON. Only Windows was exercised; no live POSIX/Linux/macOS claim is made.
The CLI accepts a new --build-root and --clang/--linker/--objcopy overrides. The current Python alone runs
the explicit scheduling command, with -B; the runner also disables bytecode caching.
--firmware is forwarded through build/replay dependency contexts and requires the same fixed hash;
an alternate-reference archive must replay with its same explicit path. Explicit replay language must match,
and build/tool overrides are rejected during replay. Actual default C/C++ replay, explicit canonical reference
and wrong-language/override rejection were checked. An alternate-location context forwarding check is
separate and does not claim a second whole-image build with that reference.

Each language has 57 recipes (56 LLVM plus one explicit Python scheduling invocation), 42 per-rule MMD
target/primary/adapter checks, 72 existing non-system native inputs and 12 generated filter/adapter inputs.
All 691 allocation roles and 680 retained partial-storage hashes survive. Actual RELA totals 8270:
8259 full outside roles plus eleven owned JALs. Fifty-three canonical relative bindings and twenty incoming
entry references are retained. Ten exact private branch roles are discharged (four IRQ and six Flash), with
no fabricated numeric provider/alias. FILE/SECTION/mapping metadata are checked separately.
All fifteen LOAD payload, memory and permission extents cover exactly the allocated sections. No holes,
old-BIN fallback, NOBITS/RAM export or ROM bytes supply the export.

Per language, 23 actual ELF/RELA/image mutations, three MMD mutations and four scheduling-receipt
mutations are rejected. All 201 actual artifacts are hashed and replayed. Retained storage hashes refer to
partial objects; relocated linked sections/LOAD/BIN are checked separately, avoiding false partial/final equality.

The strict final link still rejects the sole missing ROM provider. Numeric 0x40000 supplies an address witness
only, not ROM content or execution evidence. Whole-image byte identity is a static storage fact.
Full physical register/asynchronous/interrupt/fault semantics, computed interior-entry assumptions, ROM,
actual chip/board/Flash capacity, power failure, boot and OTA compatibility remain unproved.
No RV32 execution, ISA emulation, device I/O or network operation occurs.

The historical layout retains exact CRLF bytes with SHA
`651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`;
all newly authored reports/source/docs use UTF-8 LF. prepare_manifest.py is a historical ledger bootstrap
requiring an explicit local component; normal verification uses the published pinned ledger without
W-only historical build/exports dependencies. A prebuild source-drift rejection and provisional builds remain
local diagnostic archives.

Publication includes source, pinned ledger, separate-language docs and selected receipt metadata.
Build/log archives stay local. check_image.py lists missing archives; --require-local-builds requires actual
pre/post objects, receipts, ELF, BIN, logs, dependencies and controls. Metadata reading is never presented
as a fresh build, actual-artifact replay or hardware validation.
