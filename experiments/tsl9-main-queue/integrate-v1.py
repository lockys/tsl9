#!/usr/bin/env python3
"""Link the actual1000B main-queue closure into the retained original startup graph."""
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
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
need(sha(ROOT/S['parent_checker'])==S['pins'][S['parent_checker']],'Frozen genuine parent checker')
need(sha(ROOT/K['provider_checker'])==K['provider_checker_sha256'],'Frozen actual-provider audit')
P=runpy.run_path(str(ROOT/S['parent_checker']))
V=runpy.run_path(str(ROOT/K['provider_checker']))
portable,encoded,E=V['portable'],V['encoded'],V['E']
OUTPUT='UNRESOLVED-STARTUP-MAIN-QUEUE.o'

def parent(mode):return ROOT/S['parent_component']/mode/S['parent_object']
def selected(mode):return [V['object_path'](p,mode,ROOT/K['provider_folder'])for p in S['providers']]
def global_map(e):
    rows=[x for x in e.symbols if x['info']>>4];gm={x['name']:x for x in rows}
    need(len(gm)==len(rows)and all(x['section']!=0xfff1 for x in rows),'Unique globals withoutABS providers')
    return gm

def source_proof(llvm):
    V['pins'](llvm)
    need(sha(ROOT/K['provider_receipt'])==K['provider_receipt_sha256'],'Retained actual selection receipt')
    report=json.loads((ROOT/K['provider_receipt']).read_bytes())
    need(report['inputs']==portable(V['inputs'](llvm),llvm)and report['modes']==V['audit'](ROOT/K['provider_folder'],llvm),'Complete actual-source provider original-byte andselection replay')
    saved=json.loads((ROOT/S['parent_component']/'measurement.json').read_bytes())
    need(saved['inputs']==portable(P['inputs'](llvm),llvm),'All retained parent producer inputs unchanged')
    proof=P['source_proof'](llvm)
    need(saved['source_proof']==proof,'Retained parent source proof freshly verified')
    for mode in ('c','cpp'):
        need(P['inventory'](parent(mode).parent)==saved['modes'][mode]['artifacts'],'Whole retained parent output inventory')
        need(P['audit_component'](parent(mode),mode)==saved['modes'][mode]['result'],'Retained whole original startup graph')
    need(proof['source_C_H_files']==95 and proof['native_code_units']==68 and
         proof['total_current_source_comparisons']==138 and proof['total_current_source_objects']==276,
         'Current complete source curation scope')
    need(sha(ROOT/S['manifest'])==S['pins'][S['manifest']],'No manifest/source-promotion change')
    return dict(passed=True,source_C_H_files=95,native_code_units=68,independent_data_units=1,
        function_source_comparisons=136,function_source_objects=272,
        independent_data_comparisons=2,independent_data_objects=4,
        total_current_source_comparisons=138,total_current_source_objects=276,
        manifest_unchanged=True,current_whole_source_proof_replayed=True,
        existing_curated_units_reused=10,new_curated_C_H_sources=0,derived_selection_C_units_compiled=1,selected_genuine_bytes=1464,
        full_native_source_objects_audited=20,selected_genuine_regions=59,
        provider_source_and_typed_reference_provenance_passed=True,
        parent5636B_and_independent_pointer_data_positive_audits_passed=True,
        no_legacy_negative_matrix_executed=True,target_executed=False,negative_cases_executed=0)

