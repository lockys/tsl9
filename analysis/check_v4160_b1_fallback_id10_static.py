"""Offline selected ID10 core/fill paths, ending before status or NV read.

Original-byte/CFG guards and immutable geometry, interval/frame certificates.
No target execution/emulation or mutable RAM/heap/provider/MMIO/NV model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_id9_static as previous
import check_v4160_id10_nv_initialization_static as id10

init,sparse,check=previous.init,previous.sparse,previous.check
id8=previous.previous
third=id8.third
layout,separated=previous.layout,previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-id10-static.json')


def families():
 rows,zero,prior=id8.geometry();by_source={};first=third.previous.geometry()[1]
 for row in rows:
  n,b,q,r,H,size,req,R,P,N,size2,k,account,used=row;t=prior[n,q]
  owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request']),('ID8_header',H,8),('ID8_payload',P,R)]
  headers=[('third_remainder_or_ID8_header',t['new_remainder'],8),('ID8_remainder',N,8)]
  a,e=t['first_table_payload'];by_source[n,b]=(q,t,owners,headers,e-a)
 q0R=next(v['rounded_payload'] for v in layout.facts() if v['input_byte']==0)
 for n,b,q in zero:
  if q:
   t=prior[n,q];owners=t['prior_owned_intervals']+[('third_header',t['required_free_header'],8),('third_payload',t['payload'],t['request'])];headers=[('third_remainder',t['new_remainder'],8)];a,e=t['first_table_payload'];size=e-a
  else:
   t=None;owners=[];headers=[];size=q0R
   if n:
    f=first[n-1];owners=[('first_header',f['header'],8),('first_payload',f['payload'],f['request'])];headers=[('first_remainder',f['new_remainder'],8)]
  by_source[n,b]=(q,t,owners,headers,size)
 check(len(by_source)==1024,'fallbackid10 inherited source-family census')
 return by_source,first


def small_geometry(n,q,t,first,m):
 S=layout.A+24
 if not n and (q==0 or q>=5):H,size,k=S,480,1
 elif q and q<=(3 if not n else 4):H,size,k=t['new_remainder'],t['new_remainder_size'],3
 elif not n:H,size,k=t['new_remainder'],t['new_remainder_size'],2
 else:f=first[n-1];H,size,k=f['new_remainder'],f['new_remainder_size'],2
 req=16*m;P=H+8;N=P+req;size2=size-req-8
 check(m in (1,2,3) and H%4==0 and req<=52 and size-req>8 and N+8+size2==layout.B,'fallbackid10 selected small fit/split')
 return dict(first_count=n,q_group=q if 1<=q<=4 else -1,nv_count=m,free_header=H,free_size=size,allocated_headers_skipped=k,request=req,tag=66,payload=P,new_remainder=N,new_remainder_size=size2,account_delta=-(req+8))


def allocation_paths(body,ap):
 e={int(p,16):[int(q,16) for q in qs] for p,qs in body['conditional_CFG'].items()};result=[dict(m=0,path=id10.paths.chain(e,ap,{ap+74:ap+114}),core_zero_early_return=True,F8_flag_written=False)]
 prefix=[int(a,16) for a in id10.paths.chain(e,ap,{ap+74:ap+76},cut=ap+92)][:-1]
 cycle=(92,94,392,396,400,402,406,408,412,416,420,422,426,428,430,434,438,442,444,448,450,454,458)
 suffix=[int(a,16) for a in id10.paths.chain(e,ap+114,{})]
 for m in range(1,4):
  for flagzero in (False,True):
   walk=prefix+[ap+o for _ in range(m) for o in cycle]+[ap+o for o in (92,94,98,102,106)]+[ap+o for o in ((460,464,468) if flagzero else (110,))]+suffix
   check(all(b in e[a] for a,b in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackid10 finite allocation CFG walk')
   result.append(dict(m=m,F8_word_zero=flagzero,F8_flag_value=128 if flagzero else 0,path=[hex(p) for p in walk],record_repetitions=m,finite_graph_walk_not_target_execution=True))
 check(len(result)==7,'fallbackid10 allocation-path census')
 return result


def profile(data,hexraw,index,parent,by_source,first):
 g=0x20003000+80*index;delta=80*index;F=g+492;ctx=F-80;d=id10.role.DETAILS[index];entry=d['entry'];pc,ap,lp,wp,op=id10.STARTS[index]
 check(parent['end_cut']['pc']==entry+84 and parent['end_cut']['target']==pc and [parent['end_cut'][k] for k in ('fallback','gate','task_count','saved_ID6','local_ID7','local_ID8','local_ID9','A0','A2')]==[0,5,11,6,7,8,9,10,11],'fallbackid10 inherited ID10/count11 join')
 windows={p:id10.body(init.binding.take(data,id10.STARTS[index][k],id10.SIZES[k]),p,index) for k,p in enumerate(id10.PARTS)}
 pn={v['pc']:v for v in windows['initializer']['instructions']};an={v['pc']:v for v in windows['allocate']['instructions']};ln={v['pc']:v for v in windows['load']['instructions']}
 check(an[ap+10]['imm']+an[ap+28]['imm']==F and an[ap+32]['imm']==14 and an[ap+46]['imm']==66,'fallbackid10 fresh source F14/tag66')
 check([v['target'] for v in windows['allocate']['calls']]==['0x20000040']+['0x2000039c']*4,'fallbackid10 matching core/fill inventory')
 check(pn[pc+10]['rd']==10 and pn[pc+10]['imm']==12 and pn[pc+18]['rs2']==10 and pn[pc+18]['imm']==-62+delta,'fallbackid10 saved inputID10 reload/publication')
 check(pn[pc+12]['rd']==1 and pn[pc+12]['imm']==28 and pn[pc+22]['imm']==32 and pn[pc+24]['rd']==0 and pn[pc+24]['target']==lp,'fallbackid10 wrapper frame release/load tail')
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]+[('ID9_vector36',g+904,36),('local_ID9',g+943,1),('record2',g+824,3),('entries0_to10',layout.T,44)]
 def exclude(a,z):
  check(0<=a<a+z<=1<<32,'fallbackid10 nonwrapping envelope')
  for name,p,w in protected:check(separated(a,z,p,w),'fallbackid10 envelope excludes '+name)
 rows=id10.interval_rows(index)
 check({ap+o for o,a,z in rows}=={p for p,v in an.items() if v['op']=='store' and v['rs1']!=2 and p not in (ap+450,ap+454)},'fallbackid10 complete fixed allocation store census')
 fixed=[dict(role='allocate',offset=o,address=a,bytes=z) for o,a,z in rows]+[dict(role='wrapper_ID10',offset=18,address=g-62,bytes=1)]
 fills=[dict(role='common_fill16',address=g+off,bytes=16) for off in (380,364)]
 for v in fixed+fills:exclude(v['address'],v['bytes'])
 for o in (170,250):check(windows['allocate']['calls'][1 if o==170 else 2]['target']=='0x2000039c','fallbackid10 common fill target')
 check(an[ap+162]['imm']+an[ap+142]['imm']==g+380 and an[ap+242]['imm']+an[ap+222]['imm']==g+364 and an[ap+154]['imm']==an[ap+234]['imm']==16,'fallbackid10 common fill16 exact extents')
 common=[(v['address'],v['bytes']) for v in fixed+fills];core_fixed=[(0x4002420c,4),(ctx+6,2)]
 for a,z in core_fixed:exclude(a,z)
 groups={};owner_pair_checks=0;positive_cases=0
 for (n,b),(q,t,owners,headers,table_size) in by_source.items():
  # Source0 takes the unconditional core zero-request return and no heap writes.
  for a,z in common:
   for name,p,w in owners+headers:check(separated(a,z,p,w),'fallbackid10 zero-case retained owner/header '+name)
   check(separated(a,z,layout.P,table_size),'fallbackid10 zero-case full table payload')
  for m in range(1,4):
   r=small_geometry(n,q,t,first,m);H=r['free_header'];P=r['payload'];N=r['new_remainder'];req=r['request']
   # A selected old free header is deliberately reused; allocated owners and
   # every other carried header must remain disjoint from all new writes.
   kept=owners+[(name,a,z) for name,a,z in headers if a!=H]
   effects=common+core_fixed+[(H,8),(N,8)]+[(P+16*j+o,z) for j in range(m) for o,z in ((0,6),(6,6),(12,2),(14,1))]
   for a,z in effects:
    exclude(a,z)
    for name,p,w in kept:check(separated(a,z,p,w),'fallbackid10 positive-case retained owner/header '+name);owner_pair_checks+=1
    check(separated(a,z,layout.P,table_size),'fallbackid10 positive-case full table payload')
   for j in range(m):check(P<=P+16*j<P+16*j+15<P+req+1,'fallbackid10 record stores remain owned; byte15 untouched')
   key=(n,r['q_group'],m);check(key not in groups or groups[key]==r,'fallbackid10 small geometry group agreement');groups[key]=r;positive_cases+=1
 check(positive_cases==3072 and len(groups)==60,'fallbackid10 positive family/group census')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=third.outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackid10 software fill preserves required S/frame')
 certs=[third.previous.core_certificate(data,index,True,k) for k in sorted({v['allocated_headers_skipped'] for v in groups.values()})]+[third.previous.core_certificate(data,index,True,0,True)]
 le={int(p,16):[int(q,16) for q in qs] for p,qs in windows['load']['conditional_CFG'].items()}
 loader0=id10.paths.chain(le,lp,{lp+32:lp+36},cut=lp+36);loader_positive=id10.paths.chain(le,lp,{lp+32:lp+88},cut=lp+112)
 check(ln[lp+36]['target']==0x6af88+484*index and ln[lp+112]['target']==0x440c2+148*index,'fallbackid10 first status/NVread service cuts')
 check(ln[lp+108]['imm']==512 and ln[lp+104]['imm']==16 and ln[lp+96]['rd']==12,'fallbackid10 first read index0 arguments512/16/freshP')
 old=id10.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in old['instructions']};check(en[entry+84]['target']==pc and en[entry+84]['rd']==1,'fallbackid10 original outer savedRA')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[(p,id10.STARTS[index][k],id10.SIZES[k]) for k,p in enumerate(id10.PARTS)]+[('core',third.closure.core.DETAILS[index][0],208),('fill',fs,46),('outer_entry',entry,112)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackid10 strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],bodies=windows,strictHEX_guards=guards,fixed_conditional_envelopes=fixed,common_fill_envelopes=fills,protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],
  source_count=dict(address=F+14,selected_domain=[0,3],positive_second_config_and_loop_count_reload_equal_only_under_retention=True,pool_reload_sameP_only_under_retention=True),
  selected_small_geometry_groups=[groups[k] for k in sorted(groups)],interval_certificate=dict(inherited_source_families=1024,nv_count_zero_cases=1024,nv_count_positive_cases=3072,small_geometry_groups=60,owner_pair_checks=owner_pair_checks,all_old_allocated_owners_and_unselected_headers_preserved=True,selected_free_header_reuse_intentional=True),
  selected_core_certificates=certs,allocation_CFG_paths=allocation_paths(windows['allocate'],ap),
  local_state=dict(pool_word=g-68,count_byte=g-63,limit_byte=g-70,ID_byte=g-62,transient_ID_value=255,wrapper_final_ID_value=10,source0_pool0_count0_not_allocation_success=True,positive_records='each16B: fillFF6 at0 and6;SH0 at12;SB0 at14;byte15 not initialized',positive_F8_status=dict(source_word=F+8,destination_byte=g+1443,source_zero=128,source_nonzero=0),zero_request_does_not_update_F8_status=True),
  end_cuts=dict(source0=dict(pc=lp+36,target=0x6af88+484*index,kind='before_first_status_call',loader_prefix_CFG=loader0,pool_word_value=0,count=0,task_count=11,local_ID10=10,fallback=0,gate=5),source1_to3=dict(pc=lp+112,target=0x440c2+148*index,kind='before_first_NV_read',loader_prefix_CFG=loader_positive,A0=512,A1=16,A2='retained nonnull P from selected allocation',count='m1..3',task_count=11,local_ID10=10,fallback=0,gate=5)),
  frames=dict(outer=16,wrapper=32,allocate=32,core_child=16,stage_live_max=96,loader=32,live_at_both_cuts=48,loader_reuses_released_wrapper_frame=True),
  status_NV_optional_save_bodies_not_composed=True,next_ID11_count12_not_claimed=True,required_premises=['all inherited b/q/r/pool/CB/vector/source/metadata/frame/first-copy/ISA conditions remain conditional; selected fresh NV countm0..3 is an additional independent premise, not actualboot setting',
   'mpositive requires fresh smallheadA allocated16/tagff03/nextS=A24 plus matching chain of first/second/third allocated headers and exact selected remainder; extra freshA premise applies even where previous path used onlylargearena',
   'selected matching core0 earlyreturn OR mpositive smallfit/split returns valid owned nonnull P; fallback-slot load/callback is not on these selected core paths; no arbitrary failure/header/m4..255 domain closed',
   'F14/count/pool reloads retainm/P, matching local software fill returns through correct RA with no pointer retention and required S/GP/SP/frame preservation; all physical accesses/owned allocations/globals/frames/code/tables nonalias and no adverse IRQ/DMA/reentry/externalwriters',
   'status/NVread/optional/write services are not executed or assumed to return here; source0 still reaches status and save later, positive path still requires actual NV outcomes/borrowed-buffer contracts before a full initializer/ID11 return'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);by_source,first=families()
 return dict(schema='TSL9-fallback-ID10-selected-small-core-fill-before-status-NVread-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(data,h,i,parent['profiles'][i],by_source,first) for i,(data,h) in enumerate(zip(carriers,hexes))],stack_encoding=id10.stack_encoding_source(),
  source_composition='selected ID10/count11 -> core0 OR smallm1..3/records/commonfills -> wrapperID10 -> loader first status OR NVread cut',C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual installed binding/source writers/other counts and allocation-failure domains','status6af88/6b16c,NVread440c2/44156,optional andsave/write contracts beforefullreturn','sixth outerinitializer/tail,provider effects/borrowed buffer/full cross-event lifetime'])


def tests(carriers):
 previous.tests(carriers);id10.tests(carriers);by_source,first=families();groups=set()
 for (n,b),(q,t,owners,headers,size) in by_source.items():
  for m in range(1,4):r=small_geometry(n,q,t,first,m);groups.add((n,r['q_group'],m))
 check(len(groups)==60 and 1549+454==2003,'fallbackid10 geometry/mutation composition census')
 print('PASS:2003 original operand/core mutations rejected;1024 zero+3072 positive NV-count families;60 small-geometry groups;first-service cuts only')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackid10 exactledger')
 print('PASS:selected ID10 core/fill/wrapper/loader tofirststatus-or-NVread;8strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,NV or targetnetwork;fullNVreturn/ID11/bindings/lifetime UNPROVED')


if __name__=='__main__':main()
