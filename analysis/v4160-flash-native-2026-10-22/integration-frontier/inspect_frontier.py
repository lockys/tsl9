"""Inspect existing relocations as data; never execute firmware or fill gaps."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
OBJECT_SHA = '9a5bd413ce37d618859031c4246f55a717b4c0cc64063adaee9c933ef07179b9'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MANIFEST_SHA = 'd952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7'
EXTENTS = {0x9c0a:64,0x18e90:8,0x18e98:30,0x18eb6:14,0x18ec4:46,0x18ef2:100}
EXPECTED = {(0x9c1e,17,0x18e98),(0x9c26,17,0x18e90),
            (0x9c2c,17,0x18ec4),(0x9c34,17,0x18ef2),(0x9c38,17,0x18eb6),
            (0x12e7a,17,0x9c0a),(0x12f0c,17,0x9c0a),(0x12f6e,17,0x9c0a),
            (0x13078,17,0x9c0a),(0x130fc,17,0x9c0a),(0x1315e,17,0x9c0a),
            (0x197c8,17,0x18e98),(0x197ce,17,0x18ec4),
            (0x197d8,17,0x18ef2),(0x197dc,17,0x18eb6),
            (0x18ee4,44,0x18ee0),(0x18f06,44,0x18f02),
            (0x18f10,44,0x18f0c),(0x18f2e,44,0x18f2a),
            (0x18f32,16,0x18f1a),(0x18f48,44,0x18f44),
            (0x9e7a,45,0x9c0a),(0x9d00,45,0x9c0a)}


def need(v, text):
    if not v:
        raise ValueError(text)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def location(root, published, workspace):
    paths = (root/published, root/workspace)
    return next((p for p in paths if p.is_file()), paths[0])


def validate(rows):
    need(len(rows) == len(EXPECTED) == 23, 'exact relocation multiplicity')
    need({(r['PC'],r['type'],r['target']) for r in rows} == EXPECTED,
         'exact original relocation sites, roles and targets')
    external = [r for r in rows if not r['owned_source']]
    need(len(external) == 12 and all(r['target'] in EXTENTS for r in external),
         'all twelve retained external references enter original function starts')
    need(sum(r['owned_source'] and r['type'] == 17 for r in rows) == 5,
         'five owned direct calls')
    need(sum(r['owned_source'] and r['type'] in (16,44) for r in rows) == 6,
         'six owned polling/loop branch relocations need explicit replacement')


def inspect(root, path):
    parser = location(root,'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',
                      'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py')
    firmware = location(root,'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
                        'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
    need(sha(parser) == PARSER_SHA and sha(firmware) == FW_SHA,'pinned parser and original Runtime')
    manifest = root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json'
    need(sha(manifest) == MANIFEST_SHA,'pinned original placement manifest')
    allocations = json.loads(manifest.read_bytes())['allocations']
    e = runpy.run_path(str(parser))['ELF'](path)
    need(e.kind == 1 and len(e.relocations) == 8276,'actual retained ET_REL carrier with all relocations')
    aliases = {s['name']:s for s in e.symbols if s['name'].startswith('__tsl9v4160_call_')}
    section_base = {e.byname[n]['index']:r['originalVA'] for n,r in allocations.items() if n in e.byname}
    for name,s in aliases.items():
        value = int(name.removeprefix('__tsl9v4160_call_'),16)-s['value']
        if s['index'] in section_base:
            need(section_base[s['index']] == value,'consistent section-relative numeric origin')
        section_base[s['index']] = value
    owners = {}
    raw = firmware.read_bytes()
    for va,size in EXTENTS.items():
        s = aliases['__tsl9v4160_call_'+format(va,'x')]
        sec = e.sections[s['index']]
        need(s['value'] == 0 and s['size'] == sec['size'] == size and s['info'] == 18,
             'actual full function symbol, role and extent')
        need(e.data(sec) == raw[va-0x8000:va-0x8000+size],'all six retained bodies equal original bytes')
        owners[s['index']] = va
    rows = []
    for r in e.relocations:
        s = r['symbol']
        if s['index'] not in owners:
            continue
        owner = e.byname[r['owner']]
        need(owner['index'] in section_base,'source owner has real section-relative entry')
        rows.append(dict(PC=section_base[owner['index']]+r['offset'],owner=r['owner'],offset=r['offset'],
                         type=r['type'],target=owners[s['index']]+s['value']+r['addend'],
                         target_symbol=s['name'],symbol_value=s['value'],addend=r['addend'],
                         owned_source=owner['index'] in owners))
    rows.sort(key=lambda r:(r['PC'],r['type'],r['target']))
    validate(rows)
    negatives = []
    trials = [('missing-record',lambda a:a.pop()),
              ('duplicate-record',lambda a:a.append(copy.deepcopy(a[0]))),
              ('external-interior-target',lambda a:a.__setitem__(next(i for i,r in enumerate(a) if not r['owned_source']),
                  dict(next(r for r in a if not r['owned_source']),target=0x18f50))),
              ('wrong-relocation-role',lambda a:a[0].update(type=1)),
              ('wrong-source-site',lambda a:a[0].update(PC=a[0]['PC']+2))]
    for name,change in trials:
        altered = copy.deepcopy(rows)
        change(altered)
        try:
            validate(altered)
        except ValueError as ex:
            negatives.append(dict(name=name,rejected=True,reason=str(ex)))
        else:
            raise ValueError('accepted semantic relocation negative '+name)
    need(sha(path) == OBJECT_SHA,'exact previously source-integrated object identity')
    return dict(schema='TSL9-six-Flash-integration-frontier-v1',passed=True,
                object=dict(sha256=OBJECT_SHA,bytes=path.stat().st_size,RELA=8276),
                parser_sha256=PARSER_SHA,firmware_sha256=FW_SHA,manifest_sha256=MANIFEST_SHA,rows=rows,
                external_entry_references=12,owned_calls=5,owned_branches=6,
                outside_owned_relocations=8265,semantic_negative_controls=negatives,
                gap=dict(start=0x18f50,end_exclusive=0x18f56,bytes=6,
                         ownership_proved=False,padding_emitted=False),
                search_boundary='Recorded section-relative RELA in this exact retained object only; no ROM, numeric-indirect, runtime or missing-reference completeness claim.',
                full_image_integration=False,all_original_interior_entries_excluded=False,
                target_execution=False,emulation=False,hardware=False,network=False,new_BIN=False,OTA_ready=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--merged-object',type=Path,required=True)
    p.add_argument('--check',action='store_true')
    p.add_argument('--seal',action='store_true')
    a = p.parse_args()
    report = inspect(a.project_root.resolve(),a.merged_object.resolve())
    raw = (json.dumps(report,indent=2)+'\n').encode('utf8')
    out = HERE/'report.json'
    if a.check:
        need(out.read_bytes() == raw,'exact archived report replay')
    else:
        with out.open('xb') as stream:
            stream.write(raw)
    if a.seal:
        files = sorted([p for p in HERE.iterdir() if p.is_file() and p.name != 'seal.json'])
        seal = dict(passed=True,members=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files],
                    target_execution=False,network=False,hardware=False,new_BIN=False,OTA_ready=False)
        with (HERE/'seal.json').open('xb') as stream:
            stream.write((json.dumps(seal,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,recorded_RELA=8276,external_entries=12,owned_calls=5,
                         owned_branches=6,semantic_negatives=5,unowned_gap_bytes=6,OTA_ready=False)))


if __name__ == '__main__':
    main()
