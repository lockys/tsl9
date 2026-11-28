"""Offline third-pool geometry, getter retention and conditional parent return.

Original bytes/CFG, finite graph walks and immutable interval identities only.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_parent_static as previous
import check_v4160_id6_leaf_return_static as leaf

init,sparse,check=previous.init,previous.sparse,previous.check
outer,layout,closure=previous.outer,previous.layout,previous.closure
OUT=Path(__file__).with_name('v4160-b1-fallback-third-static.json')


def geometry():
 second,first=previous.geometry();resources=previous.previous.geometry();rows=[];S=layout.A+24
 for case,n in [('second',0)]+[('first_then_zero_second',v['first_count']) for v in first]:
  for resource,r in zip(resources,second):
   q=r['q'];small=q<=4;req=12*q;owners=[('resource_header',resource['free_header'],8),('resource_payload',resource['payload'],resource['request'])]
   if case=='second':
    owners += [('second_header',r['required_free_header'],8),('second_payload',r['payload'],r['request'])]
    H=r['new_remainder'] if q!=4 else S;size=r['new_remainder_size'] if q!=4 else 480;skips=2 if q<=3 else 1 if q==4 else 3
   else:
    f=first[n-1];owners += [('first_header',f['header'],8),('first_payload',f['payload'],f['request'])]
    H=f['new_remainder'] if small else resource['new_remainder_header'];size=f['new_remainder_size'] if small else resource['new_remainder_size'];skips=2
   P=H+8;N=P+req;remainder=size-req-8;end=layout.B if small else layout.E
   check(1<=q<=66 and req%4==0 and (req<=52)==small and 0<req<=792 and remainder>0,'fallbackthird request/arena/split')
   check(H%4==0 and size%4==0 and N+8+remainder==end,'fallbackthird exact free remainder end')
   writes=[(H,8),(N,8),(P,req)]
   for a,z in writes:
    for name,p,w in owners+[('first_table',layout.P,resource['first_table_payload_R'])]:check(previous.previous.separated(a,z,p,w),'fallbackthird prior owner survives '+name)
   rows.append(dict(case=case,first_count=n,q=q,capacity=resource['capacity'],request=req,tag=0x4c06,small=small,
    required_free_header=H,required_free_size=size,allocated_headers_to_skip=skips,payload=P,new_remainder=N,new_remainder_size=remainder,account_delta=-(req+8),
    write_intervals=writes,prior_owned_intervals=owners,first_table_payload=[layout.P,layout.P+resource['first_table_payload_R']],
    extra_fresh_timer_small_geometry_required=case=='second' and q==4))
 check(len(rows)==264 and len({(r['case'],r['first_count'],r['q']) for r in rows})==264,'fallbackthird geometry census')
 return rows


def profile(data,hexraw,index,parent,rows):
 G=0x20003000;delta=80*index;ip=outer.STARTS[index][0];F=G+492+delta;ctx=F-80;d=leaf.role.DETAILS[index];entry=d['entry'];CB=G+856+delta;qaddr=G+948+delta
 check(parent['end_cut']['pc']==ip+276 and parent['end_cut']['fallback']==0 and parent['end_cut']['task_count']==7,'fallbackthird inherited parent join')
 b=outer.body(init.binding.take(data,ip,386),'initializer',index);pn={v['pc']:v for v in b['instructions']};edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['normal_return_CFG'].items()}
 windows={p:leaf.body(init.binding.take(data,leaf.specs(p,index)[0],leaf.SIZES[k]),p,index) for k,p in enumerate(leaf.PARTS)}
 getter=windows['getter'];callback=windows['callback_register'];next_outer=windows['next_outer'];gpc=int(getter['start'],16);cpc=int(callback['start'],16)
 gn={v['pc']:v for v in getter['instructions']};cn={v['pc']:v for v in callback['instructions']};on={v['pc']:v for v in next_outer['instructions']}
 check(gn[gpc+4]['imm']+G==qaddr and [pn[ip+o]['target'] for o in (276,316)]==[gpc,gpc],'fallbackthird getter source and both call joins')
 check(pn[ip+280]['imm']==pn[ip+320]['imm']==12 and pn[ip+286]['imm']+pn[ip+288]['imm']==0x4c06,'fallbackthird size/tag operands')
 init.g(pn,ip+308,'fallbackthird returned pool store',op='store',rs1=15,rs2=10,imm=792+delta,width=4)
 check(pn[ip+304]['imm']==G and pn[ip+314]['target']==ip+338,'fallbackthird pointer source/null exit')
 check(pn[ip+338]['rd']==8 and pn[ip+340]['rd']==1 and pn[ip+340]['imm']==44 and pn[ip+358]['imm']==48,'fallbackthird restored S0/RA/frame')
 check(pn[ip+360]['rd']==0 and pn[ip+360]['target']==cpc and pn[ip+350]['imm']+pn[ip+354]['imm']==0x4d916+152*index,'fallbackthird unlinked callback-register tail')
 check(pn[ip+68]['rs2']==1 and pn[ip+68]['imm']==44,'fallbackthird saved caller RA')
 old=leaf.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in old['instructions']}
 check(en[entry+20]['target']==ip and en[entry+20]['rd']==1 and int(next_outer['start'],16)==entry+24,'fallbackthird parent normal return join')
 def walk(positive):
  result=outer.paths.chain(edges,ip+276,{ip+314:ip+(316 if positive else 338)},ip+360)
  check([a for a in map(lambda v:int(v,16)-ip,result) if a in (276,296,316,330)]==([276,296,316,330] if positive else [276,296]),'fallbackthird exact suffix call census')
  return result
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]
 protected += [('first_pool_pointer',G+784+delta,4),('second_pool_pointer',G-104+delta,4)]
 fixed=[dict(role=k,address=a,bytes=z) for k,a,z in [('third_pool_pointer',G+792+delta,4),('control',0x4002420c,4),('account',ctx+6,2)]]
 def exclude(a,z,skip=()):
  check(0<=a<a+z<=1<<32,'fallbackthird nonwrapping write')
  for name,p,w in protected:
   if name not in skip:check(previous.previous.separated(a,z,p,w),'fallbackthird write excludes '+name)
 for v in fixed:exclude(v['address'],v['bytes'])
 for r in rows:
  for a,z in r['write_intervals']:exclude(a,z)
  for v in fixed:
   for name,a,z in r['prior_owned_intervals']:check(previous.previous.separated(v['address'],v['bytes'],a,z),'fallbackthird fixed excludes owner '+name)
   p,e=r['first_table_payload'];check(previous.previous.separated(v['address'],v['bytes'],p,e-p),'fallbackthird fixed excludes table payload')
 # A zero request has no header/account/control effects, but still stores 0 in
 # the third pointer. The inherited first-small payloads remain owned as well.
 for r in previous.geometry()[1]:
  for a,z in ((r['header'],8),(r['payload'],r['request'])):check(previous.previous.separated(G+792+delta,4,a,z),'fallbackthird zero path preserves first pool')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackthird fill GPR/frame preservation')
 certs=[previous.core_certificate(data,index,s,k) for s,k in sorted({(r['small'],r['allocated_headers_to_skip']) for r in rows})]
 certs.append(previous.core_certificate(data,index,True,0,True))
 cases=leaf.path_certificates(callback)
 check(cn[cpc+4]['imm']+G==cn[cpc+10]['imm']+G==CB,'fallbackthird callback table base')
 for j in range(12):
  a=CB+4*j;check(CB<=a<a+4<=CB+48,'fallbackthird callback slot extent');exclude(a,4,('resource_callback_table',))
  for r in rows:
   for name,p,z in r['prior_owned_intervals']:check(previous.previous.separated(a,4,p,z),'fallbackthird callback store excludes owner '+name)
   p,e=r['first_table_payload'];check(previous.previous.separated(a,4,p,e-p),'fallbackthird callback excludes table payload')
 handler=0x46000+d['outer_lows'][1]
 check(on[entry+24]['imm']+on[entry+28]['imm']==handler and on[entry+32]['target']==d['reg'] and on[entry+36]['target']==d['outer_init'][1],'fallbackthird next task and initializer joins')
 reg=leaf.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackthird task registration preserves A1')
 entry7=layout.T+28
 for a,z in ((entry7,4),(ctx+1,1)):exclude(a,z,('task_count',))
 check(entry7+4<=layout.T+4*14 and 7<14 and 8<=14,'fallbackthird count7 admission and entry7 bounds')
 # Original resource tail is the source of CB zeroes in nonzero-q cases.
 rpc=outer.STARTS[index][1];rb=outer.body(init.binding.take(data,rpc,160),'resources',index);rn={v['pc']:v for v in rb['instructions']}
 check(rn[rpc+112]['imm']==48 and rn[rpc+108]['imm']+rn[rpc+118]['imm']==CB,'fallbackthird original resource 48-byte fill join')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 for name,a,z in [('parent',ip,386),('resources',rpc,160),('core',closure.core.DETAILS[index][0],208),('fill',fs,46),('outer_entry',entry,112),('task_register',d['reg'],48)]+[(p,leaf.specs(p,index)[0],leaf.SIZES[k]) for k,p in enumerate(leaf.PARTS)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackthird strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],strictHEX_guards=guards,leaf_bodies=windows,parent_suffix_paths=dict(positive_allocation=walk(True),zero_request=walk(False)),
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],fixed_conditional_envelopes=fixed,selected_core_certificates=certs,
  getter_retention=dict(address=qaddr,independent_fresh_loads=True,no_encoded_equality_check=True,selected_retained_q=[0,66],g1_equals_g2_only_under_premises=True,
   allocation_bytes='12*q',fill_bytes='12*q on positive allocation only',low16_no_truncation_for_all_U8=True,source_count_and_lowbits_excluded_from_all_selected_nonleaf_writes=True),
  selected_domains=dict(positive_geometry_cases=264,second_pool_cases=66,first_small_then_second_zero_cases=198,
   zero_request_cases=[dict(first_count=n,resource_q=0,third_reply=0,third_fill_called=False) for n in range(4)],
   positive_failure_cases_included=False,extra_q4_second_case_premise='fresh smallhead A allocated16/tagff03/nextS=A+24 and S free480/tag0/nextB'),
  callback_table=dict(base=CB,bytes=48,fresh_read_paths=cases,nonzero_resource_q_case=dict(prior_zero_fill_retained=True,selected_slot=0,published_pointer=0x4d916+152*index,A0_A1_A2=[0,0,12]),
   zero_resource_q_case='all13 fresh-read outcomes retained: insert at first observed zero0..11, or full after12 nonzero reads; no coherent snapshot presumed',callback_invoked=False),
  parent_return=dict(tail_pc=ip+360,target=cpc,RA_restored_from_SP44=True,parent_frame_released=48,normal_return_pc=entry+24,conditional_whole_selected_parent_path_closed=True),
  next_registration=dict(pc=entry+32,target=d['reg'],handler=handler,required_fresh_count=7,required_capacity_min=14,required_table=layout.T,entry7=entry7,new_count=8,reply_A0=7,reply_A2=8,A1='0 after insertion; last observed nonzero slot11 word on full q0 table',leaf_reply_not_tested=True),
  end_cut=dict(pc=entry+36,target=d['outer_init'][1],fallback=0,gate=5,task_count=8,saved_ID6=6,A0=7,A2=8,second_outer_initializer_not_executed=True),
  frames=dict(parent=48,core_child=16,selected_stage_live_max=64,parent_released_before_leaf=True,outer16B_frame_still_live=True),
  required_premises=['all inherited selected first/second/resource pool paths, matching original code/first-copy/core/fill and ABI, valid frame/metadata/owned payloads remain',
   'fresh q0..66 count retained from previous boundary; positive allocation uses exact listed fresh free header/next/sizes, preceding allocated headers and arena head; firstsmall n1..3 additionally uses inherited independent tag(-q)&255 condition',
   'positive third core follows fit/split without fallback; q0 follows early zero return; successful allocation and required fresh metadata/frame/table/counter reloads retained, no arbitrary null-failure/fallback domain proved',
   'actual fill does not retain pointers, matches local software fill; resource CB48 zero result retained for q>0; q0 CB contents remain unconstrained; all table/code/frame accesses physical nonalias',
   'no adverse MMIO/FENCE/IRQ/DMA/reentry/external writes or other side effects; leaf publication does not prove callback execution, asynchronous ordering, atomicity, actual installed binding or cross-event lifetime'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);rows=geometry();leaf.getter_domain()
 return dict(schema='TSL9-fallback-third-selected-getter-pool-parent-return-ID7-v1',APP_sha256=sha256(image).hexdigest(),third_pool_geometry_cases=rows,
  profiles=[profile(d,h,i,parent['profiles'][i],rows) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='inherited selected resource/first/second pools -> retained getter -> third4c06 pool or zero request -> parent callback-register tail normal RET -> taskID7/count8',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['other fresh count/tag/header/allocator-failure domains and actual bindings/ownership','second outer initializer46570/46608 and callback consumer flows','asynchronous effects/polling progress/full cross-event retention-consumption-release'])


def tests(carriers):
 previous.tests(carriers);leaf.tests(carriers);rows=geometry()
 for i,data in enumerate(carriers):
  for small,skips in sorted({(r['small'],r['allocated_headers_to_skip']) for r in rows}):previous.core_certificate(data,i,small,skips)
  previous.core_certificate(data,i,True,0,True)
 check({r['q'] for r in rows}==set(range(1,67)) and sum(r['small'] for r in rows)==16,'fallbackthird exact positive/small domain')
 print('PASS:548 original operand/core mutations rejected;264 third-pool geometries;26 callback CFG paths;4 zero-request domains per candidate')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackthird exactledger')
 print('PASS:selected getter/third4c06/parent-tail/ID7 count8 join;264geometrycases/strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;actualbindings/otherpaths/secondinitializer/full lifetime UNPROVED')


if __name__=='__main__':main()
