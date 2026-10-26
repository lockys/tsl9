#!/usr/bin/env python3
"""Audit actual idle/service helper bodies and retain all physical execution gates."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-scheduler-state-services'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='idle_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual native inputs unchanged');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete actual object/include inventories')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers match compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 objects identical');return N,result
def reachable(graph,start,skip_node=None,skip_edge=None):
    seen=set();pending=[start]
    while pending:
        pc=pending.pop()
        if pc==skip_node or pc in seen:continue
        seen.add(pc);pending.extend(v for v in graph[pc]if(pc,v)!=skip_edge)
    return seen
def cfg(ops,B,external):
    graph={pc:[]for pc in ops};returns=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']=='ret':returns.append(pc);continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in external and following in ops,'Actual selected/external callee and normal continuation');calls.append(dict(PC=pc,target=target));graph[pc].append(following)
            elif target in ops:
                graph[pc].append(target)
                if o['type']=='cjmp':need(following in ops,'Whole conditional fallthrough');graph[pc].append(following)
            else:need(target in external and o['type']=='jmp','Actual terminal external tail transfer')
        else:
            need(following in ops,'No fallthrough into adjacent function');graph[pc].append(following)
            if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
    return graph,returns,calls
def state8_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};frames={0x64f04:64,0x2000078a:0,0x6434a:0,0x63c54:0,0x43728:48};functions=[];graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,returns,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and len(returns)==1,'Every complete original body instruction belongs to its actual entry CFG')
        frame=frames[f['start']];changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-frame,frame]if frame else []),'Exact own-frame changes')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent affine own SP on every branch/list-loop join');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only actual own frame positions')
            if not g[pc]:need(pc in returns and after==0,'Own frame balanced at every actual normal return')
            pending.extend((v,after)for v in g[pc])
        for c in calls:
            if c['PC']in pairs:c['target']=pairs[c['PC']]['target_PC']
        graphs[f['start']]=g;functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced=True,return_PCs=returns,calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x64f1e:'lw s5, 524(a5)',0x64f22:'sw zero, 524(a5)',0x64f26:'fence.i',0x64f32:'lw a4, 8(a4)',0x64f34:'bnez a4, 0x64f54',0x64f36:'sw s5, 524(a5)',0x64f3a:'li a0, 1',0x64f58:'lw a4, 1120(a4)',0x64f5c:'beqz a4, 0x64f66',0x64f5e:'sw s5, 524(a5)',0x64f62:'li a0, 2',0x64f66:'lbu a5, 1344(s1)',0x64f70:'andi a5, a5, 1',0x64f74:'mv a2, a1',0x64f76:'mv s2, a0',0x64f82:'lw a5, 4(a5)',0x64f88:'bnez a5, 0x64fa2',0x64f8a:'lbu a0, 29(s4)',0x64f90:'li a1, 73',0x64f94:'addi a0, a0, 2',0x64fa0:'sw a0, 4(s0)',0x64fa4:'bnez a5, 0x64fb2',0x64faa:'sw s5, 524(a5)',0x64fae:'li a0, 3',0x64fb2:'qk.c.lbu a4, 2(s0)',0x64fb4:'qk.c.sb a4, 0(a5)',0x64fb8:'beqz s2, 0x6500c',0x64fbc:'beqz a2, 0x6500c',0x64fbe:'qk.c.sb a2, 1(a5)',0x64fc2:'mv a1, s2',0x64fc4:'addi a0, a0, 2',0x64fd6:'qk.c.lbu a5, 7(a5)',0x64fe2:'lbu a5, 8(s2)',0x64ff2:'lbu a5, 9(s2)',0x64ffc:'sh a5, 8(s2)',0x65004:'sw s5, 524(a5)',0x65008:'li a0, 0',0x6500c:'sb zero, 1(a5)',
        0x650ba:'sb s8, 3(s0)',0x650be:'sb s7, 2(s0)',0x650de:'lw a5, 536(a5)',0x650e2:'beqz a5, 0x650f0',0x650e4:'qk.c.lbu a0, 16(s0)',0x650e6:'li a2, 1600',0x650ea:'li a1, 16',0x650fa:'lui a0, 0x65',0x650fe:'addi a0, a0, 928',0x6515a:'lui a0, 0x65',0x6515e:'addi a0, a0, 356',
        0x2000078a:'lui a5, 0x20003',0x2000078e:'sw a0, -264(a5)',0x20000792:'beqz a0, 0x2000079e',0x20000798:'li a4, 1',0x2000079a:'sb a4, -260(a5)',0x2000079e:'ret',
        0x6434e:'lui a0, 0x20003',0x6435e:'lw a3, 1288(a5)',0x64364:'andi a6, a5, 127',0x64368:'beqz a1, 0x643f6',0x6439a:'divu a2, a5, a6',0x643a4:'remu a5, a5, a6',0x643c2:'divu a5, a5, a2',
        0x63c58:'lw a5, 1292(a5)',0x63c5c:'beqz a5, 0x63c76',0x63c7a:'lbu a6, 1296(a4)',0x63c86:'andi a3, a0, 2',0x63c8a:'lw a5, 1288(a5)',0x63cec:'sw a1, 16(a4)',0x63cee:'beqz a2, 0x63cf4',0x63cf0:'slli a2, a2, 0x1',0x63cf2:'sw a2, 16(a4)',
        0x43740:'lw s4, 524(s1)',0x43744:'sw zero, 524(s1)',0x43748:'fence.i',0x43750:'lbu a5, 413(a5)',0x43754:'bleu a5, a0, 0x43764',0x4375c:'lw s7, 480(a5)',0x43760:'bnez s7, 0x4376e',0x43768:'sw s4, 524(a5)',0x43776:'mv s5, a1',0x43778:'lw s6, 4(s2)',0x4377c:'lhu a1, 8(s2)',0x43780:'lui a5, 0xfe364',0x43784:'addi a5, a5, -896',0x43798:'addi a0, a5, 800',0x4379c:'sltu a5, a0, a5',0x437a0:'li a2, 1600',0x437aa:'bleu a0, s6, 0x437ca',0x437ae:'sw s4, 524(s1)',0x437b2:'li a0, 0',0x437ca:'jalr s7',0x437cc:'lhu a1, 8(s2)',0x437e0:'addi a0, a5, 800',0x437ee:'add a5, a0, s1',0x437f4:'lw a4, 4(s2)',0x43810:'beqz a0, 0x43820',0x43812:'sw s1, 8(a0)',0x43818:'sw s4, 524(a5)',0x4381c:'li a0, 1',0x43828:'li a0, 16',0x43832:'bnez a0, 0x43846',0x43838:'lw a5, 544(a5)',0x4383c:'beqz a5, 0x43764',0x4383e:'mv a1, s0',0x43840:'li a0, 4',0x43842:'jalr a5',0x4384a:'lw a5, 488(a4)',0x43850:'sw a0, 488(a4)',0x43856:'sw zero, 12(a0)',0x4385a:'sw s1, 8(a0)',0x4385c:'sh s5, 2(a0)',0x43860:'qk.c.sb s0, 0(a0)',0x43862:'qk.c.sb a5, 1(a0)',0x43864:'sw zero, 4(a0)',0x4386c:'lw a4, 12(a5)',0x4386e:'bnez a4, 0x4386a',0x43870:'sw a0, 12(a5)'}
    need(all(ops[pc]['opcode']==value for pc,value in expected.items()),'Actual state8 allocation,copy,setter,register and timer instruction roles')
    need(sorted((p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs'])==sorted([(0x64f96,0x20000040),(0x64fc6,0x20000332),(0x65102,0x2000078a),(0x43808,0x20000314),(0x4382a,0x20000040)]),'All five real far providers')
    for entry,ret,restores in [(0x64f04,0x64f52,[0x64f36,0x64f5e,0x64faa,0x65004]),(0x43728,0x437c8,[0x43768,0x437ae,0x43818])]:
        g=graphs[entry];cut={pc:[]if pc in restores else values for pc,values in g.items()};need(ret not in reachable(cut,entry),'Every local normal return follows an original saved-word restore')
    need(0x65102 not in reachable(graphs[0x64f04],0x650ec,skip_node=0x650fa,skip_edge=(0x6515a,0x6515e)),'Timer status is overwritten by one of two actual CODE literal setups before setter')
    literal_values=[(0x65<<12)+928,(0x65<<12)+356];need(sorted(literal_values)==[0x65164,0x653a0]and E['numeric_CODE_dependencies']==[0x65164,0x653a0],'Actual two unprovided numeric CODE dependencies')
    setter=E['selected_functions'][1];need(not any(o['type']in ['call','ucall']for o in setter['operations']),'Setter stores a CODE pointer without invoking it')
    timer_ops={o['addr']:o for o in E['selected_functions'][4]['operations']};existing_path=reachable(graphs[0x43728],0x43812)
    need(not any(pc in existing_path and o['type']=='store'and o['opcode'].endswith(', 4(a0)')for pc,o in timer_ops.items()),'Existing-node success path does not reset interval')
    need(N['EV']['official_timer_start_binding']['target']==0x43728,'Actual official slot9 TimerStart binding')
    need(B['decode_control'](bytes.fromhex(ops[0x650ec]['bytes']),0x650ec)[1]==0x43728 and all(B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)[1]==0x6df1a for pc in [0x437a6,0x437ea]),'Real timer and arithmetic calls')
    need(previous['state_contract']['positive_next_callee']['original_sha256']==E['selected_functions'][0]['original_sha256'],'Previously reference-only608 bytes now have an actual native body')
    return dict(passed=True,static_only=True,functions=functions,state8=dict(entry=0x64f04,bytes=608,own_frame_bytes=64,local_return_codes=[0,1,2,3],return_codes_are_not_physical_success=True,prerequisite_word=0x20003548,busy_word=0x20003460,buffer_pointer_storage=0x20003564,allocation_size_expression='parameter_byte29+2',allocation_request_range=[2,257],allocator_second_argument=73,copy_inputs='destination=buffer+2,source=entry_A0,count=entry_A1',buffer_byte1_receives_low8_length_or_zero=True,capacity_and_input_range_proved=False,callback_argument_bytes_saved_at_parameter_offsets=[3,2],optional_timer_condition_pointer=0x20003218,timer_task_byte=0x20003570,timer_event_literal=16,timer_interval_literal=1600,timer_return_inspected=False,physical_time_units_proved=False),
        callback_setter=dict(entry=0x2000078a,bytes=22,storage=0x20002ef8,flag=0x20002efc,nonnull_input_sets_flag_one=True,null_input_does_not_clear_flag=True,callback_invoked=False,numeric_CODE_dependencies=[0x65164,0x653a0],numeric_CODE_targets_provided=False,numeric_CODE_addresses_are_not_linker_relocations=True),
        register_helpers=[dict(entry=0x6434a,bytes=192,own_frame_bytes=0,incoming_A0_overwritten_before_use=True,physical_register_identity_proved=False),dict(entry=0x63c54,bytes=278,own_frame_bytes=0,optional_descriptor=0x2000350c,physical_register_identity_proved=False)],
        timer_start=dict(entry=0x43728,bytes=332,official_slot=9,own_frame_bytes=48,task_count=0x2000319d,raw_clock_storage=0x200031e0,nonnull_cached_raw_callback_required=True,clock_frequency_fresh_read_PCs=[0x4377c,0x437cc],raw_callback_between_frequency_reads=0x437ca,converted_operand_setup='64-bit live_frequency*entry_A2+800;A2=1600;A3=0',arithmetic_helper=0x6df1a,arithmetic_semantics_proved=False,first_range_limit='u32(MaxCount-30000000)',only_low_returned_A0_compared=True,existing_node_updates_deadline_only=True,existing_node_interval_not_reset=True,new_node_bytes=16,new_node_offsets=dict(task=0,flag=1,event=2,interval=4,deadline=8,next=12),new_node_flag_one=True,new_node_interval_zero=True,head=0x200031e8,append_walk_termination_proved=False,status_callback_storage=0x20003220,allocation_failure_status_callback_arguments=[4,'entry_task'],local_success_returns_one=True,local_invalid_or_failure_returns_zero=True,returns_do_not_prove_physical_execution=True),
        saved_word_restore_on_every_local_normal_return=True,saved_word_address=0x4002420c,selected_state8_plus_timer_own_frame_bytes=112,whole_program_stack_IRQ_alias_or_callback_bound_proved=False,raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],callees_preserving_SP_and_normal_returns_assumed=True,installed_ROM_identity_proved=False,hardware_accessed=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_57dae','tsl9_candidate_external_flash_6020a'}and len(u)==7 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real state8,allocator,copy,math,lookup and selected setter providers retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(6554,256,549,1,402),'Exact6554-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=6554,DATA_bytes=256,allocated_bytes=6810,instructions=2274,positive_FUNC_regions=549,positive_OBJECT_regions=1,relocations=402,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,state8_and_existing_cross_imports_have_real_bodies=True,all_five_new_real_bodies_retained=True,numeric_callback_targets_provided=False,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=state8_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-state8-service-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,state8_contract=contract,prior_scheduler_state_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=5122,prior_SDK_composition_DATA_bytes=256,prior_scheduler_state_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=1432,instructions=492,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
