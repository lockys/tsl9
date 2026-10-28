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
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();by={};graphs={};opmaps={};cfgs=[];fs={f['start']:f for f in e['selected_functions']}
 bounds=[(0x5a1dc,0x5a206),(0x5a222,0x5a23e),(0x5a23e,0x5a25e),(0x5a25e,0x5a286),(0x5a286,0x5a2a2),(0x5a2a2,0x5a306),(0x5a306,0x5a326),(0x5a326,0x5a348),(0x5a348,0x5a370),(0x5a370,0x5a386),(0x5a386,0x5a406),(0x5a48e,0x5a52a)]
 need([(f['start'],f['end'])for f in e['selected_functions']]==bounds and e['code_bytes']==682 and e['instructions']==257,'Twelve complete original state helpers')
 parentUND=set(parent['SDK_composition']['c']['named_UND']);provided={f['name']for f in fs.values()}
 need(len(parentUND)==42 and len(provided)==12 and provided<=parentUND and set(K['expected_UND'])==parentUND-provided,'Exactly twelve real original bodies for actual parent imports')
 for f in fs.values():
  at=f['start'];payload=b''
  for o in f['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Contiguous complete original instruction widths');payload+=bb;at+=len(bb)
  need(at==f['end']and payload==raw[f['start']-0x40000:f['end']-0x40000],'Every whole original helper byte')
  ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,c=V['whole_cfg'](f,B,ext,0);by.update(ops);opmaps[f['start']]=ops;graphs[f['start']]=g;cfgs.append(c)
  need(not c['calls']and all(x['type']=='ret'for x in c['typed_exits'])and all(not o['opcode'].startswith(('addi sp,','sw ra,','lw ra,'))for o in f['operations']),'Whole leaf helper with zero own frame and only returns')
 def operands(w):need(all(by[p]['opcode']==text for p,text in w.items()),'Exact numeric helper operands and branch targets')
 guarded=[dict(entry=0x5a1dc,length=2,opcode=2,branch=0x5a1e4,null=0x5a202,null_return=7),dict(entry=0x5a222,length=1,opcode=6,branch=0x5a22a,null=0x5a23a,null_return=1),dict(entry=0x5a23e,length=2,opcode=7,branch=0x5a246,null=0x5a25a,null_return=1),dict(entry=0x5a25e,length=1,opcode=10,branch=0x5a266,null=0x5a282,null_return=1),dict(entry=0x5a286,length=1,opcode=11,branch=0x5a28e,null=0x5a29e,null_return=1),dict(entry=0x5a306,length=2,opcode=13,branch=0x5a30e,null=0x5a322,null_return=1),dict(entry=0x5a326,length=3,opcode=17,branch=0x5a32e,null=0x5a344,null_return=1),dict(entry=0x5a348,length=1,opcode=18,branch=0x5a350,null=0x5a36c,null_return=1),dict(entry=0x5a370,length=1,opcode=19,branch=0x5a378,null=0x5a382,null_return=1)]
 for row in guarded:
  a=row['entry'];ops=opmaps[a];g=graphs[a];b=row['branch'];n=row['null'];need(set(g[b])=={b+2,n},'Exact null/non-null edge pair')
  operands({b:'beqz a5, '+hex(n),n:'li a0, '+str(row['null_return']),n+2:'ret'})
  prefix=[o for p,o in ops.items()if p<b];need(any(o['opcode']=='lw a5, 272(a0)'for o in prefix)and any(o['opcode']=='qk.c.sb '+('a4'if a==0x5a1dc else'a5')+', 21(a0)'for o in prefix),'Frame pointer load and prepared length store precede null guard')
  need(any(o['opcode']=='li '+('a4'if a!=0x5a1dc else'a4')+', '+str(row['opcode'])for p,o in ops.items()if p!=n)and any(o['opcode']=='qk.c.sb a4, 2(a5)'for o in ops.values()),'Exact wire opcode write on normal path')
  need(all(p in V['reachable'](g,b+2)for p,o in ops.items()if o['opcode']=='qk.c.sb a4, 2(a5)'),'Wire opcode write reachable on nonnull arm')
 operands({0x5a1e0:'li a4, 2',0x5a224:'qk.c.sb a5, 21(a0)',0x5a23e:'li a5, 2',0x5a25e:'li a5, 1',0x5a286:'li a5, 1',0x5a306:'li a5, 2',0x5a326:'li a5, 3',0x5a348:'li a5, 1',0x5a370:'li a5, 1'})
 operands({0x5a2a2:'lw a4, 272(a0)',0x5a2a6:'li a5, 6',0x5a2a8:'qk.c.sb a5, 21(a0)',0x5a2aa:'li a5, 12',0x5a2ac:'qk.c.sb a5, 2(a4)',0x5a2ae:'lui a5, 0x20003',0x5a2b2:'addi a5, a5, 952',0x5a2b6:'qk.c.lhu a3, 20(a5)',0x5a2b8:'qk.c.sb a3, 3(a4)',0x5a2ba:'qk.c.lbu a3, 22(a5)',0x5a2bc:'qk.c.sb a3, 4(a4)',0x5a2be:'qk.c.lhu a3, 22(a5)',0x5a2c0:'srli a3, a3, 0x8',0x5a2c2:'qk.c.sb a3, 5(a4)',0x5a2c4:'qk.c.lbu a3, 24(a5)',0x5a2c6:'qk.c.sb a3, 6(a4)',0x5a2c8:'qk.c.lbu a5, 25(a5)',0x5a2ca:'qk.c.sb a5, 7(a4)',0x5a2cc:'lbu a5, 46(a0)',0x5a2d0:'andi a4, a5, 64',0x5a2d4:'beqz a4, 0x5a2ec',0x5a2d6:'li a5, 58',0x5a2da:'qk.c.sb a5, 16(a0)',0x5a2dc:'lbu a5, 46(a0)',0x5a2e0:'andi a5, a5, 127',0x5a2e4:'sb a5, 46(a0)',0x5a2ec:'andi a5, a5, 1',0x5a2ee:'beqz a5, 0x5a2dc',0x5a2f0:'lw a5, 160(a0)',0x5a2f4:'sb zero, 43(a0)',0x5a2f8:'sb zero, 46(a0)',0x5a2fc:'ori a5, a5, 64',0x5a300:'sw a5, 160(a0)',0x5a304:'j 0x5a2dc'})
 operands({0x5a386:'lw a4, 272(a0)',0x5a38a:'li a5, 3',0x5a38c:'qk.c.sb a5, 21(a0)',0x5a38e:'li a5, 22',0x5a390:'qk.c.sb a5, 2(a4)',0x5a392:'lbu a3, 324(a0)',0x5a396:'qk.c.sb a3, 3(a4)',0x5a398:'lbu a5, 325(a0)',0x5a39c:'andi a3, a3, 4',0x5a39e:'qk.c.sb a5, 4(a4)',0x5a3a0:'lhu a4, 486(a0)',0x5a3a4:'beqz a3, 0x5a3ee',0x5a3a6:'li a3, 847',0x5a3aa:'li a5, 0',0x5a3ac:'bleu a4, a3, 0x5a3c6',0x5a3b0:'addi a5, a4, -376',0x5a3b4:'lhu a4, 328(a0)',0x5a3b8:'beqz a4, 0x5a3ea',0x5a3ba:'srai a5, a5, 0x1',0x5a3bc:'addi a5, a5, -43',0x5a3c0:'srai a5, a5, 0x3',0x5a3c2:'slli a5, a5, 0x10',0x5a3c4:'srli a5, a5, 0x10',0x5a3c6:'lhu a4, 484(a0)',0x5a3ca:'bleu a4, a5, 0x5a3d0',0x5a3ce:'mv a4, a5',0x5a3d4:'sb a4, 78(a0)',0x5a3ea:'srai a5, a5, 0x3',0x5a3ec:'j 0x5a3bc',0x5a3ee:'andi a5, a5, 1',0x5a3f0:'beqz a5, 0x5a3fe',0x5a3f2:'addi a5, a4, -80',0x5a3f6:'li a4, 8',0x5a3f8:'div a5, a5, a4',0x5a3fc:'j 0x5a3c2',0x5a3fe:'addi a5, a4, -68',0x5a402:'li a4, 4',0x5a404:'j 0x5a3f8'})
 operands({0x5a48e:'li a5, 5',0x5a490:'qk.c.sb a5, 21(a0)',0x5a492:'lhu a5, 64(a0)',0x5a496:'lw a4, 272(a0)',0x5a49a:'li a3, 24',0x5a49c:'addi a5, a5, 8',0x5a49e:'slli a5, a5, 0x10',0x5a4a0:'srli a5, a5, 0x10',0x5a4a2:'sh a5, 332(a0)',0x5a4a6:'qk.c.sb a3, 2(a4)',0x5a4a8:'lbu a3, 330(a0)',0x5a4ac:'qk.c.sb a3, 3(a4)',0x5a4ae:'lbu a2, 331(a0)',0x5a4b2:'sb zero, 5(a4)',0x5a4b6:'sb zero, 6(a4)',0x5a4ba:'qk.c.sb a2, 4(a4)',0x5a4bc:'lw a1, 328(a0)',0x5a4c0:'lui a2, 0xffff0',0x5a4c2:'and a2, a2, a1',0x5a4c4:'beqz a2, 0x5a4cc',0x5a4c6:'qk.c.sb a5, 5(a4)',0x5a4c8:'srli a5, a5, 0x8',0x5a4ca:'qk.c.sb a5, 6(a4)',0x5a4cc:'andi a5, a3, 4',0x5a4d0:'lhu a4, 486(a0)',0x5a4d4:'beqz a5, 0x5a512',0x5a4d6:'li a3, 847',0x5a4da:'li a5, 0',0x5a4dc:'bleu a4, a3, 0x5a4f6',0x5a4e0:'addi a5, a4, -376',0x5a4e4:'lhu a4, 328(a0)',0x5a4e8:'beqz a4, 0x5a50e',0x5a4ea:'srai a5, a5, 0x1',0x5a4ec:'addi a5, a5, -43',0x5a4f0:'srai a5, a5, 0x3',0x5a4f2:'slli a5, a5, 0x10',0x5a4f4:'srli a5, a5, 0x10',0x5a4f6:'lhu a4, 484(a0)',0x5a4fa:'bleu a4, a5, 0x5a500',0x5a4fe:'mv a4, a5',0x5a504:'sb a4, 78(a0)',0x5a50e:'srai a5, a5, 0x3',0x5a510:'j 0x5a4ec',0x5a512:'andi a3, a3, 1',0x5a514:'beqz a3, 0x5a522',0x5a516:'addi a5, a4, -80',0x5a51a:'li a4, 8',0x5a51c:'div a5, a5, a4',0x5a520:'j 0x5a4f2',0x5a522:'addi a5, a4, -68',0x5a526:'li a4, 4',0x5a528:'j 0x5a51c'})
 for a,store in [(0x5a386,0x5a3d4),(0x5a48e,0x5a504)]:
  defs=reaching(fs[a],opmaps[a],graphs[a],'a0');need(defs[store]=={-1},'Original record remains store destination on every reaching path')
  need(all(not(o['opcode'].startswith(('beqz a4,','beqz a5,'))and p<next(q for q,x in opmaps[a].items()if x['opcode'].startswith('qk.c.sb')and ', 2(a4)'in x['opcode']))for p,o in opmaps[a].items()),'No invented null-buffer guard before original header write')
 need(parent['contract']['prepared_state_byte_offset']==27 and parent['contract']['frame_buffer_record_offset']==272,'Prior caller uses same original frame pointer')
 return dict(passed=True,whole_CFGs=cfgs,whole_helper_bounds=bounds,whole_CODE_bytes=682,whole_instructions=257,all_twelve_are_leaf_with_zero_own_frame=True,resolved_actual_parent_UND=sorted(provided),resolved_prior_normal_imports=12,new_normal_imports=0,remaining_normal_named_UND=30,new_indirect_sites=[],guarded_builders=guarded,guarded_length_field_updated_before_null_return=True,no_null_guard_builders=[0x5a2a2,0x5a386,0x5a48e],opcode12_global_source_base=0x200033b8,opcode12_global_source_offsets=[20,22,24,25],opcode12_live_global_values_not_observed=True,fragment_limit_writers=[0x5a3d4,0x5a504],fragment_limit_record_offset=78,fragment_limit_ceiling_halfword_record_offset=484,fragment_limit_input_halfword_record_offset=486,fragment_limit_mode_halfword_record_offset=328,fragment_limit_signed_division_and_arithmetic_shifts_preserved=True,fragment_limit_uint16_truncation_then_unsigned_min_then_uint8_store_preserved=True,live_fragment_limit_bound_by_frame_allocation_proved=False,opcode24_counter_plus8_uint16_field=332,opcode24_header_optional_counter_guard_uses_upper_halfword_of_word328=True,wire_opcode_semantic_names_proved=False,readonly_RAM_MMIO_dependencies_closed=False,all_inherited_indirect_runtime_targets_closed=False,conditions=['Archived installed ROM/Xwchc and original argument ABI must match','Record and frame buffer spans must remain valid;three selected helpers have no null guard','Concurrent record/IRQ/DMA mutation and live input ranges are unproved','Signed arithmetic and two truncations must be retained;no clamp to allocation size is invented','Live global values,wire semantic names,physical event binding and allocator lifetime remain unproved','Thirty genuine normal imports plus inherited indirect/RAM/MMIO and4B startup-source gaps remain'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and not native['c']['UND']and native['c']['opaque_call_sites']==0,'Identical twelve whole leaf providers without new ordinary imports or indirect sites')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(49402,412,3657,5,2942,30));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==49402 and owned['duplicate_original_CODE_bytes']==0 and owned['named_UND']==K['expected_UND'],'Unique actual SDK CODE and every genuine unprovided normal callee retained')
  bm=owned['_byte_map'];need(all(p in bm for a,z in c['whole_helper_bounds']for p in range(a,z)),'Every complete original helper genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==17140,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-transmit-state-helpers-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=12,new_SDK_CODE_bytes=682,new_SDK_instructions=257,new_SDK_DATA_bytes=0,new_normal_imports_resolved=0,new_prior_normal_imports_resolved=12,prior_genuine_import_body_resolved=K['resolved_prior_UND'],new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
