"""Project narrowly validated .comment mappings from three parsed-object views."""
import re
import types


def need(ok, message):
    if not ok:
        raise ValueError(message)


def comment_projections(baseline, combined, leaf_partial, views):
    """Validate all three partial links before projecting only their .comment mappings."""
    elfs = (baseline, combined, leaf_partial)
    sections = []
    mappings = []
    fields = ('type', 'flags', 'size', 'alignment', 'address', 'link', 'info', 'entry_size')
    for elf in elfs:
        found = [s for s in elf.sections if s['name'] == '.comment']
        need(len(found) == 1, 'unique .comment section required')
        section = found[0]
        index = section['index']
        need(0 < index < len(elf.sections) and elf.sections[index] is section
             and section['size'] > 0, 'invalid .comment section')
        need(section['type'] == 1, '.comment must be SHT_PROGBITS')
        data = elf.data(section)
        need(len(data) == section['size'], 'invalid .comment bytes length')
        sections.append((tuple(section[key] for key in fields), data))
        selected = []
        section_symbols = 0
        for symbol in elf.symbols:
            if symbol['index'] != index:
                continue
            if (symbol['name'], symbol['value'], symbol['size'], symbol['info'], symbol['other']) == ('', 0, 0, 3, 0):
                need(all(r['symbol'] is not symbol for r in elf.relocations),
                     '.comment section symbol referenced by relocation')
                section_symbols += 1
                continue
            need(re.fullmatch(r'\$d\.[0-9]+', symbol['name']) is not None
                 and (symbol['value'], symbol['size'], symbol['info'], symbol['other']) == (0, 0, 0, 0),
                 'unexpected or invalid .comment symbol')
            need(all(r['symbol'] is not symbol for r in elf.relocations),
                 '.comment mapping symbol referenced by relocation')
            selected.append(symbol)
        need(section_symbols == 1, 'exactly one .comment section symbol required')
        mappings.append(selected)
    need(sections[0] == sections[1] == sections[2], '.comment metadata or bytes differ')
    # This experiment expects exactly one leaf_partial contribution, not merely
    # equality of the totals (which would allow paired unexplained additions).
    need(len(mappings[2]) == 1, 'leaf_partial must have exactly one .comment mapping')
    # All retained fields are identical; only the numeric name suffix is normalized.
    need(len(mappings[1]) == len(mappings[0]) + len(mappings[2]),
         '.comment mapping multisets differ: combined != baseline + leaf_partial')
    projected = []
    for view, selected in zip(views, mappings):
        ids = {id(s) for s in selected}
        projected.append(types.SimpleNamespace(kind=view.kind, flags=view.flags,
            sections=view.sections, symbols=[s for s in view.symbols if id(s) not in ids],
            relocations=view.relocations, data=view.data, function_bytes=view.function_bytes))
    return projected
