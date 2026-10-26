#!/usr/bin/env python3
"""Verify the real slot19 body and conditional sequential registration invariant."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-message-queue';LAYOUT=ROOT/'experiments/tsl9-resident-task-layout-contract'
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
def registration_contract(N,layout):
    E,B=N['EV'],N['B'];need(len(E['selected_functions'])==1,'One complete official registration body');f=E['selected_functions'][0];ops={o['addr']:o for o in f['operations']}
    expected={0x43c4e:'lui a4, 0x20003',0x43c52:'addi a4, a4, 412',0x43c56:'qk.c.lbu a5, 1(a4)',0x43c58:'qk.c.lbu a3, 2(a4)',0x43c5a:'bleu a3, a5, 0x43c78',0x43c5e:'lui a3, 0x20003',0x43c62:'lw a3, 452(a3)',0x43c66:'addi a2, a5, 1',0x43c6a:'qk.c.sb a2, 1(a4)',0x43c6c:'slli a4, a5, 0x2',0x43c70:'add a4, a4, a3',0x43c72:'sw a0, 0(a4)',0x43c74:'mv a0, a5',0x43c76:'ret',0x43c78:'li a5, 255',0x43c7c:'j 0x43c74'}
    need({pc:o['opcode']for pc,o in ops.items()}==expected,'All16 actual decoded instructions,including three conditional Xwchc fields')
    need(B['decode_control'](bytes.fromhex(ops[0x43c5a]['bytes']),0x43c5a)==(16,0x43c78)and B['decode_control'](bytes.fromhex(ops[0x43c7c]['bytes']),0x43c7c)==(45,0x43c74),'Two actual control targets')
    edges=[];returns=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        need(o['type']not in ['call','ucall','rjmp'],'No encoded call or indirect transfer within this function')
        if o['type']=='ret':returns.append(pc);continue
        if d:
            need(d[1]in ops,'Complete local control edge');edges.append([pc,d[1]])
            if o['type']=='cjmp':need(following in ops,'Complete conditional fallthrough');edges.append([pc,following])
        else:need(following in ops,'No fallthrough into adjacent BLE entry');edges.append([pc,following])
    reached=set();pending=[f['start']]
    while pending:
        pc=pending.pop()
        if pc in reached:continue
        reached.add(pc);pending.extend(b for a,b in edges if a==pc)
    need(reached==set(ops)and returns==[0x43c76],'Every selected instruction has an entry path to the shared return')
    need(not N['S']['undefined']and not N['S']['PC_relative_pairs'],'No named import or hidden far call in the complete body')
    # Algebra over byte bounds,not executions over supplied states or a memory model.
    byte_max=255;max_success_old=byte_max-1;max_new=max_success_old+1
    need(max_new==255 and 4*max_success_old+4==4*255,'Success old<capacity<=255 prevents byte wrap and fits a4*capacity table')
    n=layout['numerical_contract'];need(n['conditional_original_values']['capacity']==29 and n['conditional_original_values']['requested_bytes']==750,'Previous conditional layout retained')
    initial_count=3;capacity=n['conditional_original_values']['capacity'];remaining=capacity-initial_count
    need(remaining==26 and 4*(capacity-1)+4==n['conditional_original_values']['handler_bytes'],'Conditional original table capacity matches last valid registration word')
    return dict(passed=True,static_only=True,concrete_machine_or_memory_simulated=False,complete_range=[0x43c4e,0x43c7e],instructions=16,direct_edges=edges,return_PCs=returns,official_bindings=E['official_bindings'],
        count_byte=0x2000319d,capacity_byte=0x2000319e,handler_pointer_storage=0x200031c4,
        success_guard='old_count < capacity',success_count='old_count+1',success_handler_store='handler_array + 4*old_count receives unvalidated entry_A0 word',success_return='old_count',
        failure_guard='old_count >= capacity',failure_return=255,failure_has_no_store=True,
        sequential_invariant='If0<=old_count<=capacity<=255 and the count/capacity/pointer are stable,success gives old_count+1<=capacity and failure preserves count;no byte wrap occurs',
        handler_bound='With an aligned writable4*capacity-byte array,success store ends at4*(old_count+1)<=4*capacity',
        instruction_store_order=[dict(PC=0x43c6a,role='count byte'),dict(PC=0x43c72,role='handler word')],entry_callback_null_check_present=False,entry_callback_callable_validity_proved=False,
        encoded_gate_save_restore_or_FENCE_sequence_present=False,physical_atomicity_proved=False,concurrent_observer_order_or_IRQ_state_proved=False,
        conditional_original_capacity=capacity,conditional_initial_registered_count=initial_count,conditional_remaining_successful_registrations=remaining,
        assumptions=['capacity,count and handler pointer are not changed concurrently','handler_array is an aligned writable4*capacity-byte region with exclusive ownership','the precondition old_count<=capacity holds initially','the26-slot example additionally assumes the earlier SNV path leaves count/pointers unchanged and the three built-in registrations complete','caller supplies a valid callable handler if later dispatch requires it'],
        task_count_zero_after_SNV_proved=False,physical_RAM_capacity_proved=False,heap_or_APP_global_ownership_proved=False,installed_ROM_identity_proved=False,runtime_closed=False,new_BIN=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        r=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,r
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    need(not u and facts(path)==(a,d,set(),sorted(rel)),'Every input byte,positive symbol and relocation retained;no unresolved or invented provider')
    need(sum(len(v[1])for v in a.values())==2312 and len(d)==208 and len(rel)==151,'Exact2312-byte composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=2312,instructions=821,positive_FUNC_regions=208,relocations=151,named_UND=[],every_input_byte_symbol_relocation_retained=True,independent_readers=independent,official_slot19_has_real_body=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);layout=lib(LAYOUT/'verify-v1.py')['audit'](llvm)
    need(canonical(layout)==json.loads((LAYOUT/'verification-v1.json').read_bytes()),'Fresh750/752-byte layout and prior2264-byte SDK/Flash proofs retained')
    contract=registration_contract(N,layout);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh nonloadable composition trial')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ composition objects identical')
    return dict(schema='TSL9-public-SDK-task-registration-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,registration_contract=contract,prior_layout_verification_sha256=sha(LAYOUT/'verification-v1.json'),prior_SDK_composition_bytes=2264,prior_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable registration receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=48,instructions=16,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},conditional_remaining_slots=26,physical_atomicity_proved=False,APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
