"""Read-only RV32 ELF/Runtime coverage audit; no relocations are applied.
Writes only into this script's own coverage-review directory. No target execution.
"""
from pathlib import Path
import collections
import hashlib
import json
import struct

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

D = _paths["project_root"]()
E = D / 'experiments/tsl9-lookup-domain-closure'
OUT = Path(__file__).resolve().parent
BASE, LENGTH = 0x8000, 76800
EXPECTED_SHA = '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'
BUILD = {'c': '314eca1a9e964cb491b4a28a1d37889a', 'cpp': 'd4e57847e2914baa9f3eaa23347b7970'}
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))


def elf(path):
    b = path.read_bytes()
    assert b[:6] == b'\x7fELF\x01\x01'
    assert struct.unpack_from('<HH', b, 16) == (1, 243)
    start = struct.unpack_from('<I', b, 32)[0]
    stride, count, strings_index = struct.unpack_from('<HHH', b, 46)
    assert stride == 40 and start + count * stride <= len(b)
    sections = []
    for i in range(count):
        v = struct.unpack_from('<10I', b, start+i*stride)
        s = dict(index=i, name_offset=v[0], type=v[1], flags=v[2], addr=v[3], offset=v[4], size=v[5], link=v[6], info=v[7], align=v[8], entsize=v[9])
        assert s['type'] == 8 or s['offset'] + s['size'] <= len(b)
        sections.append(s)
    st = sections[strings_index]
    names = b[st['offset']:st['offset']+st['size']]
    for s in sections:
        s['name'] = names[s['name_offset']:names.index(0, s['name_offset'])].decode('ascii')
    relocations = collections.Counter()
    for s in sections:
        if s['type'] == 4:
            assert s['entsize'] == 12 and s['size'] % 12 == 0
            relocations[s['info']] += s['size'] // 12
    return b, sections, {s['name']: s for s in sections if s['name']}, relocations


