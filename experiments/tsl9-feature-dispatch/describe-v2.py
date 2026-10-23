#!/usr/bin/env python3
"""Derive a bounded static contract from original records and real compiler objects."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT/'build/curated-source/feature-dispatch-20261023-v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def describe():
    manifest = json.loads((ROOT/'src/source-manifest.json').read_bytes())
    parent = json.loads((ROOT/'experiments/tsl9-channel-route/spec.json').read_bytes())
    outer = json.loads((ROOT/'experiments/tsl9-feature-dispatch-outer/spec.json').read_bytes())
    tree = json.loads((ROOT/'experiments/tsl9-feature-dispatch-tree/spec.json').read_bytes())
    handlers = json.loads((ROOT/'experiments/tsl9-feature-dispatch-handlers/original-blocks.json').read_bytes())
    E = runpy.run_path(str(ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v3.py'))['ELF']
    original_defs = {
        'feature-dispatch-tree': [[d['name'],int(d['original_address'],16),d['size']] for d in tree['regions']],
        'feature-dispatch-outer': outer['definitions'],
        'feature-dispatch-handlers': [['tsl9_feature_handler_'+format(d['start'],'x'),d['start'],d['end']-d['start']] for d in handlers['blocks']]
    }
    units = []
    for name,defs in original_defs.items():
        m = next(x for x in manifest['native_units'] if x['name'] == name)
        e = E(BASE/name/'c/curated/unit.o')
        unit = {k:m[k] for k in ('name','profile','origin_unit','curated_unit','origin_unit_sha256')}
        unit['definitions'] = sorted(defs,key=lambda x:x[1])
        unit['file_entry'] = next(f for f in manifest['files'] if f['destination'] == m['curated_unit'])
        unit['unit_entry'] = m
        unit['relocations'] = sorted([e.sections[r['section']]['name'],r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations)
        unit['native_object_sha256'] = {mode:sha(BASE/name/mode/'curated/unit.o') for mode in ('c','cpp')}
        unit['original_trial'] = {'feature-dispatch-tree':'experiments/tsl9-feature-dispatch-tree/build/trial-v3/trial.json',
                                 'feature-dispatch-outer':'experiments/tsl9-feature-dispatch-outer/build/trial-v2',
                                 'feature-dispatch-handlers':'experiments/tsl9-feature-dispatch-handlers/build/trial-v4/trial.json'}[name]
        units.append(unit)
    defs = [d for u in units for d in u['definitions']]
    assert len(defs) == 210 and len({d[0] for d in defs}) == 210 and sum(d[2] for d in defs) == 1922
    for lo,hi in [(0x829e,0x82a8),(0x14d2e,0x154a6)]:
        at = lo
        for n,a,z in sorted(defs,key=lambda d:d[1]):
            if lo <= a < hi:
                assert a == at
                at += z
        assert at == hi
    fw = (ROOT/parent['firmware']).read_bytes()
    tables = [
        dict(name='tsl9_feature_mode_table_1a6b8',section='.rodata.tsl9_feature_mode_table_1a6b8',address=0x1a6b8,
             targets=outer['table_targets']),
        dict(name='tsl9_feature_nested_table_1a6d4',section='.rodata.tsl9_feature_nested_table',address=0x1a6d4,
             targets=[0x15364,0x1536c,0x15370,0x15394,0x153b4,0x153b4,0x153b4,0x153b0])]
    for table in tables:
        if table['targets'] and isinstance(table['targets'][0],str):
            addresses = {n:a for n,a,z in defs}
            table['targets'] = [addresses[n] for n in table['targets']]
        table['bytes'] = 4*len(table['targets'])
        table['sha256'] = hashlib.sha256(fw[table['address']-0x8000:table['address']-0x8000+table['bytes']]).hexdigest()
    return dict(schema='TSL9-complete-feature-dispatch-contract-v2',
        firmware=parent['firmware'],firmware_sha256=parent['firmware_sha256'],
        reader='experiments/tsl9-feature-dispatch-tree/elf_reader-v3.py',
        reader_sha256=sha(ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v3.py'),
        original_reader='build/feature-dispatch-frontier-20261023-v1/reader-output.json',
        original_reader_sha256=sha(ROOT/'build/feature-dispatch-frontier-20261023-v1/reader-output.json'),
        curation_checker='scripts/verify-curated-source.py',curation_checker_sha256=sha(ROOT/'scripts/verify-curated-source.py'),
        curation_root=BASE.relative_to(ROOT).as_posix(),curation_receipt_sha256=sha(BASE/'verification.json'),
        previous_curation_root='build/curated-source/channel-filter-20261023-v1',
        previous_curation_receipt_sha256=parent['curation_receipt_sha256'],
        prior_manifest_commit='79a78e6729eff43966e18c6b1fb9a99cbcd909c5',
        prior_manifest_sha256='ae0b407623df2158e916293746e95b85ca131309c4085af240463ebfbb25c39c',
        parent_checker='experiments/tsl9-channel-route/verify-v2.py',
        parent_checker_sha256=sha(ROOT/'experiments/tsl9-channel-route/verify-v2.py'),
        parent_object_sha256='0a72ce02c4eb6893ab5f718443e07bf510bea9d5990fd7441a12645b6ae1174b',
        tools=parent['tools'],stdint_sha256=parent['stdint_sha256'],units=units,tables=tables,
        code_spans=[[0x829e,0x82a8],[0x14d2e,0x154a6]],
        literal_code_pointer_dependencies=[
            dict(AUIPC=0x15184,ADDI=0x15188,target=0x1069e,callee=0x1083c),
            dict(AUIPC=0x1523a,ADDI=0x1523e,target=0x1069e,callee=0x1083c)],
        target_executed=False,ISA_emulated=False,firmware_ready=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--limit',type=int,default=19000)
    a = p.parse_args()
    text = json.dumps(describe(),indent=2,ensure_ascii=True)+'\n'
    print(json.dumps(text[a.offset:a.offset+a.limit],ensure_ascii=True))
