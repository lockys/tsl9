# Clock routines: original register outputs and native-checker limits

This source review reuses the sealed ID 2966 V4.1.60 proof (`ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51`). It covers query `0x18834..0x188E2` and fields `0x1973C..0x19764`: 214 bytes / 69 instructions. The original image SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

The following normal-return residues assume the exact original code, completed memory effects and no unaccounted external GPR mutation or trap effect. Each external memory sample remains independent. They are static dataflow conclusions, not observed execution or a complete physical interrupt model.

## Exact integer write sets

| Original routine | Possible architectural integer destinations | Instructions naming destinations | Untouched integer registers |
|---|---|---:|---|
| Query 0x18834 | x12/A2, x13/A3, x14/A4, x15/A5 | 44 | x1..x11 and x16..x31 |
| Fields 0x1973C | x14/A4, x15/A5 | 8 | x1..x13 and x16..x31 |

These counts are static instruction counts across complete ranges, including mutually exclusive paths. They are not executed-instruction counts. A destination may receive a value equal to its prior value; a write set does not assert that bits change. x0 remains architectural zero. Both routines are leaves, contain no SP adjustment and never explicitly assign A0, A1, GP or RA. Their `RET` is raw `8280` (`jalr x0,ra,0`), which transfers to the live RA with bit zero cleared; it does not write RA.

The raw destination-field inspector checks every retained instruction rather than interpreting mnemonic text. It recognizes only instruction classes present in the immutable source. It does not execute instructions or evaluate a general instruction set. The independent source proof remains responsible for exact bytes, operands and the 50 raw negative controls.

## Query final residues

The query's first RCC sample chooses `(sample & 12)`. Its last table byte is the unsigned READ8 at 0x18864. Its last scalar word is the fresh READ32 at 0x1886C.

| Path | Final A2 | Final A3 |
|---|---|---|
| Selector 4, literal 32000000 | incoming A2 | 4, assigned at 0x1883A |
| Selector 0 or 12, literal 8000000 | incoming A2 | 8, assigned at 0x18842 |
| Selector 8, separately sampled source bit 16 clear | incoming A2 | 17, assigned at 0x18890 |
| Selector 8, source bit 16 set, next sample bits 22 and 23 both set | 0x00C00000, assigned at 0x188B6 | 0x40021000, assigned at 0x188B0 |
| Selector 8, source bit 16 set, next sample bits 22 and 23 not both set | 0x00C00000 | low32(following fresh RCC sample << 14), assigned at 0x188D0 |

The multiplier replacement 17→18 at 0x18896 changes A5, **not A3**. Internal-source paths retain A3=17 regardless of that replacement. The final external fallback A3 preserves the entire shifted word, not merely its sign or bit-17 decision. The zero/one/other choices above refer to the exact independent source samples, not one cached RCC word.

On every normal-return path, final A4 is the zero-extended live table byte read at 0x18864. Final A5 is the fresh scalar word read at 0x1886C logically shifted right by `(A4 & 31)`. The last WRITE32 does not modify either register. A0 and A1 retain their incoming values; A2 is preserved only on the nonexternal paths above. GP, SP and RA remain unchanged by the body, subject to the stated external-effect assumptions.

## Fields final residues

Let `q8 = (uint32(fresh READ32 at GP+108) / 8000000) & 255`. Final A4 is 1000, assigned at 0x19756. Final A5 is the complete 32-bit product `q8 * 1000`, produced at 0x1975A, in range 0..255000. WRITE16 at 0x1975E stores only the low sixteen bits but does **not** truncate A5 itself. The WRITE8 at 0x19752 does not reload or otherwise replace the held quotient.

For example, a scalar 528000000 yields q8=66, final A5=66000 and stored halfword=464. Returning with A5=464 reproduces the stored halfword but fails the original register-output contract. A2 and A3 are untouched by this second routine; their incoming values may be residues from an earlier call, and restoring them to a guessed constant is unjustified.

## What a native write checker proves

A complete static scan of a bounded native function can establish that every decoded explicit integer destination belongs to an allowlist. That claim depends on complete/correct decoding, correctly bounded reachable code, and the absence of unanalysed direct calls, indirect calls or transfers. It must reject unknown encodings instead of silently skipping them. Instruction-specific implicit effects, CSR access, floating/vector state and system instructions need their own checks; a generic `rd` field is insufficient.

An allowlist alone does **not** establish the final values of allowed registers, correct return target, temporary or restored SP behavior, memory ordering, write width, fresh reads or function behavior. A query implementation that restores all A2..A5 can preserve all untouched registers while still disagreeing with the original query's required outputs. A fields implementation that leaves A4 arbitrary or truncates A5 to sixteen bits can pass an x14/x15 allowlist while failing original semantics. Failing to write an allowed register is not necessarily a success.

Checking a C function's final binary for A0/A1 preservation is stronger than relying on a `void` declaration, but it still does not prove the required A2..A5 residues or every architectural effect. An assembly adapter that saves and restores all temporary registers implements a different observable register contract unless it separately installs the original outputs. Ordinary C compiler ABI assumptions are not recovered original-binary ABI evidence.

## Evidence needed before dropping an output requirement

To justify omitting original residue restoration, establish all actual callers and entry paths, including indirect and resident/ROM callers if applicable. At each call, prove that every differing result register is overwritten before any possible read, branch, store, outgoing argument use, return forwarding or opaque helper use. The analysis must include alternate continuations and applicable interrupt/trap entry/exit behavior. A single immediate next instruction, one synthetic caller or ordinary ABI caller-saved convention does not prove whole-binary deadness. Unknown caller or interrupt behavior leaves the corresponding requirement unresolved.

The caller proof must also show preserved input/return registers, original GP-relative addressing assumptions, stack alignment/storage and RA return behavior for the proposed adapter. Physical MCU, resident ABI and OTA compatibility remain separate unproved gates. This review makes no drop-in, physical-device or flash-readiness claim.

## Replay

```sh
python3 check-source-review.py --project-root /absolute/path/project --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
```

The read-only checker pins the immutable proof and all five members, invokes its original checker, then verifies all 69 raw destination fields against `source-facts.json`. It supports `apk-analysis/` and published `analysis/` layouts, requires Python 3 and performs no network access, hardware I/O, RV32 execution or ISA emulation. The residue formulas remain explicitly identified static review conclusions; this command is not a general native binary verifier.
