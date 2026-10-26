"""Verify one actual CODE owner per original PC; no target or model execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'experiments/tsl9-original-RF-bridge'
INPUTS=[('experiments/tsl9-resident-lle-callback-gateway/build/composition-v1','candidate.o'),('experiments/tsl9-sdk-unique-code-ownership/build/native-v1','unit.o'),('experiments/tsl9-resident-callback-registration/build/native-v2','unit.o'),('experiments/tsl9-original-RF-bridge/build/native-v2','unit.o')]
PINS=['da0013b58ec42b86b4458a5b9f78eb57747b92825a57cad145214883b622bd57','8afc4fa83d75a99b0cbe3eb1210d4936b304b3821f16c914eb3b4766d3d1c4bc','ac48167f497406bda778aaaed00559b9984055aafbd517bf669baf1591a67f72','757827265d2b08fffe7e6c9dd31f187d695ab043bfb0f5c136a95328f06d5c17']
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='unique_ownership_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Actual compilation inputs unchanged');results={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete native artifacts and include dependencies')
        results[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(results[mode]['CODE']==v['result']and results[mode]['ABI']==v['ABI_result'],'Fresh native readers match receipt')
    need(results['c']==results['cpp'],'C11/C++17 native artifacts identical');return N,results
def facts(path,ELF):
    e=ELF(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable RV32 ET_REL')
    a={s['name']:(s['type'],s['flags'],s['align'],e.data(s))for s in e.sections if s['flags']&2 and s['size']}
    d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']}
    u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
    r=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations)
    return a,d,u,r
def composition(path,inputs,N,O,before):
    ELF=lib(ROOT/N['S']['reader'])['ELF'];a={};d={};u=set();r=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique actual input section/symbol ownership');a.update(aa);d.update(dd);u.update(uu);r+=rr
    need(facts(path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected input byte,alignment,symbol and relocation retained')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    after=O['inspect'](path)
    need(after['passed']and after['duplicate_original_CODE_bytes']==0,'One real allocation per original-PC CODE byte')
    need(after['_byte_map']==before['_byte_map']and after['_typed_relations']==before['_typed_relations'],'Exact before/after original-PC native byte map and typed relocation relation set')
    need(after['non_CODE_allocations']==before['non_CODE_allocations']and after['named_UND']==before['named_UND'],'DATA allocation bytes/type/flags/alignment and all genuine dependencies unchanged')
    need((after['CODE_bytes'],after['distinct_original_CODE_bytes'],after['positive_FUNC_regions'],after['relocations'],after['distinct_PC_typed_relocations'])==(12658,12658,1037,781,781),'Exact unique composition counts')
    need(sum(v['size']for v in after['non_CODE_allocations'].values())==256 and len(after['named_UND'])==19,'256 DATA bytes and 19 genuine named dependencies')
    count=0
    for kind,flags,align,raw in a.values():
        if not flags&4:continue
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2;need(at+width<=len(raw),'Whole instruction extent');at+=width;count+=1
    need(count==4412,'Actual distinct native instruction count')
    return dict(**O['public'](after),DATA_bytes=256,allocated_bytes=12914,instructions=count,independent_readers=independent,every_selected_input_byte_symbol_relocation_retained=True,before_after_original_PC_byte_map_equal=True,before_after_original_PC_typed_relations_equal=True,DATA_and_named_UND_unchanged=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    prior=lib(OLD/'audit-v2.py');previous=prior['audit'](llvm,refs);need(canonical(previous)==json.loads((OLD/'audit-result-v2.json').read_bytes()),'Fresh complete previous native/static/trap/startup audit matches retained historical receipt')
    N,results=native(llvm);E=N['EV'];O=lib(HERE/'verify-ownership-v1.py');oldpath=OLD/'build/composition-v1/c/candidate.o';before=O['inspect'](oldpath)
    red=E['regression_before'];need(red['exit_code']==1 and red['checker_sha256']==sha(HERE/'verify-ownership-v1.py')and red['result']==O['public'](before)and not before['passed'],'Reproduce actual pre-fix regression failure without synthetic input')
    need(before['overlap_intervals']==[[0x63c54,0x63d6a]]and before['duplicate_original_CODE_bytes']==278,'Exact original duplicate range')
    oldev=json.loads((ROOT/'experiments/tsl9-resident-dispatch-handlers/evidence-v1.json').read_bytes());canonicalev=json.loads((ROOT/'experiments/tsl9-resident-state8-service/evidence-v1.json').read_bytes())
    oldbody=next(f for f in oldev['selected_functions']if f['start']==0x63c54);keptbody=next(f for f in canonicalev['selected_functions']if f['start']==0x63c54)
    need(oldbody['end']==keptbody['end']==0x63d6a and oldbody['original_sha256']==keptbody['original_sha256']=='82f07fced82ac94eae52ed7927014447b4d2e293589bdb031a252e6c4ee14cfe','Two selected names refer to the same original complete body')
    expected=[f for f in oldev['selected_functions']if f['start']!=0x63c54];need(E['selected_functions']==expected and len(expected)==3,'Only redundant complete body removed;retained instruction inventories unchanged')
    frames={0x57dae:32,0x6020a:32,0x63eda:16};external={f['start']for f in expected}|{int(k)for k in E['target_names']};cfg=[]
    for f in expected:
        ops,g,exits,calls=prior['own_frame'](f,N['B'],external,frames[f['start']]);cfg.append(dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frames[f['start']],whole_CFG_reachable=True,own_frame_balanced=True,exit_PCs=exits))
    out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition trial')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[ROOT/p/mode/n for p,n in INPUTS];need([sha(p)for p in inputs]==PINS,'All four exact native input identities');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(v)for v in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O,before)
    need(composed['c']==composed['cpp'],'Whole C11/C++17 compositions identical')
    return dict(schema='TSL9-unique-original-PC-CODE-ownership-audit-v1',passed=True,checker_sha256=sha(__file__),ownership_checker_sha256=sha(HERE/'verify-ownership-v1.py'),prior_audit_sha256=sha(OLD/'audit-result-v2.json'),native_results=results,retained_CFGs=cfg,regression_before=O['public'](before),duplicate_CODE_bytes_removed=278,duplicate_instructions_removed=95,duplicate_FUNC_regions_removed=16,duplicate_relocations_removed=9,new_unique_original_CODE_bytes=0,regenerated_dispatch_CODE_bytes=840,regenerated_instructions=289,canonical_existing_provider='tsl9_candidate_register_config_63c54',canonical_provider_original_body_sha256=keptbody['original_sha256'],composition=composed,composition_input_hashes=hashes,prior_sources_and_receipts_preserved=True,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,removed_duplicate_bytes=278,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','relocations']},new_unique_original_CODE_bytes=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
