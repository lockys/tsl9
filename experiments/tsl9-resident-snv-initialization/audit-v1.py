#!/usr/bin/env python3
"""Read positive native evidence and partially compose real SDK bodies. No execution model."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-ble-initialization'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='SNV_positive_static_library')
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every actual compile input unchanged')
    results={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete artifacts and include dependencies')
        results[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(results[mode]['CODE']==v['result']and results[mode]['ABI']==v['ABI_result'],'Fresh native/ABI proof matches actual compile receipt')
    need(results['c']==results['cpp'],'Complete C11/C++17 objects identical')
    return N,results
def static_contract(N):
    E,B=N['EV'],N['B'];functions=[]
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};edges=[];returns=[];calls=[]
        for pc,o in ops.items():
            d=B['decode_control'](bytes.fromhex(o['bytes']),pc);nextpc=pc+o['size']
            if o['type']=='ret':returns.append(pc);continue
            if d:
                kind,target=d;need(target in ops,'All direct branches stay in their complete original body')
                edges.append((pc,target))
                if o['type']=='cjmp':need(nextpc in ops,'Complete branch fallthrough');edges.append((pc,nextpc))
            else:
                need(nextpc in ops,'No implicit fallthrough into an adjacent function');edges.append((pc,nextpc))
                if o['type']=='ucall':calls.append(pc)
        reached=set();pending=[f['start']]
        while pending:
            pc=pending.pop()
            if pc in reached:continue
            reached.add(pc);pending.extend(b for a,b in edges if a==pc)
        need(reached==set(ops)and returns,'Every instruction belongs to entry CFG under conditional normal call return')
        functions.append(dict(entry=f['start'],end=f['end'],CODE_bytes=f['end']-f['start'],instructions=len(ops),direct_edges=edges,return_PCs=returns,indirect_call_PCs=calls,all_instructions_reached_in_conditional_CFG=True))
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    required={
        0x4329a:'lui a5, 0x20003',0x4329e:'sw zero, 408(a5)',0x432a2:'ret',
        0x4402e:'lw a0, 8(a5)',0x44036:'bnez a0, 0x44046',0x44038:'li a0, 1',
        0x4404a:'lw a5, 56(s0)',0x4404e:'lw a4, 60(s0)',0x44052:'addi a2, sp, 12',0x44054:'li a1, 1',0x44056:'jalr a5',
        0x44058:'lw a4, 8(s0)',0x4405a:'lw a5, 12(sp)',0x4405c:'beq a4, a5, 0x44038',
        0x44060:'qk.c.lhu a0, 12(s0)',0x44062:'li a1, 78',0x44076:'sw a0, 32(a4)',0x4407c:'beqz a0, 0x44038',
        0x4407e:'qk.c.lhu a2, 12(s0)',0x44080:'li a1, 255',0x44084:'li s2, 0',
        0x4408e:'qk.c.lbu a5, 14(s0)',0x44090:'lw a2, 32(s1)',0x44092:'blt s2, a5, 0x440ac',
        0x44096:'mv a0, a2',0x440a0:'li a0, 0',0x440a2:'sw zero, 32(s1)',0x440a6:'sw zero, 36(s1)',0x440aa:'j 0x4403a',
        0x440ac:'qk.c.lhu a1, 12(s0)',0x440ae:'lw a0, 8(s0)',0x440b0:'lw a4, 60(s0)',0x440b2:'mul a5, a1, s2',0x440b6:'srli a1, a1, 0x2',0x440b8:'addi s2, s2, 1',0x440ba:'add a0, a0, a5',0x440bc:'sw a0, 0(a2)',0x440be:'jalr a4',0x440c0:'j 0x4408e'}
    need(all(ops[pc]['opcode']==text for pc,text in required.items()),'Exact actual SNV field loads,parameters and local paths')
    pairs=N['S']['PC_relative_pairs'];need({p['PC']:p['target_PC']for p in pairs}=={0x4406a:0x20000040,0x44086:0x2000039c,0x44098:0x20000110},'Real heap allocate,fill and release call targets')
    need(ops[0x44058]['opcode']=='lw a4, 8(s0)'and ops[0x440c0]['opcode']=='j 0x4408e','Both Flash callback return values unused in original caller')
    isbuf={o['addr']:o for o in E['selected_functions'][0]['operations']}
    expected={0x200004bc:'lui a4, 0x40024',0x200004c0:'lw a5, 524(a4)',0x200004c4:'sw zero, 524(a4)',0x200004c8:'fence.i',0x200004cc:'beqz a0, 0x200004d4',0x200004ce:'add a4, a0, a2',0x200004d2:'bnez a2, 0x200004e0',0x200004d8:'sw a5, 524(a4)',0x200004dc:'li a0, 0',0x200004e2:'lbu a3, -1(a0)',0x200004e6:'bne a3, a1, 0x200004d4',0x200004f2:'sw a5, 524(a4)',0x200004f6:'li a0, 1'}
    # Independently constrain the original 32-bit ADD operands as well as decoder text.
    need(bytes.fromhex(isbuf[0x200004ce]['bytes'])==bytes.fromhex('3307c500'),'Actual ADD A4,A0,A2,not a guessed compressed mnemonic')
    need(all(isbuf[pc]['opcode']==text for pc,text in expected.items()),'Exact buffer predicate/MMIO paths')
    return dict(passed=True,functions=functions,normal_callback_return_is_an_assumption=True,all_local_control_targets_within_original_bodies=True,
        message_global_zero=0x20003198,configuration_base=0x200031ec,SNVAddr_offset=8,SNVBlock_offset=12,SNVNum_offset=14,readFlashCB_offset=56,writeFlashCB_offset=60,
        read_call=dict(PC=0x44056,A0='SNVAddr',A1=1,A2='original entry SP-20 (local word)',return_value_used=False,callback_output_validity_proved=False),
        allocate_call=dict(PC=0x4406a,target=0x20000040,A0='SNVBlock',A1=78),fill_call=dict(PC=0x44086,target=0x2000039c,A0='allocated buffer',A1=255,A2='SNVBlock'),
        write_call=dict(PC=0x440be,A0='SNVAddr + SNVBlock * loop_index',A1='SNVBlock >> 2',A2='allocated buffer with first word replaced by write address',return_value_used=False,flash_count_units_confirmed=False,requires_valid_at_least_four_byte_buffer=True),
        local_return_values=dict(one='disabled SNV,missing callback,first word equals SNVAddr,or allocation failure',zero='loop finishes,real heap release returns,then pointer/state words cleared'),
        return_code_is_not_flash_success_proof=True,loop_termination_requires_stable_configuration_and_normal_callbacks=True,
        isbufset=dict(null_or_zero_length_return=0,all_equal_return=1,comparison_uses_full_A1_register=True,MMIO=0x4002420c,physical_MMIO_semantics_proved=False),
        raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],historical_symbol_label=E['historical_symbol_label'],target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        allocated={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']}
        defined={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']}
        und={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        rel=sorted((e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations)
        return allocated,defined,und,rel
    allocated={};defined={};undefined=set();rel=[]
    for p in inputs:
        a,d,u,r=facts(p);need(not set(allocated).intersection(a)and not set(defined).intersection(d),'Unique real input code owners')
        allocated.update(a);defined.update(d);undefined.update(u);rel+=r
    remaining=undefined-set(defined);need(not remaining and len(undefined)==6,'Six real cross-input imports resolved; no fake provider')
    need(facts(path)==(allocated,defined,remaining,sorted(rel)),'Every input byte,positive FUNC and typed relocation retained')
    need(sum(len(v[1])for v in allocated.values())==1568 and len(defined)==138 and len(rel)==104,'Exact1568-byte composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=1568,instructions=550,positive_FUNC_regions=138,relocations=104,named_UND=[],real_named_imports_resolved=sorted(undefined),
        every_input_byte_symbol_relocation_retained=True,independent_readers=independent,raw_callback_CODE_dependencies=[0x432a4,0x43326],raw_RAM_and_callback_dependencies_provided=False,
        named_UND_zero_is_not_runtime_closure=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,results=native(llvm);P=lib(PRIOR/'audit-v1.py');old=P['audit'](llvm);need(old==json.loads((PRIOR/'audit-result-v2.json').read_bytes()),'All preceding1336-byte composition and APP contract proof unchanged')
    contract=static_contract(N);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only nonloadable composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')]
            p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Native partial link failed; preserve trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-SNV-helper-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=results,static_contract=contract,
        prior_audit_sha256=sha(PRIOR/'audit-result-v2.json'),prior1336_object_sha256=old['composition']['c']['object_sha256'],composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,
        Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=232,instructions=83,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},APP_byte_coverage_unchanged=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
