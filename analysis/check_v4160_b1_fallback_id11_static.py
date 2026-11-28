"""Offline selected final initializer and outer gate return certificates.

Original bytes/CFG and immutable interval/scalar/frame proofs only.
No target execution/emulation or mutable RAM/heap/provider/MMIO/NV model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_writer_static as previous
import check_v4160_id11_outer_tail_static as id11
import check_v4160_b1_fallback_source_static as source

init,sparse,check=previous.init,previous.sparse,previous.check
layout,separated=previous.layout,previous.separated
prefix=previous.previous.previous
nv=previous.previous.nv
OUT=Path(__file__).with_name('v4160-b1-fallback-id11-static.json')


def callback_quads():
 triples=prefix.previous.q0_callback_triples();rows=[[a,b,c,d] for a,b,c in triples for d in (range(c+1,13) if c<12 else [12])]
 check(len(rows)==794 and len({tuple(r) for r in rows})==794,'fallbackid11 callback four-scan census')
 check(all(all(x<y or x==y==12 for x,y in zip(r,r[1:])) for r in rows),'fallbackid11 callback monotonic/full relation')
 check([sum(sum(x<12 for x in r)==n for r in rows) for n in (4,3,2,1,0)]==[495,220,66,12,1],'fallbackid11 callback partition')
 return rows


def pool_paths(body,pc):
 e={int(p,16):[int(q,16) for q in qs] for p,qs in body['conditional_CFG'].items()};result=[]
 for r in range(4):
  offsets=[0,4,8,10]+[o for _ in range(r) for o in (12,18,20,24,26,28)]+[12,16];walk=[pc+o for o in offsets]
  check(all(b in e[a] for a,b in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackid11 pool finite CFG')
  result.append(dict(r=r,path=[hex(p) for p in walk],store_bytes_per_record=3,unwritten_record_offset=3,no_pointer_dereference_if_r0=True))
 return result


def copy_contract(data,index):
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];pc=0x20000332;src=int(fc['source'],16)+pc-int(fc['destination'],16)
 b=source.qret.binding.callees.previous.copier.body(init.binding.take(data,src,58),'copy',pc,18,init.binding.COPY_HASH)
 check(b['encoded_GPR_writes']==[13,14,15,16],'fallbackid11 copy preserves gate S/frame')
 e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_normal_return_CFG'].items()}
 offsets=[0,4,8,12,16,18,20,22]+[o for _ in range(16) for o in (34,38,42,46,48,52)]+[56,24,28,32];walk=[pc+o for o in offsets]
 check(all(z in e[a] for a,z in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackid11 copy16 finite CFG')
 return dict(source=src,body=b,copy16_path=offsets,source_zeros_and_nonalias_imply_destination_zeros=True,frame=0,control_clear_FENCE_capture_restore_not_executed=True)


def profile(data,hexraw,index,parent,by_source,first):
 base=0x20003000;delta=80*index;g=base+delta;F=g+492;C=F-80;d=id11.role.DETAILS[index];entry=d['entry'];pc,fp,dp,pp,ep,gp,ip=id11.STARTS[index]
 check(parent['end_cut']['pc']==entry+100 and parent['end_cut']['target']==pc and [parent['end_cut'][k] for k in ('fallback','gate','task_count','A0','A1','A2')]==[0,5,12,11,1,12],'fallbackid11 prior final-initializer join')
 windows={p:id11.body(init.binding.take(data,id11.STARTS[index][k],id11.SIZES[k]),p,index) for k,p in enumerate(id11.PARTS)}
 pn={v['pc']:v for v in windows['initializer']['instructions']};fn={v['pc']:v for v in windows['factory']['instructions']};dn={v['pc']:v for v in windows['defaults']['instructions']};gn={v['pc']:v for v in windows['gate']['instructions']}
 check([v['target'] for v in windows['factory']['calls']]==['0x2000039c']*2,'fallbackid11 factory fill-only calls')
 check(pn[pc+6]['rs2']==10 and pn[pc+20]['rs2']==pn[pc+40]['rs2']==8 and pn[pc+28]['imm']==-128+delta,'fallbackid11 saved ID11/pool pointer join')
 check(pn[pc+48]['imm']+pn[pc+52]['imm']==0x4cff6+152*index and pn[pc+58]['target']==0x4efe2+152*index,'fallbackid11 fourth callback input/tail')
 check(gn[gp+4]['imm']+base==F+21 and gn[gp+40]['imm']+base==g+1525,'fallbackid11 gate original source/cache')
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]+[('entries0_to11',layout.T,48),('NV_read_cache_word',C+32,4)]
 def exclude(a,z,skip=()):
  check(0<=a<a+z<=1<<32,'fallbackid11 nonwrapping envelope')
  for name,p,w in protected:
   if name not in skip:check(separated(a,z,p,w),'fallbackid11 envelope excludes '+name)
 factory=[]
 for part in ('factory','defaults'):
  body=windows[part];start=int(body['start'],16);nodes={v['pc']:v for v in body['instructions']};rows=id11.fixed_rows(part,index)
  check({start+o for o,a,z in rows}=={p for p,v in nodes.items() if v['op']=='store' and v['rs1']!=2},'fallbackid11 all fixed nonframe stores '+part)
  for o,a,z in rows:check(nodes[start+o]['width']==z,'fallbackid11 original fixed width');factory.append(dict(role=part,pc=start+o,address=a,bytes=z))
 factory += [dict(role='factory_fill6',pc=fp+98,address=g-156,bytes=6),dict(role='factory_fill24',pc=fp+192,address=g+12,bytes=24),dict(role='ID11_A',pc=pc+20,address=g-289,bytes=1),dict(role='ID11_B',pc=pc+40,address=g-274,bytes=1)]
 for v in factory:exclude(v['address'],v['bytes'])
 check(fn[fp+58]['imm']==-292+delta and fn[fp+58]['rs2']==8 and fn[fp+20]['imm']==2,'fallbackid11 deliberate ID66 byte10-to2 update')
 check(dn[dp+164]['imm']==-128+delta and dn[dp+218]['rs2']==14,'fallbackid11 end-pointer publication into defaults object')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0]);firstcopy=fc['first_copy'];cs=int(firstcopy['destination'],16);ce=int(fc['first_copy_end_exclusive'],16)
 overlaps=[v for v in factory if not separated(v['address'],v['bytes'],cs,ce-cs)]
 check(len(overlaps)==1 and overlaps[0]['pc']==fp+228 and overlaps[0]['address']==ce-4 and overlaps[0]['bytes']==4,'fallbackid11 intentional last4 copied-region overwrite')
 fs=int(firstcopy['source'],16)+0x2000039c-cs;fill=prefix.third.outer.previous.source.fill_contract(init.binding.take(data,fs,46));copy=copy_contract(data,index)
 check(fill['encoded_GPR_writes']==[10,14,15],'fallbackid11 fill preserves factory/gate S/frame')
 helper_ranges=[(0x2000039c,46),(0x20000332,58),(0x20000040,208),(0x200004bc,62)]
 for v in factory:
  for a,z in helper_ranges:check(separated(v['address'],v['bytes'],a,z),'fallbackid11 actual helper code preserved')
 gate=[('cache_ID',gp+68,g+1525,1),('clear_word',gp+80,g-16,4),('clear_word',gp+90,g+1484,4),('state4',gp+98,g+1524,1),('special_ID12',ip+4,g+942,1),('fillA',gp+122,g+1492,16),('fillB',gp+142,g+1508,16),('clear_byte',gp+150,g+1450,1),('clear_byte',gp+160,g+1488,1),('state7',gp+168,g+1449,1),('clear_byte',gp+188,g+1544,1),('output_word_zero',gp+192,g-12,4),('copyA',gp+230,g+1528,16),('copyB',gp+252,g+1464,16)]
 for name,p,a,z in gate:exclude(a,z)
 check([v['target'] for v in windows['gate']['calls']]==[hex(d['reg']),hex(ip),'0x2000039c','0x2000039c',hex(nv.STARTS[index]),hex(nv.STARTS[index]),'0x20000332','0x20000332',hex(nv.STARTS[index])],'fallbackid11 exact admitted helper/callee joins')
 check({v['pc'] for v in windows['gate']['instructions'] if v['op']=='store' and v['rs1']!=2}=={p for name,p,a,z in gate if gp<=p<gp+272 and name not in ('fillA','fillB','copyA','copyB')},'fallbackid11 complete gate nonframe store census')
 effects=[(v['address'],v['bytes']) for v in factory]+[(a,z) for name,p,a,z in gate]+[(g+856+4*j,4) for j in range(12)]+[(0x4002420c,4)]
 for a,z in effects[-13:]:exclude(a,z,('resource_callback_table',))
 for a,z in effects:
  for h,w in helper_ranges:check(separated(a,z,h,w),'fallbackid11 all fixed/control/CB writes exclude actual helpers')
 owner_checks=0;margin_cases=[]
 for (n,b),(q,t,owners,headers,table_size) in by_source.items():
  r=b&3;P8=next((a for name,a,z in owners if name=='ID8_payload'),None)
  if r:
   check(P8 is not None,'fallbackid11 positive r has ID8 payload');M=P8+190*r+6;request=194*r+6
   margin=[(M+4*j+o,z) for j in range(r) for o,z in ((0,2),(2,1))]
   check(M+4*r==P8+request and all(P8<=a<a+z<=P8+request for a,z in margin),'fallbackid11 reserved4r exact bound')
  else:M=0;margin=[]
  for m in range(4):
   nvowners=[]
   if m:
    s=prefix.small_geometry(n,q,t,first,m);nvowners=[('NV_header',s['free_header'],8),('NV_payload',s['payload'],s['request']),('NV_remainder',s['new_remainder'],8)]
   for a,z in effects:
    for name,p,w in owners+headers+nvowners:check(separated(a,z,p,w),'fallbackid11 fixed/gate/CB effects exclude owner '+name);owner_checks+=1
    check(separated(a,z,layout.P,table_size),'fallbackid11 first table payload before extra registration')
   for a,z in margin:
    exclude(a,z)
    for h,w in helper_ranges:check(separated(a,z,h,w),'fallbackid11 pool margin excludes actual helpers')
    for name,p,w in [(name,p,w) for name,p,w in owners if name!='ID8_payload']+headers+nvowners:check(separated(a,z,p,w),'fallbackid11 pool margin excludes other owner '+name)
    check(separated(a,z,layout.P,table_size),'fallbackid11 pool margin excludes table')
   for name,p,w in owners+headers+nvowners:check(separated(layout.T+48,4,p,w),'fallbackid11 optional entry12 excludes owner '+name)
  margin_cases.append(dict(first_count=n,source_byte=b,r=r,start=M,bytes=4*r,zero_r_no_pointer_dereference=not r))
 cb=id11.leaves.body(init.binding.take(data,0x4efe2+152*index,42),'callback_register',index);cbpaths=id11.leaves.path_certificates(cb)
 check(parent['end_cut']['task_count']==12 and id11.STARTS[index][4]==entry+104,'fallbackid11 callback return/outer epilogue')
 ebody=windows['outer_return'];en={v['pc']:v for v in ebody['instructions']};check(en[ep]['rd']==1 and en[ep]['imm']==12 and en[ep+2]['imm']==16 and en[ep+4]['rd']==0 and en[ep+4]['target']==gp,'fallbackid11 released outer frame tails gate')
 read=nv.body(init.binding.take(data,nv.STARTS[index],590),index);readpaths=nv.paths(read);readnodes={v['pc']-read['start']:v for v in read['instructions']}
 selected_reads={k:readpaths[k] for k in ('configured_missing_callback','RAM_null')}
 for label,path in selected_reads.items():check(not any(readnodes[o]['op'] in ('jal','jalr','call_indirect') for o in path) and all(readnodes[o]['rs1']==2 for o in path if readnodes[o]['op']=='store'),'fallbackid11 selected NV reads no nestedcalls/outputstores')
 check(all(readnodes[o].get('rd')!=12 for path in selected_reads.values() for o in path),'fallbackid11 final read preserves entryA2')
 check(all(readnodes[o].get('rd')!=11 for o in selected_reads['configured_missing_callback']) and 534 in selected_reads['RAM_null'] and readnodes[534]['rd']==11,'fallbackid11 selected final A1 difference')
 reg=id11.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackid11 registrar preserves inherited A1')
 check(gn[gp+56]['imm']+gn[gp+60]['imm']==0x6d26c+492*index and gn[gp+64]['target']==d['reg'],'fallbackid11 optional handler')
 check(12<14 and layout.T+52<=layout.T+56,'fallbackid11 optional ID12/count13 admission')
 for a,z in ((layout.T+48,4),(C+1,1)):
  for name,p,w in protected:
   if name!='task_count':check(separated(a,z,p,w),'fallbackid11 optional registration excludes '+name)
 copies=[(g+1492,g+1528,16),(g+1508,g+1464,16)]
 for s,t,z in copies:check(separated(s,z,t,z),'fallbackid11 copy16 no overlap');check(all(0<=j<z for j in range(16)),'fallbackid11 zero transfer scalar extent')
 check(gn[gp+264]['target']==nv.STARTS[index] and gn[gp+260]['imm']==4 and gn[gp+262]['imm']==4 and gn[gp+256]['imm']==-12+80*index and gn[gp+268]['imm']==0,'fallbackid11 last read(4,4,g-12) and forced gateA0zero')
 ROM=[0x6f000+v+496*index for v in (-1408,-1424,-1428,-1392,-1376)];check(all(p>0x40000+len(data) for p in ROM),'fallbackid11 stored ROM pointers outside candidate; no dereference')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[(p,id11.STARTS[index][k],id11.SIZES[k]) for k,p in enumerate(id11.PARTS)]+[('callback_register',int(cb['start'],16),42),('fill',fs,46),('copy',copy['source'],58),('read',nv.STARTS[index],590),('registrar',d['reg'],48)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackid11 strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],bodies=windows,strictHEX_guards=guards,fixed_factory_defaults_envelopes=factory,conditional_admitted_gate_envelopes=[dict(role=k,pc=p,address=a,bytes=z) for k,p,a,z in gate],protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],
  deliberate_updates=dict(ID66_byte=dict(address=g-292,old_value=10,new_value=2),local_ID11_bytes=[g-289,g-274],local_ID11_values=[11,11],first_copy_last4=dict(address=ce-4,bytes=4,new_value=0x49156+152*index,whole_first_copy_preservation_claimed=False,actual_called_helpers_excluded=True),object_RAM_delta=76,scalar_RAM_delta=80,stored_ROM_delta=496,stored_ROM_addresses=ROM,missing_ROM_not_dereferenced=True,end_pointer_published_at=base-388+76*index+60),
  pool_margin=dict(case_columns=['first_count','source_byte','r','start','bytes'],cases=[[v[k] for k in ('first_count','source_byte','r','start','bytes')] for v in margin_cases],r0_no_pointer_dereference=True,paths=pool_paths(windows['pool'],pp),formula='ID8 P+190*r+6 .. P+194*r+6; 4*r bytes',ordered_stores='SHffff@4*j;SB0@4*j+2;byte3 untouched',r_and_gate_low2_match_only_under_original_source_retention=True),
  callback_publication=dict(input_pointer=0x4cff6+152*index,generic_leaf_paths=cbpaths,q_positive_selected_slot=3,q0_retained_four_scan_indices=callback_quads(),index12_means_full=True,partition=[495,220,66,12,1],callback_invoked=False),
  interval_certificate=dict(source_families=1024,NV_count_families=4096,owner_header_checks=owner_checks,ID8_reserved_margin_write_is_intentional=True),
  gate_CFG_paths=id11.gate_paths(windows['gate']),admitted_copy16=copy,admitted_NV_paths=selected_reads,
  selected_returns=dict(low2_zero=dict(A0=24,A1='callback-register result; may be last nonzero slot11 word if q0/full',A2=12,task_count=12,frames_released=True),low2_nonzero_cachedID_notFF=dict(A0=24,A1=0,A2=12,task_count=12,frames_released=True),low2_nonzero_cachedID_FF_admitted=dict(required_count=12,required_capacity_min=14,required_table=layout.T,handler=0x6d26c+492*index,entry12=layout.T+48,new_count=13,cached_ID_address=g+1525,cached_ID_value=12,special_ID_address=g+942,special_ID_value=12,NV_fast_error_replies=[10,10,10],zero_buffers=[g+1492,g+1508,g+1528,g+1464],zero_word_output=g-12,A0=0,A1_configured_missing_callback=4,A1_RAM_null=0,A2=g-12,frames_released=True)),
  end_summary=dict(selected_outer_initialization_returns_to_original_caller=True,full_application_or_all_domains_complete=False,fallback=0,ID66_byte_value=2,local_ID11_values=[11,11],task_count= '12 on early returns;13 on admitted gate',physical_NV_success_or_persistence_claimed=False),
  frames=dict(outer=16,initializer=16,factory=16,pool_callback_fill_copy=0,gate=16,NV_read_wrapper=32,selected_stage_peak=48,outer_released_before_gate=True,all_stage_frames_released_at_final_RET=True),
  required_premises=['all inherited selected b/q/r/m0..3/NV-fast-error/FF-status/flags/ISA/first-copy/code/metadata/frame/header ownership conditions remain conditional; original F21 byte andlow2/endpointer reloads retained',
   'matching local fill/copy normal returns and required S/GP/SP/RA/savedwords, valid nonalias physical frames/globals/owned pool-margin/control/code/table extents; no adverse control/FENCE/IRQ/DMA/reentry/externalwriters',
   'prior three callback observations/nonnull insertions and remaining zero words retained through all fixed/pool writes; four-scan scalar relations not coherent snapshots. Actual callbacks and missingROM pointer consumers not invoked',
   'admitted gate additionally requires fresh cacheIDff/count12/cap>=14/tableT plus one retained read-wrapper fast-failure condition for all three reads. Their reply10 is ignored; zero-fill and matchingcopy results do not prove NV success',
   'first-copy tail4 intentionally rewritten, only actual used helper code ranges proved untouched; no claim of whole copied-region immutability, installedbindings, complete lifetimes or all-path application/firmware completion'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);by_source,first=prefix.families()
 return dict(schema='TSL9-fallback-final-ID11-factory-margin-selected-outer-gate-returns-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(data,h,i,parent['profiles'][i],by_source,first) for i,(data,h) in enumerate(zip(carriers,hexes))],C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  source_composition='selected ID11/count12 -> factory/defaults/poolmargin -> fourthcallback -> outerframe release -> gate24 OR selected admittedID12/count13/readerrors/zeros/copies/RET0',
  remaining=['actual installedbindings/sourcewriters/other allocation-NV-flag-cache domains','special handler6d26c/6d458,callback4cff6/4d08e and object/ROM consumers','complete APP return/reachability,physicaleffects/IRQprogress/cross-event retention-consumption-release lifetime'])


def tests(carriers):
 previous.tests(carriers);id11.tests(carriers);mutations=0;callback_quads()
 for i,data in enumerate(carriers):
  c=copy_contract(data,i);raw=init.binding.take(data,c['source'],58);base=0x20000332
  for p,d in id11.decode(raw,base).items():
   o=p-base;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:source.qret.binding.callees.previous.copier.body(bad,'copy',base,18,init.binding.COPY_HASH)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackid11 copy mutation escaped')
   mutations+=1
 check(mutations==36 and 2933+528+36==3497,'fallbackid11 mutation census')
 print('PASS:3497 original instruction/typed-load mutations rejected;794 conditional callback quads;reserved4r/factory/helper-tail/selected gate return proofs')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackid11 exactledger')
 print('PASS:selected finalinitializer/poolmargin/outergate RET24-or-RET0;12strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,NV or targetnetwork;actualbindings/otherdomains/APP/full lifetime UNPROVED')


if __name__=='__main__':main()
