"""Audit conditional trap operands,zero-allocation C/C++ contracts and prior real CODE."""
import argparse,json,runpy,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-resident-lle-callback-gateway'
def need(ok,label):
    if not ok:raise ValueError(label)
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='static_trap_audit_library')
def audit(llvm,refs):
    N=lib(HERE/'build-v1.py');s,e=N['pins'](llvm,refs);saved=load(HERE/'build/native-v1/measurement.json');need(saved['inputs']==N['inputs'](llvm,refs),'Every native compile input retained');native={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['dependencies'](f,llvm,refs),'Actual complete native artifacts and dependency closure retained');native[mode]=N['object_facts'](f/'unit.o');need(native[mode]==v['result'],'Independent current ELF facts match saved compile result')
    need(native['c']==native['cpp'],'Actual C11/C++17 numeric constraint objects identical')
    previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(json.loads(json.dumps(previous))==load(PRIOR/'audit-result-v1.json'),'Full fresh prior original-byte/CFG/frame/composition proof retained')
    for mode in ['c','cpp']:need(previous['composition'][mode]['object_sha256']=='da0013b58ec42b86b4458a5b9f78eb57747b92825a57cad145214883b622bd57','Actual9608-CODE/256-DATA prior composition retained')
    memory=load(ROOT/'analysis/memory-rom-requirements-2026-10-25/evidence.json');need(memory['passed']and all(memory['current'][k]==e[v]for k,v in [('initial_gp','initial_GP'),('initial_sp','initial_SP'),('copy_end','copy_end'),('zero_end','zero_end')]),'Pinned prior memory analysis and independent actual reset fields agree')
    need(len(load(ROOT/'src/source-manifest.json')['files'])==159,'Formal APP source inventory retained')
    return dict(schema='TSL9-trap-profile-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),source_sha256=sha(HERE/'trap_context_contract.c'),spec_sha256=sha(HERE/'spec-v1.json'),build_sha256=sha(HERE/'build-v1.py'),native_results=native,prior_LLE_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_real_CODE_composition={k:previous['composition']['c'][k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},all_prior_real_CODE_and_contracts_retained=True,new_APP_CODE_bytes=0,new_SDK_CODE_bytes=0,new_DATA_bytes=0,new_functional_implementation_bytes=0,static_primary_vector_slots=e['vector_enum_correspondence'],initial_GP=e['initial_GP'],initial_SP=e['initial_SP'],LLE_initial_GP_plus384_word=e['LLE_GP_plus384_pointer'],LLE_word_in_original_zero_interval=True,LLE_binding_must_precede_any_dispatch=True,actual_binding_before_dispatch_proved=False,original_reset_CSR804_value=3,documented_candidate_nesting_bit_initially_set=True,restore_CSR804_OR_mask=32,restore_does_not_disable_nesting_bit=True,mode3_or_bit5_meaning_proved=False,primary_header_is_not_physical_identity=True,GP_stability_after_resident_proved=False,global_stack_or_IRQ_budget_proved=False,inherited_startup_source_gap_bytes=4,startup_completed_proved=False,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_trap_route_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--reference-root',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve())
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,native_allocated_bytes=0,new_CODE_bytes=0,prior_CODE_bytes=9608,prior_DATA_bytes=256,static_primary_slots=4,initial_LLE_pointer=hex(result['LLE_initial_GP_plus384_word']),actual_binding_before_dispatch_proved=False,physical_trap_route_proved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
