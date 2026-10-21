# Complete offline image with twelve readable functions

[繁體中文](README.md)

This pass integrates the C/C++ page reply at `0x9B8E..0x9C0A` into the complete
image. Readable sources cover twelve functions / 650 bytes; 679 remaining
carrier sections retain their original contents. The 76,800-byte output
matches official ID2966 V4.1.60 SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
This remains partial source recovery.

## Evidence and reproduction

| Scope | Entry | Limit |
| --- | --- | --- |
| Actual old object, sources and new boundary | [Plan](image-plan/readme.en.md) | Default checks metadata/source; the plan is not a completed build |
| Fresh compilation, two backends, complete link/export | [Implementation](implementation/readme.en.md) | ROM numeric-address witness, no implementation |
| Independent source/dependency/recipe checks | [Source review](source-review/readme.en.md) | Record controls and actual artifact checks are separate |
| Sections, symbols, relocations, LOADs and BIN | [ABI review](ABI-review/readme.en.md) | Actual ELF/BIN evidence is not physical hardware proof |

Generation compiles 34 original carriers and nine readable units and emits
nine LLVM IR files. Its 61 commands comprise 59 LLVM operations and two
explicit Python ABI stages: order the standalone reply's existing compiler
words, partially link, then restore IRQ/quarter save order. There are no new
opcodes, padding, original-BIN fallback or compiler-only final-order claim.

All 43 compilations use full `-MD` dependencies: 74 project inputs, fourteen
generated inputs and one actual Clang resource header. Old `-MMD` output's
omission of system headers did not prove they were not used.

The image retains 691 allocations, 8,257 outside plus twelve source JAL
relocations (8,269 total), 53 relative bindings and 21 incoming roles. The
reply's public NOTYPE / size 0 and local entry remain, while the new readable
function is separately FUNC / size 124. `0x9DF4` remains a linking `C.JAL`.
Private branches are discharged against exact operands and destinations.

The `.llvm_addrsig` increment has explicit old-prefix, compiler-payload and
symbol-origin checks; its excluded metadata status does not waive arbitrary
changes. All fifteen LOADs' complete file/memory extents, permissions and
exported byte coverage must pass.

## Remaining full-goal requirements

Strict linking still rejects the unknown ROM implementation; numeric
`0x40000` is an address witness only. Board/chip identity, installed ROM/BOOT,
memory and interrupts, physical BLE OTA acceptance and recovery remain
unproved. The exact official file previously updated successfully by the
user has not been matched to this image.

**Not verified as flashable; the full goal remains active.** No RV32 code is
executed or emulated; no BLE/CAN/UART/Flash hardware is operated. Offline
page-range and version-applicability preflight remains a proposal, not an
implemented device feature.

Next priorities are the complete OTA handler, TX wrapper and their external
services, keeping versions and Runtime/BOOT directions separate. Actual
Windows compilation, shell/Linux/macOS/CI and physical hardware evidence are
reported separately.
