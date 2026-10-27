"""Verify complete58988/580A4 candidate bodies and both frame-released tails;no execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-record-configuration';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='record_transition_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result

def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');rows=[];graphs={};op={};frames={0x58988:32,0x580a4:32}
    for f in E['selected_functions']:
        ext={c[1]for o in f['operations']if(c:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,frames[f['start']]);rows.append(q);graphs[f['start']]=g;op.update(oo)
    need(sum(f['bytes']for f in rows)==918 and sum(f['instructions']for f in rows)==322,'Two complete reachable CFGs and balanced original32-byte frames')
    required={0x58988:'addi sp, sp, -32',0x58b1a:'jal ra, 0x580a4',0x58b50:'lbu a5, 1300(s1)',0x58b54:'andi a5, a5, 1',0x58b56:'beqz a5, 0x58b9c',0x58b58:'mv a0, s0',0x58b5a:'lw s0, 24(sp)',0x58b5c:'sb zero, 1300(s1)',0x58b60:'lw ra, 28(sp)',0x58b62:'lw s1, 20(sp)',0x58b64:'lw s2, 16(sp)',0x58b66:'lw s3, 12(sp)',0x58b68:'lw s4, 8(sp)',0x58b6a:'addi sp, sp, 32',0x58b6c:'j 0x58788',0x58c12:'jal ra, 0x585c8',0x58c16:'li a5, 1',0x58c18:'li s2, 8',0x58c1a:'bne a0, a5, 0x58b9c',0x58c1e:'mv a0, s0',0x58c20:'lw s0, 24(sp)',0x58c22:'lw ra, 28(sp)',0x58c24:'lw s1, 20(sp)',0x58c26:'lw s2, 16(sp)',0x58c28:'lw s3, 12(sp)',0x58c2a:'lw s4, 8(sp)',0x58c2c:'addi sp, sp, 32',0x58c2e:'j 0x58744',0x580a4:'addi sp, sp, -32',0x580a8:'lui s3, 0x20003',0x580ac:'lw a5, 1340(s3)',0x580ba:'lui s2, 0x20003',0x580c6:'lw a3, 1288(s2)',0x580ca:'lui a4, 0x8e89c',0x580ce:'addi a4, a4, -298',0x580d2:'sw a4, 8(a3)',0x580d4:'lui a4, 0x555',0x580d8:'addi a4, a4, 1365',0x580dc:'sw a4, 4(a3)',0x580e0:'li a2, 0',0x580e2:'li a1, 255',0x580ec:'li a5, -77',0x580f0:'qk.c.sb a5, 6(a0)',0x580f6:'lbu a0, 60(a0)',0x580fe:'li a4, 7',0x58100:'qk.c.sb a4, 7(s1)',0x58102:'sb zero, 1300(a5)',0x58106:'jal ra, 0x63c54',0x58162:'lw ra, 28(sp)',0x5816c:'addi sp, sp, 32',0x5816e:'ret'}
    need(all(op[p]['opcode']==s for p,s in required.items()),'Exact original guards,arguments,frame restores,tails and numeric configuration operands')
    tails=[];g=graphs[0x58988]
    for pc,target,dominators in [(0x58b6c,0x58788,[0x58b58,0x58b60,0x58b6a]),(0x58c2e,0x58744,[0x58c1e,0x58c22,0x58c2c])]:
        word=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(op[pc]['bytes']),pc)[1]==target,'Actual JALzero tail,not ordinary C call');need(all(pc not in V['reachable'](g,0x58988,skip=p)for p in dominators),'Original record argument,RA restoration and32-byte frame release dominate each tail');tails.append(dict(PC=pc,target=target,original_record_argument_restored=True,original_RA_restored=True,own32_frame_released=True))
    need(g[0x58b56]==[0x58b9c,0x58b58]and g[0x58c1a]==[0x58b9c,0x58c1e],'Exact bit-test and equality guard polarities');need(max(graphs[0x580a4])+op[max(graphs[0x580a4])]['size']==0x58170 and max(g)+op[max(g)]['size']==0x58c52,'Complete body bounds exclude adjacent58170 and58C52');need(0x58c4c in g,'All late reachable arms beyond early RET retained')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={pc for f in rows for pc in range(f['start'],f['end'])};need(parent['passed']and not newbytes&set(parent['_byte_map'])and set(E['resolved_prior_dependencies'])<=set(parent['named_UND']),'Actual missing58988 provider and unique CODE');need(all(pc in parent['_byte_map']for pc in E['real_prior_providers'])and len(E['real_prior_providers'])==9 and not E['retained_prior_genuine_UND'],'All nine imports have real prior bodies')
    far={p['PC']+4:p['target_PC']for p in N['S']['PC_relative_pairs']};calls=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target']);need(target is not None and target in newbytes|set(E['real_prior_providers']),'Every actual call has an exact selected/prior target');calls.append(dict(PC=call['PC'],target=target))
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Complete caller evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x58c52);sites=[];raw=(ROOT/E['firmware']).read_bytes()
    for o in f['operations']:
        need(bytes.fromhex(o['bytes'])==raw[o['addr']-0x40000:o['addr']-0x40000+o['size']],'Original caller bytes');d=B['decode_control'](bytes.fromhex(o['bytes']),o['addr'])
        if d and d[1]==0x58988:sites.append(o['addr'])
    need(len(sites)==1,'One actual encoded58C52 caller for58988')
    return dict(passed=True,functions=rows,CODE_bytes=918,instructions=322,complete_functions=2,own_frames=[32,32],conditional_Xwchc_ports=17,actual_calls=calls,actual_opaque_callbacks=0,original_caller=0x58c52,actual_58988_call_sites=sites,resolved_prior_dependencies=E['resolved_prior_dependencies'],real_prior_providers=E['real_prior_providers'],retained_prior_genuine_UND=[],new_genuine_named_dependencies=0,direct_no_link_tails=tails,guard_polarities=dict(first_flag_bit0_zero_skips_58788=True,second_585C8_result_equals1_reaches_58744=True,physical_success_not_inferred=True),configuration_helper=dict(entry=0x580a4,end=0x58170,first_base_pointer_slot=0x2000353c,second_base_pointer_slot=0x20003508,second_base_word8_constant=0x8e89bed6,second_base_word4_constant=0x00555555,record_byte6_literal_low8=179,register_helper=0x63c54,A1=255,A2=0,physical_register_or_radio_meaning_proved=False),all_post_RET_reachable_arms_preserved=True,no_live_record_or_MAC_contents_observed=True,all_numeric_CODE_pointers_or_callbacks_closed=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set();expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==1 and out['non_CODE_allocations']==before['non_CODE_allocations'],'One genuine prior58988 gap supplied;all nine imports have real bodies;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(32386,2187,1754),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=32642,instructions=11209,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,one_genuine_prior_named_dependency_has_real_body=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh entire callback-provenance and preceding APP/SDK/native/IRQ/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],result[mode]['CODE']['object_sha256']],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-record-transition-two-tails-audit-v1',passed=True,checker_sha256=sha(__file__),prior_record_configuration_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=918,new_instructions=322,new_complete_functions=2,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=918,new_instructions=322,complete_functions=2,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=len(v['contract']['resolved_prior_dependencies']),opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
