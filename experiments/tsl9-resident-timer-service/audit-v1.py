#!/usr/bin/env python3
"""Verify the real scheduler timer callee,deadline arithmetic and providers without execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-scheduler'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='registration_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every actual compile input unchanged');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete actual object and include inventories')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh independent native and ABI readers match retained receipt')
    need(result['c']==result['cpp'],'Actual complete C11/C++17 objects identical');return N,result
def timer_contract(N,previous):
    E,B=N['EV'],N['B'];f=E['selected_functions'][0];ops={o['addr']:o for o in f['operations']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};named={int(k)for k in E['target_names']};edges=[];returns=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']=='ret':returns.append(pc);continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in named and following in ops,'Genuine direct provider and conditional normal return');calls.append(dict(PC=pc,target=target));edges.append([pc,following])
            else:
                need(target in ops,'All local branches stay in complete timer body');edges.append([pc,target])
                if o['type']=='cjmp':need(following in ops,'Whole local branch fallthrough');edges.append([pc,following])
        else:
            need(following in ops,'No fallthrough into adjacent independent entry');edges.append([pc,following])
            if o['type']=='ucall':calls.append(dict(PC=pc,target=pairs[pc]['target_PC']if pc in pairs else None))
    pending=[f['start']];seen=set()
    while pending:
        pc=pending.pop()
        if pc in seen:continue
        seen.add(pc);pending.extend(b for a,b in edges if a==pc)
    need(seen==set(ops)and returns==[0x200005da],'Complete103-instruction timer CFG with shared return')
    need(calls==[dict(PC=0x20000550,target=0x20000110),dict(PC=0x20000560,target=None),dict(PC=0x20000588,target=0x4354a)],'One real free provider,one opaque clock callback and one real event provider')
    expected={0x20000504:'lw s0, 488(s1)',0x20000518:'beqz s0, 0x200005c4',0x20000526:'li s7, 0',0x2000052c:'lui s6, 0x1c9c',0x20000530:'addi s4, s4, 492',0x20000534:'addi s2, s2, 412',0x20000538:'addi s3, s3, 564',0x2000053c:'qk.c.lhu a5, 2(s0)',0x2000053e:'bnez a5, 0x2000055c',0x20000540:'lw a5, 12(s0)',0x20000546:'sw a5, 488(s1)',0x2000054a:'lw s8, 12(s0)',0x2000054e:'mv a0, s0',0x20000552:'mv s0, s8',0x20000556:'sw a5, 12(s7)',0x2000055c:'lw a5, 480(s5)',0x20000560:'jalr a5',0x20000562:'lw a5, 8(s0)',0x20000564:'sub a4, a0, a5',0x20000568:'bleu a5, a0, 0x20000574',0x2000056c:'lw a4, 4(s3)',0x20000570:'sub a4, a4, a5',0x20000572:'add a4, a4, a0',0x20000574:'addi a3, s6, 895',0x20000578:'bltu a3, a4, 0x200005ec',0x2000057c:'sw zero, 16(s2)',0x20000580:'qk.c.lhu a1, 2(s0)',0x20000582:'qk.c.lbu a0, 0(s0)',0x2000058c:'lw a5, 4(s0)',0x2000058e:'lw a4, 12(s0)',0x20000590:'beqz a5, 0x200005dc',0x20000592:'lw a1, 8(s0)',0x20000594:'lw a2, 4(s3)',0x20000598:'add a5, a5, a1',0x2000059a:'mv a3, a5',0x2000059c:'bltu a5, a1, 0x200005a4',0x200005a0:'bltu a5, a2, 0x200005a8',0x200005a4:'sub a3, a5, a2',0x200005a8:'sw a3, 8(s0)',0x200005aa:'mv s7, s0',0x200005ac:'mv s0, a4',0x200005ae:'bnez s0, 0x2000053c',0x200005b8:'lw a4, 16(a5)',0x200005ba:'li a3, 1',0x200005bc:'bleu a4, a3, 0x20000614',0x200005c0:'addi a4, a4, -1',0x200005c2:'sw a4, 16(a5)',0x200005dc:'bnez s7, 0x200005e6',0x200005e0:'sw a4, 488(s1)',0x200005e6:'sw a4, 12(s7)',0x200005ec:'lw a4, 40(s4)',0x200005f0:'beqz a4, 0x20000606',0x200005f2:'bltu a5, a0, 0x2000060c',0x200005f6:'sub a0, a5, a0',0x200005fa:'lw a5, 16(s2)',0x200005fe:'bleu a5, a0, 0x20000606',0x20000602:'sw a0, 16(s2)',0x20000606:'mv s7, s0',0x20000608:'lw s0, 12(s0)',0x2000060c:'lw a4, 4(s3)',0x20000610:'add a5, a5, a4',0x20000614:'sw zero, 16(a5)'}
    need(all(ops[pc]['opcode']==v for pc,v in expected.items()),'Exact timer-node accesses,removal,rearm,wrap threshold and cached-delay instructions')
    threshold=(0x1c9c<<12)+895;need(threshold==29999999,'Actual numeric due-threshold constant;units unproved')
    changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(changes=={0x200004fa:-48,0x200005d8:48},'Actual48-byte affine own frame')
    pending=[(f['start'],0)];depths={}
    while pending:
        pc,before=pending.pop()
        if pc in depths:need(depths[pc]==before,'Consistent own-frame position at CFG joins');continue
        depths[pc]=before;after=before+changes.get(pc,0);need(after in [-48,0],'Only original48-byte local frame positions')
        if pc in returns:need(after==0,'Own frame balanced at common return')
        pending.extend((b,after)for a,b in edges if a==pc)
    need(set(depths)==set(ops),'All103 timer instructions covered by static own-frame proof')
    pe=json.loads((PRIOR/'evidence-v1.json').read_bytes());main={o['addr']:o for f in pe['selected_functions']for o in f['operations']}
    caller={0x20000866:'lw a5, 480(a5)',0x2000086a:'beqz a5, 0x2000094e',0x2000086c:'lw a5, 4(s1)',0x2000086e:'sw a5, 16(s4)'};need(all(main[pc]['opcode']==v for pc,v in caller.items()),'Actual known main caller checks clock pointer and initializes cached delay')
    need(B['decode_control'](bytes.fromhex(main[0x20000872]['bytes']),0x20000872)==(45,0x200004fa)and B['decode_control'](bytes.fromhex(main[0x200008be]['bytes']),0x200008be)==(45,0x2000061a),'Real caller and independent next entry bound the selected timer body')
    q=json.loads((ROOT/'experiments/tsl9-resident-message-queue/evidence-v1.json').read_bytes());qops={o['addr']:o for f in q['selected_functions']for o in f['operations']};need(qops[0x439d4]['opcode']=='sh zero, 2(a0)','Existing stop_task marks the same timer event halfword zero')
    need(previous['scheduler_contract']['own_frame_bytes']==32,'Known caller own frame retained')
    return dict(passed=True,static_only=True,concrete_machine_or_memory_simulated=False,complete_range=[f['start'],f['end']],instructions=103,direct_edges=edges,return_PCs=returns,calls=calls,
        timer_head=0x200031e8,node_accesses=dict(task_byte=0,event_halfword=2,interval_word=4,deadline_word=8,next_word=12),minimum_valid_node_bytes=16,
        clock_callback_storage=0x200031e0,clock_callback_null_guard_within_body=False,known_main_caller_checks_pointer_before_call=True,caller_pointer_stability_still_required=True,wrap_word=0x20003238,clock_units_or_range_proved=False,
        elapsed_expression='now>=deadline ? now-deadline : M-deadline+now (u32)',due_if_unsigned_elapsed_le=threshold,
        due_event_call=dict(target=0x4354a,A0='fresh node task byte',A1='fresh node event halfword',return_value_used=False),
        repeat_expression='s=(fresh_deadline+interval) mod2^32;store s-M mod2^32 if s<fresh_deadline or s>=M,otherwise s',repeat_updates_per_traversed_node=1,general_modulo_or_multi_period_catchup_proved=False,
        unlink_and_free='zero event or zero interval after a due event unlinks head/predecessor,reads next into S8,then frees the node through real20000110',stop_task_zero_event_is_collected_only_when_this_service_runs=True,
        cached_delay_word=0x200031ac,future_delay_update_requires_nonnull_idleCB_at=0x20003214,future_delay_expression='deadline>=now ? deadline-now : deadline+M-now (u32)',cached_delay_replaced_only_when_candidate_is_smaller=True,post_nonempty_traversal='cache<=1 ?0:cache-1',initially_empty_list_returns_without_postpass=True,
        own_frame_bytes=48,own_frame_balanced_at_return=True,known_main_plus_timer_own_frame_bytes=80,callee_and_global_IRQ_stack_budget_proved=False,opaque_transfers=E['opaque_transfers'],raw_dependencies=E['raw_dependencies'],
        requires_valid_stable_acyclic_list_node_lifetime_and_normal_callee_returns=True,clock_callback_effects_on_nodes_or_globals_bounded=False,termination_proved=False,physical_atomicity_proved=False,installed_ROM_identity_proved=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        r=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,r
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_63dd0','tsl9_candidate_external_ram_2000061a','tsl9_candidate_external_ram_20002610'}and len(u)==6 and facts(path)==(a,d,remaining,sorted(rel)),'Every input byte,symbol and relocation retained;real timer/free/event providers resolve three imports')
    need(sum(len(v[1])for v in a.values())==3038 and len(d)==279 and len(rel)==205,'Exact3038-byte composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=3038,instructions=1074,positive_FUNC_regions=279,relocations=205,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,real_scheduler_timer_import_resolved=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm)
    need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh2750-byte scheduler,binding,registration,layout and Flash proofs retained')
    contract=timer_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh nonloadable scheduler composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ composition objects identical')
    return dict(schema='TSL9-public-SDK-timer-service-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,timer_contract=contract,prior_scheduler_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_bytes=2750,prior_scheduler_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable registration receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=288,instructions=103,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},startup_completed_proved=False,physical_atomicity_proved=False,APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
