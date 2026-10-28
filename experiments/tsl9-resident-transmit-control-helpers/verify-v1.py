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
 bounds=[(0x5a120,0x5a1dc,0),(0x5a568,0x5a588,0),(0x5a588,0x5a5ae,0),(0x5a614,0x5a686,0),(0x5a686,0x5a6e0,0),(0x5a6e0,0x5a70c,0),(0x5a70c,0x5a768,16),(0x5a7ba,0x5a804,16),(0x5a804,0x5a84e,16),(0x5a898,0x5a928,16)]
 need([(f['start'],f['end'],f['own_frame_bytes'])for f in e['selected_functions']]==bounds and e['code_bytes']==890 and e['instructions']==321,'Ten whole original control helpers')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in fs.values()}
 need(len(parentUND)==30 and len(provided)==10 and provided<=parentUND and set(K['expected_UND'])==parentUND-provided,'Exactly ten actual parent imports now supplied by original bodies')
 for f in fs.values():
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every original whole helper byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);opmaps[f['start']]=ops;graphs[f['start']]=g;cfgs.append(c)
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact original numeric operands and branch targets')
 def definitions(start,reg,p,w):
  need(reaching(fs[start],opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG exact argument provenance');rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 operands({0x5a120:'li a5, 12',0x5a122:'qk.c.sb a5, 21(a0)',0x5a124:'lw a5, 272(a0)',0x5a128:'beqz a5, 0x5a1d8',0x5a12a:'li a4, 2',0x5a12c:'sb a4, 85(a0)',0x5a130:'lhu a3, 94(a0)',0x5a134:'lhu a4, 64(a0)',0x5a138:'lhu a1, 96(a0)',0x5a13c:'bltu a3, a4, 0x5a14a',0x5a140:'addi a2, a1, 5',0x5a144:'sub a3, a3, a4',0x5a146:'blt a2, a3, 0x5a16c',0x5a14a:'lui a3, 0x20003',0x5a14e:'lhu a3, 1132(a3)',0x5a152:'li a6, 3',0x5a154:'li a2, 4',0x5a156:'bltu a6, a3, 0x5a160',0x5a15a:'addi a3, a3, 1',0x5a15c:'andi a2, a3, 255',0x5a160:'add a4, a4, a1',0x5a162:'addi a4, a4, 8',0x5a164:'sb a2, 85(a0)',0x5a168:'sh a4, 94(a0)',0x5a16c:'sb zero, 2(a5)',0x5a170:'lbu a4, 85(a0)',0x5a174:'qk.c.sb a4, 3(a5)',0x5a176:'lbu a4, 86(a0)',0x5a17a:'lhu a2, 88(a0)',0x5a17e:'lhu a3, 90(a0)',0x5a182:'qk.c.sb a4, 4(a5)',0x5a184:'lhu a4, 86(a0)',0x5a188:'qk.c.sb a2, 6(a5)',0x5a18a:'qk.c.sb a3, 8(a5)',0x5a18c:'srli a4, a4, 0x8',0x5a18e:'qk.c.sb a4, 5(a5)',0x5a190:'srli a4, a2, 0x8',0x5a194:'qk.c.sb a4, 7(a5)',0x5a196:'srli a4, a3, 0x8',0x5a19a:'qk.c.sb a4, 9(a5)',0x5a19c:'lhu a4, 92(a0)',0x5a1a0:'srli a1, a4, 0x8',0x5a1a4:'qk.c.sb a1, 11(a5)',0x5a1a6:'lbu a1, 94(a0)',0x5a1aa:'qk.c.sb a4, 10(a5)',0x5a1ac:'qk.c.sb a1, 12(a5)',0x5a1ae:'lhu a1, 94(a0)',0x5a1b2:'srli a1, a1, 0x8',0x5a1b4:'qk.c.sb a1, 13(a5)',0x5a1b6:'qk.c.lhu a1, 58(a0)',0x5a1b8:'li a5, 0',0x5a1ba:'bne a1, a2, 0x5a1cc',0x5a1be:'qk.c.lhu a2, 60(a0)',0x5a1c0:'bne a2, a3, 0x5a1cc',0x5a1c4:'qk.c.lhu a5, 62(a0)',0x5a1c6:'sub a5, a5, a4',0x5a1c8:'seqz a5, a5',0x5a1cc:'sh a5, 98(a0)',0x5a1d0:'li a5, 16',0x5a1d2:'qk.c.sb a5, 16(a0)',0x5a1d8:'li a0, 1',0x5a1da:'ret'})
 operands({0x5a568:'li a5, 2',0x5a56a:'qk.c.sb a5, 21(a0)',0x5a56c:'lw a5, 272(a0)',0x5a570:'li a4, 29',0x5a572:'qk.c.sb a4, 2(a5)',0x5a574:'lui a4, 0x20003',0x5a578:'lbu a4, 955(a4)',0x5a57c:'qk.c.sb a4, 3(a5)',0x5a588:'li a5, 2',0x5a58a:'qk.c.sb a5, 21(a0)',0x5a590:'li a4, 30',0x5a592:'qk.c.sb a4, 2(a5)',0x5a594:'lbu a4, 47(a0)',0x5a598:'qk.c.sb a4, 3(a5)',0x5a59a:'lw a5, 160(a0)',0x5a59e:'lui a4, 0x8',0x5a5a0:'or a5, a5, a4',0x5a5a2:'sw a5, 160(a0)'})
 operands({0x5a614:'lw a5, 272(a0)',0x5a618:'li a2, 4',0x5a61a:'li a4, 35',0x5a61e:'qk.c.sb a2, 21(a0)',0x5a620:'qk.c.sb a4, 2(a5)',0x5a622:'lbu a4, 370(a0)',0x5a626:'andi a4, a4, 4',0x5a628:'beqz a4, 0x5a65a',0x5a62a:'lbu a4, 372(a0)',0x5a62e:'sb zero, 4(a5)',0x5a632:'addi a3, a4, -1',0x5a636:'li a4, 1',0x5a638:'sll a4, a4, a3',0x5a63c:'qk.c.sb a4, 3(a5)',0x5a63e:'lbu a4, 323(a0)',0x5a642:'qk.c.sb a4, 5(a5)',0x5a644:'lbu a5, 42(a0)',0x5a648:'ori a5, a5, 4',0x5a64c:'sb a5, 42(a0)',0x5a65a:'lbu a3, 327(a0)',0x5a65e:'li a4, 2',0x5a660:'bne a3, a4, 0x5a67e',0x5a664:'lui a4, 0x20003',0x5a668:'lbu a4, 1311(a4)',0x5a66c:'beqz a4, 0x5a674',0x5a66e:'li a4, 8',0x5a670:'qk.c.sb a4, 3(a5)',0x5a674:'qk.c.sb a2, 3(a5)',0x5a676:'lbu a4, 383(a0)',0x5a67a:'qk.c.sb a4, 4(a5)',0x5a67c:'j 0x5a63e',0x5a67e:'li a4, 1',0x5a680:'sll a4, a4, a3',0x5a684:'j 0x5a670'})
 operands({0x5a686:'li a5, 5',0x5a688:'qk.c.sb a5, 21(a0)',0x5a68e:'li a4, 36',0x5a692:'qk.c.sb a4, 2(a5)',0x5a694:'sb zero, 3(a5)',0x5a698:'lb a4, 323(a0)',0x5a69c:'lb a3, 377(a0)',0x5a6a0:'bne a3, a4, 0x5a6a8',0x5a6a4:'li a3, 2',0x5a6a6:'qk.c.sb a3, 3(a5)',0x5a6a8:'lb a3, 376(a0)',0x5a6ac:'bne a3, a4, 0x5a6b8',0x5a6b0:'qk.c.lbu a3, 3(a5)',0x5a6b2:'ori a3, a3, 1',0x5a6b6:'qk.c.sb a3, 3(a5)',0x5a6b8:'lb a3, 375(a0)',0x5a6bc:'qk.c.sb a3, 4(a5)',0x5a6be:'lbu a2, 374(a0)',0x5a6c2:'qk.c.sb a4, 5(a5)',0x5a6c4:'qk.c.sb a2, 6(a5)',0x5a6c6:'lbu a5, 370(a0)',0x5a6ca:'andi a5, a5, 1',0x5a6cc:'beqz a5, 0x5a6dc',0x5a6ce:'beqz a3, 0x5a6dc',0x5a6d0:'lw a5, 160(a0)',0x5a6d4:'lui a4, 0x10',0x5a6d6:'or a5, a5, a4',0x5a6d8:'sw a5, 160(a0)',0x5a6e0:'li a5, 4',0x5a6e2:'qk.c.sb a5, 21(a0)',0x5a6e8:'li a4, 40',0x5a6ec:'qk.c.sb a4, 2(a5)',0x5a6ee:'lui a4, 0x20003',0x5a6f2:'lbu a4, 1034(a4)',0x5a6f6:'qk.c.sb a4, 3(a5)',0x5a6f8:'li a4, 10',0x5a6fa:'qk.c.sb a4, 4(a5)',0x5a6fc:'li a4, 50',0x5a700:'qk.c.sb a4, 5(a5)'})
 calls=[dict(entry=0x5a70c,high=0x5a73e,call=0x5a742,A0=0x5a738,A1=0x5a728,A2=0x5a73c,source_offset=296,destination_offset=3,length=5,guard=0x5a71c,null=0x5a764),dict(entry=0x5a7ba,high=0x5a7dc,call=0x5a7e0,A0=0x5a7da,A1=0x5a7d4,A2=0x5a7d8,source_offset=248,destination_offset=3,length=8,guard=0x5a7c2,null=0x5a800),dict(entry=0x5a804,high=0x5a824,call=0x5a828,A0=0x5a822,A1=0x5a81c,A2=0x5a820,source_offset=248,destination_offset=3,length=8,guard=0x5a808,null=0x5a84a),dict(entry=0x5a898,high=0x5a900,call=0x5a904,A0=0x5a8f8,A1=0x5a8b2,A2=0x5a8bc,source_offset=104,destination_offset=14,length=12,guard=0x5a8a0,null=0x5a924)]
 operands({0x5a710:'lw s1, 272(a0)',0x5a726:'mv s0, a0',0x5a728:'addi a1, a0, 296',0x5a738:'addi a0, s1, 3',0x5a73c:'li a2, 5',0x5a7ce:'mv s0, a0',0x5a7d0:'lw a0, 272(a0)',0x5a7d4:'addi a1, s0, 248',0x5a7d8:'li a2, 8',0x5a7da:'addi a0, a0, 3',0x5a816:'mv s0, a0',0x5a818:'lw a0, 272(a0)',0x5a81c:'addi a1, s0, 248',0x5a820:'li a2, 8',0x5a822:'addi a0, a0, 3',0x5a8b0:'mv s0, a0',0x5a8b2:'addi a1, a0, 104',0x5a8bc:'li a2, 12',0x5a8f8:'addi a0, a5, 14'})
 for row in calls:
  a=row['entry'];pc=row['call'];g=graphs[a];need(e['reference_roles'][str(row['high'])]==dict(reference_kind='code-call',target=0x20000332),'Actual far call targets provided original copy body')
  for reg,key in [('a0','A0'),('a1','A1'),('a2','A2')]:definitions(a,reg,pc,[row[key]])
  need(pc not in V['reachable'](g,a,skip=row['guard'])and set(g[row['guard']])=={row['guard']+2,row['null']},'Null guard dominates every whole-copy call')
  operands({row['null']:'li a0, 1'})
 for a,p in [(0x5a70c,0x5a726),(0x5a7ba,0x5a7ce),(0x5a804,0x5a816),(0x5a898,0x5a8b0)]:definitions(a,'a0',p,[-1])
 definitions(0x5a70c,'s1',0x5a742,[0x5a710]);definitions(0x5a898,'a5',0x5a8f8,[0x5a89c])
 operands({0x5a7bc:'qk.c.sb a5, 21(a0)',0x5a7be:'lw a5, 272(a0)',0x5a7c2:'beqz a5, 0x5a800',0x5a804:'lw a5, 272(a0)',0x5a808:'beqz a5, 0x5a84a',0x5a810:'li a4, 9',0x5a812:'qk.c.sb a4, 21(a0)',0x5a814:'qk.c.sb a4, 2(a5)',0x5a82c:'lw a5, 160(s0)',0x5a830:'sb zero, 43(s0)',0x5a836:'ori a5, a5, 32',0x5a83a:'sw a5, 160(s0)',0x5a83e:'li a5, 1',0x5a840:'qk.c.sb a5, 16(s0)',0x5a7e4:'lbu a5, 42(s0)',0x5a7ea:'ori a5, a5, 4',0x5a7ee:'sb a5, 42(s0)',0x5a7f2:'li a5, 48',0x5a7f6:'qk.c.sb a5, 16(s0)'})
 need(not any('21(a0)'in o['opcode']for p,o in opmaps[0x5a804].items()if p<0x5a808),'Opcode9 length update occurs only after null guard')
 need(len(e['real_prior_providers'])==1 and e['real_prior_providers']==[0x20000332]and len(e['reference_roles'])==4 and not e['opaque_transfers'],'Only one genuine provided copy import and four real calls')
 return dict(passed=True,whole_CFGs=cfgs,reaching_definition_assertions=rd,whole_helper_bounds=bounds,whole_CODE_bytes=890,whole_instructions=321,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=10,new_normal_imports=1,new_normal_imports_resolved=1,remaining_normal_named_UND=20,new_indirect_sites=[],copy_target=0x20000332,whole_copy_calls=calls,all_copy_calls_null_guarded=True,copy_source_and_destination_original_argument_provenance=True,copy_overlap_or_live_buffer_lifetime_proved=False,guarded_length_before_null_entries=[0x5a120,0x5a70c,0x5a7ba,0x5a898],guarded_length_after_null_entries=[0x5a804],no_null_guard_builders=[0x5a568,0x5a588,0x5a614,0x5a686,0x5a6e0],opcode0_halfword_source_offsets=[86,88,90,92,94],opcode0_frame_byte_extent=[2,14],opcode0_original_conditional_counter_update_offset=94,opcode0_counter_store_uint16_preserved=True,opcode0_global_halfword_count_address=0x2000346c,opcode0_three_halfword_match_boolean_offset=98,opcode29_global_byte_address=0x200033bb,opcode40_global_byte_address=0x2000340a,opcode35_branch_global_byte_address=0x2000351f,opcode35_RV32_shift_mask_and_byte_store_preserved=True,opcode36_signed_byte_loads_and_conditional_flag0x10000_preserved=True,opcode8_flags42_OR4_state16_48=True,opcode9_zero43_flags160_OR32_state16_1=True,wire_opcode_semantic_names_proved=False,live_global_values_observed=False,physical_radio_delivery_or_ACK_proved=False,readonly_RAM_MMIO_dependencies_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Actual installed archived ROM/Xwchc and original ABI must match','Record/frame/source spans remain valid;five selected builders lack local null guards','Copy inputs must satisfy the actual helper overlap/lifetime contract;no live buffer contents were observed','Retain conditional counter arithmetic,RV32 variable-shift masking,signed byte reads and byte/halfword truncation','Numeric opcodes/record states are not proved wire semantic names or physical ACK/radio delivery','Twenty genuine normal imports,inherited callbacks/RAM/MMIO and4B startup-source remain incomplete'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and native['c']['UND']==['tsl9_candidate_copy_arch_20000332']and native['c']['opaque_call_sites']==0,'Identical ten complete providers with one real copy import and no own indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(50292,412,3706,5,2971,20));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==50292 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  bm=owned['_byte_map'];need(all(p in bm for a,z,_ in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==17461,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-transmit-control-helpers-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=10,new_SDK_CODE_bytes=890,new_SDK_instructions=321,new_SDK_DATA_bytes=0,new_normal_imports_resolved=1,new_prior_normal_imports_resolved=10,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
