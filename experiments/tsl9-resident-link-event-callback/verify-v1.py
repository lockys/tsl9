"""Verify complete archived link-event bodies/native composition without executing the target."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='link_event_static_library')
def contract(K,parent):
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py')
 P=lib(K['parent_checker']);e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();by={};graphs={};cfgs=[];fs={f['start']:f for f in e['selected_functions']}
 need(len(fs)==14 and e['code_bytes']==1068 and e['instructions']==428,'Exactly fourteen complete original bodies')
 for f in e['selected_functions']:
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(at==o['addr']and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Contiguous original instruction widths')
   payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['source_start']-0x40000:f['source_end']-0x40000],'Every selected original source byte')
  if f['start']>=0x20000000:need(f['source_start']==f['start']-0x20000000+0x40270 and f['source_end']==f['end']-0x20000000+0x40270,'Existing conditional first-copy mapping,not startup success')
  else:need(f['source_start']==f['start'],'Direct archived Flash reference')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
  ops,g,cfg=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);graphs[f['start']]=g;cfgs.append(cfg)
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact event/state/lookup/cleanup/serialization operands')
 operands({0x4d916:'lui a4, 0x10',0x4d918:'addi a4, a4, -2',0x4d91a:'beq a0, a4, 0x4d950',0x4d91e:'addi sp, sp, -16',0x4d924:'li a5, 1',0x4d926:'mv s0, a0',0x4d928:'bne a1, a5, 0x4d93a',0x4d92c:'mv a0, s0',0x4d932:'li a1, 0',0x4d934:'addi sp, sp, 16',0x4d936:'j 0x4d83a',0x4d93a:'li a5, 2',0x4d93c:'bne a1, a5, 0x4d948',0x4d940:'li a1, 1',0x4d942:'jal ra, 0x4f072',0x4d946:'beqz a0, 0x4d92c',0x4d94e:'ret',0x4d950:'ret'})
 root=fs[0x4d916];ro={o['addr']:o for o in root['operations']};rg=graphs[0x4d916];rd=[]
 for reg,pc,w in [('s0',0x4d92c,{0x4d926}),('a0',0x4d936,{0x4d92c}),('a1',0x4d936,{0x4d932}),('a1',0x4d942,{0x4d940}),('a0',0x4d942,{-1})]:
  need(P['reaching'](root,ro,rg,reg)[pc]==w,'Whole-CFG event callback argument provenance')
  rd.append(dict(register=reg,PC=pc,definitions=sorted(w)))
 need((root['end']-root['start'],len(ro))==(60,25),'Whole60-byte registered callback,not adjacent functions')
 operands({0x4f072:'lui a5, 0x10',0x4f074:'addi a5, a5, -2',0x4f076:'beq a0, a5, 0x4f0a0',0x4f080:'mv s0, a1',0x4f082:'auipc ra, 0x1ffb2',0x4f086:'jalr -1518(ra)',0x4f08a:'mv a5, a0',0x4f08c:'li a0, 0',0x4f08e:'beqz a5, 0x4f098',0x4f090:'qk.c.lbu a0, 4(a5)',0x4f092:'and s0, s0, a0',0x4f094:'snez a0, s0',0x4f0a0:'li a0, 1'})
 need((0x4f082+0x1ffb2000-1518)&0xfffffffe==0x20000a94,'Actual normal far call to mapped link-record lookup')
 operands({0x20000a94:'lui a5, 0x20003',0x20000a98:'lbu a2, 948(a5)',0x20000a9c:'lui a5, 0x20003',0x20000aa0:'lw a4, 852(a5)',0x20000aa4:'li a5, 0',0x20000aa6:'bne a2, a5, 0x20000ab0',0x20000aaa:'li a3, 0',0x20000aac:'mv a0, a3',0x20000ab0:'mv a3, a4',0x20000ab2:'addi a4, a4, 60',0x20000ab6:'lhu a1, -58(a4)',0x20000aba:'beq a1, a0, 0x20000aac',0x20000abe:'addi a5, a5, 1',0x20000ac0:'andi a5, a5, 255',0x20000ac4:'j 0x20000aa6'})
 need(0x20003000+948==0x200033b4 and 0x20003000+852==0x20003354,'Same live total/pointer as prior allocation contract')
 pc=parent['contract'];need(pc['total_connections_address']==0x200033b4 and pc['allocator_pointer_address']==0x20003354 and pc['unprovided_literal_callback']==0x4d916,'Fresh prior callback literal/allocation provenance')
 mapping=read(R/e['mapping_proof'])['conditional_mapping']['first_copy']
 need(mapping['source']==0x402b0 and mapping['destination']==0x20000040 and mapping['source']<=0x40d04<0x40d36<=mapping['source']+mapping['bytes'],'Whole50-byte lookup lies in captured conditional first-copy source')
 slots={p:int.from_bytes(raw[p-0x40000:p-0x40000+4],'little')for p in [0x400ac,0x400b0]}
 need(slots=={0x400ac:0x4efe2,0x400b0:0x4f072},'Actual archived register/state API slots')
 operands({0x4d852:'lui s4, 0x20003',0x4d856:'lui s5, 0x20003',0x4d85c:'lbu a5, -95(s4)',0x4d860:'bltu s0, a5, 0x4d8aa',0x4d864:'bnez s3, 0x4d896',0x4d874:'lbu a5, -96(s3)',0x4d87c:'li s0, 4',0x4d87e:'li s1, 8',0x4d880:'mv a0, s0',0x4d886:'li a2, 255',0x4d88a:'mv a1, s2',0x4d88e:'jal ra, 0x4d70a',0x4d892:'bne s0, s1, 0x4d880',0x4d8aa:'lw a5, -104(s5)',0x4d8ae:'slli s1, s0, 0x4',0x4d8b4:'qk.c.lbu a5, 0(s1)',0x4d8b8:'qk.c.lhu a5, 6(s1)',0x4d8be:'bne s3, s6, 0x4d8c8',0x4d8c4:'jal ra, 0x4ed48',0x4d8ce:'jal ra, 0x4e43e',0x4d8d4:'jal ra, 0x4d66e',0x4d8e0:'lw a5, -104(s4)',0x4d8ee:'qk.c.lbu a5, 9(s1)',0x4d8f0:'beq a5, s5, 0x4d90e',0x4d8f4:'qk.c.lhu a5, 6(s1)',0x4d8fc:'jal ra, 0x4d820',0x4d902:'li a1, 20',0x4d904:'jal ra, 0x4e46e',0x4d90a:'jal ra, 0x4d66e'})
 operands({0x4d672:'lw s0, 12(a0)',0x4d67a:'beqz s0, 0x4d69e',0x4d67c:'lw a0, 12(s0)',0x4d67e:'beqz a0, 0x4d688',0x4d688:'lw a0, 20(s0)',0x4d68a:'beqz a0, 0x4d694',0x4d694:'mv a0, s0',0x4d69e:'mv a0, s1',0x4d6a0:'li a2, 16',0x4d6a2:'li a1, 0',0x4d6b0:'li a5, -1',0x4d6b2:'qk.c.sb a5, 9(s1)',0x4d710:'addi s1, a0, -4',0x4d714:'mul a3, s1, a3',0x4d71c:'addi a4, a5, 800',0x4d726:'qk.c.lhu a3, 10(a4)',0x4d728:'bne a3, a1, 0x4d756',0x4d72c:'lw a0, 4(a4)',0x4d72e:'beqz a0, 0x4d756',0x4d738:'beq a2, a5, 0x4d742',0x4d73e:'bne a5, a2, 0x4d756',0x4d752:'sw zero, 4(a5)',0x4d828:'qk.c.lbu a0, 9(a0)',0x4d82a:'jal ra, 0x43a14',0x4d830:'qk.c.sb a5, 9(s0)'})
 for high,target in [(0x4d680,0x20000110),(0x4d68c,0x20000110),(0x4d696,0x20000110),(0x4d6a4,0x2000039c),(0x4d742,0x20000110),(0x4e306,0x20000236),(0x4e334,0x20000332),(0x4e34e,0x2000039c)]:
  role=e['reference_roles'][str(high)];need(role['target']==target,'Original actual free/fill/message/copy role')
 operands({0x4e2f4:'li a0, 32',0x4e30e:'beqz a0, 0x4e358',0x4e31c:'li a0, -94',0x4e320:'qk.c.sb a0, 0(s0)',0x4e322:'qk.c.sb a2, 1(s0)',0x4e324:'qk.c.sh a1, 2(s0)',0x4e326:'qk.c.sb a4, 4(s0)',0x4e328:'qk.c.sb a3, 5(s0)',0x4e32a:'addi a0, s0, 8',0x4e32e:'li a2, 24',0x4e330:'beqz a5, 0x4e34c',0x4e346:'addi sp, sp, 48',0x4e348:'j 0x43208',0x4e34c:'li a1, 0',0x4e360:'ret',0x4ed4c:'lui a3, 0x4f',0x4ed5c:'addi a3, a3, -1086',0x4ed66:'jal ra, 0x4eb12'})
 need(0x4f000-1086==0x4ebc2 and e['raw_pointer_literal_dependencies']==[dict(PC=0x4ed4c,low_PC=0x4ed5c,value=0x4ebc2,body_provided=True,typed_relocation=False,physical_binding_proved=False)],'Actual serializer literal now has a whole body,but no invented typed binding')
 operands({0x4ebc2:'qk.c.lhu a5, 0(a1)',0x4ebc4:'qk.c.sb a5, 0(a0)',0x4ebc6:'qk.c.lhu a5, 0(a1)',0x4ebc8:'srli a5, a5, 0x8',0x4ebca:'qk.c.sb a5, 1(a0)',0x4ebcc:'qk.c.lhu a5, 2(a1)',0x4ebce:'qk.c.sb a5, 2(a0)',0x4ebd0:'qk.c.lhu a5, 2(a1)',0x4ebd2:'srli a5, a5, 0x8',0x4ebd4:'qk.c.sb a5, 3(a0)',0x4ebd6:'li a0, 4',0x4ebd8:'ret'})
 need(e['new_genuine_code_dependency_entries']==[0x4eb12]and len(e['real_prior_providers'])==6,'Six real prior providers and one genuine missing normal callee')
 return dict(passed=True,whole_CFGs=cfgs,unique_reaching_definitions=rd,registered_callback=[0x4d916,0x4d952],registered_callback_bytes=60,registered_callback_instructions=25,previous_literal_callback_body_now_provided=True,normal_width_header_condition=True,loopback_handle=65534,loopback_returns_before_frame=True,removed_event=1,stateflags_event=2,removed_event_cleans_without_state_query=True,stateflags_event_queries_connected_mask=1,stateflags_not_up_cleans=True,other_events_return_without_cleanup=True,cleanup_tail=0x4d936,cleanup_target=0x4d83a,cleanup_reason=0,cleanup_tail_frame_released=True,state_helper=[0x4f072,0x4f0a4],state_helper_loopback_returns_true=True,state_helper_missing_record_returns_false=True,state_helper_reads_flag_byte_offset=4,state_helper_returns_boolean=True,mapped_lookup=[0x20000a94,0x20000ac6],mapped_lookup_source=[0x40d04,0x40d36],mapped_lookup_bytes=50,mapped_lookup_total_byte=0x200033b4,mapped_lookup_pointer=0x20003354,mapped_lookup_total_sampled_once=True,mapped_lookup_pointer_loaded_even_for_zero_total=True,mapped_lookup_zero_total_no_record_dereference=True,mapped_lookup_record_stride=60,mapped_lookup_handle_offset=2,mapped_lookup_first_match_or_null=True,candidate_slots=slots,pending_record_pointer=0x20002f98,pending_record_stride=16,pending_record_handle_offset=6,pending_record_timer_offset=9,pending_live_count_addresses=[0x20002fa1,0x20002fa0],pending_pointer_and_counts_remain_unproved=True,record_cleanup=0x4d66e,record_nested_pointer_offset=12,nested_release_offsets_in_order=[12,20],nested_nonnull_guards=True,nested_record_released_after_children=True,pending_record_clear_bytes=16,pending_record_timer_after_clear=255,filtered_resource_table_base=0x20003320,filtered_resource_table_stride=12,resource_cleanup_indices_under_zero_reason=[4,5,6,7],resource_match_handle_offset=10,resource_owned_pointer_offset=4,resource_null_guard=True,resource_255_type_wildcard=True,timer_release_callee=0x43a14,timer_release_writes_slot255=True,message_wrapper=0x4e2ee,message_allocation_bytes=32,message_header_marker_byte=162,message_body_offset=8,message_body_bytes=24,message_null_source_zero_fills_body=True,message_nonnull_source_copies24_bytes=True,message_allocation_null_returns_without_send=True,message_send_frame_released_tail=0x43208,stack_payload_complete_initialization_proved=False,serializer=[0x4ebc2,0x4ebda],serializer_bytes=24,serializer_instructions=12,serializer_source_halfword_offsets=[0,0,2,2],serializer_output_byte_offsets=[0,1,2,3],serializer_return_length=4,serializer_fresh_repeated_halfword_loads_preserved=True,serializer_literal_typed_relocation=False,unprovided_normal_callee=0x4eb12,new_native_imports=7,real_prior_imports_resolved=6,remaining_named_UND=1,callback_table_dispatcher_or_physical_invocation_proved=False,CCC_record_clearing_by_this_callback_proved=False,conditions=['Archived installed-ROM/Xwchc/header and normal saved-register/argument ABI must match','Conditional first-copy mapping preserves50B atRAM20000A94;startup completion remains unproved','Live counts,pointers,16/60-byte tables and nested allocations remain valid;no alias/IRQ/DMA/reentrant mutation violates each fresh access','Allocator/free/timer/message providers execute normally;physical effects and callback lifetimes are unproved','4EB12 remains a genuine missing normal callee;literal callbacks require original address binding,not a fabricated provider alias','Stack payload byte initialization is not fully proven by these wrappers;do not silently zero or coalesce original fresh accesses'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
def run(llvm,trial=None):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():need(sha(R/p)==h,'Frozen link-event evidence/native input '+p)
 for n,h in K['tools'].items():need(sha(llvm/n)==h,'Pinned LLVM '+n)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==K['stdint_sha256'],'Pinned compiler header')
 P=lib(K['parent_checker']);parent=P['run'](llvm);need(parent==read(R/K['parent_receipt']),'Fresh full parent capacity/native evidence')
 N=lib(K['builder']);N['pins'](llvm);saved=read(HERE/'build/native-v2/measurement.json')
 need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every extended fourteen-body native input retained')
 native={}
 for mode in ['c','cpp']:
  folder=HERE/'build/native-v2'/mode;need(N['inventory'](folder)==saved['modes'][mode]['artifacts'],'Retained complete native artifacts')
  need(N['portable'](N['dependencies'](folder,llvm),llvm)==saved['modes'][mode]['dependencies'],'Native include provenance')
  native[mode]=N['audit_object'](folder/'unit.o')
  need(native[mode]==saved['modes'][mode]['result']and N['audit_abi'](folder/'config_abi.o')==saved['modes'][mode]['ABI_result'],'Fresh original native/zero-runtime ABI proof')
 need(native['c']==native['cpp']and len(native['c']['UND'])==7,'Identical native unit with seven genuine imports')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only actual composition')
 else:need(out.exists(),'Retained composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v2'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual link-event SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(43350,412,3048,5,2435,1));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==43350 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==['tsl9_candidate_unprovided_flash_4eb12'],'Unique SDK CODE and exactly one honest unresolved callee')
  bm=owned['_byte_map'];pending=set(bm);count=0
  while pending:
   pc=min(pending)
   while pc in pending:
    width=4 if bm[pc]&3==3 else 2;need(all(pc+i in pending for i in range(width)),'Every complete native instruction owned once')
    pending.difference_update(range(pc,pc+width));pc+=width;count+=1
  need(count==15020,'Actual SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Whole SDK C/C++ composition identical')
 result=dict(schema='TSL9-link-event-callback-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=14,new_SDK_CODE_bytes=1068,new_SDK_instructions=428,new_SDK_DATA_bytes=0,new_normal_imports_resolved=6,new_genuine_unprovided_normal_callees=1,previous_literal_callback_body_now_provided=True,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
 result=json.loads(json.dumps(result))
 if trial:
  need(not(HERE/'verification-v1.json').exists(),'Create-only successful receipt');(HERE/'verification-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 else:need(result==read(HERE/'verification-v1.json'),'Fresh full proof equals exact successful receipt')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');a=p.parse_args()
 try:
  v=run(a.tool_dir.resolve(),a.trial);print(json.dumps({k:v[k]for k in ['passed','new_complete_bodies','new_SDK_CODE_bytes','new_SDK_instructions','new_genuine_unprovided_normal_callees','formal_APP_byte_coverage_unchanged','new_BIN']}))
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
