"""Offline complete RF return chain and large common masked-word reply.
Immutable CFG/dominance/def-use certificates and host mask identities only.
No target execution/emulation, mutable MMIO/provider/callback/IRQ state model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_provider_app_static as previous
import check_v4160_post_rf_leaves_static as leaves
import check_v4160_rf_tail_return_static as tail
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-rf-reply-static.json')
SLICE=(0x160,0x1f6,0x1fa,0xccc,0xcd0,0xcd6,0xcd8,0xd32)


def guard_large(raw,index):
 pc=leaves.DETAILS[index][0][0];n=leaves.decode(raw,pc)
 specs={0x160:dict(op='load',rd=15,rs1=8,imm=1424+80*index,width=4),0x1f6:dict(op='lui',rd=10,imm=0xf1000000),0x1fa:dict(op='addi',rd=10,rs1=10,imm=-1),
  0xccc:dict(op='load',rd=14,rs1=15,imm=208,width=4),0xcd0:dict(op='and',rd=10,rs1=10,rs2=14),0xcd6:dict(op='or',rd=13,rs1=13,rs2=10),0xcd8:dict(op='store',rs1=15,rs2=13,imm=208,width=4),0xd32:dict(op='jr',rs1=1)}
 for o,f in specs.items():init.g(n,pc+o,'RFreply return-slice '+hex(o),**f)
 check(int.from_bytes(raw[0xccc:0xcd0],'little')&0x707f==0x2003,'RFreply fullword unsignedload')
 n,e=leaves.inspect(raw,'large',index)
 return n,e


def lastdefs(n,e,start,at,reg,preserved_calls=()):
 pred={a:[] for a in e}
 for a,zs in e.items():
  for z in zs:pred[z].append(a)
 todo=pred[at][:];seen=set();defs=set();entry=False
 while todo:
  a=todo.pop();d=n[a]
  if d.get('rd')==reg or (10<=reg<=17 and d['op'] in ('jal','jalr','call_indirect') and d.get('rd')==1 and a not in preserved_calls):defs.add(a-start);continue
  if a==start:entry=True
  if a not in seen:seen.add(a);todo.extend(pred[a])
 return defs,entry


def dominators(e,start):
 pred={a:[] for a in e}
 for a,zs in e.items():
  for z in zs:pred[z].append(a)
 dom={a:({start} if a==start else set(e)) for a in e};change=True
 while change:
  change=False
  for a in e:
   if a==start:continue
   v={a}|set.intersection(*(dom[z] for z in pred[a]))
   if v!=dom[a]:dom[a]=v;change=True
 return dom


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());lp=leaves.DETAILS[index][0][0];raw=init.binding.take(data,lp,3388);check(sparse.captured(mem,lp,3388)==raw,'RFreply large all3388B strictHEX');n,e=guard_large(raw,index);dom=dominators(e,lp);ret=lp+0xd32
 check([a-lp for a,d in n.items() if d.get('rd')==10]==[0x172,0x1f6,0x1fa,0xcd0],'RFreply allencodedA0defs')
 check(lastdefs(n,e,lp,ret,10)==({0xcd0},False) and lastdefs(n,e,lp,lp+0xcd0,10)==({0x1fa},False) and lastdefs(n,e,lp,lp+0x1fa,10)==({0x1f6},False),'RFreply completeA0 mask/reply reachingchain')
 check(lastdefs(n,e,lp,lp+0xcd0,14)==({0xccc},False) and lastdefs(n,e,lp,lp+0xccc,15)==({0x160},False),'RFreply freshword fromheldQ')
 check({lp+o for o in (0x154,0x160,0x1f6,0x1fa,0xccc,0xcd0)}<=dom[ret],'RFreply commonpointer/mask/read dominate soleRET')
 calls=[a-lp for a,d in n.items() if d['op']=='jalr' and d['rd']==1];check(calls==[0xa0,0xe2,0x12e] and max(calls)<0x154,'RFreply allopaque calls beforecommonjoin')
 check(n[lp+0xd38]['op']=='jal' and n[lp+0xd38]['rd']==0 and n[lp+0xd38]['target']==lp+0x154,'RFreply magic localjump rejoinscommon beforemask')
 check(n[lp+0xcc8]['op']=='store' and n[lp+0xcc8]['rs1']==15 and n[lp+0xcc8]['imm']==208 and lp+0xcc8 in dom[lp+0xccc],'RFreply freshread follows earlierstore; no readbackequality claim')
 check(n[lp+0xcd2]['imm']==15 and n[lp+0xcd4]['imm']==24 and n[lp+0xcd8]['rs2']==13,'RFreply laterstore insertsothernibble withoutchangingreply')
 paths={}
 for name,t in (('magic',0xd34),('nonmagic',0x78)):
  path=leaves.previous.paths.chain(e,lp,{lp+0x74:lp+t});seq=[int(a,16)-lp for a in path];check(seq[-1]==0xd32 and all(o in seq for o in SLICE),'RFreply bothcomplete paths traverse return-slice')
  check(all((a in seq)==(name=='nonmagic') for a in calls),'RFreply onlynonmagic traversesthreecallee normaledges');paths[name]=seq
 rp=tail.DETAILS[index][0][2];rr=init.binding.take(data,rp,232);check(sparse.captured(mem,rp,232)==rr,'RFreply outer232B strictHEX');rb=tail.body(rr,'tail',index);rn={d['pc']:d for d in rb['instructions']};re=tail.edge_map(rb);small={}
 for role in ('enable','wait','final'):
  k=leaves.ROLES.index(role);pc=leaves.DETAILS[index][0][k];z=leaves.SIZES[k];r=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==r,'RFreply allremainingleaves strictHEX');b=leaves.render_small(r,role,index);ns=b['instructions']
  check(all(d.get('rd') not in (1,2,3,8,9,10,*range(18,28)) for d in ns) and all(d['op'] not in ('jal','jalr','call_indirect') for d in ns),'RFreply leafnoA0/SP/RA/S/GPdefs/calls');small[role]=dict(start=pc,bytes=z,sha256=b['sha256'],instruction_count=len(ns),A0_nonwrite=True)
 preserved={rp+0x9a,rp+0x9e,rp+0xa2};check(lastdefs(rn,re,rp,rp+0xe6,10,preserved)==({0x96},True),'RFreply allouterRET sources largecall orentry')
 for o,role in ((0x96,'large'),(0x9a,'enable'),(0x9e,'wait'),(0xa2,'final')):check(rn[rp+o]['op']=='jal' and rn[rp+o]['target']==leaves.DETAILS[index][0][leaves.ROLES.index(role)],'RFreply outer exactcalleechain')
 early=[tail.selected(rb,choices) for choices in ({28:214},{28:32,34:214},{28:32,34:38,54:214})]
 for p in early:check(all(rn[int(a,16)].get('rd')!=10 and rn[int(a,16)]['op'] not in ('jal','jalr','call_indirect') for a in p),'RFreply eachouterearlypath retainsentryA0')
 sp=previous.previous.STARTS[index];sr=init.binding.take(data,sp,106);check(sparse.captured(mem,sp,106)==sr,'RFreply service106B strictHEX');sb=previous.previous.body(sr,index);sn={d['pc']:d for d in sb['instructions']};check(sn[sp+0x56]['target']==rp,'RFreply providerpostservice RFcall joinsouter')
 check(all(d.get('rd')!=10 and d['op'] not in ('jal','jalr','call_indirect') for a,d in sn.items() if sp+0x56<a<=sp+0x66),'RFreply servicekeepsRFword throughsnapshotstore/RET')
 magic=leaves.large_contract(data,index)
 return dict(label=init.binding.PROFILES[index][0],large=dict(start=lp,bytes=3388,sha256=sha256(raw).hexdigest(),instruction_count=len(n),return_slice=[n[lp+o] for o in SLICE],all_A0_definition_offsets=[0x172,0x1f6,0x1fa,0xcd0],all_linkedcall_offsets=calls,
  both_normalreturn_paths=paths,dominating_offsets=[0x154,0x160,0x1f6,0x1fa,0xccc,0xcd0],last_A0_definition=0xcd0,Q_definition=0x160,reply_fresh_word_load=0xccc,mask=0xf0ffffff,
  reply='fresh U32[held Q+208] & 0xf0ffffff',Q='fresh pointer fromG1424/1504 at+160;actualvalue maydiffer betweeninvocations',absoluteQ40025000_unconditionally_proved=False,
  magic_path_reused_frame_certificate=magic,nonmagic_calls_mustreturn_withneededS_SP_RA_frame_preservation=True,opaque_calls_neednotpreserveA0_for_final_common_mask=True),
  outer_RF=dict(start=rp,bytes=232,sha256=sha256(rr).hexdigest(),early_paths=early,early_reply='entry A0',main_reply='large maskedfreshword;later3leaves keepA0;waitmustexit',lastdefs=[0x96,'entry']),
  reused_leaves=small,postservice=dict(start=sp,RF_call=0x56,RF_link=0x5a,snapshot_store='low16(savedgetterX) toM8',reply='RF A0retained;differentfromsavedgetterX'),
  conditional_return_cases=['getterabsent:entryA0','matchinggetter andskipRF:U16X','admittedRF/early/optionalhookabsent:U16X','admittedRF/early/optionalhookpresent:mode3replyunknown','admittedRF/main:maskedfreshQ208word'],
  actualbindings_magicreachability_Qidentity_physicalreadback_pollcompletion_fullownership_proved=False)


def domains():
 mask=0xf0ffffff;cases=0
 check((0xf1000000-1)&0xffffffff==mask and (~mask&0xffffffff)==0x0f000000,'RFreply exactconstant/complement')
 for low in range(65536):
  for high in (0,0x0fff0000,0xf0000000,0xffff0000):
   word=high|low;reply=word&mask
   check(reply&0x0f000000==0 and reply&mask==reply and reply&(0xf0000000|0xffffff)==word&(0xf0000000|0xffffff),'RFreply maskbitidentity');cases+=1
 check(0xffffffff&mask==0xf0ffffff and 1&mask==1,'RFreply neitherfixedsuccessnorU16')
 return dict(fullword_boundary_family_cases=cases,cleared_bit_positions=list(range(24,28)),preserved_bit_positions=[*range(24),*range(28,32)],possible_masked_patterns_count=1<<28,actual_word_values_notproved=True,closed_host_scalar_identities_only=True,no_targetreadback_orMMIOmodel=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-RF-large-masked-word-return-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),reused_complete_RF_body_bytes=7684,reused_complete_RF_instructions=2402,new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['actualprovider/Qslot/magicwriters andnonmagicRAMcallee effects','physicalMMIOfreshread vspriorwrites/IRQordering andwaitprogress','sameN12writer/allocationretention/fullconsumption-release/notificationlifetimes'])


def tests(carriers):
 count=0
 def mutate(raw,pc,o,decode,guard):
  nonlocal count
  d=decode(raw,pc)[pc+o];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:guard(bad)
  except RuntimeError:pass
  else:raise RuntimeError('RFreply linkmutation escaped')
  count+=1
 for i,data in enumerate(carriers):
  lp=leaves.DETAILS[i][0][0];r=init.binding.take(data,lp,3388)
  for o in SLICE:mutate(r,lp,o,leaves.decode,lambda b:guard_large(b,i))
  rp=tail.DETAILS[i][0][2];r=init.binding.take(data,rp,232)
  for o in (0x96,0x9a,0x9e,0xa2):mutate(r,rp,o,tail.decode,lambda b:tail.body(b,'tail',i))
  for part in ('enable','wait','final'):
   k=leaves.ROLES.index(part);pc=leaves.DETAILS[i][0][k];r=bytearray(init.binding.take(data,pc,leaves.SIZES[k]));r[:4]=((int.from_bytes(r[:4],'little')&~(31<<7))|(10<<7)).to_bytes(4,'little')
   try:leaves.inspect(r,part,i)
   except RuntimeError:pass
   else:raise RuntimeError('RFreply A0nonwrite mutationescaped')
   count+=1
  pc=previous.previous.STARTS[i];r=init.binding.take(data,pc,106);mutate(r,pc,0x5a,previous.previous.decode,lambda b:previous.previous.guard(b,i))
 check(count==32,'RFreply mutationcensus');print('PASS:32 return-slice/callee/nonwrite/snapshot mutations rejected;allnormalRFreply joins')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'RFreply exactledger')
 print('PASS:large bothbranches return freshQ208 & f0ffffff;RFmain/early/service joins;strictHEX/dominance/exactledger')
 print('PASS:NO target execution/emulation;actualbinding/Qvalues/readback/pollprogress/fullownership UNPROVED')


if __name__=='__main__':main()
