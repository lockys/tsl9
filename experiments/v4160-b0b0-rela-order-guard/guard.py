"""Boundary and ordered relocation projection for the B0B0 split checker."""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_owners(elf):
    """Reject REL, invalid owners, and repeated owners, including empty sections."""
    owners = set()
    for section in elf.sections:
        if section.get('type') in (4, 9):
            need(section['type'] == 4, 'RELA encoding only')
            owner = section['info']
            need(0 < owner < len(elf.sections), 'invalid relocation section owner index')
            need(owner not in owners, 'multiple relocation sections for owner')
            owners.add(owner)


def relocation_facts(elf, target_section, target_index, target_name, mapping_kind):
    """Return (retained ordered records with symbol facts, removed records)."""
    sections = {s['name']: s for s in elf.sections}
    retained, removed = [], []
    for r in elf.relocations:
        symbol = r['symbol']
        need(mapping_kind(symbol) is None, 'relocation references a mapping symbol')
        need(r['owner'] and r['owner'] in sections, 'invalid relocation owner section')
        if symbol['info'] & 15 == 3:
            need(0 < symbol['index'] < len(elf.sections), 'invalid relocation section symbol target')
        if r['owner'] != target_section:
            need(symbol['name'] != target_name
                 and (target_index is None or symbol['index'] != target_index),
                 'retained relocation references removed section')
        record = (r['owner'], r['offset'], r['type'], r['addend'], symbol['name'])
        if r['owner'] == target_section:
            removed.append(record)
        else:
            index = symbol['index']
            owner = ('section', elf.sections[index]['name']) if 0 < index < len(elf.sections) else ('special', index)
            retained.append((record, owner, symbol['value'], symbol['size'], symbol['info'], symbol['other']))
    return retained, removed
