"""Offline fallback preservation through selected timer and next task setup.

Original bytes/CFG and closed integer/interval/frame certificates only.
No target execution/emulation or mutable list/heap/RAM/provider/MMIO model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_wrapper_static as previous
import check_v4160_timer_provider_closure_static as closure

init,sparse,check=previous.init,previous.sparse,previous.check
timer,core,layout=closure.timer,closure.core,closure.timer.layout
OUT=Path(__file__).with_name('v4160-b1-fallback-timer-static.json')


def separated(a,z,b,w=4):return a+z<=b or b+w<=a


def deadline_certificate():
 period=0xffffffff;delta=1920000;rows=[]
 for start,end,carry,subtract in ((0,period-delta,False,False),(period-delta,period-delta+1,False,True),(period-delta+1,1<<32,True,True)):
  check(0<=start<end<=1<<32,'fallbacktimer nonempty deadline interval')
  # An affine relation over each full interval; endpoint bounds plus its
  # slope establish carry/threshold and one-subtraction bounds throughout.
  q=int(subtract)
  for R in (start,end-1):
   total=R+delta;low=total&0xffffffff
   check((total>=1<<32)==carry and (low<delta or low>=period)==subtract,'fallbacktimer deadline interval branch bounds')
   check(0<=total-q*period<period and total-q*period==total%period,'fallbacktimer full affine quotient interval')
   check(((low-period)&0xffffffff if subtract else low)==total-q*period,'fallbacktimer one subtraction vs modulo')
  rows.append(dict(R_start=start,R_end_exclusive=end,carry=carry,subtract_period=subtract,deadline_affine_constant=delta-q*period))
 check(rows[0]['R_start']==0 and rows[-1]['R_end_exclusive']==1<<32 and all(a['R_end_exclusive']==b['R_start'] for a,b in zip(rows,rows[1:])),'fallbacktimer entire U32 reader domain partition')
 return dict(period=period,delta=delta,intervals=rows,all_U32_R_covered=True,physical_clock_unit_or_event_delivery_proved=False)


def zero_failure_paths(data,index):
 pc=timer.DETAILS[index][0];raw=init.binding.take(data,pc,332);b=timer.body(raw,'service',index);n={d['pc']:d for d in b['instructions']};e=timer.edges(n)
 cr,ce=closure.core_body(init.binding.take(data,core.DETAILS[index][0],208),index);cc=core.ENTRY
 cp=timer.chain(ce,cc,{cc+a:cc+z for a,z in {22:24,24:38,56:60,76:80,88:26}.items()})
 offsets=[int(p,16)-cc for p in cp]
 check(84 in offsets and 96 not in offsets and not any(cr[int(p,16)]['op'] in ('jal','jalr','call_indirect') for p in cp),'fallbacktimer small-sentinel zero core no callback')
 cases=[]
 for adjust in ({208:216},{208:212,212:216},{208:212,212:220}):
  choices={44:48,56:70,130:162,232:248,266:268,276:60}|adjust
  sp=timer.chain(e,pc,{pc+a:pc+z for a,z in choices.items()});off=[int(p,16)-pc for p in sp]
  check(272 in off and 282 not in off and 296 not in off,'fallbacktimer failure reload excludes hook/node publication')
  defs=[n[int(p,16)] for p in sp if n[int(p,16)].get('rd')==10]
  check(defs[-1]['op']=='li' and defs[-1]['imm']==0,'fallbacktimer failure normal reply0')
  stores=[n[int(p,16)] for p in sp if n[int(p,16)]['op']=='store']
  check(all(d['rs1']==2 or d['imm']==524 for d in stores),'fallbacktimer failure own stores onlyframe/control')
  cases.append(off)
 return dict(core_offsets=offsets,timer_paths=cases,additional_fresh_condition='small_head == sentinelE, rather than nominal freeA; finite valid reads/frames/control/slot preserved',core_reply=0,timer_reply=0,core_and_timer_fallback_calls_absent=True,success_small_fit_premises_not_simultaneously_assumed=True)


def profile(data,hexraw,index,parent,tp,arith,reader):
 pc,co,service,copied,head,fall,*_=timer.DETAILS[index];ctx=0x20003000+co;slot=parent['fallback_slot'];head+=0x20003000;node=layout.A+8;rem=layout.A+24
 check(parent['conditional_result']['tail_jump']==0x19b54 and parent['conditional_result']['fallback_before_tail']==0 and parent['conditional_result']['tail_arguments']=={'A0':3,'A1':8192,'A2':192000},'fallbacktimer prior tail/zero/arguments join')
 check(slot==0x20003000+fall and init.binding.word(data,0x40058)==pc==parent['conditional_result']['candidate40058_word'],'fallbacktimer candidate40058/fallback join')
 _,mem=sparse.inspect(hexraw,sparse.parser());sources=[]
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];lsrc=int(mapping['source'],16)+0x20000314-int(mapping['destination'],16)
 for role,a,z in [('timer',pc,332),('lookup_firstcopy_source',lsrc,30),('core_firstcopy_source',core.DETAILS[index][0],208),('arithmetic',closure.previous.config.BASES[index],914),('lookup_table',closure.previous.config.BASES[index]+0xa42,16),('fill_firstcopy_source',(0x4060c,0x4064c)[index],46),('task_register',timer.registration.DETAILS[index][0],48),('slot40058',0x40058,4)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbacktimer strictHEX '+role);sources.append(dict(role=role,source=a,bytes=z,sha256=sha256(raw).hexdigest()))
 check(tp['service']['start']==hex(pc) and tp['lookup_candidate_source']==hex(lsrc),'fallbacktimer complete service/lookup joins')
 check(arith['selected_offsets']==list(closure.previous.PATH) and reader['GPR_writes']==[10,11,12,13,14,15],'fallbacktimer arithmetic/reader closure joins')
 node_fields=[(0,1,3),(1,1,1),(2,2,8192),(4,4,0),(8,4,'deadline'),(12,4,0)]
 check({x for a,z,_ in node_fields for x in range(a,a+z)}==set(range(16)),'fallbacktimer exact node16 field coverage')
 check(node+16==rem and rem+8+480==layout.B and layout.A+8+504==layout.B,'fallbacktimer small split geometry')
 effects=[]
 def add(role,a,z):
  check(0<=a<a+z<=1<<32 and separated(a,z,slot) and separated(a,z,previous.pub.TASK,1),'fallbacktimer projected effects exclude fallback/firsttask')
  effects.append(dict(role=role,address=a,bytes=z))
 for role,a,z in [('control',0x4002420c,4),('new_timer_head',head,4),('small_header',layout.A,8),('small_remainder_header',rem,8),('new_timer_payload',node,16),('core_account',ctx+6,2),('second_task_fill',0x2000be08,180),('second_task_callback',layout.T+16,4),('second_task_count',ctx+1,1),('second_task_saved_byte',previous.pub.GP+166,1)]:add(role,a,z)
 check(len(effects)==10,'fallbacktimer ten success/continuation interval envelopes')
 for cap in range(14,213,3):check(4<cap and layout.T+20<=layout.T+4*cap,'fallbacktimer second task admitted in all67 capacities')
 # Earlier post clear is an original source witness, not a retention assertion.
 postpc=timer.post.DETAILS[index][0];postraw=init.binding.take(data,postpc,272)
 postn=timer.post.decode(postraw,postpc);init.g(postn,postpc+4,'fallbacktimer earlier headzero source',op='store',rs1=15,rs2=0,imm=head-0x20003000,width=4)
 failure=zero_failure_paths(data,index)
 return dict(label=parent['label'],fallback_slot=slot,source_guards=sources,projected_success_and_secondtask_intervals=effects,
  earlier_headzero_source=dict(pc=postpc+4,address=head,value=0,retention_to_timer_fresh_head_samples_proved=False),
  arithmetic=dict(H0=16000,H1=16000,K=192000,divisor=1600,both_quotients=1920000,period=0xffffffff,threshold=0xfe363c7f,threshold_admits=True,actual_snapshot_coherence_or_time_units_proved=False),
  selected_success=dict(fresh_count=4,task=3,event=8192,lookup_head=0,small_head=layout.A,small_initial_next=layout.B,small_initial_size=504,small_initial_tag=0,node=node,node_fields=node_fields,remainder_header=rem,remainder_size=480,allocated_tag=0xff03,account_delta=-24,head_published_before_node_fields=True,normal_reply=1,fallback_after_timer=0,source_or_ownership_snapshot_proved=False),
  alternative_failure=failure,
  second_task=dict(timer_reply_ignored=True,APP_entry=0x907a,fill=[0x2000be08,0x2000bebc],callback=0x901a,entry4=layout.T+16,reply=4,count_after=5,saved_byte=previous.pub.GP+166,fallback_after=0),
  end_cut=dict(setup_return_link=0x8eb0,task_return_link=0x8eb2,before_indirect_call=0x8eb6,fallback=0,A0=4,A1=0,A2=5,target='fresh U32[then-live S0+416] & ~1; nominal401a0 only if S0=40000'),
  required_premises=['all previous source/getter/post IO alternatives/wrapper source and fallback-zero conditions remain; matching candidate40058/helper/reader/firstcopy/fill/40080 code and preserved mappings','fresh count4/retained copied reader191c6/periodffffffff/H16000 at required samples; no coherent-snapshot assumption from separate loads','head=0 remains through lookup and insertion; success additionally fresh smallA(nextB,size504,tag0), matching sentinelE/account/globalheaders/valid owned split extent; earlier post/bootstrap are sources, not a new proof of all intervening writers','failure is separate smallhead==E alternative; zero fallback must survive frame/control/external effects through both fresh fallback loads; this does not prove termination or arbitrary failed-search behavior','valid nonwrapping nonalias timer48B/core16B and caller/task16B frames, savedwords/registers/code/heap/metadata; no adverse MMIO/FENCE/IRQ/DMA/reentry/externalwriter effects; all required readers/calls/accesses finish','after either normal timer reply, task fill/registration must match, frames/GP preserved, fresh count4/capacityN0/tableT held until admitted secondregistration'],
  boundary='before fresh401a0 target executes; existing-node update/append/unknown nonzero fallback/other input domains and complete event delivery/retention/release remain unproved',actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);tp=timer.derive(image,carriers,header,coverage);reader=closure.reader(image[0x191c6-0x8000:0x19220-0x8000]);domains=closure.domains()
 profiles=[]
 for i,(data,h) in enumerate(zip(carriers,hexes)):
  ar=closure.previous.selected(init.binding.take(data,closure.previous.config.BASES[i],914),init.binding.take(data,closure.previous.config.BASES[i]+0xa42,16),i)
  profiles.append(profile(data,h,i,parent['profiles'][i],tp['profiles'][i],ar,reader))
 return dict(schema='TSL9-fallback-timer-smallfit-zero-failure-secondtask-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=profiles,deadline=deadline_certificate(),closed_clock_integer_domains=domains,
  source_composition='prior wrapper zero -> matching timer selected emptylist/smallfit normal1 OR separate smallsentinel/fallback0 normal0 -> setup907a task registration -> cut8eb6 beforefresh401a0',
  frame_certificate=dict(timer_bytes=48,allocator_child_bytes=16,APP_timer_subgraph_peak_bytes=64,secondtask_bytes=16,frames_physically_disjoint_from_protected_fields_is_premise=True),
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['head/smallheader/interveningwriter preservation and actualprovider/freshsource binding','fresh401a0/laterAPP/RF boundaries','otherlistpaths/allocatorfallback/IRQpollprogress/physicaleffects andfullretention-consumption-release lifetime'])


def tests(image,carriers):
 timer.tests(image,carriers);count=0
 for i,data in enumerate(carriers):
  pc=timer.DETAILS[i][0];raw=init.binding.take(data,pc,332);n=timer.decode(raw,pc)
  for off in (40,44,52,56,80,84,126,162,194,228,232,262,266,272,276,282,294,296,302,306,308,312,314,316,328):
   w=n[pc+off]['size'];bad=bytearray(raw);bad[off:off+w]=(int.from_bytes(bad[off:off+w],'little')^(4 if w==2 else 1<<20)).to_bytes(w,'little')
   try:timer.body(bad,'service',i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbacktimer mutated boundary escaped')
   count+=1
  zero_failure_paths(data,i)
 check(count==50,'fallbacktimer extra mutationcensus');deadline_certificate()
 print('PASS:50 additional timer source/branch/call/node/fallback mutations rejected; two separate zero-failure CFG certificates; fullU32 affine deadline partition')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbacktimer exactledger')
 print('PASS:conditional empty-list/smallfit OR separate zero-failure timer, second-task and fallback-zero to8eb6;10 interval envelopes/profile;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;head/headerretention/actualbinding/401a0/full lifetime UNPROVED')


if __name__=='__main__':main()
