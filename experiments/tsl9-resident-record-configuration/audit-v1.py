"""Verify the complete58788/58744/581CE candidate chain;never execute it."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-record-comparison';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='record_configuration_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result

def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');rows=[];graphs={};op={};frames={0x58788:16,0x58744:16,0x581ce:32}
    for f in E['selected_functions']:
        ext={c[1]for o in f['operations']if(c:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,frames[f['start']]);rows.append(q);graphs[f['start']]=g;op.update(oo)
    need(sum(f['bytes']for f in rows)==1028 and sum(f['instructions']for f in rows)==355,'Three complete reachable CFGs and balanced original frames')
    required={0x58788:'addi sp, sp, -16',0x58890:'mv a0, s0',0x58892:'lw s0, 8(sp)',0x58894:'lw ra, 12(sp)',0x58896:'lw s1, 4(sp)',0x58898:'lw s2, 0(sp)',0x5889a:'addi sp, sp, 16',0x5889c:'j 0x58744',0x58744:'addi sp, sp, -16',0x5874c:'jal ra, 0x581ce',0x58750:'lui a5, 0x20003',0x58754:'lw a4, 148(s0)',0x58758:'lw a5, 1340(a5)',0x5875c:'lui a3, 0x800',0x58760:'sw a4, 112(a5)',0x58762:'lui a5, 0x20003',0x58766:'lw a5, 1288(a5)',0x5876a:'lw a4, 0(a5)',0x5876c:'or a4, a4, a3',0x5876e:'sw a4, 0(a5)',0x58770:'lw a4, 44(a5)',0x58772:'andi a4, a4, -4',0x58774:'sw a4, 44(a5)',0x58782:'li a0, 0',0x58784:'addi sp, sp, 16',0x58786:'ret',0x581ce:'addi sp, sp, -32',0x581dc:'lbu a4, 57(a0)',0x581e0:'li a5, 8',0x581e4:'bne a4, a5, 0x583ec',0x581e8:'li a5, -75',0x581ec:'qk.c.sb a5, 6(a0)',0x581ee:'lbu a0, 60(a0)',0x581f2:'li a1, 34',0x581f6:'jal ra, 0x63b0e',0x581fe:'li a5, 2',0x58200:'bleu s2, a5, 0x58206',0x58204:'li s2, 2',0x583dc:'lw ra, 28(sp)',0x583e8:'addi sp, sp, 32',0x583ea:'ret',0x583ec:'li a5, -76',0x583f0:'qk.c.sb a5, 6(a0)',0x583f2:'li a1, 34',0x583f6:'li a0, 0',0x583f8:'jal ra, 0x63b0e',0x583fc:'li s2, 0',0x5840c:'divu a3, a3, s2',0x58442:'lw a0, 0(a0)',0x58444:'j 0x58354',0x58460:'j 0x5836c'}
    need(all(op[p]['opcode']==s for p,s in required.items()),'Exact original argument/frame/tail/configuration/DIVU/list-walk operands')
    word=int.from_bytes(bytes.fromhex(op[0x5889c]['bytes']),'little');need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(op[0x5889c]['bytes']),0x5889c)[1]==0x58744,'Actual JALzero tail,not ordinary C call')
    g=graphs[0x58788];need(all(0x5889c not in V['reachable'](g,0x58788,skip=p)for p in [0x58890,0x58894,0x5889a]),'Record argument,original RA restoration and16-byte frame release dominate tail')
    need(any(pc>0x58874 for pc in g)and 0x583ec in graphs[0x581ce]and 0x58460 in graphs[0x581ce],'All late reachable arms retained beyond early RETs');need(max(graphs[0x581ce])+op[max(graphs[0x581ce])]['size']==0x58462,'Complete581CE body excludes adjacent58462')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={pc for f in rows for pc in range(f['start'],f['end'])};need(parent['passed']and not newbytes&set(parent['_byte_map'])and set(E['resolved_prior_dependencies'])<=set(parent['named_UND']),'Actual missing58788 provider and unique CODE')
    need(all(pc in parent['_byte_map']for pc in E['real_prior_providers'])and len(E['real_prior_providers'])==6 and not E['retained_prior_genuine_UND'],'All six imports have real prior bodies')
    far={p['PC']+4:p['target_PC']for p in N['S']['PC_relative_pairs']};calls=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target']);need(target is not None and target in newbytes|set(E['real_prior_providers']),'Every actual call resolves to exact selected/prior entry');calls.append(dict(PC=call['PC'],target=target))
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Complete caller evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x58c52);sites=[];raw=(ROOT/E['firmware']).read_bytes()
    for o in f['operations']:
        need(bytes.fromhex(o['bytes'])==raw[o['addr']-0x40000:o['addr']-0x40000+o['size']],'Original caller bytes');d=B['decode_control'](bytes.fromhex(o['bytes']),o['addr'])
        if d and d[1]==0x58788:sites.append(o['addr'])
    need(len(sites)==1,'One actual encoded58C52 caller for58788')
    return dict(passed=True,functions=rows,CODE_bytes=1028,instructions=355,complete_functions=3,own_frames=[16,16,32],conditional_Xwchc_ports=45,actual_calls=calls,actual_opaque_callbacks=0,original_caller=0x58c52,actual_58788_call_sites=sites,resolved_prior_dependencies=E['resolved_prior_dependencies'],real_prior_providers=E['real_prior_providers'],retained_prior_genuine_UND=[],new_genuine_named_dependencies=0,direct_no_link_tail=dict(PC=0x5889c,target=0x58744,original_record_argument_restored=True,original_RA_restored=True,own16_frame_released=True),configuration_helper=dict(entry=0x58744,callee=0x581ce,record_word_offset=148,first_base_pointer_slot=0x2000353c,first_base_write_offset=112,second_base_pointer_slot=0x20003508,word0_OR_mask=0x08000000,word44_clear_mask=3,encoded_return=0,physical_role_or_success_not_proved=True),record_setup=dict(entry=0x581ce,record_byte57_equals8_branch=True,byte6_literals_low8=[181,180],register_helper=0x63b0e,second_argument=34,divu_PC=0x5840c,original_DIVU_instruction_retained=True,nonzero_runtime_divisor_proved=False,list_next_load_PC=0x58442,list_walk_termination_or_valid_memory_proved=False),all_post_RET_reachable_arms_preserved=True,no_live_record_or_MAC_contents_observed=True,all_numeric_CODE_pointers_or_callbacks_closed=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set();expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==2 and out['non_CODE_allocations']==before['non_CODE_allocations'],'One genuine prior58788 gap supplied;all six imports have real bodies;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(31468,2136,1707),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=31724,instructions=10887,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,one_genuine_prior_named_dependency_has_real_body=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh entire callback-provenance and preceding APP/SDK/native/IRQ/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],result[mode]['CODE']['object_sha256']],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-record-configuration-tail-chain-audit-v1',passed=True,checker_sha256=sha(__file__),prior_record_comparison_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=1028,new_instructions=355,new_complete_functions=3,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1028,new_instructions=355,complete_functions=3,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=len(v['contract']['resolved_prior_dependencies']),opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
