"""Offline selected parent 4c04/4c05 pools and first-getter boundary.

Original bytes/CFG and closed pool/header/record interval certificates only.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_outer_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
outer,layout,closure=previous.outer,previous.layout,previous.closure
OUT=Path(__file__).with_name('v4160-b1-fallback-parent-static.json')


def geometry():
 rows=[];S=layout.A+24
 for r in previous.geometry():
  q=r['q'];req=16*q;small=q<=3
  H=S if small else r['new_remainder_header'];size=480 if small else r['new_remainder_size'];P=H+8;N=P+req
  check(0<req<=1056 and req%4==0 and (req<=52)==small and size-req>8,'fallbackparent second-pool size/arena choice')
  check(N+8+size-req-8==(layout.B if small else layout.E),'fallbackparent exact second-pool remainder end')
  check(all(P<=P+16*j+9<P+16*j+10<=P+req for j in range(q)),'fallbackparent every byte9 record within second payload')
  check(previous.separated(H,8,r['free_header'],8) and previous.separated(P,req,r['payload'],r['request']),'fallbackparent distinct priorresource allocation')
  check(previous.separated(H,8,layout.P,r['first_table_payload_R']) and previous.separated(P,req,layout.P,r['first_table_payload_R']),'fallbackparent table payload survives second allocation')
  rows.append(dict(q=q,capacity=r['capacity'],request=req,tag=0x4c05,small=small,required_free_header=H,required_free_size=size,payload=P,new_remainder=N,new_remainder_size=size-req-8,account_delta=-(req+8),allocated_headers_to_skip=1 if small else 2,prior_resource_header=r['free_header'],prior_resource_payload=[r['payload'],r['payload']+r['request']],first_table_payload=[layout.P,layout.P+r['first_table_payload_R']],write_intervals=[(H,8),(N,8),(P,req)],record_count=q,stride=16,record_byte_offset=9,record_byte_value=255))
 small_rows=[dict(first_count=n,request=16*n,tag=0x4c04,header=S,payload=S+8,new_remainder=S+8+16*n,new_remainder_size=480-16*n-8,account_delta=-(16*n+8)) for n in range(1,4)]
 check(len(rows)==66 and len(small_rows)==3,'fallbackparent geometry census')
 return rows,small_rows


def core_certificate(data,index,small,skips,zero=False):
 n,e=closure.core_body(init.binding.take(data,closure.core.DETAILS[index][0],208),index);pc=closure.core.ENTRY
 if zero:walk=[0,2,4,8,10,14,18,22,26,30,34,36,196,198,200,202]
 else:
  walk=[0,2,4,8,10,14,18,22,24,38,42,44,46,48,50,52,56]+([60,64] if small else [100,104,108])+[68,72]
  walk += [o for _ in range(skips) for o in (76,110,112,204,206)]
  walk += [76,110,112,114,116,120,124,128,130,134,138,142,146,150,152,154,156,158,162,166,168,170,174,176,178,180,182,186,188,192,196,198,200,202]
 for a,z in zip(walk,walk[1:]):check(pc+z in e[pc+a],'fallbackparent finite core graph edge')
 check(not e[pc+walk[-1]] and 84 not in walk and 96 not in walk and not any(n[pc+o]['op'] in ('jal','jalr','call_indirect') for o in walk),'fallbackparent no failure-slot or callee on selected core path')
 return dict(request_zero=zero,small=None if zero else small,allocated_headers_skipped=0 if zero else skips,offsets=walk,graph_certificate_not_target_execution=True)


def profile(data,hexraw,index,parent,rows,small_rows):
 G=0x20003000;delta=80*index;ip=outer.STARTS[index][0];F=G+492+delta;ctx=F-80;slot=parent['fallback_slot'];B=0x200033b8+delta
 check(parent['end_cut']['pc']==ip+126 and parent['end_cut']['target']==0x2000039c and parent['end_cut']['fallback']==0 and parent['end_cut']['saved_ID_byte_value']==6,'fallbackparent prior fillcut/zero/ID6 join')
 b=outer.body(init.binding.take(data,ip,386),'initializer',index);n={v['pc']:v for v in b['instructions']};e={int(p,16):[int(q,16) for q in qs] for p,qs in b['normal_return_CFG'].items()}
 for off in (134,178,186,210,214,246,264):
  v=n[ip+off]
  if v['size']==4:check(int.from_bytes(bytes.fromhex(v['bytes']),'little')>>12&7==4,'fallbackparent unsigned fresh count/tag load')
 check(n[ip+228]['imm']==0 and n[ip+240]['imm']==0 and n[ip+366]['imm']==0,'fallbackparent combined-count/pool/record store operands')
 # Parent paths are original CFG prefixes, with callees only as conditional
 # normal-return edges. The record loop's finite q bound is integer algebra.
 def path(choices):return outer.paths.chain(e,ip+130,{ip+a:ip+z for a,z in choices.items()},ip+276)
 zero_path=path({150:206,244:376})
 success_prefix=outer.paths.chain(e,ip+130,{ip+150:ip+206,ip+244:ip+246},ip+272)
 loop=(272,364,366,368,372,374)
 for q in range(1,67):
  walk=[int(a,16) for a in success_prefix[:-1]]+[ip+o for _ in range(q) for o in loop]+[ip+272,ip+276]
  check(all(z in e[a] for a,z in zip(walk,walk[1:])),'fallbackparent finite record CFG walk')
 first_success_second_zero=path({150:152,176:178,244:376})
 check(ip+164 not in map(lambda a:int(a,16),zero_path) and ip+236 in map(lambda a:int(a,16),zero_path),'fallbackparent zero firstcount still reaches second core call')
 check(n[ip+272]['op']=='bne' and n[ip+364]['imm']==1 and n[ip+368]['imm']==255 and n[ip+372]['imm']==16 and n[ip+374]['target']==ip+272,'fallbackparent byte counter/stride graph ranking operands')
 protected=[('fallback',slot,4),('F96',F,96),('role_object',B,296),('task_count',ctx+1,1),('capacity',ctx+2,1),('gate',ctx+3,1),('table_pointer',ctx+40,4),('entries0_to6',layout.T,28),('timer_head',ctx+76,4),('timer_node',layout.A+8,16),('timer_header',layout.A,8),('large_table_header',layout.B,8),('task0',0x20004184,1),('task1',0x200040a6,1),('saved_ID6',G+788+delta,1),('resource_counts',G+948+delta,2),('resource_pool_pointer',G+852+delta,4),('resource_callback_table',G+856+delta,48)]
 fixed=[dict(role=k,address=a,bytes=z) for k,a,z in [('parent_fill48',G+800+delta,48),('control',0x4002420c,4),('account',ctx+6,2),('first_pool_pointer',G+784+delta,4),('first_count',G-93+delta,1),('local_tag',G-95+delta,1),('combined_count',G-96+delta,1),('second_pool_pointer',G-104+delta,4)]]
 def exclude(a,z):
  check(0<=a<a+z<=1<<32,'fallbackparent nonwrapping footprint')
  for name,p,w in protected:check(previous.separated(a,z,p,w),'fallbackparent footprint excludes '+name)
 for v in fixed:exclude(v['address'],v['bytes'])
 for r in rows:
  for a,z in r['write_intervals']:
   exclude(a,z)
   check(previous.separated(a,z,r['prior_resource_header'],8) and previous.separated(a,z,r['prior_resource_payload'][0],r['prior_resource_payload'][1]-r['prior_resource_payload'][0]),'fallbackparent second pool preserves prior resource owner')
   check(previous.separated(a,z,r['first_table_payload'][0],r['first_table_payload'][1]-r['first_table_payload'][0]),'fallbackparent second pool preserves full first-table payload')
 for r in small_rows:
  for a,z in ((r['header'],8),(r['new_remainder'],8),(r['payload'],r['request'])):exclude(a,z);check(a+z<=layout.B,'fallbackparent first small pool below large arena')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackparent fill preserves S/frame')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 for k,a,z in [('parent',ip,386),('core',closure.core.DETAILS[index][0],208),('fill',fs,46)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackparent strictHEX '+k);guards.append(dict(role=k,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 certs=[core_certificate(data,index,True,1),core_certificate(data,index,False,2),core_certificate(data,index,True,0,True)]
 return dict(label=parent['label'],fallback_slot=slot,strictHEX_guards=guards,protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],fixed_conditional_envelopes=fixed,selected_core_certificates=certs,
  zero_case=dict(fresh_first_count=0,resource_q=0,required_local_byte=0,first_allocator_called=False,second_allocator_request=0,second_allocator_tag=0x4c05,second_allocator_reply=0,failure_callback_called=False,record_writes=0,cleared_local_bytes=[G-96+delta,G-95+delta],first_pool_pointer_not_cleared_by_skipped_branch=True),
  second_success_case=dict(fresh_first_count=0,resource_q_domain=[1,66],required_local_byte=0,combined_count='q',request='16*q',tag=0x4c05,first_allocator_called=False,geometry_cases='second_pool_geometry_cases',required_reloads=['fresh fill count and record count == q','fresh second pointer == returned P'],record_stride=16,record_byte_offset=9,record_byte_value=255,record_CFG_certificate=dict(prefix=success_prefix,loop_offsets=loop,repetitions=[1,66],exit_offsets=[272,276],finite_graph_walk_not_execution=True),first_pool_pointer_not_cleared_by_skipped_branch=True),
  first_small_success_second_zero=dict(fresh_first_count_domain=[1,3],tag=0x4c04,first_geometry_cases='first_small_geometry_cases',resource_q_domain=[0,66],required_fresh_tag_byte='(-q) & 255',combined_count=0,required_first_fill_count_equals_entry_count=True,second_allocator_called_with_size0=True,second_reply=0,second_record_writes=0,first_pool_remains_allocated=True),
  end_cut=dict(pc=ip+276,target=0x4efd8+152*index,fallback=0,gate=5,task_count=7,saved_ID_byte=6,parent48Bframe_live=True,getter_not_executed=True),
  frames=dict(parent=48,core_child=16,selected_live_max=64,valid_ownership_nonalias_savedwords_is_premise=True),
  required_premises=['all previous selected retry/outer resource zero OR success/source/header conditions remain; actual matching core/fill/ISA/firstcopy and valid frames/metadata/code','parentfill48 normal completion clearsG800..G848 but not fresh countG848 or tagG849; selected initial count0 OR1..3 and independent tag conditions are extra fresh premises, not actualbootreachability','second-success q1..66 inherits previous successful resource geometry/capacity14+3*q, with prior resource headers/payload intact and free remainder as specified; q<=3 additionally fresh timer A allocated16/tagff03/nextS=A24, freeS size480/tag0/nextB and smallheadA','first-small case similarly requires fresh A/S small geometry; resourceq0..66 held, later tag chosen(-q)&255 so second combinedcount0; first allocation/count-fill reloads remain compatible and payloadowned','positive allocations return indicated nonnull P; fresh fill/record counts and pointer reloads staywithinactualowned extent; no generic nullfailure or arbitraryheader search case included','all selected core walks fit/split or request0 earlyreturn, no sentinel fallback load/callback; zero request earlyreturn is not allocation success; valid nonwrappingnonalias frames/heap/globals/table/control and no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriters'],
  boundary='before first fresh getter4efd8/4f070; third4c06 allocation/fill/parent tail and laterregistrationIDs remain unclosed',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);rows,small=geometry()
 return dict(schema='TSL9-fallback-parent-selected4c04-4c05-firstgetter-boundary-v1',APP_sha256=sha256(image).hexdigest(),second_pool_geometry_cases=rows,first_small_geometry_cases=small,profiles=[profile(d,h,i,parent['profiles'][i],rows,small) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='parentfill48 -> firstcount0 plus second0/validq pool OR firstsmallfit withsecondcombined0 -> beforegetter withfallback0',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['other first-count/tag/allocatorfailure/heap domains and actualfreshsource/header/ownership','firstgetter/third4c06allocation/fill/parenttail/nextregistrationIDs','physicaleffects/IRQprogress/actualproviders/fullretention-consumption-release'])


def tests(carriers):
 outer.tests(carriers);rows,small=geometry();mutations=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,closure.core.DETAILS[i][0],208);n,_=closure.core_body(raw,i)
  for p,d in n.items():
   o=p-closure.core.ENTRY;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(128 if d['op']=='fence.i' else 4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:closure.core_body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackparent core mutationescaped')
   mutations+=1
  for s,k,z in ((True,1,False),(False,2,False),(True,0,True)):core_certificate(data,i,s,k,z)
 check(mutations==144,'fallbackparent core mutation census '+str(mutations))
 for q in range(67):check((q+((-q)&255))&255==0,'fallbackparent second zero combination')
 print('PASS:500 original parent/resource/core mutations rejected;66second-pool/3first-small geometries;zero-request vs fallback CFG;record and modulo-count certificates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackparent exactledger')
 print('PASS:selected parentfill/4c04-4c05/record paths preservefallback0 tofirstgetter;69geometrycases/strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;otherpaths/getter/thirdpool/actualbinding/full lifetime UNPROVED')


if __name__=='__main__':main()
