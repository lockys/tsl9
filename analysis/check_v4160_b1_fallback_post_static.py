"""Offline fallback preservation through nominal post-config callee cases.

Original bodies/CFGs and closed footprint/geometry certificates only; no
target execution/emulation or mutable heap/NV/RAM/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_fallback_source_static as previous
import check_v4160_post_config_static as post
import check_v4160_heap_bootstrap_static as heap
import check_v4160_initial_table_extent_static as layout
import check_v4160_post_shortcut_preservation_static as shortcut
import check_v4160_mismatch_temp_release_static as mismatch

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-fallback-post-static.json')


def separated(a,z,b,w=4):return a+z<=b or b+w<=a


def guard_post(raw,index):
 pc=post.DETAILS[index][0];ctx=0x2000319c+80*index;n=post.decode(raw,pc);s=post.specs(pc,ctx,post.DETAILS[index]);pairs=(48,66,128,156)
 check(set(n)==set(s)|{pc+o+d for o in pairs for d in (0,4)},'fallbackpost fullpost boundaries')
 for a,f in s.items():init.g(n,a,'fallbackpost operand '+hex(a-pc),**f)
 for o,t in ((48,0x2000039c),(66,0x2000039c),(128,0x20000040),(156,0x2000039c)):init.pair(n,pc+o,1,t,'fallbackpost linkedcallee')
 check(len(raw)==272 and sha256(raw).hexdigest()==post.DETAILS[index][-1],'fallbackpost completepost identity')
 edges,cycles=init.timer.cfg(n,pc);check(not cycles,'fallbackpost postCFG acyclic')
 return n,{int(a,16):[int(z,16) for z in zs] for a,zs in edges.items()}


def footprint_cases():
 unique={r['N0']:r for r in layout.facts()};temp={r['capacity']:r for r in mismatch.geometry_cases()};rows=[]
 check(set(unique)==set(temp) and len(unique)==67,'fallbackpost exact67capacitycases')
 for cap,r in sorted(unique.items()):
  t=temp[cap];q,R=r['request'],r['rounded_payload'];M=layout.P+R;P2=M+8;N=P2+256
  check((M,P2,N)==tuple(int(t[k],16) for k in ('temporary_header','temporary_payload','next_free_header')),'fallbackpost first/secondallocation joins')
  first=[(layout.B,8),(M,8),(layout.P,q)]
  second=[(M,8),(N,8),(P2,256),(P2,4),(M,8)]
  table=[(layout.T+4*j,4) for j in range(3)]
  check(layout.T==layout.P+576 and layout.T+12<=layout.T+4*cap<=layout.P+q<=layout.P+R==M,'fallbackpost threebuiltins insidefirstallocation')
  check(layout.B<M<P2<N<layout.E and N+8<=layout.E,'fallbackpost tempheaders separatednonwrapping')
  rows.append(dict(capacity=cap,first_request=q,first_R=R,first_header=layout.B,remainder_header=M,first_payload=[layout.P,layout.P+q],temp_payload=[P2,P2+256],temp_next_header=N,
   first_effect_intervals=first,mismatch_effect_intervals=second,builtin_intervals=table))
 return rows


def profile(data,hexraw,index,parent,hp,pp,sp,mp,rows):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=post.DETAILS[index][0];slot=parent['fallback_slot'];D=parent['config_destination'];ctx=D-80
 check(parent['initializer']['postconfig_target']==pc and ctx==0x2000319c+80*index,'fallbackpost priorzero/callee/context joins')
 raw=init.binding.take(data,pc,272);check(sparse.captured(mem,pc,272)==raw,'fallbackpost strictHEX postbody');n,e=guard_post(raw,index)
 check(pp['target']==hex(pc) and sp['post_start']==hex(pc) and mp['IO_entry']==pp['calls'][6]['target'],'fallbackpost existingfullcallee proof joins')
 effects=[];code=[]
 def add(role,a,z,origin=None):
  check(0<=a<a+z<=0x100000000 and separated(a,z,slot),'fallbackpost projectedinterval excludesfallback')
  effects.append(dict(role=role,address=a,bytes=z,origin=origin))
 def source_guard(a,z,role):
  b=init.binding.take(data,a,z);check(sparse.captured(mem,a,z)==b,'fallbackpost originalHEX '+role);code.append(dict(role=role,source=a,bytes=z,sha256=sha256(b).hexdigest()));return b
 source_guard(pc,272,'post')
 for x in pp['fixed_stores_with_live_base_premise']:add('post_fixed',int(x['address'],16),x['bytes'],int(x['pc'],16))
 for x in pp['fixed_zero_fill_requests']:add('post_fixed_fill',int(x['address'],16),x['bytes'])
 check(len(effects)==10,'fallbackpost 8fixedwrites/2fills')
 for b in hp['bodies']:
  a=int(b['start'],16);source_guard(a,b['bytes'],'heap_'+b['role'])
 check(hp['config_base']==hex(D) and hp['slots']['fallback']==hex(slot),'fallbackpost bootstrap configuredsource')
 for k,w in (('small_head',4),('large_head',4),('sentinel',4),('accounting',2),('late_reset',4)):add('heap_fixed_'+k,int(hp['slots'][k],16),w)
 # These are encoded store destinations in the nominal bootstrap geometry,
 # not a constructed or traversed heap image.
 for a,z in ((layout.A,4),(layout.A+4,2),(layout.A+6,2),(layout.B,4),(layout.B+4,2),(layout.B+6,2)):add('bootstrap_header',a,z)
 add('core_account',ctx+6,2);add('core_fill_copy_control',0x4002420c,4)
 add('IO_cache_pointer',ctx+32,4);add('IO_cleanup_neighbor',ctx+36,4)
 for j in range(3):add('mismatch_NV_program_destination',mismatch.NV+256*j,256)
 check(len(effects)==28,'fallbackpost common28intervals')
 # Every first-allocation payload, each second-allocation header/payload/free
 # footprint and three table words excludes the added protected fallback word.
 for r in rows:
  for label in ('first_effect_intervals','mismatch_effect_intervals','builtin_intervals'):
   for a,z in r[label]:check(separated(a,z,slot) and layout.H<=a<a+z<=layout.E,'fallbackpost all67heap/table footprint exclusions')
 check(slot+4<layout.H and layout.H==0x2000418c and layout.L==0x7000,'fallbackpost nominalsource domain')
 # Original helper and I/O identities are checked in their existing complete
 # contracts; also bind every byte of the reused resident bodies to strict HEX.
 for role,a,z in (('core',mismatch.core.DETAILS[index][0],208),('private_release',mismatch.release.DETAILS[index][0],212),('fill',(0x4060c,0x4064c)[index],46),('copy',(0x405a2,0x405e2)[index],58),('IO',shortcut.io.DETAILS[index][0],160)):
  source_guard(a,z,role)
 check(set(sp['config_IO']['selected_paths'])==set(shortcut.CHOICES),'fallbackpost all4shortcut cases')
 check(sp['conditional_post_reply']==1 and mp['conditional_IO_and_post_reply']==0,'fallbackpost lastIO reply classification')
 check(mp['conditional_post_count']==sp['post_suffix_count']==3 and sp['nominal_P']==hex(layout.P) and sp['nominal_T']==hex(layout.T),'fallbackpost builtin/table sources preserved')
 check([int(x['address'],16) for x in sp['builtin_word_stores']]==[layout.T+4*j for j in range(3)],'fallbackpost exactthree nominalstores')
 for a,d in n.items():
  if a>=pc+200:check(d.get('rd')!=10,'fallbackpost suffix noA0defs')
 check(n[pc+140]['rs1']==10 and n[pc+136]['rs2']==10 and layout.P!=0,'fallbackpost fitreply admitsnormalcontinuation')
 # The post return value is discarded by the initializer's published path.
 fd=previous.fallback.DETAILS[index];cfg=fd[2];ir,inn,ie,_=previous.fallback.config_contract(data,cfg,D,fd[9],fd[10]);check(sparse.captured(mem,cfg,228)==ir,'fallbackpost strictHEX initializer')
 suffix=post.reachable({int(a,16):list(map(lambda z:int(z,16),zs)) for a,zs in ie.items()},cfg+208)
 check([a-cfg for a in sorted(suffix)]==[208,210,212,214,216,218,220],'fallbackpost initializer straight epilogue')
 check(not any(inn[a]['op'] in ('store','jal','jalr','call_indirect') for a in suffix),'fallbackpost initializer epilogue nowrites/calls')
 check((inn[cfg+208]['op'],inn[cfg+208]['rd'],inn[cfg+208]['imm'],inn[cfg+216]['op'],inn[cfg+216]['rd'],inn[cfg+216]['rs2'])==('li',15,0,'mv',10,15),'fallbackpost initializer discardsIOreply/forces0')
 return dict(label=parent['label'],fallback_slot=slot,post_entry=pc,post_RET=pc+270,post_bytes=272,post_instruction_count=len(n),initializer_call=cfg+206,initializer_published_path_RET=cfg+220,
  original_code_guards=code,common_effect_intervals=effects,all67_geometry_intervals_exclude_fallback=True,
  bootstrap=dict(fresh_H=layout.H,fresh_L=layout.L,small_header=layout.A,large_header=layout.B,sentinel=layout.E,walker_two_node_sum=28104,actual_fresh_fields_or_ownership_proved=False),
  first_allocation=dict(request='576+6*N0',N0_domain=[14,212,3],R_domain=[660,1848],pointer=layout.P,table=layout.T,no_search_or_fallback_on_selected_first_fit=True,required_later_samples=['N1=N2=N0','freshP_prime=P','preservedtable/count/callback/code/frames']),
  IO_cases=dict(shortcuts=list(sp['config_IO']['selected_paths']),equal_readback_requires_actual4byte_result=True,shortcut_post_reply=1,mismatch=dict(fresh_NV=mismatch.NV,fresh_length=256,fresh_record_count=3,read_callback=0x1979a,write_callback=0x197be,write_destinations=[mismatch.NV+256*j for j in range(3)],same_fresh_temp_pointer_required=True,temp_free='prevallocated/nextfree:onlyforwardmerge',mismatch_post_reply=0)),
  conditional_result=dict(entry_fallback=0,post_normal_return_fallback=0,initializer_normal_return_fallback=0,initializer_reply=0,reply_does_not_prove_NV_or_allocation_success=True),
  required_premises=['matchingoriginalcode/ISA/provider/helper/firstcopymapping;previousinitializer/getter sourcepremises','freshheapH2000418c/L7000 andnominalbootstrap writes/links/headers/account/source preservation;validownednonwrappingframes/heap/globals','firstfit/payload/table extent andfreshP_prime/P/capacity equalities;allrequiredGPR/SP/RA/S/frame/code preservation','IOshortcut gates absent,orcompleted4byte readback equalstofreshbase;alternativelymatchingmismatch NV08077c00/length256/count3/readwritebindings andunequalresult','mismatch initialread/tempallocate/fill/3callbacks/free finishnormally;freshcache pointers equalP2 andheaders/context unchangedasrequired','allprojectedNV/MMIO/FENCE effects physicalseparatefromprotectedRAM;noadversealiases/IRQ/DMA/reentry/otherwriters;polls/accesses complete','proofendsatinitializerRET;doesnotcrossAPP19106/wrapper/registration/param774/otherlaterboundaries'],
  actual_boot_provider_NV_progress_header_ownership_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 hp=heap.derive(image,carriers,header);pp=post.derive(image,carriers,header);sp=shortcut.derive(image,carriers,header,coverage);mp=mismatch.derive(image,carriers,header,coverage)
 rows=footprint_cases()
 check(len(layout.facts())==256 and len(rows)==67,'fallbackpost fullinput/uniquegeometry domain')
 return dict(schema='TSL9-fallback-nominal-post-config-shortcut-mismatch-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i],hp['profiles'][i],pp['profiles'][i],sp['profiles'][i],mp['profiles'][i],rows) for i,(d,h) in enumerate(zip(carriers,hexes))],capacity_geometry_cases=rows,
  source_composition='previous matchedAPPsource/copy/getter zero-atcfg+ce plus selectedpostcase ->initializer normalRET zero;notactualboot/freshfield proof',
  reused_APP_write_family=mp['reused_APP_bodies'],new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,
  remaining=['APP19106/remainingbuilder/wrapper/registration/param774 preservation','actualinstalledprovider/sourceandheader snapshots/physicalmapping/IRQpollprogress','otherNVlength/count/callbackdomains andfullretention-consumption-release/notificationlifetime'])


def tests(carriers):
 count=0
 for i,data in enumerate(carriers):
  pc=post.DETAILS[i][0];raw=init.binding.take(data,pc,272);n,_=guard_post(raw,i)
  for o in (4,18,30,36,56,60,74,118,128,136,140,142,156,164,168,174,180,190,194,198,200,202,220,242,256,260):
   z=n[pc+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard_post(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackpost mutationescaped')
   count+=1
 check(count==52,'fallbackpost mutationcensus');print('PASS:52 original post stores/source/callee/branch/table/return-boundary mutations rejected')
 epilogues=0
 for i,data in enumerate(carriers):
  fd=previous.fallback.DETAILS[i];cfg,D,h,b=fd[2],fd[5],fd[9],fd[10];_,n,_,_=previous.fallback.config_contract(data,cfg,D,h,b)
  for o in (208,216):
   z=n[cfg+o]['size'];p=cfg-0x40000+o;bad=bytearray(data);bad[p:p+z]=(int.from_bytes(bad[p:p+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:previous.fallback.config_contract(bad,cfg,D,h,b)
   except RuntimeError:pass
   else:raise RuntimeError('fallbackpost epiloguemutationescaped')
   epilogues+=1
 check(epilogues==4,'fallbackpost epiloguemutationcensus');print('PASS:4 original initializer forced-zero epilogue mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'fallbackpost exactledger')
 print('PASS:nominal post-config shortcut/mismatch/initializerRET fallback-zero certificates;strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork;laterwrapper/actualbinding/lifetime UNPROVED')


if __name__=='__main__':main()
