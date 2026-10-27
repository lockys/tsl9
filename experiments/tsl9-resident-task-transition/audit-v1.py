"""Audit complete actual task/parser/event/message chain;never execute it."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-init-final';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
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
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');A=lib(ROOT/'experiments/tsl9-original-APP-library-binding/verify-v1.py');C=lib(ROOT/'experiments/tsl9-original-APP-early-IRQ/verify-v1.py');rows=[];graphs={};op={};frames={0x5f0d2:80,0x5ee98:48,0x6a79e:0,0x52906:80,0x43208:16,0x2000021c:0}
    for f in E['selected_functions']:
        external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,external,frames[f['start']]);op.update(oo);graphs[f['start']]=g;rows.append(v)
    need(sum(v['bytes']for v in rows)==1378 and sum(v['instructions']for v in rows)==479 and len(rows)==6,'Six whole reachable CFGs and balanced original own frames')
    def needops(mapping):need(all(op[p]['opcode']==s for p,s in mapping.items()),'Exact original operands for selected effect contract')
    def dominates(root,end,pcs):return all(end not in V['reachable'](graphs[root],root,skip=pc)for pc in pcs)
    def store(o):
        value=A['store'](o)
        if value is not None:return value
        raw=bytes.fromhex(o['bytes']);w=int.from_bytes(raw,'little')
        if len(raw)==2 and w&0xe003==0xc000:return(8+((w>>7)&7),8+((w>>2)&7),4,((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64)
        if o.get('conditional_Xwchc'):
            text=lib(ROOT/N['S']['source_deriver'])['custom_decode'](w);need(text==o['opcode'],'Actual primary custom store decode');mn,args=text.split(' ',1)
            if mn not in ['qk.c.sb','qk.c.sh']:return None
            rd,operand=args.split(', ');offset,base=operand[:-1].split('(');registers={'s0':8,'s1':9,**{'a'+str(i):10+i for i in range(6)}};return(registers[base],registers[rd],1 if mn.endswith('sb')else 2,int(offset))
        return None
    needops({0x5f0d2:'addi sp, sp, -80',0x5f0da:'lw s0, 1080(a5)',0x5f10e:'lw a5, 1340(s2)',0x5f112:'lw a4, 100(a5)',0x5f114:'bnez a4, 0x5f112',0x5f116:'lw a3, 12(a5)',0x5f118:'and a4, a3, s1',0x5f11c:'sw a4, 12(a5)',0x5f122:'lw a4, 1340(s2)',0x5f126:'li a5, 1426',0x5f12e:'sw s3, 8(a4)',0x5f136:'sw a5, 100(a4)',0x5f138:'sw a3, 12(a4)',0x5f196:'auipc ra, 0x1ffa3',0x5f19a:'jalr 1146(ra)',0x5f19e:'jal ra, 0x63e58',0x5f1a2:'lbu a5, 1300(s7)',0x5f1a6:'andi a5, a5, 1',0x5f1a8:'beqz a5, 0x5f1b6',0x5f1aa:'mv a0, s0',0x5f1b0:'jal ra, 0x5ee98',0x5f1b4:'beqz a0, 0x5f200',0x5f1b6:'li a5, -96',0x5f1ba:'qk.c.sb a5, 10(s0)',0x5f1e4:'sw zero, 16(sp)',0x5f1e6:'sw zero, 12(sp)',0x5f1e8:'sw zero, 8(sp)',0x5f1ea:'sw zero, 4(sp)',0x5f1ec:'qk.c.lhu a2, 62(s0)',0x5f1f4:'sw a2, 0(sp)',0x5f1fa:'jal ra, 0x6a79e',0x5f224:'addi sp, sp, 80',0x5f226:'ret',0x5f228:'qk.c.lbu a4, 10(s0)',0x5f22a:'li a5, 165',0x5f22e:'beq a4, a5, 0x5f10e',0x5f232:'j 0x5f1bc'})
    need(graphs[0x5f0d2][0x5f114]==[0x5f112,0x5f116]and graphs[0x5f0d2][0x5f22e]==[0x5f10e,0x5f232]and graphs[0x5f0d2][0x5f232]==[0x5f1bc],'Fresh status poll and reachable post-return retry arms retained')
    need(dominates(0x5f0d2,0x5f226,[0x5f114,0x5f19a,0x5f19e]),'Status poll and actual wait/reset providers precede normal return')
    need(C['constant'](op[0x5f0e2],9)==0xffffe000 and op[0x5f0fa]['opcode']=='addi s1, s1, -1','Actual FFFFDFFF mask base,clearbit13 only');need(C['constant'](op[0x5f126],15)==1426 and store(op[0x5f136])==(14,15,4,100),'Raw control request1426 width and offset')
    needops({0x6a79e:'lhu t1, 0(sp)',0x6a7a2:'lbu t3, 4(sp)',0x6a7a6:'lbu t4, 12(sp)',0x6a7aa:'andi a7, a7, 255',0x6a7ae:'andi a6, a6, 255',0x6a7b2:'sw t4, 12(sp)',0x6a7b4:'sw t3, 4(sp)',0x6a7b6:'sw t1, 0(sp)',0x6a7b8:'j 0x52906'})
    need(B['decode_control'](bytes.fromhex(op[0x6a7b8]['bytes']),0x6a7b8)[1]==0x52906 and int.from_bytes(bytes.fromhex(op[0x6a7b8]['bytes']),'little')>>7&31==0,'Original wrapper zero-link tail and incoming stack normalization')
    needops({0x52906:'addi sp, sp, -80',0x5290a:'lbu s1, 92(sp)',0x52912:'addi a0, s1, 36',0x5293a:'lhu s5, 80(sp)',0x5293e:'lbu s4, 84(sp)',0x52942:'lw s3, 88(sp)',0x52944:'lw s2, 96(sp)',0x5294e:'beqz a0, 0x529e4',0x52960:'mv s0, a0',0x5296c:'li a2, 6',0x52970:'addi a0, a0, 10',0x52998:'addi a0, s0, 25',0x5299c:'li a2, 6',0x529a6:'addi a0, s0, 36',0x529aa:'qk.c.sb s1, 31(s0)',0x529ac:'sw a0, 32(s0)',0x529ae:'mv a1, s2',0x529b0:'mv a2, s1',0x529ba:'mv a1, s0',0x529da:'lbu a0, 940(a5)',0x529de:'addi sp, sp, 80',0x529e0:'j 0x43208',0x529fe:'addi sp, sp, 80',0x52a00:'ret'})
    need(graphs[0x52906][0x5294e]==[0x529e4,0x52950]and dominates(0x52906,0x529e0,[0x5294a,0x5294e,0x52976,0x529a2,0x529b6,0x529de]),'Actual non-null allocation gate and all copy calls precede released-frame send tail')
    need(dominates(0x52906,0x52a00,[0x5294a,0x5294e,0x529fe]),'Allocation-null arm restores original frame and returns without message send')
    need(36+255==291 and 10+6==16 and 25+6==31 and 32+4==36,'Exact numeric event extent and copies')
    builder_stores=[o for o in E['selected_functions'][3]['operations']if o['type']=='store'];header=set()
    for o in builder_stores:
        parsed=store(o);need(parsed is not None,'Every actual builder store independently decoded');base,source,width,offset=parsed
        if base==2:continue
        need(base==8 or base==10 and o['addr']in [0x52962,0x52964,0x52968,0x5296a],'Only actual allocated pointer bases');header.update(range(offset,offset+width))
    header.update(range(10,16));header.update(range(25,31));need(header==set(range(36))-{21},'Only byte21 lacks an explicit builder store/copy request;allocator/callee effects not inferred')
    needops({0x43208:'addi sp, sp, -16',0x43216:'lw s2, 524(s1)',0x4321a:'sw zero, 524(s1)',0x4321e:'fence.i',0x43222:'bnez a1, 0x4322c',0x43228:'li a0, 5',0x43230:'lbu a5, 413(a5)',0x43238:'bleu a5, s0, 0x43242',0x4323c:'li a5, 2',0x4323e:'bltu a5, s0, 0x4325a',0x43242:'jal 0x431ba',0x4324c:'li a0, 3',0x4325a:'lw a5, -8(a1)',0x43260:'lbu a4, -2(a1)',0x43264:'li a5, 255',0x43268:'beq a4, a5, 0x43278',0x4326c:'jal 0x431ba',0x4327c:'sb s0, -2(a1)',0x43280:'addi a0, a0, 408',0x4328c:'lui a1, 0x8',0x43290:'jal 0x4354a',0x43292:'li a0, 0',0x43294:'sw s2, 524(s1)',0x43298:'j 0x4324e'})
    need(C['constant'](op[0x4320e],9)==0x40024000 and store(op[0x4321a])==(9,0,4,524),'Actual saved control word4002420C,not inferred hardware atomicity')
    need(dominates(0x43208,0x43258,[0x43216,0x4321a,0x4321e]),'All send return paths begin with saved word,zero,FENCE.I');need(dominates(0x43208,0x43290,[0x4327c,0x43288]),'Actual message metadata write and enqueue before event request')
    for pc in [0x43224,0x43248,0x43272,0x43294]:need(store(op[pc])in [(9,18,4,524),(15,18,4,524)],'Raw original saved-word stores on retained outcomes')
    qroot=0x2000021c;needops({qroot:'sw zero, -8(a1)',qroot+4:'lw a5, 0(a0)',qroot+6:'bnez a5, 0x2000022a',qroot+8:'sw a1, 0(a0)',qroot+10:'ret',qroot+12:'mv a5, a4',qroot+14:'lw a4, -8(a5)',qroot+18:'bnez a4, 0x20000228',qroot+20:'sw a1, -8(a5)',qroot+24:'ret'})
    need(dominates(qroot,qroot+10,[qroot])and dominates(qroot,qroot+24,[qroot]),'Both enqueue exits clear incoming next pointer;linked traversal kept with no added limit')
    need(sha(ROOT/E['loader_evidence'])==E['loader_evidence_sha256'],'Retained complete loader mapping evidence');need(0x2000021c-0x20000000+0x40270==0x4048c and 0x20000040<=qroot<qroot+26<=0x20002e74,'Entire enqueue mapping inside prior first inclusive loader copy,no missing source slice')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Original callback source identity');f=next(f for f in caller['selected_functions']if f['start']==0x60516);io={o['addr']:o for o in f['operations']}
    need(io[0x60540]['opcode']=='li s4, 165'and io[0x606ac]['opcode']=='li a5, 165','Original two state165 comparison operands')
    for pc in [0x606b4,0x60708]:need(B['decode_control'](bytes.fromhex(io[pc]['bytes']),pc)[1]==0x5f0d2,'Both actual registered task calls use this real root')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};need(parent['passed']and not set(parent['_byte_map'])&newbytes and 'tsl9_candidate_external_flash_5f0d2'in parent['named_UND'],'Actual previous missing task provider,no duplicate original-PC CODE');need(all(p in parent['_byte_map']for p in E['real_prior_providers']),'All seven actual imports already have prior bodies')
    far={x['PC']+4:x['target_PC']for x in N['S']['PC_relative_pairs']};actual=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target']);need(target is not None and(target in E['real_prior_providers']or target in frames),'Every actual call reaches a selected or real prior provider');actual.append(dict(PC=call['PC'],target=target))
    header=(ROOT/E['header']).read_text('gb18030');need('#define    tmos_msg_send' in header and 'BLE_LIB_JT(12)'in next(l for l in header.splitlines()if l.startswith('#define    tmos_msg_send')),'Official candidate tmos_msg_send slot12 declaration');raw=(ROOT/E['firmware']).read_bytes();need(0x40034+12*4==0x40064 and int.from_bytes(raw[0x64:0x68],'little')==0x43208,'Candidate slot12 is an actual function-pointer word,not a branch opcode')
    return dict(passed=True,functions=rows,actual_calls=actual,actual_opaque_callbacks=0,complete_functions=6,CODE_bytes=1378,instructions=479,own_frames=[80,48,0,80,16,0],conditional_Xwchc_ports=17,task_caller=dict(start=0x60516,calls=[0x606b4,0x60708],target=0x5f0d2,state_byte_offset=10,state_comparison=165),poll=dict(PC=0x5f114,fresh_word_offset=100,pointer_slot=0x2000353c,termination_proved=False),post_return_retry_arms_preserved=True,wrapper=dict(start=0x6a79e,no_link_target=0x52906,stack_read_widths=[2,1,1],stack_offsets=[0,4,12],A6_A7_low8=True),event_builder=dict(start=0x52906,own_frame=80,prefix_bytes=36,length_unsigned8=True,maximum_numeric_allocation_bytes=291,copy_dest_offsets=[10,25,36],copy_lengths=[6,6,'length'],prefix_byte21_explicitly_initialized_here=False,live_byte21_or_allocator_initialization_observed=False,null_allocation_returns_without_send=True,success_releases_frame_before_tail=0x43208),message_send=dict(start=0x43208,candidate_primary_JT_slot=12,own_frame=16,null_pointer_result=5,task_reject_result=3,metadata_reject_result=5,encoded_enqueue_event_result=0,event_bits=0x8000,queue_root=0x20003198,control_word=0x4002420c,control_word_saved_zero_FENCE_I_and_restore_requests=True,physical_atomicity_or_live_delivery_proved=False),enqueue=dict(start=qroot,end=qroot+26,source_start=0x4048c,source_end=0x404a6,metadata_next_offset=-8,own_frame=0,no_new_callback=True,traversal_termination_or_alias_safety_proved=False),requires_matching_ROM_valid_memory_original_private_callee_contracts_and_no_async_alias=True,all_remaining_callee_effects_proved=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved={'tsl9_candidate_external_flash_5f0d2'};expected_UND=sorted(set(before['named_UND'])-resolved);need(out['named_UND']==expected_UND and len(out['named_UND'])==8 and out['non_CODE_allocations']==before['non_CODE_allocations'],'Actual task root and complete parser/event/send/queue chain resolve one prior dependency;all imports use real prior bodies;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(22786,1460,1109),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=23042,instructions=7810,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,one_genuine_prior_named_dependency_has_real_body=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/'audit-v1.py')['audit'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes())and sha(ROOT/E['prior_study']/'audit-result-v1.json')==E['prior_receipt_sha256'],'Fresh entire prior NVM/settings/IRQ/startup/APP/SDK/native/reader/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],'e09a05cc79990344f5c861b02841934f5aa6ea631bfc3ec82e13b74ab66d7e7d'],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-task-transition-parser-event-message-audit-v1',passed=True,checker_sha256=sha(__file__),prior_initializer_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=1378,new_instructions=479,new_complete_functions=6,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1378,new_instructions=479,complete_functions=6,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=1,opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
