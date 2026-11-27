"""Offline Q-slot zero/publisher inventory and selected initializer preservation.
Original-byte guards, immutable call/CFG paths and integer write intervals only.
No target execution/emulation or mutable RAM/provider/MMIO/IRQ state model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_rf_reply_static as previous
import check_v4160_radio_config_chain_static as radio
import check_v4160_fallback_initialization_static as startup
import check_v4160_nonmagic_service_static as nonmagic
init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-b1-q-source-static.json')


def scan_words(rows):
 hits=[];windows=0
 for a,raw in rows:
  check(a%2==0 and len(raw)==4,'Qsource alignedwindow');windows+=1;w=int.from_bytes(raw,'little')
  if w&0x707f!=0x2023:continue
  u=((w>>25)<<5)|((w>>7)&31);imm=u-4096 if u&2048 else u
  if imm in (1424,1504):hits.append(dict(pc=a,raw=raw.hex(),base_register=w>>15&31,source_register=w>>20&31,displacement=imm))
 return dict(halfword_aligned_complete_windows=windows,matches=hits,scope='standardSW opcode/funct3 andexactimmediate1424or1504 only; includesdata/overlappingdecodes; notallreachable/effectiveaddress/writeranalysis')


def image_scan(raw,base):return scan_words((base+o,raw[o:o+4]) for o in range(0,len(raw)-3,2))
def sparse_scan(mem):return scan_words((a,bytes(mem[a+k] for k in range(4))) for a in sorted(mem) if a%2==0 and all(a+k in mem for k in range(4)))


def compact(b,name):
 return dict(start=b['start'],bytes=b['bytes'],sha256=b['sha256'],instruction_count=len(b['instructions']),complete_guard=name)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());G=0x20003000;delta=80*index;qslot=G+1424+delta;protected=[(G+1340+delta,4),(G+1288+delta,4),(qslot,4),(G+1292+delta,4)];bodies={};nodes={};effects=[]
 def take(src,z):
  r=init.binding.take(data,src,z);check(sparse.captured(mem,src,z)==r,'Qsource fullbody strictHEX');return r
 def add(role,pc,off,address,width):effects.append(dict(role=role,pc=pc+off,address=address,bytes=width))
 def stores(seq,n):return [(a,d) for a in seq if (d:=n[a])['op']=='store' and d['rs1']!=2]
 for k,role in enumerate(radio.ROLES[:5]):
  pc=radio.DETAILS[index][0][k];b=radio.body(take(pc,radio.SIZES[k]),role,index);nodes[role]={d['pc']:d for d in b['instructions']};bodies[role]=compact(b,'check_v4160_radio_config_chain_static.py')
 pp=radio.DETAILS[index][0][0];pn=nodes['parent'];check(pn[pp+44]['imm']==0x40025000 and pn[pp+48]['imm']==G and pn[pp+52]['op']=='store' and pn[pp+52]['imm']==1424+delta and pn[pp+52]['rs1']==14 and pn[pp+52]['rs2']==13,'Qsource exactliteralpublisher')
 pub=dict(pc=pp+52,address=qslot,value=0x40025000,raw=pn[pp+52]['bytes'])
 check(pn[pp+12]['rs2']==0 and pn[pp+12]['imm']==1292+delta and pn[pp+40]['imm']==1340+delta and pn[pp+66]['imm']==1288+delta,'Qsource simultaneousdescriptor/T/Q/R publications')
 check(pn[pp+82]['imm']==7 and pn[pp+80]['imm']==1,'Qsource parentinitialcontextstate1')
 for a,d in stores(pn,pn):
  if a>pp+66:
   check(d['rs1']==15 and d['imm'] in (7,32,36),'Qsource parentremainingfixedstorecensus');add('parent_after_pointer_publication',pp,a-pp,G+1300+delta+d['imm'],d['width'])
 for role,base in (('registers',0x40024200),('bulk',0x40025000),('pulse',0x40025000),('bits',0x40024100)):
  pc=radio.DETAILS[index][0][radio.ROLES.index(role)]
  for a,d in stores(nodes[role],nodes[role]):add(role,pc,a-pc,base+d['imm'],d['width'])
 check(sum(x['role'] in ('registers','bulk','pulse','bits') for x in effects)==49,'Qsource complete49radio helperprojectedstores')
 check([pn[pp+o]['target'] for o in (100,102,106)]==[radio.DETAILS[index][0][k] for k in (1,2,4)] and pn[pp+114]['rd']==0,'Qsource parentthreecalls/tailspine')
 # Reuse the two RF cases for the publisher-established state1/A0=13.
 tp=previous.tail.DETAILS[index][0][2];tb=previous.tail.body(take(tp,232),'tail',index);tn={d['pc']:d for d in tb['instructions']};bodies['RFtail']=compact(tb,'check_v4160_rf_tail_return_static.py')
 fp=previous.tail.DETAILS[index][0][0];fb=previous.tail.body(take(fp,198),'rf',index);fn={d['pc']:d for d in fb['instructions']};bodies['RFhelper']=compact(fb,'check_v4160_rf_tail_return_static.py')
 paths={name:previous.tail.selected(fb,choices) for name,choices in (('Tlow2zero',{38:124}),('Tlow2nonzero',{38:40,58:78,80:144,146:164,166:170,172:176,180:112}))}
 for name,path in paths.items():
  seq=list(map(lambda a:int(a,16),path));ss=stores(seq,fn);check(fp+76 not in seq and all(d['rs1']!=8 for _,d in ss),'Qsource state1 excludesindirectcallback andcontext8/9stores')
  check([a-fp for a,d in ss]==([18,132] if name=='Tlow2zero' else [18,116,132]),'Qsource exactselectedRFstorecensus')
  for a,d in ss:add('RFhelper_'+name,fp,a-fp,G-260+delta if a==fp+116 else 0x4002420c,d['width'])
 rp=previous.tail.DETAILS[index][0][1];rb=previous.tail.body(take(rp,130),'reset',index);rn={d['pc']:d for d in rb['instructions']};bodies['reset']=compact(rb,'check_v4160_rf_tail_return_static.py')
 resetpaths=[previous.tail.selected(rb,{28:t,94:116}) for t in (30,38)]
 targets={12:0x40024250,20:0x40024200,56:0x40024100,76:0x40025008,82:0x40024250,124:G+1307+delta}
 for path in resetpaths:check([a-rp for a,d in stores([int(v,16) for v in path],rn)]==list(targets),'Qsource descriptorzero exactresetstores')
 for o,address in targets.items():add('reset_descriptorzero',rp,o,address,rn[rp+o]['width'])
 tailpath=previous.tail.selected(tb,{28:32,34:38,54:58},cut=150);seq=[int(a,16) for a in tailpath];targets={62:0x4002420c,104:0x40024100,116:0x40024100,128:0x40024100,138:0x40025008,148:0x40024250}
 check([a-tp for a,d in stores(seq,tn)]==list(targets),'Qsource tailprelarge exactstores')
 for o,address in targets.items():add('RFtail_beforelarge',tp,o,address,tn[tp+o]['width'])
 # Both large branches, including the mapped helper, up to the Q capture.
 lp=previous.leaves.DETAILS[index][0][0];ln,le=previous.guard_large(take(lp,3388),index);check(tn[tp+150]['target']==lp,'Qsource exacttailtolargejoin');largepaths={}
 special={178:G-90+delta,190:G-89+delta,246:G+1429+delta,264:G+1420+delta,318:G+1428+delta,336:G+1412+delta,3380:G+1416+delta}
 for name,t in (('magic',3380),('nonmagic',120)):
  path=previous.leaves.previous.paths.chain(le,lp,{lp+116:lp+t},lp+352);largepaths[name]=path;seq=[int(a,16) for a in path]
  for a,d in stores(seq,ln):
   o=a-lp
   if o in special:address=special[o]
   else:check(d['rs1']==15 and d['width']==4,'Qsource largeprefix allotherprojectedstoresQword');address=0x40025000+d['imm']
   add('large_'+name+'_beforecapture',lp,o,address,d['width'])
 nd=nonmagic.DETAILS[index];source,entry=nd[:2];nr=take(source,54);nb=nonmagic.body(nr,'service',index);nn={d['pc']:d for d in nb['instructions']};bodies['nonmagic_service']=compact(nb,'check_v4160_nonmagic_service_static.py')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+entry-int(fc['destination'],16)==source and entry+54<=int(mapping['first_copy_end_exclusive'],16),'Qsource mappedhelper sourcecomplete')
 check([d['pc']-entry for d in nb['instructions'] if d['op']=='store']==[14] and nn[entry+14]['rs1']==14 and nn[entry+14]['imm']==100,'Qsource mappedhelper soleT100store');add('nonmagic_service',entry,14,0x40024264,4)
 for o in (160,226,302):
  au=ln[lp+o-4];d=ln[lp+o];check((lp+o-4+au['imm']+d['imm'])&0xfffffffe==entry,'Qsource all3nonmagiccalleejoins')
 check((ln[lp+352]['rs1'],ln[lp+352]['imm'],ln[lp+352]['rd'])==(8,1424+delta,15),'Qsource laterfreshcapture samefixedslot')
 # Simultaneous pointer/descriptor invariant: all selected nonframe effects
 # after establishment are disjoint, under the stated memory-base premises.
 for x in effects:
  for p,z in protected:check(x['address']+x['bytes']<=p or p+z<=x['address'],'Qsource projectedwrites excludeall4publishedpointer/descriptorcells')
 fd=startup.DETAILS[index];zr,zn,ze,zc=startup.zero_contract(data,fd[1],fd[3],fd[4]);check(sparse.captured(mem,fd[1],30)==zr,'Qsource fullzerobody strictHEX');check(fd[3]<=qslot and qslot+4<=fd[4]+4 and (qslot-fd[3])%4==0,'Qsource zerohelper includesQword')
 bin_inventory=image_scan(data,0x40000);hex_inventory=sparse_scan(mem);expected=[dict(pc=pub['pc'],raw=pub['raw'],base_register=14,source_register=13,displacement=1424+delta)]
 check(bin_inventory['matches']==hex_inventory['matches']==expected,'Qsource exactone standardSWimm candidate hit inbin/allstrictHEX')
 return dict(label=init.binding.PROFILES[index][0],Q_slot=qslot,publisher=pub,bodies=bodies,zero_source=dict(code_source=fd[1],bytes=30,sha256=sha256(zr).hexdigest(),write_range=[fd[3],fd[4]+4],Qword_one_based_index=(qslot-fd[3])//4+1,value=0,actualzero_execution_ororder_proved=False),
  binary_inventory=bin_inventory,full_sparse_inventory=hex_inventory,protected_cells=[dict(address=a,bytes=z) for a,z in protected],conditional_projected_write_intervals=effects,
  selected_RF_paths=paths,selected_reset_paths=resetpaths,selected_RFtail_beforelarge=tailpath,large_prefix_paths_to_capture=largepaths,
  initializer_spine_Q_capture=dict(value=0x40025000,capture=lp+352,absolute_masked_reply='fresh U32[0x400250d0] & 0xf0ffffff',conditional_within_this_direct_initializer_spine_only=True),
  required_premises=['matching candidate code and radio parent reachespublication','fourpointer/descriptor cells established byparent;selectedstate1 RFcases andneededcallee context/frames preserved','validnonaliasframes;allprojected400xxxxx accesses physicallyseparate from2000xxxx cells','allnestedcalls/polls/instructions/accesses complete normally;noexternalIRQ/DMA/reentry or otherwriter modifiesprotectedcells','memory-baseorigin projections remainvalid acrosscalls;numericaddress disjointness notphysicalmapping proof'],
  limitations=['inventory excludes computed/otherbase/narrow/copy/fill/alias/unaligned writes andruntimecodechanges','zero/helper/publisher existence doesnot prove actualstartuporder','laterindependentpostservice RF entry stillneeds itsownpublication-to-capture preservation','freshMMIOword notprovedequal toearlier/laterstore'],
  actualinstalledQ_globalinvariant_allwriters_eventorder_physicalreadback_pollprogress_fullownership_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes);app=image_scan(image,0x8000);check(not app['matches'],'Qsource originalAPP hasnoexactSWimmediate hits')
 return dict(schema='TSL9-B1-Q-slot-zero-publication-selected-preservation-static-v1',APP_sha256=sha256(image).hexdigest(),APP_encoding_inventory=app,profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['othercomputed/narrow/copy/fill/aliaswriters/actualstartuporder','Qpreservationforlaterpostserviceentry vsoneinitializerspine','physicalMMIOmapping/readback/IRQ/pollprogress','sameN12writer/retainedallocation/fullconsumption-release/notificationlifetimes'])


def tests(carriers):
 count=0
 def mutate(raw,pc,o,decode,guard):
  nonlocal count
  d=decode(raw,pc)[pc+o];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:guard(bad)
  except RuntimeError:pass
  else:raise RuntimeError('Qsource mutationescaped')
  count+=1
 for i,data in enumerate(carriers):
  pp=radio.DETAILS[i][0][0];r=init.binding.take(data,pp,118)
  for o in (44,48,52,100,102,106,114):mutate(r,pp,o,radio.decode,lambda b:radio.body(b,'parent',i))
  fd=startup.DETAILS[i];r=bytearray(data);r[fd[1]-0x40000+22]^=0x80
  try:startup.zero_contract(r,fd[1],fd[3],fd[4])
  except RuntimeError:pass
  else:raise RuntimeError('Qsource zerostoremutationescaped')
  count+=1
  lp=previous.leaves.DETAILS[i][0][0];r=init.binding.take(data,lp,3388);mutate(r,lp,352,previous.leaves.decode,lambda b:previous.guard_large(b,i))
 check(count==18,'Qsource mutationcensus')
 for off in (1424,1504):
  # Closed SW immediate bitfield oracle, no decoded instruction is run.
  w=((off>>5)<<25)|(13<<20)|(14<<15)|(2<<12)|((off&31)<<7)|0x23;row=image_scan(w.to_bytes(4,'little'),0)['matches'];check(len(row)==1 and row[0]['displacement']==off and row[0]['base_register']==14,'Qsource independentSWfieldoracle')
 print('PASS:18 publisher/call/zero/capture mutations rejected;BIN/fullstrictHEX inventory and selectedwriteinterval certificates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'Qsource exactledger')
 print('PASS:Qslot zero/literalpublisher/freshcapture joins;selectedinitializer preserves40025000 underexplicitpremises;strictHEX/exactledger')
 print('PASS:NO target execution/emulation;allwriters/actualorder/globalQinvariant/physicalmapping/fullownership UNPROVED')


if __name__=='__main__':main()
