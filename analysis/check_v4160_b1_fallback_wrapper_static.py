"""Offline fallback preservation through constructor/config to wrapper tail.

Original bytes/CFG/def-use, closed interval and frame-offset certificates only.
No target execution/emulation or mutable RAM/heap/MMIO/provider/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_app_static as previous
import check_v4160_registration_return_chain_static as returns

init,sparse,check=previous.init,previous.sparse,previous.check
pub=returns.previous
OUT=Path(__file__).with_name('v4160-b1-fallback-wrapper-static.json')


def app_closure(image,carriers,header,coverage):
 r=returns.derive(image,carriers,header,coverage)
 p=pub.derive(image,carriers,header,coverage)
 pre=pub.pre.derive(image,carriers,header,coverage)
 reader=pub.mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,pub.mode.service.APP_HASHES[1])
 defs=sorted({d['rd'] for d in reader['instructions'] if d.get('rd',0)})
 mode=pub.mode.body(image[pub.mode.PC-0x8000:pub.mode.END-0x8000],defs)
 effects=set()
 for role,e in pre['MMIO_encoded_contracts'].items():
  if role=='19272':continue  # Poll reads only; neither a write nor a progress proof.
  for a in e.get('addresses',[e.get('address')]):effects.add((int(a,16),e['width']))
 check(len(effects)==10,'fallbackwrapper ten pre-call MMIO interval envelopes')
 mode_stores=[d for d in mode['memory_accesses_with_origin_proofs'] if d['op']=='store' and d['address'].startswith('0x')]
 check(len(mode_stores)==36,'fallbackwrapper mode36 fixed stores')
 mode_effects={(int(d['address'],16),d['width']) for d in mode_stores}
 check(len(mode_effects)==4,'fallbackwrapper four mode MMIO interval envelopes')
 check(not reader['calls'] and not any(d['op']=='store' for d in reader['instructions']),'fallbackwrapper reader no stores/calls')
 wrapper=pub.app.body(image[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
 constructor=pub.app.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct')
 check(p['nominal_GP']==hex(pub.GP) and pub.TASK==pub.GP+388==0x20004184,'fallbackwrapper GP/task join')
 check(all(q['conditional_published_service_word']=='0x191c6' for q in p['profiles']),'fallbackwrapper published reader join')
 # C is the constructor's live SP. These are footprints, not a stack image.
 frames={'constructor_config':[(0,16)],'constructor_saved_RA':[(28,4)],'wrapper_frame':[(32,16)],
  'pre_pair_child': [(-20,4),(-4,4)],'pre_mode_child':[(-68,4),(-52,52)],
  'provider_saves':[(-20,4),(-8,8)],'provider_optional_mode_child':[(-100,4),(-84,52)],
  'registration_saved_RA':[(-36,4)],'immediate_callback_saves':[(-76,28)]}
 protected=set(range(16))|set(range(28,48))
 for role,intervals in frames.items():
  if role in ('constructor_config','constructor_saved_RA','wrapper_frame'):continue
  for a,z in intervals:check(not set(range(a,a+z))&protected,'fallbackwrapper child offsets exclude live constructor/wrapper fields')
 return r,p,dict(pre_call_MMIO_envelopes=sorted(effects),mode_MMIO_envelopes=sorted(mode_effects),mode_store_sites=36,
  original_APP_guards=[dict(role=k,start=b['start'],bytes=b['bytes'],sha256=b['sha256']) for k,b in [('wrapper',wrapper),('construct',constructor),('mode3',mode),('reader',reader)]],
  thirteen_pre_calls=constructor['calls'][:-1],constructor_config=pub.CONFIG.hex(),frame_offsets_relative_to_constructor_SP=frames,
  reader_no_stores_or_calls=True,full_callback_arithmetic_no_stores_or_calls=True,
  required_frame_condition='absolute live/child frames valid, owned, nonwrapping and separated from fallback/task/metadata/code/other live fields; saved words preserved',
  progress_boundary='four19272 calls and mode/reader waits must complete normally; no eventual return/time/hardware success claim')


def profile(data,hexraw,index,parent,r,p,common):
 _,mem=sparse.inspect(hexraw,sparse.parser());slot=parent['fallback_slot'];task=pub.TASK
 check(parent['conditional_result']['cut_at_registration_return_link']==0x19b30 and parent['conditional_result']['fallback_at_cut']==0 and parent['conditional_result']['reply_at_cut']==3,'fallbackwrapper prior zero/reply join')
 effects=[dict(role='wrapper_task_byte',address=task,bytes=1)]
 def add(role,a,z):
  check(0<=a<a+z<=1<<32 and previous.previous.separated(a,z,slot),'fallbackwrapper excludes fallback')
  check(previous.previous.separated(a,z,task,1),'fallbackwrapper later effects preserve task byte')
  effects.append(dict(role=role,address=a,bytes=z))
 check(previous.previous.separated(task,1,slot),'fallbackwrapper task store excludes fallback')
 for a,z in common['pre_call_MMIO_envelopes']:add('pre_call_MMIO_envelope',a,z)
 for a,z in common['mode_MMIO_envelopes']:add('pre_or_optional_mode_MMIO_envelope',a,z)
 add('copy_control_save_restore',0x4002420c,4)
 for e in p['fixed_direct_RAM_writes']:add('selected_provider_RAM',int(e['address'],16),e['bytes'])
 add('immediate_callback_registration_slot',int(r['callback_slot'],16),4)
 add('callback_Q_then_registration_delta_same_word',int(r['prior_and_final_result_word'],16),4)
 check(len(effects)==21+index,'fallbackwrapper exact interval envelope census')
 gd=pub.gates.DETAILS[index];regpc,cbpc=returns.DETAILS[index][:2];arpc=pub.arithmetic.BASES[index]
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy']
 src=int(mapping['source'],16)+0x20000332-int(mapping['destination'],16)
 sources=[]
 for role,a,z in [('provider40074',gd[0],gd[1]),('immediate_registration',regpc,30),('immediate_callback',cbpc,130),('general_arithmetic',arpc,914),('normalization_lookup',arpc+0xa42,16),('copied_software_copy',src,58),('candidate40074_word',0x40074,4),('candidate40058_word',0x40058,4)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackwrapper strictHEX '+role)
  sources.append(dict(role=role,source=a,bytes=z,sha256=sha256(raw).hexdigest()))
 check(init.binding.word(data,0x40074)==gd[0] and p['candidate40074']==hex(gd[0]),'fallbackwrapper candidate40074 join')
 check(p['conditional_copied_16bytes']==pub.CONFIG.hex() and len(p['paths'])==4,'fallbackwrapper config exact16 and four selected hook/state paths')
 check(r['registration_return_zero'] and r['config_return_zero'] and int(r['copied_reader_word'],16)==int(p['copied_config'],16),'fallbackwrapper callback/config return joins')
 check(int(r['prior_and_final_result_word'],16)==0x20003000+returns.DETAILS[index][3],'fallbackwrapper callback/reg same result address')
 # Callback Q/delta are unconstrained scalar values stored at the fixed result
 # address; they are not dereferenced as writable pointers by these bodies.
 return dict(label=parent['label'],fallback_slot=slot,task_byte=task,projected_effect_intervals=effects,resident_strictHEX_guards=sources,
  config_source=pub.CONFIG.hex(),optional_hook_cases=['fresh zero','fresh197b8 with matching full mode3/reader closure'],fresh_state23_cases=['zero -> specialized arithmetic ->22','nonzero -> no arithmetic/store'],
  provider_copy=dict(bytes=16,destination=int(p['copied_config'],16),published_reader=0x191c6,software_copy_source=src,required_source_stability_and_nonaliasing=True),
  immediate_callback=dict(entry=cbpc,reader='fresh copied word191c6 with matching reader body',Q_and_delta_numeric_values_proved=False,store_word=int(r['prior_and_final_result_word'],16),registration_overwrites_callback_Q_with_delta=True,registration_reply=0),
  conditional_result=dict(entry_cut=0x19b30,entry_fallback=0,task_byte_after_store=3,constructor_normal_return_fallback=0,constructor_reply=0,tail_jump=0x19b54,fallback_before_tail=0,tail_arguments={'A0':3,'A1':8192,'A2':192000},candidate40058_word=int(r['candidate40058_word'],16),tail_target='fresh U32[then-liveS1+88] & ~1; nominal slot40058 only if S1=40000 at load19b40'),
  required_premises=['all prior source/getter/post IO alternatives/nominal heap/APP/first-registration conditions remain in force','nominal GP20004000 is established and preserved at19b30; required fresh40074/code/firstcopy bindings match candidate, not a proven installed image','all13 constructor precalls and optional zero-or197b8 hook path complete normally; mode/reader polls/accesses are not proved to progress','source constructor16bytes, copied16bytes and published reader remain intact at fresh samples; config byte12=0 and nonzero gate fields as proved under source/frame conditions','fresh callback/copy/arithmetic code, metadata and live saved frame words preserved; valid nonwrapping physical accesses/owned nonaliasframes and no adverse IRQ/DMA/reentry/externalwriter/MMIO/FENCE effects'],
  actual_installed_binding_or_full_lifetime_proved=False,boundary='before19b54 tail target executes; no40058/param774/RF effects or cross-event retention/consumption/release proof')


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);r,p,c=app_closure(image,carriers,header,coverage)
 return dict(schema='TSL9-fallback-constructor-config-callback-wrapper-tail-preservation-v1',APP_sha256=sha256(image).hexdigest(),common=c,
  profiles=[profile(d,h,i,parent['profiles'][i],r['profiles'][i],p['profiles'][i],c) for i,(d,h) in enumerate(zip(carriers,hexes))],
  composition='conditional fallback0 at19b30 -> wrapper taskbyte3 -> all13 pre-calls -> matching40074 source/copy/publication/immediate callback/registration -> constructorRET -> wrapper fresh taskbyte3 and tail args; cut before fresh40058 target',
  C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['fresh40058/param774/RF target and subsequent boundaries','actual GP/provider/startup/firstcopy/freshfields/physical mapping/IRQ progress','unknown hook/other source domains/external writers and full retention-consumption-release lifetime'])


def tests(image,carriers):
 cases=[]
 for role,pc,z,_,_ in pub.app.DETAILS:
  raw=image[pc-0x8000:pc-0x8000+z];cases.append((raw,pc,list(pub.app.decode(raw,pc)),lambda b,role=role:pub.app.body(b,role)))
 for role,pc,z,_,_ in pub.pre.DETAILS:
  raw=image[pc-0x8000:pc-0x8000+z];cases.append((raw,pc,list(pub.pre.decode(raw,pc)),lambda b,role=role:pub.pre.body(b,role)))
 role,pc,z,num,stores,digest=next(d for d in pub.pre.setup.DETAILS if d[0]=='clock1c')
 raw=image[pc-0x8000:pc-0x8000+z];cases.append((raw,pc,list(pub.pre.decode(raw,pc)),lambda b,role=role,pc=pc,z=z,num=num,stores=stores,digest=digest:pub.pre.setup.body(b,role,pc,z,num,stores,digest)))
 reader=pub.mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,pub.mode.service.APP_HASHES[1]);defs=sorted({d['rd'] for d in reader['instructions'] if d.get('rd',0)})
 raw=image[pub.mode.PC-0x8000:pub.mode.END-0x8000];cases.append((raw,pub.mode.PC,[s[0] for s in pub.mode.STORES],lambda b:pub.mode.body(b,defs)))
 for i,data in enumerate(carriers):
  pc,z=pub.gates.DETAILS[i][:2];raw=init.binding.take(data,pc,z);cases.append((raw,pc,list(pub.gates.decode(raw,pc)),lambda b,i=i:pub.gates.body(b,i)))
  for role,pc,z in [('registration',returns.DETAILS[i][0],30),('callback',returns.DETAILS[i][1],130)]:
   raw=init.binding.take(data,pc,z);cases.append((raw,pc,list(returns.decode(raw,pc)),lambda b,role=role,i=i:returns.body(b,role,i)))
  pc=pub.arithmetic.BASES[i];raw=init.binding.take(data,pc,914);cases.append((raw,pc,[pc+o for o in (8,12,18,26,46,56,186,188,226,350,384,414,818,912)],lambda b,pc=pc:returns.arithmetic(b,pc)))
  m=init.binding.profile(data,init.binding.PROFILES[i][0])['first_copy'];src=int(m['source'],16)+0x20000332-int(m['destination'],16);raw=init.binding.take(data,src,58)
  cases.append((raw,0x20000332,list(pub.payload.decode(raw,0x20000332)),lambda b:pub.payload.body(b,'copy',0x20000332,58,18,3,init.binding.COPY_HASH)))
 count=0
 for raw,pc,pcs,guard in cases:
  n=returns.decode(raw,pc)
  for p in pcs:
   o=p-pc;w=n[p]['size'];bad=bytearray(raw);bad[o:o+w]=(int.from_bytes(bad[o:o+w],'little')^(4 if w==2 else 1<<20)).to_bytes(w,'little')
   try:guard(bad)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackwrapper original mutationescaped')
   count+=1
 check(count==557,'fallbackwrapper mutationcensus '+str(count))
 print('PASS:557 original wrapper/constructor/prehelper/mode/config/callback/arithmetic/copy mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackwrapper exactledger')
 print('PASS:conditional fallback-zero constructor/config/callback/wrapper19b54 certificates;21/22 interval envelopes;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware or targetnetwork;fresh40058/actualbinding/full lifetime UNPROVED')


if __name__=='__main__':main()
