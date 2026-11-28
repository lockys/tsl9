"""Offline selected ID7 initialization, exact updates and ID8 return join.

Original-byte/CFG guards and immutable scalar/interval/frame certificates.
No target execution/emulation or mutable RAM/heap/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_third_static as previous
import check_v4160_id7_initialization_static as id7

init,sparse,check=previous.init,previous.sparse,previous.check
layout=previous.layout
separated=previous.previous.previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-id7-static.json')


def profile(data,hexraw,index,parent,geometry):
 G=0x20003000;delta=80*index;g=G+delta;F=g+492;ctx=F-80;pc=id7.STARTS[index][0];d=id7.role.DETAILS[index];entry=d['entry']
 check(parent['end_cut']['pc']==entry+36 and parent['end_cut']['target']==pc and [parent['end_cut'][k] for k in ('fallback','gate','task_count','saved_ID6','A0','A2')]==[0,5,8,6,7,8],'fallbackid7 inherited input join')
 windows={part:id7.body(init.binding.take(data,id7.STARTS[index][k],id7.SIZES[index][k]),part,index) for k,part in enumerate(id7.PARTS)}
 pn={v['pc']:v for v in windows['initializer']['instructions']};sn={v['pc']:v for v in windows['state']['instructions']};tn={v['pc']:v for v in windows['selector']['instructions']};on={v['pc']:v for v in windows['next_outer']['instructions']}
 check([int(v['target'],16) for v in windows['initializer']['calls']]==list(id7.STARTS[index][1:5]),'fallbackid7 four guarded direct callees')
 check(pn[pc+4]['rs2']==10 and pn[pc+4]['imm']==12 and pn[pc+44]['rs1']==2 and pn[pc+44]['imm']==12 and pn[pc+44]['rd']==10,'fallbackid7 ID7 save/reload')
 check(pn[pc+56]['rs2']==10 and pn[pc+56]['imm']==940+delta and pn[pc+60]['imm']==5,'fallbackid7 local ID7 and selector5')
 check(pn[pc+54]['rd']==1 and pn[pc+54]['imm']==28 and pn[pc+62]['imm']==32 and pn[pc+64]['rd']==0 and pn[pc+64]['target']==id7.STARTS[index][5],'fallbackid7 restore RA/frame and unlinked selector tail')
 # F96 has a deliberate write to its last two bytes. Preserve only its prefix,
 # and separately certify that sole intersection rather than hiding the update.
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals'] if v['role']!='F96']
 check(sum(v['role']=='F96' for v in parent['protected_intervals'])==1,'fallbackid7 inherited F96 census')
 protected += [('F_prefix94',F,94),('third_pool_pointer',g+792,4),('entries0_to7',layout.T,32)]
 def exclude(a,z,skip=()):
  check(0<=a<a+z<=1<<32,'fallbackid7 nonwrapping envelope')
  for name,p,w in protected:
   if name not in skip:check(separated(a,z,p,w),'fallbackid7 footprint excludes '+name)
 writes=[]
 for part in id7.PARTS[:-1]:
  b=windows[part];start=int(b['start'],16);nodes={v['pc']:v for v in b['instructions']};rows=id7.fixed_intervals(part,index)
  check({start+o for o,a,z in rows}=={p for p,n in nodes.items() if n['op']=='store' and n['rs1']!=2},'fallbackid7 complete nonframe store census '+part)
  for o,a,z in rows:
   check(nodes[start+o]['width']==z,'fallbackid7 original store width');exclude(a,z);writes.append(dict(role=part,pc=start+o,address=a,bytes=z))
 statepc=id7.STARTS[index][4];fill_address=g+1456
 check(windows['state']['tails']==[dict(pc=hex(statepc+122),target='0x2000039c',rd=0)],'fallbackid7 sole state fill tail')
 check(sn[statepc+88]['imm']+sn[statepc+110]['imm']==fill_address and sn[statepc+108]['imm']==0 and sn[statepc+102]['imm']==6,'fallbackid7 six-byte zero-fill arguments')
 exclude(fill_address,6);writes.append(dict(role='state_fill6',pc=statepc+122,address=fill_address,bytes=6))
 check(len(writes)==119+index,'fallbackid7 fixed/fill envelope census')
 hits=[(v['role'],v['pc']-pc,v['address'],v['bytes']) for v in writes if not separated(v['address'],v['bytes'],F,96)]
 check(hits==[('initializer',34,F+94,2)] and pn[pc+30]['imm']==-256,'fallbackid7 sole F96 intersection is FF00 at F94')
 record=g+812
 record_hits=[(v['role'],v['pc']-id7.STARTS[index][5],v['address'],v['bytes']) for v in writes if not separated(v['address'],v['bytes'],g+800,48)]
 check(record_hits==[('selector',32,record+2,1),('selector',34,record,2)],'fallbackid7 sole record48 intersections')
 check(pn[pc+36]['rs2']==0 and pn[pc+36]['width']==1 and record+3<=g+848,'fallbackid7 F96outside zero/record1 extent')
 te={int(p,16):[int(q,16) for q in qs] for p,qs in windows['selector']['conditional_CFG'].items()};tpc=id7.STARTS[index][5]
 selector_path=id7.paths.chain(te,tpc,{tpc+12:tpc+16});check(len(selector_path)==14 and tn[tpc+36]['imm']==0 and 11 not in windows['selector']['encoded_GPR_definitions'],'fallbackid7 selector5 ordinary RET A0zero/A1five')
 # These are immutable interval lists from the already selected allocation
 # cases, not a heap model or load/store replay.
 owner_checks=0
 for r in geometry:
  owners=r['prior_owned_intervals']+[(name,a,z) for name,(a,z) in zip(('third_header','third_free_remainder_header','third_payload'),r['write_intervals'])]
  table_start,table_end=r['first_table_payload']
  for v in writes:
   for name,a,z in owners:check(separated(v['address'],v['bytes'],a,z),'fallbackid7 prior allocation survives '+name);owner_checks+=1
   check(separated(v['address'],v['bytes'],table_start,table_end-table_start),'fallbackid7 first-table payload survives pre-registration')
  for name,a,z in owners:check(separated(layout.T+32,4,a,z),'fallbackid7 entry8 excludes allocations '+name)
 small=previous.previous.geometry()[1]
 q0layout=next(r for r in layout.facts() if r['input_byte']==0);q0R=q0layout['rounded_payload'];check(q0layout['N0']==14,'fallbackid7 q0 table capacity')
 for v in writes:
  check(separated(v['address'],v['bytes'],layout.P,q0R),'fallbackid7 q0 first-table payload survives')
  for r in small:
   for a,z in ((r['header'],8),(r['payload'],r['request']),(r['new_remainder'],8)):check(separated(v['address'],v['bytes'],a,z),'fallbackid7 q0 first-small owner/remainder survives')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16)
 fill=previous.outer.previous.source.fill_contract(init.binding.take(data,fs,46));check(fill['encoded_GPR_writes']==[10,14,15],'fallbackid7 matching fill/frame preservation')
 original_entry=id7.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in original_entry['instructions']}
 check(en[entry+36]['target']==pc and en[entry+36]['rd']==1 and int(windows['next_outer']['start'],16)==entry+40,'fallbackid7 saved caller return join')
 check(on[entry+48]['target']==d['reg'] and on[entry+52]['target']==d['outer_init'][2],'fallbackid7 next registration and third initializer cut')
 handler=0x4b000+d['outer_lows'][2];check(on[entry+40]['imm']+on[entry+44]['imm']==handler,'fallbackid7 next handler formation')
 reg=id7.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackid7 registrar preserves A1five')
 for a,z in ((layout.T+32,4),(ctx+1,1)):exclude(a,z,('task_count',))
 check(layout.T+36<=layout.T+4*14 and 8<14 and 9<=14,'fallbackid7 entry8 extent/count admission')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[(part,id7.STARTS[index][k],id7.SIZES[index][k]) for k,part in enumerate(id7.PARTS)]+[('fill',fs,46),('outer_entry',entry,112),('task_register',d['reg'],48)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackid7 strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],bodies=windows,strictHEX_guards=guards,fixed_conditional_envelopes=writes,
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],allocation_interval_certificate=dict(positive_cases=len(geometry),owner_pair_checks=owner_checks,q0_firstsmall_cases=3,whole_first_table_payload_preserved_before_next_registration=True,third_free_remainder_header_preserved=True),
  deliberate_updates=[dict(role='F94_word',address=F+94,bytes=2,value=0xff00,byte_values=[0,255]),dict(role='F96_outside_byte',address=F+96,bytes=1,value=0),dict(role='record1_ID',address=record+2,bytes=1,value=7),dict(role='record1_selector',address=record,bytes=2,value=5),dict(role='local_ID7',address=g+940,bytes=1,value=7)],
  F96_whole_preservation_claimed=False,selected_fallback_zero_retained=True,prior_callback_table_published_pointer_or_unconstrained_q0_outcome_retained=True,
  direct_call_contracts=dict(no_callee_source_loads_or_frame=True,defaults_clobbers_A0_then_initializer_reloads_saved_ID7=True,state_tail_fill=dict(target=0x2000039c,A0=fill_address,A1=0,A2=6,ordinary_return_to=pc+22),entry_A1_not_needed_for_fixed_selector5=True),
  selector=dict(A0=7,A1=5,record_index=1,accepted_CFG_path=selector_path,ordinary_RET_A0=0,ordinary_RET_A1=5,return_to_outer=entry+40),
  frames=dict(initializer=32,saved_ID_relative_entry_SP=-20,saved_RA_relative_entry_SP=-4,all_direct_callees_and_fill=0,outer=16,selected_stage_live_max=48,initializer_released_before_selector=True),
  next_registration=dict(pc=entry+48,target=d['reg'],handler=handler,required_fresh_count=8,required_capacity_min=14,required_table=layout.T,entry8=layout.T+32,new_count=9,A0=8,A1=5,A2=9),
  end_cut=dict(pc=entry+52,target=d['outer_init'][2],fallback=0,gate=5,task_count=9,saved_ID6=6,local_ID7=7,A0=8,A1=5,A2=9,third_outer_initializer_not_executed=True),
  required_premises=['all inherited selected q0/positive first/second/third pool conditions, matching original resident/first-copy/fill/ISA and source/header ownership remain conditional',
   'actual state-tail fill matches guarded local software fill with no pointer retention, normal RET through carried RA to initializer+22, valid owned nonalias frames/globals/tables/code and saved ID/RA/GP/S/SP',
   'closed fixed-address writes and six-byte fill are physical extents under valid accesses and no adverse IRQ/DMA/reentry/external writers or hardware side effects; fixed vector stores publish code pointers without invoking them',
   'fresh count8/capacity>=14/tableT and required retained metadata at registration; source/code/stack validity and uninterrupted scalar algebra do not prove actual installed binding, async ordering, callback invocation or cross-event lifetime'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);geometry=previous.geometry();domain=id7.selector_domain()
 return dict(schema='TSL9-fallback-ID7-exact-updates-selected-ID8-count9-join-v1',APP_sha256=sha256(image).hexdigest(),selector_domain=domain,
  profiles=[profile(data,h,i,parent['profiles'][i],geometry) for i,(data,h) in enumerate(zip(carriers,hexes))],
  source_composition='selected ID7/count8/fallback0 cut -> four fixed callees and matching state fill -> explicit F94/record1/ID7 updates -> selector5 RET -> fresh taskID8/count9',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual installed bindings/source/header writers/other allocation domains','third outer initializer4a7d6/4a86e and later registrations/callback consumers','physicaleffects/IRQprogress/full cross-event retention-consumption-release'])


def tests(carriers):
 previous.tests(carriers);id7.tests(carriers)
 check(548+511==1059,'fallbackid7 mutation composition census')
 print('PASS:1059 original operand/core mutations rejected;264 prior-allocation geometries;65536 selector cases;explicit F94/record1 updates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackid7 exactledger')
 print('PASS:selected ID7 callees/explicit updates/selector RET/ID8 count9 join;10strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;actualbindings/thirdinitializer/full lifetime UNPROVED')


if __name__=='__main__':main()
