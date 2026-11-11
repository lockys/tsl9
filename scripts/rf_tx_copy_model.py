"""Synthetic, normal-completion model of the selected V1.31 RF_Tx copy path.

Addresses are numeric u32 values, memory is a caller-supplied byte mapping, and
no device accesses are performed. This models neither guards nor other calls.
"""

POINTER_WORD = 0x20003534
U32_END = 1 << 32


def load_pointer(memory):
    """Read W as a little-endian word from the synthetic byte map."""
    word = [memory.get(POINTER_WORD + i) for i in range(4)]
    if any(not isinstance(b, int) or isinstance(b, bool) or not 0 <= b <= 255 for b in word):
        raise ValueError('missing or invalid pointer word')
    return int.from_bytes(bytes(word), 'little')


def tx_copy_from_word(memory, source, length, packet_type):
    """Load at 64e0e, perform the selected path, observe the 64e28 reload.

    Assumes no intervening modifications beyond the modeled stores/helper and
    normal return. Does not model the later 64e5c reload or intervening calls.
    """
    p = load_pointer(memory)
    result = tx_copy(memory, p, source, length, packet_type)
    return result, p, load_pointer(result)


def tx_copy(memory, p, source, length, packet_type):
    """Return a new memory mapping after the two prefix stores and forward copy.

    p is the value already loaded at 64e0e, not a live pointer lookup. All
    addressed bytes must be present; ranges must not wrap. The source must be
    nonzero (the other RF_Tx branch is outside this model). The helper's MMIO
    save/clear/restore and exceptional execution are outside this data model.
    """
    values = (p, source, length, packet_type)
    if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < U32_END for v in values):
        raise ValueError('arguments must be u32 integers')
    if not source or p + 2 + length > U32_END or source + length > U32_END:
        raise ValueError('null source or wrapping range')
    # A0=P+2 must be nonzero for the helper copy to run.
    if p + 2 >= U32_END:
        raise ValueError('invalid destination')
    result = dict(memory)
    addresses = set(range(p, p + 2 + length)) | set(range(source, source + length))
    if any(a not in result or not isinstance(result[a], int) or isinstance(result[a], bool)
           or not 0 <= result[a] <= 255 for a in addresses):
        raise ValueError('missing or invalid synthetic byte')
    result[p] = packet_type & 255
    result[p + 1] = length & 255
    for i in range(length):
        result[p + 2 + i] = result[source + i]
    return result
