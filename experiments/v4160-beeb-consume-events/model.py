"""Bounded byte-memory events derived from the static instruction slice."""

MASK = 0xffffffff
SOURCE = 0x2000beeb


def consume(memory, gp):
    """Mutate a mapped byte dict; return (exit, trace). No implicit bytes."""
    if not isinstance(gp, int) or not 0 <= gp <= MASK:
        raise ValueError('gp must be u32')
    a = (gp + 188) & MASK
    b = (gp + 189) & MASK
    trace = []

    def read(pc, addr):
        value = memory[addr]
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError('memory values must be bytes')
        trace.append((pc, 'read', addr, value))
        return value

    def write(pc, addr, value):
        value &= 255
        memory[addr] = value
        trace.append((pc, 'write', addr, value))

    x = read(0xaea2, SOURCE)
    if x != 0:
        write(0xaeac, a, 6)
        write(0xaeb0, b, x + 3)
        write(0xaeb8, SOURCE, 0)
    count = read(0xaebc, a)
    if count == 0:
        return '0xaf48', trace
    write(0xaec4, a, count - 1)
    read(0xaec8, b)
    return '0xaecc', trace
