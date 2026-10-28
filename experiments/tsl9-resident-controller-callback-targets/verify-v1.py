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
 pure=set('beq beqz bgez ble bltz bleu blt bltu bne bnez fence.i j jr ret nop'.split());stores=set('sb sh sw qk.c.sb qk.c.sh qk.c.shsp'.split())
 results=set('add addi and andi auipc c.srli lbu lhu li lui lw xor xori mul mulhu mulhsu div divu remu sltu sra lb lh mv not or ori sll slli srai srl srli sub qk.c.lbu qk.c.lhu'.split())
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
 bounds=[(0x55c32,0x55c48,0),(0x56cb2,0x56cdc,16),(0x561b8,0x5627a,16)]
 need([(f['start'],f['end'],f['own_frame_bytes'])for f in fs.values()]==bounds and e['code_bytes']==258 and e['instructions']==86,'Two whole callback targets and one whole ordinary dependency')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in fs.values()}&parentUND
 need(len(parentUND)==19 and provided=={'tsl9_candidate_unprovided_flash_561b8'}and set(K['expected_UND'])==parentUND-provided and not e['new_genuine_code_dependencies'],'Exactly one old ordinary dependency resolved without inventing imports for numeric pointers')
 def inspect_body(f,frame,is_new):
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every whole original callback/reference byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,frame);by.update(ops);graphs[f['start']]=g;opmaps[f['start']]=ops
  if is_new:cfgs.append(c)
  return c
 for f in fs.values():inspect_body(f,f['own_frame_bytes'],True)
 refs=[]
 for key,selected in [('state_evidence',[(0x55c6e,0x55cc4,32),(0x55cc4,0x55d00,32),(0x56574,0x56716,16)]),('registry_evidence',[(0x43874,0x43932,48)]),('dispatch_evidence',[(0x432a4,0x43326,48),(0x43326,0x433a8,16)])]:
  re=read(R/K[key]);rf={f['start']:f for f in re['selected_functions']}
  for a,z,frame in selected:
   need(rf[a]['end']==z,'Independent whole reference bound');refs.append(inspect_body(rf[a],frame,False))
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact original callback/registry/dispatch operands')
 def definitions(start,reg,p,w):
  f=fs.get(start)or dict(start=start);need(reaching(f,opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG exact callback argument provenance');rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 operands({0x55c32:'beqz a0, 0x55c46',0x55c34:'lw a5, 160(a0)',0x55c38:'ori a5, a5, 128',0x55c3c:'sw a5, 160(a0)',0x55c40:'li a5, -1',0x55c42:'sb a5, 38(a0)',0x55c46:'ret',0x56cb2:'beqz a0, 0x56cda',0x56cb4:'addi sp, sp, -16',0x56cb6:'li a1, 34',0x56cbe:'mv s0, a0',0x56cc0:'jal ra, 0x568f6',0x56cc4:'li a5, -1',0x56cc6:'sb a0, 43(s0)',0x56cca:'sb zero, 16(s0)',0x56cce:'sb a5, 39(s0)',0x56cd6:'addi sp, sp, 16',0x56cd8:'ret',0x56cda:'ret'})
 definitions(0x56cb2,'a0',0x56cc0,[-1]);definitions(0x56cb2,'a1',0x56cc0,[0x56cb6]);definitions(0x56cb2,'a0',0x56cc6,[0x56cc0])
 operands({0x55cb6:'lui a0, 0x56',0x55cba:'addi a0, a0, -974',0x55caa:'mv a1, s0',0x55c9a:'addi a3, s0, 38',0x55cc0:'j 0x43874',0x55cf2:'lui a0, 0x57',0x55cf6:'addi a0, a0, -846',0x55cec:'mv a1, s0',0x55ce8:'addi a3, s0, 39',0x55cfc:'j 0x43874'})
 need(((0x56<<12)-974,(0x57<<12)-846)==(0x55c32,0x56cb2),'Original numeric arguments equal whole positive callback CODE entries')
 operands({0x43892:'lw s3, 524(a5)',0x43896:'sw zero, 524(a5)',0x4389a:'fence.i',0x4389e:'beqz a0, 0x438fe',0x438a0:'li s0, 16',0x438a2:'mv s2, a3',0x438a4:'mv s5, a2',0x438a6:'mv s4, a1',0x438a8:'mv s1, a0',0x438aa:'li s9, 12',0x438ac:'lui s6, 0x20003',0x438b0:'li s10, 1',0x438b2:'li s8, 48',0x438b6:'mul s7, s0, s9',0x438ba:'lw a4, 556(s6)',0x438be:'add a4, a4, s7',0x438c0:'lw a5, 0(a4)',0x438c2:'bnez a5, 0x43920',0x438c4:'andi a1, s0, 15',0x438c8:'sll a1, s10, a1',0x438cc:'srai a0, s0, 0x4',0x438d0:'slli a1, a1, 0x10',0x438d2:'mv a2, s5',0x438d4:'srli a1, a1, 0x10',0x438d6:'andi a0, a0, 255',0x438da:'jal 0x43728',0x438dc:'beqz a0, 0x43920',0x438de:'lw a5, 556(s6)',0x438e2:'add a5, a5, s7',0x438e4:'sw s1, 0(a5)',0x438e6:'sw s4, 4(a5)',0x438ea:'beqz s2, 0x438f2',0x438ee:'sb s0, 0(s2)',0x438fa:'li a0, 0',0x43902:'li a0, 2',0x43920:'addi s0, s0, 1',0x43922:'bne s0, s8, 0x438b6',0x4392e:'li a0, 8'})
 definitions(0x43874,'s1',0x438e4,[0x438a8]);definitions(0x43874,'s4',0x438e6,[0x438a6]);definitions(0x43874,'s2',0x438ee,[0x438a2])
 operands({0x432be:'slli a0, a0, 0x4',0x432c0:'li a4, 12',0x432c2:'add a0, a0, s0',0x432c4:'mul a0, a0, a4',0x432c8:'lui a5, 0x20003',0x432cc:'lw s2, 556(a5)',0x432dc:'add s2, s2, a0',0x432de:'lw a4, 0(s2)',0x432e2:'beqz a4, 0x432ee',0x432e4:'lw a0, 4(s2)',0x432ea:'jalr a4',0x4335c:'mv a5, a0',0x4336a:'slli a5, a5, 0x4',0x4336c:'add a5, a5, a4',0x4336e:'li a3, 12',0x43370:'mul a5, a5, a3',0x43374:'lui a3, 0x20003',0x43378:'lw s2, 556(a3)',0x43386:'add s2, s2, a5',0x43388:'lw a5, 0(s2)',0x4338c:'lw a0, 4(s2)',0x43390:'jalr a5',0x43392:'sw zero, 0(s2)',0x43396:'sw zero, 4(s2)'})
 definitions(0x432a4,'a0',0x432ea,[0x432e4]);definitions(0x432a4,'a4',0x432ea,[0x432de]);definitions(0x43326,'a0',0x43390,[0x4338c]);definitions(0x43326,'a5',0x43390,[0x43388])
 operands({0x561be:'mv s0, a0',0x561c0:'li a1, 4',0x561c2:'li a0, 0',0x561ce:'jal ra, 0x43e6a',0x561d2:'lhu a4, 180(s1)',0x561d6:'sh a0, 86(s0)',0x561dc:'bleu a4, a5, 0x56236',0x561e0:'lhu a0, 486(s0)',0x561e4:'lhu a5, 482(s0)',0x561f2:'lhu a0, 572(a4)',0x561f6:'addi a5, a5, 625',0x561fe:'mulhsu a1, a5, a0',0x56208:'jal ra, 0x6df1a',0x56218:'lw a7, 156(s1)',0x56226:'li a2, 1',0x56228:'addi t1, a1, -1',0x5622c:'li t3, 40',0x56232:'bltu a2, t1, 0x56240',0x56240:'mul a6, a2, t3',0x5624c:'sh a2, 86(s0)',0x5625a:'lw t4, 140(a5)',0x5625e:'bne t4, a1, 0x5626e',0x5626a:'remu a3, a3, a1',0x56276:'addi a2, a2, 2',0x56278:'j 0x56232',0x565d2:'mv a0, s0',0x565ec:'jal ra, 0x561b8'})
 definitions(0x56574,'a0',0x565ec,[0x565d2])
 need(not e['opaque_transfers']and len(e['real_prior_providers'])==3,'Only three real ordinary providers and no new own indirect calls')
 return dict(passed=True,whole_CFGs=cfgs,reference_CFGs=refs,reaching_definition_assertions=rd,whole_helper_bounds=bounds,whole_CODE_bytes=258,whole_instructions=86,reference_CODE_bytes=sum(x['bytes']for x in refs),reference_instructions=sum(x['instructions']for x in refs),reference_new_CODE_bytes=0,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=1,new_normal_imports=3,new_normal_imports_resolved=3,new_genuine_missing_normal_imports=[],remaining_normal_named_UND=18,new_indirect_sites=[],new_literal_target_bodies=[0x55c32,0x56cb2],numeric_pointer_original_CODE_body_identity_proved=True,native_literal_relocations_added=False,original_runtime_address_binding_proved=False,conditional_registry_dispatch_record_provenance_proved=True,registry_table_pointer_global=0x2000322c,registry_entry_stride=12,registry_slot_range=[16,48],registry_callback_word_offset=0,registry_argument_word_offset=4,registry_slot_pointer_A3_optional=True,registry_null_callback_return=2,registry_exhausted_return=8,registry_success_return=0,registry_success_requires43728_nonzero=True,registry_scheduler_task_and_mask='task=slot>>4;mask=uint16(1<<(slot&15))',dispatch_entry_index_formula='12*((task<<4)+event_bit_index)',dispatch_record_passed_in_A0=True,dispatch_first_indirect_site=0x432ea,dispatch_second_indirect_site=0x43390,dispatch_first_pointer_has_null_guard=True,dispatch_second_pointer_has_no_local_null_guard=True,live_table_identity_or_immutability_proved=False,callback55c32_null_record_is_noop=True,callback55c32_record160_OR0x80_and_slot38_ff=True,callback56cb2_null_record_returns_before_frame=True,callback56cb2_calls568f6_with_original_record_and34=True,callback56cb2_return_low_byte_to43_zero16_slot39_ff=True,helper561b8_original_caller_PC=0x565ec,helper561b8_initial_field86_from43e6a_0_4=True,helper561b8_original_odd_candidate_step2_and_RV32_math_preserved=True,record86_product_meaning_or_live_domain_proved=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Actual installed archived ROM/Xwchc and original ABI must match','Registration success,matching event/task,unchanged valid table/record and callback lifetime are required for the conditional dispatch chain','Two numeric pointer target CODE bodies are now owned,but existing literal instructions still have no new relocation or final original-address binding','Dispatch43390 has no local pointer-null guard;do not invent safety or reentrant stability','Preserve original helper561B8 high multiply,remainder,truncation and candidate/list domains without invented product semantics','Eighteen ordinary imports,inherited dynamic/RAM/MMIO,original4B startup and physical ROM/RAM/IRQ/Flash/OTA remain incomplete'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==3 and native['c']['opaque_call_sites']==0,'Identical two callback target bodies and one ordinary provider with three real imports')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(54780,412,4091,5,3253,18));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==54780 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  need(any(json.loads(t)==[['CODE',0x565ec],17,0,['CODE',0x561b8]]for t in owned['_typed_relations'])and 0x561b8 in owned['_byte_map'],'Original561B8 call role now has an actual positive original provider')
  need(all(p in owned['_byte_map']for p in [0x55c32,0x56cb2]),'Both original numeric pointer CODE bodies are now genuinely owned')
  bm=owned['_byte_map'];need(all(p in bm for a,z,_ in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==18917,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-controller-callback-targets-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=3,new_SDK_CODE_bytes=258,new_SDK_instructions=86,new_SDK_DATA_bytes=0,new_normal_imports_resolved=3,new_prior_normal_imports_resolved=1,new_literal_target_bodies=2,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
