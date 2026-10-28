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
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();by={};graphs={};opmaps={};cfgs=[];rd=[];fs={f['start']:f for f in e['selected_functions']}
 need([(f['start'],f['end'])for f in e['selected_functions']]==[(0x5774e,0x5784a),(0x59042,0x595b8),(0x595b8,0x59d3e)]and e['code_bytes']==3576 and e['instructions']==1173,'Three complete original transmit/complete/drain bodies')
 for f in e['selected_functions']:
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every whole original handler byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);opmaps[f['start']]=ops;graphs[f['start']]=g;cfgs.append(c)
 def operands(w):need(all(by[p]['opcode']==s for p,s in w.items()),'Exact caller/header/release/guard operands')
 def definitions(start,reg,p,w):
  need(reaching(fs[start],opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG exact caller/completion register provenance');rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 operands({0x59050:'mv s0, a0',0x5920e:'auipc ra, 0x1ffa8',0x59212:'jalr -1864(ra)',0x59216:'bnez a0, 0x591f6',0x59218:'j 0x590aa',0x59280:'auipc ra, 0x1ffa8',0x59284:'jalr -1978(ra)',0x59288:'beqz a0, 0x590aa',0x59590:'auipc ra, 0x1ffa7',0x59594:'jalr 1334(ra)',0x59598:'beqz a0, 0x590aa'})
 for hi,lo in [(0x5920e,0x59212),(0x59280,0x59284),(0x59590,0x59594)]:
  need(e['reference_roles'][str(hi)]==dict(reference_kind='code-call',target=0x20000ac6),'Actual original far-call target is the provided RAM fragment body')
  definitions(0x59042,'a0',lo,[-1]);definitions(0x59042,'s0',lo,[0x59050])
 need(parent['contract']['fragment_preparer']==[0x20000ac6,0x20000bc0]and parent['contract']['first_whole_state']==1 and parent['contract']['split_state']==2 and parent['contract']['continuation_whole_state']==3,'Fresh actual fragment-provider/state proof')
 operands({0x590aa:'qk.c.lbu a4, 27(s0)',0x590ac:'li a5, 1',0x590ae:'bne a4, a5, 0x5919c',0x590b2:'lw a5, 280(s0)',0x590b6:'qk.c.lbu a4, 12(s0)',0x590b8:'lw a5, 4(a5)',0x590ba:'qk.c.sb a4, 0(a5)',0x590bc:'lw a5, 280(s0)',0x590c0:'qk.c.lbu a4, 21(s0)',0x590c2:'lw a5, 4(a5)',0x590c4:'qk.c.sb a4, 1(a5)',0x590c6:'lw a4, 280(s0)',0x590ca:'lw a5, 1340(s1)',0x590ce:'lw a4, 4(a4)',0x590d4:'sw a4, 112(a5)',0x5919c:'lw a5, 272(s0)',0x591a0:'qk.c.lbu a4, 12(s0)',0x591a2:'qk.c.sb a4, 0(a5)',0x591a4:'lw a5, 272(s0)',0x591a8:'qk.c.lbu a4, 21(s0)',0x591aa:'qk.c.sb a4, 1(a5)',0x591ac:'lw a5, 1340(s1)',0x591b0:'lw a4, 272(s0)',0x591b4:'j 0x590d0'})
 definitions(0x59042,'a4',0x590d4,[0x590ce,0x591b0]);definitions(0x59042,'a5',0x590d4,[0x590ca,0x591ac])
 operands({0x595bc:'lui s2, 0x20003',0x595c0:'addi a5, s2, 952',0x595c6:'lw s0, 164(a5)',0x595d0:'lui s1, 0x20003',0x595e8:'addi s1, s1, 1300',0x597e2:'qk.c.lbu a5, 6(s1)',0x597e4:'andi a5, a5, 1',0x597e6:'bnez a5, 0x59b30',0x597fe:'mv a0, s0',0x59800:'jal ra, 0x560b2',0x59804:'bnez a0, 0x5985e',0x59806:'lw a5, 280(s0)',0x5980e:'beqz a5, 0x5984c',0x59810:'qk.c.lbu a4, 27(s0)',0x59812:'beqz a4, 0x5984c',0x59814:'qk.c.lbu a4, 9(a5)',0x59816:'andi a4, a4, 1',0x59818:'bnez a4, 0x5984c',0x5981a:'qk.c.lhu a4, 10(a5)',0x5981c:'lw a0, 4(a5)',0x5981e:'ori a4, a4, -256',0x59822:'qk.c.sh a4, 10(a5)',0x59824:'auipc ra, 0x1ffa7',0x59828:'jalr -1812(ra)',0x5982c:'lhu a5, 68(s0)',0x59830:'addi a5, a5, 1',0x59832:'sh a5, 68(s0)',0x59836:'lw a5, 280(s0)',0x5983a:'lw a5, 0(a5)',0x5983c:'sw a5, 280(s0)',0x59840:'lw a5, 420(s0)',0x59844:'beqz a5, 0x5984c',0x59846:'addi a5, a5, -1',0x59848:'sw a5, 420(s0)'})
 g=graphs[0x595b8];dominators=[0x597e6,0x59804,0x5980e,0x59812,0x59818,0x59822,0x59828]
 need(all(0x5983c not in V['reachable'](g,0x595b8,skip=p)for p in dominators),'All original status/helper/head/state/marker/tag/free stages dominate completion head update')
 need(e['reference_roles'][str(0x59824)]==dict(reference_kind='code-call',target=0x20000110),'Actual payload-release helper,not a standard-library replacement')
 definitions(0x595b8,'s0',0x59806,[0x595c6]);definitions(0x595b8,'a0',0x59828,[0x5981c])
 operands({0x57754:'mv s0, a0',0x57756:'lw a5, 280(s0)',0x5775a:'bnez a5, 0x5780a',0x5775c:'lw a5, 288(s0)',0x57760:'bnez a5, 0x5782a',0x57762:'lw a0, 272(s0)',0x57766:'beqz a0, 0x57770',0x57770:'lbu a0, 39(s0)',0x57780:'lbu a0, 38(s0)',0x57790:'lbu a0, 40(s0)',0x577a0:'lbu a0, 41(s0)',0x577b2:'sb a5, 41(s0)',0x577b6:'qk.c.lhu a0, 8(s0)',0x577b8:'jal 0x57a4a',0x5780a:'lw a0, 4(a5)',0x5780c:'beqz a0, 0x57816',0x57812:'jalr -1790(ra)',0x57816:'lw a5, 280(s0)',0x5781a:'qk.c.lhu a4, 10(a5)',0x5781c:'ori a4, a4, -256',0x57820:'qk.c.sh a4, 10(a5)',0x57822:'lw a5, 0(a5)',0x57824:'sw a5, 280(s0)',0x57828:'j 0x57756',0x5782a:'lw a0, 4(a5)',0x5782c:'beqz a0, 0x57836',0x57832:'jalr -1822(ra)',0x57836:'lw a5, 288(s0)',0x5783a:'qk.c.lhu a4, 10(a5)',0x5783c:'ori a4, a4, -256',0x57840:'qk.c.sh a4, 10(a5)',0x57842:'lw a5, 0(a5)',0x57844:'sw a5, 288(s0)',0x57848:'j 0x5775c'})
 for p in [0x57768,0x577f2,0x5780e,0x5782e]:need(e['reference_roles'][str(p)]==dict(reference_kind='code-call',target=0x20000110),'Original guarded drain/frame/shared release calls')
 need(len(e['new_genuine_code_dependencies'])==len(e['new_genuine_code_dependency_entries'])==42 and len(e['real_prior_providers'])==12,'All twelve real prior providers and42 genuine new missing dependencies retained')
 need(len(e['opaque_transfers'])==2 and [x['PC']for x in e['opaque_transfers']]==[0x599f6,0x59bec],'Two runtime indirect callback sites remain open')
 need(parent['contract']['first_fragment_test_marker_high_bit']==128 and parent['contract']['clear_first_marker_high_bit_on_split']and parent['contract']['whole_fragment_clears_node_marker_byte'],'Fresh producer marker transitions match completion low-bit gate under stable ownership')
 return dict(passed=True,whole_CFGs=cfgs,unique_reaching_definitions=rd,whole_code_bytes=3576,whole_instructions=1173,whole_handler_entries=[0x5774e,0x59042,0x595b8],fragment_calling_handler=[0x59042,0x595b8],completion_handler=[0x595b8,0x59d3e],drain_handler=[0x5774e,0x5784a],admitted_fragment_far_calls=[dict(high=0x5920e,call=0x59212,target=0x20000ac6),dict(high=0x59280,call=0x59284,target=0x20000ac6),dict(high=0x59590,call=0x59594,target=0x20000ac6)],all_three_fragment_calls_preserve_original_incoming_record_A0=True,static_original_call_binding_proved=True,physical_incoming_event_or_IRQ_binding_proved=False,prepared_state_byte_offset=27,state1_selects_queue_head_buffer=True,other_states_select_record_frame_buffer=True,queue_head_record_offset=280,node_buffer_pointer_offset=4,frame_buffer_record_offset=272,header_byte0_source_record_offset=12,header_byte1_source_record_offset=21,handoff_context_pointer_global=0x2000353c,handoff_word_offset=112,handoff_source_paths=['state1:queue_head.buffer','other:record.frame_buffer'],first_whole_no_copy_explained_by_caller_direct_buffer_handoff=True,physical_handoff_register_or_radio_delivery_proved=False,completion_current_record_pointer_global=0x2000345c,completion_status_byte=0x2000351a,completion_status_bit0_must_be_clear=True,completion_helper_560b2_result_must_be_zero=True,completion_requires_nonnull_head=True,completion_requires_prepared_state_nonzero=True,completion_requires_head_marker_low_bit_clear=True,completion_head_update_PC=0x5983c,completion_guard_and_release_dominators=dominators,completion_tag_update_PC=0x59822,completion_tag_formula='uint16(tag | 0xff00)',completion_preserves_tag_low_byte=True,completion_release_PC=0x59828,completion_release_target=0x20000110,completion_release_argument_is_current_node_buffer=True,completion_increments_halfword_counter_offset=68,completion_refreshes_queue_head_after_release=True,completion_head_update_uses_current_head_next=True,completion_optional_decrement_word_offset=420,known_marker0x81_to0x01_split_keeps_low_bit_set=True,known_whole_fragment_marker_zero_is_eligible_only_under_other_guards=True,physical_ACK_or_CRC_meaning_proved=False,drain_TX_head_offset=280,drain_other_queue_head_offset=288,drain_null_buffer_guard=True,drain_payload_release_precedes_tag_restore_and_head_advance=True,drain_restores_tag_high_byte_ff=True,drain_refreshes_head_after_release=True,drain_does_not_explicitly_clear_tail_fields=True,drain_guarded_frame_buffer_release_offset=272,drain_optional_slot_release_offsets=[39,38,40,41],drain_slot_sentinel=255,drain_controller_release_callee=0x57a4a,custom_release_and_buffer_lifetime_still_require_proof=True,new_native_imports=54,real_prior_imports_resolved=12,new_genuine_missing_normal_dependencies=42,new_genuine_missing_entries=e['new_genuine_code_dependency_entries'],runtime_indirect_sites=[0x599f6,0x59bec],readonly_RAM_MMIO_dependencies_closed=False,literal_address_CODE_DATA_classification_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Actual installed ROM/Xwchc/header and saved-register/argument ABI must match this archived candidate','Incoming controller record,queue/node/frame buffers,head/tail links,mutable counters and status snapshots remain valid;no incompatible alias/IRQ/DMA/reentrant mutation','The three encoded far calls use the original incoming record;copied RAM code and final original-address binding must still be valid on hardware','Handoff global2000353C/word112 is an original pointer write;its physical MMIO/DMA/radio meaning is not established','Completion eligibility follows numeric status/helper/state/marker gates;hardware ACK/CRC interpretation and actual event arrival remain unproved','Payload release uses the current node.buffer value;custom allocator/free behavior and ownership ranges must be valid;do not replace it with an assumed standard free','All42 new normal callees,readonly/RAM dependencies and two new indirect sites remain explicit gaps;no fake providers or callback bodies are supplied','Startup4B source,installed ROM identity,physical RAM/IRQ/Flash and OTA compatibility remain incomplete'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==54 and native['c']['opaque_call_sites']==2,'Identical whole-handler unit with54 real imports and two open indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(48720,412,3595,5,2913,42));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==48720 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  bm=owned['_byte_map'];need(all(p in bm for p in range(0x59042,0x59d3e)),'Every original3324-byte calling/completion body genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==16883,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-transmit-handlers-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=3,new_SDK_CODE_bytes=3576,new_SDK_instructions=1173,new_SDK_DATA_bytes=0,new_normal_imports_resolved=12,prior_genuine_import_body_resolved=None,new_genuine_unprovided_normal_callees=42,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
