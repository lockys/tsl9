"""Source-layout plan for replacing six Flash carriers; no native execution."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_OBJECT = '9a5bd413ce37d618859031c4246f55a717b4c0cc64063adaee9c933ef07179b9'
OLD_MANIFEST = 'd952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7'
OLD_RUNNER = 'b26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
SIZES = {0x9c0a:64,0x18e90:8,0x18e98:30,0x18eb6:14,0x18ec4:46,0x18ef2:100}


def need(value,text):
    if not value:
        raise ValueError(text)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def find(root,slug,member):
    for p in (root/'analysis'/slug/member,root/('apk-analysis/tsl9-'+slug)/member):
        if p.is_file():
            return p
    raise ValueError('Missing pinned input '+slug+'/'+member)


def constraints(value):
    need(value['allocations'] == 691 and value['readable_original_bytes'] == 526,'exact full storage and eleven source extents')
    need(value['retained_storage_sections'] == 680,'six Flash plus five IRQ owned storage sections')
    need(value['outside_RELA'] == 8259 and value['old_owned_RELA'] == 17,'exact old outside/owned multiplicity')
    need(len(value['incoming']) == 20 and all(r['symbol']['offset'] == 0 for r in value['incoming']),
         'twenty recorded external function-entry references')
    need(value['program_required_bytes'] == 100 and value['program_tail_is_padding'] is False,'no implicit six-byte tail waiver')


def inspect(root,obj):
    manifest = root/'experiments/tsl9-v4160-irq-image-integration/source-manifest.json'
    old_runner = find(root,'v4160-irq-image-integration-2026-10-21','integration/verify_image.py')
    parser = find(root,'v4160-irq-native-2026-10-21','compiler-review/elf32.py')
    need(sha(manifest) == OLD_MANIFEST and sha(old_runner) == OLD_RUNNER and sha(parser) == PARSER,'fixed source plan/tool bytes')
    m = json.loads(manifest.read_bytes())
    V = load('prior_irq_integration_plan',old_runner)
    e = load('bounded_plan_elf',parser).ELF(obj)
    need(sha(obj) == OLD_OBJECT and e.kind == 1 and len(e.relocations) == 8276,'actual prior partial object')
    need(set(V.alloc(e)) == set(m['allocations']) and len(V.alloc(e)) == 691,'all original allocation owners')
    syms = {s['name']:s for s in e.symbols}
    selected = [{k:r[k] for k in ('name','originalVA','bytes','global_alias','producer')} for r in m['selected_sections']]
    units = {name:(root/name).read_bytes() for name in m['source_units']}
    for name,raw in units.items():
        need(hashlib.sha256(raw).hexdigest() == m['source_files'][name],'all thirty-four original C carrier sources')
    for va,size in SIZES.items():
        alias = '__tsl9v4160_call_'+format(va,'x')
        s = syms[alias]
        sec = e.sections[s['index']]
        name = sec['name']
        need(s['info'] == 18 and s['value'] == 0 and s['size'] == sec['size'] == size,'exact original Flash FUNC owner')
        need(hashlib.sha256(e.data(sec)).hexdigest() == m['allocations'][name]['sha256'],'Flash carrier bytes equal original source extent')
        producers = [n for n,raw in units.items() if ('.section '+name+',').encode() in raw]
        need(len(producers) == 1,'exact quoted source carrier producer')
        selected.append(dict(name=name,originalVA=va,bytes=size,global_alias=alias,producer=producers[0]))
    names = {r['name'] for r in selected}
    need(len(names) == len(selected) == 11,'eleven distinct original function storage owners')
    for name in m['allocations']:
        sec = e.byname[name]
        need({k:sec[k] for k in ('type','flags','size','alignment','entry_size')} == m['section_metadata'][name],
             'full original section metadata')
    selected_by_unit = {}
    for r in selected:
        selected_by_unit.setdefault(r['producer'],{})[r['name']] = r
    filtered = []
    for name,rows in sorted(selected_by_unit.items()):
        raw = units[name]
        after = V.filtered_source(raw,rows)
        need(all(('.section '+n+',').encode() not in after for n in rows),'all selected quoted blocks removed')
        filtered.append(dict(path=name,removed=sorted(rows),before_sha256=hashlib.sha256(raw).hexdigest(),
                             filtered_sha256=hashlib.sha256(after).hexdigest(),removed_source_bytes=len(raw)-len(after)))
    inside = [V.relocation(e,r) for r in e.relocations if r['owner'] in names]
    outside = [V.relocation(e,r) for r in e.relocations if r['owner'] not in names]
    incoming = [r for r in outside if r['symbol']['owner'] in names]
    original_roles = [V.role(e,s) for s in e.symbols]
    branch_roles = [r for r in inside if r['type'] in (16,44)]
    need(len(branch_roles) == 6 and len(inside) == 17,'six old Flash branch records and eleven direct calls')
    need(not any(b['role']['owner'] in {r['name'] for r in selected if r['originalVA'] in SIZES}
                 for b in m['section_relative_bindings']),'no original canonical interior binding inside six Flash owners')
    checks = dict(allocations=691,readable_original_bytes=sum(r['bytes'] for r in selected),
                  retained_storage_sections=691-len(names),outside_RELA=len(outside),old_owned_RELA=len(inside),
                  incoming=incoming,program_required_bytes=100,program_tail_is_padding=False)
    constraints(checks)
    negative = []
    changes = [('drop-storage',lambda x:x.update(allocations=690)),
               ('waive-six-bytes',lambda x:x.update(program_required_bytes=94)),
               ('invent-padding',lambda x:x.update(program_tail_is_padding=True)),
               ('lose-outside-RELA',lambda x:x.update(outside_RELA=8258)),
               ('invent-interior-entry',lambda x:x['incoming'][0]['symbol'].update(offset=2)),
               ('omit-incoming-reference',lambda x:x['incoming'].pop())]
    for label,change in changes:
        altered = copy.deepcopy(checks)
        change(altered)
        try:
            constraints(altered)
        except ValueError as ex:
            negative.append(dict(case=label,rejected=True,reason=str(ex)))
        else:
            raise ValueError('accepted integration constraint mutation '+label)
    return dict(schema='TSL9-eleven-function-source-layout-plan-v1',passed=True,
                prior_object_sha256=OLD_OBJECT,prior_manifest_sha256=OLD_MANIFEST,prior_runner_sha256=OLD_RUNNER,
                parser_sha256=PARSER,selected=selected,filtered_carrier_units=filtered,
                outside_RELA_semantic_sha256=V.digest(sorted(outside,key=lambda r:json.dumps(r,sort_keys=True))),
                original_symbol_roles_sha256=V.digest(original_roles),old_owned_RELA=inside,
                all_53_canonical_bindings_retained=True,checks=checks,negative_controls=negative,
                expected_native_compile_units=42,new_native_extent_or_branch_contracts_admitted=False,
                search_boundary='Exact prior source-integrated object and pinned quoted sources; not runtime/ROM/indirect-reference completeness.',
                native_compilation_performed=False,new_BIN=False,full_image_integration=False,
                target_execution=False,hardware=False,network=False,OTA_ready=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--merged-object',required=True,type=Path)
    p.add_argument('--check',action='store_true')
    a = p.parse_args()
    report = inspect(a.project_root.resolve(),a.merged_object.resolve())
    payload = (json.dumps(report,indent=2)+'\n').encode('utf8')
    out = HERE/'report.json'
    if a.check:
        need(out.read_bytes() == payload,'exact plan replay')
    else:
        with out.open('xb') as f:
            f.write(payload)
    print(json.dumps(dict(passed=True,allocations=691,selected_functions=11,carrier_units_filtered=len(report['filtered_carrier_units']),
                          outside_RELA=8259,owned_RELA_to_replace=17,incoming_entry_references=20,
                          controls=len(report['negative_controls']),native_compilation=False,new_BIN=False)))
