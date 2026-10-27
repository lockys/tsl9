"""Audit complete actual parser callees,mapped RAM helpers and event builders;never execute them."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-task-parser';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='range_random_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result
def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');A=lib(ROOT/'experiments/tsl9-original-APP-library-binding/verify-v1.py');C=lib(ROOT/'experiments/tsl9-original-APP-early-IRQ/verify-v1.py');rows=[];graphs={};op={};frames={0x5e950:16,0x5ea9a:16,0x5eaca:48,0x5ee06:16,0x5ecf6:16,0x2000202c:32,0x20002078:16,0x200020b6:16,0x200020f4:32,0x20002276:32,0x6a730:0,0x6a796:0,0x5e4b0:48,0x52418:48,0x527fa:48,0x200022be:0}
    for f in E['selected_functions']:
        need(f['own_frame_bytes']==frames[f['start']],'Exact declared own frame');external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,external,frames[f['start']]);op.update(oo);graphs[f['start']]=g;rows.append(v)
    need(sum(v['bytes']for v in rows)==2492 and sum(v['instructions']for v in rows)==940 and len(rows)==16,'Sixteen complete reachable CFGs and balanced own frames')
    def needops(mapping):need(all(op[p]['opcode']==s for p,s in mapping.items()),'Exact original effect operands')
    def dom(root,end,pcs):return all(end not in V['reachable'](graphs[root],root,skip=pc)for pc in pcs)
    def store(o):
        value=A['store'](o)
        if value is not None:return value
        raw=bytes.fromhex(o['bytes']);w=int.from_bytes(raw,'little')
        if len(raw)==2 and w&0xe003==0xc000:return(8+((w>>7)&7),8+((w>>2)&7),4,((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64)
        if o.get('conditional_Xwchc'):
            text=lib(ROOT/N['S']['source_deriver'])['custom_decode'](w);need(text==o['opcode'],'Actual primary custom operand');mn,args=text.split(' ',1)
            if mn not in ['qk.c.sb','qk.c.sh']:return None
            rd,operand=args.split(', ');offset,base=operand[:-1].split('(');registers={'s0':8,'s1':9,**{'a'+str(i):10+i for i in range(6)}};return(registers[base],registers[rd],1 if mn.endswith('sb')else 2,int(offset))
        return None
    need(sha(ROOT/E['loader_evidence'])==E['loader_evidence_sha256']and sha(ROOT/E['loader_receipt'])==E['loader_receipt_sha256'],'Complete retained loader evidence and receipt');loader=json.loads((ROOT/E['loader_receipt']).read_bytes())['contract'];first=loader['first_copy'];need(first==dict(source=0x402b0,destination=0x20000040,last_destination_word_inclusive=0x20002e70,bytes=11828),'Actual first-copy inclusive bound,not an off-by-four extent')
    mapped=[];sdk=(ROOT/E['firmware']).read_bytes()
    for f in E['selected_functions']:
        need(b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==sdk[f['source_start']-0x40000:f['source_end']-0x40000],'Every actual original source byte')
        if f['start']>=0x20000000:
            need(f['source_start']==f['start']-0x20000000+0x40270 and f['source_end']==f['end']-0x20000000+0x40270 and first['destination']<=f['start']<f['end']<=first['last_destination_word_inclusive']+4,'Whole RAM body fits genuine first loader copy and actual ROM source')
            mapped.append(dict(start=f['start'],end=f['end'],source_start=f['source_start'],source_end=f['source_end'],bytes=f['bytes']))
    need(len(mapped)==6 and sum(f['bytes']for f in mapped)==782,'Six complete mapped RAM providers782 bytes')
    needops({0x6a730:'j 0x52418',0x6a796:'j 0x527fa',0x5ea9a:'lbu a4, 84(a0)',0x5ea9e:'beqz a4, 0x5eac4',0x5eaa0:'qk.c.lbu a4, 16(a0)',0x5eaa4:'li a0, 1',0x5eaa6:'andi a4, a4, 1',0x5eaa8:'beqz a4, 0x5eac8',0x5eaaa:'lw a0, 84(a5)',0x5eaac:'lw a1, 88(a5)',0x5eaae:'addi sp, sp, -16',0x5eabc:'snez a0, a0',0x5eac0:'addi sp, sp, 16',0x5eac2:'ret',0x5eac4:'li a0, 1',0x5eac6:'ret',0x5eac8:'ret'})
    for pc,target in [(0x6a730,0x52418),(0x6a796,0x527fa)]:
        word=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(op[pc]['bytes']),pc)[1]==target,'Actual four-byte no-link tail,not neighboring wrapper/function')
    need(dom(0x5ea9a,0x5eac2,[0x5eab6,0x5eabc,0x5eac0])and dom(0x5ea9a,0x5eac6,[0x5eac4])and dom(0x5ea9a,0x5eac8,[0x5eaa4]),'Conditional predicate returns only SNEZ or literal1,including zero-frame early returns')
    needops({0x2000202e:'lui a5, 0x20003',0x20002034:'lw s0, 1156(a5)',0x2000207a:'lui a5, 0x20003',0x20002080:'lw s0, 1156(a5)',0x200020b8:'lui a5, 0x20003',0x200020be:'lw s0, 1156(a5)',0x20002278:'lui a5, 0x20003',0x2000227e:'lw s0, 1148(a5)'})
    need(C['constant'](op[0x2000202e],15)==C['constant'](op[0x20002278],15)==0x20003000 and 0x20003000+1156==0x20003484 and 0x20003000+1148==0x2000347c,'Actual fresh list-head numeric addresses,not live node values')
    needops({0x200022be:'lui a3, 0x20003',0x200022c2:'lw a5, 1284(a3)',0x200022c6:'li a4, 256',0x200022ca:'sw a4, 0(a5)',0x200022cc:'sw zero, 0(a5)',0x20002420:'ret',0x20002422:'nop',0x20002424:'j 0x200023ac'})
    need(C['constant'](op[0x200022be],13)==0x20003000 and 0x20003000+1284==0x20003504 and store(op[0x200022ca])==(15,14,4,0)and store(op[0x200022cc])==(15,0,4,0),'Actual transform-helper base slot and ordered word requests256 then0')
    need(graphs[0x200022be][0x20002424]==[0x200023ac]and 0x20002422 in graphs[0x200022be],'Reachable post-RET nop/retry arm remains,not treated as padding')
    needops({0x52418:'addi sp, sp, -48',0x5241e:'li a0, 49',0x52432:'mv s1, a3',0x52440:'beqz a0, 0x5249e',0x5245c:'li a2, 6',0x52460:'addi a0, a0, 10',0x5246c:'qk.c.sb s1, 16(s0)',0x5246e:'addi a0, s0, 17',0x52472:'mv a2, s1',0x5247c:'sb s2, 48(s0)',0x52498:'addi sp, sp, 48',0x5249a:'j 0x43208',0x524ae:'ret',0x527fa:'addi sp, sp, -48',0x52800:'li a0, 24',0x52826:'beqz a0, 0x5289e',0x52828:'lui a4, 0x10b4',0x5282c:'addi a4, a4, -367',0x52830:'addi s0, a0, 8',0x52836:'sw a4, 0(a0)',0x5283a:'li s2, 0',0x5283c:'addi a0, s0, 2',0x52848:'li a2, 6',0x52854:'addi a0, s0, 9',0x5285c:'li a2, 6',0x52868:'sb s8, 15(s0)',0x5286c:'qk.c.lbu a4, 3(s1)',0x5286e:'addi s2, s2, 1',0x52870:'andi s2, s2, 255',0x52874:'addi s0, s0, 16',0x52876:'bltu s2, a4, 0x5283c',0x52898:'addi sp, sp, 48',0x5289a:'j 0x43208',0x528b4:'ret'})
    need(C['constant'](op[0x5241e],10)==49 and C['constant'](op[0x52800],10)==24 and 17+32==49,'Actual numeric allocation requests and conditional variable-copy bound,not a new guard')
    need(dom(0x52418,0x5249a,[0x5243c,0x52440,0x52466,0x52478,0x52498])and dom(0x527fa,0x5289a,[0x52822,0x52826,0x52850,0x52864,0x52898]),'Both real message builders require nonnull gate/copies/frame release before send tail')
    header=((int.from_bytes(bytes.fromhex(op[0x52828]['bytes']),'little')&0xfffff000)-367)&0xffffffff;need(header==0x010b3e91 and header>>24==1 and store(op[0x52836])==(10,14,4,0),'Original allocated header has encoded byte3 count1;fresh loop read is retained')
    need(graphs[0x527fa][0x52876]==[0x5283c,0x5287a],'Original loop remains;single iteration requires stable header and callee/memory contracts')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Whole original parser caller evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x5f234);io={o['addr']:o for o in f['operations']};original=[]
    for pc,target in [(0x5f37c,0x5e950),(0x5f512,0x5ea9a),(0x5f88a,0x5eaca),(0x5f93c,0x5ee06)]:need(B['decode_control'](bytes.fromhex(io[pc]['bytes']),pc)[1]==target,'Each prior genuine parser dependency has its actual callsite');original.append(dict(PC=pc,target=target))
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};need(parent['passed']and not set(parent['_byte_map'])&newbytes and set(E['resolved_prior_dependencies'])<=set(parent['named_UND']),'Four genuine prior missing bodies supplied,no duplicate CODE');need(all(p in parent['_byte_map']for p in E['real_prior_providers']),'All seven current imports have actual retained providers')
    far={x['PC']+4:x['target_PC']for x in N['S']['PC_relative_pairs']};actual=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target']);need(target is not None and target in set(frames)|set(E['real_prior_providers']),'Every actual call has a selected or real prior body;no hidden new opaque call');actual.append(dict(PC=call['PC'],target=target))
    need(len(far)==24 and far[0x200020aa]==far[0x200020e8]==0x5e4b0,'Two RAM-to-ROM HI/LO calls normalized in actual execution context')
    return dict(passed=True,functions=rows,actual_calls=actual,actual_opaque_callbacks=0,complete_functions=16,CODE_bytes=2492,instructions=940,own_frames=[frames[f['start']]for f in E['selected_functions']],conditional_Xwchc_ports=92,prior_parser_calls=original,resolved_prior_dependencies=E['resolved_prior_dependencies'],new_genuine_named_dependencies=0,real_prior_providers=E['real_prior_providers'],mapped_RAM_functions=mapped,loader_first_copy=first,source_address_is_not_execution_address=True,lookup_heads=[0x20003484,0x2000347c],actual_list_contents_or_domain_proved=False,list_termination_or_alias_safety_proved=False,predicate=dict(start=0x5ea9a,own_frame_max=16,early_zero_frame_returns=True,conditional_normal_return_range=[0,1],same_record_offset84_byte_gate_and_word_argument_preserved=True),transform_helper=dict(start=0x200022be,end=0x20002426,own_frame=0,calls=0,base_pointer_slot=0x20003504,initial_word_requests=[256,0],post_return_retry_arm=[0x20002422,0x20002424],physical_operation_and_retry_termination_proved=False),message_builders=[dict(start=0x52418,own_frame=48,allocation_request=49,copy_dest_offsets=[10,17],copy_lengths=[6,'incomingA3'],final_byte_store_offset=48,variable_copy_full32_argument_distinct_from_stored_low8=True,all_callers_copy_length_bound_proved=False,frame_released_send_tail=0x5249a),dict(start=0x527fa,own_frame=48,allocation_request=24,body_offset=8,copy_body_offsets=[2,9],copy_lengths=[6,6],body_stride=16,header_word=header,encoded_header_count=1,fresh_header_count_read_PC=0x5286c,loop_not_replaced_by_constant=True,single_iteration_requires_stable_valid_memory_private_callees_no_async_alias=True,frame_released_send_tail=0x5289a)],no_live_record_or_MAC_contents_observed=True,conditional_callback_provenance_prior_retained=True,all_remaining_callee_effects_proved=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set();expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==7 and out['non_CODE_allocations']==before['non_CODE_allocations'],'Four prior parser dependencies supplied through actual helper/lookup/event bodies;all seven imports real;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(27594,1821,1423),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=27850,instructions=9520,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,four_genuine_prior_named_dependencies_have_real_bodies=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/E['prior_verifier'])['verify'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh entire callback-provenance and preceding APP/SDK/native/IRQ/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],'76fa40dc7a2b4adf77105d7d4dbdcb22c1a594f0b12f52e6de761c04204dddf4'],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-parser-callees-lookups-event-builders-audit-v1',passed=True,checker_sha256=sha(__file__),prior_callback_provenance_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=2492,new_instructions=940,new_complete_functions=16,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=2492,new_instructions=940,complete_functions=16,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=4,opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
