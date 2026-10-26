#!/usr/bin/env python3
"""Verify five real clock bodies and the original APP clock configuration without execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-timer-service'
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
def app_clock_contract(N):
    paths={'startup':'analysis/resident-startup-2026-10-25/evidence.json','primitives':'analysis/peripheral-primitives-2026-10-25/evidence.json'}
    hashes={'startup':'9c9e418f16ec9b7231df2dc623ee90c39a0b1bba53f0a116271800d7ad8770f5','primitives':'47ae1080ee3138610d45da71b456b83c61ccb89e1343e62515fa9f2f2390c6e6'}
    for k,p in paths.items():need(sha(ROOT/p)==hashes[k],'Pinned original APP clock evidence '+k)
    records={k:json.loads((ROOT/p).read_bytes())for k,p in paths.items()};ops={o['addr']:o for e in records.values()for f in e['selected_functions']for o in f['operations']}
    expected={0x19b60:'sw zero, 0(sp)',0x19b62:'sw zero, 4(sp)',0x19b64:'sw zero, 8(sp)',0x19b66:'sw zero, 12(sp)',0x19bac:'li a5, -1',0x19bae:'sw a5, 4(sp)',0x19bb0:'lui a5, 0x3e84',0x19bb4:'addi a5, a5, -384',0x19bb8:'sw a5, 8(sp)',0x19bba:'auipc a5, 0xfffff',0x19bbe:'addi a5, a5, 1548',0x19bc2:'sw a5, 0(sp)',0x19bc4:'lui a5, 0x40',0x19bc8:'lw a5, 116(a5)',0x19bca:'mv a0, sp',0x19bcc:'jalr a5',0x19b3a:'lbu a0, 0(s0)'}
    need(all(ops[pc]['opcode']==v for pc,v in expected.items()),'Actual APP zero16/configuration stores and status-overwrite instructions')
    fw=(ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes();need(__import__('hashlib').sha256(fw).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Exact original APP input')
    selected=[next(f for f in records['startup']['selected_functions']if f['start']==pc)for pc in [0x19b16,0x19b56]]+[next(f for f in records['primitives']['selected_functions']if f['start']==0x191c6)]
    facts=[]
    for f in selected:
        at=f['start']
        for o in f['operations']:
            b=bytes.fromhex(o['bytes']);need(o['addr']==at and len(b)==o['size']and b==fw[at-0x8000:at-0x8000+len(b)],'Whole actual APP caller/counter instruction');at+=len(b)
        need(at==f['end'],'Complete original APP clock-related body');facts.append(dict(entry=f['start'],end=f['end'],bytes=at-f['start'],instructions=len(f['operations'])))
    packed=(int.from_bytes(bytes.fromhex(ops[0x19bb0]['bytes']),'little')&0xfffff000)-384
    frequency,accuracy=packed&65535,packed>>16;callback=(0x19bba+(int.from_bytes(bytes.fromhex(ops[0x19bba]['bytes']),'little')&0xfffff000)+1548)&0xffffffff
    need((frequency,accuracy,callback)==(16000,1000,0x191c6),'Actual packed nominal frequency/accuracy and callback address')
    carrier=(ROOT/N['S']['firmware']).read_bytes();need(int.from_bytes(carrier[0x74:0x78],'little')==0x43f46,'Actual slot16 pointer storage40074 binds TimerInit')
    need(N['B']['decode_control'](bytes.fromhex(ops[0x19b38]['bytes']),0x19b38)==(45,0x19b56),'Actual caller invokes APP clock-configuration function')
    direct_after_clear=[o for o in selected[1]['operations']if o['addr']>0x19b66 and o['opcode'].endswith(', 12(sp)')and o['type']=='store'];need(not direct_after_clear,'No later direct caller-frame write to irqEnable word')
    counter=selected[2];need(counter['end']==0x19220 and counter['end']-counter['start']==90,'Complete existing90-byte custom clock callback')
    high,low=0x40003000-2024,0x40003000-2020;need((high,low)==(0x40002818,0x4000281c),'Actual numeric halfword counter addresses')
    need(ops[0x1921a]['opcode']=='slli a0, a0, 0x10'and ops[0x1921c]['opcode']=='or a0, a0, a5','Actual combined high/low return')
    return dict(passed=True,static_only=True,input_paths=paths,input_sha256=hashes,complete_APP_bodies=facts,new_APP_CODE_bytes=0,configuration_call_PC=0x19bcc,configuration_pointer='caller SP',configuration_bytes=16,initial_zero_store_PCs=[0x19b60,0x19b62,0x19b64,0x19b66],
        conditional_configuration=dict(getClockValue=callback,ClockMaxCount=0xffffffff,ClockFrequency=frequency,ClockAccuracy=accuracy,irqEnable=0),nominal_frequency_unit='Hz as declared by original header',nominal_accuracy_unit='ppm as declared by original header',known_caller_uses_TimerInit_status=False,status_overwritten_PC=0x19b3a,
        custom_counter=dict(entry=callback,bytes=90,high_halfword_address=high,low_halfword_address=low,repeated_equal_read_checks=True,high_recheck_and_conditional_low_reread=True,return_expression='high_last<<16 | low_last',retry_termination_proved=False,hardware_coherent_snapshot_proved=False),
        requires_helpers_IRQ_and_aliases_not_to_overwrite_caller_configuration=True,actual_hardware_frequency_proved=False,configuration_acceptance_or_full_initialization_proved=False,installed_ROM_identity_proved=False,hardware_accessed=False)
def clock_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};named={int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};functions=[]
    expected_frames={0x43f46:32,0x43b0a:16,0x43d62:32,0x20000986:0,0x43520:16}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};edges=[];returns=[];calls=[]
        for pc,o in ops.items():
            following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
            if o['type']=='ret':returns.append(pc);continue
            if d:
                kind,target=d
                if o['type']=='call':need(target in entries|named and following in ops,'Real direct callee and normal-return continuation');calls.append(dict(PC=pc,target=target));edges.append([pc,following])
                else:
                    need(target in ops,'Every local branch stays within its complete clock function');edges.append([pc,target])
                    if o['type']=='cjmp':need(following in ops,'Whole local branch fallthrough');edges.append([pc,following])
            else:
                need(following in ops,'No fallthrough into adjacent code');edges.append([pc,following])
                if o['type']=='ucall':calls.append(dict(PC=pc,target=pairs[pc]['target_PC']if pc in pairs else None))
        changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};frame=expected_frames[f['start']];need(sorted(changes.values())==([-frame,frame]if frame else []),'Actual own-frame adjustments')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent affine own-frame position at every join');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only original own-frame positions')
            if pc in returns:need(after==0,'Own frame balanced at every normal return')
            pending.extend((b,after)for a,b in edges if a==pc)
        need(set(depths)==set(ops)and len(returns)==1,'Every selected instruction belongs to its entry CFG')
        functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),direct_edges=edges,return_PCs=returns,calls=calls,own_frame_bytes=frame,own_frame_balanced=True))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x43f52:'lw a5, 48(a5)',0x43f60:'jalr a5',0x43f64:'beqz a1, 0x43fe6',0x43f66:'lw a5, 0(a1)',0x43f68:'li a0, 1',0x43f6a:'beqz a5, 0x43fde',0x43f6c:'lw a5, 4(a1)',0x43f70:'qk.c.lhu a5, 8(a1)',0x43f74:'qk.c.lhu a5, 10(a1)',0x43f78:'qk.c.lbu a5, 12(a1)',0x43f7c:'qk.c.lbu a5, 21(s0)',0x43f88:'blt a4, a5, 0x43fde',0x43f90:'li a2, 16',0x43fa2:'lw a3, 564(a5)',0x43faa:'sw a3, 480(a4)',0x43fae:'qk.c.lbu a4, 23(s0)',0x43fb6:'qk.c.lhu a0, 8(a5)',0x43fb8:'li a5, 1400',0x43fc0:'mul a0, a0, a5',0x43fc8:'li a3, 0',0x43fca:'li a1, 0',0x43fd0:'qk.c.sb a0, 23(s0)',0x43fd2:'lui a0, 0x44',0x43fd6:'addi a0, a0, -670',0x43fdc:'li a0, 0',
        0x43ff2:'sw zero, 28(a5)',0x43ff6:'addi a4, a4, -1658',0x43ffe:'sw a4, 564(a5)',0x4400a:'li a3, -1',0x44010:'sw a3, 4(a5)',0x44012:'sw a4, 8(a5)',0x44014:'sb zero, 12(a5)',0x4401c:'sw a3, 616(a5)',
        0x43b12:'sw a0, 560(a5)',0x43b16:'jalr a0',0x43b1e:'sw a0, 436(a5)',0x43b22:'li a0, 0',
        0x43d6a:'lw a5, 564(s2)',0x43d7a:'jalr a5',0x43d7c:'li s4, 1600',0x43d80:'mulhu a1, a0, s4',0x43d88:'lhu s5, 8(s2)',0x43d8c:'li a3, 0',0x43d8e:'mv a2, s5',0x43d90:'mul a0, a0, s4',0x43da0:'lw s0, 24(a4)',0x43da2:'mv s1, a0',0x43da4:'li a0, 0',0x43da6:'beq s0, s1, 0x43dd2',0x43dae:'sub a0, s1, s0',0x43db2:'bltu s0, s1, 0x43dce',0x43db6:'lw a0, 4(s2)',0x43dbe:'mulhu a1, s4, a0',0x43dc2:'mul a0, s4, a0',0x43dca:'sub a0, a0, s0',0x43dcc:'add a0, a0, s1',0x43dce:'sw s1, 24(s3)',
        0x43524:'lw a5, 560(a5)',0x43536:'beqz a5, 0x43540',0x43538:'jalr a5',0x4353a:'lw a5, 20(s0)',0x4353c:'add a0, a0, a5',0x4353e:'sw a0, 20(s0)',0x43540:'lw a0, 20(s0)',
        0x2000098a:'lw a3, 524(a4)',0x20000992:'and a5, a5, a3',0x20000994:'sw a5, 524(a4)',0x20000998:'nop',0x2000099a:'nop',0x200009a4:'lw a0, 28(a5)',0x200009a6:'lw a5, 616(a4)',0x200009aa:'sw a3, 524(a4)',0x200009ae:'slli a0, a0, 0x1a',0x200009b0:'not a5, a5',0x200009b4:'srli a5, a5, 0x6',0x200009b6:'or a0, a0, a5'}
    need(all(ops[pc]['opcode']==v for pc,v in expected.items()),'Actual clock validation,copy,provider,baseline,default-counter and public getter instruction roles')
    need((0x44<<12)-670==0x43d62 and(0x20001<<12)-1658==0x20000986,'Actual two numeric CODE pointer values correspond to selected real bodies')
    defaults=(0x328<<12)-1518;need((defaults&65535,defaults>>16)==(31250,50),'Actual default nominal frequency/accuracy word')
    need((0xf4<<12)+576==1000000 and 65535*1400<2**32,'Actual arithmetic-helper denominator and no frequency-product32-bit overflow')
    arithmetic_calls=[0x43fcc,0x43d94,0x43dc6];need(all(B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)==(17,0x6df1a)for pc in arithmetic_calls),'Three actual unresolved arithmetic-helper calls')
    need(B['decode_control'](bytes.fromhex(ops[0x43fda]['bytes']),0x43fda)==(45,0x43b0a),'Actual TimerInit provider-registration call')
    header=(ROOT/E['header']).read_text(encoding='gb18030');need('current system clock (in 0.625ms)'in header,'Official documented public-clock unit')
    return dict(passed=True,static_only=True,functions=functions,official_bindings=E['official_bindings'],clock_configuration_bytes=16,clock_field_offsets=dict(getClockValue=0,ClockMaxCount=4,ClockFrequency=8,ClockAccuracy=10,irqEnable=12),
        TimerInit=dict(entry=0x43f46,optional_rcCB_storage=0x2000321c,nonnull_config_requires_nonzero_fields=['getClockValue','ClockMaxCount','ClockFrequency','ClockAccuracy'],nonzero_irqEnable_additionally_requires_BLE_connection_sum_le=2,accepted_config_copied_bytes=16,raw_clock_callback_storage=0x200031e0,clock_config_storage=0x20003234,normal_completion_return=0,local_invalid_config_return=1,normal_return_is_not_hardware_success=True),
        default_config=dict(callback=0x20000986,ClockMaxCount=0xffffffff,nominal_ClockFrequency=31250,nominal_ClockAccuracy=50,irqEnable=0),
        WaitWindow=dict(storage=0x20003203,update_only_when_zero=True,helper_PC=0x43fcc,helper=0x6df1a,helper_arguments=['ClockFrequency*1400','0','1000000','0'],stored_result='low8(returned_A0)',external_helper_division_contract_proved=False),
        provider_registration=dict(entry=0x43b0a,storage=0x20003230,immediately_calls_entry_A0=True,known_TimerInit_target=0x43d62,stores_callback_return_to=0x200031b4,callback_may_itself_update_that_same_word=True,repeat_initialization_baseline_contract_proved=False),
        delta_provider=dict(entry=0x43d62,raw_clock_pointer_storage=0x20003234,scale_constant=1600,helper=0x6df1a,first_helper_inputs='64-bit raw_counter*1600 divided-operand setup with ClockFrequency in A2 and0 in A3',baseline_storage=0x200031b4,return_if_same=0,return_if_new_gt_old='new_helper_result_low32-old_baseline',otherwise='second_helper_result_low32-old_baseline+new_helper_result_low32 (u32)',baseline_updated_to_new_when_changed=True,arithmetic_helper_contract_proved=False),
        public_getter=dict(entry=0x43520,provider_pointer_storage=0x20003230,accumulator=0x200031b0,nonnull_provider_return_added_mod2_32=True,documented_unit='0.625ms',actual_time_accuracy_proved=False),
        default_getter=dict(entry=0x20000986,saved_modified_restored_MMIO=0x4002420c,counter_MMIO=0x40024268,software_rollover_word=0x200031b8,return_expression='(software_word<<26) | ((~counter_word)>>6) in u32',physical_MMIO_semantics_proved=False),
        raw_CODE_pointer_values_have_real_bodies=True,numeric_CODE_addresses_are_not_linker_relocations=True,opaque_transfers=E['opaque_transfers'],raw_dependencies=E['raw_dependencies'],callees_preserving_SP_is_assumed=True,whole_program_stack_IRQ_or_callback_effects_proved=False,physical_frequency_or_range_proved=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        r=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,r
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_63dd0','tsl9_candidate_external_flash_6df1a','tsl9_candidate_external_ram_2000061a','tsl9_candidate_external_ram_20002610'}and len(u)==5 and facts(path)==(a,d,remaining,sorted(rel)),'Every input byte,symbol and relocation retained;real copy provider resolves while the arithmetic helper remains genuine')
    need(sum(len(v[1])for v in a.values())==3512 and len(d)==312 and len(rel)==224,'Exact3512-byte composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=3512,instructions=1242,positive_FUNC_regions=312,relocations=224,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,clock_numeric_CODE_targets_have_real_bodies=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm)
    need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh3038-byte timer,scheduler,binding,layout and Flash proofs retained')
    app=app_clock_contract(N);contract=clock_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh nonloadable scheduler composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ composition objects identical')
    return dict(schema='TSL9-public-SDK-clock-services-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,app_clock_contract=app,clock_contract=contract,prior_timer_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_bytes=3038,prior_timer_scheduler_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable registration receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=474,instructions=168,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},startup_completed_proved=False,physical_atomicity_proved=False,APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
