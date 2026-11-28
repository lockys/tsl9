"""Offline selected NV-read failure, FF-record status and pre-write join.

Original CFG/operands and immutable scalar, interval/frame certificates only.
No target execution/emulation or mutable RAM/heap/provider/MMIO/NV model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_id10_static as previous
import check_v4160_b1_nv_read_static as nv
import check_v4160_n136_predicate_static as predicate

init,sparse,check=previous.init,previous.sparse,previous.check
id10=previous.id10
layout,separated=previous.layout,previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-nv-static.json')
STATUS=(0x6af88,0x6b16c)
STATUS_HASH=('de7650a390bbd1823df3559bdf4717f817459a6108ed6f48419575baf50648e0','db4fda8e8df5c120153c36038f0fbd20da100f2dbfd407f333962d668ee8b79a')


def status_body(raw,index):
 pc=STATUS[index];g=0x20003000;delta=80*index;n=id10.decode(raw,pc);s={}
 def e(o,op,**f):s[pc+o]=dict(op=op,**f)
 e(0,'addi',rd=2,rs1=2,imm=-32)
 for o,r,v in ((2,8,24),(4,9,20),(6,18,16),(8,19,12),(10,1,28)):e(o,'store',rs1=2,rs2=r,imm=v,width=4)
 e(12,'li',rd=9,imm=0);e(14,'li',rd=8,imm=0);e(16,'lui',rd=18,imm=g);e(20,'lui',rd=19,imm=g)
 e(24,'load',rd=15,rs1=18,imm=-63+delta,width=1);e(28,'bltu',rs1=8,rs2=15,target=pc+48)
 e(32,'load',rd=1,rs1=2,imm=28,width=4);e(34,'load',rd=8,rs1=2,imm=24,width=4);e(36,'mv',rd=10,rs2=9)
 for o,r,v in ((38,18,16),(40,9,20),(42,19,12)):e(o,'load',rd=r,rs1=2,imm=v,width=4)
 e(44,'addi',rd=2,rs1=2,imm=32);e(46,'jr',rs1=1);e(48,'load',rd=15,rs1=19,imm=-68+delta,width=4)
 e(52,'slli',rd=10,rs1=8,imm=4);e(56,'li',rd=12,imm=6);e(58,'addi',rd=11,rs1=0,imm=255);e(62,'add',rd=10,rs1=10,rs2=15)
 e(64,'auipc',rd=1,imm=0x1ff95000);e(68,'jalr',rd=1,rs1=1,imm=1268-484*index);e(72,'bnez',rs1=10,target=pc+80)
 e(74,'addi',rd=9,rs1=9,imm=1);e(76,'andi',rd=9,rs1=9,imm=255);e(80,'addi',rd=8,rs1=8,imm=1);e(82,'andi',rd=8,rs1=8,imm=255);e(86,'jump',target=pc+24)
 check(set(n)==set(s),'fallbackNV status boundaries')
 for p,f in s.items():init.g(n,p,'fallbackNV status operand '+hex(p-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(88,33,STATUS_HASH[index]),'fallbackNV status identity')
 check(int.from_bytes(raw[24:28],'little')>>12&7==4,'fallbackNV status count unsigned load')
 check((pc+64+n[pc+64]['imm']+n[pc+68]['imm'])&0xfffffffe==0x200004bc,'fallbackNV status predicate join')
 egraph={}
 for p,d in n.items():
  q=[] if d['op']=='jr' else [d['target']] if d['op']=='jump' else [p+d['size']]
  if d['op'] in ('bltu','bnez'):q.append(d['target'])
  check(all(a in n for a in q),'fallbackNV status closed CFG');egraph[p]=q
 stores=[d for d in n.values() if d['op']=='store'];check(len(stores)==5 and all(d['rs1']==2 for d in stores),'fallbackNV status frame-only stores')
 check([p-pc for p,d in n.items() if d['op'] in ('jal','jalr','call_indirect')]==[68],'fallbackNV status sole callee')
 return dict(start=pc,bytes=88,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=egraph,stores=stores)


def status_paths(b):
 pc=b['start'];e=b['CFG'];result=[];prefix=[0,2,4,6,8,10,12,14,16,20];cycle=[24,28,48,52,56,58,62,64,68,72,80,82,86];suffix=[24,28,32,34,36,38,40,42,44,46]
 for m in range(4):
  offsets=prefix+cycle*m+suffix;walk=[pc+o for o in offsets];check(all(b in e[a] for a,b in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackNV FF-status CFG')
  check(74 not in offsets and 76 not in offsets and offsets.count(68)==m,'fallbackNV predicate1 does not increment accumulator')
  result.append(dict(m=m,path=[hex(p) for p in walk],predicate_calls=m,predicate_reply=1,status_reply=0,finite_graph_walk_not_target_execution=True))
 return result


def all_ff_predicate_path(b):
 pc=b['start'];e=b['CFG'];offsets=[0,4,8,12,16,18,22]+[o for _ in range(6) for o in (36,38,42,46)]+[50,54,58,60];walk=[pc+o for o in offsets]
 check(all(z in e[a] for a,z in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackNV sixFF predicate CFG')
 check(offsets.count(38)==6 and 32 not in offsets,'fallbackNV six exact unsigned byte comparisons and reply1')
 return dict(path=offsets,entry_A1=255,entry_A2=6,required_six_source_bytes_value=255,reply=1,frame_bytes=0,control_word=0x4002420c,control_clear_and_capture_restore_and_FENCE_are_not_executed=True)


def scan_path(load,lp,m):
 e={int(p,16):[int(q,16) for q in qs] for p,qs in load['conditional_CFG'].items()};prefix=[0,2,4,6,8,10,12,14,16,18,22,26]
 cycle=[28,32,88,92,96,100,104,106,108,112,116,118,122,124,128,130,134,138,142,144,148,150,152,156,160,164,166,170,172,176]
 suffix=[28,32,36,40,44,48,54,58,62,68,70,72,74,76,78,80,82,84]
 offsets=prefix+cycle*m+suffix;walk=[lp+o for o in offsets];check(all(z in e[a] for a,z in zip(walk,walk[1:])) and not e[walk[-1]],'fallbackNV bounded read-error scan/status/flags/tail CFG')
 check(offsets.count(112)==m and 50 not in offsets and 64 not in offsets,'fallbackNV scan counts and optional calls skipped')
 return dict(m=m,path=[hex(p) for p in walk],read_wrapper_calls=m,error_reply=10,FF_fills=2*m,post_scan_status_reply=0,required_second_flag_fresh_zero=True,tail_to_save=True)


def profile(data,hexraw,index,parent,by_source,first):
 g=0x20003000+80*index;F=g+492;C=F-80;pc,ap,lp,wp,op=id10.STARTS[index];d=id10.role.DETAILS[index]
 check(parent['end_cuts']['source0']['target']==STATUS[index] and parent['end_cuts']['source1_to3']['target']==nv.STARTS[index],'fallbackNV inherited first-service joins')
 windows={p:id10.body(init.binding.take(data,id10.STARTS[index][k],id10.SIZES[k]),p,index) for k,p in enumerate(id10.PARTS)}
 status=status_body(init.binding.take(data,STATUS[index],88),index);reader=nv.body(init.binding.take(data,nv.STARTS[index],nv.SIZE),index);read_paths=nv.paths(reader);rn={v['pc']-reader['start']:v for v in reader['instructions']}
 selected={name:read_paths[name] for name in ('configured_missing_callback','RAM_null')}
 for name,offsets in selected.items():
  check(not any(rn[o]['op'] in ('jal','jalr','call_indirect') for o in offsets),'fallbackNV selected NV-wrapper no nested calls')
  check(all(rn[o]['rs1']==2 for o in offsets if rn[o]['op']=='store'),'fallbackNV selected NV-wrapper frame-only stores')
  check(338 in offsets and 196 not in offsets and rn[338]['imm']==10,'fallbackNV selected forced read-wrapper reply10')
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];fs=int(fc['source'],16)+0x2000039c-int(fc['destination'],16);ps=int(fc['source'],16)+0x200004bc-int(fc['destination'],16)
 fill=previous.third.outer.previous.source.fill_contract(init.binding.take(data,fs,46));predraw=init.binding.take(data,ps,62);pred=predicate.body(predraw,'predicate',index)
 check(fill['encoded_GPR_writes']==[10,14,15] and int.from_bytes(predraw[38:42],'little')>>12&7==4,'fallbackNV fill ABI and predicate zero-extended byte load')
 check(all(v['base']==14 and v['bytes']==4 for v in pred['stores']) and not pred['calls'],'fallbackNV predicate control-only stores/no calls')
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]+[('NV_pool',g-68,4),('NV_count',g-63,1),('NV_ID10',g-62,1),('NV_limit',g-70,1),('first_optional_flag',g-71,1),('second_optional_flag',g-72,1)]
 def exclude(a,z):
  check(0<=a<a+z<=1<<32,'fallbackNV nonwrapping interval')
  for name,p,w in protected:check(separated(a,z,p,w),'fallbackNV write excludes '+name)
 exclude(0x4002420c,4);owner_checks=0
 for (n,b),(q,t,owners,headers,table_size) in by_source.items():
  for m in range(1,4):
   geometry=previous.small_geometry(n,q,t,first,m);P=geometry['payload'];request=geometry['request'];H=geometry['free_header'];N=geometry['new_remainder']
   for j in range(m):
    for o,z in ((0,6),(6,6),(12,2)):
     a=P+16*j+o;check(P<=a<a+z<=P+request and a+z<=P+16*j+14,'fallbackNV record fallback writes owned; bytes14/15 excluded');exclude(a,z)
     for name,p,w in owners+headers+[('NV_header',H,8),('NV_free_header',N,8)]:check(separated(a,z,p,w),'fallbackNV old/NV owner header survives '+name);owner_checks+=1
     check(separated(a,z,layout.P,table_size),'fallbackNV complete first table payload survives')
    check(16*j+6<=request and 6<16 and 14<15,'fallbackNV predicate6-byte FF extent/byte15 exclusion')
 an={v['pc']:v for v in windows['allocate']['instructions']};ln={v['pc']:v for v in windows['load']['instructions']};wn={v['pc']:v for v in windows['save']['instructions']}
 check(an[ap+340]['rs2']==0 and an[ap+340]['imm']==-71+80*index and [ln[lp+o]['imm'] for o in (44,58)]==[-71+80*index,-72+80*index],'fallbackNV first flag prior cleared vs second independent fresh premise')
 check(wn[wp+4]['target']==STATUS[index] and wn[wp+30]['target']==0x494ee+152*index,'fallbackNV save status/read wrapper/write joins')
 we={int(p,16):[int(q,16) for q in qs] for p,qs in windows['save']['conditional_CFG'].items()};save_path=id10.paths.chain(we,wp,{wp+12:wp+18},cut=wp+30)
 check(wn[wp+8]['imm']==1 and wn[wp+10]['imm']==10 and wn[wp+12]['rs1']==14 and wn[wp+12]['rs2']==10,'fallbackNV status0 selects literal10 byte')
 check((wn[wp+28]['op'],wn[wp+28]['rs1'],wn[wp+28]['rs2'],wn[wp+28]['imm'],wn[wp+28]['width'])==('store',2,15,15,1),'fallbackNV exact borrowed stack byte store')
 check(15+1<=28 and set(range(15,16)).isdisjoint(range(28,32)),'fallbackNV one-byte scratch distinct from saved RA')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 ranges=[('status',STATUS[index],88),('read',reader['start'],590),('predicate',ps,62),('fill',fs,46),('load',lp,178),('save',wp,40)]
 for name,a,z in ranges:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackNV strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],strictHEX_guards=guards,status_body=status,status_FF_paths=status_paths(status),predicate=dict(source=ps,body=pred,selected_sixFF_path=all_ff_predicate_path(pred)),
  read_wrapper=dict(body=reader,selected_paths=selected,configured_missing_callback_premise='retained U32[F+8]!=0 and U32[F+56]==0',RAM_null_premise='retained U32[F+8]==0 and U32[C+32]==0',reply=10,no_output_or_context_store_on_selected_paths=True,no_nested_provider_allocator_copy_or_release_calls_on_selected_paths=True,no_physical_NV_read_claimed=True),
  loader_scans=[scan_path(windows['load'],lp,m) for m in range(4)],record_result=dict(bytes0_to11=255,bytes12_to14=0,byte15_not_initialized_or_proved_known=True,predicate_first6_reply=1,status_counts_predicate_zero_only=True,status_reply_for_m0_to3=0),
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],interval_certificate=dict(source_families=1024,m_zero_cases=1024,m_positive_cases=3072,old_and_NV_header_owner_checks=owner_checks,FF_fill_halfword_only_new_payload_writes=True),
  optional_services=dict(first_flag_address=g-71,first_flag_zero_from_selected_setup_and_preservation=True,second_flag_address=g-72,second_fresh_flag_zero_is_extra_premise=True,optional_calls_executed=False),
  save_prefix=dict(path=save_path,second_status_reply=0,chosen_byte=10,byte_source_GPR=15,initialized_stack_bytes=[15],borrowed_source_relative_save_entry_SP=-17,saved_RA_relative_save_entry_SP=-4,save_frame_live_at_cut=True),
  end_cut=dict(pc=wp+30,target=0x494ee+152*index,A0=66,A1=1,A2='current save SP+15, one initialized byte10',fallback=0,gate=5,task_count=11,local_ID10=10,NV_write_not_executed=True,next_ID11_count12_not_claimed=True),
  frames=dict(outer=16,loader=32,read_wrapper=32,status=32,predicate=0,save=32,new_extension_max_live=80,prior_allocation_stage_max=96,live_at_write_cut=48,loader_released_before_save=True),
  required_premises=['all prior selected m0..3 and1024source/allocation/source/header/frame/code/first-copy/ISA bindings remain conditional; positive scans additionally use one of two retained original read-wrapper failure route conditions; no read-success or physical NV result inferred',
   'read-wrapper/FF fill/predicate/status match original guarded bodies; counts/pool/index/required S/GP/SP/RA/savedwords and owned payloads remain; first6recordbytesFF after each known fallback and before both status scans',
   'predicate control clear/FENCE.I/captured-control restore have no adverse physical effects on protectedRAM/frames; no interfering IRQ/DMA/reentry/otherwriters; valid code/metadata/physical nonalias frame/heap/control accesses',
   'fresh second optional flagG-72==0; first flagG-71 remainssetup0. Optional bodies are skipped, not assumed harmless. All nonzero observations and previous callbacks/fields retained as before',
   'stop before NV writer: one stack byte10 valid in live save frame; actual writer consumption/retention/output/sideeffects/normalreturn and ID11publication remain unproved'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);by_source,first=previous.families()
 return dict(schema='TSL9-fallback-selected-NVfailure-FFstatus-before-onebyte-write-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(data,h,i,parent['profiles'][i],by_source,first) for i,(data,h) in enumerate(zip(carriers,hexes))],
  source_composition='selected m0 OR mpositive NV-wrapper no-call reply10/fallbackFF -> status0 -> bothoptionalflags0 -> save status0 -> stackbyte10 -> before writer(66,1,SP15)',C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['other read-success/provider/cache/flag domains and actual installedbindings','writer494ee/49586 consumption/retention and full ID10 return/ID11registration','sixthinitializer/outertail and complete cross-event/borrowed-buffer lifetime'])


def tests(carriers):
 previous.tests(carriers);nv.tests(carriers);mutations=0
 for i,data in enumerate(carriers):
  fc=init.binding.profile(data,init.binding.PROFILES[i][0])['first_copy'];ps=int(fc['source'],16)+0x200004bc-int(fc['destination'],16)
  for role,source,z,guard in [('status',STATUS[i],88,lambda raw:status_body(raw,i)),('predicate',ps,62,lambda raw:predicate.body(raw,'predicate',i))]:
   raw=init.binding.take(data,source,z);base=STATUS[i] if role=='status' else 0x200004bc
   for p,d in id10.decode(raw,base).items():
    o=p-base;s=d['size'];bad=bytearray(raw);bad[o:o+s]=(int.from_bytes(bad[o:o+s],'little')^(4 if s==2 else 1<<20)).to_bytes(s,'little')
    try:guard(bad)
    except RuntimeError:pass
    else:raise RuntimeError('fallbackNV status/predicate mutation escaped')
    mutations+=1
 check(mutations==104 and 2003+404+48+104==2559,'fallbackNV cumulative mutation census')
 print('PASS:2559 original operand/typed-load mutations rejected;4 FF-status paths/profile;selected NV reply10 scan joins;one-byte writer cut only')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackNV exactledger')
 print('PASS:selected NVfailure/FFstatus/optional-skip/save-byte10 towriter;6strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,NV or targetnetwork;writer/fullreturn/ID11/bindings/lifetime UNPROVED')


if __name__=='__main__':main()
