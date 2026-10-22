# OTA command body: shared C/C++ and measured native gaps

[繁體中文](README.md)

This milestone adds readable shared HOST/native C/C++ for U/S/W/R/E at original `0x9C4A..0x9E5C`. The original body is 530 bytes / 169 instructions. The current complete image still retains original storage here; the new component is not integrated.

## Actual code and validation

- Shared high-level C uses narrow ports: explicit synthetic numeric memory/callees for HOST, volatile memory/live GP/explicit call bridges for native. Original BIN bytes are validation input, never new-code templates or missing-code fallback.
- Actual C11/C++17 HOST suites each pass ten cases / 8,292 checks and three compiled semantic negatives. Independent fixtures each pass sixteen narratives / eighteen dispatches / 898 behavior assertions and four compiled negatives. These are synthetic results, not hardware execution; every HOST executable passes the immutable machine guard first.
- Actual C11/C++17 ET_REL outputs each have one **776-byte FUNC / 285 instructions / 112-byte frame**, versus original 530 bytes / 48-byte frame: an excess of 246 bytes. Full MD covers three project sources and one Clang resource header.
- Nine true UND remain: six direct callees and three callback addresses. The 23 relocations are fifteen JAL and four callback HI/LO pairs, plus one indirect call through slot `0x4004C`. The compiler unrolls the original single quarter-loop callsite into four calls; equal static callsite counts are not a semantic requirement.
- Independent review reads actual object/IR/MD/source/tool identities, all 285 raw operands and three native counterexamples. **No RV32 execution, new linked ELF, new BIN or hardware operation occurs.**

See the [model](../../experiments/tsl9-v4160-ota-handler/readme.en.md), [implementation](implementation/readme.en.md), [original source and consumer review](source-review/readme.en.md), [independent HOST/native review](ABI-review/readme.en.md), [plan](plan.en.md) and [whole-goal scope/gaps](status.en.md).

## Important behavior

W preserves active, length1026, BE16 page/range, required alignment copy, four 256-byte primitives, per-word Flash-before-live-RAM readback and reply order. It writes the numeric BOOT alias `0x08001000 + page*1024`, not a proved Runtime self-flash path.

U clears active before UID comparison and retains `(length-1)&255`. S stores the earlier mode for its reply and uses post-comparison live mode/GP/S1 for active. E retains active/strict15/mode0/UID14 order; R retains strict16/UID14 without adding W's page limit. HALT/TRANSFER/UNKNOWN stop later effects without undoing previous ones.

Source review also repairs W reply projections in the new C: A3 is the last source word, A4 is1024, and A5 is failing offset or successful1024. These are explicit observed projections, not equality of every ambient/intermediate physical register. Original `0x9DF4` is a linking `C.JAL` to `0x9B8E` with `RA=0x9DF6`, not a tail jump.

## Why integration is not admitted

The component exceeds the original530 region by246 bytes. A reviewed location, live-ingress/continuation and complete-image layout solution is absent. The nine UND may later use existing real section-backed providers ([baseline inventory](existing-providers.json)), but no link is performed now; ABS/numeric providers, stubs or fabricated FUNC sizes are forbidden.

HOST named S/SP/GP values are explicit source/effect projections, not a CPU interpreter. Native code remains conditional on conventional callee preservation. Its two-byte C response array is not original live SP+12. Full scratch/S/SP/RA/alias/asynchronous contracts are unproved. A larger function alone does not prove ABI failure, and compilation alone does not admit physical use.

The existing complete TX image remains unchanged at SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. The full goal still requires MCU/ISA, installed ROM/BOOT, RAM/IRQ, Flash, OTA acceptance and recovery evidence. **No rebuilt BIN is verified as flashable.** Offline preflight and wait-reason displays remain proposals, not delivered hardware features.

## Reproduce

```sh
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root /absolute/re-tsl9 --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler/build/new-host
python3 -B analysis/v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler/build/new-native
```

Outputs are create-only; replay uses an actual `verification.json`. Subdirectories document independent reviews and metadata/actual distinctions. Windows is the measured environment; portable Python/shell interfaces alone do not establish Linux/macOS verification.
