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
 results=set('add addi and andi auipc c.srli lbu lhu li lui lw mul mulhu div divu remu sltu sra lb lh mv not or ori sll slli srai srl srli sub qk.c.lbu qk.c.lhu'.split())
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
 bounds=[(0x567be,0x568d4,32),(0x56d0e,0x5774e,48),(0x58f14,0x59042,32)]
 need([(f['start'],f['end'],f['own_frame_bytes'])for f in e['selected_functions']]==bounds and e['code_bytes']==3204 and e['instructions']==1011,'Three complete original controller completion-chain bodies')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in fs.values()};new=set(e['new_genuine_code_dependencies'])
 need(len(parentUND)==15 and len(provided)==3 and provided<=parentUND and len(new)==10 and not new&parentUND and set(K['expected_UND'])==(parentUND-provided)|new,'Actual three old imports resolved and every ten newly exposed callee retained')
 for f in fs.values():
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every original whole controller byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);graphs[f['start']]=g;opmaps[f['start']]=ops;cfgs.append(c)
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact original numeric tail/state/callback operands')
 def definitions(start,reg,p,w):
  need(reaching(fs[start],opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG callback/record argument provenance');rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 ref=read(R/K['caller_evidence']);caller=next(f for f in ref['selected_functions']if f['start']==0x595b8);callops={o['addr']:o for o in caller['operations']};calls=[dict(PC=0x59bc0,target=0x56d0e,kind='call',argument_move=0x59bbe),dict(PC=0x59bfa,target=0x58f14,kind='call',argument_move=0x59bf8),dict(PC=0x59c14,target=0x567be,kind='tail',argument_move=0x59bfe),dict(PC=0x59c3c,target=0x56d0e,kind='call',argument_move=0x59c3a)]
 _,cg,cc=V['whole_cfg'](caller,B,{d[1]for o in caller['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))},48)
 for row in calls:
  p=row['PC'];need(B['decode_control'](bytes.fromhex(callops[p]['bytes']),p)[1]==row['target']and callops[row['argument_move']]['opcode']=='mv a0, s0','Actual original completion caller target and record argument move')
  need(reaching(caller,callops,cg,'a0')[p]=={row['argument_move']},'Whole completion-caller A0 provenance')
 need(any(x['PC']==0x59c14 and x['type']=='direct-tail'and x['target']==0x567be for x in cc['typed_exits']),'Original completion tail restores its own frame before transfer')
 operands({0x567c6:'addi sp, sp, -32',0x567d6:'mv s2, a0',0x5685a:'li a5, -80',0x5685e:'sb a5, 14(s2)',0x56862:'qk.c.lbu a5, 12(s1)',0x56864:'beqz a5, 0x568b4',0x56866:'li a0, 0',0x56868:'auipc ra, 0x1ffaa',0x5686c:'jalr -222(ra)',0x56870:'lui a5, 0x20003',0x56874:'sw zero, 1116(a5)',0x56878:'lui a5, 0x20003',0x5687c:'lw a0, 1260(a5)',0x56880:'jal ra, 0x43ed2',0x56888:'lui a5, 0xe000e',0x5688c:'lui a4, 0x2000',0x56890:'sw a4, 516(a5)',0x568b4:'lbu a5, 41(s2)',0x568ba:'li a1, 1',0x568c4:'sll a1, a1, a5',0x568c8:'slli a1, a1, 0x10',0x568ca:'srli a1, a1, 0x10',0x568cc:'li a0, 0',0x568ce:'addi sp, sp, 32',0x568d0:'j 0x4354a'})
 need(e['reference_roles'][str(0x56868)]==dict(reference_kind='code-call',target=0x2000078a),'Actual existing callback-set provider target')
 need(any(x['PC']==0x568d0 and x['type']=='direct-tail'and x['target']==0x4354a for x in cfgs[0]['typed_exits']),'Original tail32 frame released before set-event transfer')
 operands({0x56d0e:'lw a5, 160(a0)',0x56d12:'addi sp, sp, -48',0x56d22:'mv s0, a0',0x56d24:'beqz a5, 0x571c4',0x56d28:'andi a4, a5, 2',0x56d2c:'beqz a4, 0x56d40',0x56d2e:'andi a5, a5, -3',0x56d30:'sw a5, 160(a0)',0x56d34:'qk.c.lhu a0, 8(a0)',0x56d36:'li a2, 6',0x56d38:'li a1, 128',0x56d3c:'jal ra, 0x5e3a8'})
 operands({0x574e0:'jal ra, 0x56574',0x574e4:'lhu a5, 64(s0)',0x574e8:'beqz a5, 0x5754c',0x574ea:'li a4, 100',0x574ee:'remu a5, a5, a4',0x574f2:'bnez a5, 0x5754c',0x574f4:'lui a5, 0x20003',0x574f8:'lw a5, 1252(a5)',0x574fc:'lui s1, 0x20003',0x57500:'addi s1, s1, 952',0x57504:'andi a5, a5, 2',0x57506:'beqz a5, 0x57544',0x57508:'lui s2, 0x20003',0x5750c:'addi s2, s2, 492',0x57510:'lw a4, 52(s2)',0x57514:'beqz a4, 0x57544',0x57516:'qk.c.lhu a5, 16(s1)',0x57518:'qk.c.lhu a1, 18(s1)',0x5751a:'li a0, 9',0x5751c:'slli a5, a5, 0x10',0x5751e:'or a1, a1, a5',0x57520:'jalr a4',0x57522:'lw a5, 52(s2)',0x57526:'qk.c.lhu a1, 14(s1)',0x57528:'li a0, 10',0x5752a:'jalr a5',0x5752c:'lw a5, 52(s2)',0x57530:'lh a1, 50(s0)',0x57534:'li a0, 11',0x57536:'jalr a5',0x57538:'lw a5, 52(s2)',0x5753c:'lb a1, 52(s0)',0x57540:'li a0, 12',0x57542:'jalr a5',0x57544:'sh zero, 14(s1)',0x57548:'sw zero, 16(s1)',0x5754c:'lw ra, 44(sp)',0x5755a:'addi sp, sp, 48',0x5755c:'ret'})
 callback_sites=[0x57520,0x5752a,0x57536,0x57542];g=graphs[0x56d0e]
 for p in callback_sites:need(all(p not in V['reachable'](g,0x56d0e,skip=gate)for gate in [0x574e8,0x574f2,0x57506,0x57514]),'All four diagnostic sites require original nonzero/mod100/config/initial-callback gates')
 for pc,reg,definition,code in [(0x57520,'a4',0x57510,9),(0x5752a,'a5',0x57522,10),(0x57536,'a5',0x5752c,11),(0x57542,'a5',0x57538,12)]:
  definitions(0x56d0e,reg,pc,[definition]);definitions(0x56d0e,'a0',pc,[{9:0x5751a,10:0x57528,11:0x57534,12:0x57540}[code]])
 need(0x57544 in V['reachable'](g,0x57544)and 0x57548 in V['reachable'](g,0x57544),'Counter cache reset remains on original no-callback arm')
 text=(R/e['header']).read_text('latin1');need(re.search(r'typedef\s+void\s*\(\*pfnLibStatusErrorCB\)\(\s*uint8_t\s+code,\s*uint32_t\s+status\s*\)',text)and'pfnLibStatusErrorCB staCB;'in text,'Pinned official two-argument status callback declaration')
 operands({0x58f14:'lbu a5, 310(a0)',0x58f18:'srli a3, a5, 0x3',0x58f1c:'add a3, a3, a0',0x58f1e:'lbu a1, 304(a3)',0x58f22:'andi a4, a5, 7',0x58f26:'sra a2, a1, a4',0x58f2a:'andi a2, a2, 1',0x58f2c:'beqz a2, 0x59032',0x58f30:'qk.c.lbu a5, 17(a0)',0x58f32:'andi a5, a5, 2',0x58f34:'bnez a5, 0x59040',0x58f38:'lw a5, 164(a0)',0x58f3c:'andi a5, a5, 2',0x58f3e:'bnez a5, 0x59040',0x58f42:'addi sp, sp, -32',0x58f46:'mv s0, a0',0x58f48:'addi a0, a0, 312',0x58f4e:'jal ra, 0x57ad8',0x58fd6:'addi a0, a0, -5',0x58fd8:'sb a0, 309(s0)',0x58fdc:'li a2, 5',0x58fde:'addi a1, sp, 8',0x58fe0:'addi a0, s0, 296',0x58fe4:'auipc ra, 0x1ffa7',0x58fe8:'jalr 846(ra)',0x58fec:'lw a5, 164(s0)',0x58ff0:'ori a5, a5, 2',0x58ff4:'sw a5, 164(s0)',0x59032:'li a5, 1',0x59034:'sll a5, a5, a4',0x59038:'or a5, a5, a1',0x5903a:'sb a5, 304(a3)',0x5903e:'ret',0x59040:'ret'})
 need(e['reference_roles'][str(0x58fe4)]==dict(reference_kind='code-call',target=0x20000332),'Actual five-byte copy uses the existing real provider')
 definitions(0x58f14,'a0',0x58fe8,[0x58fe0]);definitions(0x58f14,'a1',0x58fe8,[0x58fde]);definitions(0x58f14,'a2',0x58fe8,[0x58fdc])
 sites=sorted(o['PC']for o in e['opaque_transfers']);need(sites==[0x5681e,0x56858,0x57098,0x57520,0x5752a,0x57536,0x57542,0x575f6,0x5766e],'Every nine own indirect sites remains explicit')
 return dict(passed=True,whole_CFGs=cfgs,reaching_definition_assertions=rd,whole_helper_bounds=bounds,whole_CODE_bytes=3204,whole_instructions=1011,original_completion_calls=calls,completion_tail_frames_balanced=True,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=3,new_normal_imports=23,new_normal_imports_resolved=13,new_genuine_missing_normal_imports=sorted(new),remaining_normal_named_UND=22,new_indirect_sites=sites,tail_record14_value=176,tail_numeric_MMIO_write_address=0xe000e204,tail_numeric_MMIO_write_value=0x02000000,physical_interrupt_controller_identity_proved=False,tail_set_event_target=0x4354a,tail_set_event_task_argument=0,tail_set_event_mask='uint16(1 << RV32_low5(record41))',controller_transition_frame_bytes=48,controller_transition_all818_instructions_owned=True,optional_status_callback_global=0x20003220,official_status_callback_config_offset=52,official_status_callback_signature='void(uint8_t code,uint32_t status)',diagnostic_sites=callback_sites,diagnostic_codes=[9,10,11,12],diagnostic_arguments=['(uint16(global200033B8+16)<<16)|uint16(global200033B8+18)','uint16(global200033B8+14)','sign_extend16(record+50)','sign_extend8(record+52)'],diagnostic_nonzero_record64_mod100_gate=True,diagnostic_config_word_global=0x200034e4,diagnostic_config_bit=1,diagnostic_only_initial_pointer_has_null_guard=True,diagnostic_pointer_reloaded_after_each_callback=True,diagnostic_pointer_must_remain_valid_between_reloads=True,diagnostic_cache_reset_after_dispatch_or_null_config_arm=True,diagnostic_cache_reset_addresses=[0x200033c6,0x200033c8],diagnostic_semantic_names_or_physical_values_proved=False,mask_transition_index_record_offset=310,mask_transition_bitmap_record_offset=304,mask_transition_first_clear_bit_path_sets_bit_and_returns_before_frame=True,mask_transition_guard_record17_bit1_or_record164_bit1=True,mask_transition_copy_length=5,mask_transition_copy_destination_record_offset=296,mask_transition_bit_meaning_or_live_input_range_proved=False,live_record_or_callback_values_observed=False,readonly_RAM_MMIO_dependencies_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Installed archived ROM/Xwchc and original record/callback ABI must match','All three complete bodies preserve original reads,branches,calls and frames;many numeric state branches have no proved product-level meaning','Twenty-two ordinary imports and nine own indirect sites remain explicit,without stubs or invented providers','Status code9-12 callback reads are original numeric observations;actual callback pointer lifetime,IRQ/DMA/reentrancy and signed-value meaning remain unproved','Numeric writeE000E204=02000000 is not proved physical interrupt-controller compatibility','Bitmap input index,record spans,five-byte copy lifetime and event-mask binding remain valid;live bounds are unproved','Original startup4B,installed ROM/RAM/IRQ/Flash/OTA and inherited indirect gaps remain'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==23 and native['c']['opaque_call_sites']==9,'Identical three complete chain bodies with all23 imports and nine own indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(53742,412,3997,5,3185,22));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==53742 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  need(all(any(json.loads(t)==[['CODE',pc],kind,0,['CODE',target]]for t in owned['_typed_relations'])and target in owned['_byte_map']for pc,kind,target in [(0x59bc0,17,0x56d0e),(0x59bfa,17,0x58f14),(0x59c14,17,0x567be),(0x59c3c,17,0x56d0e)]),'Every original completion call/tail role retained with actual positive original providers')
  bm=owned['_byte_map'];need(all(p in bm for a,z,_ in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==18558,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-completion-chain-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=3,new_SDK_CODE_bytes=3204,new_SDK_instructions=1011,new_SDK_DATA_bytes=0,new_normal_imports_resolved=13,new_prior_normal_imports_resolved=3,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=10,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
