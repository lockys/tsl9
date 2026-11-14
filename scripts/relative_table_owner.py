"""Checks for the split original-coordinate relative-table owner in a linked ELF."""
import struct


def check_relative_table_owner(result):
    owned = sorted((s for s in result.sections if s['flags'] & 2 and s['size']
                    and s['address'] < 0x1a6b8 and s['address'] + s['size'] > 0x1a6a0),
                   key=lambda s: s['address'])
    if ([(s['address'], s['size']) for s in owned] != [(0x1a6a0, 4), (0x1a6a4, 20)]
        or any(s['type'] != 1 or s['flags'] != 2 for s in owned)
        or result.data(owned[0]) != bytes(4)
        or struct.unpack('<5i', result.data(owned[1])) != tuple(x - 0x1a6a4 for x in
            (0x1452e, 0x1453e, 0x1454a, 0x1473e, 0x14748))):
        raise ValueError('Relative table ownership or values changed')
    for name, address, size, owner in (('tsl9_opaque_gap_0001a6a0', 0x1a6a0, 24, owned[0]),
                                       ('tsl9_opaque_prefix_0001a6a0', 0x1a6a0, 4, owned[0]),
                                       ('tsl9_relative_table_0001a6a4', 0x1a6a4, 20, owned[1])):
        symbols = [s for s in result.symbols if s['name'] == name]
        if (len(symbols) != 1 or symbols[0]['value'] != address or symbols[0]['size'] != size
            or symbols[0]['info'] != 0x11 or symbols[0]['other'] != 0
            or symbols[0]['index'] != owner['index']):
            raise ValueError('Relative table symbol changed: ' + name)
