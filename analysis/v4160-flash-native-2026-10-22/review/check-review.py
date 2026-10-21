#!/usr/bin/env python3
"""Read-only source/receipt replay; never executes original or rebuilt RV32."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--firmware',type=Path)
    p.add_argument('--old-runtime',type=Path)
    p.add_argument('--boot',type=Path)
    p.add_argument('--old-evidence',type=Path)
    p.add_argument('--archive-root',type=Path,help='Original review build/ archive for actual artifact replay; recorded tool/absolute paths must remain available')
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=Path(__file__).resolve().parent;r=read(root/'review.json')
    for x in r['model_inputs']:
        target=(project/x['path']).resolve(strict=True);target.relative_to(project)
        need(sha(target)==x['sha256'],'Reviewed model/helper input '+x['path'])
    for x in r['case_inputs']:
        target=(root.parent/x['path']).resolve(strict=True);target.relative_to(root.parent.resolve())
        need(sha(target)==x['sha256'],'Reviewed native/source input '+x['path'])
    source=root.parent/'source';need(sha(source/'seal.json')==r['source_seal_sha256'],'Original source seal')
    for x in read(source/'seal.json')['members']:
        target=(source/x['path']).resolve(strict=True);target.relative_to(source)
        need(sha(target)==x['sha256'] and target.stat().st_size==x['bytes'],'Original source sealed member')
    raw_checked=False
    if a.firmware:
        raw=a.firmware.read_bytes();need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==r['original_firmware_sha256'],'Exact ID2966 original')
        decoder=load('readonly_flash_raw',source/'inspect.py');proof=read(source/'source-proof.json')
        need(decoder.facts(raw)==proof['ledger'],'All262 original bytes /99 source rows')
        for x in proof['raw_negatives']:
            changed=bytearray(raw);offset=x['PC']-0x8000;replacement=bytes.fromhex(x['after'])
            need(changed[offset:offset+len(replacement)].hex()==x['before'],'Actual original mutation anchor')
            changed[offset:offset+len(replacement)]=replacement
            try:decoder.facts(changed)
            except ValueError:pass
            else:raise ValueError('Raw source negative accepted '+x['name'])
        raw_checked=True
    cross_checked=False
    if any((a.old_runtime,a.boot,a.old_evidence)):
        need(all((a.firmware,a.old_runtime,a.boot,a.old_evidence)),'Cross-version replay needs all three exact images and historical native evidence')
        comparison=load('readonly_flash_comparison',root/'compare-versions.py')
        need(comparison.compare(project,a.old_runtime,a.boot,a.firmware,a.old_evidence)==read(root/'cross-version.json'),'Exact bounded historical/current raw comparison')
        cross_checked=True
    modes={'effects':set(),'host':set(),'native':set()};host_controls=0;native_controls=0
    for x in r['receipts']:
        path=(root/x['path']).resolve(strict=True);path.relative_to(root)
        need(sha(path)==x['sha256'],'Exact selected actual receipt')
        v=read(path);kind=x['kind'];mode=v['language'] if kind=='effects' else v['mode'];modes[kind].add(mode)
        need(v['passed'] is True,'Actual successful run')
        if kind=='effects':
            need(v['positive']['result']=={'passed':True,'groups':1,'cases':12,'checks':8964,'synthetic_effects_only':True},'Independent expected-effect coverage')
            need(v['actual_mutants_rejected']==12 and all(z['result']['rejected'] for z in v['actually_compiled_mutants']),'Twelve independently compiled behavior controls')
            host_controls+=12
        elif kind=='host':
            need(v['tests']=={'passed':True,'groups':5,'cases':481,'checks':247191,'synthetic_provider':True,'RV32_execution':False},'Full canonical host coverage')
            need(len(v['actual_compiled_controls'])==6 and all(z['compiled'] and z['rejected'] for z in v['actual_compiled_controls']),'Six canonical compiled behavior controls')
            host_controls+=6
            if a.archive_root:
                receipt=a.archive_root/x['artifact_path'];need(sha(receipt)==x['sha256'],'Actual original host receipt')
                load('readonly_flash_host',project/'experiments/tsl9-v4160-flash-native/verify_host.py').replay(project,receipt)
        else:
            c=v['checks'];b=c['independent_normal_contract'];need(c['allocated_function_bytes']==256 and c['original_function_bytes']==262 and c['unowned_original_program_tail_bytes']==6,'Only six bounded component extents')
            need({k:z['bytes'] for k,z in c['functions'].items()}=={'quarter':64,'status':8,'unlock':30,'lock':14,'erase':46,'program':94},'Actual per-function native sizes')
            need(sum(z['instructions'] for z in c['functions'].values())==98,'Full compiled instruction coverage')
            need(len(v['artifacts'])==41 and c['native_dependencies']['rules']==6,'Actual native artifact/dependency inventory')
            need(b['all_six_normal_boundaries_admitted'] and len(b['raw_machine_negatives'])==15 and len(b['IR_transcript_negatives'])==3,'Normal boundary and explicit raw/IR controls')
            need(all(not c[k] for k in ('original_frame_prefix_equivalence','pointwise_async_equivalence','nonreturn_physical_GPR_prefix_equivalence','full_image_integration','firmware_BIN_produced','OTA_ready')),'Required unproved boundaries remain false')
            native_controls+=15
            if a.archive_root:
                receipt=a.archive_root/x['artifact_path'];need(sha(receipt)==x['sha256'],'Actual original native receipt')
                runner=load('readonly_flash_native',root.parent/'implementation/verify_native.py')
                runner.replay(project,receipt,runner.context(project,a.firmware))
    need(all(v=={'c','cpp'} for v in modes.values()),'Independent effect, canonical host and native C/C++ evidence')
    if (root/'seal.json').is_file():
        for x in read(root/'seal.json')['members']:
            target=(root/x['path']).resolve(strict=True);target.relative_to(root)
            need(sha(target)==x['sha256'] and target.stat().st_size==x['bytes'],'Review sealed member')
    print(json.dumps({'passed':True,'raw_source_and20controls_rechecked':raw_checked,'cross_version_raw_rechecked':cross_checked,'actual_archived_artifacts_replayed':bool(a.archive_root),'host_compiled_behavior_controls':host_controls,'native_raw_controls':native_controls,'native_IR_transcript_controls':6,'native_component_bytes':256,'new_firmware_BIN':False,'full_image_integration':False,'target_execution':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
