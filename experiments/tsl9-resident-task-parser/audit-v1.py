"""Audit complete actual parser,scheduler records and masked bit count;preserve genuine gaps and callbacks."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-task-transition';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
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
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');A=lib(ROOT/'experiments/tsl9-original-APP-library-binding/verify-v1.py');C=lib(ROOT/'experiments/tsl9-original-APP-early-IRQ/verify-v1.py');frames={0x5f234:112,0x43414:48,0x43a14:32,0x57ad8:0};rows=[];graphs={};op={}
    for f in E['selected_functions']:
        external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,external,frames[f['start']]);op.update(oo);graphs[f['start']]=g;rows.append(v)
    need(sum(v['bytes']for v in rows)==2316 and sum(v['instructions']for v in rows)==770 and len(rows)==4,'Four complete reachable CFGs and balanced own frames')
    def needops(mapping):need(all(op[p]['opcode']==s for p,s in mapping.items()),'Exact original effect operands')
    def dominates(root,end,pcs):return all(end not in V['reachable'](graphs[root],root,skip=pc)for pc in pcs)
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
    needops({0x5f234:'addi sp, sp, -112',0x5f238:'addi a2, a0, 21',0x5f23c:'mv s0, a0',0x5f23e:'lw a0, 120(a0)',0x5f240:'li a3, 0',0x5f242:'li a1, 0',0x5f25c:'auipc ra, 0x1ffa3',0x5f260:'jalr 990(ra)',0x5f266:'bnez a0, 0x5f304',0x5f272:'lbu a3, 0(s4)',0x5f276:'andi a3, a3, 15',0x5f278:'qk.c.sb a3, 13(s0)',0x5f27a:'lbu a5, 1(s4)',0x5f27e:'qk.c.sb a5, 14(s0)',0x5f280:'bne a3, a2, 0x5f304',0x5f28a:'srli s5, s1, 0x6',0x5f320:'addi sp, sp, 112',0x5f322:'ret',0x5f6a8:'lui s8, 0x20003',0x5f6ce:'lw a5, 564(s8)',0x5f6d6:'jalr a5',0x5f6f8:'lui a5, 0x20003',0x5f6fc:'lw a5, 480(a5)',0x5f708:'jalr a5',0x5f7c2:'jal ra, 0x43a14',0x5f7fe:'jal ra, 0x43414',0x5f96a:'j 0x5f8da'})
    need(graphs[0x5f234][0x5f266]==[0x5f304,0x5f268]and graphs[0x5f234][0x5f280]==[0x5f304,0x5f284],'Original receive-status and low-nibble rejection arms retained');need(dominates(0x5f234,0x5f322,[0x5f260,0x5f266,0x5f320]),'Actual receive provider and restore precede normal return')
    need(max(graphs[0x5f234])+op[max(graphs[0x5f234])]['size']==0x5f96c and graphs[0x5f234][0x5f96a]==[0x5f8da]and all(0x5f96c not in es for es in graphs[0x5f234].values()),'Whole parser stops before distinct frame0 sibling;no fallthrough into5F96C')
    need(all(p in graphs[0x5f234]for p in [0x5f864,0x5f93c,0x5f96a]),'Late post-RET arms included;early512-byte capture alone insufficient')
    needops({0x43414:'addi sp, sp, -48',0x4342e:'lw s1, 524(a5)',0x43432:'sw zero, 524(a5)',0x43436:'fence.i',0x4343a:'bnez a0, 0x4345a',0x43440:'li a0, 2',0x43456:'addi sp, sp, 48',0x43458:'ret',0x4345a:'lui a5, 0x20003',0x4345e:'lw a5, 480(a5)',0x4346c:'jalr a5',0x43472:'lw a4, 556(a5)',0x43478:'li s0, 0',0x4347a:'li a3, 12',0x4347c:'li a5, 16',0x4347e:'mul s8, s0, a3',0x43486:'lw a2, 0(a2)',0x43488:'bnez a2, 0x4350e',0x43490:'li a0, 16',0x4349a:'bnez a0, 0x434b8',0x4349c:'lui a5, 0x20003',0x434a0:'lw a5, 544(a5)',0x434a4:'beqz a5, 0x434ac',0x434aa:'jalr a5',0x434b4:'li a0, 11',0x434bc:'lw a4, 488(a5)',0x434c0:'bnez a4, 0x43506',0x434c2:'sw a0, 488(a5)',0x434d4:'sw zero, 12(a0)',0x434dc:'qk.c.sh a4, 2(a0)',0x434f0:'beqz s4, 0x434f8',0x434f4:'sb s0, 0(s4)',0x43500:'li a0, 0',0x43506:'lw a5, 12(a4)',0x43508:'bnez a5, 0x43504',0x4350e:'addi s0, s0, 1',0x43510:'bne s0, a5, 0x4347e',0x4351c:'li a0, 8',0x4351e:'j 0x43442'})
    need(graphs[0x43414][0x43510]==[0x4347e,0x43514]and graphs[0x43414][0x43508]==[0x43504,0x4350a],'Original16-record scan and next+12 traversal remain distinct')
    need(C['constant'](op[0x43418],15)==0x40024000 and store(op[0x43432])==(15,0,4,524),'Original saved control word4002420C and zero request');need(dominates(0x43414,0x43458,[0x4342e,0x43432,0x43436,0x43456]),'Save,zero,FENCE.I and own frame restore precede normal return')
    needops({0x43a14:'addi sp, sp, -32',0x43a24:'lw s2, 524(s1)',0x43a28:'sw zero, 524(s1)',0x43a2c:'fence.i',0x43a30:'li a5, 47',0x43a34:'bltu a5, a0, 0x43a80',0x43a38:'li a5, 12',0x43a3a:'mul s0, a0, a5',0x43a42:'lw a5, 556(s3)',0x43a48:'lw a5, 0(a5)',0x43a4a:'beqz a5, 0x43a80',0x43a4c:'andi a5, a0, 15',0x43a50:'li a1, 1',0x43a52:'sll a1, a1, a5',0x43a56:'slli a1, a1, 0x10',0x43a58:'srli a1, a1, 0x10',0x43a5a:'srli a0, a0, 0x4',0x43a5c:'jal 0x439a8',0x43a62:'li a0, 0',0x43a66:'sw zero, 0(a5)',0x43a6a:'sw zero, 4(a5)',0x43a7c:'addi sp, sp, 32',0x43a7e:'ret',0x43a88:'li a0, 2',0x43a8a:'j 0x43a72'})
    need(B['decode_control'](bytes.fromhex(op[0x43a5c]['bytes']),0x43a5c)[1]==0x439a8 and store(op[0x43a66])==(15,0,4,0)and store(op[0x43a6a])==(15,0,4,4),'Actual prior stop-task provider and two cleared entry words;third word retained')
    need(dominates(0x43a14,0x43a7e,[0x43a24,0x43a28,0x43a2c,0x43a7c]),'Removal original save,zero,FENCE.I and own frame restore')
    needops({0x57ade:'slli a5, a5, 0x8',0x57ae0:'slli a4, a4, 0x10',0x57ae2:'add a5, a5, a4',0x57ae6:'andi a3, a3, 31',0x57ae8:'li a6, 1',0x57aee:'li a1, 32',0x57af2:'li a0, 0',0x57af4:'slli a4, a4, 0x18',0x57af6:'add a5, a5, a4',0x57af8:'li a4, 0',0x57afa:'sll a2, a6, a4',0x57afe:'and a2, a2, a5',0x57b00:'beqz a2, 0x57b08',0x57b02:'addi a0, a0, 1',0x57b04:'andi a0, a0, 255',0x57b08:'addi a4, a4, 1',0x57b0a:'bne a4, a1, 0x57afa',0x57b0e:'li a5, 0',0x57b10:'li a2, 8',0x57b12:'sra a4, a3, a5',0x57b16:'andi a4, a4, 1',0x57b18:'beqz a4, 0x57b20',0x57b1a:'addi a0, a0, 1',0x57b1c:'andi a0, a0, 255',0x57b20:'addi a5, a5, 1',0x57b22:'bne a5, a2, 0x57b12',0x57b26:'ret'})
    loads={pc:o['opcode']for pc,o in op.items()if 0x57ad8<=pc<0x57ade or pc in [0x57ae4,0x57aec]};need(loads=={0x57ad8:'qk.c.lbu a5, 1(a0)',0x57ada:'qk.c.lbu a4, 2(a0)',0x57adc:'qk.c.lbu a3, 4(a0)',0x57ae4:'qk.c.lbu a4, 0(a0)',0x57aec:'qk.c.lbu a4, 3(a0)'},'Exactly five actual byte loads and order;no atomic snapshot assumed')
    need(graphs[0x57ad8][0x57b0a]==[0x57afa,0x57b0e]and graphs[0x57ad8][0x57b22]==[0x57b12,0x57b26],'Actual counters visit32 and8 bit positions,masked high byte has only5 bits');need(32+5==37<256,'Unsigned8 accumulator cannot overflow under this symbolic count bound;no test inputs executed')
    callbacks=E['opaque_transfers'];need([(x['PC'],x['pointer_slot'])for x in callbacks]==[(0x5f6d6,0x20003234),(0x5f708,0x200031e0),(0x4346c,0x200031e0),(0x434aa,0x20003220)],'Four genuine callback sites and three fresh slots')
    for item in callbacks:
        raw=bytes.fromhex(op[item['PC']]['bytes']);word=int.from_bytes(raw,'little');need(len(raw)==2 and word&0xf07f==0x9002 and(word>>7)&31==15,'Actual compressed JALR throughA5,no fabricated direct target')
    need(C['constant'](op[0x5f6a8],24)==C['constant'](op[0x5f6f8],15)==C['constant'](op[0x4345a],15)==C['constant'](op[0x4349c],15)==0x20003000 and 0x20003000+564==0x20003234 and 0x20003000+480==0x200031e0 and 0x20003000+544==0x20003220,'Independent actual callback address arithmetic;values/effects unknown')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};need(parent['passed']and not set(parent['_byte_map'])&newbytes and 'tsl9_candidate_external_flash_5f234'in parent['named_UND'],'Actual prior missing parser root,no duplicate CODE');need(all(p in parent['_byte_map']for p in E['real_prior_providers']),'All seven claimed prior providers have real bodies')
    missing={x['address']:x['name']for x in E['new_genuine_code_dependencies']};need(set(missing)=={0x5e950,0x5ea9a,0x5eaca,0x5ee06}and all(p not in parent['_byte_map']and name not in parent['named_UND']for p,name in missing.items()),'Four genuine newly exposed missing code bodies,not provided by old composition')
    far={x['PC']+4:x['target_PC']for x in N['S']['PC_relative_pairs']};actual=[];opaque_seen=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target'])
            if target is None:
                need(call['PC']in [x['PC']for x in callbacks],'Only actual known opaque sites');opaque_seen.append(call['PC']);kind='opaque'
            else:
                need(target in set(E['real_prior_providers'])|set(frames)|set(missing),'Each actual static call classified');kind='real-prior'if target in E['real_prior_providers']else'genuine-missing'if target in missing else'selected'
            actual.append(dict(PC=call['PC'],target=target,provider_kind=kind))
    need(set(opaque_seen)=={x['PC']for x in callbacks}and len(opaque_seen)==4,'Exactly four preserved real opaque calls')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Original registered task evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x60516);io={o['addr']:o for o in f['operations']};need(B['decode_control'](bytes.fromhex(io[0x606fe]['bytes']),0x606fe)[1]==0x5f234 and io[0x606f8]['opcode']=='mv a0, s0','Actual task606FE calls whole parser with original record')
    return dict(passed=True,functions=rows,actual_calls=actual,actual_opaque_callbacks=4,callback_sites=callbacks,complete_functions=4,CODE_bytes=2316,instructions=770,own_frames=[112,48,32,0],conditional_Xwchc_ports=27,caller=dict(start=0x60516,call=0x606fe,target=0x5f234,record_argument=True),parser=dict(start=0x5f234,end=0x5f96c,own_frame=112,instructions=597,receive_status_prior_provider=0x2000263a,opaque_callbacks=[0x5f6d6,0x5f708],all_late_reachable_arms_preserved=True,excluded_adjacent_start=0x5f96c,excluded_adjacent_bytes=34),scheduler_record=dict(start=0x43414,own_frame=48,scan_entries=16,record_stride=12,scan_numeric_bytes=192,allocation_request_bytes=16,list_next_offset=12,encoded_results=[2,11,8,0],optional_index_pointer_store_preserved=True,actual_list_termination_proved=False),removal=dict(start=0x43a14,own_frame=32,accepted_numeric_ID_range=[0,47],ID_stride=12,numeric_extent=576,event_mask='low16(1 << (ID & 15))',task_ID='ID >> 4',real_prior_stop_provider=0x439a8,cleared_word_offsets=[0,4],third_word_unchanged_by_explicit_stores=True,encoded_results=[0,2]),masked_popcount=dict(start=0x57ad8,end=0x57b28,own_frame=0,input_bytes=5,load_offsets=[1,2,4,0,3],fifth_byte_mask=31,loop_bounds=[32,8],conditional_result_range=[0,37],calls=0,source_snapshot_atomicity_or_domain_proved=False),scheduler_control_word=0x4002420c,control_word_save_zero_FENCE_I_restore_requests_preserved=True,physical_atomicity_proved=False,new_genuine_named_dependencies=4,new_genuine_missing_bodies=E['new_genuine_code_dependencies'],all_remaining_callee_effects_proved=False,actual_callback_targets_or_effects_proved=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved={'tsl9_candidate_external_flash_5f234'};added={x['name']for x in N['EV']['new_genuine_code_dependencies']};expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==11 and out['non_CODE_allocations']==before['non_CODE_allocations'],'One prior parser dependency supplied;four genuine missing deeper callees exposed;all seven prior imports real;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(25102,1630,1249),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=25358,instructions=8580,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,one_genuine_prior_named_dependency_has_real_body=True,new_genuine_named_dependencies=4,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/'audit-v1.py')['audit'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes())and sha(ROOT/E['prior_study']/'audit-result-v1.json')==E['prior_receipt_sha256'],'Fresh entire prior NVM/settings/IRQ/startup/APP/SDK/native/reader/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],'3b3b80e003601a6c86c9dcc0e71ffb930c211c124ad8040f731716a33773589b'],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-complete-task-parser-scheduler-count-audit-v1',passed=True,checker_sha256=sha(__file__),prior_transition_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=2316,new_instructions=770,new_complete_functions=4,new_genuine_named_dependencies=4,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=2316,new_instructions=770,complete_functions=4,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=1,opaque_callbacks=4,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
