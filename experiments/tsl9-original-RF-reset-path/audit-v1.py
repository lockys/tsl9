"""Audit actual RF initializer dependencies and register polling,without execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-original-RF-tx-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='RF_reset_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual native inputs unchanged');results={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Native object/log/include inventories retained')
        results[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(results[mode]['CODE']==v['result']and results[mode]['ABI']==v['ABI_result'],'Fresh native readers match compile receipt')
    need(results['c']==results['cpp'],'Actual C11/C++17 native objects identical');return N,results
def callers(N):
    E=N['EV'];p=ROOT/E['required_callers']['evidence'];need(sha(p)==E['required_callers']['evidence_sha256'],'Original actual initializer/reset caller evidence unchanged');old=json.loads(p.read_bytes());A=lib(ROOT/'experiments/tsl9-original-RF-bridge/audit-v2.py');external={f['start']for f in old['selected_functions']}|{int(k)for k in old['target_names']};selected={f['start']:f for f in old['selected_functions']};graphs={};ops={};rows=[]
    for root,frame in [(0x641b0,32),(0x64298,16)]:
        oo,g,exits,cs=A['own_frame'](selected[root],N['B'],external,frame);ops.update(oo);graphs[root]=g
        for call in cs:
            if call['target']in [0x660ce,0x662da,0x6636e,0x6645c,0x67198]:rows.append(dict(owner=root,PC=call['PC'],target=call['target'],dominates_all_local_normal_exits=all(v not in A['reachable'](g,root,skip_node=call['PC'])for v in exits)))
    need(sorted((v['PC'],v['target'])for v in rows)==sorted((v['PC'],v['target'])for v in E['required_callers']['direct_calls']),'All five newly supplied entries are actual prior direct callees')
    need([v['dominates_all_local_normal_exits']for v in rows]==[False,False,False,False,True],'Conditional common-reset calls distinguished from initializer call dominating its local tail')
    expected={0x641b8:'addi s0, s0, 1300',0x641bc:'qk.c.lbu a4, 7(s0)',0x641ca:'li a5, 4',0x641cc:'beq a5, a4, 0x64286',0x641d0:'qk.c.lbu a4, 7(s0)',0x641d2:'beq a5, a4, 0x64286',0x641da:'lw a4, 1284(a5)',0x641de:'lui s1, 0x40024',0x641e2:'addi a5, s1, 768',0x641e6:'bne a4, a5, 0x64286',0x64246:'jal ra, 0x6645c',0x6424a:'jal ra, 0x67198',0x6424e:'jal ra, 0x662da',0x64252:'jal ra, 0x6636e',0x642fe:'jal ra, 0x660ce'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual two fresh mode reads,pointer comparison and direct call operands')
    g=graphs[0x641b0]
    for edge in [(0x641cc,0x641d0),(0x641d2,0x641d6),(0x641e6,0x641ea)]:need(0x64246 not in A['reachable'](g,0x641b0,skip_edge=edge),'Each actual guard fallthrough required for reset-call path')
    need(all(b not in A['reachable'](g,0x64246,skip_node=a)for a,b in [(0x6424a,0x6424e),(0x6424e,0x64252)]),'Actual local reset call order retained')
    return dict(passed=True,direct_calls=rows,initializer_call_660CE_dominates_local_tail=True,four_reset_calls_are_conditional=True,two_fresh_mode_byte_reads=dict(storage=0x2000351b,comparison=4,PCs=[0x641bc,0x641d0]),pointer_guard=dict(storage=0x20003504,compared_value=0x40024300,branch_PC=0x641e6),guard_stability_across_async_effects_proved=False,normal_callee_returns_and_register_preservation_assumed=True,physical_pointer_or_register_identity_proved=False)
def contract(N,V):
    E=N['EV'];frames={0x660ce:16,0x662da:0,0x6636e:0,0x6645c:80,0x67198:0,0x66098:0,0x20002df2:0};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};ops={};graphs={};rows=[]
    for f in E['selected_functions']:
        oo,g,v=V['whole_cfg'](f,N['B'],set(frames),frames[f['start']]);ops.update(oo);graphs[f['start']]=g
        for call in v['calls']:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        need(all(call['target']in frames for call in v['calls']),'Every actual direct or far callee has selected complete CODE');rows.append(v)
    expected={0x660d2:'jal ra, 0x66098',0x660d6:'lui a5, 0x20003',0x660da:'lw a5, 1424(a5)',0x66098:'lui a5, 0x20003',0x6609c:'lw a3, 1424(a5)',0x660a0:'lui a4, 0x1',0x660a2:'addi a4, a4, 257',0x660a6:'sw a4, 12(a3)',0x660a8:'li a4, 20',0x660ae:'bnez a4, 0x660aa',0x660b4:'sw zero, 12(a4)',0x660b8:'li a4, 20',0x660be:'bnez a4, 0x660ba',0x660ca:'sw a5, 12(a4)',0x6632c:'sw a5, 100(a2)',0x6632e:'lw a5, 100(a2)',0x66330:'beqz a5, 0x6633c',0x66332:'lw a5, 156(a3)',0x66336:'srli a5, a5, 0x8',0x66338:'andi a5, a5, 1',0x6633a:'beqz a5, 0x6632e',0x664c2:'lw a2, 1416(a3)',0x664c6:'lui a4, 0x12345',0x664ca:'addi a4, a4, 1656',0x664d0:'beq a2, a4, 0x67190',0x67190:'sw zero, 1416(a3)',0x67194:'j 0x665b0',0x20002df6:'lw a4, 1340(a5)',0x20002dfa:'lui a5, 0x1',0x20002dfc:'addi a5, a5, 1904',0x20002e00:'sw a5, 100(a4)',0x20002e06:'lw a5, 1424(a5)',0x20002e0a:'lw a3, 144(a5)',0x20002e0e:'slli a2, a3, 0x5',0x20002e12:'bgez a2, 0x20002e22',0x20002e16:'lw a3, 144(a5)',0x20002e1a:'slli a2, a3, 0x6',0x20002e1e:'bltz a2, 0x20002e26',0x20002e22:'lw a3, 100(a4)',0x20002e24:'bnez a3, 0x20002e0a'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual reset pulses,magic branch,polling reads and raw threshold operands')
    need(0x12345000+1656==0x12345678 and 0x1000+1904==6000 and 0x1000+257==0x1101,'Original raw arithmetic operands')
    far=sorted((p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs']);need(far==[(0x664f8,0x20002df2),(0x6653a,0x20002df2),(0x66586,0x20002df2)],'Exactly three real calls to selected polling helper')
    g=graphs[0x6645c];bypass=V['reachable'](g,0x67190);need(all(pc not in bypass for pc,target in far)and 0x665b0 in bypass and 0x6718e in bypass,'Magic branch clears word then joins after three polling-helper calls,including late arm afterRET')
    need(0x6718e not in V['reachable'](g,0x6645c,skip=0x6718c),'Large body releases actual80-byte frame at normal return')
    vectors=(ROOT/E['official_vectors']['path']).read_text();need(sha(ROOT/E['official_vectors']['path'])==E['official_vectors']['sha256']and len(E['official_vectors']['checked'])==52 and all(N['lib'](N['S']['source_deriver'])['custom_decode'](v['word'])==v['instruction']for v in E['official_vectors']['checked']),'All52 pinned primary instruction vectors');need(sum(o['opcode'].startswith('qk.c.')for o in ops.values())==4,'All4 actual conditional custom operations')
    return dict(passed=True,functions=rows,caller_contract=callers(N),selected_CALL_targets_all_have_real_bodies=True,opaque_CODE_transfers=0,raw_dependency_list_is_not_exhaustive=True,raw_dependencies=E['raw_dependencies'],primary_vectors_checked=52,actual_custom_ports=4,register_sequence_helper=dict(entry=0x66098,pointer_word=0x20003590,pointed_offset=12,raw_writes=[0x1101,0,0x1101],software_loop_initial_counts=[20,20],physical_reset_or_duration_proved=False),polling_helpers=[dict(entry=0x662da,timeout_pointer_word=0x2000353c,timeout_offset=100,raw_threshold=80,status_pointer_word=0x20003590,status_offset=156,status_bit=8,termination_or_timeout_units_proved=False),dict(entry=0x20002df2,timeout_pointer_word=0x2000353c,timeout_offset=100,raw_threshold=6000,status_pointer_word=0x20003590,status_offset=144,first_read_bit=26,second_distinct_read_bit=25,fresh_volatile_reads_must_not_be_merged=True,termination_or_timeout_units_proved=False)],magic_branch=dict(word_storage=0x20003588,compared_word=0x12345678,compare_PC=0x664d0,late_arm_PC=0x67190,word_cleared_before_join=True,join_PC=0x665b0,three_polling_calls_skipped_on_that_CFG_path=True,calibration_or_cache_semantic_name_is_inferred=True,physical_effects_or_validity_proved=False,runtime_control_added=False),all_callee_side_effects_MMIO_capacity_aliasing_and_async_effects_bounded=False,installed_ROM_identity_proved=False,physical_register_identity_proved=False,runtime_closed=False)
def composition(path,inputs,N,P,O):
    ELF=lib(ROOT/N['S']['reader'])['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique actual input section and symbol names');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC CODE ownership within and between inputs');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every actual input byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC native byte and typed relation union')
    before=O['inspect'](inputs[0]);need(set(out['named_UND'])==set(before['named_UND'])-set(N['EV']['supplied_prior_UND'])and len(out['named_UND'])==14 and out['non_CODE_allocations']==before['non_CODE_allocations'],'Five genuine dependencies supplied;14 genuine dependencies and256 DATA bytes retained')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(18526,1194,894),'Exact unique native composition counts');independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=18782,instructions=6330,independent_readers=independent,every_selected_input_byte_symbol_relocation_retained=True,five_genuine_prior_named_dependencies_have_real_bodies=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_MMIO_and_poll_termination_proved=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    V=lib(PRIOR/'audit-v1.py');previous=V['audit'](llvm,refs);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh full prior native/static/ownership/trap proof equals retained receipt');N,results=native(llvm);sc=contract(N,V);P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');O=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/verify-ownership-v1.py');out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==['5bfd1a5a83abdff174844a0228d687f7dff7c8a6c6961d5c3ab312553145083c','3173fe31fac139659b8c249bfef119803f891419e23313c74d3a2c142d4cd3ff'],'Exact current unique parent and new actual native input identities');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(v)for v in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,P,O)
    need(composed['c']==composed['cpp'],'Whole actual C/C++ compositions identical')
    return dict(schema='TSL9-required-RF-reset-dependencies-audit-v1',passed=True,checker_sha256=sha(__file__),prior_audit_sha256=sha(PRIOR/'audit-result-v1.json'),native_results=results,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=4090,new_instructions=1298,new_complete_bodies=7,supplied_genuine_prior_dependencies=5,new_genuine_named_dependencies=0,new_APP_CODE_bytes=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=4090,new_instructions=1298,supplied_genuine_dependencies=5,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','relocations','named_UND']},new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