def main():
    cfgpath = E / 'layout/closure.json'
    cfg = load(cfgpath)
    carrier = D / 'apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
    source = carrier.read_bytes()
    assert len(source) == LENGTH and sha(source) == EXPECTED_SHA == cfg['source_sha256']
    groups = sorted(cfg['output_groups'], key=lambda g: g['original_va'])
    assert len(groups) == 667 and len({g['output_section'] for g in groups}) == 667
    byte_owners = [0] * LENGTH
    rows = []
    for g in groups:
        off, size = g['original_va']-BASE, g['bytes']
        assert 0 <= off < LENGTH and off+size <= LENGTH
        for i in range(off, off+size): byte_owners[i] += 1
        member_owners = [0] * size
        for m in g['members']:
            assert m['original_va'] == g['original_va'] + m['output_offset']
            assert 0 <= m['output_offset'] and m['output_offset'] + m['bytes'] <= size
            for i in range(m['output_offset'], m['output_offset']+m['bytes']): member_owners[i] += 1
        assert all(n >= 1 for n in member_owners), 'Member hole: '+g['output_section']
        rows.append(dict(section=g['output_section'], original_va=g['original_va'], file_offset=off, size=size, kind=g['kind'], member_count=len(g['members']), shared_member_view_bytes=sum(n>1 for n in member_owners), source_sha256=sha(source[off:off+size])))
    assert not any(n > 1 for n in byte_owners), 'Mapped FLASH overlap'
    gaps = []
    at = 0
    while at < LENGTH:
        if byte_owners[at]: at += 1; continue
        end = at+1
        while end < LENGTH and not byte_owners[end]: end += 1
        gaps.append(dict(original_va=BASE+at, end_exclusive=BASE+end, file_offset=at, size=end-at, sha256=sha(source[at:end]), semantic_status='opaque_original_carrier_not_semantically_reconstructed', evidence='Original Runtime hash and file bounds only; no padding assumption'))
        at = end
    for g in gaps:
        if g['original_va'] == 0x199fa:
            g['evidence'] = 'fifty-fourth-round/plan.md:14 describes 199FA illegal/padding; exact original bytes retained, never synthesized'
        elif g['original_va'] == 0x19a91:
            g['evidence'] = 'fortieth-round/independent-ble-init/contract.md:81 explicitly declines to infer 19A91..19A93 as padding'
    modes = {}
    for mode, run in BUILD.items():
        build = E / 'build' / mode / run
        producer, audit = load(build/'producer.json'), load(build/'audit.json')
        p = Path(producer['objects']['memory']['path'])
        raw, sections, names, rels = elf(p)
        assert sha(raw) == producer['objects']['memory']['sha256']
        assert len(raw) == producer['objects']['memory']['bytes']
        assert audit['passed'] and audit['schema'] == 'R81-complete-native-static-audit'
        allocated = [s for s in sections if s['flags'] & 2 and s['size']]
        assert len(allocated) == 668
        comparisons, totals = [], collections.Counter()
        for row in rows:
            s = names[row['section']]
            assert s['type'] == 1 and s['flags'] & 2 and s['size'] == row['size']
            assert s['addr'] == 0, 'R81 ET_REL must not be mistaken for final VMA'
            b = raw[s['offset']:s['offset']+s['size']]
            original = source[row['file_offset']:row['file_offset']+row['size']]
            differences = [i for i, (a,b) in enumerate(zip(b,original)) if a != b]
            comparisons.append(dict(section=s['name'], elf_file_offset=s['offset'], elf_size=s['size'], elf_sh_addr=s['addr'], elf_sha256=sha(b), raw_equal_without_relocations=not differences, mismatched_bytes=len(differences), relocation_count=rels[s['index']]))
            assert not differences or rels[s['index']] > 0, 'Raw mismatch in a section without relocations'
            totals[row['kind']+'_bytes'] += len(b)
            totals[row['kind']+'_raw_mismatched_bytes'] += len(differences)
            totals['raw_equal_sections'] += not differences
            totals['relocations'] += rels[s['index']]
        extra = [s for s in allocated if s['name'] not in {g['section'] for g in rows}]
        assert len(extra) == 1
        s = extra[0]
        ram = cfg['memory']['ram']
        assert s['name'] == ram['output_section'] and s['size'] == ram['bytes'] and s['type'] == 8
        modes[mode] = dict(object=str(p), sha256=sha(raw), producer_sha256=sha((build/'producer.json').read_bytes()), audit_sha256=sha((build/'audit.json').read_bytes()), totals=dict(totals), sections=comparisons, ram=dict(section=s['name'], original_va=ram['origin'], end_exclusive=ram['origin']+s['size'], size=s['size'], data_bytes=ram['data_bytes'], bss_bytes=ram['bss_bytes'], elf_sh_addr=s['addr'], elf_file_offset=s['offset'], file_backed_bytes=0, type='SHT_NOBITS', lma_not_in_binary=True), existing_strict_undefined=audit['remaining_UND'])
    report = dict(schema='CH32V208-candidate-independent-coverage-v1', source=dict(path=str(carrier), bytes=LENGTH, base=BASE, end_exclusive=BASE+LENGTH, sha256=sha(source)), closure_sha256=sha(cfgpath.read_bytes()), mapped=dict(groups=len(groups), code_groups=sum(r['kind']=='code' for r in rows), readonly_groups=sum(r['kind']=='readonly' for r in rows), bytes=sum(n == 1 for n in byte_owners), percent=100*sum(n == 1 for n in byte_owners)/LENGTH, overlap_bytes=sum(n > 1 for n in byte_owners), shared_member_view_bytes=sum(r['shared_member_view_bytes'] for r in rows), member_holes=0), gaps=dict(count=len(gaps), bytes=sum(g['size'] for g in gaps), percent=100*sum(g['size'] for g in gaps)/LENGTH, ranges=gaps), groups=rows, modes=modes, relocations_applied=False, rebuilt=False, target_executed=False, network=False, hardware=False, target_ready=False, ota_verified=False, goal_complete=False)
    assert report['mapped']['bytes'] + report['gaps']['bytes'] == LENGTH
    report['c_cpp_group_payloads_identical'] = all(a['elf_sha256']==b['elf_sha256'] for a,b in zip(modes['c']['sections'],modes['cpp']['sections']))
    assert report['c_cpp_group_payloads_identical']
    report['all_raw_mismatch_sections_contain_relocations'] = True
    report['coverage_is_not_high_level_semantic_recovery_percentage'] = True
    report['historical_gap_search_boundary'] = ['fifty-fourth-round/plan.md:14', 'fortieth-round/independent-ble-init/contract.md:81', 'eighty-first-round/model-root/FEATURE-COVERAGE.md', 'eighty-first-round/model-root/experiments/tsl9-lookup-domain-closure/README.md']
    report['outside_source_272_bytes_added'] = False
    (OUT/'coverage.json').write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(mapped=report['mapped'], gaps={k:v for k,v in report['gaps'].items() if k!='ranges'}, modes={k:dict(totals=v['totals'],ram=v['ram']) for k,v in modes.items()}),indent=2))


if __name__ == '__main__': main()
