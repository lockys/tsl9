#!/usr/bin/env python3
"""Bind genuine record-decode providers C/C++ regions; inspect normal native artifacts only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes())
K=json.loads((HERE/'integration-v1.json').read_bytes())
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(ROOT/K['parent_checker'])==K['parent_checker_sha256'],'Frozen genuine parent checker')
P=runpy.run_path(str(ROOT/K['parent_checker']))
N=runpy.run_path(str(HERE/'build-v1.py'))
portable,encoded=N['portable'],N['encoded']
OUTPUT='UNRESOLVED-STARTUP-RECORD-DECODE.o'
def parent(mode):return ROOT/K['parent_component']/mode/K['parent_object']
def native(mode):return (ROOT/K['curation']).parent/'record-decode'/mode/'curated/unit.o'
def elf(path):return N['elf'](path)
def expand(value,llvm):
    for name,path in [('CLANG_RESOURCE',llvm.parent/'lib/clang/18'),('LLVM_BIN',llvm),('PROJECT_ROOT',ROOT)]:
        value=value.replace('$'+'{'+name+'}',str(path))
    return Path(value)
def inputs(llvm):
    paths=[Path(__file__),HERE/'integration-v1.json',HERE/'joined-v1.ld',HERE/'spec-v1.json',
           HERE/'build-v1.py',ROOT/K['parent_checker'],ROOT/K['parent_manifest_deriver'],
           ROOT/K['parent_component']/'measurement.json',ROOT/'src/source-manifest.json',
           ROOT/K['curation'],ROOT/K['previous_curation'],ROOT/K['standalone_receipt'],
           ROOT/K['data_builder'],ROOT/K['data_receipt'],ROOT/K['vector_spec'],
           ROOT/S['source'],ROOT/S['curated_source'],ROOT/S['firmware'],ROOT/S['reader'],
           ROOT/S['curation_checker'],ROOT/S['source_deriver'],llvm.parent/'lib/clang/18/include/stdint.h']
    for mode in('c','cpp'):
        paths += [parent(mode),parent(mode).parent/'verification.json',native(mode),
                  (ROOT/K['standalone_receipt']).parent/mode/'unit.o']
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def audit_positive_ancestors(mode):
    P['audit_positive_ancestors'](mode)
    old=P['parent'](mode)
    need(P['P']['audit_component'](old,mode)==json.loads((old.parent/'verification.json').read_bytes()),
         'Complete retained genuine LLE component audit')

def source_proof(llvm):
    for key in('source','firmware','reader','curation_checker','reference_candidate','source_deriver'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    need(sha(ROOT/S['curated_source'])==S['source_sha256'],'Exact curated context source')
    for key in('parent_checker','parent_manifest_deriver','curation','previous_curation',
               'standalone_receipt','data_builder','data_receipt'):
        need(sha(ROOT/K[key])==K[key+'_sha256'],'Pinned '+key)
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned local '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/'src/source-manifest.json')==K['current_manifest_sha256'],'Exact current95-file manifest')
    raw=runpy.run_path(str(ROOT/K['parent_manifest_deriver']))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==K['previous_manifest_sha256'],'Exact retained94-file parent bytes')
    value=json.loads(raw)
    value['files'].append(K['new_file_entry'])
    value['native_units'].append(K['new_unit_entry'])
    need(value==json.loads((ROOT/'src/source-manifest.json').read_bytes()),'Only exact one-source/one-unit extension')
    previous=json.loads((ROOT/K['previous_curation']).read_bytes())
    current=json.loads((ROOT/K['curation']).read_bytes())
    need(len(previous['results'])==134 and len(current['results'])==136 and
         current['results'][:134]==previous['results'],'All prior134 code comparisons unchanged')
    need(len(previous['artifacts'])==805 and len(current['artifacts'])==817 and
         all(current['artifacts'].get(k)==v for k,v in previous['artifacts'].items()),
         'All prior805 code artifact records unchanged')
    p=subprocess.run([sys.executable,'-B',str(ROOT/S['curation_checker']),'--replay',str(ROOT/K['curation'])],
                     cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    need(p.returncode==0,'Actual current whole code-source replay')
    replay=json.loads(p.stdout)
    need(replay['passed']and replay['comparisons']==136,'All136 current code comparisons')
    data=json.loads((ROOT/K['data_receipt']).read_bytes())
    D=runpy.run_path(str(ROOT/K['data_builder']))
    need(data['variants']==['origin','curated']and
         data['inputs']==portable(D['inputs'](llvm,data['variants']),llvm),'Independent data inputs unchanged')
    standalone=json.loads((ROOT/K['standalone_receipt']).read_bytes())
    need(standalone['inputs']==portable(N['inputs'](llvm),llvm),'All standalone compiler inputs unchanged')
    record_path=ROOT/K['parent_component']/'measurement.json'
    need(sha(record_path)==K['parent_receipt_sha256'],'Frozen actual parent build receipt')
    record=json.loads(record_path.read_bytes())
    for key,pin in record['inputs'].items():
        path=expand(key,llvm)
        if path==ROOT/'src/source-manifest.json':
            need(pin['sha256']==K['previous_manifest_sha256']and pin['bytes']==len(raw),'Only exact proven manifest extension')
        else:
            need(path.is_file()and path.stat().st_size==pin['bytes']and sha(path)==pin['sha256'],
                 'Every other recorded parent producer input unchanged')
    for mode in('c','cpp'):
        need(sha(parent(mode))==K['parent_object_sha256'],'Actual genuine parent component')
        need(P['inventory'](parent(mode).parent)==record['modes'][mode]['artifacts'],'Complete parent output inventory')
        need(P['audit_component'](parent(mode),mode)==record['modes'][mode]['result'],'Whole retained parent normal-artifact audit')
        audit_positive_ancestors(mode)
        for variant in('origin','curated'):
            folder=(ROOT/K['data_receipt']).parent/mode/variant;job=data['modes'][mode][variant]
            need(job['artifacts']==D['inventory'](folder)and job['result']==D['audit_object'](folder/'unit.o'),
                 'Complete actual pointer-data audit')
            need(job['dependencies']==portable(D['dependencies'](folder,variant,llvm),llvm),'Every pointer-data dependency')
        need(D['complete_projection_equal']((ROOT/K['data_receipt']).parent/mode/'origin/unit.o',
                                           (ROOT/K['data_receipt']).parent/mode/'curated/unit.o'),
             'Independent pointer-data source projection equality')
        original=(ROOT/K['standalone_receipt']).parent/mode/'unit.o'
        need(sha(original)==K['standalone_native_object_sha256']and
             N['audit_object'](original)==standalone['modes'][mode]['result'],'Actual original212B77i native audit')
        need(sha(native(mode))==K['curated_native_object_sha256']and
             N['audit_object'](native(mode))==dict(standalone['modes'][mode]['result'],
                 native_object_sha256=K['curated_native_object_sha256']),'Actual curated212B77i native identity')
    return dict(passed=True,source_C_H_files=95,native_code_units=68,independent_data_units=1,
                function_source_comparisons=136,function_source_objects=272,
                independent_data_comparisons=2,independent_data_objects=4,
                total_current_source_comparisons=138,total_current_source_objects=276,
                prior134_results_and805_artifact_records_unchanged=True,
                exact_one_source_unit_manifest_extension=True,all_other_recorded_parent_inputs_unchanged=True,
                retained_positive_ancestor_code_and_data_audits_passed=True,
                old_parent_whole_manifest_replay_claimed=False,
                standalone_and_curated212B_original_VA_encoded_equal=True,
                historical_negative_matrices_executed=False,target_executed=False,negative_cases_executed=0)

def global_map(e):
    rows=[s for s in e.symbols if s['info']>>4]
    need(len({s['name']for s in rows})==len(rows),'Unique genuine global symbols')
    need(all(s['section']!=0xfff1 for s in rows),'No ABS provider substitutes')
    return {s['name']:s for s in rows}

def audit_component(path,mode):
    p,n,e=(elf(x)for x in(parent(mode),native(mode),path))
    pm,nm,em=(global_map(x)for x in(p,n,e))
    defs={name:s for name,s in nm.items()if s['section']}
    need(len(defs)==17,'Seventeen real decoder/setter architectural regions')
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual unresolved RISC-V ET_REL')
    alloc={'.boot_code':(6,4636),'.initializer':(2,128),'.vectors':(2,328)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(alloc),'Only genuine code/data allocations')
    for name,(flags,size)in alloc.items():
        sec=e.section(name)
        need(sec['flags']==flags and sec['type']==1 and sec['size']==size and sec['address']==0,'Exact diagnostic allocation')
    offsets={};pieces=[p.data('.boot_code')];at=4424
    for region in S['regions']:
        f=nm[region['name']];offsets[f['name']]=at
        pieces.append(n.data(n.sections[f['section']]));at+=region['bytes']
    need(at==4636 and e.data('.boot_code')==b''.join(pieces),'All parent4424B plusgenuine212B native source bytes')
    need(e.data('.initializer')==p.data('.initializer')and e.data('.vectors')==p.data('.vectors'),'All456 parent data bytes unchanged')
    need(set(em)==set(pm)|set(nm),'Exact actual merged global inventory')
    for name,s in pm.items():
        actual=em[name]
        if s['section']:
            need(actual['info']==s['info']and actual['other']==s['other']and actual['size']==s['size']and actual['value']==s['value']and e.sections[actual['section']]['name']==p.sections[s['section']]['name'],'Exact retained parent owner')
        elif name not in K['aliases']:
            need(actual['section']==0 and actual['info']==s['info']and actual['value']==actual['size']==0,'Every other parent gap retained')
    for name,s in defs.items():
        actual=em[name]
        need(s['info']==18 and actual['info']==18 and actual['other']==s['other']and actual['size']==s['size']and actual['value']==offsets[name]and e.sections[actual['section']]['name']=='.boot_code','Each full-size realnew region')
    need(K['aliases']=={
        'tsl9_record_consumer_provider_c6a8':'tsl9_record_decode_entry_c6a8',
        'tsl9_record_consumer_provider_faf8':'tsl9_record_decode_entry_faf8',
        'tsl9_record_decode_provider_12a08':'tsl9_queue_external_12a08'},'Exactly three genuine entry bindings')
    for alias,name in K['aliases'].items():
        actual,target=em[alias],em[name]
        need(actual['info']==18 and actual['other']==0 and actual['size']==0 and actual['section']==target['section']and actual['value']==target['value'],'True alias at actual full-sized body')
    need([em[name]['size']for name in K['aliases'].values()]==[12,6,12],'Genuine decoder,setter andexisting dispatcher entry sizes')
    need(N['audit_object'](native(mode))['complete_original_VA_encoded_bytes_equal'],'All212B original-VA native source proof')
    expected=Counter()
    for obj,is_new in[(p,False),(n,True)]:
        gm=global_map(obj)
        for rel in obj.relocations:
            s=obj.symbols[rel['symbol']]
            if s['info']>>4:
                target=em[s['name']];owner=e.sections[target['section']]['name']if target['section']else''
                role=(target['name'],target['info'],target['other'],target['size'],owner,target['value'])
            else:
                need(not is_new and s['section']>0 and s['section']!=0xfff1,'Retained real parent local reference')
                role=(s['name'],s['info'],s['other'],s['size'],p.sections[s['section']]['name'],s['value'])
            if is_new:
                owner_name=next(f['name']for f in gm.values()if f['section']==rel['section'])
                section='.boot_code';offset=offsets[owner_name]+rel['offset']
            else:
                section=p.sections[rel['section']]['name'];offset=rel['offset']
            expected[(section,offset,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        s=e.symbols[rel['symbol']];owner=e.sections[s['section']]['name']if s['section']else''
        role=(s['name'],s['info'],s['other'],s['size'],owner,s['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==309,'All309 typed local/global reference roles')
    vector=json.loads((ROOT/K['vector_spec']).read_bytes());restored=bytearray(e.data('.vectors'));bound=external=0
    for row in vector['entries']:
        if not row['symbol']:continue
        if em[row['symbol']]['section']:bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    fw=(ROOT/S['firmware']).read_bytes()
    need(bytes(restored)==fw[vector['start']-0x8000:vector['end']-0x8000]and bound==62 and external==0,'Original vector carrier and62 genuine bindings')
    undefined=sorted(name for name,s in em.items()if not s['section'])
    need(undefined==K['remaining_undefined']and len(undefined)==20,'Exactly20 honest direct provider gaps')
    funcs=[s for s in em.values()if s['info']==18 and s['section']]
    need(sum(bool(s['size'])for s in funcs)==388 and sum(not s['size']for s in funcs)==21,'388 realregions and21 genuine aliases')
    return dict(passed=True,mode=mode,code_bytes=4636,original_code_instructions=1647,
        initializer_bytes=128,vector_carrier_bytes=328,total_data_bytes=456,
        nonzero_FUNC_regions=388,zero_size_FUNC_aliases=21,RELA=309,UND=undefined,
        new_record_decode_bytes=212,new_record_decode_instructions=77,new_record_decode_regions=17,
        parent4424B_code_and456B_data_unchanged=True,all212B_additions_original_VA_encoded_equal=True,
        all_global_local_relocation_targets_owned=True,three_real_entry_aliases_added=True,
        C6A8_and_FAF8_bound_to_real_bodies=True,existing12A08_dispatch_reused=True,
        vector_slots_bound_to_real_code=62,vector_slots_still_external=0,
        dynamic_provider_identities_and_ABI_proved=False,source_target_memory_ownership_proved=False,
        record_field_physical_semantics_proved=False,physical_MCU_ROM_IRQ_proved=False,
        final_original_address_placement_proved=False,component_sha256=sha(path),
        ELF_VMA_zero=True,executable=False,ABS_providers=0,no_executable_stub_added=True,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
        network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--output',type=Path);group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'Every retained actual producer input unchanged')
        for mode in('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Complete retained output inventory')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Whole actual context component replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-record-decode-link-replay',source_proof=proof)));return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned output')
    report=dict(schema='TSL9-record-decode-native-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[];output=f/OUTPUT
        recipes=[('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),
                          str(parent(mode)),str(native(mode)),'-o',str(output)]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout);commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        audit=audit_component(output,mode);(f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode]=dict(result=audit,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in audit.items()if k!='UND'}|dict(UND_count=len(audit['UND']))))
    need(before==portable(inputs(llvm),llvm),'Every actual input unchanged during normal link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
if __name__=='__main__':
    try:main()
    except(ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in[(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
