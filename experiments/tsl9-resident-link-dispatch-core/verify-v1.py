"""Whole archived request,callback-dispatch and removal proof;no target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='link_dispatch_static_library')
def reaching(f,ops,g,reg):
 pure=set('beq beqz bleu blt bltu bne bnez j jr ret'.split());stores=set('sb sh sw qk.c.sb qk.c.sh qk.c.shsp'.split())
 results=set('add addi andi auipc c.srli lbu lhu li lui lw mul mv slli srai srli sub qk.c.lbu qk.c.lhu'.split())
 volatile=set('ra t0 t1 t2 t3 t4 t5 t6 a0 a1 a2 a3 a4 a5 a6 a7'.split());incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
 while todo:
  p=todo.pop();o=ops[p];mn=o['opcode'].split()[0];need(mn in pure|stores|results|{'jal','jalr'},'Every register-transfer opcode modelled')
  writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(o['type']in ['call','ucall']and reg in volatile)
  out={p}if writes else incoming[p]
  for n in g[p]:
   before=len(incoming[n]);incoming[n]|=out
   if before!=len(incoming[n]):todo.append(n)
 return incoming
def contract(K,parent):
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes()
 fs={f['start']:f for f in e['selected_functions']};by={};graphs={};cfgs=[];ops_by={}
 need(len(fs)==14 and e['code_bytes']==1260 and e['instructions']==495,'Exactly fourteen whole original bodies')
 for f in e['selected_functions']:
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(at==o['addr']and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Contiguous original instruction widths')
   payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['source_start']-0x40000:f['source_end']-0x40000],'Every whole original source byte')
  if f['start']>=0x20000000:need(f['source_start']==f['start']-0x20000000+0x40270 and f['source_end']==f['end']-0x20000000+0x40270,'Existing conditional first-copy source mapping')
  else:need(f['source_start']==f['start'],'Direct archived Flash source')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
  ops,g,cfg=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);graphs[f['start']]=g;ops_by[f['start']]=ops;cfgs.append(cfg)
 def operands(w):need(all(by[p]['opcode']==s for p,s in w.items()),'Exact dispatch/removal/request/prefix operands')
 rd=[]
 def definitions(start,reg,p,w):
  need(reaching(fs[start],ops_by[start],graphs[start],reg)[p]==set(w),'Whole-CFG callback/register provenance')
  rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 operands({0x4ed98:'addi sp, sp, -32',0x4ed9c:'lui s0, 0x20003',0x4eda0:'addi s0, s0, 856',0x4edac:'mv s2, a0',0x4edae:'mv s3, a1',0x4edb0:'addi s1, s0, 48',0x4edb4:'lw a5, 0(s0)',0x4edb6:'beqz a5, 0x4edbe',0x4edb8:'mv a1, s3',0x4edba:'mv a0, s2',0x4edbc:'jalr a5',0x4edbe:'addi s0, s0, 4',0x4edc0:'bne s0, s1, 0x4edb4',0x4edce:'addi sp, sp, 32',0x4edd0:'ret'})
 for reg,p,w in [('a5',0x4edbc,[0x4edb4]),('a0',0x4edbc,[0x4edba]),('a1',0x4edbc,[0x4edb8]),('s2',0x4edba,[0x4edac]),('s3',0x4edb8,[0x4edae])]:definitions(0x4ed98,reg,p,w)
 operands({0x4f00c:'addi sp, sp, -16',0x4f012:'auipc ra, 0x1ffb2',0x4f016:'jalr -1406(ra)',0x4f01a:'beqz a0, 0x4f054',0x4f01c:'mv s0, a0',0x4f01e:'qk.c.lhu a0, 2(a0)',0x4f020:'li a1, 1',0x4f022:'jal ra, 0x4ed98',0x4f026:'lw a0, 44(s0)',0x4f028:'beqz a0, 0x4f032',0x4f032:'mv a0, s0',0x4f034:'li a2, 60',0x4f038:'li a1, 0',0x4f042:'li a5, -1',0x4f044:'qk.c.sh a5, 2(s0)',0x4f046:'sb zero, 4(s0)',0x4f04a:'li a0, 0',0x4f054:'li a0, 2',0x4f056:'j 0x4f04c'})
 for reg,p,w in [('a0',0x4f022,[0x4f01e]),('a1',0x4f022,[0x4f020]),('s0',0x4f026,[0x4f01c])]:definitions(0x4f00c,reg,p,w)
 need(0x4f026 not in V['reachable'](graphs[0x4f00c],0x4f00c,skip=0x4f022),'Status callbacks precede release and record clearing on normal CFG')
 for high,target,kind in [(0x4f012,0x20000a94,'code-call'),(0x4f02a,0x20000110,'code-call'),(0x4f03a,0x2000039c,'code-call'),(0x4da52,0x20000040,'code-call'),(0x4da62,0x200001e4,'code-tail'),(0x4e6ec,0x200001e4,'code-call')]:
  need(e['reference_roles'][str(high)]==dict(reference_kind=kind,target=target),'Actual lookup/free/fill/heap/prefix call or released-frame tail')
 ce=read(R/K['capacity_evidence']);cap=read(R/K['capacity_receipt'])['contract']
 need(cap['callback_table']==[0x20003358,0x20003388]and cap['callback_slots']==12 and cap['unprovided_literal_callback']==0x4d916 and cap['nominal_ConnectNumber_case']['total_connections']==5,'Fresh ancestor initialization/register provenance')
 need(parent['contract']['registered_callback']==[0x4d916,0x4d952]and parent['contract']['removed_event']==1 and parent['contract']['cleanup_reason']==0,'Fresh parent callback body/selector/cleanup proof')
 cbops={o['addr']:o for f in ce['selected_functions']for o in f['operations']}
 need(all(cbops[p]['opcode']==s for p,s in {0x4dbce:'lui a0, 0x4e',0x4dbd2:'addi a0, a0, -1770',0x4dbd8:'j 0x4efe2',0x4ee42:'li a2, 48',0x4ee48:'addi a0, a0, 856',0x4efea:'li a5, 0',0x4eff0:'li a2, 12',0x4eff2:'lw a1, 0(a3)',0x4eff4:'bnez a1, 0x4f000',0x4effa:'sw a0, 0(a5)'}.items()),'Actual ancestor clear/literal/first-empty registration operands')
 need(0x20003000+856==0x20003358 and 48//4==12,'Same48-byte callback table for clearing,registration and dispatch')
 operands({0x4f0cc:'beqz a0, 0x4f126',0x4f0ce:'addi sp, sp, -32',0x4f0e6:'mv s1, a0',0x4f0e8:'addi s2, s2, 940',0x4f0f0:'li s5, 60',0x4f0f4:'addi s3, s3, -1',0x4f0f6:'lbu a5, 8(s2)',0x4f0fa:'blt s0, a5, 0x4f110',0x4f110:'mul a0, s0, s5',0x4f114:'lw a5, 852(s4)',0x4f118:'add a0, a0, a5',0x4f11a:'qk.c.lhu a5, 2(a0)',0x4f11c:'beq a5, s3, 0x4f122',0x4f120:'jalr s1',0x4f122:'addi s0, s0, 1',0x4f124:'j 0x4f0f6',0x4f126:'ret'})
 for reg,p,w in [('s1',0x4f120,[0x4f0e6]),('a0',0x4f120,[0x4f118])]:definitions(0x4f0cc,reg,p,w)
 need(int.from_bytes(raw[0xb4:0xb8],'little')==0x4f0cc,'Per-link API slot points to4F0CC,including its null guard')
 operands({0x4eb12:'addi sp, sp, -48',0x4eb2a:'mv s4, a3',0x4eb2c:'bne a1, a4, 0x4eb96',0x4eb30:'qk.c.lhu a0, 2(a2)',0x4eb32:'li s0, 2',0x4eb34:'jal ra, 0x4d5a0',0x4eb38:'sw a0, 12(sp)',0x4eb3a:'beqz a0, 0x4eba6',0x4eb3c:'lw a5, 12(a0)',0x4eb42:'qk.c.lhu a5, 2(a5)',0x4eb44:'qk.c.sh a5, 0(s1)',0x4eb4e:'sb s5, 0(a5)',0x4eb52:'lbu a2, 796(a3)',0x4eb58:'addi a4, a2, 1',0x4eb5c:'andi a4, a4, 255',0x4eb60:'sb a4, 796(a3)',0x4eb64:'qk.c.sb a2, 4(a5)',0x4eb68:'li a4, 1',0x4eb6a:'sb a4, 796(a3)',0x4eb7e:'mv a4, s4',0x4eb80:'mv a3, s1',0x4eb86:'jal ra, 0x4ea8c',0x4eb8e:'beqz s0, 0x4ebba',0x4eb90:'jal ra, 0x4d66e',0x4eb9e:'jal ra, 0x4d4bc',0x4ebba:'li a1, 30',0x4ebbc:'jal ra, 0x4d806'})
 definitions(0x4eb12,'a4',0x4eb86,[0x4eb7e]);definitions(0x4eb12,'s4',0x4eb7e,[0x4eb2a])
 operands({0x4d4bc:'beqz a3, 0x4d59a',0x4d4d8:'jal ra, 0x4f072',0x4d4dc:'li a5, 20',0x4d4de:'beqz a0, 0x4d50c',0x4d50a:'li a5, 21',0x4d53a:'li a0, 32',0x4d546:'sw a0, 12(s2)',0x4d54a:'beqz a0, 0x4d50a',0x4d54c:'li a2, 32',0x4d552:'addi s1, s1, 64',0x4d55e:'sh s1, 2(s2)',0x4d580:'srai s0, s0, 0x4',0x4d582:'c.srli s0, s0, 0x4',0x4d584:'qk.c.sb s0, 28(a5)',0x4d586:'sw s2, 0(s3)',0x4d58a:'li a5, 0',0x4d59a:'li a5, 1',0x4d5a4:'lbu a1, -96(a5)',0x4d5ac:'lw a4, -104(a5)',0x4d5b2:'bne a1, a5, 0x4d5bc',0x4d5bc:'qk.c.lhu a2, 2(a4)',0x4d5c0:'beqz a2, 0x4d5c6',0x4d5c2:'beq a2, a0, 0x4d5b8',0x4d5cc:'addi a4, a4, 16'})
 operands({0x4ea9e:'sw s0, 56(sp)',0x4eaa2:'sw a3, 12(sp)',0x4eaa4:'sw a4, 8(sp)',0x4eaa6:'jal ra, 0x4da42',0x4eaaa:'beqz a0, 0x4eb0e',0x4eaac:'lw a4, 8(sp)',0x4eab2:'beqz a4, 0x4eabe',0x4eab4:'lw a3, 12(sp)',0x4eab6:'addi a0, s0, 4',0x4eaba:'mv a1, a3',0x4eabc:'jalr a4',0x4eac2:'sb s3, 0(s0)',0x4eac6:'sb s2, 1(s0)',0x4eaca:'qk.c.sb a5, 3(s0)',0x4eacc:'li a5, 5',0x4eace:'qk.c.shsp a5, 24(sp)',0x4ead8:'qk.c.sb a0, 2(s0)',0x4eada:'addi a0, a0, 4',0x4eae4:'beqz a5, 0x4eb08',0x4eae6:'jal ra, 0x4e6ca',0x4eaf4:'jalr 1568(ra)',0x4eb08:'jal ra, 0x4e4cc',0x4eb0e:'li s1, 19'})
 definitions(0x4ea8c,'a4',0x4eabc,[0x4eaac]);definitions(0x4ea8c,'a0',0x4eabc,[0x4eab6]);definitions(0x4ea8c,'a1',0x4eabc,[0x4eaba])
 need([o['addr']for o in fs[0x4ea8c]['operations']if o['addr']<0x4eabc and o['opcode'].endswith(', 8(sp)')and o['opcode'].startswith('sw ')]==[0x4eaa4],'Only explicit caller-owned stack8 store before serializer reload')
 operands({0x4d806:'li a2, 1600',0x4d80a:'mul a2, a1, a2',0x4d80e:'addi a3, a0, 9',0x4d814:'lui a0, 0x4d',0x4d818:'addi a0, a0, 1760',0x4d81c:'j 0x43874',0x4d6e0:'beqz a0, 0x4d708',0x4d6e2:'qk.c.lhu a4, 2(a0)',0x4d6ec:'beqz a4, 0x4d700',0x4d6ee:'li a1, 23',0x4d6f0:'jal ra, 0x4e46e',0x4d6fa:'addi sp, sp, 16',0x4d6fc:'j 0x4d66e'})
 need(0x4d000+1760==0x4d6e0 and e['raw_pointer_literal_dependencies']==[dict(PC=0x4d814,low_PC=0x4d818,value=0x4d6e0,body_provided=True,typed_relocation=False,physical_binding_proved=False)],'Actual scheduled callback literal has whole body,no invented typed binding')
 operands({0x4da42:'addi a0, a0, 6',0x4da46:'slli a0, a0, 0x10',0x4da4e:'srli a0, a0, 0x10',0x4da5a:'beqz a0, 0x4da6a',0x4da5e:'li a1, -6',0x4da60:'addi sp, sp, 16',0x4da62:'auipc t1, 0x1ffb2',0x4da66:'jr 1922(t1)',0x200001ec:'lw a5, 404(a5)',0x200001f0:'lw a2, 396(a3)',0x200001f6:'sub a1, a0, a1',0x200001fa:'bne a2, a5, 0x20000202',0x200001fe:'mv a0, a4',0x20000202:'addi a3, a5, 8',0x20000206:'lw a5, 0(a5)',0x20000208:'bltu a4, a3, 0x200001fa',0x2000020c:'bleu a5, a4, 0x200001fa',0x20000210:'mv a0, a1',0x20000212:'bltu a1, a3, 0x200001fa',0x20000216:'bleu a5, a1, 0x200001fa'})
 operands({0x4e6ca:'qk.c.lhu a4, 2(a1)',0x4e6cc:'beqz a4, 0x4e7a0',0x4e6d2:'lhu a3, -98(a5)',0x4e6d8:'bltu a3, a4, 0x4e7a2',0x4e6f0:'jalr -1288(ra)',0x4e716:'bne s1, a5, 0x4e75e',0x4e724:'jalr -1258(ra)',0x4e72c:'beqz a0, 0x4e752',0x4e74c:'jal ra, 0x43208',0x4e762:'jal ra, 0x534a6',0x4e77e:'beq a0, a4, 0x4e7a6',0x4e784:'beq a0, a4, 0x4e7aa',0x4e78a:'beq a0, a4, 0x4e7ae',0x4e7a0:'li a5, 27',0x534a6:'j 0x6a626'})
 old='tsl9_candidate_unprovided_flash_4eb12';need(fs[0x4eb12]['name']==old and fs[0x4eb12]['end']==0x4ebc2 and e['resolved_prior_dependencies']==[old],'Historical import name resolves to its actual176-byte source,not an alias')
 need(e['new_genuine_code_dependency_entries']==[0x6a626]and len(e['real_prior_providers'])==10 and len(e['opaque_transfers'])==3,'Ten actual prior providers,one real new dependency,three open indirect sites')
 return dict(passed=True,whole_CFGs=cfgs,unique_reaching_definitions=rd,resolved_prior_entry=0x4eb12,resolved_prior_body_bytes=176,resolved_prior_symbol=old,resolution_uses_actual_CODE_not_alias=True,status_dispatcher=[0x4ed98,0x4edd2],status_callback_table=[0x20003358,0x20003388],status_callback_slots=12,status_dispatch_fresh_slot_loads=True,status_dispatch_null_slots_skipped_without_stopping=True,status_dispatch_preserves_original_handle_and_change_type=True,status_dispatch_no_return_status_short_circuit=True,conditional_registered_slot_address=0x20003358,conditional_registered_slot_value=0x4d916,conditional_registered_slot_proof='If nonzero-total initialization completes48B zero-fill and no interference precedes first-empty registration,the first slot receives literal4D916;the matching stable dispatch iteration calls it with saved original arguments',conditional_removed_event_chain=[0x4f00c,0x4ed98,0x4d916,0x4d83a],removal_function=[0x4f00c,0x4f058],removal_missing_record_status=2,removal_found_record_status=0,removal_dispatch_event=1,removal_dispatch_precedes_nested_release_and_record_clear=True,removal_optional_release_offset=44,removal_clear_bytes=60,removal_reset_handle=65535,removal_reset_state=0,per_link_iterator=[0x4f0cc,0x4f128],per_link_iterator_is_not_status_dispatcher=True,per_link_API_slot=0x400b4,per_link_null_callback_returns_before_frame=True,per_link_callback_argument_is_record_pointer=True,per_link_record_stride=60,per_link_skips_handle65535=True,per_link_total_reloaded_each_iteration=True,per_link_record_pointer_reloaded_each_iteration=True,request_core=[0x4eb12,0x4ebc2],request_special_selector=6,request_missing_existing_record_status=2,request_existing_nested_pointer_validity_is_required=True,request_transaction_counter=0x2000331c,request_counter_increment_masks8_and_skips_zero=True,request_send_error_cleans_record=True,request_send_zero_schedules_numeric_delay_argument=30,delay_helper=[0x4d806,0x4d820],delay_multiplier=1600,delay_units_or_physical_time_proved=False,scheduled_callback_literal=0x4d6e0,scheduled_callback=[0x4d6e0,0x4d70a],scheduled_callback_nonzero_key_status=23,scheduled_callback_frame_released_cleanup_tail=True,pending_allocator=[0x4d4bc,0x4d5a0],pending_allocator_null_out_pointer_status=1,pending_allocator_not_connected_status=20,pending_allocator_no_slot_or_heap_status=21,pending_nested_allocation_bytes=32,pending_owner_stride=16,pending_allocator_preserves_both_arithmetic_and_logical_shifts_at=[0x4d580,0x4d582],serializer_call=0x4eabc,serializer_target_from_saved_incoming_A4_stack8=True,serializer_arguments=['destination_buffer+4','saved_incoming_A3'],known_wrapper_serializer_literal=0x4ebc2,known_wrapper_literal_binding_still_requires_original_layout=True,numeric_envelope_channel=5,numeric_envelope_header_bytes=4,numeric_envelope_fields=['incoming selector','incoming transaction byte','serializer length low8','serializer length high8'],numeric_envelope_is_not_full_protocol_or_hardware_proof=True,allocation_extra_bytes=6,allocation_size_truncates16=True,prefix_helper=[0x200001e4,0x2000021c],prefix_helper_source=[0x40454,0x4048c],prefix_helper_bytes=56,prefix_helper_fallback_preserves_original_pointer=True,prefix_helper_heap_chain_validity_and_termination_unproved=True,send_wrapper=[0x4e6ca,0x4e7b2],send_wrapper_loopback_separate_message_path=True,send_edge_stub=[0x534a6,0x534aa],send_edge_stub_bytes=4,send_edge_stub_tail=0x6a626,remaining_named_UND=1,remaining_unprovided_normal_callee=0x6a626,opaque_call_sites=[0x4edbc,0x4f120,0x4eabc],all_indirect_runtime_targets_closed=False,conditional_local_callback_invocation_proved=True,global_callback_table_lifetime_or_physical_invocation_proved=False,CCC_record_clearing_proved=False,conditions=['Installed ROM/Xwchc/header and normal saved-register/argument ABI must match this archived candidate','Nonzero-total initialization completes callback-table clear;the literal registration succeeds;table/GP/code addresses remain stable to dispatch','Counts,pointers,16/60-byte tables,nested owners,stack frames and all copied buffers are valid at each fresh access;no incompatible alias/IRQ/DMA/reentrant mutation','The existing-record selector6 path requires a valid nested owner before its unguarded halfword read;heap-chain traversal must remain valid and terminate','Indirect callbacks return normally and preserve the required ABI;not all possible status/per-link/serializer targets are provided','Conditional copied RAM source and literal callback positions require original startup/layout;4B startup source and send-edge6A626 remain missing','Numeric statuses,envelope fields and delay arguments do not prove physical timing,CCC cleanup,radio delivery or OTA compatibility'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
def run(llvm,trial=None):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():need(sha(R/p)==h,'Frozen dispatch-core input '+p)
 for n,h in K['tools'].items():need(sha(llvm/n)==h,'Pinned LLVM '+n)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==K['stdint_sha256'],'Pinned compiler header')
 P=lib(K['parent_checker']);parent=P['run'](llvm);need(parent==read(R/K['parent_receipt']),'Fresh complete parent callback/native proof')
 N=lib(K['builder']);N['pins'](llvm);saved=read(HERE/'build/native-v1/measurement.json');need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every native dispatch-core input retained');native={}
 for mode in ['c','cpp']:
  folder=HERE/'build/native-v1'/mode;need(N['inventory'](folder)==saved['modes'][mode]['artifacts'],'All native artifacts retained')
  need(N['portable'](N['dependencies'](folder,llvm),llvm)==saved['modes'][mode]['dependencies'],'Complete include provenance')
  native[mode]=N['audit_object'](folder/'unit.o');need(native[mode]==saved['modes'][mode]['result']and N['audit_abi'](folder/'config_abi.o')==saved['modes'][mode]['ABI_result'],'Fresh native1260-byte/ABI comparison')
 need(native['c']==native['cpp']and len(native['c']['UND'])==11 and native['c']['opaque_call_sites']==3,'Identical native unit with genuine imports and open indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition trial')
 else:need(out.exists(),'Retained composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual SDK dispatch-core partial link')
  sdk[mode]=U['union'](obj,ins,K,(44610,412,3175,5,2535,1));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==44610 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==['tsl9_candidate_unprovided_flash_6a626'],'Unique SDK CODE with one honest send-edge import')
  bm=owned['_byte_map'];need(all(p in bm for p in range(0x4eb12,0x4ebc2)),'Every176-byte original import body genuinely owned')
  pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every complete native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==15515,'Actual whole SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual complete C/C++ SDK objects identical')
 result=dict(schema='TSL9-link-dispatch-core-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=14,new_SDK_CODE_bytes=1260,new_SDK_instructions=495,new_SDK_DATA_bytes=0,new_normal_imports_resolved=10,prior_genuine_import_body_resolved=0x4eb12,new_genuine_unprovided_normal_callee=0x6a626,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
 result=json.loads(json.dumps(result))
 if trial:
  need(not(HERE/'verification-v1.json').exists(),'Create-only successful receipt');(HERE/'verification-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 else:need(result==read(HERE/'verification-v1.json'),'Fresh full proof equals exact successful receipt')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');a=p.parse_args()
 try:
  v=run(a.tool_dir.resolve(),a.trial);print(json.dumps({k:v[k]for k in ['passed','new_complete_bodies','new_SDK_CODE_bytes','new_SDK_instructions','prior_genuine_import_body_resolved','new_genuine_unprovided_normal_callee','formal_APP_byte_coverage_unchanged','new_BIN']}))
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
