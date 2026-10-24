#!/usr/bin/env python3
"""Bind actual vector data to the genuine startup component; no target execution."""
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
V=runpy.run_path(str(HERE/'build-v1.py'))
need,sha,encoded,portable=(V[n]for n in('need','sha','encoded','portable'))
OUTPUT='UNRESOLVED-STARTUP-VECTORS.o'

def parent(mode):
    return ROOT/K['previous_component']/mode/K['previous_object_name']

def vector(mode):
    return (ROOT/K['data_receipt']).parent/mode/'curated/unit.o'

def expand(text,llvm):
    for name,path in [('CLANG_RESOURCE',llvm.parent/'lib/clang/18'),('LLVM_BIN',llvm),('PROJECT_ROOT',ROOT)]:
        text=text.replace('$'+'{'+name+'}',str(path))
    return Path(text)

def inputs(llvm):
    paths=[Path(__file__),HERE/'integration-v1.json',HERE/'joined-v1.ld',HERE/'spec-v1.json',
           ROOT/K['data_builder'],ROOT/K['data_receipt'],ROOT/K['curation'],
           ROOT/K['previous_curation'],ROOT/K['parent_checker'],ROOT/K['parent_manifest_deriver'],
           ROOT/K['previous_component']/'measurement.json',ROOT/'src/source-manifest.json',
           ROOT/S['firmware'],ROOT/S['reader'],ROOT/S['curation_checker'],
           ROOT/S['source'],ROOT/S['curated_source'],llvm.parent/'lib/clang/18/include/stdint.h']
    for mode in ('c','cpp'):
        paths += [parent(mode),parent(mode).parent/'verification.json',vector(mode),
                  vector(mode).parent/'unit.d',vector(mode).parent/'compile.log']
    paths += [llvm/n for n in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def source_proof(llvm):
    for key in ('firmware','reader','curation_checker'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for key in ('curation','previous_curation','data_receipt','data_builder','parent_checker','parent_manifest_deriver'):
        need(sha(ROOT/K[key])==K[key+'_sha256'],'Pinned '+key)
    for name,pin in S['tools'].items():
        need(sha(llvm/name)==pin,'Pinned native tool '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned header')
    need(sha(ROOT/'src/source-manifest.json')==K['current_manifest_sha256'],'Exact current80-file manifest')
    raw=runpy.run_path(str(ROOT/K['parent_manifest_deriver']))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==K['previous_manifest_sha256'],'Exact79-file parent bytes')
    previous_manifest=json.loads(raw)
    previous_manifest['files'].append(K['new_file_entry'])
    previous_manifest['native_data_units']=[K['new_data_unit']]
    current_manifest=json.loads((ROOT/'src/source-manifest.json').read_bytes())
    need(previous_manifest==current_manifest,'Only one source and explicit independent data-unit registration')
    previous=json.loads((ROOT/K['previous_curation']).read_bytes())
    current=json.loads((ROOT/K['curation']).read_bytes())
    need(len(current['results'])==106 and current['results']==previous['results'],'All106 prior code comparison facts unchanged')
    need(len(current['artifacts'])==637 and current['artifacts']==previous['artifacts'],'All637 prior code artifact records unchanged')
    p=subprocess.run([sys.executable,'-B',str(ROOT/S['curation_checker']),'--replay',str(ROOT/K['curation'])],
                     cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    need(p.returncode==0,'Actual current full frozen code-verifier replay')
    replay=json.loads(p.stdout)
    need(replay['passed']and replay['comparisons']==106,'All106 current code comparisons')
    data=json.loads((ROOT/K['data_receipt']).read_bytes())
    need(data['variants']==['origin','curated']and data['inputs']==portable(V['inputs'](llvm,data['variants']),llvm),
         'Exact independent C/C++ source/data compiler provenance')
    parent_record=ROOT/K['previous_component']/'measurement.json'
    need(sha(parent_record)==K['parent_receipt_sha256'],'Pinned genuine parent measurement')
    record=json.loads(parent_record.read_bytes())
    for key,pin in record['inputs'].items():
        path=expand(key,llvm)
        if path==ROOT/'src/source-manifest.json':
            need(pin['sha256']==K['previous_manifest_sha256']and pin['bytes']==len(raw),'Only proven manifest extension')
        else:
            need(path.is_file()and path.stat().st_size==pin['bytes']and sha(path)==pin['sha256'],
                 'Every other parent producer input unchanged')
    P=runpy.run_path(str(ROOT/K['parent_checker']))
    for mode in ('c','cpp'):
        need(sha(parent(mode))==K['previous_object_sha256'],'Pinned actual parent ET_REL')
        need(P['inventory'](parent(mode).parent)==record['modes'][mode]['artifacts'],'Complete parent output inventory unchanged')
        need(P['audit_component'](parent(mode),mode)==record['modes'][mode]['result'],'Complete genuine parent component proof')
        need(P['audit_selected'](parent(mode).parent/'initializer-only.o',mode)==record['modes'][mode]['selected_data'],
             'Actual128B C initializer remains original-equal')
        for variant in ('origin','curated'):
            folder=(ROOT/K['data_receipt']).parent/mode/variant
            job=data['modes'][mode][variant]
            need(job['artifacts']==V['inventory'](folder),'Complete actual vector output inventory')
            need(job['result']==V['audit_object'](folder/'unit.o'),'Complete original328B pointer-data audit')
            need(job['dependencies']==portable(V['dependencies'](folder,variant,llvm),llvm),'Every actual pointer-data dependency')
        need(V['complete_projection_equal']((ROOT/K['data_receipt']).parent/mode/'origin/unit.o',vector(mode)),
             'Independent source organization complete projection equality')
        need(sha(vector(mode))==K['curated_object_sha256'],'Pinned curated vector object')
    return dict(passed=True,source_C_H_files=80,native_code_units=53,independent_native_data_units=1,
                frozen_code_comparisons=106,frozen_code_objects=212,independent_data_comparisons=2,
                independent_data_objects=4,total_current_source_comparisons=108,
                total_current_source_objects=216,prior106_results_and637_artifact_records_unchanged=True,
                parent_manifest_extension_exact=True,
                old_parent_whole_manifest_replay_claimed=False,
                old_frozen_code_checker_modified=False,fake_FUNC_added_to_admit_data=False,
                target_executed=False,negative_cases_executed=0)

def globals_by_name(e):
    rows=[s for s in e.symbols if s['info']>>4]
    need(len({s['name']for s in rows})==len(rows),'Unique global symbols')
    need(all(s['section']!=0xfff1 for s in rows),'No ABS provider substitutes')
    return {s['name']:s for s in rows}

def audit_component(path,mode):
    p,v,e=V['elf'](parent(mode)),V['elf'](vector(mode)),V['elf'](path)
    pm,vm,em=(globals_by_name(x)for x in(p,v,e))
    need(e.header[0]==1 and not e.program_headers,'Unresolved ET_REL without loading headers')
    allowed={'.boot_code':(6,572),'.initializer':(2,128),'.vectors':(2,328)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(allowed),'Exactly genuine code/initializer/vector allocations')
    for name,(flags,size)in allowed.items():
        sec=e.section(name)
        need(sec['flags']==flags and sec['type']==1 and sec['size']==size and sec['address']==0,'Exact allocation and no final VMA '+name)
    need(e.data('.boot_code')==p.data('.boot_code')and e.data('.initializer')==p.data('.initializer'),
         'Entire572B code and128B initializer unchanged')
    need(e.data('.vectors')==v.data(S['section']),'Entire actual compiled328B pointer-data carrier unchanged')
    need(set(em)==set(pm)|set(vm),'Complete genuine merged symbol inventory')
    for name,actual in em.items():
        owners=[(original,symbol)for original,symbol in((p,pm.get(name)),(v,vm.get(name)))
                if symbol and symbol['section']]
        if owners:
            need(len(owners)==1,'Exactly one genuine definition')
            original,symbol=owners[0]
            old_owner=original.sections[symbol['section']]['name']
            target='.vectors'if original is v else old_owner
            need(actual['info']==symbol['info']and actual['other']==symbol['other']and
                 actual['size']==symbol['size']and actual['value']==symbol['value']and
                 e.sections[actual['section']]['name']==target,'Exact code/data definition owner '+name)
        else:
            need(actual['section']==0 and actual['info']in(16,18)and
                 actual['value']==0 and actual['size']==0,'Explicit outstanding code provider '+name)
    expected=Counter()
    for original,is_vector in((p,False),(v,True)):
        for rel in original.relocations:
            symbol=original.symbols[rel['symbol']]
            owner='.vectors'if is_vector else original.sections[rel['section']]['name']
            if symbol['info']>>4:
                target=em[symbol['name']]
                target_owner=e.sections[target['section']]['name']if target['section']else''
                role=(target['name'],target['info'],target['other'],target['size'],target_owner,target['value'])
            else:
                need(not is_vector and symbol['section']>0 and symbol['section']!=0xfff1,'Genuine local parent HI-label owner')
                role=(symbol['name'],symbol['info'],symbol['other'],symbol['size'],
                      original.sections[symbol['section']]['name'],symbol['value'])
            expected[(owner,rel['offset'],rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        symbol=e.symbols[rel['symbol']]
        owner=e.sections[symbol['section']]['name']if symbol['section']else''
        role=(symbol['name'],symbol['info'],symbol['other'],symbol['size'],owner,symbol['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==144,'All144 typed references and exact global/local symbol roles')
    data_symbol=em[S['symbol']]
    need(data_symbol['info']==17 and data_symbol['size']==328 and data_symbol['value']==0 and
         e.sections[data_symbol['section']]['name']=='.vectors','Original reset literal bound to genuine328B C OBJECT')
    bound=0;external=0;restored=bytearray(e.data('.vectors'))
    for row in S['entries']:
        if not row['symbol']:continue
        symbol=em[row['symbol']]
        if symbol['section']:
            need(symbol['info']==18 and e.sections[symbol['section']]['name']=='.boot_code',
                 'Known slot binds actual original compiled code')
            bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    original=(ROOT/S['firmware']).read_bytes()[S['start']-0x8000:S['end']-0x8000]
    need(bytes(restored)==original and bound==55 and external==7,'All original vector words and55 real code references')
    undefined=sorted(name for name,s in em.items()if s['section']==0)
    need(undefined==K['remaining_undefined'],'Exactly eight explicit outstanding code entries')
    return dict(passed=True,mode=mode,code_bytes=572,instructions=212,FUNC=99,
                initializer_bytes=128,vector_carrier_bytes=328,total_data_bytes=456,
                RELA=144,original_control_and_literal_RELA=82,vector_R_RISCV_32=62,
                vector_slots_bound_to_existing_code=55,vector_slots_still_external=7,
                vector_unique_external_entries=6,UND=undefined,
                vector_literal_bound_to_real_C_OBJECT=True,
                all_parent_code_initializer_bytes_unchanged=True,
                all_vector_carrier_bytes_unchanged=True,
                all_vector_words_original_equal_after_data_only_encoding=True,
                all_global_local_relocation_targets_owned=True,
                aliases_or_fake_handlers_added=False,ABS_providers=0,diagnostic_RAM_stack_excluded=True,
                component_sha256=sha(path),ELF_VMA_zero=True,executable=False,
                hardware_IRQ_count_or_complete_vector_extent_proved=False,
                vector_storage_proves_IRQ_ABI=False,installed_resident_known=False,
                target_executed=False,ISA_emulated=False,HOST_model_executed=False,
                hardware_accessed=False,network=False,negative_cases_executed=0,
                firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--output',type=Path)
    group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve()
        need(out.parent==HERE/'build','Owned retained normal output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'Every retained native producer input unchanged')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Complete retained linked artifact inventory')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Actual linked-component replay equality')
        print(json.dumps(dict(passed=True,mode='read-only-normal-vector-startup-replay',source_proof=proof)))
        return
    out=a.output.resolve()
    need(out.parent==HERE/'build'and not out.exists(),'Create-only direct child output')
    report=dict(schema='TSL9-original-vector-startup-native-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        output=f/OUTPUT
        recipes=[('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),
                          str(parent(mode)),str(vector(mode)),'-o',str(output)]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        audit=audit_component(output,mode)
        (f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode]=dict(result=audit,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in audit.items()if k!='UND'}|dict(UND_count=len(audit['UND']))))
    need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during normal partial link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in[(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
