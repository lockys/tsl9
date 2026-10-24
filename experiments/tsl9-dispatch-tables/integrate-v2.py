#!/usr/bin/env python3
"""Link the actual1000B dispatch-table closure into the retained original startup graph."""
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
K=json.loads((HERE/'integration-v2.json').read_bytes())
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
need(sha(ROOT/S['parent_checker'])==S['pins'][S['parent_checker']],'Frozen genuine parent checker')
need(sha(ROOT/K['provider_checker'])==K['provider_checker_sha256'],'Frozen actual-provider audit')
P=runpy.run_path(str(ROOT/S['parent_checker']))
V=runpy.run_path(str(ROOT/K['provider_checker']))
portable,encoded,E=V['portable'],V['encoded'],V['E']
OUTPUT='UNRESOLVED-STARTUP-DISPATCH-TABLES.o'

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
        existing_curated_units_reused=8,new_curated_C_H_sources=0,derived_selection_C_units_compiled=1,relative_table_bytes=60,selected_genuine_bytes=2736,
        full_native_source_objects_audited=16,selected_genuine_regions=269,
        provider_source_and_typed_reference_provenance_passed=True,
        parent7100B_and_independent_pointer_data_positive_audits_passed=True,
        no_legacy_negative_matrix_executed=True,target_executed=False,negative_cases_executed=0)

