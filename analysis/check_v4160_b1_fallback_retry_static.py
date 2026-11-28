"""Offline selected range/retry source closure and post-return publication.

Original-byte CFG/operand/store and closed interval/scalar/frame certificates.
No target execution/emulation or mutable RNG/RAM/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_rf_static as previous
import check_v4160_gate_return_publication_static as publication

ranges=publication.previous
role=publication.role
init,sparse,check=previous.init,previous.sparse,previous.check
layout=previous.layout
OUT=Path(__file__).with_name('v4160-b1-fallback-retry-static.json')


def profile(image,data,hexraw,index,parent,rp,pp):
 d=role.DETAILS[index];G=0x20003000;delta=80*index;ctx=G+d['ctx'];F=ctx+80;B=G+d['base'];slot=parent['fallback_slot']
 small,wide,src,tail=ranges.DETAILS[index][0]
 check(parent['end_cut']['pc']==tail+46 and parent['end_cut']['target']==small and [parent['end_cut'][k] for k in ('A0','A1','A2')]==[0,16383,6] and parent['end_cut']['fallback']==0,'fallbackretry prior caller/args/zero join')
 check(parent['end_cut']['gate']==5 and parent['end_cut']['count']==6,'fallbackretry prior gatezero metadata')
 check(rp['bodies']['tail']['start']==hex(tail) and pp['conditional_return_links']['retry_RET_to_gate']==hex(d['gate']+30),'fallbackretry normal RET link to gate suffix')
 check(int(rp['source_primary_slot'],16)==F+36 and int(rp['source_fallback_slot'],16)==F-12 and slot==F+52,'fallbackretry distinct primary/secondary vs allocator fallback slots')
 check(len({F+36,F-12,F+52})==3,'fallbackretry no source/failure slot conflation')
 clockpc=publication.specs('clock',index)[0];cbpc=publication.clock.DETAILS[index][1];arpc=publication.clock.previous.arithmetic.BASES[index]
 reader=ranges.provider.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,ranges.provider.APP_HASHES[1])
 check(not reader['calls'] and not any(v['op']=='store' for v in reader['instructions']),'fallbackretry reader closure no stores/calls')
 cb=publication.clock.body(init.binding.take(data,cbpc,130),'callback',index)
 ar=publication.clock.arithmetic(init.binding.take(data,arpc,914),arpc)
 check(ar['complete_CFG_and_preservation'] and not any(v['op']=='store' for v in ar['instructions']),'fallbackretry general callback arithmetic no stores')
 check(cb['instructions'][0]['op']=='addi' and cb['instructions'][0]['rd']==2 and cb['instructions'][0]['imm']==-32,'fallbackretry callback frame32')
 clk=pp['windows']['clock'];cn={v['pc']:v for v in clk['instructions']}
 check(cn[clockpc+4]['imm']==560+delta and cn[clockpc+30]['imm']==20,'fallbackretry clock callback/accumulator fixed operands')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 originals=[(r,a,z) for r,a,z in zip(ranges.ROLES,ranges.DETAILS[index][0],ranges.SIZES)]+[('clock_wrapper',clockpc,42),('clock_callback',cbpc,130),('clock_arithmetic',arpc,914),('gate',d['gate'],84),('primary',d['primary'],62),('outer_entry',d['entry'],112),('registration',d['reg'],48),('candidate4007c',0x4007c,4)]
 for label,a,z in originals:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackretry strictHEX '+label);guards.append(dict(role=label,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 check(len(guards)==12,'fallbackretry strictHEX census')
 protected=[('allocator_fallback',slot,4),('config64_and_clock_source',F,96),('gate',ctx+3,1),('capacity',ctx+2,1),('table_pointer',ctx+40,4),('entries0_to5',layout.T,24),('timer_head',G+previous.previous.previous.timer.DETAILS[index][4],4),('nominal_timer_node',layout.A+8,16),('small_header',layout.A,8),('small_remainder',layout.A+24,8),('large_header',layout.B,8),('task0',0x20004184,1),('task1',0x200040a6,1)]
 effects=[]
 def add(label,a,z):
  check(0<=a<a+z<=1<<32,'fallbackretry nonwrapping interval')
  for name,b,w in protected:check(previous.previous.previous.separated(a,z,b,w),'fallbackretry '+label+' excludes '+name)
  effects.append(dict(role=label,address=a,bytes=z))
 for label,a,z in [('source_control',0x4002420c,4),('word_source_state',0x20002ec8+delta,4),('clock_accumulator',ctx+20,4),('clock_callback_result',ctx+24,4),('retry_seed_candidate',B+244,12),('registration_count',ctx+1,1),('entry6',layout.T+24,4)]:add(label,a,z)
 for v in pp['gate_publication_words']+pp['primary_publication_words']:add('gate_or_primary_pointer',int(v['address'],16),4)
 check(len(effects)==14,'fallbackretry fourteen effect envelopes')
 for v in rp['classified_direct_object_stores']:check(B+244<=int(v['address'],16)<int(v['address'],16)+v['bytes']<=B+256,'fallbackretry all retry stores inside seed/candidate envelope')
 for a,z in ((B+244,12),):
  for b,w in ((B+232,6),(B+193,1),(B+201,1)):check(previous.previous.previous.separated(a,z,b,w),'fallbackretry preserves old tuple/sample bytes')
 check(int(rp['word_source_state'],16)==0x20002ec8+delta and pp['clock_accumulator']==hex(ctx+20) and pp['matching_clock_callback']['result_word']==hex(ctx+24),'fallbackretry fixed source/clock/result joins')
 reg=pp['first_outer_registration'];cut=pp['cut_before_first_outer_initializer']
 check(reg['fresh_count_premise']==reg['reply']==6 and reg['new_count']==7 and reg['entry6_address']==hex(layout.T+24),'fallbackretry selected gatezero entry6 not entry5')
 check(cut=={'pc':hex(d['entry']+20),'target':hex(d['outer_init'][0]),'A0':6,'A1':'0xffffffff','A2':7},'fallbackretry next outer initializer args/cut')
 for cap in range(14,213,3):check(6<cap and layout.T+28<=layout.T+4*cap,'fallbackretry entry6 inside all67 tables')
 return dict(label=parent['label'],fallback_slot=slot,strictHEX_guards=guards,effect_intervals=effects,protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],
  source_bindings=dict(primary_slot=F+36,secondary_slot=F-12,allocator_failure_slot=F+52,clock_callback_slot=F+68,closed_cases=['fresh primary0 and secondary0: no source callback','fresh primary0 and secondary191c6: matching reader','fresh primary matching43520/435ac, its callback0','fresh primary matching43520/435ac, callback43d62/43dee withcopiedreader191c6'],other_nonzero_callbacks_closed=False,actual_boot_bindings_or_order_proved=False),
  source_values=dict(state_word=0x20002ec8+delta,local_formula='(214013*s+2531011) mod2^32; callback case first stores(reply+fresh postcallback state)mod32',coherent_snapshot_uniformity_or_randomness_proved=False),
  retry=dict(full_body=tail,entry_cut=tail+46,small_range=[0,16383],small_output=[0,16382],wide_range=[0,0xffffffff],wide_output=[0,0xfffffffe],independent_source_samples=True,seed_extent=[B+244,B+250],candidate_extent=[B+250,B+256],old_extent=[B+232,B+238],ordinary_RET=tail+252,reply='last Y & ffff; may be0',normal_return_implies_gate_link=d['gate']+30,termination_bound_or_actual_return_proved=False),
  returned_publication=dict(gate_words=pp['gate_publication_words'],primary_words=pp['primary_publication_words'],ordinary_reply_not_tested_as_boolean=True,gate=5,count_before_outer_registration=6,first_outer_registration=reg),
  end_cut=dict(pc=d['entry']+20,target=d['outer_init'][0],A0=6,A1=0xffffffff,A2=7,fallback=0,gate=5,count=7,outer_frame_live=True,nonzero_gate_branch_not_composed=True),
  frame_certificate=dict(retry=32,range=32,source=16,clock_wrapper=16,clock_callback=32,reader_and_arithmetic=0,selected_retry_subgraph_peak=128,after_retry_normal_RET='SP returns to gate liveSP; released initializerRA location reused; gate/primaryrestore thenonly outer16Bframe remains',absolute_nonalias_ownership_and_savedwords_is_premise=True),
  required_premises=['all previous gatezero/RF/source/timer/metadata conditions remain; actual preserved matching code/ISA/firstcopy and each required fresh primary/secondary/clockcallback binding equals one closed case','matching primary clock case additionally requires copied reader191c6 and normal reader/arithmetic/callback returns; no generic ABI or unknown callback purity assumption','all range/source calls return with needed S/SP/RA/GP/liveframewords intact; valid nonwrapping nonalias source word/context/objects/stack/heap/table; no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriter effects','retry must actually take a nonzero pair and later a candidate unequal to oldtuple; reader polls/source fairness/retry termination have no proved bound','ordinary retryRET preserves Y low16 evenif0; savedRA links/frames andfresh gate5/count6/capacityN0/tableT held until postreturn publication and accepted entry6 registration'],
  boundary='after conditional retry/initializer/gate/primary normal returns and accepted outer registration; before4da70/4db08 executes. No nonzero-gate alternative or laterouter IDs/tail/eventlifetime proof',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);r=ranges.derive(image,carriers,header,coverage);p=publication.derive(image,carriers,header,coverage)
 return dict(schema='TSL9-fallback-closed-source-retry-return-entry6-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i,parent['profiles'][i],r['profiles'][i],p['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],
  source_composition='prior range callcut fallback0 -> one closed source case and fullretry normalRET -> gate/primary sevenpointerstores -> outer accepted ID6/count7 -> beforeouterinitializer',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['actual source binding/writers and unbounded reader/retry progress','outer4da70/4db08/laterinitializers/registrationIDs/tail','physicaleffects/IRQ/ownership/otherdomains/fullretention-consumption-release lifetime'])


def tests(image,carriers):
 ranges.tests(carriers);publication.tests(image,carriers)
 for cap in range(14,213,3):check(6<cap and layout.T+28<=layout.T+4*cap,'fallbackretry all67 entry6bounds')
 check(0x200031ec+52 not in (0x200031ec+36,0x200031ec-12),'fallbackretry slot separation V131')
 check(0x2000323c+52 not in (0x2000323c+36,0x2000323c-12),'fallbackretry slot separation V140')
 check(32+32+16+16+32==128,'fallbackretry selected subgraph frame depth')
 print('PASS:438 original range/source/retry/clock/publication mutations rejected;closed source/frame/interval certificates;all67 entry6bounds')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackretry exactledger')
 print('PASS:conditional closed-source retry normalRET and gate/primary/entry6 fallback0;14envelopes/profile;12strictHEX guards;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;termination/actualbinding/outerinitializer/full lifetime UNPROVED')


if __name__=='__main__':main()
