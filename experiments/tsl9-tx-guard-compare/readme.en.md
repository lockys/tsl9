# One conditional TX-candidate guard comparison

[繁體中文](README.md)

At `0x8A76..0x8A82`, both the original V4.1.60 APP and TX candidate first execute the same `bne a4,a0,0x8A96`. On fallthrough they execute the same two compressed instructions; at `0x8A7E` the original compares `a4==a5`, while the candidate compares `a5==a0`, both targeting `0x8A96`.

If control falls through that preceding branch and no asynchronous action changes the registers, `a4==a0` holds and the two equality tests agree on that local path. The [checker](check.py) reads only 12 allowed bytes from each APP, pins instruction encodings and decodes the register fields and targets of the three branches; it does not execute the target. It does not rule out unknown direct entries into the middle, establish other TX differences, complete ABI, resident or hardware compatibility, or prove this BIN flashable.

## Local copy-loop comparison

At `0x8B10`, the original branches on unsigned `a0<s0` to copy at `0x8B52`, otherwise falling through to completion at `0x8B14`. The candidate branches on the complementary `a0>=s0` to completion at `0x8B2E`, otherwise falling through to the copy at `0x8B14`. Both extract the low 16-bit index identically; loop-body instruction order matches, with the sole non-branch difference reversing the operands of address addition. Both jump back to `0x8B0A`. The [checker](check-loop.py) pins bounded windows, decodes branch destinations and compares body encodings; it does not execute the target.

Given matching valid input registers and memory, normal execution, no entry into the middle and no asynchronous interference, this supports equivalent local comparisons, byte reads/writes and checksum accumulation order. It does not establish source/destination validity, all callers, the later completion path, device startup or flash readiness.
