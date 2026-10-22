# Event callback reconstruction in C/C++

[繁體中文](README.md)

This milestone studies official ID2966 V4.1.60 `0x8614..0x888C`: 632 bytes / 217 original instructions, 26 direct control references, 64 memory operations and fifteen opaque indirect calls. Original-source validation, readable C/C++, synthetic host behavior and actual native allocation remain separate evidence. **This callback is not integrated into a complete image; no new BIN or flashing-readiness claim is added.**

## Reconstructed logic

LOW16 event bit15 has priority, followed by mask `0x8`. Other paths first match two context bytes, then dispatch masks `0x1/0x2/0x4`. Context and event inputs retain all 32 bits rather than adopting candidate SDK narrow types. Two records use a 1062-byte buffer stride; descriptor/consumed-length halfwords, retry bytes and fresh reads retain original widths.

The mask1 and mask2 paths test the same candidate ROM gate differently: exact result1 versus only its low bit. Chunk length uses a signed remaining amount after 16-bit truncation and another opaque result. Failure handling and successful length/event updates remain distinct. Unknown ROM calls keep numeric slots, actual assigned arguments and result boundaries without claiming installed SDK identity.

The [initializer source](entry-plan/readme.en.md) independently checks three materializations of callback argument `0x8614` and stores of returned bytes at GP_after+`0x9D/0x94/0x98`. S0/S1/GP preservation across opaque calls remains unproved; nominal absolute slots and default connection halfwords are conditional.

## Evidence and remaining gaps

- [Source review](source-review/readme.en.md) reads original BIN operands and roles; raw operand negatives do not rely on rejecting file digests.
- [Implementation](implementation/readme.en.md) preserves actual C11/C++17 HOST and native compiler evidence. Named HOST values, argument projections and synthetic frames test the algorithm, not ISA execution or physical original GPR prefixes.
- [Independent review](ABI-review/readme.en.md) supplies separate synthetic cases and reads actual native ELF/IR. Unassigned scratch residues, physical SP/GP/register preservation, return addresses and asynchronous behavior need their own evidence.

The native probe has no original-placement admission. Successful strict linking or HOST tests do not authorize replacement of the original 632-byte region. Installed ROM/BOOT, chip, physical Flash aliasing, CRC/signature policy, BLE OTA and recovery remain unproved. Original firmware is data; no RV32 execution/emulation, hardware operation or vendor API call occurs.

The corrected baseline needs a 944-byte main plus a 90-byte call primitive. Explicitly inlining only that primitive reduces it to one 658-byte function with a 48-byte frame and fifteen indirect calls. It still exceeds the original extent by 26 bytes and adds S10 saves, different save order/return addresses and unresolved opaque-callee register observations. This is an actual native improvement without full-ABI or integration admission.

The complete experimental image remains the [previous TX integration](../v4160-tx-image-integration-2026-10-22/readme.en.md), retaining the original callback carrier. Further work should reduce the native gap and resolve actual call/entry/return contracts before another full-image integration. The initializer analysis adds source locations for update wait-reason research; no new hardware feature is implemented.
