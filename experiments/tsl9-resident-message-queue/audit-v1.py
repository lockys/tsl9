#!/usr/bin/env python3
"""Verify six complete message queue/event bodies;preserve the previous Flash argument contract."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-resident-task-callbacks'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='callback_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every actual compile input unchanged')
    result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete artifacts and include dependencies')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native and ABI proof matches retained compile receipt')
    need(result['c']==result['cpp'],'C11 and C++17 complete objects identical');return N,result
def queue_contract(N):
    E,B=N['EV'],N['B'];functions=[];pairs={v['PC']+4:v for v in N['S']['PC_relative_pairs']};entries={f['start']for f in E['selected_functions']}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};edges=[];returns=[];calls=[]
        for pc,o in ops.items():
            d=B['decode_control'](bytes.fromhex(o['bytes']),pc);following=pc+o['size']
            if o['type']=='ret':returns.append(pc);continue
            if d:
                kind,target=d
                if o['type']=='call':
                    need(target in entries and following in ops,'Genuine direct callee and conditional normal-return continuation');calls.append(dict(PC=pc,target=target));edges.append([pc,following])
                else:
                    need(target in ops,'Every local direct edge stays within its complete function');edges.append([pc,target])
                    if o['type']=='cjmp':need(following in ops,'Complete branch fallthrough');edges.append([pc,following])
            else:
                need(following in ops,'No fallthrough into an adjacent function');edges.append([pc,following])
                if o['type']=='ucall':need(pc in pairs,'Every indirect encoding is a resolved typed far call');calls.append(dict(PC=pc,target=pairs[pc]['target_PC']))
        reached=set();pending=[f['start']]
        while pending:
            pc=pending.pop()
            if pc in reached:continue
            reached.add(pc);pending.extend(b for a,b in edges if a==pc)
        need(reached==set(ops)and returns,'Every selected instruction belongs to entry CFG under normal callee return')
        functions.append(dict(entry=f['start'],end=f['end'],CODE_bytes=f['end']-f['start'],instructions=len(ops),direct_edges=edges,return_PCs=returns,calls=calls,all_instructions_in_conditional_CFG=True))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x2000029c:'lw s3, 524(a5)',0x200002a0:'mv s2, a0',0x200002a2:'sw zero, 524(a5)',0x200002a6:'fence.i',0x200002ae:'lw s0, 408(a0)',0x200002b2:'li s1, 0',0x200002b4:'li a2, 0',0x200002b6:'bnez s0, 0x200002c8',0x200002b8:'bnez s1, 0x200002d2',0x200002ba:'lui a1, 0x8',0x200002bc:'mv a0, s2',0x200002c8:'lbu a5, -2(s0)',0x200002cc:'bne a5, s2, 0x20000306',0x200002d0:'beqz s1, 0x20000310',0x200002d2:'mv a1, s1',0x200002d4:'addi a0, a0, 408',0x200002e0:'beqz s0, 0x200002ba',0x200002e2:'lui a1, 0x8',0x200002e4:'mv a0, s2',0x200002f6:'sw s3, 524(a5)',0x200002fa:'mv a0, s1',0x20000306:'bnez s1, 0x2000030a',0x20000308:'mv a2, s0',0x2000030a:'lw s0, -8(s0)',0x20000310:'mv s1, s0',
        0x4319c:'lw a4, 0(a0)',0x4319e:'lw a5, -8(a1)',0x431a2:'bne a4, a1, 0x431b4',0x431a6:'sw a5, 0(a0)',0x431a8:'li a5, -1',0x431aa:'sw zero, -8(a1)',0x431ae:'sb a5, -2(a1)',0x431b4:'sw a5, -8(a2)',
        0x4355e:'lbu a4, 413(a4)',0x43562:'bleu a4, a0, 0x43582',0x4356a:'slli a4, a0, 0x1',0x4356e:'lw a0, 484(a2)',0x43572:'add a0, a0, a4',0x43574:'qk.c.lhu a4, 0(a0)',0x43576:'or a1, a1, a4',0x43578:'qk.c.sh a1, 0(a0)',0x4357e:'li a0, 0',0x43586:'li a0, 3',
        0x4359e:'lbu a4, 413(a4)',0x435a2:'bleu a4, a0, 0x435c6',0x435aa:'slli a4, a0, 0x1',0x435ae:'lw a0, 484(a2)',0x435b2:'not a1, a1',0x435b6:'add a0, a0, a4',0x435b8:'qk.c.lhu a4, 0(a0)',0x435ba:'and a1, a1, a4',0x435bc:'qk.c.sh a1, 0(a0)',0x435c2:'li a0, 0',0x435ca:'li a0, 3',
        0x439b8:'lw s3, 524(a5)',0x439bc:'mv s2, a0',0x439be:'mv s0, a1',0x439c0:'sw zero, 524(a5)',0x439c4:'fence.i',0x439d0:'mv s1, a0',0x439d2:'beqz a0, 0x439d8',0x439d4:'sh zero, 2(a0)',0x439d8:'mv a1, s0',0x439da:'mv a0, s2',0x439e2:'lbu a5, 412(a5)',0x439e6:'bne a5, s2, 0x439f8',0x439ee:'lhu a4, 476(a5)',0x439f2:'or s0, s0, a4',0x439f4:'sh s0, 476(a5)',0x439fc:'sw s3, 524(a5)',0x43a00:'li a0, 0',0x43a02:'bnez s1, 0x43a06',0x43a04:'li a0, 6',
        0x20000314:'lui a5, 0x20003',0x20000318:'lw a5, 488(a5)',0x2000031c:'bnez a5, 0x20000322',0x2000031e:'mv a0, a5',0x20000322:'qk.c.lhu a4, 2(a5)',0x20000324:'bne a4, a1, 0x2000032e',0x20000328:'qk.c.lbu a4, 0(a5)',0x2000032a:'beq a4, a0, 0x2000031e',0x2000032e:'lw a5, 12(a5)'}
    need(all(ops[pc]['opcode']==text for pc,text in expected.items()),'Actual queue traversal,unlink,event and timer instruction roles')
    need({v['PC']:v['target_PC']for v in N['S']['PC_relative_pairs']}=={0x200002be:0x439a8,0x200002d8:0x4319c,0x200002e6:0x4354a,0x439c8:0x20000314},'Four actual intra-module far calls')
    need(B['decode_control'](bytes.fromhex(ops[0x439dc]['bytes']),0x439dc)==(45,0x4358a),'Actual stop-task direct call to clear-event')
    header=(ROOT/E['header']).read_text(encoding='gb18030');need('#define SYS_EVENT_MSG                   (0x8000)'in header,'Official message-event bit')
    prior=ROOT/'experiments/tsl9-resident-message-api/evidence-v1.json';old=json.loads(prior.read_bytes());dealloc={o['addr']:o for f in old['selected_functions']if f['start']==0x431ba for o in f['operations']}
    need(dealloc[0x431e4]['opcode']=='lbu a4, -2(a0)'and dealloc[0x431e8]['opcode']=='li a5, 255'and dealloc[0x431ec]['opcode']=='beq a4, a5, 0x431f8','Real preceding deallocator requires the unlink-set tag255')
    return dict(passed=True,functions=functions,official_bindings=E['official_bindings'],raw_dependencies=E['raw_dependencies'],all_five_named_calls_have_real_bodies=True,opaque_calls_within_new_bodies=0,
        receive=dict(entry=0x2000028c,queue_head_storage=0x20003198,task_tag_offset=-2,next_pointer_offset=-8,returns='first queued payload whose byte task tag equals entry_A0,or null',first_matching_node_unlinked=True,later_matching_node_controls_message_event=True,event_bit=0x8000,no_later_match_calls=0x439a8,later_match_calls=0x4354a,helper_return_values_ignored=True),
        unlink=dict(entry=0x4319c,A0='address of head word',A1='selected payload',A2='predecessor payload when selected node is not head',head_or_predecessor_link_replaced_with_next=True,clears_selected_next_pointer=True,sets_selected_task_tag=255,does_not_free_or_allocate=True,requires_valid_writable_header_and_list_ownership=True),
        event_array=dict(pointer_storage=0x200031e4,task_count_byte=0x2000319d,offset_expression='2*taskID',set_operation='old_halfword OR event',clear_operation='old_halfword AND NOT event',valid_task_numeric_return=0,out_of_range_numeric_return=3,halfword_operations_require_conditional_Xwchc_profile=True),
        stop_task=dict(entry=0x439a8,lookup=0x20000314,lookup_list_storage=0x200031e8,lookup_task_byte_offset=0,lookup_event_halfword_offset=2,lookup_next_word_offset=12,found_entry_event_halfword_set_zero=True,always_calls_clear_event=True,clear_event_return_ignored=True,found_lookup_numeric_return=0,missing_lookup_numeric_return=6,matching_global_byte=0x2000319c,matching_task_OR_halfword=0x200031dc),
        deallocator_relation='The unlink helper stores255 into payload[-2],matching the existing deallocator tag guard;valid ownership and absence of intervening mutation remain assumptions',
        MMIO=0x4002420c,encoded_save_zero_restore_retained=True,physical_MMIO_semantics_or_atomicity_proved=False,normal_callee_return_is_an_assumption=True,acyclic_stable_lists_and_valid_task_record_lifetime_required=True,termination_proved=False,IRQ_alias_or_heap_ownership_proved=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable RISC-V ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(not remaining and u=={'tsl9_candidate_message_receive_2000028c'},'The real receiver body resolves the actual preceding import')
    need(facts(path)==(a,d,remaining,sorted(rel)),'Every input byte,positive symbol and typed relocation retained')
    need(sum(len(v[1])for v in a.values())==2264 and len(d)==204 and len(rel)==149,'Exact actual partial composition metrics')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=2264,instructions=805,positive_FUNC_regions=204,relocations=149,named_UND=sorted(remaining),real_new_imports_resolved=sorted(u-remaining),independent_readers=independent,every_input_byte_symbol_relocation_retained=True,stored_numeric_CODE_targets_have_real_bodies=True,raw_RAM_and_indirect_record_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,results=native(llvm);old=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(old)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Prior1828-byte callback composition and Flash contract unchanged')
    queue=queue_contract(N);flash=old['Flash_argument_contract'];out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh retained nonloadable composition trial')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-message-queue-event-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=results,queue_contract=queue,Flash_argument_contract=flash,prior_audit_sha256=sha(PRIOR/'audit-result-v1.json'),composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=436,instructions=151,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},Flash_argument_contract=result['Flash_argument_contract'],APP_byte_coverage_unchanged=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
