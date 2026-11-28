"""Offline fallback preservation across selected first-role gate branches.

Original bytes/CFG/store classifications and closed interval/field algebra.
No target execution/emulation or mutable RAM/object/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_timer_static as previous
import check_v4160_role_initializer_fields_static as fields

role=fields.previous
init,sparse,check=previous.init,previous.sparse,previous.check
layout=previous.layout
OUT=Path(__file__).with_name('v4160-b1-fallback-role-static.json')


def profile(data,hexraw,index,parent,rp,fp):
 d=role.DETAILS[index];ctx=0x20003000+d['ctx'];base=0x20003000+d['base'];slot=parent['fallback_slot'];entry5=layout.T+20
 check(parent['end_cut']['before_indirect_call']==0x8eb6 and parent['end_cut']['fallback']==0 and [parent['end_cut'][k] for k in ('A0','A1','A2')]==[4,0,5],'fallbackrole prior zero/setup arguments join')
 check(parent['second_task']['count_after']==5 and init.binding.word(data,0x401a0)==d['entry'],'fallbackrole freshcount/candidate401a0 join')
 check(rp['zero_case']['entry5_address']==hex(entry5) and rp['zero_case']['registration_reply']==5 and rp['zero_case']['count_after_registration']==6,'fallbackrole zero register join')
 check(rp['nonzero_case']['entry5_address']==hex(entry5) and rp['nonzero_case']['initializer_incoming_A0_A1_A2']==[5,0,6],'fallbackrole nonzero register join')
 check(fp['cut_before_first_late_call']['target']==hex(fields.DETAILS[index][3][0]) and int(fp['cut_before_first_late_call']['pc'],16)==d['initialize']+388,'fallbackrole zero first late RF call cut')
 _,mem=sparse.inspect(hexraw,sparse.parser());sources=[]
 intervals=[('entry',d['entry'],112),('primary',d['primary'],62),('gate',d['gate'],84),('initializer',d['initialize'],426),('selector',fields.DETAILS[index][0],70),('setter0',d['setters'][0],10),('setter1',d['setters'][1],10),('registration',d['reg'],48),('fill',(0x4060c,0x4064c)[index],46),('candidate401a0',0x401a0,4)]
 for label,a,z in intervals:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackrole strictHEX '+label);sources.append(dict(role=label,source=a,bytes=z,sha256=sha256(raw).hexdigest()))
 # Already-complete classified initializer stores, before the first late call,
 # are own-frame or the fixed object/gate/trailing-word ranges only.
 b=fp['initializer'];pc=d['initialize'];n={v['pc']:v for v in b['instructions']}
 stores=[v for v in fp['classified_direct_stores'] if int(v['pc'],16)<pc+388]
 check(len(stores)==41 and fp['object_base']==hex(base),'fallbackrole exact41 classified stores before late call')
 for v in stores:
  a=v['address'];z=v['bytes']
  if a.startswith('initializerSP'):continue
  a=int(a,16)
  check(a==ctx+3 and z==1 or base<=a and a+z<=base+308,'fallbackrole object/gate store envelopes')
 suffix=[v for v in stores if int(v['pc'],16)>=pc+62]
 check(len(suffix)==35 and all(base<=int(v['address'],16)<int(v['address'],16)+v['bytes']<=base+296 for v in suffix),'fallbackrole all35 suffix stores inside object')
 protected=[('fallback',slot,4),('first_task_byte',0x20004184,1),('second_task_byte',0x200040a6,1),('timer_head',0x20003000+previous.timer.DETAILS[index][4],4),('nominal_timer_node',layout.A+8,16),('small_header',layout.A,8),('small_remainder_header',layout.A+24,8),('large_header',layout.B,8),('capacity',ctx+2,1),('table_pointer',ctx+40,4),('existing_entries0_to4',layout.T,20)]
 def effects(rows):
  out=[]
  for label,a,z in rows:
   check(0<=a<a+z<=1<<32,'fallbackrole nonwrapping envelope')
   for name,p,w in protected:check(previous.separated(a,z,p,w),'fallbackrole '+label+' excludes '+name)
   out.append(dict(role=label,address=a,bytes=z))
  return out
 zero=effects([('fill_control',0x4002420c,4),('registration_count',ctx+1,1),('entry5',entry5,4),('object_clear_and_suffix',base,296),('three_trailing_zero_words',base+296,12),('gate_byte',ctx+3,1)])
 nonzero=effects([('registration_count',ctx+1,1),('entry5',entry5,4)]+[('gate_or_primary_callback_word',int(v['address'],16),4) for v in rp['gate_publisher_words']+rp['primary_publisher_words']])
 check(len(zero)==6 and len(nonzero)==9,'fallbackrole branch envelope census')
 for cap in range(14,213,3):check(5<cap and entry5+4<=layout.T+4*cap,'fallbackrole all67 entry5 bounds')
 gate_pc=d['gate'];gn={v['pc']:v for v in rp['bodies']['gate']['instructions']};ge={int(p,16):[int(z,16) for z in zs] for p,zs in rp['bodies']['gate']['normal_return_CFG'].items()}
 skip=role.previous.chain(ge,gate_pc,{gate_pc+12:gate_pc+30})
 check(all(gn[int(p,16)]['op']!='jal' for p in skip),'fallbackrole nonzero no inner calls')
 # Three size classes represent all selected CFG branch combinations. Numeric
 # field bounds are checked for every U16 below; no register/object runner.
 size_classes=[dict(start=0,end_exclusive=27,path=fields.selected_prefix(b,pc,0)),dict(start=27,end_exclusive=252,path=fields.selected_prefix(b,pc,27)),dict(start=252,end_exclusive=65536,path=fields.selected_prefix(b,pc,252))]
 for c in size_classes:
  check(int(c['path'][-1],16)==pc+388,'fallbackrole zero selected prefix ends before RF')
  check([n[int(p,16)]['target'] for p in c['path'] if n[int(p,16)]['op']=='jal' and int(p,16)>=pc+62 and int(p,16)<pc+388]==[fields.DETAILS[index][0]],'fallbackrole selector only suffix call before RF')
 return dict(label=parent['label'],fallback_slot=slot,candidate401a0=d['entry'],resident_strictHEX_guards=sources,protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],
  incoming=dict(A0=4,A1=0,A2=5,fresh_count=5,gate_byte=ctx+3,gate_is_distinct_from_count_and_capacity=True),
  zero_branch=dict(fresh_gate=0,entry5_handler=d['handler'],registration_reply=5,count_after=6,gate_after_prefix=5,object=base,object_bytes=296,object_selector_byte=base+3,selector_input=int(fp['selector_input_halfword'],16),selector_output_if_retained_clock_halfword1000=0,effect_intervals=zero,size_CFG_classes=size_classes,
   cut_before_call=pc+388,RF_callee=fields.DETAILS[index][3][0],fallback_at_cut=0,arguments={'A0':27,'A1':328,'A2':'8*(k+14)','A3':'8*(k+138)'},k='min(fresh U16[config64+16],251)',gate_primary_publishers_executed_at_cut=False,initializer_return_proved=False),
  nonzero_branch=dict(fresh_gate_domain=[1,255],gate_value_preserved=True,inner_registration_or_initializer_called=False,gate_and_primary_words=rp['gate_publisher_words']+rp['primary_publisher_words'],effect_intervals=nonzero,entry5_handler=int(rp['nonzero_case']['entry5_handler'],16),registration_reply=5,count_after=6,
   cut_before_call=d['entry']+20,outer_initializer=d['outer_init'][0],fallback_at_cut=0,arguments={'A0':5,'A1':0,'A2':6}),
  frames=dict(relative_to_role_entry_SP='outerRA S-4, primaryRA S-20, gateRA S-36, initializerSP S-64/savesS2,S1,S0,RA atS-64,-60,-56,-52',zero_cut_frames_still_live=True,nonzero_cut_outer_frame_live=True),
  required_premises=['all previous conditional source/post IO/wrapper/timer success OR separate zero-failure/secondtask premises remain; fresh401a0/code/registrar/fill/selector/setters match candidates','fresh count5/capacityN0/tableT held until each branch-specific accepted registration; additional fresh gate0 OR gate1..255 separately, no actual boot branch reachability established','zero branch valid stable object308B/sourcefields/nonwrapping frames; fill/setters/selector complete normally, saved ID5 and local flags retained; optional selector0 assertion needs fresh clock-halfword1000 retained','numerical disjointness is not physical side-effect exclusion; valid owned nonalias frames/heap/globals/code/metadata and preservedsavedwords/GP/context, no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriters','zero and nonzero publish different callback handlers to same entry5 in alternative paths; no merge of gate/primary word stores before zero initializer returns'],
  boundary='zero cut before first RF callee; nonzero cut before first outer initializer; no their effects/zero initializer return/later outer registrations/tail/event lifetime proof',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);r=role.derive(image,carriers,header,coverage);f=fields.derive(image,carriers,header,coverage)
 return dict(schema='TSL9-fallback-role-gate-zero-RF-cut-nonzero-outer-cut-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i],r['profiles'][i],f['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='fallback0 at setup8eb6 -> matching401a0 withfresh count5 -> gatezero registration/fill/setters/selector/object fields beforeRF OR nonzero gate/primary publish/firstouter registration beforeouterinitializer',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['zero branch RF/remaining latecallees/tail and initializerreturn; nonzero outerinitializer/laterregistrations/tail','actual fresh gate/head/header/GP/provider/source binding and other writers','physicaleffects/IRQprogress/otherdomains andfullconsumption-retention-release lifetime'])


def tests(carriers):
 role.tests(carriers);fields.tests(carriers)
 for g in range(256):check((g==0) != (1<=g<=255),'fallbackrole exhaustive gate partition')
 for u in range(65536):
  k=min(u,251);c=0 if u<27 else 1 if u<252 else 2
  check((c==0)==(k<27) and (c==2)==(u>251),'fallbackrole size CFG classes')
  check(112<=8*(k+14)<=2120 and 1104<=8*(k+138)<=3112 and 8*(k+138)>328,'fallbackrole RF argument bounds')
 print('PASS:520 reused original role/initializer/selector mutations rejected;256 gate bytes and65536 independent size cases;branch-specific cuts/envelopes')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackrole exactledger')
 print('PASS:conditional fallback-zero role gate0 toRF cut OR nonzero toouterinitializer cut;6/9 envelopes/profile;10strictHEX guards;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;RF/outercallee/actualbinding/full lifetime UNPROVED')


if __name__=='__main__':main()
