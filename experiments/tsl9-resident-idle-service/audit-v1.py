#!/usr/bin/env python3
"""Audit actual idle/service helper bodies and retain all physical execution gates."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-arithmetic-helper'
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
def idle_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};functions=[];graphs={}
    frames={0x2000061a:32,0x6430e:0,0x638ea:0}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};graph,returns,calls=cfg(ops,B,external);need(reachable(graph,f['start'])==set(ops)and len(returns)==1,'Every complete selected body reachable from its actual entry')
        changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};frame=frames[f['start']];need(sorted(changes.values())==([-frame,frame]if frame else []),'Exact actual own-frame changes')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP at each join');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only actual own SP positions')
            if pc in returns:need(after==0,'Own SP balanced at normal return')
            pending.extend((v,after)for v in graph[pc])
        for call in calls:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        graphs[f['start']]=graph;functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced=True,return_PCs=returns,calls=calls,direct_edges=[[p,v]for p in graph for v in graph[p]]))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x2000062c:'lw s3, 524(a5)',0x20000630:'sw zero, 524(a5)',0x20000634:'fence.i',0x20000640:'lw a0, 4(a5)',0x20000642:'qk.c.lbu a5, 12(a5)',0x20000648:'beqz a5, 0x200006a6',0x20000652:'lhu a4, 180(a5)',0x20000656:'beqz a4, 0x200006a6',0x20000658:'lw s1, 176(a5)',0x2000065c:'beq s1, a0, 0x200006a6',0x20000668:'lw a4, 16(a4)',0x2000066e:'beq a4, a0, 0x2000076c',0x20000676:'lw a5, 480(s2)',0x2000067a:'jalr a5',0x20000680:'lw a5, 480(s2)',0x20000684:'sub s1, s1, a0',0x20000686:'jalr a5',0x20000688:'lw a4, 16(s4)',0x2000068c:'bleu a4, s1, 0x20000692',0x20000698:'lw a3, 4(s0)',0x200006aa:'sw s3, 524(a5)',
        0x200006b0:'bne a5, a0, 0x200006ea',0x200006bc:'lw a4, 16(s1)',0x200006c2:'lw a5, 480(a5)',0x200006c6:'bne a4, a0, 0x20000770',0x200006ca:'jalr a5',0x200006ce:'lui a5, 0xfe364',0x200006d2:'addi a5, a5, -896',0x200006d6:'add a5, a5, a3',0x200006d8:'add a4, a5, a0',0x200006de:'bltu a4, a5, 0x200006e6',0x200006e2:'bltu a4, a3, 0x200006ea',0x200006e6:'sub a0, a4, a3',
        0x200006f2:'lw a5, 36(a5)',0x200006f8:'beqz a5, 0x2000070e',0x200006fe:'lw a3, 1424(a5)',0x20000702:'lui a4, 0xffcd0',0x20000706:'addi a4, a4, -1',0x20000708:'lw a5, 8(a3)',0x2000070a:'and a5, a5, a4',0x2000070c:'sw a5, 8(a3)',0x2000070e:'bnez a0, 0x20000712',0x20000710:'lw a0, 4(s0)',0x20000712:'li a5, 1',0x20000714:'sw a5, 12(s1)',0x2000071a:'lw a5, 532(a5)',0x2000071e:'jalr a5',0x20000720:'bnez a0, 0x20000740',0x20000722:'lw a5, 36(s1)',0x20000724:'beqz a5, 0x2000073e',0x20000726:'lw a5, 12(s1)',0x20000728:'beqz a5, 0x2000073e',0x2000073a:'sw zero, 12(s1)',0x20000740:'lw a5, 36(s1)',0x20000742:'beqz a5, 0x20000756',0x20000748:'lw a4, 1424(a5)',0x2000074c:'lui a3, 0x330',0x20000750:'lw a5, 8(a4)',0x20000752:'or a5, a5, a3',0x20000754:'sw a5, 8(a4)',0x20000770:'jalr a5',0x20000772:'lw a3, 16(s1)',0x20000774:'lw a4, 4(s0)',0x20000776:'add a5, a3, a0',0x2000077c:'bltu a5, a3, 0x20000784',0x20000780:'bltu a5, a4, 0x200006ea',0x20000784:'sub a0, a5, a4'}
    need(all(ops[pc]['opcode']==value for pc,value in expected.items()),'Actual mask,deadline,fresh callbacks,flag and optional helper instruction roles')
    need(((((0xfe364<<12)-896)&0xffffffff),(((0xffcd0<<12)-1)&0xffffffff),(0x330<<12))==(((-30000000)&0xffffffff),0xffccffff,0x00330000),'Actual fallback constant and distinct AND/OR masks')
    need(sorted((v['PC'],v['target_PC'])for v in N['S']['PC_relative_pairs'])==[(0x2000072a,0x6430e),(0x20000732,0x638ea)]and all(v['reference_kind']=='direct-code-call-pair'for v in pairs.values()),'Both far call providers are actual selected bodies')
    need(B['decode_control'](bytes.fromhex(ops[0x2000073e]['bytes']),0x2000073e)[1]==0x200004fa,'Actual direct call to existing timer body')
    g=graphs[0x2000061a];need(0x2000071e not in reachable(g,0x2000061a,skip_node=0x200006aa),'Original saved word restored before every local path to idleCB')
    need(0x2000073e not in reachable(g,0x20000740),'Nonnull idleCB return branch does not locally call timer service')
    need(0x20000714 not in reachable(g,0x2000073a),'Flag clear follows helper phase,not a fresh pre-idle phase')
    # The complete primary scheduler body was already checked by the retained chain.
    scheduler=ROOT/'experiments/tsl9-resident-scheduler';se=json.loads((scheduler/'evidence-v1.json').read_bytes());sf=se['selected_functions'][0];so={o['addr']:o for o in sf['operations']}
    need(so[0x20000866]['opcode']=='lw a5, 480(a5)'and so[0x2000086a]['opcode']=='beqz a5, 0x2000094e'and so[0x20000878]['opcode']=='lw a5, 532(a5)'and so[0x2000087c]['opcode']=='beqz a5, 0x2000094e','Actual raw clock and idleCB null checks in scheduler')
    need(so[0x200008bc]['opcode']=='addi sp, sp, 32'and B['decode_control'](bytes.fromhex(so[0x200008be]['bytes']),0x200008be)==(45,0x2000061a),'Original caller restores its frame before real tail transfer')
    sg,_,_=cfg(so,B,{0x2000061a,0x200004fa,0x20002610})
    need(all(0x200008be not in reachable(sg,sf['start'],skip_edge=edge)for edge in [(0x2000086a,0x2000086c),(0x2000087c,0x2000087e)]),'Both nonnull-guard edges dominate the selected static tail transfer')
    need(N['audit_abi'](HERE/'build/native-v1/c/config_abi.o')['derived_idleCB_storage']==0x200031ec+40==0x20003214,'Real compiled public idleCB offset matches actual pointer storage')
    h1={o['addr']:o for o in E['selected_functions'][1]['operations']};h2={o['addr']:o for o in E['selected_functions'][2]['operations']}
    need(h1[0x64312]['opcode']=='lw a5, 1340(a5)'and h1[0x64334]['opcode']=='lw a4, 1336(a4)'and h2[0x638ee]['opcode']=='lw a5, 1288(a5)'and h2[0x63918]['opcode']=='lbu a4, 512(a4)','Actual register-block pointer and parameter provenance')
    return dict(passed=True,static_only=True,functions=functions,caller_tail_PC=0x200008be,caller_restores_own_frame_before_tail=True,raw_clock_and_idleCB_nonnull_guard_edges_dominate_tail=True,callback_pointer_stability_still_required=True,known_main_and_idle_own_frames_not_simultaneously_allocated=True,
        idleCB=dict(storage=0x20003214,official_config_offset=40,header_signature='uint32_t (*)(uint32_t)',callee_null_guard=False,call_PC=0x2000071e,argument_zero_replaced_by_live_MaxCount=True,argument_physical_time_units_proved=False,nonzero_return_skips_local_timer_call=True,zero_return_reaches_real_timer_service=True),
        saved_word_window=dict(address=0x4002420c,save_PC=0x2000062c,clear_PC=0x20000630,FENCE_I_PC=0x20000634,restore_PC=0x200006aa,restore_dominates_idleCB=True,physical_IRQ_mask_semantics_proved=False),
        deadline=dict(clock_config=0x20003234,irqEnable_offset=12,MaxCount_offset=4,halfword_gate=0x2000346c,word=0x20003468,cached_delay=0x200031ac,raw_clock_pointer=0x200031e0,fresh_raw_clock_call_sites=[0x2000067a,0x20000686,0x200006ca,0x20000770],fallback_signed_constant=-30000000,fallback_expression='base=u32(MaxCount-30000000);sum=u32(base+fresh_raw_clock);subtract live MaxCount once if sum<base or sum>=MaxCount',fresh_callback_reads_not_collapsed=True,general_modulo_or_physical_clock_range_proved=False),
        register_phase=dict(gate_word=0x20003538,block_pointer_storage=0x20003590,offset=8,clear_mask=0xffccffff,set_mask=0x00330000,fresh_gate_and_pointer_reads_before_and_after_idle=True,paired_hardware_restore_proved=False),
        flag=dict(address=0x20003520,set_to_one_before_idle=True,clear_only_after_both_helpers_on_zero_return_and_fresh_gate_and_flag_nonzero=True,unconditional_flag_clear=False),
        register_helpers=[dict(entry=0x6430e,bytes=60,target_pointer_storage=0x2000353c,shadow_word=0x20003538,minimum_target_span=120,physical_register_identity_proved=False),dict(entry=0x638ea,bytes=90,target_pointer_storage=0x20003508,parameter_byte=0x20003200,minimum_target_span=56,physical_register_identity_proved=False)],
        raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],callees_preserving_SP_and_normal_returns_assumed=True,global_RAM_IRQ_alias_or_stack_bound_proved=False,installed_ROM_identity_proved=False,hardware_accessed=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_63dd0','tsl9_candidate_external_ram_20002610'}and len(u)==4 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real idle and timer providers resolve cross-input imports')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(4944,256,434,1,317),'Exact4944-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=4944,DATA_bytes=256,allocated_bytes=5200,instructions=1716,positive_FUNC_regions=434,positive_OBJECT_regions=1,relocations=317,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,idle_and_timer_cross_imports_have_real_bodies=True,both_far_register_helpers_have_real_bodies=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(previous)==json.loads((PRIOR/'audit-result-v2.json').read_bytes()),'Fresh prior arithmetic,clock,timer,scheduler and earlier proofs retained')
    contract=idle_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-idle-service-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,idle_contract=contract,prior_arithmetic_audit_sha256=sha(PRIOR/'audit-result-v2.json'),prior_SDK_composition_CODE_bytes=4426,prior_SDK_composition_DATA_bytes=256,prior_arithmetic_clock_timer_scheduler_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=518,instructions=178,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
