"""Audit conditional APP reset values and the real candidate bootstrap write footprint."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='reset_state_static_library')
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def audit(llvm):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():need(not Path(p).is_absolute()and'..'not in Path(p).parts and'command_dispatch_windows'not in p,'Allowed bounded input');need(sha(R/p)==h,'Input changed: '+p)
 B=lib(K['control_reader']);M=read(R/K['APP_map']);rows=[o for o in M['instructions']if 0x186aa<=o['PC']<0x18734];need(len(rows)==37,'Complete primary reset path through resident tail');pc=0x186aa;raw=bytearray();ops={}
 for o in rows:
  b=bytes.fromhex(o['bytes']);need(o['PC']==pc and len(b)in [2,4],'Whole original APP instruction boundaries');ops[pc]=o;raw.extend(b);pc+=len(b)
 need(pc==0x18734 and len(raw)==138,'Exactly138 primary-reset CODE bytes');fw=(R/K['firmware']).read_bytes();need(raw==fw[0x186aa-0x8000:0x18734-0x8000],'All selected reset bytes equal original APP')
 E=lib(K['ELF_reader'])['ELF'];native=[]
 for mode in ['c','cpp']:
  p=R/K['APP_layout']/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';e=E(p);bm={}
  for s in e.sections:
   if s['type']!=1 or s['flags']!=6:continue
   a=max(0x186aa,s['address']);z=min(0x18734,s['address']+s['size'])
   if a<z:bb=e.data(s);bm.update({q:bb[q-s['address']]for q in range(a,z)})
  need(set(bm)==set(ops_byte for ops_byte in range(0x186aa,0x18734))and bytes(bm[q]for q in range(0x186aa,0x18734))==raw,'Actual native whole APP reset bytes');native.append(dict(mode=mode,ELF_sha256=sha(p),whole_CODE_bytes_equal=138))
 need(native[0]['ELF_sha256']==native[1]['ELF_sha256'],'Actual current C/C++ original-coordinate diagnostic identity')
 def word(p):return int.from_bytes(bytes.fromhex(ops[p]['bytes']),'little')
 def pair(hi,lo,rd):
  h,q=word(hi),word(lo);need(h&127==0x17 and(h>>7)&31==rd and q&0x707f==0x13 and(q>>7)&31==rd and(q>>15)&31==rd,'Exact original AUIPC/ADDI fields');return(hi+(h&0xfffff000)+sx(q>>20,12))&0xffffffff
 gp,sp,source,end,vector,main=[pair(a,b,r)for a,b,r in [(0x186aa,0x186ae,3),(0x186b2,0x186b6,2),(0x186ba,0x186be,10),(0x186e2,0x186e6,11),(0x18710,0x18714,5),(0x18724,0x18728,5)]];need((gp,sp,source,end,vector,main)==(0x20004000,0x20010000,0x1ab60,0x2000c958,0x8038,0x9008),'Actual current APP initialization and machine-entry profile')
 expected={0x186c2:'mv a1, gp',0x186c6:'addi a2, gp, 128',0x186ca:'bleu a2, a1, 0x186de',0x186ce:'lw t0, 0(a0)',0x186d2:'sw t0, 0(a1)',0x186d6:'addi a0, a0, 4',0x186d8:'addi a1, a1, 4',0x186da:'bltu a1, a2, 0x186ce',0x186de:'addi a0, gp, 128',0x186ea:'bleu a1, a0, 0x186f8',0x186ee:'sw zero, 0(a0)',0x186f2:'addi a0, a0, 4',0x186f4:'bltu a0, a1, 0x186ee',0x186f8:'li t0, 31',0x186fa:'csrw 0xbc0, t0',0x186fe:'li t0, 3',0x18700:'csrw 0x804, t0',0x18704:'lui t0, 0x2',0x18708:'addi t0, t0, -1912',0x1870c:'csrs mstatus, t0',0x18718:'ori t0, t0, 3',0x1871c:'csrw mtvec, t0',0x18720:'jal ra, 0x1874a',0x1872c:'csrw mepc, t0',0x18730:'j 0x40000'};need(all(ops[p]['op']==v for p,v in expected.items()),'Every remaining reset instruction explicitly checked')
 need(len(expected)+12==37,'All37 reset instructions covered by raw pair or operand checks');g={p:[]for p in ops}
 for p,o in ops.items():
  after=p+len(bytes.fromhex(o['bytes']));d=B['decode_control'](bytes.fromhex(o['bytes']),p)
  if p==0x18730:need(d==(17,0x40000)and(word(p)>>7)&31==0,'Actual no-link resident tail');continue
  if p==0x18720:need(d==(17,0x1874a)and(word(p)>>7)&31==1,'Actual clock call,with a normal-return assumption');g[p]=[after];continue
  if d:need(d[0]in [16,44]and d[1]in ops,'Actual local conditional branch');g[p]=[d[1],after]
  else:need(after in ops,'No implicit fallthrough beyond reset handoff');g[p]=[after]
 def reachable(start,skip=None):
  seen=set();pending=[start]
  while pending:
   p=pending.pop()
   if p==skip or p in seen:continue
   seen.add(p);pending.extend(g[p])
  return seen
 need(reachable(0x186aa)==set(ops)and 0x18730 not in reachable(0x186aa,skip=0x186f8),'Whole primary CFG and zero-loop exit before handoff')
 zero_start=gp+128;need(zero_start%4==end%4==0 and 0<=zero_start<end<sp and(end-zero_start)%4==0,'Nonwrapping aligned original zero loop');zero_words=(end-zero_start)//4;need(zero_words==8758 and zero_start+4*(zero_words-1)==end-4,'Finite loop induction:8758 stores,not a target or memory simulation')
 fields=[('input_counter',gp+176,1),('sequence_states',gp+332,4),('event_word_index',gp+370,1),('mode_enable_selector_countdown',0x2000bf38,4)];states=[]
 for name,a,n in fields:need(zero_start<=a<a+n<=end,'All watched bytes lie inside actual reset zero interval');states.append(dict(name=name,start=a,end=a+n,bytes=n,value_at_zero_loop_exit=0,proof_point=0x186f8,physical_live_value_observed=False))
 csr=word(0x1870c);need(csr&0x707f==0x2073 and csr>>20==0x300 and(csr>>15)&31==5,'Original CSRRS mstatus register instruction');mask=0x2000-1912;need(mask==0x1888 and mask&8 and 0x1870c<0x1871c,'Mask includes standard MIE bit before the later mtvec write')
 A=lib(K['SDK_audit']);N=lib(K['SDK_builder']);N['pins'](llvm);saved=read(R/K['SDK_measurement']);actual=N['portable'](N['inputs'](llvm),llvm);key=next(k for k in actual if k.replace('\\','/').endswith('/src/source-manifest.json'));need(set(actual)==set(saved['inputs'])and[k for k in actual if actual[k]!=saved['inputs'][k]]==[key],'Only historical manifest differs in the retained SDK native input inventory');historical=lib(K['historical_manifest_helper'])['raw_parent']();need(saved['inputs'][key]==dict(bytes=len(historical),sha256=hashlib.sha256(historical).hexdigest())and len(json.loads(historical)['files'])==159,'Exact159-source manifest exception reconstructed,not ignored')
 O=lib(K['SDK_ownership']);sdk_native=[]
 for mode in ['c','cpp']:
  folder=(R/K['SDK_measurement']).parent/mode;need(N['inventory'](folder)==saved['modes'][mode]['artifacts'],'Every retained SDK native artifact unchanged');unit=folder/'unit.o';result=N['audit_object'](unit);need(result==saved['modes'][mode]['result'],'Fresh original234B instruction/typed-relocation comparison equals compilation receipt');p=O['inspect'](unit);q=O['inspect'](R/K['SDK_component']/mode/'candidate.o');need(p['passed']and q['passed']and p['CODE_bytes']==234 and all(q['_byte_map'].get(a)==b for a,b in p['_byte_map'].items())and set(p['_typed_relations'])<=set(q['_typed_relations']),'All actual bootstrap bytes and14 typed roles have current positive SDK body backing');sdk_native.append(dict(mode=mode,unit_sha256=sha(unit),unit_CODE_bytes=234,typed_roles=14,current_SDK_sha256=q['object_sha256'],current_SDK_CODE_bytes=q['CODE_bytes'],all_bootstrap_native_bytes_and_roles_retained=True))
 stages,graphs,so=A['stages'](N);need(sum(x['instructions']for x in stages)==67 and sum(x['bytes']for x in stages)==234,'All five full bootstrap stages and67 original instructions');ap=A['absolute_pair'];sdk_gp=ap(so,0x6de7e,0x6de82,3,True);sdk_sp=ap(so,0x6de86,0x6de8a,2,True);need((sdk_gp,sdk_sp)==(gp,sp),'APP and candidate bootstrap agree on GP/SP numerical profiles')
 seed=[ap(so,hi,lo,rd,True)for hi,lo,rd in [(0x6de8e,0x6de92,10),(0x6de96,0x6de9a,11),(0x6de9e,0x6dea2,12)]];first=[ap(so,hi,lo,rd)for hi,lo,rd in [(0x6de38,0x6de46,10),(0x6de34,0x6de42,11),(0x6de30,0x6de3e,12)]];second=[ap(so,hi,lo,rd)for hi,lo,rd in [(0x6de5a,0x6de66,10),(0x6de56,0x6de62,11),(0x6de52,0x6de5e,12)]];sz=[ap(so,hi,lo,rd)for hi,lo,rd in [(0x20000022,0x2000002a,15),(0x20000026,0x2000002e,14)]]
 need(seed==[0x40280,0x20000010,0x20000040]and first==[0x402b0,0x20000040,0x20002e70]and second==[0x6eaa4,0x20002e70,0x20002ef8]and sz==[0x20002ef8,0x20003614],'Actual original seed/copy/inclusive-zero range operands')
 stores=[p for p,o in so.items()if o['opcode'].split()[0]in ['sw','sh','sb']];need(sorted(stores)==[0x6de12,0x6de1c,0x6de26,0x6de3c,0x6deae,0x2000001c,0x20000038],'Every explicit memory store across all five selected stages classified')
 writes=[dict(role='three_RAM_slots',start=0x20000000,end=0x2000000c),dict(role='seed',start=seed[1],end=seed[2]),dict(role='first_copy',start=first[1],end=first[2]+4),dict(role='second_copy',start=second[1],end=second[2]+4),dict(role='inclusive_zero',start=sz[0],end=sz[1]+4),dict(role='loader_own_frame_conservative',start=sp-16,end=sp)]
 need(all(not(w['start']<x['end']and x['start']<w['end'])for w in writes for x in states),'All known bootstrap destination and own-frame intervals are disjoint from watched state bytes')
 need(so[0x6debe]['opcode']=='mret'and so[0x6debe]['bytes']=='73002030'and not any('mepc'in o['opcode']for o in so.values()),'Actual MRET bootstrap exit with no explicit selected-stage MEPC overwrite')
 return dict(schema='TSL9-current-APP-reset-state-and-candidate-write-footprint-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),APP_primary_CODE_bytes=138,APP_primary_instructions=37,APP_native_CODE_comparisons=native,APP_primary_CFG_all_instructions_reachable=True,APP_nominal_GP=gp,APP_nominal_SP=sp,APP_copy_source=[source,source+128],APP_copy_destination=[gp,zero_start],APP_zero_destination=[zero_start,end],APP_zero_word_stores=zero_words,watched_states_at_zero_loop_exit=states,zero_loop_exit_PC=0x186f8,clock_call_PC=0x18720,clock_callee_watched_RAM_noninterference_proved=False,mstatus_OR_mask=mask,mstatus_is_not_proved_equal_to_mask=True,standard_MIE_bit_in_mask=True,mstatus_set_PC=0x1870c,mtvec_write_PC=0x1871c,local_order_sets_MIE_before_mtvec=True,incoming_IRQ_state_or_actual_interrupt_exclusion_proved=False,MEPC_before_resident_tail=main,resident_tail_PC=0x18730,resident_tail_target=0x40000,resident_tail_writes_RA=False,SDK_native_bootstrap=sdk_native,SDK_stages=stages,SDK_explicit_write_intervals=writes,SDK_known_write_intervals_disjoint_from_watched_states=True,SDK_exit_PC=0x6debe,SDK_exit_kind='MRET',SDK_first_source_gap=[0x6eb2c,0x6eb30],SDK_gap_is_not_missing_APP_bytes=True,SDK_source_gap_filled=False,SDK_known_four_source_bytes_read=False,conditional_zero_preservation_through_bootstrap_requires_clock_and_async_noninterference=True,watched_values_at_first_application_use_proved=False,global_counter_or_mode_invariants_proved=False,installed_ROM_RAM_IRQ_or_startup_completion_proved=False,source_or_native_artifact_changed=False,formal_APP_source_files_unchanged=164,formal_APP_byte_coverage_unchanged=95.75,APP_source_provider_UND_unchanged=6,new_APP_CODE_or_DATA_bytes=0,new_SDK_CODE_or_DATA_bytes=0,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False,goal_complete=False,conditions=['Original nominal placement and register/CSR instruction semantics;all stated memory accesses valid and normal loops complete','Watched zeros are established at186F8,not observed on physical hardware','To preserve zeros through handoff,clock1874A and all IRQ/DMA/alias or nested paths must not modify watched state/registers','Candidate bootstrap must match installed resident code and sources,including readable6EB2C..6EB30;MRET uses then-liveMEPC','Later writers/callbacks and first-use index or mode domains remain separate obligations'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit(a.tool_dir.resolve());dest=HERE/'verification-v1.json'
  if a.write_receipt:need(not dest.exists(),'Create-only reset-state receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(v==read(dest),'Fresh reset-state contract equals retained receipt')
  print(json.dumps(dict(passed=True,APP_CODE_bytes=138,APP_instructions=37,SDK_CODE_reference_bytes=234,SDK_instructions=67,zero_word_stores=8758,watched_groups=4,known_SDK_writes_disjoint=True,first_use_values_proved=False,firmware_ready=False,new_BIN=False)))
 except Exception as e:
  message=str(e)
  for path,label in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),label).replace(path.as_posix(),label)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
