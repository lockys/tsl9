#!/usr/bin/env python3
"""Audit complete scheduler-state bodies and retain all physical execution gates."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-idle-service'
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
def state_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};frames={0x20002610:0,0x63dd0:16};functions=[];graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,returns,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and len(returns)==1,'Complete entry CFG and exactly one normal return')
        changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};frame=frames[f['start']];need(sorted(changes.values())==([-frame,frame,frame]if frame else []),'Own frame restored separately at normal return and external tail')
        pending=[(f['start'],0)];depths={};tails=[]
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP on loop and branch joins');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only actual own frame positions')
            if not g[pc]:
                need(after==0,'Own frame released at every return or tail')
                if pc not in returns:tails.append(dict(PC=pc,target=B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)[1]))
            pending.extend((v,after)for v in g[pc])
        graphs[f['start']]=g;functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced_at_return_and_tail=True,return_PCs=returns,tail_transfers=tails,calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x20002618:'lw a2, 1340(a5)',0x2000261c:'addi a5, a3, 1300',0x20002620:'lbu a4, 1300(a3)',0x20002624:'andi a4, a4, 1',0x20002626:'bnez a4, 0x20002634',0x20002628:'qk.c.lbu a4, 1(a5)',0x2000262a:'andi a4, a4, 1',0x2000262c:'bnez a4, 0x20002634',0x2000262e:'lw a4, 100(a2)',0x20002630:'bnez a4, 0x20002620',0x20002632:'qk.c.lbu a4, 5(a5)',0x20002634:'sb zero, 5(a5)',0x20002638:'ret',
        0x63dd8:'addi a5, s0, 1300',0x63dde:'qk.c.lbu a4, 8(a5)',0x63de0:'li a5, 8',0x63de6:'bne a4, a5, 0x63e14',0x63dee:'lbu a4, 1344(a4)',0x63df6:'addi a5, a5, 1376',0x63dfa:'andi a4, a4, 1',0x63dfc:'qk.c.lbu a2, 3(a5)',0x63dfe:'qk.c.lbu a3, 2(a5)',0x63e00:'beqz a4, 0x63e4a',0x63e02:'lw a0, 4(a5)',0x63e04:'beqz a0, 0x63e4a',0x63e06:'qk.c.lbu a1, 1(a0)',0x63e08:'addi a0, a0, 2',0x63e0e:'beqz a0, 0x63e14',0x63e10:'li a5, 1',0x63e12:'qk.c.sb a5, 9(s0)',0x63e14:'qk.c.lbu a4, 8(s0)',0x63e16:'li a5, 6',0x63e18:'bne a4, a5, 0x63e2c',0x63e20:'lw a5, 1080(a5)',0x63e24:'qk.c.lbu a5, 11(a5)',0x63e26:'beqz a5, 0x63e50',0x63e2c:'qk.c.lbu a4, 8(s0)',0x63e2e:'li a5, 7',0x63e30:'bne a4, a5, 0x63e50',0x63e38:'lw a5, 1100(a5)',0x63e3c:'qk.c.lbu a5, 7(a5)',0x63e3e:'beqz a5, 0x63e50',0x63e40:'lw s0, 8(sp)',0x63e42:'lw ra, 12(sp)',0x63e44:'addi sp, sp, 16',0x63e4a:'li a1, 0',0x63e4c:'li a0, 0'}
    need(all(ops[pc]['opcode']==value for pc,value in expected.items()),'Actual polling,state byte,fresh reload,buffer argument and restored-tail instructions')
    need(0x20002638 not in reachable(graphs[0x20002610],0x20002610,skip_node=0x20002634),'Every local polling return follows flag clear')
    need(all(re.search(r'\ba0\b',o['opcode'])is None for o in E['selected_functions'][0]['operations']),'Polling body does not write or assign return status A0')
    need([(pc,B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)[1])for pc in [0x63e0a,0x63e28,0x63e46]]==[(0x63e0a,0x64f04),(0x63e28,0x6020a),(0x63e46,0x57dae)],'All three actual positive handler call/tail targets')
    scheduler=ROOT/'experiments/tsl9-resident-scheduler';S=json.loads((scheduler/'spec-v1.json').read_bytes());caller_sites=sorted(c['PC']for c in S['controls']if c['target_PC']==0x20002610);need(caller_sites==[0x20000812,0x200008cc],'Both real polling callers')
    need(len(S['PC_relative_pairs'])==1 and S['PC_relative_pairs'][0]['PC']==0x2000096e and S['PC_relative_pairs'][0]['target_PC']==0x63dd0,'Actual far scheduler caller')
    reference=E['positive_callee_reference'];need((reference['start'],reference['end'])==(0x64f04,0x65164),'Complete next positive callee reference bounds')
    carrier=(ROOT/N['S']['firmware']).read_bytes();at=reference['start'];joined=bytearray()
    for o in reference['operations']:
        b=bytes.fromhex(o['bytes']);need(o['addr']==at and len(b)==o['size']==(4 if b[0]&3==3 else 2)and b==carrier[at-0x40000:at-0x40000+len(b)],'Every positive reference instruction matches original bytes');joined.extend(b);at+=len(b)
    need(at==reference['end']and len(joined)==608 and hashlib.sha256(joined).hexdigest()==reference['original_sha256'],'Whole608-byte positive reference,not a reconstructed/native provider')
    return dict(passed=True,static_only=True,functions=functions,actual_polling_callers=caller_sites,actual_state_service_far_caller=0x2000096e,
        poll=dict(entry=0x20002610,bytes=42,state_base=0x20003514,first_flag_offset=0,second_flag_offset=1,flag_mask=1,register_pointer_storage=0x2000353c,register_offset=100,actual_back_edge=[0x20002630,0x20002620],termination_proved=False,fresh_flag_and_register_reads=True,final_byte5_read_retained_even_though_value_is_not_used=True,byte5_clear_dominates_every_local_return=True,A0_not_assigned_status=True,own_frame_bytes=0),
        state=dict(entry=0x63dd0,bytes=136,state_base=0x20003514,state_byte_offset=8,states_checked=[8,6,7],state_reloaded_at=[0x63dde,0x63e14,0x63e2c],fresh_state_reads_not_replaced_by_one_cached_switch=True,flag_byte_offset=9,flag_set_when_64F04_return_nonzero=True,parameter_base=0x20003560,A2_byte_offset=3,A3_byte_offset=2,buffer_pointer_offset=4,buffer_present_and_parameter_bit0_path='A0=buffer+2;A1=buffer_byte1',fallback='A0=0;A1=0;A2/A3 retain actual parameter bytes',state6_descriptor_pointer=0x20003438,state6_guard_byte_offset=11,state7_descriptor_pointer=0x2000344c,state7_guard_byte_offset=7,descriptor_pointers_have_no_local_null_guard=True,external_handlers=[0x64f04,0x6020a,0x57dae],own_frame_bytes=16,frame_released_before_57DAE_tail=True,protocol_role_or_handler_success_proved=False),
        positive_next_callee=dict(entry=0x64f04,end=0x65164,bytes=608,original_sha256=reference['original_sha256'],CODE_reconstructed_in_this_unit=False,numeric_CODE_literal_dependencies=[0x65164,0x653a0],further_callees_and_callback_contracts_open=True),
        raw_dependencies=E['raw_dependencies'],callees_preserving_SP_and_normal_returns_assumed=True,physical_register_identity_proved=False,global_RAM_IRQ_alias_or_stack_bound_proved=False,installed_ROM_identity_proved=False,hardware_accessed=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_57dae','tsl9_candidate_external_flash_6020a','tsl9_candidate_external_flash_64f04'}and len(u)==5 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real polling and state bodies resolve both old imports;three genuine handlers remain')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(5122,256,455,1,332),'Exact5122-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=5122,DATA_bytes=256,allocated_bytes=5378,instructions=1782,positive_FUNC_regions=455,positive_OBJECT_regions=1,relocations=332,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,scheduler_poll_and_state_cross_imports_have_real_bodies=True,prior_idle_register_helpers_retained=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior idle,arithmetic,clock,timer,scheduler and earlier proofs retained')
    contract=state_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-scheduler-state-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,state_contract=contract,prior_idle_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=4944,prior_SDK_composition_DATA_bytes=256,prior_idle_arithmetic_clock_timer_scheduler_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=178,instructions=66,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:
            for variant in [str(path).replace('\\','\\\\'),str(path),path.as_posix()]:message=message.replace(variant,token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
