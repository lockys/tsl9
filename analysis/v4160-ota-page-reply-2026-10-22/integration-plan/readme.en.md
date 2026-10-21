# Integration boundary for the twelfth function

[繁體中文](README.md)

This evidence addresses the entry roles of the original page reply function
at `0x9B8E..0x9C0A`. Complete-image integration of the twelfth readable
function is still pending. The sealed eleven-function image is unchanged.

The incoming instruction at `0x9DF4` is a `C.JAL` call setting `RA=0x9DF6`.
Relocation kind R_RISCV_RVC_JUMP alone cannot determine link semantics. See the
[supplemental correction](../entry-call-correction/readme.en.md), which
supersedes the old source archive's tail-edge wording.

`inspect-owner.py` reads the previously verified complete partial-link object:
the original 124 bytes, public NOTYPE / size 0 entry, local entry, compressed
incoming reference from `9C4A + 426`, private branch and TX JAL. `owner.json`
archives that actual inspection.

`probe-boundary.py` has compiled and partially linked two actual objects for
each of C and C++: a zero-byte original entry boundary and the newly compiled,
explicitly ordered readable function. An explicit linker script places the
new function in the original section without anchor bytes or padding. The
public entry remains NOTYPE / size 0, the local entry remains LOCAL / size 0,
and the readable C function is a separate actual FUNC / size 124. No numeric
ABS entry alias is introduced.

The actual probe checks the sole original incoming relocation's local role,
the sole owned TX JAL, every retained carrier allocation's attributes and
bytes, and all outside relocation sites/types/addends/target roles and
multiplicities. `probe-c.json` and `probe-cpp.json` archive selected actual
Windows receipts; they do not prove another platform, complete image, ROM,
hardware or OTA behavior.

## Reproduce the partial check

First produce fresh C/C++ objects with the new component's native verifier.
Then select an actual language directory:

```sh
python analysis/v4160-ota-page-reply-2026-10-22/integration-plan/probe-boundary.py \
  --project-root . --tool-dir /path/to/pinned/llvm/bin \
  --native-folder experiments/tsl9-v4160-ota-page-reply/build/NEW/c --mode c
```

The tool first replays the full native source/compiler/artifact receipt,
then compiles a new carrier and performs a new partial link. Outputs go into
a create-only `build/` subdirectory under this evidence scope. No RV32 code
is executed or emulated; the original BIN is not a generation input.

## Remaining gates and feature candidate

Complete-image integration must prove all 691 allocations, retained storage,
symbols, relocation roles, fixed placement, LOAD permissions and exported
image anew. The two-object probe does not substitute for those requirements.
Actual hardware, installed ROM/BOOT, SP/register preservation and BLE OTA
remain unproved.

This function has no local page-index bound: its header uses the low 16 bits
while its source-address formula consumes the full 32-bit index. A candidate
addition is an **offline pre-update page-range and version-applicability
check**, initially in host tooling, to reject unknown images and indices
outside established ranges. This is a proposal, not an implemented firmware
feature. Adding an on-device guard would change size and behavior and needs
separate caller, memory-layout and updater compatibility evidence. No
flash-readiness claim is made.
