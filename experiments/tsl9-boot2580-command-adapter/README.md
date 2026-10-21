# Selected BOOT ID2580 numeric/live command adapter

Readable C11/C++17 implementation of selected command-body effects from the
12,288-byte BOOT image SHA256
`650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`.
The server catalog called it ID2580/V1.0.00. Its installation on the user's
physical TSL9 remains unknown. The source body is414 bytes/144 instructions at
21BE..235C, independently retained in the adjacent `source` evidence scope.

This is a host command/data contract. It does not execute RV32 instructions,
dereference target numeric addresses on the host, connect BLE or write hardware.
`body_sp` describes the snapshot AFTER the original48-byte prologue. The adapter
represents the selected body's scratch words at body_sp+8/+12, not full register
save/restore, return addresses, original C ABI, stack validity or physical IRQs.
The caller must supply that post-prologue state, including any earlier aliases.
The modeled original entry relation is a0=connection,a1=command,a2=payload,a3=n.

## Source effects preserved

- W reads active at GP+139, rejects n!=1026, reads page low byte2210 before
  high byte2214, and uses the bounded source guard for unsigned page0..95.
  Destination is08008000+page*1024. A partial page proven out of range is rejected;
  an ambiguous guard stops. A partial page known to pass can proceed to explicit
  provider requests carrying its numeric address and bit-known mask.
- Unaligned payload+2 is moved down1..3 bytes. The source first loads the
  pointer from nominal4004C at2256, then calls that loaded pointer at225E,
  with JALR bit0 cleared. It does not directly call a function at4004C. Both
  raw and normalized pointer/mask survive in the request. The nominal copy role
  does not establish a memcpy/memmove ABI or actual original ROM implementation.
  A provider's overlap-copy semantics must be explicit.
- Four20E6 calls receive live numeric sources256 bytes apart. Return values
  are ignored; nonreturn is preserved. Then256 comparisons load Flash first
  at2282 and live source RAM second at2288. First mismatch returns silently;
  no Runtime FF reply or full-page echo is added. Equality with unknown bits
  stops at the source branch, rather than fabricating a readback success.
- S saves n then pointer to the two numeric scratch words before calling1C82.
  Both are loaded again BEFORE checking the raw UID return. Mode is read live
  only after a zero UID return, and must equal1. Active is set before canceling
  startup250E and metadata selector2184(2). A normally returned metadata scalar
  is ignored even if unknown; HALT/TRANSFER stops before later effects. Both
  scratch words are loaded again after that call, then the live pointer/n go
  to the2AA0 response wrapper. No strict n15 guard is invented: the delegated
  UID helper receives uint8(n-1), so n271 also supplies14.
- U clears active before UID checking, does not inspect mode and requests the
 2ABA wrapper with scalar byte0 on raw UID match. It does not activate W.
- E checks active, clears it, requests192C/200 and20E2/400 through1AFA, then
  requests an empty2AA0 E reply. It does not check n/payload/UID or whole-image
  completion. Schedules are requests only; no callbacks run automatically.
- Other commands, including R, return from this selected body. That does not
  establish the absence of behavior in the outer GATT dispatcher or root loader.

Normal retained BOOT parser storage200090AA gives aligned source200090AC;
the unaligned branch is a supported command-call boundary, not a claim that
every normal BLE update uses overlap copy.

## Providers, existing code and observation limits

Every memory access and delegated helper is a typed request with PC, target,
arguments and known masks. No provider means an explicit boundary. RETURNED
assumes that named helper completed under its independently justified contract,
preserving local callee-saved values and engine control; it is not proof of the
original ABI. Providers may alter synthetic memory and live GP/body_sp. Subsequent
loads use that live state. Partial addresses/indirect targets require an explicit
provider that can justify its effects. Unknown control comparisons halt.

HALT and TRANSFER retain effects already made. The next dispatch cannot silently
resume such an activation. `bc_new_activation` explicitly selects a separate
host invocation, preserving provider memory and configured GP/SP; it does not
execute an original return. Initializers/dispatch require a valid model pointer.

The observation budget is a host bound on admitted primitive requests, not an
original firmware retry limit. The last request remains visible when it stops;
earlier memory and delegated effects remain. Program/reply counters record call
attempts, including one whose provider does not return. A reply observes a whole
wrapper-call boundary, not physical BLE transmission or peripheral success.

`boot_fp_bridge.c` is a thin reusable composition seam: known selected-BOOT20E6
requests delegate to the existing `flash_page.c` FP_BOOT engine through FP_ADDRESS.
It does not snapshot256 source bytes or implement a second Flash engine. The
engine retains its CSR800 clear136, unlock/status49/erase/program256/lock/set136
contract and its own explicit MMIO/CSR providers. Both models must share the same
synthetic SRAM. The seam's known-target/image/argument checks are host preconditions,
not additional original BOOT guards. FP_HALT/FP_TRANSFER are not turned into success.

The existing TC_BOOT high-level logic, metadata5-attempt logic, startup scheduler
and response wrapper hooks remain available. The new adapter does not replace
them wholesale or assume a source snapshot was always wrong: aligned original
TC_BOOT already used shared RAM and Flash-first comparison. New source/reuse
evidence records the narrower missing numeric/callee-visible effects.

## Validation and full objective

`verify.ps1` and `-Cpp` perform portable original-BOOT source checking, bind all
compile inputs and run synthetic host behavior tests. Independent review and a
separate composition harness exercise the actual existing FP_BOOT engine. A
successful synthetic program/readback establishes only those host contracts.
No original BIN/ROM or rebuilt RV32 instructions run in these tests.

The previous source-identical76,800-byte ID2966 offline BIN is unchanged and
still NOT-FLASH-VALIDATED. Selected BOOT fitting75 numeric pages cannot prove
installed BOOT, root policy, physical Flash alias/partition, actual MCU/resident,
identity reads, metadata persistence, interruption/power-loss recovery, RAM/IRQ
contracts, original application behavior or physical OTA acceptance. Those
requirements remain open; this adapter is not a flashable firmware replacement.
