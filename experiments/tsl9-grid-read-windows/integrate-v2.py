#!/usr/bin/env python3
"""Integrate a source-proven DATA pool using the measured full relocation-retention audit."""
from pathlib import Path
import argparse,hashlib,json,runpy,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v2.json').read_bytes())
OUTPUT='UNRESOLVED-STARTUP-GRID-READ-WINDOWS.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(rel):return runpy.run_path(str(ROOT/rel),run_name='source_proven_pool_library')
Q=lib('experiments/tsl9-grid-read-windows/verify-source-v2.py')
N=lib('experiments/tsl9-grid-read-windows/build-v2.py')
D=lib(K['retention_checker'])
portable,encoded=N['portable'],N['encoded']
def parent(mode):return ROOT/K['parent_folder']/mode/K['parent_object']
def native(mode):return ROOT/K['data_folder']/mode/'curated/unit.o'
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def source_proof(llvm):
    need(sha(ROOT/K['source_proof'])==K['source_proof_sha256'],'Pinned full source-extension receipt')
    need(sha(ROOT/K['retention_checker'])==K['retention_checker_sha256']and sha(ROOT/K['retention_spec'])==K['retention_spec_sha256'],'Measured real-label retention checker/spec')
    proof=Q['proof'](llvm)
    need(proof['total_source_comparisons']==252 and proof['total_source_objects']==504 and proof['source_C_H_files']==152 and proof['independent_data_units']==5,'Full current source proof')
    for mode in ['c','cpp']:
        need(parent(mode)==D['parent_path'](mode)and sha(parent(mode))==K['parent_sha256'],'Exact accepted parent and language')
        need(N['audit_object'](native(mode))==proof['modes'][mode]['grid_read_windows']['curated'],'Actual source-proven curated DATA object')
    return proof
def audit_component(path,mode):
    measured=D['audit_partial'](path,native(mode),mode)
    need(measured['passed']and measured['CODE_bytes']==64544 and measured['DATA_bytes']==3721 and measured['RELA']==4861 and measured['UND']==22,'Complete measured component byte/symbol/relocation retention')
    need(sorted(v['name']for v in N['S']['labels'])==K['resolved_providers']and measured['ABS_providers']==0,'Only the two genuine grid labels resolve')
    e=D['elf'](path);gm=D['globals_of'](e)
    functions=[v for v in gm.values()if v['info']==18 and v['section']]
    positive_data=[v for v in gm.values()if v['info']==17 and v['size']and v['section']]
    aliases=[v for v in gm.values()if v['info']==17 and not v['size']and v['section']]
    parent_globals=D['globals_of'](D['elf'](parent(mode)))
    prior_DATA_labels={name for name,v in parent_globals.items()if v['info']==17 and not v['size']and v['section']}
    need(sum(bool(v['size'])for v in functions)==5688 and sum(not v['size']for v in functions)==71,'All existing code regions and true code aliases retained')
    need(prior_DATA_labels==set(K['retained_parent_DATA_labels'])and len(prior_DATA_labels)==4 and len(positive_data)==37 and {v['name']for v in aliases}==prior_DATA_labels|set(K['resolved_providers']),'One new DATA owner,four retained DATA labels and exactly two new grid labels')
    labels={v['name']:v for v in N['S']['labels']};owner=gm[N['S']['owner']['name']]
    for v in aliases:
        if v['name']in prior_DATA_labels:continue
        label=labels[v['name']]
        need(v['section']==owner['section']and v['value']==owner['value']+label['pool_offset']and v['info']==17,'Every interior label has actual same-section pool backing')
    return dict(passed=True,mode=mode,code_bytes=64544,original_instructions=21938,data_bytes=3721,FUNC=5688,true_aliases=71,readonly_objects=37,real_zero_size_DATA_labels=6,new_real_zero_size_DATA_labels=2,retained_parent_zero_size_DATA_labels=4,RELA=4861,UND=sorted(n for n,v in gm.items()if not v['section']),new_code_bytes=0,new_original_instructions=0,new_data_bytes=432,new_DATA_objects=1,resolved_original_providers=K['resolved_providers'],new_external_providers=[],source_curated=True,source_comparisons=252,source_objects=504,all_parent_CODE_and_DATA_bytes_preserved=True,all_actual_symbol_and_relocation_roles_preserved=True,native_object_sha256=sha(path),independent_readers=measured['independent_readers'],ABS_providers=0,no_stub_added=True,original_address_placement_proved=False,original_declaration_extents_proved=False,global_runtime_pointer_limit_bound_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,private_ABI_proved=False,executable=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,firmware_BIN_generated=False,firmware_ready=False)
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
        print(json.dumps(dict(passed=True,mode='read-only-grid-read-window-component-replay',code_bytes=64544,data_bytes=3721,RELA=4861,UND=22,source_comparisons=252,source_objects=504,firmware_ready=False)));return
    need(not out.exists(),'Create-only component output');record=dict(schema='TSL9-source-proven-grid-read-window-component-v2',inputs=before,source_proof=proof,modes={})
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
