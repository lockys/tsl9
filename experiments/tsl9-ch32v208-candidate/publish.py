"""Deliver audited local candidate artifacts; no network or target execution."""
from pathlib import Path
import argparse, hashlib, json, shutil, runpy

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def main(project, c, cpp, destination):
    project, destination = Path(project).resolve(), Path(destination).resolve()
    assert destination.is_relative_to(project/'candidate-bin') and not destination.exists()
    experiment = project/'experiments/tsl9-ch32v208-candidate'
    audit = runpy.run_path(str(experiment/'audit.py'))['audit']
    records = []
    for mode, receipt in (('c', c), ('cpp', cpp)):
        receipt = Path(receipt).resolve()
        result, producer = audit(receipt), read(receipt)
        assert result['passed'] and result['mode'] == mode
        assert result['sha256'] == '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'
        plan = read(producer['plan'])
        records.append(dict(mode=mode, producer=str(receipt), producer_sha256=sha(receipt),
                            guarded_core_source_count=plan['core_source_count'],
                            audit=str(receipt.parent/'audit.json'), audit_sha256=sha(receipt.parent/'audit.json'),
                            binary=producer['outputs']['tsl9-ch32v208-candidate.bin']))
    assert Path(records[0]['binary']['path']).read_bytes() == Path(records[1]['binary']['path']).read_bytes()
    baseline = {n:sha(project/n) for n in ('export-manifest.json','verification-r81.json')}
    destination.mkdir(parents=True)
    outputs = {}
    for name in ('tsl9-ch32v208-candidate.bin','tsl9-ch32v208-candidate.elf','tsl9-ch32v208-candidate.map'):
        source = Path(cpp).resolve().parent/name
        shutil.copyfile(source, destination/name)
        assert sha(source) == sha(destination/name)
        outputs[name] = dict(path=str(destination/name), bytes=(destination/name).stat().st_size,
                             sha256=sha(destination/name), source=str(source))
    for name in ('README.md','SCOPE.md'):
        shutil.copyfile(experiment/name,destination/name)
        outputs[name] = dict(path=str(destination/name), bytes=(destination/name).stat().st_size,
                             sha256=sha(destination/name), source=str(experiment/name))
    manifest = dict(schema='CH32V208-conditional-candidate-delivery-v1', passed=True,
        platform='CH32V208/D8W candidate, not physically identified', outputs=outputs,
        actual_builds=records, experiment=str(experiment), flash_base=0x8000, end_exclusive=0x1ac00,
        bytes=76800, unchanged_original_manifests=baseline,
        byte_exact_retained_Runtime=True, core_reused_with_source_hash_guards=True,
        guarded_core_source_counts={r['mode']:r['guarded_core_source_count'] for r in records},
        core_code_bytes=71762, core_RO_bytes=4685, freshly_compiled_original_carrier_bytes=353,
        high_level_source_fully_recovered=False, new_features_added=False, source_external_bytes=0,
        runtime_version_association='V4.1.00; not screenshot V4.1.60',
        external_address_assumptions={'__tsl9_rom_entry':0x40000,'__tsl9_opaque_address_19d10':0x19d10},
        unknown_table_tail_bytes=272, includes_BOOT_ROOT_ROM=False,
        target_ready=False, ota_verified=False, goal_complete=False, target_executed=False,
        hardware=False, network=False)
    assert all(sha(project/n) == digest for n,digest in baseline.items())
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,binary=outputs['tsl9-ch32v208-candidate.bin'],
                         manifest=str(destination/'manifest.json'),target_ready=False,ota_verified=False)))

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ('project','c','cpp','destination'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args();main(a.project,a.c,a.cpp,a.destination)
