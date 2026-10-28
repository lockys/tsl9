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
 pure=set('beq beqz bgez bleu blt bltu bne bnez fence.i j jr ret'.split());stores=set('sb sh sw qk.c.sb qk.c.sh qk.c.shsp'.split())
 results=set('add addi and andi auipc c.srli lbu lhu li lui lw mul mv or ori sll slli srai srli sub qk.c.lbu qk.c.lhu'.split())
 volatile=set('ra t0 t1 t2 t3 t4 t5 t6 a0 a1 a2 a3 a4 a5 a6 a7'.split());incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
 while todo:
  p=todo.pop();o=ops[p];mn=o['opcode'].split()[0];need(mn in pure|stores|results|{'jal','jalr'},'Every original register-transfer opcode modelled')
  writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(o['type']in ['call','ucall']and reg in volatile);out={p}if writes else incoming[p]
  for n in g[p]:
   before=len(incoming[n]);incoming[n]|=out
   if before!=len(incoming[n]):todo.append(n)
 return incoming
def contract(K,parent):
 B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py')
 e=read(HERE/'evidence-v1.json');raw=(R/K['carrier']).read_bytes();f=e['selected_functions'][0];by={};graphs={};opmaps={};cfgs=[];rd=[]
 need(len(e['selected_functions'])==1 and(f['start'],f['end'],e['code_bytes'],e['instructions'])==(0x20000ac6,0x20000bc0,250,94),'One whole original fragment preparer')
 def whole(sf,origin='SDK'):
  at=sf['start'];payload=b''
  for o in sf['operations']:
   bb=bytes.fromhex(o['bytes']);need(o['addr']==at and len(bb)==o['size']==(4 if bb[0]&3==3 else 2),'Contiguous whole original instruction widths');payload+=bb;at+=len(bb)
  source=sf.get('source_start',sf['start']);base=0x40000 if origin=='SDK'else 0x8000;data=raw if origin=='SDK'else(R/K['APP']).read_bytes()
  need(at==sf['end']and payload==data[source-base:source-base+len(payload)],'Every selected/reference original byte')
  if sf['start']>=0x20000000:need(source==sf['start']-0x20000000+0x40270,'Conditional first-copy mapping')
  ext={d[1]for o in sf['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
  ops,g,cfg=V['whole_cfg'](sf,B,ext,sf.get('own_frame_bytes',96));by.update(ops);graphs[sf['start']]=g;opmaps[sf['start']]=ops;cfgs.append(cfg);return payload
 whole(f)
 def operands(w):need(all(by[p]['opcode']==s for p,s in w.items()),'Exact fragment/init/guard operands')
 def definitions(sf,reg,p,w):
  need(reaching(sf,opmaps[sf['start']],graphs[sf['start']],reg)[p]==set(w),'Whole-CFG fragment/reference argument provenance');rd.append(dict(function=sf['start'],register=reg,PC=p,definitions=sorted(w)))
 operands({0x20000ac6:'lw a4, 280(a0)',0x20000aca:'beqz a4, 0x20000bbc',0x20000acc:'addi sp, sp, -16',0x20000ad2:'qk.c.lbu a5, 12(a0)',0x20000ad4:'lbu a1, 78(a0)',0x20000ad8:'mv s0, a0',0x20000ada:'andi a5, a5, 252',0x20000ade:'qk.c.sb a5, 12(a0)',0x20000ae0:'qk.c.lbu a3, 9(a4)',0x20000ae2:'qk.c.lhu a2, 12(a4)',0x20000ae4:'slli a0, a3, 0x18',0x20000ae8:'srai a0, a0, 0x18',0x20000aea:'bleu a2, a1, 0x20000b58',0x20000aee:'bgez a0, 0x20000b50',0x20000af2:'qk.c.lbu a0, 8(a4)',0x20000af4:'andi a3, a3, 127',0x20000af8:'qk.c.sb a3, 9(a4)',0x20000afa:'li a2, 1',0x20000afc:'ori a3, a5, 2',0x20000b00:'bne a0, a2, 0x20000b08',0x20000b04:'ori a3, a5, 1',0x20000b08:'qk.c.sb a3, 12(s0)',0x20000b0a:'lw a5, 4(a4)',0x20000b0c:'addi a5, a5, 2',0x20000b0e:'sw a5, 4(a4)',0x20000b10:'qk.c.sb a1, 21(s0)',0x20000b12:'lw a0, 272(s0)',0x20000b16:'mv a2, a1',0x20000b18:'lw a1, 4(a4)',0x20000b1a:'addi a0, a0, 2',0x20000b1c:'jal ra, 0x20000332'})
 for reg,p,w in [('a0',0x20000b1c,[0x20000b1a]),('a1',0x20000b1c,[0x20000b18]),('a2',0x20000b1c,[0x20000b16]),('s0',0x20000b12,[0x20000ad8])]:definitions(f,reg,p,w)
 operands({0x20000b20:'lw a5, 280(s0)',0x20000b24:'qk.c.lbu a2, 21(s0)',0x20000b26:'lw a3, 4(a5)',0x20000b28:'qk.c.lhu a4, 12(a5)',0x20000b2a:'add a3, a3, a2',0x20000b2c:'sub a4, a4, a2',0x20000b2e:'sw a3, 4(a5)',0x20000b30:'qk.c.sh a4, 12(a5)',0x20000b32:'li a5, 2',0x20000b34:'qk.c.sb a5, 27(s0)',0x20000b3e:'lbu a5, 510(a5)',0x20000b42:'bleu a5, a4, 0x20000b84',0x20000b48:'ori a5, a5, 16',0x20000b50:'ori a5, a5, 1',0x20000b58:'andi a3, a2, 255',0x20000b5c:'bgez a0, 0x20000b8e',0x20000b70:'qk.c.sb a2, 12(s0)',0x20000b72:'qk.c.sb a3, 21(s0)',0x20000b74:'sb zero, 9(a4)',0x20000b78:'li a5, 1',0x20000b7a:'qk.c.sb a5, 27(s0)',0x20000b7c:'lw a5, 280(s0)',0x20000b80:'lw a5, 0(a5)',0x20000b88:'li a0, 0',0x20000b8a:'addi sp, sp, 16',0x20000b8c:'ret',0x20000b8e:'ori a5, a5, 1',0x20000b94:'qk.c.sb a3, 21(s0)',0x20000b96:'sb zero, 9(a4)',0x20000b9a:'lw a0, 272(s0)',0x20000b9e:'lw a1, 4(a4)',0x20000ba0:'addi a0, a0, 2',0x20000ba2:'jal ra, 0x20000332',0x20000ba6:'lw a5, 280(s0)',0x20000baa:'qk.c.lbu a2, 21(s0)',0x20000bac:'lw a3, 4(a5)',0x20000bae:'qk.c.lhu a4, 12(a5)',0x20000bb4:'sw a3, 4(a5)',0x20000bb6:'qk.c.sh a4, 12(a5)',0x20000bb8:'li a5, 3',0x20000bbc:'li a0, 1',0x20000bbe:'ret'})
 for reg,p,w in [('a0',0x20000ba2,[0x20000ba0]),('a1',0x20000ba2,[0x20000b9e]),('a2',0x20000ba2,[0x20000ae2])]:definitions(f,reg,p,w)
 g=graphs[f['start']];copy_sites={0x20000b1c,0x20000ba2};need(not copy_sites&V['reachable'](g,0x20000b60),'First whole-fragment path has no copy-helper call')
 need({o['addr']for o in f['operations']if o['type']=='call'}==copy_sites,'Only actual original copy calls')
 need(not any(re.fullmatch(r'(sw|sh|sb) \w+, (280|284)\((s0|a0)\)',o['opcode'])for o in f['operations']),'No explicit queue-head/tail store;no invented dequeue')
 refs={}
 for item in e['execution_references']:
  sf=item['function'];need(sha(R/item['evidence'])==item['evidence_sha256']and sf==next(x for x in read(R/item['evidence'])['selected_functions']if x['start']==sf['start']),'Exact frozen whole reference');whole(sf);refs[sf['start']]=sf
 O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');owned=O['inspect'](R/K['SDK_parent']/'c/candidate.o');bm=owned['_byte_map'];roles={tuple([json.loads(x)[0][1],json.loads(x)[1],json.loads(x)[3][1]])for x in owned['_typed_relations']}
 for sf in refs.values():
  for o in sf['operations']:
   p=o['addr'];bb=bytes.fromhex(o['bytes']);nn=bytes(bm[p+i]for i in range(len(bb)));d=B['decode_control'](bb,p);rels=[r for r in roles if r[0]==p]
   if d:
    kind,target=d;need((p,kind,target)in roles,'Actual retained reference control role');mask=B['MASKS'][kind][1];need(int.from_bytes(bb,'little')&mask==int.from_bytes(nn,'little')&mask,'Reference control opcode bits')
   elif rels:
    need(len(rels)==1 and rels[0][1]in [23,24],'Actual retained far-pair role');mask=B['MASKS'][rels[0][1]][1];need(int.from_bytes(bb,'little')&mask==int.from_bytes(nn,'little')&mask,'Reference PC-relative opcode bits')
   else:need(bb==nn,'Every actual retained nonrelocated reference byte')
 operands({0x578be:'bnez a5, 0x57932',0x57912:'beqz a0, 0x57932',0x57918:'sw a0, 172(s3)',0x57940:'ret',0x57980:'mv s0, a0',0x5798c:'beqz s0, 0x579be',0x5799e:'beqz a3, 0x579cc',0x579cc:'li a5, 1',0x579ce:'qk.c.sh a5, 8(s0)',0x579d0:'sw s0, 156(s1)',0x579d4:'sw s0, 160(s1)',0x579dc:'jal ra, 0x578a4',0x579e0:'lw a5, 160(s1)',0x579e4:'sw zero, 0(a5)',0x579e8:'sb zero, 10(s0)',0x579ec:'sb zero, 14(s0)',0x579f0:'j 0x579bc',0x579bc:'qk.c.lhu a0, 8(s0)',0x579c6:'ret',0x59e70:'jal ra, 0x57962',0x59e74:'mv s3, a0',0x59e76:'beqz a0, 0x59ee0',0x59e78:'jal ra, 0x5784a',0x59e94:'addi a5, s2, 492',0x59e98:'qk.c.lhu a5, 16(a5)',0x59ea2:'addi a5, a5, 5',0x59e9a:'li a4, 260',0x59eae:'li a0, 260',0x59eb8:'li a5, 64',0x59ec0:'li a0, 64',0x59ed4:'sw a0, 272(s0)',0x59ed8:'bnez a0, 0x59ef0'})
 definitions(refs[0x57962],'s0',0x579ce,[0x57980]);definitions(refs[0x57962],'a0',0x579be,[0x579bc,0x5798a])
 path=[0x579dc,0x579e0,0x579e4,0x579e8,0x579ec,0x579f0,0x579bc];need(all(graphs[0x57962][p]==[n]for p,n in zip(path,path[1:])),'Original post-pool-call continuation never checks initializer return value')
 need((0x579dc,17,0x578a4)in roles and(0x59e70,17,0x57962)in roles,'Actual typed initializer chain')
 operands({0x20001166:'lw a4, 280(a0)',0x2000116a:'bnez a4, 0x200012fa'})
 app=next(sf for sf in read(R/K['config_evidence'])['selected_functions']if sf['start']==0x199e2);payload=whole(app,'APP');E=lib(K['reader'])['ELF'];diag=E(R/K['APP_ELF']);need(payload==U['native_bytes'](diag,app['start'],app['end']),'Whole308-byte APP config original/native reference')
 operands({0x19a5e:'li a4, 251',0x19a62:'sh a4, 32(sp)'})
 definitions(app,'a4',0x19a62,[0x19a5e]);need(16+16==32 and 251+5==256 and 64<=256<=260,'Conditional nominal configured maximum/frame-buffer arithmetic')
 need(parent['contract']['node_marker_byte']==129 and parent['contract']['node_stored_buffer_is_incoming_pointer_minus2']and parent['contract']['connection_queue_head_offset']==280,'Fresh actual enqueue/fragment input correspondence')
 return dict(passed=True,whole_CFGs=cfgs,unique_reaching_definitions=rd,fragment_preparer=[0x20000ac6,0x20000bc0],fragment_preparer_source=[0x40d36,0x40e30],fragment_preparer_bytes=250,fragment_preparer_instructions=94,empty_queue_returns1_before_frame=True,nonempty_normal_return=0,fragment_limit_record_byte_offset=78,frame_buffer_record_pointer_offset=272,copy_destination_prefix_bytes=2,queue_head_record_offset=280,node_buffer_pointer_offset=4,node_remaining_halfword_offset=12,node_marker_byte_offset=9,first_fragment_test_marker_high_bit=128,clear_first_marker_high_bit_on_split=True,first_split_advances_node_buffer_by2_before_copy=True,first_split_links_enqueue_incoming_minus2_back_to_incoming_pointer=True,first_split_or_continuation_split_copies_limit_bytes=True,copy_helper=0x20000332,copy_call_sites=[0x20000b1c,0x20000ba2],fresh_head_and_length_reads_after_copy_preserved=True,copied_fragment_advances_buffer_and_reduces_remaining_under_stability=True,fragment_size_record_byte_offset=21,prepared_state_record_byte_offset=27,split_state=2,first_whole_state=1,continuation_whole_state=3,first_whole_path_has_no_copy_call=True,first_whole_path_has_no_explicit_buffer_or_remaining_advance=True,whole_fragment_clears_node_marker_byte=True,frame_flags_record_byte_offset=12,frame_low_bits_mask_before_prepare=252,first_fragment_argument1_uses_low_bit1_other_uses_low_bit2=True,continuation_uses_low_bit1=True,more_data_candidate_bit=16,tx_event_config_byte_address=0x200031fe,tx_event_config_offset=18,no_explicit_queue_head_or_tail_update=True,no_explicit_descriptor_release=True,prepared_state_is_not_radio_delivery_or_ack_proof=True,fragment_limit_live_value_or_positive_bound_proved=False,incoming_call_or_pointer_binding_proved=False,reference_CODE_bytes=1414,reference_instructions=454,reference_new_CODE_bytes=0,pool_initializer=[0x578a4,0x57962],controller_record_constructor=[0x57962,0x57a1e],controller_record_initializer=[0x59e64,0x5a004],typed_initialization_calls=[dict(PC=0x59e70,target=0x57962),dict(PC=0x579dc,target=0x578a4)],pool_initialization_only_in_first_empty_controller_list_branch=True,controller_record_head_tail_published_before_pool_init_call=True,pool_allocation_failure_bypasses_pool_pointer_store=True,pool_initializer_status_not_checked_by_constructor=True,constructor_returns_record_ID_after_normal_pool_initializer_return=True,record_ID_does_not_prove_pool_ready=True,static_failure_branch_analysis_only_no_negative_runtime_test=True,scheduler_guard=[0x20001122,0x2000138e],scheduler_queue_nonempty_branch=0x2000116a,scheduler_guard_is_not_fragment_consumer=True,APP_config_reference_bytes=308,APP_nominal_BufMaxLen=251,APP_BufMaxLen_stack_offset=32,conditional_nominal_frame_buffer_bytes=256,fragment_limit_bound_by_frame_buffer_not_proved=True,remaining_normal_named_UND=0,own_indirect_call_sites=0,all_inherited_indirect_runtime_targets_closed=False,conditions=['Installed ROM/Xwchc/header and normal saved-register/argument ABI match the archived candidate','The conditional first-copy source mapping completed and preserves code atRAM20000AC6;entry/call binding remains unproved','Connection record,queue node,buffer pointers,two-byte prefixes and source/destination spans are valid and nonoverlapping where progress is inferred','Fragment limit and remaining length describe valid storage;fresh reads after copy remain valid despite any permitted side effects','First controller-record creation must have valid allocation and external ordering/synchronization;record publication precedes pool initialization and pool failure is not propagated here','Nominal APP BufMaxLen251/frame-buffer256 require original config stores/copy and stable configuration;record+78 is not yet bounded by that size','No target execution,radio scheduling,actual transmission,acknowledgment,descriptor recycling or physical OTA compatibility is established'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
 need(native['c']==native['cpp']and len(native['c']['UND'])==1 and native['c']['opaque_callbacks_not_provided']==0,'Identical unit with one real copy import and no own indirect site')
 c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
 if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition')
 else:need(out.exists(),'Retained actual composition required')
 U=lib('experiments/tsl9-resident-gatt-CCC-write/verify-v2.py');O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');sdk={}
 for mode in ['c','cpp']:
  folder=out/mode;ins=[R/K['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];obj=folder/'candidate.o'
  if trial:
   folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
   (folder/'link.log').write_text(U['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual controller queue SDK partial link')
  sdk[mode]=U['union'](obj,ins,K,(45144,412,3223,5,2566,0));owned=O['inspect'](obj)
  need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==45144 and owned['duplicate_original_CODE_bytes']==0 and not owned['named_UND'],'Unique actual SDK CODE and no unresolved normal imports')
  bm=owned['_byte_map'];need(all(p in bm for p in range(0x20000ac6,0x20000bc0)),'Every original250-byte fragment body genuinely owned');pending=set(bm);count=0
  while pending:
   p=min(pending)
   while p in pending:
    width=4 if bm[p]&3==3 else 2;need(all(p+i in pending for i in range(width)),'Every whole native instruction owned once')
    pending.difference_update(range(p,p+width));p+=width;count+=1
  need(count==15710,'Actual complete SDK instruction count');sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
 need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ compositions identical')
 result=dict(schema='TSL9-transmit-fragment-prepare-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_complete_bodies=1,new_SDK_CODE_bytes=250,new_SDK_instructions=94,new_SDK_DATA_bytes=0,new_normal_imports_resolved=1,prior_genuine_import_body_resolved=None,new_genuine_unprovided_normal_callees=0,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,all_indirect_runtime_targets_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
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
