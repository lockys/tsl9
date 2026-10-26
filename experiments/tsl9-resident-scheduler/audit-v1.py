#!/usr/bin/env python3
"""Verify the real RAM-JT0 scheduler,binding and local CFG without executing it."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-task-registration'
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
def startup_binding(N):
    E=N['EV'];raw=(ROOT/E['firmware']).read_bytes();fragments=E['startup_binding_fragments'];ops={}
    for f in fragments:
        at=f['start'];source=b''
        for o in f['operations']:
            b=bytes.fromhex(o['bytes']);need(o['addr']==at and len(b)==o['size']==(4 if b[0]&3==3 else 2)and b==raw[at-0x40000:at-0x40000+len(b)]and o['opcode']!='invalid','Whole captured standard startup fragment');ops[at]=o;source+=b;at+=len(b)
        need(at==f['end']and __import__('hashlib').sha256(source).hexdigest()==f['original_sha256'],'Complete exact startup fragment hash')
    def word(pc):return int.from_bytes(bytes.fromhex(ops[pc]['bytes']),'little')
    def sx12(v):return v-4096 if v&2048 else v
    def lui(pc,rd):
        v=word(pc);need(ops[pc]['size']==4 and v&0xfff==(rd<<7)|0x37,'Actual standard LUI destination');return v&0xfffff000
    def addi(pc,rd,rs):
        v=word(pc);need(ops[pc]['size']==4 and v&0xfffff==(rs<<15)|(rd<<7)|0x13,'Actual standard ADDI fields');return sx12(v>>20)
    def pair(pc,rd,target_rd=None):
        a,b=word(pc),word(pc+4);need(a&0xfff==(rd<<7)|0x17,'Actual standard AUIPC destination');out=rd if target_rd is None else target_rd
        need(b&0xfffff==(rd<<15)|(out<<7)|0x13,'Actual adjacent ADDI field role');return(pc+(a&0xfffff000)+sx12(b>>20))&0xffffffff
    need(N['B']['decode_control'](bytes.fromhex(ops[0x40000]['bytes']),0x40000)==(17,0x6de7e),'Actual carrier entry jump;following header data not selected as code')
    gp,sp,seed_source,seed_destination,seed_end=[pair(pc,rd)for pc,rd in [(0x6de7e,3),(0x6de86,2),(0x6de8e,10),(0x6de96,11),(0x6de9e,12)]]
    need((gp,sp,seed_source,seed_destination,seed_end)==(0x20004000,0x20010000,0x40280,0x20000010,0x20000040),'Actual V1.31 seed operands;no V1.40 substitutions')
    table_base=lui(0x6de14,15);values=[lui(0x6de0e,14)+addi(0x6de18,14,14),lui(0x6de1e,14)+addi(0x6de22,14,14),lui(0x6de28,14)+addi(0x6de2c,14,14)]
    for pc,offset in [(0x6de1c,0),(0x6de26,4),(0x6de3c,8)]:
        v=word(pc);need(ops[pc]['size']==2 and v&0xe003==0xc000 and 8+((v>>2)&7)==14 and 8+((v>>7)&7)==15,'Actual compressed SW A4 through A5');decoded=((v>>10)&7)*8+((v>>6)&1)*4+((v>>5)&1)*64;need(decoded==offset,'Exact three RAM jump-table store offsets')
    need(table_base==0x20000000 and values==[0x200007d0,0x2000251c,0x20002e34],'Actual RAM jump-table values')
    source=lui(0x6de38,10)+addi(0x6de46,10,10);destination=lui(0x6de34,11)+addi(0x6de42,11,11);last=lui(0x6de30,12)+addi(0x6de3e,12,12)
    need((source,destination,last)==(0x402b0,0x20000040,0x20002e70),'Actual first word-copy operands')
    a,b=word(0x6de4a),word(0x6de4e);need(a&0xfff==0x97 and b&0xfffff==0x80e7 and(0x6de4a+(a&0xfffff000)+sx12(b>>20))&0xffffffff==0x20000010,'Actual call to captured seed word-copy helper')
    selected=E['selected_functions'][0];mapped=source+selected['start']-destination;need(mapped==selected['source_start']==0x40a40 and selected['end']<=last+4,'Complete scheduler lies inside the captured first copy prefix')
    zero_start=lui(0x40292,15)+addi(0x4029a,15,15);zero_last=lui(0x40296,14)+addi(0x4029e,14,14)
    need((zero_start,zero_last)==(0x20002ef8,0x20003614),'Actual later zero-loop range')
    second_source=lui(0x6de5a,10)+addi(0x6de66,10,10);second_start=lui(0x6de56,11)+addi(0x6de62,11,11);second_last=lui(0x6de52,12)+addi(0x6de5e,12,12)
    need((second_source,second_start,second_last)==(0x6eaa4,0x20002e70,0x20002ef8),'Actual second copy operands')
    mapping=json.loads((ROOT/E['mapping_proof']).read_bytes());need(sha(ROOT/E['mapping_proof'])==E['mapping_proof_sha256']and mapping['selected_carrier_sha256']==E['firmware_sha256'],'Pinned V1.31 mapping and inherited source-gap contract')
    gap=mapping['inherited_startup_gap'];need(gap['second_copy_source']==second_source and gap['requested_bytes']==second_last-second_start+4==140 and gap['captured_intersection_bytes']==136 and sum(v['bytes']for v in gap['missing_source'])==4,'Preserve the real sparse-source gap;no hole is filled')
    need(second_start>selected['end']and zero_start>selected['end']and second_start>table_base+12 and zero_start>table_base+12,'Later numeric write spans do not overlap table words or selected scheduler')
    header=(ROOT/E['header']).read_text(encoding='gb18030');need('RAM_BASE_ADDRESSS         0x20000000'in header and 'BLE_LIB_RAM_JT(0)'in header,'Official RAM binding retained')
    return dict(passed=True,SDK_V131_candidate_only=True,entry_jump=0x6de7e,observed_initial_GP=gp,observed_initial_SP=sp,seed_source=seed_source,seed_destination=seed_destination,seed_bytes=48,table_storage=table_base,table_values=values,table_store_PCs=[0x6de1c,0x6de26,0x6de3c],TMOS_SystemProcess_RAM_index=0,actual_candidate_scheduler=values[0],candidate200004FA_is_not_RAM_JT0=True,
        first_copy_source=source,first_copy_destination=destination,first_copy_last_word_inclusive=last,first_copy_bytes=last-destination+4,scheduler_source_span=[mapped,mapped+selected['end']-selected['start']],later_second_copy_destination=[second_start,second_last+4],later_zero_destination=[zero_start,zero_last+4],later_numeric_writes_do_not_overlap_selected_scheduler_or_table=True,
        inherited_second_copy_source_gap=gap,holes_filled=False,startup_completed_proved=False,installed_RAM_table_value_proved=False,installed_ROM_identity_proved=False,physical_RAM_MMIO_or_ISA_proved=False,
        assumptions=['relevant seed and first-copy instructions execute normally with valid stable source/RAM','conditional Xwchc profile applies to the selected scheduler','no IRQ,DMA,alias or later unreviewed store changes the table or code','the sparse second-copy gap remains unresolved;later zeroing cannot prove that read completes'])
def scheduler_contract(N):
    E,B=N['EV'],N['B'];f=E['selected_functions'][0];ops={o['addr']:o for o in f['operations']};named={int(k)for k in E['target_names']};pairs={v['PC']+4:v for v in N['S']['PC_relative_pairs']};edges=[];returns=[];tails=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']=='ret':returns.append(pc);continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in named and following in ops,'Genuine direct callee and normal-return continuation');calls.append(dict(PC=pc,target=target));edges.append([pc,following])
            elif target not in ops:need(o['type']=='jmp'and target in named,'Only a genuine external tail may leave selected body');tails.append(dict(PC=pc,target=target))
            else:
                edges.append([pc,target])
                if o['type']=='cjmp':need(following in ops,'Whole local branch fallthrough');edges.append([pc,following])
        else:
            need(following in ops,'No fallthrough into excluded following bytes');edges.append([pc,following])
            if o['type']=='ucall':calls.append(dict(PC=pc,target=pairs[pc]['target_PC']if pc in pairs else None))
    def reachable(start):
        pending=[start];seen=set()
        while pending:
            pc=pending.pop()
            if pc in seen:continue
            seen.add(pc);pending.extend(b for a,b in edges if a==pc)
        return seen
    need(reachable(f['start'])==set(ops)and returns==[0x2000095e]and tails==[dict(PC=0x200008be,target=0x2000061a)],'Complete150-instruction scheduler CFG with actual return and external tail')
    opaque=[v['PC']for v in calls if v['target']is None];need(opaque==[0x20000818,0x2000081e,0x2000090a,0x2000093c],'Exactly four opaque callback sites')
    need(0x2000090a not in reachable(0x2000090c),'At most one local registered-handler invocation per normal entry;callback reentry excluded')
    expected={0x20000830:'qk.c.lbu a2, 1(a5)',0x20000836:'lbu a5, 412(s0)',0x20000840:'qk.c.lhu a3, 0(a3)',0x20000844:'lbu a5, 412(s0)',0x20000848:'bltu a5, a2, 0x200008e4',0x200008e8:'qk.c.lhu a1, 0(a4)',0x200008ea:'sh zero, 0(a4)',0x200008ee:'lbu a0, 412(s0)',0x200008f6:'lw a5, 452(a5)',0x200008fa:'slli a4, a0, 0x2',0x20000902:'add a5, a5, a4',0x20000904:'lw a5, 0(a5)',0x20000906:'sh zero, 476(s5)',0x2000090a:'jalr a5',0x2000090c:'lhu a5, 476(s5)',0x20000910:'lbu a4, 412(s0)',0x20000914:'not a5, a5',0x20000918:'and a0, a0, a5',0x2000091a:'slli a5, a4, 0x1',0x2000091e:'lw a4, 484(s3)',0x20000922:'add a4, a4, a5',0x20000924:'qk.c.lhu a5, 0(a4)',0x20000926:'or a0, a0, a5',0x20000928:'qk.c.sh a0, 0(a4)',0x20000936:'lw a5, 456(s2)',0x2000093a:'beqz a5, 0x20000942',0x2000093c:'jalr a5',0x2000093e:'sw zero, 456(s2)'}
    need(all(ops[pc]['opcode']==v for pc,v in expected.items()),'Exact actual event-take,handler arguments,reloaded index,mask and merge instructions')
    changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(changes=={0x200007d0:-32,0x200008bc:32,0x2000095c:32},'Three actual affine local SP adjustments')
    pending=[(f['start'],0)];depths={}
    while pending:
        pc,before=pending.pop()
        if pc in depths:need(depths[pc]==before,'Consistent own-frame position at every join');continue
        depths[pc]=before;after=before+changes.get(pc,0);need(after in [-32,0],'Only original32-byte local frame positions')
        if pc in returns or pc in {v['PC']for v in tails}:need(after==0,'Own frame balanced at both exits')
        pending.extend((b,after)for a,b in edges if a==pc)
    need(set(depths)==set(ops),'All150 instructions included in static own-frame proof')
    return dict(passed=True,complete_range=[f['start'],f['end']],direct_edges=edges,return_PCs=returns,external_tails=tails,calls=calls,all_selected_instructions_in_conditional_CFG=True,
        task_index_byte=0x2000319c,registered_count_byte=0x2000319d,event_array_pointer=0x200031e4,handler_array_pointer=0x200031c4,event_clear_mask_halfword=0x200031dc,
        event_take='load event halfword into A1 and clear its slot before calling',handler_A0='current task-index byte',handler_A1='taken event halfword',handler_pointer='handler_array[current_task]',handler_null_check_present=False,
        clear_mask_zeroed_before_handler=True,current_task_index_reloaded_after_handler=True,event_merge_low16='(returned_A0 & ~live_clear_mask) | live_pending_event_halfword at the reloaded current task index',
        local_handler_call_sites=1,registered_handler_calls_at_most_one_in_local_CFG=True,opaque_callback_reentry_excluded_from_local_bound=True,own_frame_bytes=32,own_frame_balanced_at_normal_return_and_external_tail=True,callee_and_global_IRQ_stack_budget_proved=False,
        opaque_transfers=E['opaque_transfers'],raw_dependencies=E['raw_dependencies'],all_callee_effects_bounded=False,physical_atomicity_or_event_race_equivalence_proved=False,callback_lifetime_or_callability_proved=False,runtime_closed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        r=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,r
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input code owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    need(u==set(N['S']['undefined'])and len(u)==4 and facts(path)==(a,d,u,sorted(rel)),'Every input byte,positive symbol and relocation retained;four genuine callee imports remain')
    need(sum(len(v[1])for v in a.values())==2750 and len(d)==247 and len(rel)==181,'Exact2750-byte composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=2750,instructions=971,positive_FUNC_regions=247,relocations=181,named_UND=sorted(u),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,official_RAM_JT0_has_real_body=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm)
    need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh2312-byte registration,layout and Flash proofs retained')
    binding=startup_binding(N);contract=scheduler_contract(N);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh nonloadable scheduler composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ composition objects identical')
    return dict(schema='TSL9-public-SDK-RAM-JT0-scheduler-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,startup_binding=binding,scheduler_contract=contract,prior_registration_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_bytes=2312,prior_registration_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable registration receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=438,instructions=150,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},startup_completed_proved=False,physical_atomicity_proved=False,APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
