"""Verify original controller enqueue,MMIO ordering,pool and APP configuration evidence offline."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='controller_queue_static_library')
def reaching(f,ops,g,reg):
 pure=set('beq beqz bgez bleu blt bltu bne bnez fence.i j jr ret nop'.split());stores=set('sb sh sw qk.c.sb qk.c.sh qk.c.shsp'.split())
 results=set('add addi and andi auipc c.srli lbu lhu li lui lw mul div mv not or ori sll slli srai srl srli sub qk.c.lbu qk.c.lhu'.split())
 volatile=set('ra t0 t1 t2 t3 t4 t5 t6 a0 a1 a2 a3 a4 a5 a6 a7'.split());incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
 while todo:
  p=todo.pop();o=ops[p];mn=o['opcode'].split()[0];need(mn in pure|stores|results|{'jal','jalr'},'Every original register-transfer opcode modelled')
  writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(o['type']in ['call','ucall']and reg in volatile);out={p}if writes else incoming[p]
  for n in g[p]:
   before=len(incoming[n]);incoming[n]|=out
   if before!=len(incoming[n]):todo.append(n)
 return incoming
def contract(K,parent):
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();by={};graphs={};cfgs=[]
 bounds=[(0x56086,0x560aa),(0x560b2,0x560d4),(0x560d4,0x560f6),(0x560f6,0x56146),(0x56146,0x56184)]
 need([(f['start'],f['end'])for f in e['selected_functions']]==bounds and e['code_bytes']==246 and e['instructions']==86,'Five whole original completion status gates')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in e['selected_functions']}
 need(len(parentUND)==20 and len(provided)==5 and provided<=parentUND and set(K['expected_UND'])==parentUND-provided,'Exactly five actual parent imports now supplied by original bodies')
 for f in e['selected_functions']:
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every original whole status-gate byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,0);by.update(ops);graphs[f['start']]=g;cfgs.append(c)
  need(not c['calls']and all(x['type']=='ret'for x in c['typed_exits'])and f['own_frame_bytes']==0,'Whole leaf gates without calls or own frames')
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Every original numeric status/counter operand')
 operands({0x56086:'lw a5, 276(a0)',0x5608a:'li a2, 3',0x5608c:'li a3, 255',0x56090:'qk.c.lbu a4, 0(a5)',0x56092:'andi a4, a4, 3',0x56094:'qk.c.sb a4, 13(a0)',0x56096:'bne a4, a2, 0x5609c',0x5609a:'qk.c.lbu a3, 2(a5)',0x5609c:'qk.c.sb a3, 23(a0)',0x5609e:'qk.c.lbu a4, 0(a5)',0x560a0:'andi a4, a4, 16',0x560a2:'qk.c.sb a4, 18(a0)',0x560a4:'qk.c.lbu a5, 1(a5)',0x560a6:'qk.c.sb a5, 22(a0)',0x560a8:'ret'})
 operands({0x560b2:'lw a5, 276(a0)',0x560b6:'qk.c.lbu a4, 12(a0)',0x560b8:'qk.c.lbu a5, 0(a5)',0x560ba:'srai a3, a4, 0x3',0x560be:'srai a5, a5, 0x2',0x560c0:'xor a5, a5, a3',0x560c2:'andi a5, a5, 1',0x560c4:'beqz a5, 0x560d0',0x560c6:'xori a4, a4, 8',0x560ca:'qk.c.sb a4, 12(a0)',0x560cc:'li a0, 0',0x560ce:'ret',0x560d0:'li a0, 1',0x560d2:'ret'})
 operands({0x560d4:'lw a5, 276(a0)',0x560d8:'qk.c.lbu a4, 12(a0)',0x560da:'qk.c.lbu a5, 0(a5)',0x560dc:'srai a3, a4, 0x2',0x560e0:'srai a5, a5, 0x3',0x560e2:'xor a5, a5, a3',0x560e4:'andi a5, a5, 1',0x560e6:'bnez a5, 0x560f2',0x560e8:'xori a4, a4, 4',0x560ec:'qk.c.sb a4, 12(a0)',0x560ee:'li a0, 0',0x560f0:'ret',0x560f2:'li a0, 1',0x560f4:'ret'})
 need(set(graphs[0x560b2][0x560c4])=={0x560c6,0x560d0}and set(graphs[0x560d4][0x560e6])=={0x560e8,0x560f2},'Exact equal/different bit-gate arms')
 need(0x560ca not in V['reachable'](graphs[0x560b2],0x560d0)and 0x560ec not in V['reachable'](graphs[0x560d4],0x560f2),'Return1 arms do not toggle record flags')
 operands({0x560f6:'lw a5, 228(a0)',0x560fa:'addi a5, a5, 1',0x560fc:'sw a5, 228(a0)',0x56100:'bnez a5, 0x5610c',0x56102:'lw a5, 232(a0)',0x56106:'addi a5, a5, 1',0x56108:'sw a5, 232(a0)',0x5610c:'lw a5, 232(a0)',0x56110:'andi a5, a5, 128',0x56114:'beqz a5, 0x56120',0x56116:'li a5, 1',0x56118:'sw a5, 228(a0)',0x5611c:'sw zero, 232(a0)',0x56120:'lbu a5, 42(a0)',0x56124:'andi a5, a5, 64',0x56128:'beqz a5, 0x56144',0x5612a:'lhu a5, 64(a0)',0x5612e:'lhu a4, 72(a0)',0x56132:'add a5, a5, a4',0x56134:'sh a5, 70(a0)',0x56138:'lw a5, 164(a0)',0x5613c:'andi a5, a5, -1025',0x56140:'sw a5, 164(a0)',0x56144:'ret'})
 operands({0x56146:'lw a5, 236(a0)',0x5614a:'addi a5, a5, 1',0x5614c:'sw a5, 236(a0)',0x56150:'bnez a5, 0x5615c',0x56152:'lw a5, 240(a0)',0x56156:'addi a5, a5, 1',0x56158:'sw a5, 240(a0)',0x5615c:'lw a5, 240(a0)',0x56160:'andi a5, a5, 128',0x56164:'beqz a5, 0x56170',0x56166:'li a5, 1',0x56168:'sw a5, 236(a0)',0x5616c:'sw zero, 240(a0)',0x56170:'lbu a5, 42(a0)',0x56174:'andi a4, a5, 64',0x56178:'beqz a4, 0x56182',0x5617a:'ori a5, a5, 32',0x5617e:'sb a5, 42(a0)',0x56182:'ret'})
 need(len(by)==86,'Exact whole status/counter operand inventory')
 ref=read(R/K['completion_reference']);c=ref['contract'];need(ref['passed']and c['completion_helper_560b2_result_must_be_zero']and c['completion_head_update_PC']==0x5983c and 0x59804 in c['completion_guard_and_release_dominators'],'Earlier whole completion proof requires this original gate return0 before dequeue')
 owner=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py')['inspect'](R/K['SDK_parent']/'c/candidate.o')
 relation=[['CODE',0x59800],17,0,['CODE',0x560b2]]
 need(relation in[json.loads(t)for t in owner['_typed_relations']]and 0x560b2 not in owner['_byte_map'],'Original normalized call role already existed while real gate body was unowned')
 return dict(passed=True,whole_CFGs=cfgs,whole_helper_bounds=bounds,whole_CODE_bytes=246,whole_instructions=86,all_five_are_leaf_with_zero_own_frame=True,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=5,new_normal_imports=0,remaining_normal_named_UND=15,new_indirect_sites=[],input_buffer_record_offset=276,record_flags_byte_offset=12,header_decoder_low2_destination=13,header_decoder_type3_byte2_destination=23,header_decoder_other_type_sentinel=255,header_decoder_raw_bit0x10_destination=18,header_decoder_byte1_destination=22,header_decoder_two_distinct_header0_reads_preserved=True,header_decoder_has_no_null_guard=True,gate560b2_formula='different(input_header0.bit2,record_flags12.bit3):toggle record bit3;return0. equal:return1 without toggle',gate560d4_formula='equal(input_header0.bit3,record_flags12.bit2):toggle record bit2;return0. different:return1 without toggle',return1_gate_arms_do_not_toggle_flags=True,completion_call_PC=0x59800,completion_call_target=0x560b2,completion_call_role_normalized_CODE_even_before_provider=True,completion_queue_head_update_PC=0x5983c,completion_requires_gate_return0_in_addition_to_other_status_head_prepared_marker_guards=True,physical_ACK_or_CRC_meaning_proved=False,first_counter_word_offsets=[228,232],second_counter_word_offsets=[236,240],counter_low32_increment_and_carry_on_zero_preserved=True,counter_high_bit7_resets_low1_high0=True,counter_updates_are_not_proved_atomic=True,counter_live_domain_or_semantic_role_proved=False,counter_flag_condition_record42_bit6=True,first_counter_conditional_halfword70_is_uint16_of64_plus72=True,first_counter_conditional_clears_record164_bit10=True,second_counter_conditional_sets_record42_bit5=True,live_header_record_values_observed=False,readonly_RAM_MMIO_dependencies_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Actual installed archived ROM/Xwchc and original record ABI must match','Record/input buffer spans remain valid;decoder reads byte2 only for low2bits3 and has no null guard','Preserve two separate header0 reads and all fresh counter/flag reads;IRQ/DMA/reentrant coherence is unproved','Gate bit relations and queue eligibility are numeric static evidence,not physical ACK/CRC validation','Counter updates preserve original carry/reset behavior and are not atomic operations or proved semantic counters','Fifteen ordinary imports,inherited callbacks/RAM/MMIO and4B startup-source remain incomplete'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
def run(llvm,trial=None):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():need(sha(R/p)==h,'Frozen controller queue input '+p)
 for n,h in K['tools'].items():need(sha(llvm/n)==h,'Pinned LLVM '+n)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==K['stdint_sha256'],'Pinned compiler header')
 P=lib(K['parent_checker']);parent=P['run'](llvm);need(parent==read(R/K['parent_receipt']),'Fresh complete parent dispatch/native proof')
 N=lib(K['builder']);N['pins'](llvm);saved=read(HERE/'build/native-v1/measurement.json');need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every controller native input retained');native={}
 for mode in ['c','cpp']:
  folder=HERE/'build/native-v1'/mode;need(N['inventory'](folder)==saved['modes'][mode]['artifacts'],'All native artifacts retained')
  need(N['portable'](N['dependencies'](folder,llvm),llvm)==saved['modes'][mode]['dependencies'],'Complete native include provenance')
  native[mode]=N['audit_object'](folder/'unit.o');need(native[mode]==saved['modes'][mode]['result']and N['audit_abi'](folder/'config_abi.o')==saved['modes'][mode]['ABI_result'],'Fresh284-byte native/ABI proof')
 need(native['c']==native['cpp']and not native['c']['UND']and native['c']['opaque_call_sites']==0,'Identical five complete leaf status gates without new imports or own indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(50538,412,3729,5,2980,15));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==50538 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  need(any(json.loads(t)==[['CODE',0x59800],17,0,['CODE',0x560b2]]for t in owned['_typed_relations'])and all(p in owned['_byte_map']for p in range(0x560b2,0x560d4)),'Retain original completion call role and now own its complete positive CODE provider')
  bm=owned['_byte_map'];need(all(p in bm for a,z in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==17547,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-completion-status-gates-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=5,new_SDK_CODE_bytes=246,new_SDK_instructions=86,new_SDK_DATA_bytes=0,new_normal_imports_resolved=0,new_prior_normal_imports_resolved=5,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
 result=json.loads(json.dumps(result))
 if trial:
  need(not(HERE/'verification-v1.json').exists(),'Create-only successful receipt');(HERE/'verification-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 else:need(result==read(HERE/'verification-v1.json'),'Fresh full proof equals exact successful receipt')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');a=p.parse_args()
 try:
  v=run(a.tool_dir.resolve(),a.trial);print(json.dumps({k:v[k]for k in ['passed','new_complete_bodies','new_SDK_CODE_bytes','new_SDK_instructions','prior_genuine_import_body_resolved','new_genuine_unprovided_normal_callees','formal_APP_byte_coverage_unchanged','new_BIN']}))
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
