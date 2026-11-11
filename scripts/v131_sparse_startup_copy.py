"""Conditional V1.31 startup word-copy effects over explicit sparse byte maps.

Host model only: no instruction execution, physical fault prediction, or implicit
flash/RAM contents. Each word is read completely before its destination is written.
"""
FIRST = (0x402B0, 0x20000040, 0x20002E70)
SECOND = (0x6EAA4, 0x20002E70, 0x20002EF8)


def copy(source, destination, which):
    """Copy fixed inclusive-last-word range; return prefix and missing byte on fault.

    source and destination are explicit address-to-byte mappings. Destination is
    copied, not mutated. An absent source byte halts before that word's write.
    """
    if which not in ('first', 'second'):
        raise ValueError('unknown copy')
    src, dst, last = FIRST if which == 'first' else SECOND
    out = dict(destination)
    for offset in range(0, last - dst + 4, 4):
        word = []
        for address in range(src + offset, src + offset + 4):
            if address not in source:
                return {'status': 'missing-source', 'address': address,
                        'words_copied': offset // 4, 'memory': out}
            value = source[address]
            if type(value) is not int or not 0 <= value <= 255:
                raise ValueError('invalid source byte')
            word.append(value)
        out.update((dst + offset + i, value) for i, value in enumerate(word))
    return {'status': 'copied', 'words_copied': (last - dst + 4) // 4,
            'memory': out}
