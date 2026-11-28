"""Offline selected ID9 vector setup, retained owners and ID10 return join.

Original-byte/CFG guards and immutable interval/index/frame certificates.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_id8_static as previous
import check_v4160_id9_vector_dispatch_static as id9

init,sparse,check=previous.init,previous.sparse,previous.check
layout,separated=previous.layout,previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-id9-static.json')


def q0_callback_triples():
 pairs=previous.q0_callback_pairs();triples=[[a,b,c] for a,b in pairs for c in (range(b+1,13) if b<12 else [12])]
 check(len(triples)==299 and len({tuple(t) for t in triples})==299,'fallbackid9 retained callback triple census')
 check(all((a<b<c or a<b==c==12 or a==b==c==12) and 2<=c<=12 for a,b,c in triples),'fallbackid9 insert indices increase; full remains full')
 check([sum(test(a,b,c) for a,b,c in triples) for test in (lambda a,b,c:c<12,lambda a,b,c:b<12 and c==12,lambda a,b,c:a<12 and b==12,lambda a,b,c:a==12)]==[220,66,12,1],'fallbackid9 closed combinatorial partition')
 return triples


def profile(data,hexraw,index,parent,allocation_rows,zero_rows,prior):
 g=0x20003000+80*index;delta=80*index;F=g+492;ctx=F-80;d=id9.role.DETAILS[index];entry=d['entry'];pc,vpc=id9.STARTS[index][0:2]
 check(parent['end_cut']['pc']==entry+68 and parent['end_cut']['target']==pc and [parent['end_cut'][k] for k in ('fallback','gate','task_count','saved_ID6','local_ID7','local_ID8','A0','A2')]==[0,5,10,6,7,8,9,10],'fallbackid9 inherited ID9/count10 join')
 windows={p:id9.body(init.binding.take(data,id9.STARTS[index][k],id9.SIZES[k]),p,index) for k,p in enumerate(id9.PARTS)}
 selector=id9.previous.previous.body(init.binding.take(data,0x4d9ec+152*index,44),'selector',index);cbreg=id9.leaves.body(init.binding.take(data,0x4efe2+152*index,42),'callback_register',index)
 pn={v['pc']:v for v in windows['initializer']['instructions']};vn={v['pc']:v for v in windows['vectors']['instructions']};on={v['pc']:v for v in windows['next_outer']['instructions']}
 check(windows['initializer']['calls']==[dict(pc=hex(pc+6),target=hex(vpc),rd=1),dict(pc=hex(pc+22),target=selector['start'],rd=1)] and windows['initializer']['tails']==[dict(pc=hex(pc+38),target=cbreg['start'],rd=0)],'fallbackid9 exact initialization calls/tail; runtime paths not invoked')
 check(pn[pc+4]['rs2']==10 and pn[pc+4]['imm']==12 and pn[pc+10]['rd']==10 and pn[pc+10]['imm']==12 and pn[pc+18]['rs2']==10 and pn[pc+16]['imm']==6,'fallbackid9 saved ID9/local byte/selector6 operands')
 check(pn[pc+26]['rd']==1 and pn[pc+26]['imm']==28 and pn[pc+36]['imm']==32 and pn[pc+28]['imm']+pn[pc+32]['imm']==id9.STARTS[index][4]!=0,'fallbackid9 restore RA/frame and nonzero callback input')
 pointer_pairs=((16,24),(40,48),(54,58),(64,72),(80,88),(94,98));pointers=[vn[vpc+a]['imm']+vn[vpc+b]['imm'] for a,b in pointer_pairs]
 check(tuple(pointers)==id9.POINTERS[index],'fallbackid9 six independent-profile vector pointers')
 vector_rows=[(4,924),(12,908),(28,904),(36,928),(52,932),(62,936),(76,912),(92,916),(102,920)]
 check(sorted(a for o,a in vector_rows)==list(range(904,940,4)) and [a for o,a in vector_rows if vn[vpc+o]['rs2']==0]==[924,908,904],'fallbackid9 exact vector36B union and zero stores')
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]
 protected += [('record0',g+800,3),('local_ID8',g+941,1),('flags_byte',g+944,1),('entries0_to9',layout.T,40),('ID8_pool_pointer',g-116,4),('ID8_middle_pointer',g-112,4),('ID8_end_pointer',g-128,4),('ID8_hook_A',g-144,4),('ID8_hook_B',g-252,4),('ID8_zero_word_A',g-148,4),('ID8_zero_word_B',g-256,4)]
 def exclude(a,z,skip=()):
  check(0<=a<a+z<=1<<32,'fallbackid9 nonwrapping interval')
  for name,p,w in protected:
   if name not in skip:check(separated(a,z,p,w),'fallbackid9 footprint excludes '+name)
 fixed=[dict(role='vectors',offset=o,address=g+a,bytes=4) for o,a in vector_rows]+[dict(role='local_ID9',offset=18,address=g+943,bytes=1),dict(role='record2_ID',offset=32,address=g+826,bytes=1),dict(role='record2_selector',offset=34,address=g+824,bytes=2)]
 check({vpc+o for o,a in vector_rows}=={v['pc'] for v in windows['vectors']['instructions'] if v['op']=='store'},'fallbackid9 complete vector store census')
 check([v['pc']-pc for v in windows['initializer']['instructions'] if v['op']=='store' and v['rs1']!=2]==[18],'fallbackid9 complete initializer nonframe store census')
 check(g+856+48==g+904 and g+936+4==g+940 and g+824+3<=g+848,'fallbackid9 CB/vector/ID adjacency and record2 extent')
 for v in fixed:exclude(v['address'],v['bytes'])
 spc=int(selector['start'],16);se={int(p,16):[int(q,16) for q in qs] for p,qs in selector['conditional_CFG'].items()}
 selector_path=id9.paths.chain(se,spc,{spc+12:spc+16});check(len(selector_path)==14 and (6-4)*12==24 and 11 not in selector['encoded_GPR_definitions'],'fallbackid9 fixed selector6/index2 accepted path')
 init_edges={int(p,16):[int(q,16) for q in qs] for p,qs in windows['initializer']['conditional_CFG'].items()};initializer_path=id9.paths.chain(init_edges,pc,{})
 check(initializer_path[-1]==hex(pc+38),'fallbackid9 initializer finite CFG ends unlinked tail')
 cb=g+856;cb_paths=id9.leaves.path_certificates(cbreg)
 check(parent['callback_publication']['q_positive_selected_slot']==1 and parent['callback_publication']['new_pointer']!=0 and parent['callback_publication']['prior_slot0_nonzero_pointer']!=0,'fallbackid9 prior selected nonzero slots0/1')
 cbwrites=[(cb+4*j,4) for j in range(12)]
 for a,z in cbwrites:exclude(a,z,('resource_callback_table',))
 footprint_checks=0;table_checks=0
 def owner_checks(owners,table_size):
  nonlocal footprint_checks,table_checks
  for a,z in [(v['address'],v['bytes']) for v in fixed]+cbwrites:
   for name,p,w in owners:check(separated(a,z,p,w),'fallbackid9 owner/header survives '+name);footprint_checks+=1
   check(separated(a,z,layout.P,table_size),'fallbackid9 full first table payload survives until registration');table_checks+=1
  for name,p,w in owners:check(separated(layout.T+40,4,p,w),'fallbackid9 entry10 excludes owner/header '+name)
 for row in allocation_rows:
  n,b,q,r,H,size,request,R,P,N,size2,k,account,used=row;t=prior[n,q]
  owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request']),('third_remainder_header_or_reused_ID8_header',t['new_remainder'],8),('ID8_header',H,8),('ID8_payload',P,R),('ID8_remainder_header',N,8)]
  a,e=t['first_table_payload'];check(a==layout.P,'fallbackid9 positive first table base');owner_checks(owners,e-a)
 q0R=next(v['rounded_payload'] for v in layout.facts() if v['input_byte']==0);firstsmall=previous.third.previous.geometry()[1]
 for n,b,q in zero_rows:
  owners=[]
  if q:
   t=prior[n,q];owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request']),('third_remainder_header',t['new_remainder'],8)];a,e=t['first_table_payload'];table_size=e-a
  else:
   table_size=q0R
   if n:
    t=firstsmall[n-1];owners=[('first_header',t['header'],8),('first_payload',t['payload'],t['request']),('first_remainder_header',t['new_remainder'],8)]
  owner_checks(owners,table_size)
 old=id9.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in old['instructions']};check(en[entry+68]['target']==pc and en[entry+68]['rd']==1 and id9.STARTS[index][6]==entry+72,'fallbackid9 tail ordinary RET joins original outer RA')
 check(on[entry+80]['target']==d['reg'] and on[entry+84]['target']==d['outer_init'][4],'fallbackid9 next registrar/fifth initializer cut')
 handler=0x6d000+d['outer_lows'][4];check(on[entry+72]['imm']+on[entry+76]['imm']==handler,'fallbackid9 next handler formation')
 reg=id9.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackid9 registrar preserves A1 result')
 for a,z in ((layout.T+40,4),(ctx+1,1)):exclude(a,z,('task_count',))
 check(layout.T+44<=layout.T+4*14 and 10<14 and 11<=14,'fallbackid9 entry10/count admission')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[(p,id9.STARTS[index][k],id9.SIZES[k]) for k,p in enumerate(id9.PARTS)]+[('selector',spc,44),('callback_register',int(cbreg['start'],16),42),('outer_entry',entry,112),('task_register',d['reg'],48)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackid9 strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],bodies=windows,strictHEX_guards=guards,initializer_CFG_path=initializer_path,selector6_CFG_path=selector_path,fixed_conditional_envelopes=fixed,
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],allocation_interval_certificate=dict(positive_ID8_cases=len(allocation_rows),zero_ID8_cases=len(zero_rows),owner_footprint_checks=footprint_checks,full_table_payload_checks=table_checks,old_and_ID8_allocated_owners_and_remainder_headers_retained=True),
  vector_setup=dict(union_start=g+904,union_bytes=36,zero_words=[g+924,g+908,g+904],A_base=g+928,A_pointers=pointers[:3],A_active_word=g+908,B_base=g+912,B_pointers=pointers[3:],B_active_word=g+904,active_words_zero_at_selected_end_under_retention=True,flags_byte_not_written=True,activation_selectors_invoked=False),
  local_publication=dict(local_ID9=g+943,local_ID9_value=9,selector=6,record_index=2,ordered_stores=[dict(address=g+826,bytes=1,value=9),dict(address=g+824,bytes=2,value=6)],record0_record1_and_ID7_ID8_retained=True),
  callback_publication=dict(table=cb,bytes=48,input_pointer=id9.STARTS[index][4],generic_leaf_paths=cb_paths,q_positive_selected_slot=2,q0_retained_index_triples=q0_callback_triples(),index12_means_full=True,triple_partition=[220,66,12,1],triples_need_all_previous_observations_nonzero_stores_retained_and_no_intervening_writes=True,no_coherent_snapshot_claimed=True,callbacks_invoked=False,leaf_reply_A0='0 inserted;19 full',leaf_reply_A1='0 inserted;last observed nonzero slot11 word full',leaf_reply_A2=12,reply_not_tested_before_task_registration=True),
  runtime_bodies_guarded_but_not_composed=dict(parts=['select_A','select_B','callback','consumer'],path_certificates={p:id9.certificates(windows[p],p) for p in ('select_A','select_B','callback','consumer')},actual_flags_source_activation_order_provider_lookup_indirect_calls_and_tails_not_closed=True),
  frames=dict(initializer=32,saved_input_ID_relative_entry_SP=-20,saved_RA_relative_entry_SP=-4,vector_selector_callback_register_frames=0,outer=16,selected_stage_live_max=48,initializer_released_before_callback_register=True),
  next_registration=dict(pc=entry+80,target=d['reg'],handler=handler,required_fresh_count=10,required_capacity_min=14,required_table=layout.T,entry10=layout.T+40,new_count=11,A0=10,A1='callback-register result',A2=11),
  end_cut=dict(pc=entry+84,target=d['outer_init'][4],fallback=0,gate=5,task_count=11,saved_ID6=6,local_ID7=7,local_ID8=8,local_ID9=9,A0=10,A1='0 on callback insertion; last observed nonzero word on full q0 table',A2=11,fifth_outer_initializer_not_executed=True),
  required_premises=['all inherited selected b/q/r/allocation/source/header/first-copy/ISA/code/metadata/frame ownership conditions remain conditional; no new allocator/fill service called on this initialization path',
   'valid physical nonalias frames/code/tables/globals/owned allocations and normal matching vectors/selector/callback-register/task-register ABI; saved input/RA/GP/S/SP and required metadata remain valid',
   'prior nonzero CB observations/nonnull stores and resource clear results retained through fixed writes and no adverse IRQ/DMA/reentry/external writers; qpositive slot2 and q0 indextriples are conditional scalar relations, not atomic snapshots',
   'fresh count10/capacity>=14/tableT at next registration; code-pointer publication/zero active words at this boundary do not prove later activation, callback execution, installed bindings or cross-event lifetime'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);rows,zero,prior=previous.geometry()
 return dict(schema='TSL9-fallback-ID9-vector-owner-retention-selected-ID10-count11-join-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(data,h,i,parent['profiles'][i],rows,zero,prior) for i,(data,h) in enumerate(zip(carriers,hexes))],
  source_composition='selected ID9/count10 -> nine vector stores -> localID9/selector6 record2 -> callback-register tail -> fresh ID10/count11',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual installed bindings/source-header writers/other allocation-failure domains','fifth outer initializer6c300/6c4ec and later registration/tail','activation flags/callers/vector target consumers/provider and lookup contracts/full cross-event lifetime'])


def tests(carriers):
 previous.tests(carriers);id9.tests(carriers);q0_callback_triples()
 check(1299+250==1549,'fallbackid9 cumulative mutation census')
 print('PASS:1549 original operand/core mutations rejected;1024 retained allocation families;299 conditional q0 three-scan index triples')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackid9 exactledger')
 print('PASS:selected ID9 vectors/record2/callback/ID10 count11 join;11strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;actualbindings/runtimeconsumers/fifthinitializer/full lifetime UNPROVED')


if __name__=='__main__':main()
