"""Verify ten complete root-chain bodies,eight genuine new CODE gaps and two callbacks;no execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-record-transition';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='record_root_chain_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result

def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');rows=[];graphs={};op={};frames={0x58498:16,0x58462:16,0x5784a:0,0x59d3e:32,0x59e64:32,0x5e3a8:32,0x57962:16,0x57a4a:16,0x57a1e:16,0x578a4:32}
    for f in E['selected_functions']:
        ext={c[1]for o in f['operations']if(c:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,frames[f['start']]);rows.append(q);graphs[f['start']]=g;op.update(oo)
    need(sum(f['bytes']for f in rows)==1700 and sum(f['instructions']for f in rows)==572 and len(rows)==10,'Ten complete reachable CFGs and original own-frame balance')
    required={0x58498:'addi sp, sp, -16',0x585b0:'lw ra, 12(sp)',0x585b4:'mv a0, s1',0x585b8:'addi sp, sp, 16',0x585ba:'j 0x58462',0x585c6:'j 0x58578',0x5784a:'lui a5, 0x20003',0x5784e:'lw a5, 1108(a5)',0x57852:'bnez a5, 0x57858',0x57854:'mv a0, a5',0x57856:'ret',0x57858:'qk.c.lhu a4, 8(a5)',0x5785a:'beq a4, a0, 0x57854',0x5785e:'lw a5, 0(a5)',0x57860:'j 0x57852',0x59df4:'lw a5, 1252(a5)',0x59dfc:'andi a5, a5, 2',0x59dfe:'beqz a5, 0x59e22',0x59e00:'lui s2, 0x20003',0x59e04:'addi s2, s2, 492',0x59e08:'lw a5, 52(s2)',0x59e0c:'beqz a5, 0x59e22',0x59e0e:'lw a1, 152(s0)',0x59e12:'li a0, 13',0x59e14:'jalr a5',0x59e16:'lw a5, 52(s2)',0x59e1a:'lw a1, 156(s0)',0x59e1e:'li a0, 14',0x59e20:'jalr a5',0x59e22:'mv a0, s0',0x59e2e:'lw ra, 28(sp)',0x59e38:'addi sp, sp, 32',0x59e3a:'j 0x56716',0x5e3e8:'lw s0, 24(sp)',0x5e3ea:'lw ra, 28(sp)',0x5e3f0:'mv a1, a0',0x5e3f6:'addi sp, sp, 32',0x5e3f8:'j 0x43208',0x5e408:'li a0, 4',0x5e40a:'addi sp, sp, 32',0x5e40c:'ret'}
    need(all(op[p]['opcode']==s for p,s in required.items()),'Exact original root tail,lookup,callback loads/guards/arguments and message tail')
    tails=[]
    for root,pc,target,frame,dominators in [(0x58498,0x585ba,0x58462,16,[0x585b0,0x585b4,0x585b8]),(0x59d3e,0x59e3a,0x56716,32,[0x59e22,0x59e2e,0x59e38]),(0x5e3a8,0x5e3f8,0x43208,32,[0x5e3ea,0x5e3f0,0x5e3f6])]:
        word=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(op[pc]['bytes']),pc)[1]==target,'Actual original JALzero tail');need(all(pc not in V['reachable'](graphs[root],root,skip=p)for p in dominators),'Original arguments,RA and frame release dominate tail');tails.append(dict(PC=pc,target=target,own_frame_released=frame,original_RA_restored=True,arguments_prepared_before_tail=True))
    need(graphs[0x59d3e][0x59e0c]==[0x59e22,0x59e0e]and graphs[0x59d3e][0x59e14]==[0x59e16]and graphs[0x59d3e][0x59e20]==[0x59e22],'Original null guard and second fresh-load/call order,without invented second guard')
    need(0x20003000+492+52==0x20003220 and 0x20003000+1108==0x20003454,'Numeric callback-slot and lookup-head arithmetic')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={pc for f in rows for pc in range(f['start'],f['end'])};need(parent['passed']and not newbytes&set(parent['_byte_map'])and set(E['resolved_prior_dependencies'])<=set(parent['named_UND']),'Actual missing58498 provider and no duplicate CODE');need(all(pc in parent['_byte_map']for pc in E['real_prior_providers'])and len(E['real_prior_providers'])==8,'Eight real prior imports');need(len(E['new_genuine_code_dependencies'])==8 and all(pc not in parent['_byte_map']and pc not in newbytes for pc in E['new_genuine_code_dependency_entries']),'Eight actual newly exposed unresolved entry points,without stubs')
    far={p['PC']+4:p['target_PC']for p in N['S']['PC_relative_pairs']};calls=[];opaque=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target'])
            if target is None:need(call['PC']in [0x59e14,0x59e20],'Only actual original optional callbacks are opaque');opaque.append(call['PC'])
            else:need(target in newbytes|set(E['real_prior_providers'])|set(E['new_genuine_code_dependency_entries']),'Every actual static call has exact selected,real prior or genuine unresolved target');calls.append(dict(PC=call['PC'],target=target))
    need(opaque==[0x59e14,0x59e20],'Exactly two original callback sites retained')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Whole actual caller evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x588b4);sites=[];raw=(ROOT/E['firmware']).read_bytes()
    for o in f['operations']:
        need(bytes.fromhex(o['bytes'])==raw[o['addr']-0x40000:o['addr']-0x40000+o['size']],'Original caller bytes');d=B['decode_control'](bytes.fromhex(o['bytes']),o['addr'])
        if d and d[1]==0x58498:sites.append(o['addr'])
    need(sites==[0x5895e],'Actual original588B4 to58498 callsite')
    return dict(passed=True,functions=rows,CODE_bytes=1700,instructions=572,complete_functions=10,own_frames=[frames[f['start']]for f in E['selected_functions']],conditional_Xwchc_ports=40,actual_static_calls=calls,actual_opaque_callback_sites=opaque,actual_opaque_callbacks=2,original_caller=0x588b4,actual_58498_call_sites=sites,resolved_prior_dependencies=E['resolved_prior_dependencies'],real_prior_providers=E['real_prior_providers'],new_genuine_code_dependencies=E['new_genuine_code_dependencies'],new_genuine_code_dependency_entries=E['new_genuine_code_dependency_entries'],new_genuine_named_dependencies=8,direct_no_link_tails=tails,optional_status_callbacks=dict(pointer_slot=0x20003220,first_pointer_load_PC=0x59e08,first_null_guard_PC=0x59e0c,first_call_PC=0x59e14,first_A0=13,first_A1_record_offset=152,second_fresh_pointer_load_PC=0x59e16,second_call_PC=0x59e20,second_A0=14,second_A1_record_offset=156,second_pointer_stability_or_nonnull_not_proved=True,callback_bodies_or_effects_not_provided=True,live_binding_or_event_meaning_not_proved=True),lookup=dict(entry=0x5784a,end=0x57862,head_pointer_slot=0x20003454,next_word_offset=0,compared_halfword_offset=8,input_A0_not_truncated=True,own_frame_bytes=0,valid_memory_acyclicity_and_termination_proved=False),all_post_RET_reachable_arms_preserved=True,no_live_record_or_MAC_contents_observed=True,all_numeric_CODE_pointers_or_callbacks_closed=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set(N['EV']['new_genuine_code_dependencies']);expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==8 and out['non_CODE_allocations']==before['non_CODE_allocations'],'58498 supplied,eight genuine newly exposed CODE imports,DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(34086,2300,1848),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=34342,instructions=11781,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,one_genuine_prior_named_dependency_has_real_body=True,new_genuine_named_dependencies=8,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh entire callback-provenance and preceding APP/SDK/native/IRQ/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],result[mode]['CODE']['object_sha256']],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-record-root-chain-audit-v1',passed=True,checker_sha256=sha(__file__),prior_record_transition_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=1700,new_instructions=572,new_complete_functions=10,new_genuine_named_dependencies=8,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1700,new_instructions=572,complete_functions=10,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=len(v['contract']['resolved_prior_dependencies']),opaque_callbacks=2,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
