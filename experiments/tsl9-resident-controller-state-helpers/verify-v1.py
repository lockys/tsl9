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
 bounds=[(0x55c6e,0x55cc4,32),(0x55cc4,0x55d00,32),(0x5649c,0x56574,16),(0x56574,0x56716,16)]
 need([(f['start'],f['end'],f['own_frame_bytes'])for f in fs.values()]==bounds and e['code_bytes']==780 and e['instructions']==273,'Four complete original controller-state bodies')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in fs.values()};new=set(e['new_genuine_code_dependencies'])
 need(len(parentUND)==22 and len(provided)==4 and provided<=parentUND and new=={'tsl9_candidate_unprovided_flash_561b8'}and set(K['expected_UND'])==(parentUND-provided)|new,'Four actual providers plus genuine new561B8 callee')
 for f in fs.values():
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Whole contiguous original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every whole original controller-state byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);by.update(ops);opmaps[f['start']]=ops;graphs[f['start']]=g;cfgs.append(c)
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact original slot/state/selection operands')
 def definitions(start,reg,p,w):
  need(reaching(fs[start],opmaps[start],graphs[start],reg)[p]==set(w),'Whole-CFG original register provenance');rd.append(dict(function=start,register=reg,PC=p,definitions=sorted(w)))
 ce=read(R/K['caller_evidence']);caller=next(f for f in ce['selected_functions']if f['start']==0x56d0e);co={o['addr']:o for o in caller['operations']};_,cg,_=V['whole_cfg'](caller,B,{d[1]for o in caller['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))},48)
 calls=[dict(PC=0x56e4c,target=0x55c6e,A0=0x56e44),dict(PC=0x57414,target=0x55cc4,A0=0x57412),dict(PC=0x57480,target=0x55cc4,A0=0x57476),dict(PC=0x574e0,target=0x56574,A0=0x574da),dict(PC=0x57748,target=0x5649c,A0=0x574da)]
 for row in calls:need(B['decode_control'](bytes.fromhex(co[row['PC']]['bytes']),row['PC'])[1]==row['target']and co[row['A0']]['opcode']=='mv a0, s0'and reaching(caller,co,cg,'a0')[row['PC']]=={row['A0']},'Every original controller call receives its original record')
 operands({0x55c74:'mv s0, a0',0x55c76:'lbu a0, 38(a0)',0x55c7a:'li a5, 255',0x55c7e:'mv a2, a1',0x55c80:'beq a0, a5, 0x55c92',0x55c84:'sw a1, 12(sp)',0x55c86:'jal ra, 0x43a14',0x55c8a:'lw a2, 12(sp)',0x55c8c:'li a5, -1',0x55c8e:'sb a5, 38(s0)',0x55c92:'lbu a5, 42(s0)',0x55c96:'lhu a4, 72(s0)',0x55c9a:'addi a3, s0, 38',0x55c9e:'ori a5, a5, 96',0x55ca2:'sb a5, 42(s0)',0x55ca6:'lhu a5, 64(s0)',0x55caa:'mv a1, s0',0x55cae:'add a5, a5, a4',0x55cb0:'sh a5, 70(s0)',0x55cb6:'lui a0, 0x56',0x55cba:'addi a0, a0, -974',0x55cbe:'addi sp, sp, 32',0x55cc0:'j 0x43874'})
 operands({0x55cca:'mv s0, a0',0x55ccc:'lbu a0, 39(a0)',0x55cd0:'li a5, 255',0x55cd4:'mv a2, a1',0x55cd6:'beq a0, a5, 0x55ce8',0x55cda:'sw a1, 12(sp)',0x55cdc:'jal ra, 0x43a14',0x55ce0:'lw a2, 12(sp)',0x55ce2:'li a5, -1',0x55ce4:'sb a5, 39(s0)',0x55ce8:'addi a3, s0, 39',0x55cec:'mv a1, s0',0x55cf2:'lui a0, 0x57',0x55cf6:'addi a0, a0, -846',0x55cfa:'addi sp, sp, 32',0x55cfc:'j 0x43874'})
 for a,pc,defs in [(0x55c6e,0x55cc0,{'a0':[0x55cba],'a1':[0x55caa],'a2':[0x55c7e,0x55c8a],'a3':[0x55c9a]}),(0x55cc4,0x55cfc,{'a0':[0x55cf6],'a1':[0x55cec],'a2':[0x55cd4,0x55ce0],'a3':[0x55ce8]})]:
  for reg,w in defs.items():definitions(a,reg,pc,w)
  need(any(x['PC']==pc and x['type']=='direct-tail'and x['target']==0x43874 for x in next(c for c in cfgs if c['start']==a)['typed_exits']),'Own32 frame released before original registration-like tail')
 literals=e['raw_pointer_literal_dependencies'];need([(x['PC'],x['low_PC'],x['value'])for x in literals]==[(0x55cb6,0x55cba,0x55c32),(0x55cf2,0x55cf6,0x56cb2)]and all(not x['body_provided']and not x['typed_relocation']and not x['physical_binding_proved']for x in literals),'Both numeric pointer gaps retained without invented CODE providers')
 operands({0x5649c:'lui a5, 0x20003',0x564a0:'addi a5, a5, 952',0x564a4:'lhu a3, 180(a5)',0x564aa:'bleu a3, a4, 0x5656e',0x564ae:'addi sp, sp, -16',0x564b2:'lw s0, 156(a5)',0x564ba:'mv a5, s0',0x564bc:'bnez a5, 0x564ce',0x564c0:'sb zero, 28(a0)',0x564ce:'qk.c.lbu a4, 29(a5)',0x564d0:'bnez a4, 0x564c4',0x564d2:'lw a5, 0(a5)',0x564d4:'j 0x564bc',0x564d6:'bne s0, a0, 0x564de',0x564da:'lw s0, 0(s0)',0x564de:'qk.c.lbu a5, 11(s0)',0x564e0:'bnez a5, 0x5656a',0x564e2:'lw a4, 140(s0)',0x564e6:'lw a5, 140(a0)',0x564ea:'beq a4, a5, 0x5656a',0x564ee:'qk.c.lbu a4, 28(a0)',0x564f0:'li a5, 128',0x564f6:'bne a4, a5, 0x56542',0x5651e:'qk.c.sb a5, 29(s1)',0x56522:'andi a5, a5, 127',0x56526:'qk.c.sb a5, 28(s1)',0x56528:'addi a0, s0, 104',0x56532:'li a2, 12',0x56534:'li a1, 255',0x56538:'addi sp, sp, 16',0x5653a:'auipc t1, 0x1ffaa',0x5653e:'jr -414(t1)',0x56564:'li a5, 2',0x56566:'qk.c.sb a5, 29(s0)',0x5656e:'sb zero, 28(a0)',0x56572:'ret'})
 need(e['reference_roles'][str(0x5653a)]==dict(reference_kind='code-tail',target=0x2000039c),'Actual original far tail uses the provided fill helper')
 operands({0x56574:'lui a5, 0x20003',0x56578:'addi a5, a5, 952',0x5657c:'lhu a3, 180(a5)',0x5658a:'mv s1, a0',0x5658c:'bleu a3, a4, 0x56710',0x56590:'lw a4, 264(a0)',0x56594:'andi a4, a4, 2',0x56596:'beqz a4, 0x56710',0x5659a:'lw a5, 156(a5)',0x565a0:'bnez a1, 0x5660e',0x565a2:'lhu a2, 484(s1)',0x565aa:'addi a2, a2, 34',0x565ae:'srai a2, a2, 0x1',0x565b0:'addi a2, a2, 11',0x565dc:'sh a5, 94(s0)',0x565e0:'qk.c.lhu a5, 60(s0)',0x565e2:'sh a5, 90(s0)',0x565e6:'qk.c.lhu a5, 62(s0)',0x565e8:'sh a5, 92(s0)',0x565ec:'jal ra, 0x561b8',0x565f0:'lw a5, 164(s0)',0x565f4:'ori a5, a5, 1',0x565f8:'sw a5, 164(s0)',0x565fc:'li a5, 1',0x565fe:'qk.c.sb a5, 20(s0)',0x56600:'li a5, 3',0x56602:'qk.c.sb a5, 29(s0)',0x5660e:'qk.c.lbu a4, 29(a1)',0x56610:'bnez a4, 0x56604',0x56612:'lw a1, 0(a1)',0x56614:'j 0x565a0',0x566aa:'li a5, 18',0x566ac:'qk.c.sb a5, 29(s0)',0x566b4:'addi sp, sp, 16',0x566b6:'j 0x5e3a8',0x56708:'li a5, 19',0x5670a:'qk.c.sb a5, 29(s1)',0x56710:'sb zero, 28(s1)',0x56714:'j 0x56604'})
 need(not e['opaque_transfers']and len(e['real_prior_providers'])==4,'No own indirect transfer and four actual prior ordinary providers')
 return dict(passed=True,whole_CFGs=cfgs,reaching_definition_assertions=rd,whole_helper_bounds=bounds,whole_CODE_bytes=780,whole_instructions=273,original_controller_calls=calls,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=4,new_normal_imports=5,new_normal_imports_resolved=4,new_genuine_missing_normal_imports=sorted(new),remaining_normal_named_UND=19,new_indirect_sites=[],numeric_pointer_gaps=literals,numeric_pointer_targets=[0x55c32,0x56cb2],numeric_pointer_target_bodies_provided=False,numeric_pointer_CODE_DATA_classification_closed=False,slot_offsets=[38,39],slot_sentinel=255,slot_release_target=0x43a14,registration_like_tail_target=0x43874,registration_tail_arguments=['numeric pointer','original record','incoming A1 preserved across optional release','address ofrecord slot38 or39'],registration_bodies_own32_frame_released_before_tail=True,slot38_flags42_OR0x60_and_halfword70_uint16_of64_plus72=True,global_list_count_address=0x2000346c,global_list_head_address=0x20003454,list_record29_nonzero_blocks_selected_paths=True,input_record28_reset_paths_preserved=True,record29_numeric_written_states=[1,2,3,18,19],peer_fill_offset=104,peer_fill_value=255,peer_fill_length=12,peer_fill_far_tail_target=0x2000039c,peer_fill16_frame_released_before_tail=True,selection_RV32_REMU_and_signed_unsigned_comparisons_preserved=True,selection_new561b8_call_PC=0x565ec,live_list_domain_acyclicity_and_concurrency_proved=False,callback_registration_target_binding_proved=False,record_state_product_meanings_proved=False,live_record_or_callback_values_observed=False,readonly_RAM_MMIO_dependencies_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Installed archived ROM/Xwchc,registration ABI and original record layout must match','Slot cleanup and register-bound parameters preserve original saves,reloads and tails;numeric target bodies55C32/56CB2 are not supplied or typed CODE bindings','List records,next pointers,count and flags remain valid;acyclicity,concurrency and IRQ/DMA/reentrancy are unproved','Retain all273 instructions including RV32 remainder,signed/unsigned comparisons and byte/halfword truncation;no invented C arithmetic or clamp','Nineteen ordinary imports,the new561B8 body,two numeric pointer gaps and inherited indirect/RAM/MMIO remain open','Original4B startup,installed ROM/RAM/IRQ/Flash/OTA compatibility remain incomplete'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==5 and native['c']['opaque_call_sites']==0,'Identical four complete controller-state bodies with five imports and two untyped literal pointers')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(54522,412,4068,5,3238,19));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==54522 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  need(all(any(json.loads(t)==[['CODE',pc],17,0,['CODE',target]]for t in owned['_typed_relations'])and target in owned['_byte_map']for pc,target in [(0x56e4c,0x55c6e),(0x57414,0x55cc4),(0x57480,0x55cc4),(0x574e0,0x56574),(0x57748,0x5649c)]),'Every original controller call role retains its actual positive original provider')
  need(all(p not in owned['_byte_map']for p in [0x55c32,0x56cb2]),'Two numeric pointer target bodies remain unprovided and uncounted')
  bm=owned['_byte_map'];need(all(p in bm for a,z,_ in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==18831,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-controller-state-helpers-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=4,new_SDK_CODE_bytes=780,new_SDK_instructions=273,new_SDK_DATA_bytes=0,new_normal_imports_resolved=4,new_prior_normal_imports_resolved=4,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=1,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
