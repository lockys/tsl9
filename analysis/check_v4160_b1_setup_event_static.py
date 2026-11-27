"""Offline setup callback publication -> event consumption -> conditional clear.
Original complete bodies/tables and immutable CFG/def-use certificates only.
No target execution/emulation, mutable target memory, hardware or replay.
"""
import argparse,json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_setup_services_static as previous
import check_v4160_event_dispatch_static as event
import check_v4160_callback_dispatch_static as callback
import check_v4160_list_common_body_static as common
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-setup-event-static.json')
PARTS=('event','callback','common')
SIZES=((438,1064,1220),(438,1154,1220))
COUNTS=((150,356,443),(150,387,443))
BASE=0x2000319c


def coordinates(index):
 return ((event.ENTRY,callback.STARTS[index],common.STARTS[index]),(event.DETAILS[index][0],callback.STARTS[index],common.STARTS[index]))


def guard(raw,part,index,table):
 if part=='event':
  M=BASE+80*index;_,direct,pair,digest=event.DETAILS[index];b=event.body(raw,M,M+152,M+888,direct,pair,digest);e={int(a,16):[int(z,16) for z in qs] for a,qs in b['conditional_normal_return_CFG'].items()}
 elif part=='callback':b=callback.body(raw,table,index);e=b['local_CFG']
 else:b=common.body(raw,index);e=b['local_CFG']
 n={d['pc']:d for d in b['instructions']};pc=coordinates(index)[0][PARTS.index(part)]
 check((len(raw),len(n))==(SIZES[index][PARTS.index(part)],COUNTS[index][PARTS.index(part)]),'setupevent reusedfullbody census')
 typed=[]
 for a,d in n.items():
  if d['op']=='load' and d['size']==4:
   f3={1:4,2:5,4:2}[d['width']];check(int.from_bytes(raw[a-pc:a-pc+4],'little')&0x707f==(f3<<12|3),'setupevent typedzeroextendedload');typed.append(a-pc)
 return dict(part=part,start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,typed_load_offsets=typed,reused_complete_body=True)


def path(e,start,end):
 seen=set();todo=deque([(start,[start])])
 while todo:
  a,p=todo.popleft()
  if a==end:return p
  if a not in seen:seen.add(a);todo.extend((z,p+[z]) for z in e.get(a,[]))
 raise RuntimeError('setupevent no syntacticwalk')


