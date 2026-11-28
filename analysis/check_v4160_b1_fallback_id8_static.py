"""Offline correlated low2 allocation and selected ID8-to-ID9 return proof.

Original bytes/CFG and immutable integer, interval and frame certificates.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_id7_static as previous
import check_v4160_id8_initialization_static as id8

init,sparse,check=previous.init,previous.sparse,previous.check
third=previous.previous
layout=previous.layout
separated=previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-id8-static.json')
COLUMNS=['first_count','source_byte','q','low2_r','free_header','free_size','request','rounded','payload','new_remainder','new_remainder_size','allocated_headers_skipped','account_delta','used_layout_bytes']


def geometry():
 prior={(r['first_count'],r['q']):r for r in third.geometry()};resources={r['q']:r for r in third.previous.previous.geometry()};seconds={r['q']:r for r in third.previous.geometry()[0]};rows=[];zero=[]
 for n in range(4):
  for b in range(256):
   r=b&3;q=r+(b>>2)
   check(r<=q<=r+63 and q<=66 and (q==0)==(b==0),'fallbackid8 correlated source domain')
   if not r:zero.append([n,b,q]);continue
   t=prior[n,q];resource=resources[q]
   if not n and q==4:H,size,k=seconds[q]['new_remainder'],seconds[q]['new_remainder_size'],3
   elif q<=(3 if not n else 4):H,size,k=resource['new_remainder_header'],resource['new_remainder_size'],2
   else:H,size,k=t['new_remainder'],t['new_remainder_size'],4 if not n else 3
   request=194*r+6;R=(request+3)&~3;P=H+8;N=P+R;size2=size-R-8;used=190*r+6
   check(request in (200,394,588) and R in (200,396,588) and request>52 and size-R>8 and size2>0,'fallbackid8 large aligned fit/split')
   check(H%4==0 and N+8+size2==layout.E and used+4*r==request and used<=request<=R,'fallbackid8 exact split/layout/request bound')
   for j in range(r):
    record=P+184*j;check(P<=record<record+184<=P+184*r,'fallbackid8 record extent')
    for a,z in [(record,2)]+[(record+4+12*h,2) for h in range(15)]+[(record+12+12*h,4) for h in range(15)]:check(record<=a<a+z<=record+184,'fallbackid8 all inner record stores owned')
   Q=P+184*r
   for j in range(r+1):
    for o,z in ((0,2),(3,1),(2,1),(4,1)):check(P<=Q+6*j+o<Q+6*j+o+z<=P+used,'fallbackid8 all queue stores owned')
   check(Q+6*(r+1)==P+used<=P+request and Q+2<=P+used,'fallbackid8 end pointer/first queue overwrite extent')
   rows.append([n,b,q,r,H,size,request,R,P,N,size2,k,-(R+8),used])
 check(len(rows)==768 and len(zero)==256 and len({(a[0],a[1]) for a in rows}|{(a[0],a[1]) for a in zero})==1024,'fallbackid8 complete four-family source census')
 return rows,zero,prior


def q0_callback_pairs():
 # Scalar index theorem: if an earlier scan inserts a nonzero pointer at j,
 # all slots through j are nonzero under retained observations/store result.
 # A later first observed zero must be strictly later, or the scan is full.
 pairs=[[a,b] for a in range(12) for b in range(a+1,13)]+[[12,12]]
 check(len(pairs)==79 and all(1<=b<=12 and (a<b or a==b==12) for a,b in pairs),'fallbackid8 retained q0 callback index relation')
 return pairs


def resource_paths(body,rpc):
 e={int(p,16):[int(q,16) for q in qs] for p,qs in body['conditional_CFG'].items()};zero=id8.paths.chain(e,rpc,{rpc+50:rpc+184});result=[dict(r=0,path=zero)]
 prefix=[int(a,16) for a in id8.paths.chain(e,rpc,{rpc+50:rpc+52},rpc+124)][:-1]
 for r in range(1,4):
  walk=prefix[:]
  for _ in range(r):walk += [rpc+o for o in (124,236,240)]+[rpc+o for _ in range(15) for o in (244,248,252,254)]+[rpc+o for o in (258,260,264)]
  walk += [rpc+o for o in (124,128,132,136,138,140,142,144,148)]+[rpc+o for _ in range(r+1) for o in (150,152,154,156,160,162,164)]
  walk += [int(a,16) for a in id8.paths.chain(e,rpc+168,{})]
  check(all(b in e[a] for a,b in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackid8 finite resource graph walk')
  result.append(dict(r=r,path=[hex(p) for p in walk],record_repetitions=r,inner_repetitions=15,queue_repetitions=r+1,finite_graph_walk_not_target_execution=True))
 return result


def profile(data,hexraw,index,parent,rows,zero,prior):
 g=0x20003000+80*index;delta=80*index;F=g+492;ctx=F-80;d=id8.role.DETAILS[index];entry=d['entry'];pc,rpc=id8.STARTS[index][0],id8.STARTS[index][2]
 check(parent['end_cut']['pc']==entry+52 and parent['end_cut']['target']==pc and [parent['end_cut'][k] for k in ('fallback','gate','task_count','saved_ID6','local_ID7','A0','A1','A2')]==[0,5,9,6,7,8,5,9],'fallbackid8 exact inherited join')
 windows={p:id8.body(init.binding.take(data,id8.STARTS[index][k],id8.SIZES[k]),p,index) for k,p in enumerate(id8.PARTS)}
 selector=id8.previous.body(init.binding.take(data,0x4d9ec+152*index,44),'selector',index);callback=id8.leaves.body(init.binding.take(data,0x4efe2+152*index,42),'callback_register',index)
 sourcepc=id8.origin.STARTS[index][1];source=id8.origin.body(init.binding.take(data,sourcepc,160),'resources',index);sn={v['pc']:v for v in source['instructions']}
 check(sn[sourcepc+16]['imm']==3 and sn[sourcepc+26]['imm']==9 and sn[sourcepc+12]['imm']+sn[sourcepc+20]['imm']+9==g+949,'fallbackid8 retained original low2 address/formula')
 pn={v['pc']:v for v in windows['initializer']['instructions']};rn={v['pc']:v for v in windows['resources']['instructions']};on={v['pc']:v for v in windows['next_outer']['instructions']}
 check([rn[rpc+o]['imm'] for o in (14,88,114)]==[9,9,9] and rn[rpc+4]['imm']+rn[rpc+8]['imm']+9==g+949,'fallbackid8 all three independent fresh loads share source')
 check(pn[pc+10]['rd']==10 and pn[pc+10]['imm']==12 and pn[pc+34]['rs2']==10 and pn[pc+28]['imm']==4,'fallbackid8 saved ID8 and exact selector4')
 check(pn[pc+38]['target']==int(selector['start'],16) and pn[pc+44]['imm']==32 and pn[pc+46]['target']==rpc and pn[pc+46]['rd']==0,'fallbackid8 initializer frame release/resources tail')
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]+[('F94_word',F+94,2),('F96_outside_byte',F+96,1),('record1',g+812,3),('local_ID7',g+940,1),('entries0_to8',layout.T,36)]
 def exclude(a,z,skip=()):
  check(0<=a<a+z<=1<<32,'fallbackid8 nonwrapping footprint')
  for name,p,w in protected:
   if name not in skip:check(separated(a,z,p,w),'fallbackid8 footprint excludes '+name)
 fixed=[('clear',4,g-252,4),('clear',12,g-256,4),('initializer',16,g-148,4),('initializer',24,g-144,4),('initializer',34,g+941,1),('resources',38,g-116,4),('resources',42,g-112,4),('resources',46,g-128,4),('resources',100,g-116,4),('resources',144,g-112,4),('resources',180,g-128,4),('hook_A',4,g-144,4),('hook_B',4,g-252,4),('selector',32,g+802,1),('selector',34,g+800,2)]
 for part,o,a,z in fixed:
  body=selector if part=='selector' else windows[part];start=int(body['start'],16);nodes={v['pc']:v for v in body['instructions']};check(nodes[start+o]['op']=='store' and nodes[start+o]['width']==z,'fallbackid8 fixed original store link');exclude(a,z)
 for part in ('initializer','clear','hook_A','hook_B','resources'):
  body=windows[part];start=int(body['start'],16);actual={p-start for p,v in ((v['pc'],v) for v in body['instructions']) if v['op']=='store' and v['rs1']!=2};expected={o for k,o,a,z in fixed if k==part}
  check(actual-expected==({150,152,154,156,170,236,244,248} if part=='resources' else set()) and expected<=actual,'fallbackid8 fixed/dynamic nonframe store census '+part)
 fixed_core=[('control',0x4002420c,4),('account',ctx+6,2)]
 for _,a,z in fixed_core:exclude(a,z)
 table_checks=0
 for row in rows:
  n,b,q,r,H,size,request,R,P,N,size2,k,account,used=row;t=prior[n,q]
  owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request'])]
  before_leaf=[(a,z) for _,o,a,z in fixed]+[(a,z) for _,a,z in fixed_core]+[(H,8),(N,8),(P,request)]
  for a,z in before_leaf:
   exclude(a,z)
   for name,p,w in owners:check(separated(a,z,p,w),'fallbackid8 prior owner retained '+name)
   p,e=t['first_table_payload'];check(separated(a,z,p,e-p),'fallbackid8 first table payload retained before registration');table_checks+=1
   if H!=t['new_remainder']:check(separated(a,z,t['new_remainder'],8),'fallbackid8 unselected third remainder header retained')
  for j in range(12):
   for name,p,w in owners:check(separated(g+856+4*j,4,p,w),'fallbackid8 callback store excludes prior owner '+name)
  for name,p,w in owners:check(separated(layout.T+36,4,p,w),'fallbackid8 entry9 excludes prior owner '+name)
  for a,z in ((H,8),(N,8),(P,R)):check(separated(layout.T+36,4,a,z),'fallbackid8 entry9 excludes new allocation')
 for n,b,q in zero:
  owners=[]
  if q:
   t=prior[n,q];owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request']),('third_free_header',t['new_remainder'],8)]
  elif n:
   s=third.previous.geometry()[1][n-1];owners=[('first_header',s['header'],8),('first_payload',s['payload'],s['request']),('first_free_header',s['new_remainder'],8)]
  for _,o,a,z in fixed:
   for name,p,w in owners:check(separated(a,z,p,w),'fallbackid8 zero-branch owner retained '+name)
 # Callback scan is a separate intentional publication in CB48. All other
 # envelopes above exclude CB48; a repeated scan is not an atomic snapshot.
 cb_cases=id8.leaves.path_certificates(callback);cb=g+856;pointers=[0x4c000+low+152*index for low in (-1724,-1286,-1882)]
 check([rn[rpc+o]['imm']+rn[rpc+o+4]['imm'] for o in (184,196,208)]==pointers and all(p!=0 for p in pointers) and 0x4d916+152*index!=0,'fallbackid8 nonzero callback inputs')
 check([v['target'] for v in windows['resources']['calls']]==['0x20000040','0x2000039c',hex(id8.STARTS[index][3]),hex(id8.STARTS[index][4]),callback['start']],'fallbackid8 exact service/callback inventory')
 for j in range(12):exclude(cb+4*j,4,('resource_callback_table',))
 check(rn[rpc+230]['imm']==0 and rn[rpc+232]['imm']==32,'fallbackid8 unconditional reply0 and resources frame release')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=third.outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackid8 matching fill GPR/frame contract')
 core_certs=[third.previous.core_certificate(data,index,False,k) for k in sorted({r[11] for r in rows})]
 old=id8.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in old['instructions']};check(en[entry+52]['target']==pc and en[entry+52]['rd']==1 and id8.STARTS[index][5]==entry+56,'fallbackid8 parent/resources normal return join')
 check(on[entry+64]['target']==d['reg'] and on[entry+68]['target']==d['outer_init'][3],'fallbackid8 next registration/fourth initializer cut')
 handler=0x50000+d['outer_lows'][3];check(on[entry+56]['imm']+on[entry+60]['imm']==handler,'fallbackid8 next handler formation')
 reg=id8.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackid8 next registrar preserves A1')
 for a,z in ((layout.T+36,4),(ctx+1,1)):exclude(a,z,('task_count',))
 check(layout.T+40<=layout.T+4*14 and 9<14 and 10<=14,'fallbackid8 entry9/count admission')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[(p,id8.STARTS[index][k],id8.SIZES[k]) for k,p in enumerate(id8.PARTS)]+[('selector',int(selector['start'],16),44),('callback_register',int(callback['start'],16),42),('source_resources',sourcepc,160),('core',third.closure.core.DETAILS[index][0],208),('fill',fs,46),('outer_entry',entry,112),('task_register',d['reg'],48)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackid8 strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],bodies=windows,strictHEX_guards=guards,protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],fixed_conditional_envelopes=[dict(role=p,offset=o,address=a,bytes=z) for p,o,a,z in fixed],
  source_retention=dict(original_byte=F+21,q_address=g+948,low2_address=g+949,formula='r=b&3;q=r+(b>>2); for fixedr q=r..r+63',three_independent_fresh_loads=True,N1_equals_N2_equals_N3_only_under_retention_premises=True),
  selected_core_certificates=core_certs,resource_CFG_paths=resource_paths(windows['resources'],rpc),allocation_interval_certificate=dict(positive_cases=768,zero_cases=256,table_payload_exclusion_checks=table_checks,old_selected_free_header_intentionally_reused=True,allocated_prior_owners_preserved=True),
  deliberate_local_updates=dict(record0=[g+800,4,g+802,8],local_ID8=[g+941,8],prior_record1_and_ID7_retained=True,cleared_pointer_words=[g-116,g-112,g-128],new_pool_pointer=g-116,middle_pointer=g-112,end_pointer=g-128,hooks=[dict(address=g-144,pointer=pointers[0]),dict(address=g-252,pointer=pointers[1])]),
  callback_publication=dict(table=cb,bytes=48,generic_leaf_paths=cb_cases,prior_slot0_nonzero_pointer=0x4d916+152*index,new_pointer=pointers[2],q_positive_selected_slot=1,q0_retained_index_pairs=q0_callback_pairs(),q0_pair_index12_means_full=True,q0_pairs_require_all_prior_observations_store_and_no_intervening_writes=True,no_atomic_snapshot_claimed=True,callbacks_invoked=False,final_A0=0,A1='0 on insertion; last observed nonzero word on full',A2=12,leaf_reply_ignored=True),
  frames=dict(initializer=32,resource=32,resource_reuses_released_initializer_frame=True,core_child=16,outer=16,selected_stage_live_max=64,saved_input_ID_relative_initializer_entry_SP=-20,saved_RA_relative_entry_SP=-4),
  next_registration=dict(pc=entry+64,target=d['reg'],handler=handler,required_fresh_count=9,required_capacity_min=14,required_table=layout.T,entry9=layout.T+36,new_count=10,A0=9,A1='callback-register result',A2=10),
  end_cut=dict(pc=entry+68,target=d['outer_init'][3],fallback=0,gate=5,task_count=10,saved_ID6=6,local_ID7=7,local_ID8=8,A0=9,A1='0 on callback insertion; last observed nonzero word on full q0 table',A2=10,fourth_outer_initializer_not_executed=True),
  required_premises=['all inherited selected q/pool/source/frame/metadata/first-copy/ISA/code bindings and ownership remain conditional; same original b supplies both q andr, not independent domains',
   'r1..3 actual core follows matching selected large-list free/allocated headers, rounded fit/split and returns indicated nonnull P; no allocator null guard or arbitrary failure/fallback domain proved',
   'three fresh low2 loads retainr; actual matching software fill writes request194r+6 bytes, with no pointer retention; subsequent pointer/count reloads and all frames/GP/S/SP/RA retained and nonalias',
   'preexisting CB zero/nonzero observations and prior published nonzero pointer retained through no-adverse IRQ/DMA/reentry/external writes; qpositive slot1 and q0 monotonic index pairs are conditional scalar consequences, not coherent snapshots',
   'valid physical accesses/frames/owned allocations/control/code/tables and no adverse hardware effects; fresh count9/cap>=14/tableT at registration; no actual installed binding/callback invocation/cross-event lifetime claimed'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);rows,zero,prior=geometry()
 return dict(schema='TSL9-fallback-ID8-correlated-low2-pool-selected-ID9-count10-join-v1',APP_sha256=sha256(image).hexdigest(),allocation_case_columns=COLUMNS,allocation_cases=rows,zero_case_columns=['first_count','source_byte','q'],zero_cases=zero,
  profiles=[profile(data,h,i,parent['profiles'][i],rows,zero,prior) for i,(data,h) in enumerate(zip(carriers,hexes))],
  source_composition='retained correlated b/q/low2 -> ID8 record0 -> zero resources OR rounded large pool/fill/bounded recordqueue -> hooks/callback register -> ID9 count10',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual installed bindings/fresh source-header writers/other allocation-failure domains','fourth outer initializer50412/504ac and new callback consumers','physicaleffects/IRQprogress/full cross-event retention-consumption-release'])


def tests(carriers):
 previous.tests(carriers);id8.tests(carriers);rows,zero,prior=geometry();q0_callback_pairs()
 for i,data in enumerate(carriers):
  for k in sorted({r[11] for r in rows}):third.previous.core_certificate(data,i,False,k)
 check(len(rows)==768 and len(zero)==256 and 1059+240==1299,'fallbackid8 combined mutation/family census')
 print('PASS:1299 original operand/core mutations rejected;1024 correlated families=768positive/256zero;79 retained q0 callback index pairs')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackid8 exactledger')
 print('PASS:selected ID8 low2/core/fill/records/callback/ID9 count10 join;13strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;actualbindings/fourthinitializer/full lifetime UNPROVED')


if __name__=='__main__':main()
