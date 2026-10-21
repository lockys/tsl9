# Original clock caller obligations

**Preserving only registers untouched by the original clock function is insufficient to prove a drop-in query replacement.** Original query's path-dependent A3 survives the known initialization sequence and is exposed to an unresolved indirect callback. Replacing that output with a preserved entry value is not justified by a standard C calling convention or by the public function's `void` return type.

This audit reads original ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. It reuses the sealed 214-byte / 69-instruction clock source proof and the sealed 9A42/helper ABI proof. New retained caller evidence covers **298 bytes / 98 instructions** in five bounded ranges: main `0x9008..0x901A`, init `0x9250..0x9290`, intervening `0x9A42..0x9AD2`, following `0x9F4C..0x9F74`, and the next callee's prefix `0x131C2..0x131E2`. `verification.json` retains exact bytes, addresses, instruction rows, direct-format candidates and source seal digests; `caller-contract.json` states the obligations and limits.

## Exact normal caller chain

| Call PC | Target | Return link |
|---|---|---|
| `0x900C` | init `0x9250` | `0x900E` |
| `0x9254` | query `0x18834` | `0x9258` |
| `0x9258` | intervening `0x9A42` | `0x925C` |
| `0x925C` | derived fields `0x1973C` | `0x9260` |
| `0x9260` | `0x9F4C` | `0x9264` |
| `0x9264` | `0x131C2` | `0x9268` |

Init makes these calls without local argument-register preparation between them. The original clock bodies do not write RA or SP; on normal, unaltered control they return using the link just installed by their caller. Init itself subtracts 16 from SP, saves RA at SP+12, later reloads that slot, adds 16, and tail-jumps to `0x17BF6`. A new native function's stack writes and restored final SP are a separate obligation; matching final register values alone does not prove that new stack accesses fit the installed memory or interrupt environment.

## Concrete register liveness

Original query writes only A2–A5. A2 is unchanged on default and internal paths, but becomes `0x00C00000` on the external multiplier path. A3 becomes 4 for selector 4; 8 for selector 0 or 12; 17 for internal multiplier paths; `0x40021000` for the external mask-equal path; or the low 32 bits of a fresh fallback config shifted left 14 for the external fallback path. A4 ends as the zero-extended live table byte; A5 ends as the shifted fresh scalar word.

Original derivation writes only A4 and A5: A4 ends as 1000, and A5 holds the full product `(((uint32 scalar / 8000000) & 255) * 1000)`, although the memory halfword store writes only its low 16 bits. A0/A1/A2/A3 are untouched by this body.

On the inspected normally completing prefix, query's incoming A0/A1 and outgoing A4/A5 are overwritten in `0x9A42` before those incoming values are read. Derivation's A4/A5 are overwritten by `0x9F4C` before use. The next function `0x131C2` overwrites A1 at `0x131CA`, A2 at `0x131CE`, and A0 at `0x131D8` before its first callback. These local deadness observations are conditional on the inspected synchronous path, not whole-program or asynchronous proofs.

**A3 has no intervening definition.** The actual 9A42 body and its helpers preserve A3, derivation preserves it, and 9F4C only changes A4/A5. At `0x131C6`, the next callee reads a function pointer from `0x4004C`; `0x131E0` performs JALR through that fresh pointer. It presents the query-produced A3 to an unresolved target. The pointer implementation and prototype have not been proved, so this audit does not assert that A3 is consumed, nor that it is ignored. A3 is a concrete remaining caller obligation, not evidence of a fourth C argument or of a recovered original prototype.

## Boundaries and remaining gaps

The intervening routine clears CSR `0x800` mask `0x88` at `0x9A50`, then sets the same mask at `0x9AC2`. It does not restore a captured old CSR value. This source evidence does not establish that interrupts are excluded during either clock call, or that all handlers preserve the relevant registers. No asynchronous handler or installed ROM callback behavior is assumed.

A bounded scan decodes JAL and RV32 C.JAL/C.J target immediates at all **38,400 halfword-aligned positions** of this image. For targets `0x9250`, `0x18834`, `0x1973C`, it finds only the three already source-proved calls `0x900C`, `0x9254`, `0x925C`. The scan is a raw-format candidate scan: it does not prove a code/data partition, exclude instructions at unusual entry boundaries, inspect computed JALR destinations, recover pointer callers, or prove there are no other callers.

General drop-in claims still require the original function's full relevant output-register contract, return/stack compatibility, linked placement and remaining callers, plus the installed interrupt/ROM/hardware environment. The derived A4/A5 results are locally dead on this one prefix; that does not establish their global irrelevance. This audit executes no firmware or ISA emulator and performs no network or hardware I/O. `audit.py --image <original-BIN> --r2 <radare2-path>` reproduces the read-only source audit.

