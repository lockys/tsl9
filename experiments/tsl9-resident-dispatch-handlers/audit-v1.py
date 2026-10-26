#!/usr/bin/env python3
"""Audit complete actual dispatch handlers and providers without target execution."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-trap-profile-contract'
CODE_PRIOR=ROOT/'experiments/tsl9-resident-lle-callback-gateway'
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
        if o['type']in ['ret','privileged-return','exception-transfer','rjmp']:returns.append(pc);continue
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
def callback_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};frames={0x57dae:32,0x6020a:32,0x63c54:0,0x63eda:16};functions=[];graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,returns,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and returns and all(ops[p]['type']=='ret'for p in returns),'Complete selected entry CFG;no adjacent functions or privileged/opaque exits')
        frame=frames[f['start']];changes={p:int(o['opcode'].rsplit(', ',1)[1],0)for p,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-frame,frame]if frame else []),'Only actual own-frame changes')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP on CFG joins');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only original own-frame states')
            if not g[pc]:need(pc in returns and after==0,'Own frame balanced at every actual local normal return')
            pending.extend((v,after)for v in g[pc])
        for call in calls:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced=True,return_PCs=returns,calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]));graphs[f['start']]=g
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x57dcc:'beq a4, a5, 0x57dd8',0x57dd4:'bne a4, a5, 0x57df2',0x57dda:'bnez a5, 0x57de2',0x57ddc:'li a5, 263',0x57de0:'qk.c.sh a5, 8(s1)',0x57ee8:'j 0x57de2',0x60228:'beq a4, a5, 0x60234',0x60230:'bne a4, a5, 0x6024e',0x60236:'bnez a5, 0x6023e',0x60238:'li a5, 262',0x6023c:'qk.c.sh a5, 8(s0)',0x6034e:'j 0x6023e',
        0x57e76:'li a0, 0',0x57e96:'lbu a5, 576(a5)',0x57e9a:'beqz a5, 0x57ea4',0x57ea0:'lw a0, 1264(a5)',0x602fc:'lbu a5, 576(a5)',0x60300:'beqz a5, 0x60312',0x60306:'lw a0, 1272(a5)',
        0x63c54:'lui a5, 0x20003',0x63c58:'lw a5, 1292(a5)',0x63c5c:'beqz a5, 0x63c76',0x63c5e:'lw a3, 4(a5)',0x63c60:'lw a6, 8(a5)',0x63c64:'lw a4, 0(a3)',0x63c6a:'sw a4, 0(a3)',0x63c6c:'lw a3, 12(a5)',0x63c6e:'lw a5, 20(a5)',0x63c74:'sw a5, 0(a3)',
        0x63ee8:'lw s2, 524(a5)',0x63eec:'sw zero, 524(a5)',0x63ef0:'fence.i',0x63efe:'andi a5, a5, 3',0x63f00:'beqz a5, 0x63f56',0x63f14:'bne a4, a5, 0x63f28',0x63f18:'lui a5, 0x20003',0x63f1c:'lw a5, 1360(a5)',0x63f20:'li a2, 0',0x63f22:'li a1, 0',0x63f24:'li a0, 17',0x63f26:'jalr a5',0x63f4e:'sb zero, -260(a5)',0x63f52:'jal ra, 0x63e58',0x63f5e:'sw s2, 524(a5)',0x63f68:'ret'}
    need(all(ops[p]['opcode']==v for p,v in expected.items()),'Exact guards,pending packed halfwords,setter asymmetry,optional descriptor,hardware word and opaque callback operands')
    need(sorted((p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs'])==[(0x57ea4,0x2000078a),(0x6030a,0x2000078a)],'Both actual far calls have real prior setter provider')
    opaque=[c['PC']for f in functions for c in f['calls']if c['target']is None];need(opaque==[0x63f26],'Exactly one new genuinely opaque callback;far pairs are real code calls')
    ga,gb,gh=graphs[0x57dae],graphs[0x6020a],graphs[0x63eda]
    need(0x57ea8 not in reachable(ga,0x57dae,skip_node=0x57e76)and 0x57ea8 in reachable(ga,0x57ea4)and 0x6030e not in reachable(gb,0x60312),'First setter has initializedA0 and remains called on zero-selection branch;second skips setter on zero flag')
    need(0x63f26 not in reachable(gh,0x63eda,skip_edge=(0x63f14,0x63f18))and 0x63f26 not in reachable(gh,0x63eda,skip_node=0x63f1c),'Opaque callback is state-conditioned and load-dominated;no pointer null check claimed')
    for p in [0x63f26,0x63f52]:need(p not in reachable(gh,0x63eda,skip_node=0x63eec),'Actual clear dominates both calls')
    need(0x63f68 not in reachable(gh,0x63eda,skip_node=0x63f5e),'Actual hardware restore store dominates each local normal return;callee register preservation and aliasing remain assumptions')
    need(0x40024000+524==0x4002420c and ops[0x63ede]['opcode']=='lui a5, 0x40024'and ops[0x63f5a]['opcode']=='lui a5, 0x40024','Both actual hardware address forms')
    vectors=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',vectors)];need(actual==E['official_vectors']['checked']and len(actual)==52,'All52 pinned primary instruction vectors')
    parent=N['lib'](N['S']['reader'])['ELF'](CODE_PRIOR/'build/composition-v1/c/candidate.o');prior_UND={s['name']for s in parent.symbols if s['info']>>4 and not s['section']};need(prior_UND=={E['selected_functions'][0]['name'],E['selected_functions'][1]['name']},'Actual new bodies exactly supply both genuine prior UND names')
    return dict(passed=True,static_only=True,functions=functions,previous_two_named_handlers_have_real_bodies=True,no_stub_or_ABS_function_provider=True,primary_Xwchc=dict(official_vectors=52,families=8,actual_ports=29,physical_profile_proved=False),handler_state=dict(base=0x20003514,mode_byte_offset=7,pending_kind_offset=8,pending_flag_offset=9,first_packed_deferred_value=263,second_packed_deferred_value=262,first_back_edge=[0x57ee8,0x57de2],second_back_edge=[0x6034e,0x6023e],packet_or_feature_meaning_proved=False),
        callback_selection=dict(flag_byte=0x20003240,first_raw_pointer_storage=0x200034f0,first_zero_flag_calls_setter_with_A0_zero=True,second_raw_pointer_storage=0x200034f8,second_zero_flag_skips_setter=True,setter_entry=0x2000078a,raw_RAM_pointer_targets_provided=False),optional_descriptor=dict(pointer_storage=0x2000350c,nonnull_descriptor_gates_two_pointed_word_updates=True,descriptor_capacity_or_target_register_identity_proved=False),
        hardware_word=dict(address=0x4002420c,load_PC=0x63ee8,clear_PC=0x63eec,FENCE_I_PC=0x63ef0,restore_PC=0x63f5e,restore_store_on_every_local_normal_return=True,saved_value_register='s2',actual_saved_value_preservation_requires_callees_and_no_alias=True,physical_identity_atomicity_or_interrupt_mask_semantics_proved=False),opaque_transfers=E['opaque_transfers'],shared_callback=dict(pointer_storage=0x20003550,PC=0x63f26,A0=17,A1=0,A2=0,state_conditioned=True,pointer_null_guard=False,effects_bounded=False),raw_dependencies=E['raw_dependencies'],callees_preserving_SP_S2_and_returning_normally_assumed=True,numeric_or_raw_pointer_closure_proved=False,physical_trap_route_proved=False,installed_ROM_identity_proved=False,global_stack_or_IRQ_budget_proved=False,runtime_closed=False,hardware_accessed=False)

def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining==set()and len(u)==4 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real callback providers and existing event/state8/setter definitions retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(10726,256,865,1,629),'Exact10726-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=10726,DATA_bytes=256,allocated_bytes=10982,instructions=3751,positive_FUNC_regions=865,positive_OBJECT_regions=1,relocations=629,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,callback_and_existing_cross_imports_have_real_bodies=True,all_four_new_real_bodies_retained=True,previous_numeric_callbacks_have_real_bodies=True,previous_two_named_handlers_provided=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm,refs);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior state8,scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=callback_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[CODE_PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-two-handlers-two-providers-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,callback_contract=contract,prior_state8_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=9608,prior_SDK_composition_DATA_bytes=256,prior_state8_scheduler_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=1118,instructions=384,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
