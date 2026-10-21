# Resident copy reference: source implementation and physical gates

The previous goal turn made concrete progress: the source-bound BOOT UID helper,
its frame-data effects, independent review, actual command composition and fresh
destination host builds were delivered and read back. This turn closes another
source implementation seam without treating host success as physical validation.

`experiments/tsl9-resident-copy-reference/src/reference_copy.c` reconstructs the
selected Dec2023 candidate's 58-byte, 18-instruction copy body. Slot `0x4004C`
contains RAM target `0x20000332`, not a carrier ROM-text target. Under the declared
normal first-initializer-copy prefix, the entire body maps from carrier
`[0x405A2,0x405DC)`. The portable source checker verifies the exact original
carrier, slot, seed/loader operands and helper and rejects 23 raw mutants.

The reconstructed body preserves READ32/save at `0x4002420C`, WRITE32 zero and
`FENCE.I` before null/length guards. It reads each source byte freshly, computes
destination with the old index, increments before store, and restores the saved
MMIO word only on an ordinary path. Destination-above-source overlap propagates
modified bytes. Partial-known data, u32 arithmetic/length and HALT/TRANSFER/budget
prefixes are explicit. No `memmove`, identity stub, cleanup handler or second
fence replaces source behavior. The hardware register's purpose remains unknown.

Thin bindings connect the reference leaf to the unchanged UID helper's real
8-byte and 6-byte requests and to the selected BOOT225E 1024-byte staging-copy
request. Source-specific register data is preserved; writes can still alias the
shared frame memory which the caller later reloads. A default unknown profile
does not perform effects. Choosing the Dec2023 reference is an explicit host
assumption, never detection of the module's installed ROM.

Two formal MSVC `/W4 /WX` C11/C++17 parent builds each pass five groups/772 checks.
Each receipt binds seven model files, twelve original/dependency inputs, actual
host executable and compiler bytes. Source and version audits are separate sealed
scopes. The version audit finds the same 58 bytes in a retained older reference;
its different entry/initialization prevents substituting whole resident profiles.
Independent model review and actual BC/UID/copy/Flash composition provide separate
receipts. All tests use synthetic memory and identifiers; no original ISA, native
BIN, module, BLE, CAN or vendor service is executed or contacted.

Independent review passes nine groups/583 checks per language, including a real
UB-to-RP shared-frame saved-RA alias. Actual composition passes 23 groups/34,613
assertions per language and rejects four successfully compiled countercases.
It links the unchanged BC/UID/Flash engines with the new RP body. UID's two copy
calls issue 38 RP effects; an unaligned W request issues 2,053 RP effects, then four
actual FP_BOOT calls/256 live words/616 FP requests and Flash-before-source
comparisons before the empty reply. Synthetic memory changes between RP bytes and
between FP words remain visible. Aligned W source skips staging copy as the source
does. Negative cases omit MMIO or replace UID copy with a scalar stub and fail
their independent assertions in both languages.

Parent replay of `review/audit.py --check` and
`composition/check-composition.py --check` passes against all pinned sources,
actual host executables and seals. The independent source, version, model-review
and composition scopes remain separately sealed. Create-only destination delivery
adds these scopes and the new model, requires fresh C/C++ builds using destination
inputs, and verifies every protected old file. Its receipt is generated only after
that delivery actually completes; an archival workspace receipt alone does not
establish destination success.

## Full original objective audit

| Requirement | Authoritative evidence and remaining gap | State |
| --- | --- | --- |
| C/C++ necessary application functions | Existing feature/transport/UID/BOOT contracts and new selected resident copy; opaque/unreconstructed behavior remains | Partial |
| Original runtime/startup implementation | Existing source layout and initializer/IRQ frame contracts; actual resident entry/provider unresolved | Partial |
| Reference copy source implementation | Exact carrier/body/mapping proof, own C/C++ tests and explicit provider effects | Reconstructed under reference assumptions |
| Installed resident/copy ABI | Reference target and body known; no original module resident dump/identity or physical call evidence | Unproven |
| Exact original hardware composition | Candidate WCH family evidence; exact chip/PCB/Flash/RAM peripherals not identified | Unproven |
| Original BOOT and startup compatibility | Candidate BOOT2580 and Dec2023 initialization, missing four-byte second-copy source load retained | Unproven |
| Memory/stack/ROM/interrupt compatibility | Source-bound data effects and conditional profiles; actual memory/IRQ/hardware ABI missing | Unproven |
| Flash persistence and original update protocol | BC/UID/copy/Flash synthetic composition and APK source contracts; physical storage/transport/acceptance absent | Partial |
| Complete new BIN with necessary functionality | Prior source-identical offline candidate preserves source bytes; strict native link still has unresolved resident entry | Not achieved |
| BIN accepted over original BLE OTA and runs on original module | No physical acceptance, boot, behavior or recovery evidence | Not achieved |

The 76,800-byte source-identical ID2966 offline image remains
`NOT-FLASH-VALIDATED`, SHA256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
No new native BIN is emitted here. The missing second-initializer four-byte read
is not repaired by inventing bytes, using another version or observing that a
later zero-fill would overwrite its destination. Prefix mapping of this helper
does not prove whole initialization completed. Hardware, installed ROM, native
ABI and end-to-end OTA gates remain required by the unchanged goal.
