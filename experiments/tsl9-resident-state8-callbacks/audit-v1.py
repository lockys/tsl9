#!/usr/bin/env python3
"""Audit actual idle/service helper bodies and retain all physical execution gates."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-state8-service'
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
def callback_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};frames={0x65164:48,0x653a0:48,0x200007a0:16,0x2000263a:0,0x6440a:16,0x63b0e:0,0x63e58:0,0x200026ba:16};functions=[];graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,returns,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and returns,'Every selected instruction statically reachable in its complete entry CFG')
        frame=frames[f['start']];changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-frame,frame]if frame else []),'Actual own-frame changes')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP on branch and polling joins');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only original own-frame positions')
            if not g[pc]:need(pc in returns and after==0,'Own frame balanced at every local normal return')
            pending.extend((v,after)for v in g[pc])
        for c in calls:
            if c['PC']in pairs:c['target']=pairs[c['PC']]['target_PC']
        graphs[f['start']]=g;functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced=True,return_PCs=returns,calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x65178:'qk.c.lbu a5, 1(a4)',0x6517a:'andi a5, a5, 1',0x6517c:'beqz a5, 0x6535c',0x65188:'sb zero, 15(sp)',0x6518c:'lw s3, 36(s0)',0x65190:'sb zero, 1(s0)',0x6520e:'qk.c.lbu a0, 16(s1)',0x65210:'li a1, 2',0x65282:'li a2, 1',0x652fa:'lw a0, 36(s0)',0x652fc:'li a3, 0',0x652fe:'li a1, 0',0x65300:'addi a2, sp, 15',0x6530e:'slli a1, a0, 0x18',0x65318:'srai a1, a1, 0x18',0x65336:'qk.c.lbusp a5, 15(sp)',0x65338:'sb a5, 0(s3)',0x65340:'lw a5, 16(s2)',0x65344:'lw a2, 36(s0)',0x65346:'andi a1, a1, 255',0x6534a:'li a0, 3',0x6534c:'jalr a5',
        0x653c0:'lw s3, 36(a5)',0x653c4:'li a3, 0',0x653c6:'addi a2, sp, 15',0x653ca:'li a1, 0',0x653cc:'mv a0, s3',0x653ce:'sb zero, 1300(s0)',0x653d2:'sb zero, 15(sp)',0x6541e:'qk.c.lbusp a5, 15(sp)',0x65470:'qk.c.lbu a0, 16(s1)',0x65472:'li a1, 2',0x65500:'lui a0, 0x65',0x65504:'addi a0, a0, 1568',0x65534:'lw a5, 16(s2)',0x65538:'lw a2, 36(s0)',0x6553a:'li a1, 0',0x6553c:'li a0, 3',0x6553e:'jalr a5',0x65550:'lw a5, 16(s2)',0x65554:'li a0, 3',0x65556:'andi a1, s4, 255',0x6555a:'jalr a5',
        0x200007a4:'lw a4, -264(a5)',0x200007ae:'addi s0, a5, -264',0x200007b2:'beqz a4, 0x200007b6',0x200007b4:'jalr a4',0x200007ba:'lbu a5, -260(a5)',0x200007c2:'bnez a5, 0x200007c8',0x200007c4:'sw zero, 0(s0)',
        0x2000263e:'lw a4, 1288(a6)',0x20002642:'lw a5, 56(a4)',0x20002644:'srli a5, a5, 0x5',0x20002646:'andi a5, a5, 1',0x20002648:'bnez a5, 0x200026b6',0x2000264a:'beqz a2, 0x20002652',0x2000264c:'lw a5, 48(a4)',0x2000264e:'srli a5, a5, 0xf',0x20002650:'qk.c.sb a5, 0(a2)',0x20002652:'beqz a3, 0x20002680',0x2000267a:'div a5, a5, a4',0x20002680:'beqz a1, 0x200026a0',0x2000268c:'li a0, 6',0x2000269a:'li a0, 14',0x200026a8:'li a0, 0',0x200026b6:'li a0, 1',
        0x64412:'sb zero, 1390(a5)',0x6441c:'li a0, 0',0x63ed4:'sb zero, 7(a5)',0x200026ce:'lw a3, 100(a4)',0x200026d0:'bnez a3, 0x200026ce',0x2000272c:'bnez a4, 0x2000271e'}
    need(all(ops[pc]['opcode']==value for pc,value in expected.items()),'Actual callback guards,stack output,status flow,runner lifetime and provider roles')
    for entry,init,call,load in [(0x65164,0x65188,0x65308,0x65336),(0x653a0,0x653d2,0x653da,0x6541e)]:
        g=graphs[entry];need(call not in reachable(g,entry,skip_node=init)and load not in reachable(g,entry,skip_node=call),'Both stack byte outputs initialized before actual parser call and load')
    vectors=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',vectors)]
    need(actual==E['official_vectors']['checked']and len(actual)==52,'Exactly52 positive vectors from the pinned primary file,not self-generated examples')
    fragmented=E['resolved_standard_decoder_fragments'];need([p['PC']for p in fragmented]==[0x65336,0x6541e]and all(p['word']==0x879c and p['standard_decoder_fragment_count']==2 for p in fragmented),'Both real16-bit stack loads replace exactly two decoder one-byte fragments')
    word=0x879c;need(word>>11==0b10000 and word&3==0 and(word>>5)&3==0 and(word>>2)&7==7 and(word>>7)&15==15,'Primary QKStackInst bits select LBUSP,compressed register15/A5 and offset15')
    need(all(0<=15<frames[pc]for pc in [0x65164,0x653a0]),'Actual stack byte offset falls within each selected own48-byte frame;global stack validity unproved')
    need(sorted((p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs'])==sorted([(0x65284,0x200026ba),(0x65304,0x2000263a),(0x653d6,0x2000263a),(0x65508,0x2000078a),(0x200026e2,0x63b0e)]),'All five actual far calls,including work-mode rather than a guessed copy target')
    need((0x65<<12)+1568==0x65620 and E['new_numeric_CODE_dependencies']==[0x65620]and not E['new_numeric_CODE_dependencies_provided'],'Actual next callback remains unprovided')
    need(set(previous['state8_contract']['callback_setter']['numeric_CODE_dependencies'])=={0x65164,0x653a0}<=entries,'Both previous actual CODE literals now have real native bodies')
    candidate=E['unbound_runner_call_candidate'];b=bytes.fromhex(candidate['bytes']);carrier=(ROOT/N['S']['firmware']).read_bytes();need(b==carrier[0x3098:0x30a0]and len(b)==8 and B['decode_control'](b[:4],0x20002e28)==(17,0x200007a0)and(int.from_bytes(b[:4],'little')>>7)&31==1 and int.from_bytes(b[4:],'little')==0x73,'Exact JAL-runner/ECALL reference bytes without inventing a containing function or entry')
    actual_opaque=sorted(c['PC']for f in functions for c in f['calls']if c['target']is None);need(actual_opaque==sorted(v['PC']for v in E['opaque_transfers']),'Every opaque callback remains explicit')
    return dict(passed=True,static_only=True,functions=functions,primary_Xwchc=dict(official_vectors=52,families=8,stack_vectors=24,actual_custom_ports=45,fragmented_actual_stack_loads=2,stack_load_word=0x879c,stack_load_instruction='qk.c.lbusp a5,15(sp)',primary_bit_fields_checked=True,physical_ISA_profile_proved=False),
        previous_numeric_CODE_callbacks_have_real_bodies=[0x65164,0x653a0],new_numeric_CODE_callbacks_unprovided=[0x65620],numeric_CODE_addresses_are_not_linker_relocations=True,
        runner=dict(entry=0x200007a0,bytes=48,pointer_storage=0x20002ef8,flag_storage=0x20002efc,nonnull_entry_pointer_called=True,pointer_loaded_before_call=True,flag_read_fresh_after_return=True,fresh_flag_zero_clears_pointer_word=True,no_compare_with_original_pointer_before_clear=True,callback_side_effects_atomicity_or_lifetime_proved=False,invoker_or_execution_reachability_proved=False),
        callbacks=dict(entries=[0x65164,0x653a0],own_frames=[48,48],stack_byte_offset=15,stack_byte_initialized_before_parser=True,parser_A1_zero_and_A3_zero_on_known_paths=True,parser_A2_points_to_own_stack_byte=True,state_base=0x20003514,first_entry_flag_byte=1,second_entry_flag_byte=0,actual_event_setter=0x4354a,event_literal=2,event_success_proved=False,unconditional_shared_callback_storage=0x20003550,unconditional_shared_callback_PCs=[0x6534c,0x6553e,0x6555a],shared_callback_arguments='A0=3,A1=status_low8,A2=shared_descriptor_word',status_callback_storage=0x20003220,new_CODE_setter_call=0x65508,new_CODE_value=0x65620,buffer_or_descriptor_capacity_proved=False,packet_protocol_meaning_proved=False),
        receive_status=dict(entry=0x2000263a,bytes=128,own_frame_bytes=0,register_pointer_storage=0x20003508,local_return_codes=[0,1,6,14],optional_A2_byte_output='low8(register_word48>>15)',optional_A3_signed_halfword_output=True,trailer_check_runs_only_for_nonzero_A1=True,known_callback_paths_pass_A1_zero=True,status_codes_are_not_physical_success=True),
        register_work=dict(entry=0x200026ba,bytes=250,own_frame_bytes=16,polling_back_edges=[[0x200026d0,0x200026ce],[0x2000272c,0x2000271e]],termination_proved=False),unbound_runner_call_candidate=candidate,raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],callees_preserving_SP_and_normal_returns_assumed=True,global_RAM_IRQ_alias_or_stack_bound_proved=False,installed_ROM_identity_proved=False,hardware_accessed=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_57dae','tsl9_candidate_external_flash_6020a'}and len(u)==5 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real callback providers and existing event/state8/setter definitions retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(8672,256,703,1,516),'Exact8672-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=8672,DATA_bytes=256,allocated_bytes=8928,instructions=3029,positive_FUNC_regions=703,positive_OBJECT_regions=1,relocations=516,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,callback_and_existing_cross_imports_have_real_bodies=True,all_eight_new_real_bodies_retained=True,previous_numeric_callbacks_have_real_bodies=True,new_numeric_callback_65620_provided=False,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior state8,scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=callback_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-state8-callbacks-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,callback_contract=contract,prior_state8_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=6554,prior_SDK_composition_DATA_bytes=256,prior_state8_scheduler_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=2118,instructions=755,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
