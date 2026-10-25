#!/usr/bin/env python3
"""Integrate a source-proven DATA pool using the measured full relocation-retention audit."""
from pathlib import Path
import argparse,hashlib,json,runpy,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v2.json').read_bytes())
OUTPUT='UNRESOLVED-STARTUP-CALLBACK-PREFIX-DATA.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(rel):return runpy.run_path(str(ROOT/rel),run_name='source_proven_pool_library')
Q=lib('experiments/tsl9-callback-prefix-data/verify-source-v2.py')
N=lib('experiments/tsl9-callback-prefix-data/build-v2.py')
D=lib(K['retention_checker'])
portable,encoded=N['portable'],N['encoded']
def parent(mode):return ROOT/K['parent_folder']/mode/K['parent_object']
def native(mode):return ROOT/K['data_folder']/mode/'curated/unit.o'
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def source_proof(llvm):
    need(sha(ROOT/K['source_proof'])==K['source_proof_sha256'],'Pinned full source-extension receipt')
    need(sha(ROOT/K['retention_checker'])==K['retention_checker_sha256']and sha(ROOT/K['retention_spec'])==K['retention_spec_sha256'],'Measured real-label retention checker/spec')
    proof=Q['proof'](llvm)
    need(proof['total_source_comparisons']==254 and proof['total_source_objects']==508 and proof['source_C_H_files']==153 and proof['independent_data_units']==6,'Full current source proof')
    for mode in ['c','cpp']:
        need(parent(mode)==D['parent_path'](mode)and sha(parent(mode))==K['parent_sha256'],'Exact accepted parent and language')
        need(N['audit_object'](native(mode))==proof['modes'][mode]['callback_prefix_data']['curated'],'Actual source-proven curated DATA object')
    return proof
def audit_component(path,mode):
    measured=D['audit_partial'](path,native(mode),mode)
    need(measured['passed']and measured['CODE_bytes']==64544 and measured['DATA_bytes']==3830 and measured['RELA']==4861 and measured['UND']==8,'Exact whole-component DATA/reference retention')
    need(measured['resolved_original_DATA_providers']==K['resolved_providers']and measured['ABS_providers']==0,'Only fourteen genuine readonly providers resolve')
    e=D['elf'](path);gm=D['globals_of'](e);parent_globals=D['globals_of'](D['elf'](parent(mode)))
    functions=[v for v in gm.values()if v['info']==18 and v['section']]
    positive_data=[v for v in gm.values()if v['info']==17 and v['section']and v['size']]
    labels={n for n,v in gm.items()if v['info']==17 and v['section']and not v['size']}
    old_labels={n for n,v in parent_globals.items()if v['info']==17 and v['section']and not v['size']}
    need(sum(bool(v['size'])for v in functions)==5688 and sum(not v['size']for v in functions)==71,'All existing CODE regions and true CODE aliases retained')
    need(labels==old_labels==set(K['retained_parent_DATA_labels'])and len(labels)==6 and len(positive_data)==51,'Six retained real DATA labels and exactly fourteen new positive owners')
    for d in N['S']['data_regions']:
        v=gm[d['name']]
        need(v['info']==17 and v['size']==d['bytes']and e.sections[v['section']]['name']==d['section'],'Every new provider has exact actual readonly storage')
    return dict(passed=True,mode=mode,code_bytes=64544,original_instructions=21938,data_bytes=3830,FUNC=5688,true_aliases=71,readonly_objects=51,real_zero_size_DATA_labels=6,new_real_zero_size_DATA_labels=0,retained_parent_zero_size_DATA_labels=6,RELA=4861,UND=sorted(n for n,v in gm.items()if not v['section']),new_code_bytes=0,new_original_instructions=0,new_data_bytes=109,new_DATA_objects=14,resolved_original_providers=K['resolved_providers'],new_external_providers=[],source_curated=True,source_comparisons=254,source_objects=508,all_parent_CODE_and_DATA_bytes_preserved=True,all_actual_symbol_and_relocation_roles_preserved=True,native_object_sha256=sha(path),independent_readers=measured['independent_readers'],ABS_providers=0,no_stub_added=True,original_address_placement_proved=False,original_declaration_extents_proved=False,installed_ROM_read_contract_proved=False,unprovided_candidate_callback_CODE_targets=[0x10c36,0x10d2e,0x10d30,0x11544],compiler_UND_is_not_complete_missing_runtime_target_count=True,global_runtime_pointer_limit_bound_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,private_ABI_proved=False,executable=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths={Path(__file__),HERE/'integration-v2.json',ROOT/K['source_proof'],ROOT/K['retention_checker'],ROOT/K['retention_spec']}
    paths.update(Path(p)for p in Q['inputs'](llvm))
    for mode in ['c','cpp']:paths.update([parent(mode),native(mode)])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path);a=p.parse_args();llvm=a.tool_dir.resolve()
    proof=source_proof(llvm);before=portable(inputs(llvm),llvm);out=(a.replay or a.output).resolve();need(out.parent==HERE/'build','Owned component output')
    if a.replay:
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before and saved['source_proof']==proof,'Exact current source/component inputs')
        for mode in ['c','cpp']:
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Complete retained component outputs')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Actual full component replay')
        print(json.dumps(dict(passed=True,mode='read-only-callback-prefix-component-replay',code_bytes=64544,data_bytes=3830,RELA=4861,UND=8,source_comparisons=254,source_objects=508,firmware_ready=False)));return
    need(not out.exists(),'Create-only component output');record=dict(schema='TSL9-source-proven-callback-prefix-component-v2',inputs=before,source_proof=proof,modes={})
    for mode in ['c','cpp']:
        f=out/mode;f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent(mode)),str(native(mode)),'-o',str(f/OUTPUT)]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/'link.log').write_text(portable((result.stdout+result.stderr).decode('utf8','replace'),llvm),encoding='utf8');need(result.returncode==0,'Actual native link failed;local log retained')
        facts=audit_component(f/OUTPUT,mode);(f/'verification.json').write_bytes(encoded(facts));record['modes'][mode]=dict(result=facts,commands=[dict(label='link',argv=portable(argv,llvm),exit=result.returncode)],artifacts=inventory(f))
        print(json.dumps({k:v for k,v in facts.items()if k not in ('UND','independent_readers')}|dict(UND_count=len(facts['UND']))))
    need(sha(out/'c'/OUTPUT)==sha(out/'cpp'/OUTPUT),'Complete C/C++ component identity')
    need(before==portable(inputs(llvm),llvm),'Every actual input unchanged during integration');(out/'measurement.json').write_bytes(encoded(record))
if __name__=='__main__':
    try:main()
    except Exception as e:
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));sys.exit(1)
