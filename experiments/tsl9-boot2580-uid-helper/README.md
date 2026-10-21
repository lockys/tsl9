# BOOT2580 UID builder, matcher and command bridge

Readable C11/C++17 reconstruction of original1C4A..1CC4:122 source bytes,
48 instructions, two fixed helper bodies. This is source-specific data, frame
and callback logic. It is not an ISA interpreter, original BIN execution, ROM
execution, device access or proof of the original C ABI. Numeric PCs/addresses
remain data and never become host memory/function pointers.

The selected BOOT is12,288 bytes, SHA256
`650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`.
Installed BOOT identity and physical mappings remain unknown. A portable
source checker binds every original byte/PC and rejects24 raw operand mutations.

## Builder and local matcher

`ub_build` represents all selected builder frame effects. SP decreases16; old
S1 is saved BEFORE the first loaded-pointer read at1C52. Then S0/S2/RA saves
and the first8-byte copy request occur. After a normal provider return, the
second source is formed from live S0 BEFORE restoring S0. The second slot uses
live S1 BEFORE restoring S1; its pointer is loaded fresh. The second destination
is live S2+8 BEFORE restoring S2. RA is loaded from the current frame, SP adds16,
and the second6-byte operation is a tail call through the loaded pointer.

Slot addresses, raw/normalized JALR targets and continuations are explicit.
Normal copy return is an external whole-primitive contract, not inferred from
issuing a call. A tail provider's RETURNED says control returned through its
declared continuation, conditionally on that provider. Standalone build exposes
that target; callers must not assume it equals their expected continuation.

`ub_compare` first checks the full source length register for14. A definite
mismatch sets raw result1 and requests RET without creating a frame or copying.
Length14 creates a32-byte frame, saves old S0/RA, and calls the builder into its
frame base. Only a builder tail return normalized to1C94 permits comparison.
For each of14 bytes, incoming memory is read at1C9C before the expected frame
byte at1CA4. First definite mismatch returns1;14 equal bytes return0. Unknown
branch data stops, rather than selecting a match or using a generic memcmp
provider. RA/S0 are restored from fresh frame words and SP adds32 before RET.

The library retains partial-known words. Memory providers preserve modeled
register/control data while completing their explicit effect. Copy callbacks
may change modeled SP/S0/S1/S2/RA and synthetic memory. Later source operations
use those live fields. Caller register knowledge is supplied; unknown saved
words are not invented as initialized zero. Aligned/unaligned word access,
readability and traps are provider conditions, not inferred physical properties.

## Conditional14-byte geometry

For a stable source with ordinary byte-copy semantics, the two ranges are
1FFFF7EC..1FFFF7F3 (8 bytes), then1FFFF7E8..1FFFF7ED (6 bytes). They cover12
distinct addresses; output bytes12/13 repeat bytes0/1. This relationship requires
correct slot ABI, stable sources, valid destination and suitable return/register
behavior. It is not an actual device UID, signature, hardware-identification
proof or license to manufacture a packet from a screenshot. No real identifier
is used, printed, requested or transmitted by the model or its tests.

## Actual command integration seam

`ub_identity_bridge` handles only the source-bound BC_IDENTITY calls at22AC/22DA
to1C82. It takes the command's live bodySP as helper entrySP and sets the source
call continuation22AE/22DC. Caller saved-register knowledge and primitive backends
are explicit. It propagates SP prefix effects even when a helper stops. A raw
result is returned to the command adapter only after a reported normal helper
return with a matching normalized target. A definite other route is TRANSFER;
an unknown route halts. There is no automatic retry/resume after nonreturn.

This closes the prior scalar-only identity seam for the reconstructed source
algorithm, conditionally on memory/copy/return providers. It does not close the
actual resident4004C implementation, hardware UID reads, physical stack/IRQ or
complete original ABI. Copy return values are not used as identity comparisons.
S's mode/active/metadata handling and U's active clearing stay in the unchanged
command adapter. The separate integration harness must exercise that actual
adapter, not replace identity with a preselected zero result.

All observations have an explicit host budget. HALT/TRANSFER/budget stops retain
prior data effects, including SP arithmetic before a blocked provider call.
Counters are host diagnostics; they are not original firmware retry limits.
`ub_new_activation` selects a separate host invocation without resetting register
or memory state. It does not resume an original instruction stream.

## Validation and remaining objective

`verify.ps1` and `-Cpp` bind the original source, current model and unchanged
command dependencies before compiling with MSVC /W4 /WX. Synthetic tests cover
frame order, both copy requests, prefix/suffix geometry, input-first comparisons,
length rejection, partial-known branches, changed slots/return routes, budget,
HALT/TRANSFER and the command bridge. Independent review and actual command
composition receipts provide separate evidence. All execute own host C/C++ only.

No physical BLE/Flash/ROM operation or real UID packet occurs. The previous
source-identical ID2966 offline BIN remains unchanged and NOT-FLASH-VALIDATED.
Original MCU/resident, installed BOOT/root, memory/IRQ, metadata persistence,
application behavior and end-to-end OTA acceptance are still unproven.