def reaching(b,at,reg,opaque_calls=True):
 pc=b['start'];e=b['CFG'];n={d['pc']:d for d in b['instructions']};pred={a:[] for a in e}
 for a,zs in e.items():
  for z in zs:
   if z in pred:pred[z].append(a)
 todo=pred[pc+at][:];seen=set();defs=set();entry=False
 while todo:
  a=todo.pop();d=n[a]
  if d.get('rd')==reg or (opaque_calls and 10<=reg<=17 and d['op'] in ('jal','jalr','call_indirect')):defs.add(a-pc);continue
  if a==pc:entry=True
  if a not in seen:seen.add(a);todo.extend(pred[a])
 return defs,entry


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pcs,sources=coordinates(index);tabraw=init.binding.take(data,callback.TABLES[index],52);check(sparse.captured(mem,callback.TABLES[index],52)==tabraw,'setupevent strictHEX fulltable');tab=callback.table(tabraw,index);bs={}
 for j,part in enumerate(PARTS):
  raw=init.binding.take(data,sources[j],SIZES[index][j]);check(sparse.captured(mem,sources[j],len(raw))==raw,'setupevent allfullbodies strictHEX');bs[part]=guard(raw,part,index,tabraw)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy'];check(int(f['source'],16)+event.ENTRY-int(f['destination'],16)==sources[0] and int(f['destination'],16)<=event.ENTRY and event.ENTRY+438<=int(mapping['first_copy_end_exclusive'],16),'setupevent completeevent firstcopymapping')
 # Reuse the reviewed producer args/registrar/normal-return certificates.
 services=previous.profile(data,hexraw,index);producer=services['joins']['registrar'];ep,cp,mp=pcs;eb,cb,mb=(bs[p] for p in PARTS);en,cn,mn=({d['pc']-b['start']:d for d in b['instructions']} for b in (eb,cb,mb));slot=BASE+80*index+44
 check(producer['slot']==slot and producer['callback']==cp and producer['index']==0,'setupevent samepublishedslotandliteralcallback')
 check(en[358]['op']=='load' and en[358]['width']==4 and en[358]['rs1']==18 and en[358]['imm']+0x20003000==slot,'setupevent freshcallbackslotload')
 check(en[362]['op']=='beqz' and en[362]['rs1']==15 and en[362]['target']==ep+370 and en[364]['op']=='call_indirect' and en[364]['rs1']==15,'setupevent capturedword nullguard/call')
 check(en[366]['op']=='store' and en[366]['width']==4 and en[366]['rs1']==18 and en[366]['rs2']==0 and en[366]['imm']==en[358]['imm'],'setupevent unconditionalpostcallclear sameword')
 check(reaching(eb,364,15)==({358},False) and reaching(eb,358,18)==({26},False) and en[26]['imm']==0x20003000,'setupevent slotpointerGPRdefs')
 check(eb['CFG'][ep+364]==[ep+366] and eb['CFG'][ep+366]==[ep+370],'setupevent clearonlyafter normalcallreturn')
 # Full A0 is retained even though the pending writeback uses a halfword.
 check(reaching(eb,364,10)==({342},False),'setupevent hookA0 fromfullOR notlaterhalfwordstore')
 check(en[316]['width']==2 and en[316]['imm']==BASE+80*index+64-0x20003000 and en[324]['op']=='xori' and en[324]['imm']==-1 and en[328]['op']=='and' and en[328]['rd']==10,'setupevent fullreplyandcomplementmask')
 check(reaching(eb,328,10)==({314},False) and en[340]['width']==2 and en[342]['op']=='or' and en[342]['rd']==10 and en[344]['op']=='store' and en[344]['width']==2 and en[344]['rs2']==10,'setupevent handlerreply/freshpending/store16 distinctions')
 check(reaching(eb,364,11)==({314},False) and reaching(eb,364,12)==({314},False),'setupevent hookA1A2 areopaquehandlerreturns notreusedinputargs')
 check(en[370]['op']==en[374]['op']=='load' and en[370]['width']==en[374]['width']==1 and en[378]['rs1']==14 and en[378]['rs2']==15,'setupevent freshcursorcount branch notcallbackreply')
 check(reaching(eb,378,10)==({342,364},False),'setupevent nullpathkeepsmerge/nonnullpathkeepsreply throughbranch')
 check(all(en[o].get('rd')!=10 and en[o]['op'] not in ('jal','jalr','call_indirect') for o in (366,370,374,378)),'setupevent noA0kill afterhook beforecursorbranch')
 for o in (358,362,364,366,370,374,378):check(en[o].get('rd')!=18,'setupevent localS2base unchanged')
 # Callback object is independently captured; it is not the hook input A0.
 check(cn[8]['rs1']==9 and cn[8]['imm']==952+80*index and cn[0xe]['op']=='load' and cn[0xe]['rd']==8 and cn[0xe]['rs1']==15 and cn[0xe]['imm']==100,'setupevent callbackN independentB100 source')
 check(cn[0x40]['rs1']==8 and cn[0x40]['imm']==11 and reaching(cb,0x40,8,False)==({0xe},False),'setupevent capturedN usedonredispatch')
 check(cn[0x3c]['op']=='addi' and cn[0x3c]['rs1']==8 and cn[0x3c]['imm']==20,'setupevent N20pointer derivedfromcapturedN')
 # Complete callback has its own 48-byte frame and one ordinary return.
 saved=((9,36),(8,40),(18,32),(20,24),(21,20),(19,28),(22,16),(1,44))
 check([(d['rs2'],d['imm']) for d in cn.values() if d['op']=='store' and d['rs1']==2 and d['width']==4]==list(saved),'setupevent callback all8registersaves')
 check(sorted((d['rd'],d['imm']) for d in cn.values() if d['op']=='load' and d['rs1']==2)==sorted(saved),'setupevent callback all8restores')
 check([(o,d['imm']) for o,d in cn.items() if d.get('rd')==2]==[(0,-48),(0xce,48)] and cn[0xd0]['rs1']==1,'setupevent callback frame48 soleRET')
 # A syntactic republishing route exists inside the callback's common callee.
 call=0x26c+2*index;check(cn[call]['op']=='jal' and cn[call]['target']==mp and cn[call-2]['op']=='mv' and cn[call-2]['rs2']==8,'setupevent callbackcommon capturedN call')
 check(mn[0x498]['imm']+mn[0x49e]['imm']==cp and mn[0x49c]['imm']==0 and mn[0x4a2]['target']==previous.STARTS[index][0],'setupevent commonrepublishes samecallback/indexzero')
 check(mb['CFG'][mp+0x4a2]==[mp+0x4a6] and mn[0x4c0]['rd']==0,'setupevent commoncontinuesbyframereleasingtail afterregistrar')
 walks={
  'event_entry_to_hookload':[a-ep for a in path(eb['CFG'],ep,ep+358)],
  'nonnull_hook_to_clear':[358,362,364,366,370],
  'null_hook_skips_clear':[358,362,370],
  'callback_entry_to_common':[a-cp for a in path(cb['CFG'],cp,cp+call)],
  'callback_normalreturn_from_commonlink':[a-cp for a in path(cb['CFG'],cp+call+4,cp+0xd0)],
  'common_entry_to_registrar':[a-mp for a in path(mb['CFG'],mp,mp+0x4a2)],
  'common_registrarlink_to_tail':[a-mp for a in path(mb['CFG'],mp+0x4a6,mp+0x4c0)]}
 for key in ('nonnull_hook_to_clear','null_hook_skips_clear'):check(all(ep+z in eb['CFG'][ep+a] for a,z in zip(walks[key],walks[key][1:])),'setupevent chosenhookwalk edges')
 slots=dict(hook=slot,return_mask=BASE+80*index+64,cursor=BASE+80*index,count=BASE+80*index+1)
 for a,z in ((slot,4),(slots['return_mask'],2),(slots['cursor'],1),(slots['count'],1)):
  for b,w in ((slot,4),(slots['return_mask'],2),(slots['cursor'],1),(slots['count'],1)):
   if a!=b:check(a+z<=b or b+w<=a,'setupevent distinctfixedcells notglobalaliasproof')
 guards=dict(event='check_v4160_event_dispatch_static.py',callback='check_v4160_callback_dispatch_static.py',common='check_v4160_list_common_body_static.py')
 evidence={part:{**{k:v for k,v in b.items() if k!='instructions'},'instruction_count':len(b['instructions']),'original_complete_guard':guards[part]} for part,b in bs.items()}
 return dict(label=init.binding.PROFILES[index][0],bodies=evidence,switch_table=tab,event_flash_source=sources[0],reused_setup_registrar=producer,slots=slots,
  callback_B=0x200033b8+80*index,callback_N_source_slot=0x200033b8+80*index+100,setup_P_equals_callback_N_proved=False,
  event_hook_contract=dict(load=358,nullgate=362,call=364,clear=366,next_cursor_count_branch=378,A0='full32((opaquehandlerA0 & ~freshU16returnmask) | separatelyfreshU16pending)',A1_A2='opaque handler-return registers; not reloaded',captured_pointer_reloaded_beforecall=False,clear_conditional_on_normalreturn=True,clear_checks_current_slot_or_reply=False,callback_reply_not_used_by_immediate_clear_or_cursorbranch=True,reply_kept_inA0_notgloballydiscarded=True),
  possible_reregistration=dict(callback_common_call=call,common_registrar_call=0x4a2,slot=slot,callback_literal=cp,normal_return_before_outer_clear_required=True,syntactic_route_only=True,actualorder_or_feasibility_notproved=True),
  CFG_walks=walks,callback_frame_bytes=48,event_frame_bytes=32,own_frame_andneededS_preservation_required=True,
  one_shot_delivery_exactly_once_clear_atomicity_callbacktermination_actualbinding_fullownership_proved=False)


