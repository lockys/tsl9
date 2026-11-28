"""Offline selected ID66 byte setter and ID11/count12 return join.

Original bytes/closed CFG and immutable operands, intervals/frame proofs.
No target execution/emulation or mutable RAM/heap/provider/MMIO/NV model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_nv_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
id10=previous.id10
layout,separated=previous.layout,previous.separated
OUT=Path(__file__).with_name('v4160-b1-fallback-writer-static.json')
STARTS=(0x494ee,0x49586)
HASHES=('f2aa8ae2a694cd9dc97d6dc7b7f59139106b8f0ee69587a757bb3528176c8aa1','71a71f355cdc5db416c64dbda1aa14d4ce34ebe504ccd09f69d36cc1ae3e570c')


def writer_body(raw,index):
 pc=STARTS[index];n=id10.decode(raw,pc);s={}
 def e(o,op,**f):s[pc+o]=dict(op=op,**f)
 e(0,'li',rd=15,imm=5);e(2,'beq',rs1=10,rs2=15,target=pc+0x1a6);e(6,'addi',rd=2,rs1=2,imm=-48)
 for o,r,v in ((8,8,40),(10,9,36),(12,1,44),(14,18,32),(16,19,28),(18,20,24)):e(o,'store',rs1=2,rs2=r,imm=v,width=4)
 e(20,'mv',rd=9,rs2=12);e(22,'mv',rd=8,rs2=11);e(24,'bltu',rs1=15,rs2=10,target=pc+96)
 e(96,'addi',rd=15,rs1=0,imm=66);e(100,'beq',rs1=10,rs2=15,target=pc+462)
 e(462,'li',rd=15,imm=1);e(464,'bne',rs1=11,rs2=15,target=pc+216);e(468,'load',rd=14,rs1=12,imm=0,width=1)
 e(470,'lui',rd=15,imm=0x20003000);e(474,'store',rs1=15,rs2=14,imm=-292+80*index,width=1);e(478,'jump',target=pc+356)
 e(356,'li',rd=10,imm=0);e(358,'jump',target=pc+48);e(216,'li',rd=10,imm=24);e(218,'jump',target=pc+48)
 for o,r,v in ((48,1,44),(50,8,40),(52,9,36),(54,18,32),(56,19,28),(58,20,24)):e(o,'load',rd=r,rs1=2,imm=v,width=4)
 e(60,'addi',rd=2,rs1=2,imm=48);e(62,'jr',rs1=1)
 # The ID5 length-error branch reaches a shared leaf after the earlier RET.
 # Include it so this full function CFG has no silently omitted local target.
 e(424,'bne',rs1=11,rs2=15,target=pc+546);e(546,'li',rd=10,imm=24);e(548,'jr',rs1=1)
 check((len(raw),len(n),sha256(raw).hexdigest())==(550,187,HASHES[index]),'fallbackwriter full550B/187i identity')
 for p,f in s.items():init.g(n,p,'fallbackwriter selected operand '+hex(p-pc),**f)
 check(raw[468:470].hex()=='1822' and n[pc+468].get('mnemonic')=='qk.c.lbu','fallbackwriter original QK unsigned-byte load')
 edges={};calls=[];rets=[]
 for p,d in n.items():
  op=d['op'];q=[p+d['size']]
  if op=='jr':check(d['rs1']==1,'fallbackwriter RET RA');q=[];rets.append(p-pc)
  elif op=='jump':q=[d['target']]
  elif op in ('beq','bne','bltu','bgeu','beqz','bnez'):q.append(d['target'])
  elif op in ('jal','jalr'):
   target=d['target'] if op=='jal' else (p-4+n[p-4]['imm']+d['imm'])&0xfffffffe
   check(d['rd']==1,'fallbackwriter linked callee');calls.append(dict(offset=p-pc,target=target))
  else:check(op!='call_indirect','fallbackwriter no unlisted indirect call')
  check(all(a in n for a in q),'fallbackwriter complete closed local edges');edges[p]=q
 seen={pc};todo=[pc]
 while todo:
  for a in edges[todo.pop()]:
   if a not in seen:seen.add(a);todo.append(a)
 check(seen==set(n) and previous.nv.common.acyclic(edges),'fallbackwriter all local nodes reachable/acyclic')
 expected=[(202,0x490f8+152*index),(256,0x20000110),(290,0x20000040),(322,0x2000039c),(344,0x20000332),(416,0x20000332)]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[62,440,548],'fallbackwriter exact call/RET census')
 success_offsets=[0,2,6,8,10,12,14,16,18,20,22,24,96,100,462,464,468,470,474,478,356,358,48,50,52,54,56,58,60,62]
 badlength_offsets=success_offsets[:16]+[216,218]+success_offsets[-8:]
 paths={}
 for name,offsets in (('ID66_length1',success_offsets),('ID66_length_not1',badlength_offsets)):
  walk=[pc+o for o in offsets];check(all(b in edges[a] for a,b in zip(walk,walk[1:])) and not edges[walk[-1]],'fallbackwriter selected complete CFG '+name)
  check(not any(n[a]['op'] in ('jal','jalr','call_indirect') for a in walk),'fallbackwriter selected no nested service calls')
  stores=[d for a in walk if (d:=n[a])['op']=='store'];global_stores=[d for d in stores if d['rs1']!=2]
  check(len(stores)==(7 if name=='ID66_length1' else 6) and len(global_stores)==int(name=='ID66_length1'),'fallbackwriter selected store census')
  check(not any(n[a].get('rd') in (11,12) for a in walk),'fallbackwriter selected preserves A1/A2 locally')
  paths[name]=dict(path=[hex(a) for a in walk],reply_A0=0 if name=='ID66_length1' else 24,global_byte_stores=len(global_stores),source_byte_reads=int(name=='ID66_length1'))
 return dict(start=pc,bytes=550,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,returns=rets,selected_paths=paths,unselected_branch_calls_not_composed=True)


def profile(data,hexraw,index,parent,by_source,first):
 g=0x20003000+80*index;F=g+492;C=F-80;dst=g-292;d=id10.role.DETAILS[index];entry=d['entry'];wp=id10.STARTS[index][3]
 check(parent['end_cut']['pc']==wp+30 and parent['end_cut']['target']==STARTS[index] and parent['end_cut']['A0']==66 and parent['end_cut']['A1']==1 and parent['end_cut']['task_count']==11,'fallbackwriter prior writer-cut args/count')
 b=writer_body(init.binding.take(data,STARTS[index],550),index)
 protected=[(v['role'],v['address'],v['bytes']) for v in parent['protected_intervals']]+[('entries0_to10',layout.T,44)]
 for name,a,z in protected:check(separated(dst,1,a,z),'fallbackwriter byte setter excludes '+name)
 fc=init.binding.profile(data,init.binding.PROFILES[index][0]);firstcopy=fc['first_copy'];a=int(firstcopy['destination'],16);z=int(fc['first_copy_end_exclusive'],16)-a
 check(separated(dst,1,a,z),'fallbackwriter byte setter excludes entire first-copy code region')
 owner_checks=0
 for (n,source_byte),(q,t,owners,headers,table_size) in by_source.items():
  for name,a,z in owners+headers:check(separated(dst,1,a,z),'fallbackwriter byte setter excludes inherited owner/header '+name);owner_checks+=1
  check(separated(dst,1,layout.P,table_size),'fallbackwriter byte setter excludes full first-table payload')
  for m in range(1,4):
   v=previous.previous.small_geometry(n,q,t,first,m)
   for name,a,z in [('NV_header',v['free_header'],8),('NV_payload',v['payload'],v['request']),('NV_remainder',v['new_remainder'],8)]:
    check(separated(dst,1,a,z),'fallbackwriter byte setter excludes '+name);owner_checks+=1
    check(separated(layout.T+44,4,a,z),'fallbackwriter entry11 excludes '+name)
  for name,a,z in owners+headers:check(separated(layout.T+44,4,a,z),'fallbackwriter entry11 excludes prior owner/header '+name)
 save=id10.body(init.binding.take(data,wp,40),'save',index);sn={v['pc']:v for v in save['instructions']}
 check(sn[wp+30]['target']==STARTS[index] and [sn[wp+o]['op'] for o in (34,36,38)]==['load','addi','jr'] and sn[wp+34]['rd']==1 and sn[wp+34]['imm']==28 and sn[wp+36]['imm']==32,'fallbackwriter normal return/save restore chain')
 check(48+15==63 and 63+1<=48+32 and 63>=48 and set(range(63,64)).isdisjoint(range(44,48)),'fallbackwriter borrowed SP63 byte outside writer48 frame and savedRA')
 outer=id10.role.body(init.binding.take(data,entry,112),'entry',index);en={v['pc']:v for v in outer['instructions']}
 check(en[entry+84]['target']==id10.STARTS[index][0] and en[entry+84]['rd']==1,'fallbackwriter saved original outer RA')
 next_outer=id10.body(init.binding.take(data,id10.STARTS[index][4],16),'next_outer',index);on={v['pc']:v for v in next_outer['instructions']}
 check(id10.STARTS[index][4]==entry+88 and on[entry+96]['target']==d['reg'] and on[entry+100]['target']==d['outer_init'][5],'fallbackwriter next registration/sixth initializer cut')
 handler=0x4d000+d['outer_lows'][5];check(on[entry+88]['imm']+on[entry+92]['imm']==handler,'fallbackwriter handler formation')
 reg=id10.registration.body(init.binding.take(data,d['reg'],48),index);check(11 not in reg['encoded_GPR_definitions'],'fallbackwriter registrar preserves A1one')
 # The returned A2 may still hold the borrowed pointer after save frees its
 # frame. The selected registrar overwrites A2 before reading/dereferencing it.
 before=[]
 for v in reg['instructions']:
  if v.get('rd')==12:break
  before.append(v)
 else:raise RuntimeError('fallbackwriter registrar has no A2 definition')
 check(all(v.get('rs1')!=12 and v.get('rs2')!=12 for v in before),'fallbackwriter no borrowed A2 use before registrar overwrites it')
 for a,z in ((layout.T+44,4),(C+1,1)):
  for name,p,w in protected:
   if name!='task_count':check(separated(a,z,p,w),'fallbackwriter registration excludes '+name)
 check(11<14 and layout.T+48<=layout.T+4*14,'fallbackwriter entry11/count admission')
 _,mem=sparse.inspect(hexraw,sparse.parser());guards=[]
 for name,a,z in [('writer',STARTS[index],550),('save',wp,40),('outer',entry,112),('next_outer',id10.STARTS[index][4],16),('registrar',d['reg'],48)]:
  raw=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==raw,'fallbackwriter strictHEX '+name);guards.append(dict(role=name,start=a,bytes=z,sha256=sha256(raw).hexdigest()))
 return dict(label=parent['label'],writer=b,strictHEX_guards=guards,selected_local_store=dict(address=dst,bytes=1,value=10,source='one initialized byte at live saveSP15',source_load_encoding='1822 QK unsigned byte',global_pointer_store=False,physical_NV_persistence_proved=False),
  protected_intervals=[dict(role=k,address=a,bytes=z) for k,a,z in protected],interval_certificate=dict(old_source_families=1024,selected_NV_count_families=4096,owner_header_exclusion_checks=owner_checks,first_copy_region_excluded=True),
  borrowed_source=dict(save_frame=32,source_offset=15,initialized_bytes=1,writer_frame=48,source_relative_writer_SP=63,selected_source_reads=1,nested_calls=0,ordinary_return_before_save_frame_release=True,A2_still_contains_pointer_on_writer_and_save_return=True,registrar_overwrites_A2_before_use=True,complete_no_escape_or_cross_event_lifetime_claimed=False),
  return_join=dict(writer_A0=0,writer_A1=1,writer_A2='borrowed pointer still in register',save_continuation=wp+34,save_frame_released=32,outer_continuation=entry+88),
  next_registration=dict(pc=entry+96,target=d['reg'],handler=handler,required_fresh_count=11,required_capacity_min=14,required_table=layout.T,entry11=layout.T+44,new_count=12,A0=11,A1=1,A2=12),
  end_cut=dict(pc=entry+100,target=d['outer_init'][5],fallback=0,gate=5,task_count=12,saved_ID6=6,local_ID7=7,local_ID8=8,local_ID9=9,local_ID10=10,ID66_byte_value=10,A0=11,A1=1,A2=12,sixth_outer_initializer_not_executed=True),
  frames=dict(outer=16,save=32,writer=48,selected_writer_peak=96,writer_and_save_released_before_next_outer=True,outer16_only_at_end=True),
  required_premises=['all inherited selected m0..3/NV-fast-failure/FF-status0/optional-flags0/source/header/metadata/ISA/first-copy/code/ABI conditions remain conditional; broader NV and writer option domains are not composed',
   'valid nonalias writer/save/outer frames, initialized source byte10 at saveSP15, ordinary RAM byte store and required savedwords/S/GP/SP/RA preserved with no adverse IRQ/DMA/reentry/externalwriters or physical effects',
   'fresh count11/capacity>=14/tableT at registrar; its count and entry11 writes are intentional publications; source A2 register persistence does not extend the released caller frame lifetime',
   'selected writerID66 has no nested provider/copy/allocator/NV calls; only normal RAM byte publication/return is proved, not persistence, installed binding, all-pointer no-escape or full cross-event consumption/release'],
  actual_installed_binding_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);by_source,first=previous.previous.families()
 return dict(schema='TSL9-fallback-ID66-local-byte-setter-ID11-count12-return-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(data,h,i,parent['profiles'][i],by_source,first) for i,(data,h) in enumerate(zip(carriers,hexes))],
  source_composition='selected FF-status savebyte10 -> ID66 length1 localRAM store/return0 -> saveRET -> fresh ID11/count12',C_reconstruction_coverage_changed=False,new_original_C_bytes=0,target_execution_or_emulation=False,
  remaining=['other writer/NV/flag domains and actual installedbindings/sourcewriters','sixth initializer4d172/4d20a and outerfinaltail','physicaleffects/IRQprogress and complete cross-event/borrowed-pointer lifetime'])


def tests(carriers):
 previous.tests(carriers);mutations=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],550);writer_body(raw,i)
  for p,d in id10.decode(raw,STARTS[i]).items():
   o=p-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:writer_body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackwriter instruction mutation escaped')
   mutations+=1
 check(mutations==374 and 2559+374==2933,'fallbackwriter mutation census')
 check([v for v in range(256) if v==1]==[1] and (66>5) and 66!=5,'fallbackwriter selected dispatch/length scalar domain')
 print('PASS:2933 original instruction/typed-load mutations rejected;550B closed writer CFG/profile;ID66 length1 vs mismatch;ID11 count12 join')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackwriter exactledger')
 print('PASS:selected writerID66 byte10/normalRET/save release/ID11 count12;5strictHEXranges/profile;exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,NV or targetnetwork;otherbranches/sixthinitializer/bindings/full lifetime UNPROVED')


if __name__=='__main__':main()
