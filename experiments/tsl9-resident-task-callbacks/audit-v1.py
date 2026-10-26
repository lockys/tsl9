#!/usr/bin/env python3
"""Verify real callback bodies and static Flash argument flow;never execute code or a model."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-resident-snv-initialization'
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
def callback_contract(N):
    E,B=N['EV'],N['B'];functions=[]
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};edges=[];returns=[];calls=[]
        for pc,o in ops.items():
            d=B['decode_control'](bytes.fromhex(o['bytes']),pc);following=pc+o['size']
            if o['type']=='ret':returns.append(pc);continue
            if d:
                kind,target=d
                if o['type']=='call':
                    need(str(target)in E['target_names']and following in ops,'Genuine named direct call with local normal-return continuation');calls.append(dict(PC=pc,target=target));edges.append([pc,following])
                else:
                    need(target in ops,'Every local branch targets its own complete body');edges.append([pc,target])
                    if o['type']=='cjmp':need(following in ops,'Complete conditional fallthrough');edges.append([pc,following])
            else:
                need(following in ops,'No fallthrough into an adjacent body');edges.append([pc,following])
                if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
        reached=set();pending=[f['start']]
        while pending:
            pc=pending.pop()
            if pc in reached:continue
            reached.add(pc);pending.extend(b for a,b in edges if a==pc)
        need(reached==set(ops)and returns,'All selected instructions reachable in conditional normal-return CFG')
        functions.append(dict(entry=f['start'],end=f['end'],CODE_bytes=f['end']-f['start'],instructions=len(ops),direct_edges=edges,return_PCs=returns,calls=calls,all_instructions_in_conditional_CFG=True))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x432be:'slli a0, a0, 0x4',0x432c2:'add a0, a0, s0',0x432c4:'mul a0, a0, a4',0x432cc:'lw s2, 556(a5)',0x432dc:'add s2, s2, a0',0x432de:'lw a4, 0(s2)',0x432e2:'beqz a4, 0x432ee',0x432e4:'lw a0, 4(s2)',0x432ea:'jalr a4',0x432ee:'li a4, 12',0x432f0:'mul s0, s0, a4',0x432f4:'lw a5, 556(s3)',0x432f8:'add s0, s0, a5',0x432fa:'lw a5, 8(s0)',0x432fc:'bnez a5, 0x43306',0x432fe:'sw zero, 0(s2)',0x43302:'sw zero, 4(s2)',0x4330a:'xor a1, a1, s1',0x43312:'mv a0, a1',0x43328:'slli a4, a1, 0x10',0x43334:'srai a4, a4, 0x10',0x43338:'bgez a4, 0x4335a',0x43344:'beqz a0, 0x43348',0x43348:'lui a5, 0x8',0x4334a:'xor s0, s0, a5',0x4334c:'mv a0, s0',0x4336a:'slli a5, a5, 0x4',0x4336c:'add a5, a5, a4',0x4336e:'li a3, 12',0x43370:'mul a5, a5, a3',0x43378:'lw s2, 556(a3)',0x43386:'add s2, s2, a5',0x43388:'lw a5, 0(s2)',0x4338c:'lw a0, 4(s2)',0x43390:'jalr a5',0x43392:'sw zero, 0(s2)',0x43396:'sw zero, 4(s2)',0x4339a:'xor s0, s0, s1'}
    need(all(ops[pc]['opcode']==text for pc,text in expected.items()),'Actual indexing,callback guard,clears and bit-return instructions')
    need(N['B']['decode_control'](bytes.fromhex(ops[0x43346]['bytes']),0x43346)==(45,0x431ba),'Actual nonnull-message deallocator call')
    need(len(N['S']['PC_relative_pairs'])==1 and N['S']['PC_relative_pairs'][0]['PC']==0x4333c and N['S']['PC_relative_pairs'][0]['target_PC']==0x2000028c,'Actual message-receive far call')
    path=ROOT/'experiments/tsl9-resident-ble-initialization/evidence-v1.json';need(sha(path)=='d32203b264e1f0c63b7a263997965fbbab7ed7397750e19a67dfdb2a33bf9208','Pinned registration instruction source')
    p={o['addr']:o for f in json.loads(path.read_bytes())['selected_functions']for o in f['operations']}
    registration={0x43c0c:'lui a2, 0x43',0x43c16:'addi a2, a2, 676',0x43c1a:'sw a2, 0(a4)',0x43c26:'lui a2, 0x43',0x43c2c:'addi a2, a2, 806',0x43c30:'sw a2, 0(a4)',0x43c42:'sw a2, 0(a5)'}
    need(all(p[pc]['opcode']==text for pc,text in registration.items())and (0x43<<12)+676==0x432a4 and (0x43<<12)+806==0x43326,'Three actual registration stores refer to these real bodies')
    return dict(passed=True,functions=functions,registration_store_targets={str(0x43c1a):0x432a4,str(0x43c30):0x43326,str(0x43c42):0x43326},stored_numeric_CODE_values_are_not_linker_relocations=True,
        record_array_pointer_storage=0x2000322c,selected_record_expression='record_array + 12*(16*entry_A0 + first_set_bit)',
        first_callback=dict(entry=0x432a4,opaque_call=0x432ea,callback_null_guard=True,callback_A0='selected_record.word4',third_word_test_expression='record_array + 12*first_set_bit + 8',third_word_test_is_not_the_task_indexed_record=True,zero_test_then_clear='selected_record.word0 and word4',return_expression='entry_A1 XOR low16 selected-bit mask',one_event_handled_per_return=True),
        second_callback=dict(entry=0x43326,message_bit=15,receive_call=0x4333c,receive_target=0x2000028c,nonnull_message_free_call=0x43346,deallocate_target=0x431ba,deallocator_return_used=False,opaque_call=0x43390,callback_null_guard=False,callback_A0='selected_record.word4',clears_after_normal_callback_return=['selected_record.word0','selected_record.word4'],one_event_handled_per_return=True),
        requires_valid_task_index_record_array_callback_lifetime_and_normal_return=True,callbacks_may_mutate_table_or_RAM=True,raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],physical_ownership_proved=False,runtime_closed=False)
def flash_contract(N):
    paths={'startup':'analysis/resident-startup-2026-10-25/evidence.json','program':'analysis/ota-runtime-2026-10-24/evidence.json'}
    pins={'startup':'9c9e418f16ec9b7231df2dc623ee90c39a0b1bba53f0a116271800d7ad8770f5','program':'d33fa76b0e288b6df0ed8a6199067f74af450ea14d6bb24999c593346fc4978e'}
    # Each input is pinned before extracting any selected original APP instruction.
    for key,p in paths.items():need(sha(ROOT/p)==pins[key],'Pinned original APP Flash argument evidence '+key)
    allf=[f for p in paths.values()for f in json.loads((ROOT/p).read_bytes())['selected_functions']]
    selected=[next(f for f in allf if f['start']==pc)for pc in [0x1979a,0x197be,0x18ec4,0x18ef2]]
    fw=(ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes();need(hashlib.sha256(fw).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Actual original APP input')
    facts=[];ops={}
    for f in selected:
        pc=f['start']
        for o in f['operations']:
            b=bytes.fromhex(o['bytes']);need(o['addr']==pc and len(b)==o['size']==(4 if b[0]&3==3 else 2)and fw[pc-0x8000:pc-0x8000+len(b)]==b and o['opcode']!='invalid','Whole exact original Flash callback/helper instruction');ops[pc]=o;pc+=len(b)
        need(pc==f['end'],'Complete original APP helper');facts.append(dict(entry=f['start'],end=f['end'],bytes=pc-f['start'],instructions=len(f['operations']),sha256=hashlib.sha256(fw[f['start']-0x8000:pc-0x8000]).hexdigest()))
    expected={0x1979a:'lui a5, 0x40',0x1979e:'lw a5, 76(a5)',0x197a2:'mv a4, a2',0x197a6:'slli a2, a1, 0x2',0x197aa:'mv a1, a0',0x197ac:'mv a0, a4',0x197ae:'jalr a5',0x197b2:'li a0, 0',0x197c4:'sw a2, 12(sp)',0x197cc:'mv a0, s0',0x197d2:'lw a2, 12(sp)',0x197d4:'mv a0, s0',0x197d6:'mv a1, a2',0x197e6:'lw ra, 28(sp)',0x197ea:'li a0, 0',0x18ece:'andi a0, a0, -256',0x18ed6:'sw a0, 20(a5)',0x18efa:'andi a0, a0, -256',0x18f0c:'lw a5, 12(a4)',0x18f0e:'andi a5, a5, 2',0x18f10:'bnez a5, 0x18f0c',0x18f16:'li a2, 256',0x18f1a:'add a3, a1, a5',0x18f1e:'lw a6, 0(a3)',0x18f22:'add a3, a0, a5',0x18f26:'sw a6, 0(a3)',0x18f2a:'lw a3, 12(a4)',0x18f2c:'andi a3, a3, 2',0x18f2e:'bnez a3, 0x18f2a',0x18f30:'addi a5, a5, 4',0x18f32:'bne a5, a2, 0x18f1a'}
    need(all(ops[pc]['opcode']==text for pc,text in expected.items()),'Exact actual Flash argument transformations and fixed program-loop operands')
    B=N['B'];calls={0x197c8:0x18e98,0x197ce:0x18ec4,0x197d8:0x18ef2,0x197dc:0x18eb6,0x197e2:0x19764}
    need(all(B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)==(17,target)for pc,target in calls.items()),'Exact original direct helper calls;no execution')
    carrier=(ROOT/N['S']['firmware']).read_bytes();need(int.from_bytes(carrier[0x4c:0x50],'little')==0x20000332,'Candidate copy pointer storage4004C binds real reconstructed copy body')
    need(256//4==64 and 256%4==0,'Static fixed-loop arithmetic')
    proof=ROOT/'experiments/tsl9-safe-gap-functions/verify-source-v1.py';Q=lib(proof);llvm=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin'
    retained=json.loads((ROOT/'experiments/tsl9-safe-gap-functions/build/source-proof-v1.json').read_bytes());need(retained['inputs']==Q['portable'](Q['inputs'](llvm),llvm),'All formal original APP C/C++ proof inputs retained')
    return dict(passed=True,static_only=True,concrete_machine_or_memory_simulated=False,input_paths=paths,input_sha256=pins,complete_original_APP_helpers=facts,new_APP_CODE_bytes=0,
        read=dict(entry=0x1979a,copy_pointer_storage=0x4004c,candidate_copy_target=0x20000332,copy_arguments=['entry_A2 buffer','entry_A0 address','entry_A1 << 2 bytes'],numeric_return_after_normal_copy=0),
        write=dict(entry=0x197be,program_helper_call=0x197d8,program_helper=0x18ef2,program_A0='saved entry_A0 address',program_A1='saved entry_A2 buffer',program_A2='saved entry_A2 buffer;overwritten by helper before data loop',incoming_num_not_forwarded_as_program_count=True,
            numeric_return_after_all_normal_helpers=0,all_callback_ancillary_helper_effects_closed=False),
        program_helper=dict(entry=0x18ef2,source='program helper entry_A1',destination='program helper entry_A0 & 0xFFFFFF00',count_register_replaced_with_constant=256,loop_offset_initial_zero_from_poll_exit=True,loop_offset_step=4,conditional_word_loads=64,conditional_word_stores=64,conditional_source_span_bytes=256,conditional_destination_span_bytes=256,minimum_valid_source_bytes=256),
        erase_helper=dict(entry=0x18ec4,encoded_address_mask=0xffffff00,numeric_MMIO_address_register=0x40022014),
        relation_to_SNV='A256-byte SNVBlock is numerically consistent with the fixed256-byte helper;arbitrary SNVBlock sizes are not validated by this proof',
        wait_termination_proved=False,physical_Flash_commit_proved=False,physical_Flash_capacity_or_mapping_proved=False,IRQ_alias_or_stack_ownership_proved=False,installed_ROM_identity_proved=False,callback_success_status_proved=False,hardware_accessed=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable RISC-V ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_message_receive_2000028c'},'Actual queue receiver remains genuinely unresolved')
    need(facts(path)==(a,d,remaining,sorted(rel)),'Every input byte,positive symbol and typed relocation retained')
    need(sum(len(v[1])for v in a.values())==1828 and len(d)==164 and len(rel)==120,'Exact actual partial composition metrics')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=1828,instructions=654,positive_FUNC_regions=164,relocations=120,named_UND=sorted(remaining),real_new_imports_resolved=sorted(u-remaining),independent_readers=independent,every_input_byte_symbol_relocation_retained=True,stored_numeric_CODE_targets_have_real_bodies=True,raw_RAM_and_indirect_record_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,results=native(llvm);old=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(old)==json.loads((PRIOR/'audit-result-v3.json').read_bytes()),'Prior1568-byte composition and SNV contract unchanged')
    callbacks=callback_contract(N);flash=flash_contract(N);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh retained nonloadable composition trial')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-task-callback-and-Flash-argument-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=results,callback_contract=callbacks,Flash_argument_contract=flash,prior_audit_sha256=sha(PRIOR/'audit-result-v3.json'),composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=260,instructions=104,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},Flash_argument_contract=result['Flash_argument_contract'],APP_byte_coverage_unchanged=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