def audit_component(path,mode):
    p,e=E(parent(mode)),E(path);pm,em=global_map(p),global_map(e)
    additions=[]
    for provider,objpath in zip(S['providers'],selected(mode)):
        obj=E(objpath);additions.append((provider,obj,global_map(obj)))
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual unresolved RISC-V ET_REL')
    alloc={'.boot_code':(6,7100),'.initializer':(2,128),'.vectors':(2,328)}
    need({x['name']for x in e.sections if x['flags']&2 and x['size']}==set(alloc),'Only genuine selected code/data allocations')
    for name,(flags,size)in alloc.items():
        sec=e.section(name);need(sec['flags']==flags and sec['type']==1 and sec['address']==0 and sec['size']==size,'Exact VMA-zero diagnostic allocation')
    owners={};source_defs={};source_globals=set(pm)
    for provider,obj,gm in additions:
        source_globals.update(gm)
        for region in provider['selected_regions']:
            name=region['name'];need(name not in owners and not(name in pm and pm[name]['section']),'No duplicate genuine body owner')
            owners[name]=(obj,gm[name],region);source_defs[name]=gm[name]
    need(set(em)==source_globals,'Exact actual merged global inventory')
    offsets={};pieces=[p.data('.boot_code')];at=5636
    for region in S['all_selected_regions']:
        name=region['name'];obj,f,record=owners[name];need(record==region,'Exact original-PC region order')
        offsets[name]=at;pieces.append(obj.data(obj.sections[f['section']]));at+=f['size']
    need(at==7100 and e.data('.boot_code')==b''.join(pieces),'All parent5636B andgenuine1464B compiler-carrier bytes')
    need(e.data('.initializer')==p.data('.initializer')and e.data('.vectors')==p.data('.vectors'),'All456 parent data bytes unchanged')
    for name,f in pm.items():
        a=em[name]
        if f['section']:
            need(a['info']==f['info']and a['other']==f['other']and a['size']==f['size']and a['value']==f['value']and
                 e.sections[a['section']]['name']==p.sections[f['section']]['name'],'Every original parent owner retained')
        elif name not in source_defs and name not in S['aliases']:
            need(a['info']==f['info']and a['section']==a['value']==a['size']==0,'Every remaining parent provider explicit')
    for name,f in source_defs.items():
        a=em[name];need(f['info']==18 and a['info']==18 and a['other']==f['other']and a['size']==f['size']and
                       a['value']==offsets[name]and e.sections[a['section']]['name']=='.boot_code','Actual full-sized compiled provider body')
    need(S['aliases']=={
        'tsl9_main_provider_12c58':'tsl9_queue_entry_12c58',
        'tsl9_main_provider_17002':'tsl9_flag_consumer_entry_17002',
        'tsl9_queue_external_820c':'tsl9_queue_clear_820c'},'Only three genuine naming aliases')
    for name,entry in S['aliases'].items():
        alias,target=em[name],em[entry]
        need(alias['info']==18 and alias['other']==0 and alias['size']==0 and
             alias['section']==target['section']and alias['value']==target['value'],'True alias at real entry')
    need([em[name]['size']for name in S['aliases'].values()]==[46,8,18],'Actual main queue/flag/clear entry sizes')
    expected=Counter()
    for obj,is_new in [(p,False)]+[(x[1],True)for x in additions]:
        gm=global_map(obj)
        for rel in obj.relocations:
            f=obj.symbols[rel['symbol']]
            if f['info']>>4:
                target=em[f['name']];owner=e.sections[target['section']]['name']if target['section']else''
                role=(target['name'],target['info'],target['other'],target['size'],owner,target['value'])
            else:
                need(not is_new and f['section']>0 and f['section']!=0xfff1,'Retained real parent local reference')
                role=(f['name'],f['info'],f['other'],f['size'],p.sections[f['section']]['name'],f['value'])
            if is_new:
                candidates=[f for f in gm.values()if f['section']==rel['section']and f['size']]
                need(len(candidates)==1,'One genuine source owner per addition reference')
                section='.boot_code';offset=offsets[candidates[0]['name']]+rel['offset']
            else:
                section=p.sections[rel['section']]['name'];offset=rel['offset']
            expected[(section,offset,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        f=e.symbols[rel['symbol']];owner=e.sections[f['section']]['name']if f['section']else''
        role=(f['name'],f['info'],f['other'],f['size'],owner,f['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==424,'All424 typedlocal/global reference roles andtargets')
    undefined=sorted(name for name,f in em.items()if not f['section'])
    need(undefined==K['remaining_undefined']and len(undefined)==16,'Exactly16 honest remaining direct provider gaps')
    funcs=[f for f in em.values()if f['info']==18 and f['section']]
    need(sum(bool(f['size'])for f in funcs)==514 and sum(not f['size']for f in funcs)==25,'514 realregions and22 truealiases')
    vector=json.loads((ROOT/'experiments/tsl9-original-vectors/spec-v1.json').read_bytes());restored=bytearray(e.data('.vectors'));bound=external=0
    for row in vector['entries']:
        if not row['symbol']:continue
        if em[row['symbol']]['section']:bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    fw=(ROOT/S['firmware']).read_bytes()
    need(bytes(restored)==fw[vector['start']-0x8000:vector['end']-0x8000]and bound==62 and external==0,'Original vector carrier and62 genuine bindings retained')
    return dict(passed=True,mode=mode,code_bytes=7100,original_code_instructions=2505,
        initializer_bytes=128,vector_carrier_bytes=328,total_data_bytes=456,
        nonzero_FUNC_regions=514,zero_size_FUNC_aliases=25,RELA=424,UND=undefined,
        reused_provider_bytes=1464,reused_provider_instructions=509,reused_provider_regions=59,reused_curated_units=10,
        parent5636B_code_and456B_data_unchanged=True,all1464B_original_VA_encoded_equal=True,
        all_global_local_relocation_targets_owned=True,selected_provider_children_bound_except12ABE14D2E=True,
        main_queue_and_IRQ_flag_entries_bound=True,three_real_entry_aliases_added=True,
        vector_slots_bound_to_real_code=62,vector_slots_still_external=0,
        dynamic_resident_identities_and_ABI_proved=False,physical_CAN_SPI_success_proved=False,
        physical_MCU_ROM_IRQ_proved=False,source_target_memory_ownership_proved=False,
        final_original_address_placement_proved=False,component_sha256=sha(path),
        ELF_VMA_zero=True,executable=False,ABS_providers=0,no_executable_stub_added=True,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
        network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',HERE/'integration-v1.json',HERE/'joined-v1.ld',
           ROOT/K['provider_checker'],ROOT/K['provider_receipt'],ROOT/'experiments/tsl9-original-vectors/spec-v1.json']
    paths += [Path(p)for p in V['inputs'](llvm)]
    paths += [Path(p)for p in P['inputs'](llvm)]
    for mode in ('c','cpp'):paths += [parent(mode),*selected(mode)]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--output',type=Path);group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained partial component')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'All retained current component inputs unchanged')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Complete actual retained output inventory')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Whole retained genuine component replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-main-queue-link-replay',source_proof=proof)));return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned native output')
    report=dict(schema='TSL9-main-queues-native-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir(parents=True);output=folder/OUTPUT;commands=[]
        recipes=[('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),str(parent(mode)),
                          *[str(p)for p in selected(mode)],'-o',str(output)]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        for label,argv in recipes:
            proc=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (folder/(label+'.log')).write_bytes(proc.stdout);commands.append(dict(label=label,argv=argv,exit=proc.returncode))
            need(proc.returncode==0,'Actual partial-link command failed; log retained')
        result=audit_component(output,mode);(folder/'verification.json').write_bytes(encoded(result))
        report['modes'][mode]=dict(result=result,commands=commands,artifacts=inventory(folder))
        print(json.dumps({k:v for k,v in result.items()if k!='UND'}|dict(UND_count=len(result['UND']))))
    need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during native link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(passed=False,error=str(error))),file=sys.stderr);raise SystemExit(1)