def domains():
 cases=0
 for low in range(65536):
  for high in (0,0xffff0000):
   for mask in (0,1,0x8000,0xffff):
    full=((high|low)&(~mask&0xffffffff))|0x5555
    check(full&0xffff==((low&(mask^0xffff))|0x5555) and full&0xffff0000==high,'setupevent hook fullword vsstoredhalfword');cases+=1
 return dict(fullreply_low16_highboundary_mask_cases=cases,opaquehandler_reply_domain_notconstrained=True,closed_host_scalar_identity_only=True,no_mutablecallback_or_targetmemory_model=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-setup-event-hook-consume-postclear-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),reused_code_bytes=5534,reused_instructions=1929,reused_table_bytes=104,reused_table_words=26,new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['actualstartup/JT0/provider/registrationorder andsamevalueattimeofload','callbackN B100source producer/validity/lifetime vssetupP','reregistration/interference/IRQorder andcallback/callee/polltermination','fullbufferownership/consumption/release andnotificationretention'])


def tests(carriers):
 total=typed=words=0
 for i,data in enumerate(carriers):
  pcs,srcs=coordinates(i);tab=init.binding.take(data,callback.TABLES[i],52)
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,srcs[k],SIZES[i][k]);b=guard(raw,part,i,tab)
   for d in b['instructions']:
    o,z=d['pc']-pcs[k],d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:guard(bad,part,i,tab)
    except RuntimeError:pass
    else:raise RuntimeError('setupevent instructionmutation escaped')
    total+=1
   for o in b['typed_load_offsets']:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:guard(bad,part,i,tab)
    except RuntimeError:pass
    else:raise RuntimeError('setupevent typedmutation escaped')
    typed+=1
  for j in range(13):
   bad=bytearray(tab);bad[4*j]^=1
   try:callback.table(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('setupevent tablemutation escaped')
   words+=1
 check((total,typed,words)==(1929,214,26),'setupevent mutationcensus')
 print(f'PASS:{total} instruction/{typed} typed-load/{words} tableword mutations rejected')
 return typed


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();ledger['typed_mutation_count']=tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'setupevent exactledger')
 print('PASS:5534B/1929i reusedcode+104B/26tablewords;setup/event/callback/common/postreturn-clear joins;strictHEX/exactledger')
 print('PASS:NO target execution/emulation;binding/order/exactlyonce/polltermination/fullownership UNPROVED')


if __name__=='__main__':main()
