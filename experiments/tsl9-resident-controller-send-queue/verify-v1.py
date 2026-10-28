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
 pure=set('beq beqz bleu blt bltu bne bnez fence.i j jr ret'.split());stores=set('sb sh sw qk.c.sb qk.c.sh qk.c.shsp'.split())
 results=set('add addi and andi auipc c.srli lbu lhu li lui lw mul mv or sll slli srai srli sub qk.c.lbu qk.c.lhu'.split())
 volatile=set('ra t0 t1 t2 t3 t4 t5 t6 a0 a1 a2 a3 a4 a5 a6 a7'.split());incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
 while todo:
  p=todo.pop();o=ops[p];mn=o['opcode'].split()[0];need(mn in pure|stores|results|{'jal','jalr'},'Every original register-transfer opcode modelled')
  writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(o['type']in ['call','ucall']and reg in volatile);out={p}if writes else incoming[p]
  for n in g[p]:
   before=len(incoming[n]);incoming[n]|=out
   if before!=len(incoming[n]):todo.append(n)
 return incoming
def contract(K,parent):
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');P=lib(K['parent_checker']);U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py')
 e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();fs={f['start']:f for f in e['selected_functions']};by={};graphs={};opmaps={};cfgs=[];rd=[]
 def whole(f,frame,origin='SDK'):
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instructions')
   payload+=bb;at+=len(bb)
  base=0x40000 if origin=='SDK'else 0x8000;data=raw if origin=='SDK'else(R/K['APP']).read_bytes()
  need(at==f['end']and payload==data[f['start']-base:f['end']-base],'Every whole original reference byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
  ops,g,cfg=V['whole_cfg'](f,B,ext,frame);by.update(ops);graphs[f['start']]=g;opmaps[f['start']]=ops;cfgs.append(cfg)
  return payload
 need(len(fs)==2 and e['code_bytes']==284 and e['instructions']==101,'Exactly two whole284-byte101-instruction bodies')
 for f in e['selected_functions']:whole(f,f['own_frame_bytes'])
 def operands(w):need(all(by[p]['opcode']==s for p,s in w.items()),'Exact enqueue/pool/MMIO/configuration operands')
 def definitions(start,reg,p,w):
  need(reaching(fs[start],opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG unique controller argument/control provenance')
  rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 operands({0x6a634:'mv s3, a1',0x6a636:'mv s4, a2',0x6a638:'mv s1, a3',0x6a63a:'jal ra, 0x5784a',0x6a63e:'beqz a0, 0x6a6fc',0x6a640:'lui a5, 0x20003',0x6a644:'addi a5, a5, -88',0x6a648:'bnez s4, 0x6a662',0x6a64c:'li a4, 1',0x6a64e:'qk.c.sb a4, 0(a5)',0x6a650:'li a0, 0',0x6a65e:'addi sp, sp, 32',0x6a660:'ret',0x6a662:'qk.c.lbu a3, 0(a5)',0x6a668:'bne a3, a4, 0x6a672',0x6a66c:'sb zero, 0(a5)',0x6a670:'li s3, 2',0x6a672:'lui a5, 0x40024',0x6a676:'lw s2, 524(a5)',0x6a67a:'sw zero, 524(a5)',0x6a67e:'fence.i',0x6a682:'lui a0, 0x10',0x6a684:'addi a0, a0, -172',0x6a688:'jal ra, 0x57862',0x6a68c:'beqz a0, 0x6a6dc'})
 for reg,p,w in [('a0',0x6a63a,[-1]),('s4',0x6a648,[0x6a636]),('s1',0x6a6a4,[0x6a638]),('s2',0x6a6ce,[0x6a676]),('s2',0x6a6f4,[0x6a676]),('a0',0x6a688,[0x6a684])]:definitions(0x6a626,reg,p,w)
 operands({0x6a68e:'qk.c.lbu a5, 10(a0)',0x6a690:'qk.c.sh a5, 10(a0)',0x6a692:'lw a5, 280(s0)',0x6a696:'bnez a5, 0x6a6d4',0x6a698:'sw a0, 280(s0)',0x6a69c:'sw a0, 284(s0)',0x6a6a0:'li a5, -127',0x6a6a4:'addi s1, s1, -2',0x6a6a6:'sw zero, 0(a0)',0x6a6aa:'sh s4, 12(a0)',0x6a6ae:'qk.c.sb a5, 9(a0)',0x6a6b0:'sb s3, 8(a0)',0x6a6b4:'sw s1, 4(a0)',0x6a6b6:'lbu a5, 41(s0)',0x6a6ba:'li a1, 1',0x6a6bc:'li a0, 0',0x6a6be:'sll a1, a1, a5',0x6a6c2:'slli a1, a1, 0x10',0x6a6c4:'srli a1, a1, 0x10',0x6a6c6:'jal ra, 0x4354a',0x6a6ca:'lui a5, 0x40024',0x6a6ce:'sw s2, 524(a5)',0x6a6d2:'j 0x6a650',0x6a6d4:'lw a5, 284(s0)',0x6a6d8:'sw a0, 0(a5)',0x6a6da:'j 0x6a69c',0x6a6dc:'lui a5, 0x20003',0x6a6e0:'lw a5, 544(a5)',0x6a6e4:'beqz a5, 0x6a6f0',0x6a6e6:'lui a1, 0x5',0x6a6e8:'addi a1, a1, 1365',0x6a6ec:'li a0, 1',0x6a6ee:'jalr a5',0x6a6f0:'lui a5, 0x40024',0x6a6f4:'sw s2, 524(a5)',0x6a6f8:'li a0, 7',0x6a6fc:'li a0, 2'})
 for reg,p,w in [('a5',0x6a6ee,[0x6a6e0]),('a0',0x6a6ee,[0x6a6ec]),('a1',0x6a6ee,[0x6a6e8]),('a1',0x6a6e8,[0x6a6e6])]:definitions(0x6a626,reg,p,w)
 g=graphs[0x6a626];states={p:set()for p in g};pending=[(0x6a626,0)];restore_sites={0x6a6ce,0x6a6f4};normal_restores=[]
 while pending:
  p,before=pending.pop()
  if before in states[p]:continue
  states[p].add(before);after=before
  if p==0x6a67a:need(before==0,'One original MMIO clear,without nesting');after=1
  if p in restore_sites:need(before==1,'Restore has the original cleared control word outstanding');after=0;normal_restores.append(p)
  if not g[p]:need(after==0,'Every normal return after MMIO clear follows a matching restore')
  pending.extend((n,after)for n in g[p])
 need(set(normal_restores)==restore_sites and states[0x6a6ee]=={1},'Both restore branches and optional callback ordering observed')
 need(0x40024000+524==0x4002420c and 0x20003000-88==0x20002fa8 and 0x20003000+544==0x20003220,'Actual control/flag/callback addresses')
 operands({0x57862:'lui a4, 0x20003',0x57866:'lbu a3, 507(a4)',0x5786e:'lbu a2, 576(a4)',0x57876:'lw a5, 1124(a5)',0x5787a:'addi a4, a3, 1',0x5787e:'beqz a2, 0x57884',0x57880:'slli a4, a3, 0x1',0x57884:'slli a4, a4, 0x4',0x57888:'add a4, a4, a5',0x5788a:'addi a3, a3, -1',0x5788c:'bne a4, a5, 0x57896',0x57890:'li a5, 0',0x57892:'mv a0, a5',0x57896:'qk.c.lhu a2, 10(a5)',0x57898:'beq a2, a0, 0x57892',0x5789c:'beq a2, a3, 0x57892',0x578a0:'addi a5, a5, 16',0x578a2:'j 0x5788c'})
 pool=e['pool_initializer_reference'];need(pool==next(f for f in read(R/e['pool_initializer_evidence'])['selected_functions']if f['start']==0x578a4),'Exact already-provided pool initializer reference');whole(pool,32)
 operands({0x578b0:'lw a5, 172(a5)',0x578be:'bnez a5, 0x57932',0x578cc:'qk.c.lbu a5, 15(a5)',0x578ce:'lbu a3, 576(a3)',0x578da:'addi s2, a5, 1',0x578e0:'slli s2, a5, 0x1',0x578e4:'lhu s0, 46(s3)',0x578e8:'sub a0, s2, a5',0x578ec:'slli s1, s2, 0x4',0x578f0:'addi s0, s0, 33',0x578f4:'srai s0, s0, 0x5',0x578f6:'slli s0, s0, 0x5',0x578f8:'slli s0, s0, 0x10',0x578fa:'c.srli s0, s0, 0x10',0x578fc:'mul a0, s0, a0',0x57904:'add a0, a0, s1',0x57906:'slli a0, a0, 0x10',0x57908:'srli a0, a0, 0x10',0x5790a:'auipc ra, 0x1ffa8',0x5790e:'jalr 1846(ra)',0x57912:'beqz a0, 0x57932',0x57914:'lbu a3, 15(s4)',0x57918:'sw a0, 172(s3)',0x5791c:'add a4, a0, s1',0x57920:'sub a3, s2, a3',0x57926:'li a2, -172',0x5792a:'li a1, -174',0x57946:'sw a4, 4(a0)',0x57948:'qk.c.sh a1, 10(a0)',0x57950:'sb zero, 9(a0)',0x57956:'addi a0, a0, 16',0x5795a:'qk.c.sh a2, 10(a0)',0x5795c:'sw zero, 4(a0)'})
 E=lib(K['reader'])['ELF'];O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');owned=O['inspect'](R/K['SDK_parent']/'c/candidate.o');bm=owned['_byte_map'];roles={tuple([json.loads(x)[0][1],json.loads(x)[1],json.loads(x)[3][1]])for x in owned['_typed_relations']}
 def native_reference(f):
  for o in f['operations']:
   p=o['addr'];bb=bytes.fromhex(o['bytes']);nn=bytes(bm[p+i]for i in range(len(bb)));d=B['decode_control'](bb,p);rels=[v for v in roles if v[0]==p]
   if d:
    kind,target=d;need((p,kind,target)in roles,'Actual retained reference control target');mask=B['MASKS'][kind][1]
    need(int.from_bytes(bb,'little')&mask==int.from_bytes(nn,'little')&mask,'Reference native control opcode bits')
   elif rels:
    need(len(rels)==1 and rels[0][1]in [23,24],'Actual retained far-pair role');mask=B['MASKS'][rels[0][1]][1]
    need(int.from_bytes(bb,'little')&mask==int.from_bytes(nn,'little')&mask,'Reference native PC-relative opcode bits')
   else:need(bb==nn,'Every retained nonrelocated reference byte')
 native_reference(pool);need((0x5790a,23,0x20000040)in roles,'Real original pool heap-allocation provider')
 app=next(f for f in read(R/K['config_evidence'])['selected_functions']if f['start']==0x199e2);payload=whole(app,96,'APP');diag=E(R/K['APP_ELF']);need(payload==U['native_bytes'](diag,app['start'],app['end']),'Every308-byte original APP config byte equals the formal native diagnostic')
 operands({0x199f0:'lui s0, 0x40',0x19a20:'li a2, 64',0x19a2e:'li a1, 0',0x19a34:'lw a5, 72(s0)',0x19a36:'addi a0, sp, 16',0x19a38:'jalr a5',0x19a54:'lui a5, 0x1',0x19a56:'addi a4, a5, -2045',0x19a5a:'sh a4, 30(sp)',0x19ae6:'lw a5, 164(a5)',0x19aea:'addi a0, sp, 16',0x19aec:'jalr a5'})
 for reg,p,w in [('a0',0x19a38,[0x19a36]),('a1',0x19a38,[0x19a2e]),('a2',0x19a38,[0x19a20]),('a5',0x19a38,[0x19a34]),('s0',0x19a34,[0x199f0]),('a4',0x19a5a,[0x19a56]),('a5',0x19a56,[0x19a54])]:
  need(reaching(app,opmaps[app['start']],graphs[app['start']],reg)[p]==set(w),'Whole APP config argument/value provenance');rd.append(dict(function=app['start'],register=reg,PC=p,definitions=sorted(w)))
 need(int.from_bytes(raw[0x48:0x4c],'little')==0x2000039c,'APP64-byte clear uses actual original memset slot')
 stores=[]
 for o in app['operations']:
  p=o['addr'];m=re.fullmatch(r'(sb|sh|sw) \w+, (-?\d+)\(sp\)',o['opcode'])
  if not m or not 0x19a38<p<0x19aec:continue
  off=int(m[2]);width={'sb':1,'sh':2,'sw':4}[m[1]];need(not(off<72 and 68<off+width),'No later explicit SP store overlaps staCB52')
  if p>0x19a5a:need(not off<=31<off+width,'No later explicit SP store overlaps BufNumber15')
  stores.append(dict(PC=p,offset=off,bytes=width))
 cap=read(R/K['capacity_receipt'])['contract'];need(cap['six_byte_copy_stack_offsets']==[40,46]and cap['BLE_library_config_base']==0x200031ec,'Fresh ancestor copy-loop/config base provenance')
 ble=next(f for f in read(R/K['BLE_evidence'])['selected_functions']if f['start']==0x43c7e);whole(ble,16);native_reference(ble)
 operands({0x43cc4:'lui s0, 0x20003',0x43cc8:'li a2, 64',0x43cce:'addi a0, s0, 492',0x43cda:'li a2, 64',0x43cde:'mv a1, s1',0x43ce0:'addi a0, s0, 492',0x43ce8:'jalr 1614(ra)'})
 need(0x200031ec+15==0x200031fb and 0x200031ec+52==0x20003220 and((0x1000-2045)>>8)==8,'Copied BufNumber8 and staCB addresses,without observing device data')
 old='tsl9_candidate_unprovided_flash_6a626';need(fs[0x6a626]['name']==old and fs[0x6a626]['end']==0x6a700 and e['resolved_prior_dependencies']==[old]and not e['new_genuine_code_dependency_entries'],'Actual218-byte controller body resolves prior import')
 need(parent['contract']['send_edge_stub']==[0x534a6,0x534aa]and parent['contract']['send_edge_stub_tail']==0x6a626,'Fresh prior actual4-byte send-edge tail')
 return dict(passed=True,whole_CFGs=cfgs,unique_reaching_definitions=rd,controller_enqueue=[0x6a626,0x6a700],controller_enqueue_bytes=218,controller_enqueue_instructions=79,pool_lookup=[0x57862,0x578a4],pool_lookup_bytes=66,pool_lookup_instructions=22,prior_import_resolved_to_actual_CODE=0x6a626,connection_lookup=0x5784a,invalid_connection_status=2,zero_length_tests_original_argument=True,zero_length_sets_shared_flag_and_returns_zero=True,shared_argument_override_flag=0x20002fa8,next_valid_nonzero_length_when_flag1_clears_flag_and_uses_argument2=True,shared_flag_is_not_per_connection=True,control_word=0x4002420c,control_read_PC=0x6a676,control_clear_PC=0x6a67a,original_fence_i_PC=0x6a67e,control_restore_PCs=[0x6a6ce,0x6a6f4],matching_restore_on_all_normal_paths_after_clear=True,physical_register_role_or_interrupt_semantics_proved=False,requested_pool_tag=0xff54,pool_record_stride=16,pool_record_tag_offset=10,pool_acceptable_tags_under_stability=[0xff54,0xffff],pool_first_acceptable_in_scan_order=True,pool_no_global_exact_match_preference=True,pool_lookup_not_heap_allocator=True,pool_low_byte_read_then_halfword_write_preserved=True,pool_narrowing_store_offset=10,node_queue_next_offset=0,node_buffer_pointer_offset=4,node_argument_byte_offset=8,node_marker_byte_offset=9,node_marker_byte=129,node_length_halfword_offset=12,node_stored_buffer_is_incoming_pointer_minus2=True,incoming_payload_pointer_null_guard_present=False,connection_queue_head_offset=280,connection_queue_tail_offset=284,consistent_head_tail_and_buffer_prefix_required=True,queue_empty_sets_head_and_tail=True,queue_nonempty_links_old_tail_then_replaces_tail=True,event_task_argument=0,event_slot_byte_offset=41,event_mask_formula='low16(1u << (slot_byte & 31)) under original RV32 instruction semantics',original_variable_sll_port_preserved=True,event_setter=0x4354a,event_setter_result_is_ignored=True,queue_return_zero_is_not_radio_delivery_proof=True,pool_lookup_failure_status=7,pool_failure_callback_address=0x20003220,pool_failure_callback_arguments=[1,0x5555],pool_failure_callback_runs_before_control_restore=True,live_error_callback_targets_closed=False,pool_initializer_reference=[0x578a4,0x57962],pool_initializer_reference_bytes=190,pool_initializer_reference_instructions=66,pool_initializer_new_CODE=False,pool_initializer_input_count_byte=0x200031fb,pool_mode_flag=0x20003240,pool_base_pointer=0x20003464,pool_count_formula='mode==0 ? c+1 : 2*c',pool_count_inputs_sampled_once_for_lookup=True,pool_initializer_skips_existing_nonzero_pointer=True,pool_initializer_heap_failure_leaves_pointer_unprovided=True,pool_initializer_does_not_prove_boot_order=True,pool_initializer_fresh_count_reload_after_heap_preserved=True,pool_buffer_size_halfword=0x200033e6,pool_chunk_formula='low16(((L+33)>>5)<<5)',pool_allocation_formula='low16(chunk*(n-c)+16*n), with original fresh post-call c reload for partitioning',pool_initializer_tags=[0xff52,0xff54],pool_configuration_live_value_or_extent_proved=False,APP_config_reference_bytes=308,APP_config_clear_bytes=64,APP_BufNumber_store_halfword=0x0803,APP_BufNumber_store_PC=0x19a5a,APP_nominal_BufNumber=8,APP_BufNumber_stack_offset=31,APP_staCB_stack_range=[68,72],APP_staCB_has_no_later_explicit_overlapping_stack_store=True,APP_direct_stack_stores=stores,APP_nominal_staCB=0,conditional_nominal_pool_counts=dict(mode_zero=9,mode_nonzero=16),conditional_nominal_staCB_zero_skips_error_callback=True,conditional_config_preservation_is_not_live_value_proof=True,remaining_normal_named_UND=0,opaque_call_sites=[0x6a6ee],all_indirect_runtime_targets_closed=False,conditions=['Installed ROM/Xwchc/header and normal saved-register/argument ABI match the archived candidate','Live connection records,head/tail links,pool base/count/mode,heap chain and payload prefix are valid;no incompatible alias/IRQ/DMA/reentrant mutation','Pool initialization and allocation completed before lookup;pointer/count and16-bit allocation-size arithmetic describe valid nonwrapping storage','Control MMIO reads/writes and FENCE.I execute normally;the optional callback returns and preserves ABI so normal restore can occur','BufNumber8 and staCB0 require APP64B clear,observed stores and library copy to complete without intervening stack/config overwrite;later global writes remain unclosed','Queue insertion and ignored event-setter result do not prove task consumption,radio delivery,CCC notification or OTA compatibility','Literal/original layout,global lifetime,installed hardware and inherited4B startup source remain unproved'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==2 and native['c']['opaque_call_sites']==1,'Identical unit with two real prior imports and one generic indirect site')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(44894,412,3203,5,2553,0));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==44894 and owned['duplicate_original_CODE_bytes']==0 and not owned['named_UND'],'Unique actual SDK CODE and no unresolved normal imports')
  bm=owned['_byte_map'];need(all(p in bm for p in range(0x6a626,0x6a700)),'Every original218-byte controller body genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==15616,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-controller-send-queue-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=2,new_SDK_CODE_bytes=284,new_SDK_instructions=101,new_SDK_DATA_bytes=0,new_normal_imports_resolved=2,prior_genuine_import_body_resolved=0x6a626,new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
