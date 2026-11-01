# One conditional TX-candidate guard comparison

[繁體中文](README.md)

At `0x8A76..0x8A82`, both the original V4.1.60 APP and TX candidate first execute the same `bne a4,a0,0x8A96`. On fallthrough they execute the same two compressed instructions; at `0x8A7E` the original compares `a4==a5`, while the candidate compares `a5==a0`, both targeting `0x8A96`.

If control falls through that preceding branch and no asynchronous action changes the registers, `a4==a0` holds and the two equality tests agree on that local path. The [checker](check.py) reads only 12 allowed bytes from each APP, pins instruction encodings and decodes the register fields and targets of the three branches; it does not execute the target. It does not rule out unknown direct entries into the middle, establish other TX differences, complete ABI, resident or hardware compatibility, or prove this BIN flashable.

## Local copy-loop comparison

At `0x8B10`, the original branches on unsigned `a0<s0` to copy at `0x8B52`, otherwise falling through to completion at `0x8B14`. The candidate branches on the complementary `a0>=s0` to completion at `0x8B2E`, otherwise falling through to the copy at `0x8B14`. Both extract the low 16-bit index identically; loop-body instruction order matches, with the sole non-branch difference reversing the operands of address addition. Both jump back to `0x8B0A`. The [checker](check-loop.py) pins bounded windows, decodes branch destinations and compares body encodings; it does not execute the target.

Given matching valid input registers and memory, normal execution, no entry into the middle and no asynchronous interference, this supports equivalent local comparisons, byte reads/writes and checksum accumulation order. It does not establish source/destination validity, all callers, the later completion path, device startup or flash readiness.

## Completion path and indirect slot

The original `[0x8B14,0x8B52)` and candidate `[0x8B2E,0x8B6C)` completion paths are each 62 bytes. Corresponding bytes match except for two encoding groups: the multiply reverses its source operands, and the `a2` address is calculated by adding GP before or after forming `GP+148`. Both calculate `(4*initial_a2 + GP + 148) mod 2^32`; identical following instructions read a byte there and obtain the tail-call target from `0x40050`.

With matching valid registers and memory, normal completion and no mid-path entry, exception or asynchronous interference, this supports the same corresponding record read and indirect slot call. The [checker](check-tail.py) pins two bounded byte windows without executing the target. Intermediate `a5` values may differ, which matters under exceptions or interrupts; actual slot identity, valid memory, complete ABI and device startup remain unverified.

## Entire TX prefix before the loop

The [prefix checker](check-prefix.py) compares the same-address 180-byte range `[0x8A56,0x8B0A)` in both images. All bytes match except the sentinel comparison above and the multiply at `0x8AD2`, which reverses source operands. Both multiply instructions write the low 32 bits of `a2*a5` to `a5`; the checker decodes MUL fields and reruns the sentinel branch check. The two instruction groups differ in four bytes total.

Together with the local loop and completion comparisons on this page, this supports a conditional comparison of the main TX path given normal entry, matching valid state, normal memory and no asynchronous interference. Unknown mid-function entries, exceptions/interrupts, side effects, unverified resident ABI and other hardware differences remain open; this is not evidence of a successful flash or restart. Only the specified APP windows are read, not excluded ranges; the target is not executed.

### Prefix branch targets after relocation

The [edge checker](check-prefix-edges.py) scans all 62 instruction boundaries in each prefix: all seven direct branch targets are instruction boundaries inside the same prefix or the shared return at `0x8B6C`, whose two bytes match between images. Two indirect calls occur at `0x8A8E` and `0x8AB4`, and a return occurs at `0x8ACA`; this check does not resolve the indirect-call targets or side effects. It also reruns the bounded loop and completion checks.

This rules out these seven identified direct branches landing in different instructions due to the loop relocation. It does not cover calculated mid-function entries from elsewhere, indirect-call effects, exceptions/interrupts or device execution, and does not prove complete equivalence or flash readiness.
