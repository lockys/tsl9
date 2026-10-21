# Clock register reconstruction review

This review is separate from the immutable sibling `caller-review`. The source basis is original ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, with the sealed 214-byte / 69-instruction clock proof. Caller review showed why query's path-dependent A3 cannot simply be preserved from entry: that source output reaches an unresolved indirect callback at `0x131E0` through the known normal initialization prefix.

The product under review is the new readable component `experiments/tsl9-v4160-clock-registers/src/`, not the prior memory-only component and not an ISA interpreter. Hosted register commitments are observations of new C hooks; they do not by themselves prove physical native-register assignments. Native write-set, stack, extent, and compiler-reservation checks require separate actual compiled evidence. No hosted test establishes the installed interrupt ABI or physical hardware/OTA behavior.

## Independent test design

The independent harness reuses the immutable **independent** memory-effect fixture in `apk-analysis/tsl9-v4160-native-clock-2026-10-21/code-review/test_independent.c`; it does not include the parent's test implementation. That fixture checks all selectors and multiplier fields, fresh config/global reads, four/three live GP sites with wrapping numeric addresses, every table index and shift byte, and unsigned quotient boundaries.

Additional expectations independently derive the original A3 for each branch, require a conditional A2=`0x00C00000` commitment immediately after the fourth fresh config sample on the external source branch, and require no A2 write on the other paths. Query's final A4 must be the full unsigned byte; A5 must be the full shifted fresh word. Derivation's A4 must be 1000, and A5 must hold the full product of the masked quotient and 1000, despite the memory store truncating to 16 bits. Each output commitment must occur after its final original memory effect, with no commitment to the other function's output domain.

The parent test source was inspected while implementation was still pending freeze. It extends its prior memory fixture with path-specific A3, conditional A2 timing/value, query A4/A5, and full derived A5 checks. That inspection is test coverage evidence; it is not a compiled test result or a native ABI proof.

## Frozen-source hosted verification

After the parent froze all four C/header files, independent C11 and C++17 each passed **4 groups, 5,345 cases, 250,316 checks**. The baseline independent memory fixture contributes 214,811 checks; the additional checks observe the source-derived normal-return register commitments and conditional A2 hook. No blocking source mismatch was found in the frozen component. The external mask is produced only on the external branch; the field multiplier is held as 1000 for both the product and the final A4 commitment.

Each language also compiled and ran eight incorrect product variants: wrong default A3; internal A3 of 18 instead of 17; wrong external mask-equal A3; fallback A3 shifted by 13 after preserving the correct frequency choice; unconditional A2 write; masked A4 output instead of the full byte; swapped field A4/A5; and field A5 truncated to 16 bits. All **16 actual compiled variants** failed the independent runtime assertions. Most mutations preserve the correct memory effects, so a memory-only test cannot justify the register contract. A compile failure is not counted as a behavioral rejection.

`audit.py --language both` reproduces the hosted review. Receipts bind the four actual source/header files, independent wrapper and immutable fixture, required headers, shared compiler helper, old source/caller evidence, compiler, actual executable and compile logs. Every input hash was unchanged during its run. This proof concerns hosted hook values and ordering; actual native commitments, register write sets, placement, stack/interrupt behavior and physical hardware compatibility remain separate checks.

Final parent C/C++ receipts each pass 6 groups / 293,845 checks. They replay the old 214-byte / 69-instruction / 50-negative source proof and bind the newly decoded original destination facts: query writes only x12–x15 (44 destination instructions); fields write only x14–x15 (8 destination instructions). The return formulas remain a static source review, not an ISA execution proof. `check-review.py` verifies these final parent receipts and both independent receipts against current input, actual compiler and actual executable digests. It also binds the final parent runner, source map and language-separated documentation through those receipts, without executing any program.

