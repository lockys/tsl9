"""Offline fallback zero source, local preservation and fresh-load call exclusion.

Original bytes/CFG/def-use and closed interval/scalar certificates only.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_q_release_static as previous
import check_v4160_n136_predicate_static as predicate
import check_v4160_config_buffer_source_static as appsource
import check_v4160_fallback_initialization_static as fallback

alloc=previous.previous
qret=alloc.previous
scanner=qret.previous
qsource=scanner.previous
rf=qsource.previous
provider=rf.previous
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-fallback-source-static.json')


def summary(b,guard):return dict(start=b['start'],bytes=b['bytes'],sha256=b['sha256'],instruction_count=len(b['instructions']),complete_guard=guard)


def app_proof(image,closure):
 b=appsource.app_contract(image[appsource.APP_PC-0x8000:appsource.APP_PC-0x8000+appsource.APP_SIZE]);n={d['pc']:d for d in b['instructions']}
 u=appsource.uid_contract(image[appsource.UID_PC-0x8000:appsource.UID_PC-0x8000+appsource.UID_SIZE])
 check(n[0x19a20]['imm']==64 and n[0x19a2e]['imm']==0 and n[0x19a36]['imm']==16,'fallbacksource APP64zero arguments')
 check(n[0x19a38]['op']=='call_indirect' and n[0x19aec]['op']=='call_indirect' and n[0x19aea]['imm']==16,'fallbacksource APPclear/configjoins')
 ss=[d for a,d in n.items() if 0x19a3a<=a<0x19aec and d['op']=='store' and d['rs1']==2]
 check(all(qret.separated(d['imm'],d['width'],68) for d in ss),'fallbacksource directstackstore excludesSP68word')
 check(b['UID_loop_destination_SP_offsets']==list(range(40,46)) and u['output_extent_bytes']==6 and u['encoded_GPR_writes']==[13,14,15],'fallbacksource UID extents/GPRs')
 check([a for a,d in n.items() if 0x19a38<a<0x19aec and d['op'] in ('jal','jalr','call_indirect')]==[0x19ab4],'fallbacksource onlyUID betweenAPPclearandconfig')
 check(16+52==68 and 16+48==64 and set(range(68,72)).isdisjoint(range(8,14)) and set(range(68,72)).isdisjoint(range(40,46)),'fallbacksource field/frame geometry')
 check(closure['combined_unique_code']==dict(bodies=14,bytes=1072,instructions=390,static_store_sites=79),'fallbacksource fullgetterclosure reused')
 c=closure['conditional_preservation'];check(c['all_callback_software_call_targets_resolved_in_bytes'] and c['maximum_nominal_stack_depth_from_callback_entry']==144,'fallbacksource gettersoftware/frameclosure')
 check(closure['memset']['callback_request']==dict(D='callback SP+32',V=0,N=32,all16_alignments_partition_checked=True),'fallbacksource getter32scratch extent')
 return dict(builder=summary(b,'check_v4160_config_buffer_source_static.py'),UID=summary(u,'check_v4160_config_buffer_source_static.py'),source_config_offset=[52,56],source_SP_offsets=[68,72],value_after_matched_clear_and_source_preservation=0,
  adjacent_hook_config_offset=[48,52],adjacent_hook_SP_offsets=[64,68],source_local_intervening_calls=[0x19ab4],getter_closure=dict(code=closure['combined_unique_code'],RAM_projection=c['RAM_write_projection'],maximum_depth=144,matching_frames_and_MMIO_effects_must_exclude_fallback=True))


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());fd=fallback.DETAILS[index];cfg,D,hoff,boff=fd[2],fd[5],fd[9],fd[10];slot=D+52
 check(slot==alloc.core.DETAILS[index][4] and slot!=D+48,'fallbacksource exactfield52/corefreshslot join')
 cr,n,e,defaults=fallback.config_contract(data,cfg,D,hoff,boff);check(sparse.captured(mem,cfg,228)==cr and sha256(cr).hexdigest()==fd[-1],'fallbacksource initializer strictHEX/fullidentity')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];helpers={}
 for role,target,z in (('predicate',0x200004bc,62),('fill',0x2000039c,46),('copy',0x20000332,58)):
  src=int(fc['source'],16)+target-int(fc['destination'],16);raw=init.binding.take(data,src,z)
  check(sparse.captured(mem,src,z)==raw,'fallbacksource helper strictHEX')
  if role=='predicate':
   b=predicate.body(raw,role,index);check(len(b['stores'])==3 and not b['calls'] and all(d['bytes']==4 for d in b['stores']),'fallbacksource validation onlycontrol stores')
   check({d['offset'] for d in b['stores']}=={8,28,54},'fallbacksource validation projectedcontrolstore sites')
  elif role=='fill':b=appsource.fill_contract(raw)
  else:b=qret.binding.callees.previous.copier.body(raw,role,target,18,init.binding.COPY_HASH)
  helpers[role]=dict(source=src,target=target,bytes=z,sha256=sha256(raw).hexdigest(),actual_mapping_proved=False)
 check(n[cfg+80]['imm']==n[cfg+98]['imm']==D-0x20003000 and n[cfg+74]['imm']==n[cfg+92]['imm']==64,'fallbacksource initializercopy64 exactD')
 for x in defaults:check(qret.separated(D+x['destination_field'],x['bytes'],slot),'fallbacksource defaults exclude52word')
 fixed_init=[dict(pc=cfg+192,address=0x20003000+hoff,bytes=2),dict(pc=cfg+202,address=0x20003000+boff,bytes=1)]
 check(all(qret.separated(x['address'],x['bytes'],slot) for x in fixed_init),'fallbacksource initializer latefixedstores exclude52word')
 check((n[cfg+182]['imm'],n[cfg+184]['target'],n[cfg+186]['rs1'])==(44,cfg+196,15),'fallbacksource initialgetter44 separatefallback52')
 # Reuse complete source mapping for field44; callback immediately replaces
 # inherited A0 with private scratch, and all software RAM effects are bounded.
 pb=provider.app_proofs(image)
 check(pb['getter_entry_A0_notobjectpointer'],'fallbacksource getter ignoresinheritedconfigpointer')
 cut=cfg+206;check(n[cut]['op']=='jal' and n[cut]['target']==cfg-320,'fallbacksource explicitpostconfig boundary')
 prefix=qsource.profile(data,hexraw,index);tail=qret.profile(data,hexraw,index)
 effects=list(prefix['conditional_projected_write_intervals'])+list(tail['projected_suffix_store_intervals'])
 pp=qsource.radio.DETAILS[index][0][0];pn=qsource.radio.decode(init.binding.take(data,pp,118),pp)
 early=[(a,d) for a,d in pn.items() if d['op']=='store' and d['rs1']!=2 and a<=pp+66]
 check([a-pp for a,d in early]==[4,12,28,40,52,66],'fallbacksource parentearly6stores')
 for a,d in early:
  check(d['rs1'] in (14,15),'fallbacksource earlyfixedGstorebase');effects.append(dict(role='parent_before_fourcell_establishment',pc=a,address=0x20003000+d['imm'],bytes=d['width']))
 check(len(effects)==233 and all(qret.separated(x['address'],x['bytes'],slot) for x in effects),'fallbacksource all233selectedRF effects excludefallback')
 caller_effects=tail['fixed_caller_writes']+tail['bulk_destinations']
 check(len(caller_effects)==15 and all(qret.separated(x['address'],x['bytes'],slot) for x in caller_effects),'fallbacksource role/config fixed andbulk exclusion')
 free=previous.profile(data,hexraw,index)
 check(all(qret.separated(x['address'],x['bytes'],slot) for x in free['fixed_write_intervals']),'fallbacksource freefixed exclusion')
 check(slot+4<qret.layout.A<qret.layout.E,'fallbacksource ownedarena excludesfallback')
 # An owned-header premise, rather than the Q-specific benign byte overlap
 # theorem, is required when transferring arbitrary fallback W through writes.
 for k in free['path_certificate']['cases'].values():
  for x in k['matched_suffix_effects']:
   if isinstance(x['address'],int):check(qret.separated(x['address'],x['bytes'],slot),'fallbacksource projectedfreefixed exclusion')
 core=alloc.core;src=core.DETAILS[index][0];raw=init.binding.take(data,src,208);check(sparse.captured(mem,src,208)==raw,'fallbacksource core strictHEX');cn,ce=alloc.guard(raw,index);entry=core.ENTRY
 before=core.reachable(ce,entry)&alloc.ancestors(ce,entry+84);store_offsets=[a-entry for a in sorted(before) if cn[a]['op']=='store']
 check(store_offsets==[2,8,14] and not any(cn[a]['op']=='call_indirect' for a in before),'fallbacksource beforefreshload only2frame/control stores')
 check((cn[entry+84]['op'],cn[entry+84]['rs1'],cn[entry+84]['imm'],cn[entry+84]['width'])==('load',14,slot-0x20003000,4),'fallbacksource exactfreshfullwordload')
 check(cn[entry+88]['op']=='beqz' and cn[entry+88]['rs1']==14 and cn[entry+88]['target']==entry+26,'fallbacksource zero skipsindirect')
 selected={a:([entry+26] if a==entry+88 else zs) for a,zs in ce.items()};seen=core.reachable(selected,entry)
 check(entry+96 not in seen,'fallbacksource zeroedge indirectcall exclusion')
 zero_suffix=core.reachable(ce,entry+26);check([a-entry for a in sorted(zero_suffix) if cn[a]['op']=='store']==[30] and cn[entry+34]['imm']==0,'fallbacksource zero failure reply/control only')
 inv=scanner.census(dict(enumerate(data,0x40000)),slot);full=scanner.census(mem,slot)
 check(not inv['overlapping_stores'] and not full['overlapping_stores'],'fallbacksource boundedliteralwriter inventories')
 reg=tail['registration'];check(qret.separated(reg['count_address'],1,slot),'fallbacksource registration fixedcount exclusion');check(all(qret.separated(reg['nominal_T']+4*j,4,slot) for j in range(255)),'fallbacksource nominaltable admittedword envelope')
 return dict(label=init.binding.PROFILES[index][0],fallback_slot=slot,config_destination=D,initializer=dict(start=cfg,bytes=228,sha256=sha256(cr).hexdigest(),copy_bytes=64,source_field=[52,56],helpers=helpers,default_stores=defaults,late_fixed_stores=fixed_init,postcopy_getter=cfg+186,conditional_zero_endpoint_before_postconfig_call=cut,postconfig_target=cfg-320,source_to_RFrole_gap_closed=False),
  RF_preservation=dict(selected_case_only=True,projected_effect_count=233,effect_certificate_sha256=sha256(json.dumps(effects,separators=(',',':')).encode()).hexdigest(),fixed_caller_effects=caller_effects,registration_count_address=reg['count_address'],registration_dynamic_store_must_exclude_fallback_separately_from_Q=True,nominal_table=reg['nominal_T'],nominal_table_envelope=reg['nominal_all_admitted_U8_store_envelope']),
  private_release_preservation='fixedstores exclude52word;matchedwrittenH/Jheaderintervals requirefallbackexclusion,withownedarena as sufficientpremise;Q-benign-valuelemma notsubstituted',
  core_fresh_load=dict(pc=entry+84,slot=slot,ancestor_store_offsets=store_offsets,conditional_zero_successor=entry+26,indirect_call_pc=entry+96,zero_at_entry_plus_protected_frame_and_control_implies_no_indirect_call=True,sentinel_zero_reply=0,fit_path_still_may_return_pointer=True,fit_return_slot_preservation_requires_header_exclusion=True,termination_notproved=True),
  bounded_writer_inventory=dict(binary=inv,full_sparse=full,not_all_writers=True),
  required_premises=['all matchingcode/ISA/helper/conditionalmapping andordinarymemory/access/frame/context assumptions','APP64zero fill andUID/validation/copy finishnormally;borrowedsource anddestination/frame ranges valid/stable/nonalias','getter14body softwareclosure matches;144B stackregion and32B scratch disjointfallback;MMIO/FENCEeffects/IRQs/DMA/reentry/otherwriters preserveprotectedRAM','copy-publication toselectedRFrole entry stillneeds postconfig/wrapper/param774/otherinterveningcall preservation;notproved here','selectedRF source/Qreturn branch andmemory-base projections hold;role registration dynamicword excludesfallback aswellasrequiredframe/code','privatefree/allocator writes ifpresent requireactualH/J/Nheader/global/frame/control effect exclusions;nominalarena isconditionalownershipgeometry','atcoreentry fallback0 pluspreloadframe/control physicalnonalias/noexternalwriters ensuresfresh0;doesnotproveallocation success orwholeboot'],
  actual_provider_fresh_slot_invariant_boot_order_or_full_lifetime_proved=False)


def domains():
 for slot in (0x20003220,0x20003270):
  bases=set()
  for j in range(255):
   for shift in range(-3,4):
    T=slot-4*j+shift;D=T+4*j;check(not qret.separated(D,4,slot),'fallbacksource dynamictable overlap preimage');bases.add(T)
  check(bases==set(range(slot-1019,slot+4)),'fallbacksource tablepreimage union')
 # A zero slot does not inherit the Q-specific no-split nonzero tag lemma:
 # tag 0x0049 at the slot start has a nonzero overlapping low byte.
 zero_lanes=alloc.lane_cases(0,73);at_zero=next(x for x in zero_lanes if x['tag_address_minus_Q']==0)
 check(at_zero['fresh_zero_tag_compatible'] and not at_zero['Q_lanes_unchanged_by_tag_store'],'fallbacksource zero-slot/tag73 distinction')
 print('PASS:two fallback registration preimage certificates;zero-slot/tag73 Q-lemma distinction')
 return dict(registration_indices=[0,254],overlap_T_union_formula='[slot-1019,slot+3]',Q_specific_tag73_value_lemma_not_generalized_to_fallback_zero=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 closure=provider.closure.derive(image,carriers,header)
 app=app_proof(image,closure);profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))]
 appinv=[scanner.census(dict(enumerate(image,0x8000)),p['fallback_slot']) for p in profiles]
 check(not any(x['overlapping_stores'] for x in appinv),'fallbacksource APP boundedinventory nohit')
 return dict(schema='TSL9-fallback-zero-source-local-RF-preservation-fresh-load-v1',APP_sha256=sha256(image).hexdigest(),APP_source=app,profiles=profiles,APP_bounded_writer_inventories=appinv,domains=domains(),new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,remaining=['postconfig/wrapper/param774 andotherpublication-to-RF boundaries','actualslot/provider/copy/physicalmapping/sourceandheadersnapshots','allwriters/reentry/IRQ/pollprogress/fullownership/notificationlifetime'])


def tests(image,carriers):
 source_raw=image[appsource.APP_PC-0x8000:appsource.APP_PC-0x8000+appsource.APP_SIZE];count=0
 for at in (0x19a20,0x19a2e,0x19a36,0x19a38,0x19aac,0x19ab4,0x19aca,0x19aea,0x19aec):
  n=appsource.cb.decode(source_raw,appsource.APP_PC);z=n[at]['size'];o=at-appsource.APP_PC;bad=bytearray(source_raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:appsource.app_contract(bad)
  except RuntimeError:pass
  else:raise RuntimeError('fallbacksource APPmutationescaped')
  count+=1
 for i,data in enumerate(carriers):
  src=alloc.core.DETAILS[i][0];raw=init.binding.take(data,src,208);n,_=alloc.guard(raw,i)
  for o in (14,84,88,96,98):
   z=n[alloc.core.ENTRY+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:alloc.guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbacksource coremutationescaped')
   count+=1
  fd=fallback.DETAILS[i];cfg,D,hoff,boff=fd[2],fd[5],fd[9],fd[10];raw=init.binding.take(data,cfg,228);n=fallback.decode(raw,cfg)
  for o in (74,80,92,98,102,182,186,192,202):
   z=n[cfg+o]['size'];bad=bytearray(data);p=cfg-0x40000+o;bad[p:p+z]=(int.from_bytes(bad[p:p+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:fallback.config_contract(bad,cfg,D,hoff,boff)
   except RuntimeError:pass
   else:raise RuntimeError('fallbacksource initializermutationescaped')
   count+=1
 check(count==37,'fallbacksource mutationcensus');print('PASS:37 APP source/initializer publication/getter/fresh-load/branch/call mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbacksource exactledger')
 print('PASS:fallback APPsource/getter/RFlocalpreservation/freshload zero-call-exclusion certificates;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork;publication-to-RF gap/actualbinding/lifetime UNPROVED')


if __name__=='__main__':main()
