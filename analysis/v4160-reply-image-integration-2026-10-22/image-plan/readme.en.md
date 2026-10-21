# Twelve-function complete-image integration plan

[繁體中文](README.md)

This plan derives the twelfth readable function's image boundary from the
actual eleven-function partial object and sealed C/C++ page-reply components.
It is not a completed image or hardware/OTA proof. Prior seals are unchanged.

`prepare-plan.py` replays the previous object's section/symbol/relocation
checks and both new reply source/compiler/fixed-placement artifacts, with
all 124 function bytes equal to the original. It then checks 679 retained
owners, 8,257 outside relocations, 21 incoming references and the existing
53 section-relative bindings. These counts describe actually read existing
evidence; the new complete build must prove its own counts.

The three native reply source/header files join the source ledger. Actual
Clang preprocessing in both languages also discovers one resource header,
`include/stdint.h`, with an exact location and digest. Full dependency output
must measure every new compilation; absence from old `-MMD` output did not
mean system headers were not read.

## Entry roles and generation

The original public GLOBAL NOTYPE / size 0 and LOCAL / size 0 entries remain
zero-byte real boundaries at the original section start. The new readable
function is separately FUNC / size 124. A linker script places the new code
into that owner without numeric ABS entry aliases, anchor bytes or padding.
The incoming `69 3b` at `0x9DF4` is `C.JAL` writing `RA=0x9DF6`; relocation
kind R_RISCV_RVC_JUMP does not determine link semantics.

Generation is intended to compile the standalone reply, explicitly order
two regions of its existing compiler words, partially link all fresh units,
then restore IRQ/quarter save order. The two explicit backends have separate
source and receipts. Clang alone does not emit the final order. The original
BIN is comparison evidence, never a generation, padding or fallback input.

`typed_provider_object_sha256` identifies the actual pre-merge provider word
stream; the reply has already been ordered at that point.
`raw_compiler_native_object_sha256` identifies its earlier compiler-only
stream. These are deliberately separate.

## Check

```sh
python analysis/v4160-reply-image-integration-2026-10-22/image-plan/check-plan.py \
  --project-root .
```

Default checks read metadata and current source/header identities, not
historical objects or BINs, and do not rerun plan preparation.
`verification.json` records actual plan checks and three bounded Clang
dependency queries. Archived metadata cannot replace new complete-image
artifact verification.

The complete build must prove every allocation, retained byte, symbol,
relocation, fixed placement, LOAD file/memory extent and permission, and
exported image. Unknown ROM, hardware, startup and updater conditions remain
independent requirements. No flash-readiness claim is made.
