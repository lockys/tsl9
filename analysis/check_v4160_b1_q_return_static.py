"""Offline Q preservation through selected RF return and caller boundaries.

Original operands, immutable CFG paths and closed write-interval algebra only.
No target execution/emulation, mutable target memory/provider/MMIO/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_q_writers_static as previous
import check_v4160_b1_binding_order_static as binding
import check_v4160_task_registration_static as registration
import check_v4160_initial_table_extent_static as layout

source=previous.previous
reply=source.previous
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-q-return-static.json')
MASK=0xffffffff


def separated(a,z,b,w=4):return a+z<=b or b+w<=a


def summary(b,guard):
 return dict(start=b['start'],bytes=b['bytes'],sha256=b['sha256'],instruction_count=len(b['instructions']),complete_guard=guard)


def allpaths(b):
 e=b['CFG'];todo=[(b['start'],())];out=[]
 while todo:
  a,path=todo.pop();path=path+(a,)
  check(a not in path[:-1],'Qreturn DAGpath')
  if e[a]:todo.extend((z,path) for z in e[a])
  else:out.append(path)
 return out


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());G=0x20003000;delta=80*index;Q=G+1424+delta;F=G+1344+delta;C=F+32
 protected=[(G+1340+delta,4),(G+1288+delta,4),(Q,4),(G+1292+delta,4)];effects=[];proofs={}
 def take(pc,z):
  raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'Qreturn fullbody strictHEX');return raw
 def effect(role,pc,o,a,z):
  check(all(separated(a,z,p,w) for p,w in protected),'Qreturn allfourpublishedcells preserved');effects.append(dict(role=role,pc=pc+o,address=a,bytes=z))
 lp=reply.leaves.DETAILS[index][0][0];raw=take(lp,3388);n,e=reply.guard_large(raw,index);region=reply.leaves.reachable(e,lp+352)
 check(len(region)==908 and [a for a in region if n[a].get('rd')==15]==[lp+352],'Qreturn suffix soleA5definition capture')
 check(not any(n[a]['op'] in ('jal','jalr','call_indirect') for a in region),'Qreturn no suffix callees')
 check([a for a in region if not e[a]]==[lp+3378],'Qreturn suffix soleRET')
 ss=[n[a] for a in sorted(region) if n[a]['op']=='store']
 check(len(ss)==109 and all(d['rs1']==15 and d['width']==4 for d in ss),'Qreturn suffix all109stores through heldQ')
 for d in ss:effect('large_after_capture',lp,d['pc']-lp,0x40025000+d['imm'],4)
 proofs['large_suffix']=dict(start=lp+352,end_return=lp+3378,original_body_sha256=sha256(raw).hexdigest(),reachable_instruction_count=908,stores=109,A5_defined_only_at_capture=True,no_nested_calls=True,arithmetic_packing_values_not_reconstructed=True)
 for j,role in enumerate(reply.leaves.ROLES[1:],1):
  pc=reply.leaves.DETAILS[index][0][j];raw=take(pc,reply.leaves.SIZES[j]);ln,le=reply.leaves.inspect(raw,role,index);proofs[role]=dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instruction_count=len(ln))
  for a,d in ln.items():
   if d['op']!='store':continue
   o=a-pc
   if role=='wait' and o==82:check(d['rs1']==12 and d['imm']==100,'Qreturn wait T100 origin');base=0x40024200
   else:
    expected=14 if role=='enable' else 13 if role=='wait' and o in (62,68) else 15
    check(d['rs1']==expected,'Qreturn selectedleaf Qbase origin');base=0x40025000
   effect(role,pc,o,base+d['imm'],d['width'])
 tp=reply.tail.DETAILS[index][0][2];tb=reply.tail.body(take(tp,232),'tail',index);tn={d['pc']:d for d in tb['instructions']};suffix=reply.tail.selected(tb,{},start=166)
 targets={180:0x40024100,196:0x40025008,202:0x40024250,206:G+1307+delta,210:0x4002420c}
 check([int(a,16)-tp for a in suffix if tn[int(a,16)]['op']=='store']==list(targets),'Qreturn tail cleanup exactfivewrites')
 for o,a in targets.items():effect('RFtail_cleanup',tp,o,a,tn[tp+o]['width'])
 check(tn[tp+206]['rs2']==0 and tn[tp+206]['imm']==7 and tn[tp+206]['width']==1,'Qreturn tail clearsH7')
 check([tn[tp+o]['target'] for o in (150,154,158,162)]==list(reply.leaves.DETAILS[index][0]),'Qreturn allfourtailcalleejoins')
 check(len(effects)==131,'Qreturn complete131suffixstoreintervals')
 proofs['RFtail_cleanup']=dict(start=tp+166,bytes_guarded=232,sha256=tb['sha256'],stores=5,H7_clear_PC=tp+206,H7_address=G+1307+delta,H7_value=0)
 bodies={};nodes={}
 for k,part in enumerate(binding.PARTS[:2]):
  pc=binding.STARTS[index][k];b=binding.body(take(pc,binding.SIZES[k]),part,index);bodies[part]=b;nodes[part]={d['pc']-pc:d for d in b['instructions']}
 # Complete original fill/copy helpers, mapped by first-copy source identity.
 fc=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];helpers={}
 for name,target,z in (('fill',0x2000039c,46),('copy',0x20000332,58)):
  src=int(fc['source'],16)+target-int(fc['destination'],16);r=take(src,z)
  check(target+z<=int(init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy_end_exclusive'],16),'Qreturn helper complete mappedextent')
  if name=='fill':guard=binding.callees.previous.previous.fill_source.fill_contract(r)
  else:guard=binding.callees.previous.copier.body(r,'copy',target,18,init.binding.COPY_HASH)
  helpers[name]=dict(source=src,target=target,bytes=z,sha256=sha256(r).hexdigest(),original_contract_guard='check_v4160_b1_binding_order_static.py reused leaf checks',actual_mapping_proved=False)
 cn,rn=nodes['config'],nodes['role'];cp=binding.STARTS[index][0];rp=binding.STARTS[index][1]
 check(cn[32]['imm']+cn[42]['imm']==F and cn[36]['imm']==cn[54]['imm']==32 and cn[60]['imm']==cn[42]['imm'],'Qreturn F32 fill/copy arguments')
 check(rn[10]['imm']+rn[14]['imm']==C and rn[18]['imm']==36 and rn[22]['imm']==0,'Qreturn role C36 fill arguments')
 fixed=[]
 for part,b in bodies.items():
  for d in b['stores']:
   if d['base']==2:continue
   o=d['offset']
   if part=='config':
    check(d['base'] in (8,9) and (d['base']!=9 or o>=178),'Qreturn config F/C definition boundaries');a=(F if d['base']==8 else C)+d['imm']
   else:
    check((o,d['base']) in ((42,8),(54,8)),'Qreturn role fixedstorecensus');a=(G if o==42 else C)+d['imm']
   check(separated(a,d['bytes'],Q),'Qreturn allcaller fixedstores excludeQ');fixed.append(dict(role=part,pc=b['start']+o,address=a,bytes=d['bytes']))
 check(len(fixed)==12 and cn[212]['width']==4,'Qreturn exact12nonframecaller writes including C20word')
 footprints=[dict(role='config_fill',address=F,bytes=32),dict(role='config_copy',address=F,bytes=32),dict(role='role_fill',address=C,bytes=36)]
 for x in footprints:check(separated(x['address'],x['bytes'],Q),'Qreturn bulkdestination excludesQ')
 check(Q-(C+36)==12 and Q==F+80,'Qreturn exactQ gapgeometry')
 paths=allpaths(bodies['config']);selected=[path for path in paths if cp+170 not in path and cp+198 not in path]
 check((len(paths),len(selected))==(1538,386),'Qreturn completeconfig pathcensus')
 callset={c['offset']:c['target'] for c in bodies['config']['calls']};selectedcalls={a-cp for path in selected for a in path if a-cp in callset}
 check(selectedcalls=={50,68},'Qreturn selectedconfig only matchedfill/copycalls')
 check(sum(not any(cp+o in path for o in selectedcalls) for path in selected)==2,'Qreturn twoearlyrejectpaths')
 configpaths=dict(all_graph_paths=1538,without_private_release_or_allocator=386,early_reject_paths=2,publication_paths=384,selected_paths_sha256=sha256(json.dumps(selected,separators=(',',':')).encode()).hexdigest(),excluded_call_offsets=[170,198],selected_call_offsets=[50,68],actual_APP_flag1_path_included=False)
 regpc=registration.DETAILS[index][0];reg=registration.body(take(regpc,48),index);nn={d['pc']-regpc:d for d in reg['instructions']}
 check(next(c['target'] for c in bodies['role']['calls'] if c['offset']==46)==regpc,'Qreturn role->exactregistration leaf')
 count=int(reg['count_byte'],16);check(separated(count,1,Q),'Qreturn registration fixedcount disjointQ')
 check(nn[12]['op']=='bgeu' and nn[30]['imm']==2 and nn[34]['op']=='add' and nn[36]['width']==4,'Qreturn registration dynamicaddress operands')
 return dict(label=init.binding.PROFILES[index][0],Q_slot=Q,config_base=F,role_context=C,selected_RF_return=proofs,projected_suffix_store_intervals=effects,
  RF_return_conditional=dict(Q_value=0x40025000,reply='fresh U32[0x400250d0] & 0xf0ffffff',H7_after_tail=0,extends_same_initializer_capture_proof_to_normal_parent_return=True),
  caller_bodies={p:summary(b,'check_v4160_b1_binding_order_static.py') for p,b in bodies.items()},matched_helpers=helpers,fixed_caller_writes=fixed,bulk_destinations=footprints,config_selected_paths=configpaths,
  registration=dict(leaf=summary(reg,'check_v4160_task_registration_static.py'),count_address=count,table_pointer_word=reg['table_pointer_word'],reject_local_stores=0,admitted_address='D=(freshT+4*n) mod2^32',unaligned_overlap_base_interval=[Q-1019,Q+3],aligned_overlap_base_interval_step4=[Q-1016,Q],nominal_T=layout.T,nominal_all_admitted_U8_store_envelope=[layout.T,layout.T+4*255],actualT_or_tableextent_proved=False),
  premises=['all preceding sameinitializer/Q-source premises and matching candidate helpers/code/ISA','normalaccesses/calls/polls and preservedcontext/S/SP/RA/validnonaliasframes','projectedMMIO physicaleffects disjointprotectedRAM;ordinary readableconfigsource hasnoadverse readsideeffects;noexternalIRQ/DMA/reentry/otherwriters','if role registration admits byn<c, Qpreservation additionallyrequires itsdynamicstore excludesQ andcallerframe/code; rejection hasno localstores','config Qpreservation restrictedto paths withoutprivatefree/allocator;actualAPPflag1 usesallocator','no claim about interveningparam774/othercalls beforelaterconfig/postservice'],
  actual_installed_provider_global_Q_invariant_boot_order_full_lifetime_proved=False)


def domains():
 pairs=accepted=0
 for n in range(256):
  for c in range(256):
   pairs+=1
   if n<c:accepted+=1;check(n<=254 and 4*n+4<=1020,'Qreturn admittedU8 index bound')
 check((pairs,accepted)==(65536,32640),'Qreturn complete n/c pairs')
 for Q in (0x20003590,0x200035e0):
  bases=set()
  for n in range(255):
   for d in range(-5,6):
    T=(Q-4*n+d)&MASK;D=(T+4*n)&MASK;actual=bool({(D+j)&MASK for j in range(4)}&set(range(Q,Q+4)))
    check(actual==(-3<=d<=3),'Qreturn exactunaligned overlappreimage')
    if actual:bases.add(T)
   check(separated(layout.T+4*n,4,Q),'Qreturn nominalT alladmittedU8 stores excludeQ')
  check(bases==set(range(Q-1019,Q+4)),'Qreturn completeunknownT preimageunion')
  check(sorted(t for t in bases if t%4==0)==list(range(Q-1016,Q+1,4)),'Qreturn alignedpreimages')
 print('PASS:65536 registration snapshot pairs; exact aligned/unaligned Q overlap preimages; nominalT envelopes')
 return dict(snapshot_pairs=65536,admitted_pairs=32640,possible_admitted_indices=[0,254],source_of_nominal_T='conditional first allocation; actual fresh table pointer notproved')


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-Q-selected-return-role-config-preservation-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,remaining=['actualprovider/memorymapping/IRQ/pollprogress','freshregistrationT andframe/code/targetaliasconditions','actualAPPflag1 privateallocator/releaseeffects andinterveningcalls','sameN12writer/fullretention-consumption-release/notificationlifetimes'])


def tests(carriers):
 total=0
 def perturb(raw,pc,o,decode,guard):
  d=decode(raw,pc)[pc+o];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:guard(bad)
  except RuntimeError:return
  raise RuntimeError('Qreturn return-projection mutationescaped')
 for i,data in enumerate(carriers):
  for k,part in enumerate(binding.PARTS[:2]):
   pc=binding.STARTS[i][k];raw=init.binding.take(data,pc,binding.SIZES[k]);nodes={d['pc']:d for d in binding.body(raw,part,i)['instructions']}
   for o in ((36,42,54,60,178,184,198,202,208,212) if part=='config' else (6,14,18,28,42,46,54)):
    z=nodes[pc+o]['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:binding.body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('Qreturn caller instructionmutationescaped')
    total+=1
 check(total==34,'Qreturn originalcaller mutationcensus')
 print('PASS:34 original caller/bulk/allocator-boundary instruction mutations rejected')
 suffix=0
 for i,data in enumerate(carriers):
  for j,role in enumerate(reply.leaves.ROLES):
   pc=reply.leaves.DETAILS[i][0][j];raw=init.binding.take(data,pc,reply.leaves.SIZES[j])
   for o in ((352,378,3288,3348) if role=='large' else (14,) if role=='enable' else (82,) if role=='wait' else (18,)):
    perturb(raw,pc,o,reply.leaves.decode,lambda b:reply.leaves.inspect(b,role,i));suffix+=1
  pc=reply.tail.DETAILS[i][0][2];raw=init.binding.take(data,pc,232);perturb(raw,pc,206,reply.tail.decode,lambda b:reply.tail.body(b,'tail',i));suffix+=1
 check(suffix==16,'Qreturn suffixmutationcensus')
 print('PASS:16 original capture/store/leaf/H7 return-chain mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'Qreturn exactledger')
 print('PASS:selected RF normal-return Q/H7 certificate; role/config bulk and registration boundaries; strictHEX/exactledger')
 print('PASS:NO target execution/emulation,mutabletargetmodel,hardware,replay ortargetnetwork; actualbinding/globalQ/fullownership UNPROVED')


if __name__=='__main__':main()
