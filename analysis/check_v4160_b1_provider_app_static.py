"""Offline APP field44/48 -> postpublication service callback and frame joins.
Complete existing byte guards plus field/frame/def-use/scalar certificates.
No target execution/emulation, RAM/provider/MMIO/callback/IRQ state model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_object_source_static as previous
import check_v4160_optional_hook_origin_static as origin
import check_v4160_app44_callback_static as getter
import check_v4160_app44_closure_static as closure
import check_v4160_mode3_frame_static as mode
import check_v4160_app_config_source_static as wrappers
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-provider-app-static.json')


def summary(b,name):
 return dict(start=b['start'],bytes=b['bytes'],sha256=b['sha256'],instruction_count=len(b['instructions']),complete_guard=name)


def app_proofs(image):
 source=origin.source
 builder=source.app_contract(image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE]);bn={d['pc']:d for d in builder['instructions']}
 uid=source.uid_contract(image[source.UID_PC-0x8000:source.UID_PC-0x8000+source.UID_SIZE]);leaf=origin.window(image[0x19aa4-0x8000:0x19ab4-0x8000],'source')
 for a,z,store,target,field in ((0x19a92,0x19a96,0x19a9e,0x197f0,44),(0x19aa4,0x19aa8,0x19ab2,0x197b8,48)):
  check(bn[a]['op']=='auipc' and a+bn[a]['imm']+bn[z]['imm']==target and bn[store]['rs2']==15 and bn[store]['rs1']==2 and bn[store]['imm']-16==field and bn[store]['width']==4,'providerapp APP numericcallbackfieldsource')
  later=[d for p,d in bn.items() if store<p<0x19aec and d['op']=='store' and d['rs1']==2]
  check(all(d['imm']+d['width']<=field+16 or field+20<=d['imm'] for d in later),'providerapp no later directframe sourcewordoverwrite')
 check(builder['UID_loop_source_SP_offsets']==list(range(8,14)) and builder['UID_loop_destination_SP_offsets']==list(range(40,46)) and uid['encoded_GPR_writes']==[13,14,15],'providerapp UID localextent excludesSP60..67')
 main=getter.callback_contract(image[getter.ENTRY-0x8000:getter.ENTRY-0x8000+getter.SIZE]);gn={d['pc']:d for d in main['instructions']};leaves=getter.leaves_contract(image)
 bodies=[closure.body(image[a-0x8000:b-0x8000],d) for d in closure.DETAILS for a,b in [d[:2]]]
 allowed={d[0] for d in closure.DETAILS}|{getter.POLL,getter.RESULT};check(all(t in allowed for _,t in getter.CALLS),'providerapp completeAPP44directclosure joined')
 check(gn[0x197f8]['rd']==10 and gn[0x197f8]['rs1']==2 and gn[0x197f8]['imm']==32 and gn[0x19814]['target']==0x8520,'providerapp getter replacesinheritedA0 byownscratch')
 check(gn[0x198dc]['target']==getter.RESULT and gn[0x198e0]['rs2']==10 and gn[0x198e0]['imm']==28 and gn[0x1991e]['imm']==28 and gn[0x19948]['rs2']==14,'providerapp resultleaf->savedword->finalA0')
 check(all(3 not in b['encoded_GPR_writes'] for b in [main]+leaves+bodies),'providerapp getterclosure noGPdefs')
 wrap=wrappers.body(image[0x197b8-0x8000:0x197be-0x8000],'mode_tail');wn={d['pc']:d for d in wrap['instructions']}
 check(wn[0x197b8]['rd']==10 and wn[0x197b8]['imm']==3 and wn[0x197ba]['target']==mode.PC and wn[0x197ba]['op']=='jal' and wn[0x197ba]['rd']==0,'providerapp optionalhook forcesmode3 andpreservesoriginalcalllink')
 reader=mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,mode.service.APP_HASHES[1]);defs=sorted({d['rd'] for d in reader['instructions'] if d.get('rd',0)})
 m=mode.body(image[mode.PC-0x8000:mode.END-0x8000],defs);check(len(m['saved_fields'])==13 and m['complete_function_bytes_CFG_and_memory_classification'],'providerapp mode completeframe/memory proof')
 return dict(builder=summary(builder,'check_v4160_config_buffer_source_static.py'),UID=summary(uid,'check_v4160_config_buffer_source_static.py'),field48_window=summary(leaf,'check_v4160_optional_hook_origin_static.py'),
  getter=summary(main,'check_v4160_app44_callback_static.py'),getter_leaves=[summary(b,'check_v4160_app44_callback_static.py') for b in leaves],getter_software_closure=[summary(b,'check_v4160_app44_closure_static.py') for b in bodies],
  mode_wrapper=summary(wrap,'check_v4160_app_config_source_static.py'),mode_callee=summary(m,'check_v4160_mode3_frame_static.py'),reader=summary(reader,'check_v4160_service_provider_link_static.py'),
  getter_result_chain=[0x198dc,0x198e0,0x1991e,0x19948],getter_conditional_reply_range=[0,65535],getter_entry_A0_notobjectpointer=True,optionalhook_mode_argument=3,optionalhook_reply_notforced3=True,
  required_premises=['matching originalAPP code/ISA and normalnestedaccesses/returns','savedSP28 resultword/context preservation and finitepolls','validnonaliasframes/protectedRAM distinctfromMMIO physicaleffects','nointerferingwriter/IRQ/DMA/reentry invalidatesflow'])


def frame_projection():
 # Relative to postpublication service entry SP=0; integer intervals only.
 service=set(range(-16,0));getterframe=set(range(-144,-16));getterextra=set(range(-160,-144));optionalwords=set(range(-68,-16));optionalscratch=set(range(-84,-80))
 check(not service&(getterframe|getterextra|optionalwords|optionalscratch),'providerapp nestedAPPframes belowservice saves')
 saved={'S0':[-8,-5],'S1':[-12,-9],'S2':[-16,-13],'RA':[-4,-1]}
 check(sum(hi-lo+1 for lo,hi in saved.values())==16,'providerapp fullservice savedframe extent')
 for r,o in mode.SAVED:check(set(range(-16-80+o,-16-80+o+4))<=optionalwords,'providerapp actualmode savedwordprojection')
 return dict(coordinate='offset fromserviceentrySP',service_saved_words=saved,getter_frame=[-144,-17],getter_nested_reserved_frame=[-160,-145],getter_maximum_nominal_depth=160,optional_mode_frame=[-96,-17],optional_mode_saved_words=[-68,-17],optional_mode_scratch=[-84,-81],encoded_frame_disjointness_only=True,physicalaliases_or_asyncpreservation_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());fd=origin.fallback.DETAILS[index];cfg,dest,hoff,boff=fd[2],fd[5],fd[9],fd[10]
 raw,n,e,defaults=origin.fallback.config_contract(data,cfg,dest,hoff,boff);check(sparse.captured(mem,cfg,228)==raw,'providerapp initializer strictHEX')
 check(init.binding.word(data,0x400a4)==cfg,'providerapp candidate initializer slot value')
 for off in (44,48):check(all(d['destination_field']+d['bytes']<=off or off+4<=d['destination_field'] for d in defaults),'providerapp fixeddefaults exclude callbackfields')
 check(n[cfg+92]['imm']==64 and n[cfg+96]['rs2']==9 and n[cfg+98]['imm']+0x20003000==dest,'providerapp exact64Bcopyprojection')
 pc=previous.STARTS[index];service=previous.body(init.binding.take(data,pc,106),index);sn={d['pc']-pc:d for d in service['instructions']}
 check(sparse.captured(mem,pc,106)==init.binding.take(data,pc,106),'providerapp fullservice strictHEX')
 getter_slot=sn[0]['imm']+sn[4]['imm']+sn[8]['imm'];hook_slot=sn[0]['imm']+sn[0x16]['imm']+sn[0x4e]['imm'];cache=0x20003000+sn[0x20]['imm']+sn[0x24]['imm']
 check((getter_slot,hook_slot)==(dest+44,dest+48),'providerapp consumer matchescopiedfield44/48')
 check(n[cfg+192]['imm']+0x20003000==cache and n[cfg+192]['width']==2 and sn[0x24]['width']==sn[0x5a]['width']==2,'providerapp initializerreplystore andservicecachedL samehalfword')
 check(n[cfg+182]['imm']==44 and n[cfg+186]['op']=='call_indirect' and n[cfg+186]['rs1']==15,'providerapp initializerinvokesfirstAPPfield44 beforecachedstore')
 check(sn[0x1a]['rs1']==14 and sn[0x54]['rs1']==15 and sn[0x26]['rs2']==10 and sn[0x5a]['rs2']==8,'providerapp actualcallee/savedfirstreply joins')
 return dict(label=init.binding.PROFILES[index][0],initializer=cfg,initializer_sha256=sha256(raw).hexdigest(),copy_destination=dest,getter_slot=getter_slot,optionalhook_slot=hook_slot,cache_halfword=cache,initial_cache_store=cfg+192,service=pc,service_sha256=service['sha256'],
  copy_sources=dict(field44=0x197f0,field48=0x197b8),service_calls=dict(getter=pc+0x1a,optionalhook=pc+0x54,RF=pc+0x56),
  conditional_result=['completednonalias64bytecopy andslotpreservation ->firsttarget197f0,optionaltarget197b8','matchinggetter normalreturn/preservedsavedresult ->X in0..65535','ifLnonzero,D=abs(X-L);strictD>20 admitshook/RF','optionalwrapperoverwritesincomingXwithmode3;normalreturnpreservescapturedX/S1cache/S2base/RA/SP','postRF normalreturn stores low16(savedX) tocache;finalA0 remainsRFreply,notnecessarilyU16'],
  cache_order='initializerfirstgetterreply ->halfwordcache;latergetter->freshcacheL->gates->optional/RF->savedXwrite. Crossinvocationorderandallwriters notproved',
  default_disjointness=defaults,unclosed_postcopy_boundaries=[cfg+206,'wrapperfresh40080','dynamicpostconfigwrites/otherwriters/IRQ'],
  actualinstalledbindings_fieldvalues_cacheinvariants_pointerownership_polltermination_proved=False)


def domains():
 cases=0
 for X in range(65536):
  for L in (0,1,20,21,65534,65535):
   d=(max(X,L)&65535)-(min(X,L)&65535);check(d==abs(X-L) and (d>20)==(X>L+20 or L>X+20),'providerapp U16 specialization andstrictthreshold');cases+=1
 for w in (0,65535,65536,0x12345678,0xffffffff):check(((w<<16)&0xffffffff)>>16==w&65535,'providerapp low16getterresult identity')
 return dict(U16X_and_Lboundary_cases=cases,absolute_difference_requiresmatchinggetterandpreservation=True,entireservice_reply_range_notrestrictedtoU16=True,zeroL_skipscachewrite_inthislocalpath=True,closed_host_scalar_identities_only=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-provider-APP-field44-field48-static-join-v1',APP_sha256=sha256(image).hexdigest(),APP_proofs=app_proofs(image),frame_projection=frame_projection(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['actualstartup/copy/providers/slotpreservation/cachewriters andIRQorder','RF641b0/6429a replyflow underthisentryA0/state andnestedcallees','B88/B100sameobjectN12writer/retainedallocation/fullconsumption-release/notificationlifetimes'])


def tests(image,carriers):
 count=0
 def mutate(raw,pc,at,decode,guard):
  nonlocal count
  d=decode(raw,pc)[at];z=d['size'];o=at-pc;bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:guard(bad)
  except RuntimeError:pass
  else:raise RuntimeError('providerapp linkmutation escaped')
  count+=1
 src=origin.source;r=image[src.APP_PC-0x8000:src.APP_PC-0x8000+src.APP_SIZE]
 for at in (0x19a92,0x19a96,0x19a9e,0x19aa4,0x19aa8,0x19ab2):mutate(r,src.APP_PC,at,src.cb.decode,src.app_contract)
 r=image[getter.ENTRY-0x8000:getter.ENTRY-0x8000+getter.SIZE]
 for at in (0x198e0,0x1991e,0x19948):mutate(r,getter.ENTRY,at,getter.decode,getter.callback_contract)
 r=image[getter.RESULT-0x8000:getter.RESULT-0x8000+8]
 for at in (getter.RESULT+2,getter.RESULT+4):mutate(r,getter.RESULT,at,getter.decode,lambda b:getter.leaf_contract(b,getter.RESULT,getter.RESULT_SHA))
 r=image[0x197b8-0x8000:0x197be-0x8000]
 for at in (0x197b8,0x197ba):mutate(r,0x197b8,at,wrappers.decode,lambda b:wrappers.body(b,'mode_tail'))
 for i,data in enumerate(carriers):
  pc=previous.STARTS[i];r=init.binding.take(data,pc,106)
  for off in (8,0x1a,0x24,0x26,0x4e,0x54,0x56,0x5a):mutate(r,pc,pc+off,previous.decode,lambda b:previous.guard(b,i))
 check(count==29,'providerapp exactlinkmutationcensus');print('PASS:29 source/call/result/field link mutations rejected;conditionalAPPprovider/frame/cache joins')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'providerapp exactledger')
 print('PASS:APP44/48->64Bcopy->postpublicationcalls;U16getter/absolute-difference/mode3/cache/frame;strictHEX/exactledger')
 print('PASS:NO target execution/emulation;actualbinding/pollprogress/RFreply/fullownership UNPROVED')


if __name__=='__main__':main()
