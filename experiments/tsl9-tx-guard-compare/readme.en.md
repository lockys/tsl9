# One conditional TX-candidate guard comparison

[繁體中文](README.md)

At `0x8A76..0x8A82`, both the original V4.1.60 APP and TX candidate first execute the same `bne a4,a0,0x8A96`. On fallthrough they execute the same two compressed instructions; at `0x8A7E` the original compares `a4==a5`, while the candidate compares `a5==a0`, both targeting `0x8A96`.

If control falls through that preceding branch and no asynchronous action changes the registers, `a4==a0` holds and the two equality tests agree on that local path. The [checker](check.py) reads only 12 allowed bytes from each APP, pins instruction encodings and decodes the register fields and targets of the three branches; it does not execute the target. It does not rule out unknown direct entries into the middle, establish other TX differences, complete ABI, resident or hardware compatibility, or prove this BIN flashable.
