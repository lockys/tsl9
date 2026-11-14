"""Conditional host-only model, not an instruction interpreter."""

TAIL = 0x9FC8


def initialize():
    """Model the separate initializer's byte store."""
    return 25


def step(counter, a0):
    """Return (counter, selected tail or None) for valid byte/uint32 inputs."""
    if not isinstance(counter, int) or not 0 <= counter <= 255:
        raise ValueError("counter must be a byte")
    if not isinstance(a0, int) or not 0 <= a0 <= 0xFFFFFFFF:
        raise ValueError("a0 must be an unsigned 32-bit integer")
    if a0 <= 24:
        if counter:
            counter -= 1
    elif counter == 0:
        return counter, TAIL
    return counter, None