def audit_component(path,mode):
    p,e=E(parent(mode)),E(path);pm,em=global_map(p),global_map(e)
    additions=[(provider,E(objpath))for provider,objpath in zip(S['providers'],selected(mode))]
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual unresolved RISC-V ET_REL')
    alloc={'.boot_code':(6,9836),'.initializer':(2,128),'.vectors':(2,328),'.feature_tables':(2,60)}
    need({x['name']for x in e.sections if x['flags']&2 and x['size']}==set(alloc),'Only genuine code, parent data andtwo real tables')
    for name,(flags,size)in alloc.items():
        sec=e.section(name)
        need(sec['flags']==flags and sec['type']==1 and sec['address']==0 and sec['size']==size,'Exact diagnostic allocation')
    need(e.section('.feature_tables')['align']==4,'Actual table alignment')
    owners={};new_defs={};source_globals=set(pm)
    for provider,obj in additions:
        gm=global_map(obj);source_globals.update(gm)
        for region in V['selected_regions'](provider):
            name=region['name'];need(name not in owners and not(name in pm and pm[name]['section']),'No duplicate genuine code owner')
            owners[name]=(obj,gm[name],region);new_defs[name]=gm[name]
    need(set(em)==source_globals,'Exact actual merged code/data/provider inventory')
    offsets={};pieces=[p.data('.boot_code')];at=7100
    for region in S['all_selected_regions']:
        name=region['name'];obj,f,record=owners[name];need(record==region,'Exact original code-region ordering')
        offsets[name]=at;pieces.append(obj.data(obj.sections[f['section']]));at+=f['size']
    need(at==9836 and e.data('.boot_code')==b''.join(pieces),'Exact parent7100B plusgenuine2736B compiled carriers')
    need(e.data('.initializer')==p.data('.initializer')and e.data('.vectors')==p.data('.vectors'),'All456 parent data bytes unchanged')
    data_offsets={};table_pieces=[];at=0
    for table in S['tables']:
        matches=[(obj,global_map(obj)[table['name']])for provider,obj in additions
                 if table['name']in global_map(obj)and global_map(obj)[table['name']]['section']]
        need(len(matches)==1,'One genuine source OBJECT for each table')
        obj,f=matches[0];actual=em[table['name']]
        need(f['info']==actual['info']==17 and f['other']==actual['other']==0 and
             f['size']==actual['size']==table['bytes']and f['value']==0 and
             e.sections[actual['section']]['name']=='.feature_tables'and actual['value']==at,'Exact actual table OBJECT role/extent')
        data_offsets[table['name']]=at;table_pieces.append(obj.data(obj.sections[f['section']]));at+=f['size']
    need(at==60 and e.data('.feature_tables')==b''.join(table_pieces)==bytes(60),'Only true symbolic table carriers retained')
    for name,f in pm.items():
        actual=em[name]
        if f['section']:
            need(actual['info']==f['info']and actual['other']==f['other']and actual['size']==f['size']and actual['value']==f['value']and
                 e.sections[actual['section']]['name']==p.sections[f['section']]['name'],'Each retained parent code/data owner')
        elif name not in new_defs:
            need(actual['section']==actual['value']==actual['size']==0 and actual['info']==f['info'],'Every other parent provider gap retained')
    for name,f in new_defs.items():
        actual=em[name]
        need(f['info']==actual['info']==18 and actual['other']==f['other']and actual['size']==f['size']and actual['value']==offsets[name]and
             e.sections[actual['section']]['name']=='.boot_code','Each real full-size selected body')
    need(S['aliases']=={} and K['true_entry_aliases']=={
        'tsl9_feature_external_c6a8':'tsl9_record_decode_entry_c6a8'},'One real existing-entry alias only')
    alias,target=em['tsl9_feature_external_c6a8'],em['tsl9_record_decode_entry_c6a8']
    need(target['info']==18 and target['size']==12 and target['section']>0 and
         alias['info']==18 and alias['other']==0 and alias['size']==0 and
         alias['section']==target['section']and alias['value']==target['value'],'C6A8 alias binds genuine retained decoder entry')
    expected=Counter()
    for obj,is_new in[(p,False)]+[(x[1],True)for x in additions]:
        gm=global_map(obj)
        for rel in obj.relocations:
            f=obj.symbols[rel['symbol']]
            if f['info']>>4:
                target=em[f['name']];owner=e.sections[target['section']]['name']if target['section']else''
                role=(target['name'],target['info'],target['other'],target['size'],owner,target['value'])
            elif is_new:
                candidates=[x for x in gm.values()if x['info']==18 and x['section']==f['section']and x['value']<=f['value']<x['value']+x['size']]
                need(len(candidates)==1 and f['info']==0 and f['other']==f['size']==0,'Local PC-relative anchor has one actual code owner')
                own=candidates[0]
                role=(f['name'],f['info'],f['other'],f['size'],'.boot_code',offsets[own['name']]+f['value']-own['value'])
            else:
                need(f['section']>0 and f['section']!=0xfff1,'Retained parent local reference')
                role=(f['name'],f['info'],f['other'],f['size'],p.sections[f['section']]['name'],f['value'])
            if is_new:
                source_section=obj.sections[rel['section']]
                candidates=[x for x in gm.values()if x['section']==rel['section']and x['size']]
                need(len(candidates)==1,'One true source code/table owner per reference')
                own=candidates[0]
                if source_section['flags']&4:
                    need(own['info']==18,'Code reference source is FUNC')
                    section='.boot_code';offset=offsets[own['name']]+rel['offset']-own['value']
                else:
                    need(own['info']==17 and own['name']in data_offsets,'Data reference source is true table OBJECT')
                    section='.feature_tables';offset=data_offsets[own['name']]+rel['offset']-own['value']
            else:
                section=p.sections[rel['section']]['name'];offset=rel['offset']
            expected[(section,offset,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        f=e.symbols[rel['symbol']];owner=e.sections[f['section']]['name']if f['section']else''
        role=(f['name'],f['info'],f['other'],f['size'],owner,f['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==698,'All698 real code/table/global/local typed-reference roles')
    by_pc={x['start']:x['name']for x in S['all_selected_regions']}
    for table in S['tables']:
        for i,pc in enumerate(table['targets']):
            f=em[by_pc[pc]]
            need(f['info']==18 and f['size']>0 and f['section']==e.section('.boot_code')['index'],'Every relative-table target has genuine actual code')
    undefined=sorted(name for name,f in em.items()if not f['section'])
    need(undefined==K['remaining_undefined']and len(undefined)==82,'Exactly82 explicit remaining provider symbols')
    funcs=[f for f in em.values()if f['info']==18 and f['section']]
    need(sum(bool(f['size'])for f in funcs)==783 and sum(not f['size']for f in funcs)==26,'783 realregions and26 true aliases')
    vector=json.loads((ROOT/'experiments/tsl9-original-vectors/spec-v1.json').read_bytes());restored=bytearray(e.data('.vectors'));bound=external=0
    for row in vector['entries']:
        if not row['symbol']:continue
        if em[row['symbol']]['section']:bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    fw=(ROOT/S['firmware']).read_bytes()
    need(bytes(restored)==fw[vector['start']-0x8000:vector['end']-0x8000]and bound==62 and external==0,'Original vectors and62 genuine bindings preserved')
    return dict(passed=True,mode=mode,code_bytes=9836,original_code_instructions=3461,
        initializer_bytes=128,vector_carrier_bytes=328,new_relative_table_bytes=60,total_data_bytes=516,
        new_relative_table_OBJECTs=2,relative_table_bindings_to_real_code=15,
        nonzero_FUNC_regions=783,zero_size_FUNC_aliases=26,RELA=698,UND=undefined,
        reused_provider_bytes=2736,reused_provider_instructions=956,reused_provider_regions=269,reused_curated_units=8,
        parent7100B_code_and456B_data_unchanged=True,all2736B_code_and60B_tables_original_VA_encoded_equal=True,
        all_global_local_code_and_table_relocation_targets_owned=True,
        channel_route_and_feature_dispatch_entries_bound=True,existing_C6A8_decoder_entry_bound=True,
        three_duplicate_clock_bodies_supplied_by_real_parent=True,
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
    paths=[Path(__file__),HERE/'spec-v1.json',HERE/'integration-v2.json',HERE/'joined-v2.ld',
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
        print(json.dumps(dict(passed=True,mode='read-only-normal-dispatch-table-link-replay',source_proof=proof)));return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned native output')
    report=dict(schema='TSL9-dispatch-tables-native-link-v2',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir(parents=True);output=folder/OUTPUT;commands=[]
        recipes=[('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v2.ld'),str(parent(mode)),
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
