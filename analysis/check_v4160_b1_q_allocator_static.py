"""Offline RF config direct allocator inputs, writes and Q preservation cases.

Original instruction/CFG guards plus closed scalar and byte-lane equalities.
No target execution/emulation, mutable heap/register/RAM/MMIO/provider model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_q_return_static as previous
import check_v4160_allocation_core_static as core

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-q-allocator-static.json')
MASK=0xffffffff


def guard(raw,index):
 n=core.decode(raw);s=core.specs(core.DETAILS[index]);check(set(n)==set(s),'Qalloc completecore boundaries')
 for a,f in s.items():core.message.guard(n,a,'Qalloc core operand '+hex(a-core.ENTRY),**f)
 check(len(raw)==208 and sha256(raw).hexdigest()==core.DETAILS[index][-1],'Qalloc fullcoreidentity')
 topology={a:dict(d,op='bne') if d['op']=='bltu' else d for a,d in n.items()};edges,cycles=core.timer.cfg(topology,core.ENTRY)
 e={int(a,16):[int(z,16) for z in zs] for a,zs in edges.items()}
 expected={core.ENTRY+o for o in (76,110,112,114,116,204,206)}
 check(len(cycles)==1 and set(map(lambda x:int(x,16),cycles[0]))==expected,'Qalloc search SCC')
 check(all(n[a]['op'] not in ('store','jal','jalr','call_indirect') for a in expected),'Qalloc search SCC noencodedstores/calls')
 return n,e


def ancestors(e,target):
 pred={a:[] for a in e}
 for a,zs in e.items():
  for z in zs:pred[z].append(a)
 return core.reachable(pred,target)


def lane_cases(word,tag):
 old=tuple(word>>(8*j)&255 for j in range(4));rows=[]
 for offset in range(-1,4):
  overlap=tuple((j,j-offset) for j in range(4) if 0<=j-offset<2)
  zero_tag_read_consistent=all(old[j]==0 for j,k in overlap)
  same_written_lanes=all((tag>>(8*k)&255)==old[j] for j,k in overlap)
  rows.append(dict(tag_address_minus_Q=offset,overlap_Q_lanes=[j for j,k in overlap],fresh_zero_tag_compatible=zero_tag_read_consistent,Q_lanes_unchanged_by_tag_store=same_written_lanes))
 return rows


def domains():
 inputs=[]
 for byte in range(256):
  request=byte+2;r=(((request+3)&65535)&65532)
  check(r==(request+3)&~3 and 4<=r<=260 and bool(r>52)==bool(byte>=51),'Qalloc allU8 request/round/list domain')
  inputs.append(dict(F29=byte,request=request,rounded=r,list='large' if r>52 else 'small'))
 actual=inputs[251];check((actual['request'],actual['rounded'],actual['list'])==(253,256,'large'),'Qalloc matchingAPP defaultsample')
 rejected=whole=split=0
 for B in range(65536):
  if B<256:rejected+=1;continue
  gap=B-256
  if gap<=8:whole+=1;check(256<=B<=264,'Qalloc wholeblocksize range')
  else:
   split+=1;check(265<=B and B-264>=1 and 264+8<=B+8,'Qalloc splitheader fitsoriginalextent')
 check((rejected,whole,split)==(256,9,65271),'Qalloc exhaustiveU16 sizepartition')
 for old in range(65536):
  check(((old-8)&65535)-256 & 65535 == (old-264)&65535,'Qalloc splitaccount modulo')
  check((old-256)&65535==((old+65536)-256)%65536,'Qalloc nosplitaccount modulo')
 lanes=lane_cases(0x40025000,73)
 check([r['tag_address_minus_Q'] for r in lanes if r['fresh_zero_tag_compatible']]==[-1],'Qalloc exactword permitsonlyleading overlapzero')
 check(all(not r['fresh_zero_tag_compatible'] or r['Q_lanes_unchanged_by_tag_store'] for r in lanes),'Qalloc nosplit benign tagoverlap theorem')
 check(not lane_cases(0x40025000,0x8049)[0]['Q_lanes_unchanged_by_tag_store'],'Qalloc theorem notfor markedtag')
 # Closed interval corollary for any owned nonwrapping block; no heap contents.
 for Q in (0x20003590,0x200035e0):
  check(Q+4<previous.layout.A<previous.layout.E,'Qalloc nominalheap aboveQ')
 check((256<<16)|73==0x01000049,'Qalloc fallback packedargument')
 print('PASS:256 fresh-byte requests;65536 block sizes;131072 accounting identities;exact Q/tag byte-lane theorem')
 return dict(fresh_F29_inputs=inputs,matching_APP_F29_251=actual,U16_block_size_counts=dict(too_small=256,nosplit=9,split=65271),nosplit_overlap_lane_cases=lanes,marked_tag_counterexample_only=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());entry=core.ENTRY;src=core.DETAILS[index][0];raw=init.binding.take(data,src,208)
 check(sparse.captured(mem,src,208)==raw,'Qalloc core strictHEX');n,e=guard(raw,index)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+entry-int(fc['destination'],16)==src and entry+208<=int(mapping['first_copy_end_exclusive'],16),'Qalloc completecore conditionalmapping')
 cp=previous.binding.STARTS[index][0];cr=init.binding.take(data,cp,318);check(sparse.captured(mem,cp,318)==cr,'Qalloc config strictHEX');cb=previous.binding.body(cr,'config',index);cn={d['pc']-cp:d for d in cb['instructions']}
 call=next(c for c in cb['calls'] if c['offset']==198);check(call['target']==entry and call['target']!=core.message.ENTRY,'Qalloc directcore notmarkerwrapper')
 check((cn[186]['op'],cn[186]['rd'],cn[186]['rs1'],cn[186]['imm'],cn[186]['width'])==('load',10,8,29,1),'Qalloc freshU8 size source')
 check((cn[188]['rd'],cn[188]['rs1'],cn[188]['imm'],cn[192]['rd'],cn[192]['rs1'],cn[192]['imm'])==(11,0,73,10,10,2),'Qalloc exact request/tag arguments')
 check(cn[202]['op']=='store' and (cn[202]['rs2'],cn[202]['rs1'],cn[202]['imm'],cn[202]['width'])==(10,9,4,4),'Qalloc returnedpointer rawpublication C4')
 check(cn[206]['op']=='li' and cn[206]['rd']==10 and cn[206]['imm']==0,'Qalloc config forcedzero reply')
 after=[d for a,d in cn.items() if 202<a<=224]
 check(not any(d['op']=='load' and d['rs1']==10 for d in after),'Qalloc no localreturnedpointer dereference')
 cfg=cb['CFG'];afteralloc=previous.reply.leaves.reachable(cfg,cp+198)
 check(cp+202 in afteralloc and cp+206 in afteralloc and not any(a in afteralloc for a,d in [(cp+o,v) for o,v in cn.items()] if d['op'] in previous.binding.BRANCHES),'Qalloc postallocation no null/status branch')
 fit=core.reachable(e,entry+56)&ancestors(e,entry+176)
 check(not any(n[a]['op']=='call_indirect' or n[a].get('rd') in (11,15) for a in fit),'Qalloc R/tag preservedonallfinite fitprefixes')
 check([a-entry for a,d in n.items() if d.get('rd')==12][:1]==[124] and entry+96 not in core.reachable(e,entry+124),'Qalloc fallback A2 ambientnotfitdefined')
 continuation=core.reachable(e,entry+98)
 check(not continuation&{entry+76,entry+110,entry+176,entry+204} and entry+34 in continuation and n[entry+34]['imm']==0,'Qalloc fallbackreply discarded/noretry/forced0')
 stores=[dict(offset=a-entry,base=d['rs1'],imm=d['imm'],bytes=d['width'],source=d['rs2']) for a,d in n.items() if d['op']=='store']
 check([d['offset'] for d in stores]==[2,8,14,30,156,158,162,166,168,174,176,186,192],'Qalloc complete13store census')
 split_new=[(n[entry+o]['imm'],n[entry+o]['width']) for o in (156,158,162)]
 split_old=[(n[entry+o]['imm'],n[entry+o]['width']) for o in (166,168,176)]
 check(sorted(j for a,z in split_new for j in range(a,a+z))==list(range(8)) and sorted(j for a,z in split_old for j in range(a,a+z))==list(range(8)),'Qalloc eachsplitheader exact8Bcover')
 _,small,large,sentinel,fallback,account,_=core.DETAILS[index];Q=0x20003590+80*index;C=0x20003560+80*index
 fixed=[dict(address=account+6,bytes=2,role='account'),dict(address=0x4002420c,bytes=4,role='control')]
 check(all(previous.separated(r['address'],r['bytes'],Q) for r in fixed),'Qalloc fixed numericwrites excludeQ')
 return dict(label=init.binding.PROFILES[index][0],Q_slot=Q,C4=C+4,config_call=dict(pc=cp+198,target=entry,size_fresh_read=cp+186,request='freshU8[F+29]+2',tag=73,publish_PC=cp+202,forced0_PC=cp+206,pointer_return_used_as_status=False),
  core=dict(source=src,target=entry,bytes=208,sha256=sha256(raw).hexdigest(),instruction_count=len(n),stores=stores,slots=dict(small_head=small,large_head=large,sentinel=sentinel,fallback=fallback,account=account),complete_CFG_sha256=sha256(json.dumps(e,separators=(',',':')).encode()).hexdigest()),
  matched_APP_sample=dict(fresh_F29=251,request=253,rounded_R=256,tag=73,selected_head_slot=large,actual_fresh_head_or_sample_proved=False),
  fit_cases=dict(free_tag=0,B_min=256,nosplit_B=[256,264],nosplit_header_writes=[[6,2]],split_B=[265,65535],split_N_formula='(H+264) mod2^32',split_new_header_writes=split_new,split_old_header_writes=split_old,returned_pointer='(H+8) mod2^32',payload_fill_or_copy_calls=0,header_writes_outside_Rbyte_payload_if_validblock=True,other_write_alias_exclusion_required=True,account_decrements=dict(nosplit=256,split=264)),
  sentinel=dict(null_fallback_reply=0,header_or_account_stores_on_null_path=0,nonnull_fallback=dict(call_PC=entry+96,A0=1,A1=0x01000049,A2='ambient coreentry value',reply_discarded=True,normal_core_reply=0,list_retry=False,Q_effect_unproved=True)),
  Q_preservation=dict(nosplit='if entryQ=40025000 andfreshfree-taghalfword=0 agrees with same ordinarybyteimage,tag73 store preservesoverlappedQ lanes;fixed/frame/control writes excludedseparately',split='both nonwrapping8Bheaders H andN disjointQ,orownedblock[H,H+B+8) insidevalidheapdisjointQ;normalfinite traversal',sentinel='freshfallback0;normalvalid traversal;noheader/accountwrites',nonnull_fallback='opaque;cannot inferQpreservation fromdiscardedreply'),
  conditional_config_join='with oldC4fresh0 (noprivaterelease),matchedfill/copy andAPPsamples/frame/context/source/physicalnonalias/nointerference premises,oneprovedcorecase preservesQ throughconfignormalreturn;C4 receivesP or0,configreply0 inbothcases',
  fixed_write_intervals=fixed,required_premises=['all relevant previous selectedRF/caller and matchingcode/helper/ISA/mapping premises','finitevalidtraversal/accesses/returns;noadversecode/frame/context/physicalalias/IRQ/DMA/reentry/externalwriters','for APP-specialization freshF29sample251;earlierdefaultstore notsamplestabilityproof','oldC4snapshot0 excludes earlierprivatefree;otherwise requireseparatepreservation proof','nosplit byte-lane theorem usesfreshzero-tagload/entryQ consistency andordinarymemory littleendian;validunalignedaccess notassumed','split requires statedheader/block Q exclusion;nominalarena containment notactualheapownershipproof'],
  actual_provider_fresh_heap_ownership_termination_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-RF-config-direct-core-Q-preservation-cases-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,remaining=['freshsize/head/block/sentinel/fallback snapshots andactualmapping','privatefree foroldC4nonnull;opaquefallback/otherwriters/interveningcalls','fullpointerretention/ownership/release/notification lifetime;IRQ/pollprogress'])


def tests(carriers):
 count=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,core.DETAILS[i][0],208);n,_=guard(raw,i)
  for o in (38,46,52,56,84,88,92,96,98,110,116,124,134,152,156,158,162,166,168,174,176,180,186,192):
   z=n[core.ENTRY+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('Qalloc coremutationescaped')
   count+=1
 check(count==48,'Qalloc mutationcensus');print('PASS:48 original rounding/list/fallback/fit/header/account/return mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'Qalloc exactledger')
 print('PASS:RF config direct-core inputs/fit/fallback/publication/Q-preservation cases;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork;actualheap/provider/lifetime UNPROVED')


if __name__=='__main__':main()
