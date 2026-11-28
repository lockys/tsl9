"""Offline config private-release return/write cases and conditional Q preservation.

Original byte/CFG/def-use guards and closed scalar/byte-lane identities only.
No target execution/emulation or mutable heap/register/RAM/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_q_allocator_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
release=previous.core.message.release
caller=previous.previous.binding
reply=previous.previous.reply
OUT=Path(__file__).with_name('v4160-b1-q-release-static.json')


def guard(raw,index):
 n=release.decode(raw);s=release.specifications(release.DETAILS[index]);check(set(n)==set(s),'Qrelease completeboundaries')
 for a,f in s.items():init.g(n,a,'Qrelease operand '+hex(a-release.ENTRY),**f)
 check(len(raw)==212 and len(n)==73 and sha256(raw).hexdigest()==release.DETAILS[index][-1],'Qrelease fullidentity')
 e,cycles,dom=release.graph(n)
 check(len(cycles)==1 and set(cycles[0])=={hex(release.ENTRY+o) for o in (44,48,52,56,206,208,210)},'Qrelease traversal SCC')
 check(not any(n[int(a,16)]['op'] in ('store','jal','jalr','call_indirect') for a in cycles[0]),'Qrelease traversal SCC readonly')
 check(not any(d['op'] in ('jal','jalr','call_indirect') for d in n.values()),'Qrelease no nestedcalls')
 check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[6,10,11,12,13,14,15,16,17,28],'Qrelease exact GPRdefs noS/SP/RA/GP')
 check(release.ENTRY+18 in dom[release.ENTRY+22] and [a for a,d in n.items() if d.get('rd')==16]==[release.ENTRY+4],'Qrelease controlrestore/savedvalue')
 return n,e,dom


def paths(e,start):
 out=[];todo=[(start,())]
 while todo:
  a,path=todo.pop();check(a not in path,'Qrelease suffix acyclic');path=path+(a,)
  if e[a]:todo.extend((z,path) for z in e[a])
  else:out.append(path)
 return out


def domains():
 lanes=[];word=0x40025000;old=tuple(word>>(8*j)&255 for j in range(4))
 for a in range(-1,4):
  overlap=[(j,j-a) for j in range(4) if 0<=j-a<2]
  compatible=all(old[j]==(73>>(8*k)&255) for j,k in overlap)
  unchanged=all(old[j]==0 for j,k in overlap)
  lanes.append(dict(tag_address_minus_Q=a,overlap_Q_lanes=[j for j,k in overlap],fresh_tag73_compatible=compatible,zero_store_preserves_Q_lanes=unchanged))
 check([r['tag_address_minus_Q'] for r in lanes if r['fresh_tag73_compatible']]==[-1] and all(not r['fresh_tag73_compatible'] or r['zero_store_preserves_Q_lanes'] for r in lanes),'Qrelease nomerge tag73 valuelemma')
 check(sum(z==0x8001 for z in range(65536))==1 and 73!=0x8001,'Qrelease exactcountertagguard')
 for oldcounter in range(256):check((oldcounter+1)&255==(0 if oldcounter==255 else oldcounter+1),'Qrelease counterwrap')
 cases=0
 for oldaccount in range(65536):
  for p in (0,1):
   for n in (0,1):
    merges=p+n
    for B in range(256,265):
     check((((oldaccount-256)&65535)+B+8*merges)&65535==(oldaccount+B-256+8*merges)&65535,'Qrelease no-split allocation-release closedaccountidentity');cases+=1
    check((((oldaccount-264)&65535)+256+8*merges)&65535==(oldaccount+8*(merges-1))&65535,'Qrelease split allocation-release closedaccountidentity');cases+=1
 check(cases==2621440,'Qrelease accountcasecensus')
 # Closed interval arithmetic: either exact P or interior/inclusive next may
 # satisfy these encoded comparisons. No list or target memory is constructed.
 H,K=0x1000,0x1020;admitted=[P for P in range(H,K+1) if H<=P<=K and P>=H+8]
 check(admitted==list(range(0x1008,0x1021)),'Qrelease notexactpayload range')
 print('PASS:2621440 closed accounting cases;65536 tag values/256 counter wraps;range and Q/tag-lane certificates')
 return dict(nomerge_tag73_Q_lane_cases=lanes,counter_trigger_tag=0x8001,allocation_tag73_triggers_counter=False,account_cases=cases,
  account_credit='(B+8*previous_merge+8*next_merge) mod2^16 understable/nonaliasaccount andheader reads',
  previous_R256_allocation_size_domain=[256,264],roundtrip_nosplit_net='B-256+8*(previous_merge+next_merge)',roundtrip_split_net='8*(previous_merge+next_merge-1)',
  exact_payload_start_required_by_encoded_guard=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());entry=release.ENTRY;src,head,limit,counter,account,boundary,digest=release.DETAILS[index]
 raw=init.binding.take(data,src,212);check(sparse.captured(mem,src,212)==raw,'Qrelease strictHEX wholefree');n,e,dom=guard(raw,index)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+entry-int(fc['destination'],16)==src and entry+212<=int(mapping['first_copy_end_exclusive'],16),'Qrelease complete conditional RAMmapping')
 cd=previous.core.DETAILS[index];check((head,limit,boundary,account)==(cd[1],cd[3],cd[2],cd[5]),'Qrelease free smallhead/limit/largehead/account joinscore')
 cp=caller.STARTS[index][0];cr=init.binding.take(data,cp,318);check(sparse.captured(mem,cp,318)==cr,'Qrelease strictHEX caller');cb=caller.body(cr,'config',index);cn={d['pc']-cp:d for d in cb['instructions']}
 check(next(c['target'] for c in cb['calls'] if c['offset']==170)==entry,'Qrelease directprivatecallee join')
 check((cn[158]['op'],cn[158]['rd'],cn[158]['rs1'],cn[158]['imm'],cn[158]['width'])==('load',10,15,4,4),'Qrelease fresholdC4 argument')
 check((cn[164]['op'],cn[164]['rs1'],cn[164]['target'])==('beqz',10,cp+174),'Qrelease nullargument callguard')
 check(cn[174]['op']=='load' and cn[174]['rd']==15 and cn[174]['width']==1 and (cn[178]['op'],cn[178]['rs1'],cn[178]['rs2'],cn[178]['imm'],cn[178]['width'])==('store',9,0,4,4),'Qrelease freshflag then unconditionalC4clear')
 check(cn[182]['op']=='andi' and cn[182]['rs1']==15 and cn[182]['imm']==1 and cn[184]['op']=='beqz' and cn[184]['rs1']==15,'Qrelease subsequentbranch usesfreshflag notprivateA0')
 check(cn[202]['op']=='store' and cn[202]['rs2']==10 and cn[202]['imm']==4 and cn[206]['op']=='li' and cn[206]['rd']==10 and cn[206]['imm']==0,'Qrelease laterallocator mayreplaceC4/configforced0')
 defs,entryarg=reply.lastdefs(n,e,entry,entry+22,10);check(defs=={96,128,136} and entryarg,'Qrelease completeA0 lastdefinition classification')
 allsuffix=paths(e,entry+68);tag73=[seq for seq in allsuffix if entry+88 not in seq];check((len(allsuffix),len(tag73))==(32,16),'Qrelease allsuffix/tag73 pathcounts')
 check([a-entry for a,d in n.items() if d['op']=='store']==[8,18,88,104,118,142,152,154,190,192,198],'Qrelease exact11stores')
 groups={};q=0x20003590+80*index;F=0x20003540+80*index;C=F+32
 protected=[('Q',q,4),('F',F,32),('C',C,36)];fixed=[dict(role='control',address=0x4002420c,bytes=4),dict(role='counter_if_tag8001',address=counter,bytes=1),dict(role='account',address=account+6,bytes=2)]
 for x in fixed:
  for label,a,z in protected:check(previous.previous.separated(x['address'],x['bytes'],a,z),'Qrelease fixed numericstores excludeQ/F/C')
 for seq in tag73:
  p=entry+142 in seq;t=entry+190 in seq;key=f'previous{int(p)}_next{int(t)}';U='J' if p else 'H'
  offsets=[a-entry for a in seq if n[a]['op']=='store'];want=[104,118]+([142,152,154] if p else [])+([190,192,198] if t else [])+[18]
  check(offsets==want,'Qrelease completecase storesequence')
  effects=[dict(offset=104,address='H+6',bytes=2),dict(offset=118,address=account+6,bytes=2)]
  if p:effects.extend([dict(offset=142,address='J+0',bytes=4),dict(offset=152,address='J+4',bytes=2),dict(offset=154,address=account+6,bytes=2)])
  if t:effects.extend([dict(offset=190,address=U+'+4',bytes=2),dict(offset=192,address=U+'+0',bytes=4),dict(offset=198,address=account+6,bytes=2)])
  effects.append(dict(offset=18,address=0x4002420c,bytes=4))
  for x in effects:check(n[entry+x['offset']]['width']==x['bytes'],'Qrelease projectedcase exactwidth')
  g=groups.setdefault(key,dict(previous_merge=p,next_merge=t,tag73_syntactic_paths=0,active_header_after_previous_merge=U,matched_suffix_effects=effects,account_credit_formula=f'(B+{8*(int(p)+int(t))}) mod2^16',next_pointer_register_used_as_store_base=False));g['tag73_syntactic_paths']+=1
 check({k:v['tag73_syntactic_paths'] for k,v in groups.items()}=={'previous0_next0':9,'previous0_next1':3,'previous1_next0':3,'previous1_next1':1},'Qrelease fourcase pathpartition')
 # Heap metadata stores use the current or previous header as base, never the
 # fresh next-pointer register. Header address/physical aliases remain separate.
 check((n[entry+142]['rs1'],n[entry+152]['rs1'],n[entry+156]['rs2'],n[entry+156]['rd'],n[entry+190]['rs1'],n[entry+192]['rs1'])==(13,13,13,15,15,15),'Qrelease previous/activeheader baseorigins')
 for label,a,z in protected:check(a+z<previous.previous.layout.A<previous.previous.layout.E,'Qrelease nominalarena disjointprotecteddata')
 return dict(label=init.binding.PROFILES[index][0],Q_slot=q,F=F,C=C,private_release=dict(source=src,target=entry,bytes=212,instructions=73,sha256=digest,stores=11,local_frame_or_nested_calls=False,slots=dict(small_head=head,limit_sentinel=limit,large_head_boundary=boundary,counter=counter,account=account)),
  caller=dict(call=cp+170,oldC4_load=cp+158,nullguard=cp+164,freshflag_load=cp+174,clearC4=cp+178,optional_allocator=cp+198,replaceC4=cp+202,config_forced0=cp+206,private_reply_used_as_status=False),
  input_match='cur<limit;cur<=entryP<=capturednext;entryP>=((cur+8)mod2^32);notexactpayload/ownership validation',
  return_certificate=dict(last_encoded_A0_definitions=[96,128,136],entry_A0_may_reach_RET=True,unmatched='entryP',matched_small_head='accountbase',matched_large_boundary='freshlargeheadvalue',other_matched='freshU16[previous+6];0ifpreviousmerge',status_or_release_success=False),
  path_certificate=dict(all_matched_suffix_paths=32,tag73_paths=16,tag73_paths_sha256=sha256(json.dumps(tag73,separators=(',',':')).encode()).hexdigest(),cases=groups),
  fixed_write_intervals=fixed,Q_preservation=dict(nomerge_tag73='freshentryQ40025000/tag73 read consistent inordinarybyteimage;zero-tagstore preservesQ evenifone benignbyteoverlap;fixedeffects excluded',merging='H andpreviousJ ifwritten havevalidnonwrappingheaderwriteintervals disjointQ;nextpointer register notstorebase,butheaderaliases remainpossible',owned_arena_corollary='allwrittenH/J8Bheaders inownednonwrappingarena[200043ac,2000b184) alsoexcludeF32/C36/Q4;notactualfreshownershipproof'),
  config_join='normalprivate-return restorescontrol;configfreshF0 read thenC4zero regardlessprivateA0;laterallocator mayreplaceC4;Qpersists onlyunderselectedfreecase andsubsequentcaller/allocator premises',
  required_premises=['all matchingcode/ISA/firstcopy/context/frame/ordinarysource/nonalias/IRQ/DMA/reentry premises frompreviousphases','finitevalidtraversal andnormalaccesses;inputmayinterior/inclusivenext,so matchingpreviousallocationrequiresactualsameheader/links/size/tag/sourcepreservation','tag73specialization needsfreshmatchedtag73;earlierallocationtagstore alone notfreshproof','accountcredit identities requirestable/nonaliasheader-account reads;nomergeQlemma usesconsistent ordinarylittleendian byteimage/validcompletion','ifusingownedarena,F/Csource snapshots preservedacrossprivatefree;actualheader/arenaownership stillunproved','no state-basedsuccess/completeownership/fullretention/nextheadererasure/postfreepointervalidity claim'],
  actual_provider_fresh_list_ownership_termination_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-config-private-release-merge-return-Q-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,remaining=['freshmatchedH/J/next/tag/size/ownership/finitevalidtraversal','nonnullfallback/actualprovider/mapping/interveningcalls/IRQprogress','allocation-retention-consumption-release/notificationlifetime;postfreeC4aliases'])


def tests(carriers):
 count=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,release.DETAILS[i][0],212);n,_,_=guard(raw,i)
  for o in (44,52,56,60,64,68,74,88,96,100,104,118,120,128,132,136,138,142,152,154,156,158,160,168,172,176,178,190,192,198):
   z=n[release.ENTRY+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('Qrelease mutationescaped')
   count+=1
 check(count==60,'Qrelease mutationcensus');print('PASS:60 original traversal/tag/merge/account/return mutations rejected')
 joins=0
 for i,data in enumerate(carriers):
  pc=caller.STARTS[i][0];raw=init.binding.take(data,pc,318);b=caller.body(raw,'config',i);n={d['pc']:d for d in b['instructions']}
  for o in (158,164,170,174,178,182,184):
   z=n[pc+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:caller.body(bad,'config',i)
   except RuntimeError:pass
   else:raise RuntimeError('Qrelease callerjoinmutationescaped')
   joins+=1
 check(joins==14,'Qrelease joinmutationcensus');print('PASS:14 original oldC4/call/freshflag/clear/branch mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'Qrelease exactledger')
 print('PASS:config direct private-release/merge footprints/nonstatus returns/Q-preservation cases;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork;actualownership/lifetime UNPROVED')


if __name__=='__main__':main()
