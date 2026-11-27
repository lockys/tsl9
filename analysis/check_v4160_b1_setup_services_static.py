"""Offline setup -> registrar/RAM dispatch/channel/reset static contracts.
Reuse complete original bodies; immutable CFG/def-use/frame and scalar proofs.
No target execution/emulation, mutable target state, hardware or network.
"""
import argparse,json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_setup_full_static as previous
import check_v4160_loaded_hook_sources_static as hooks
import check_v4160_constructor_consumer_tail_static as dispatch
import check_v4160_rf_tail_return_static as reset
import check_v4160_b1_channel_static as channel
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-b1-setup-services-static.json')
PARTS=('registrar','dispatch','channel','reset')
STARTS=((0x43b28,0x200026ba,0x63b0e,0x63e58),(0x43bb4,0x20002706,0x63bf8,0x63f42))
SOURCES=((0x43b28,0x4292a,0x63b0e,0x63e58),(0x43bb4,0x429b6,0x63bf8,0x63f42))
SIZES=(22,250,326,130)
COUNTS=(8,93,124,48)
BRANCHES=previous.BRANCHES


def guard(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 if part=='registrar':b=hooks.body(raw,part,pc,456+80*index,hooks.DETAILS[index][-1][3])
 elif part=='dispatch':b=dispatch.body(raw,'ramtail',index)
 elif part=='channel':b=channel.body(raw,index)
 else:b=reset.body(raw,'reset',index)
 n={d['pc']:d for d in b['instructions']};check((len(raw),len(n))==(SIZES[k],COUNTS[k]),'setupservices reusedcomplete size/count')
 # Keep typed loads independently explicit, in addition to inherited hashes.
 typed=[]
 for a,d in n.items():
  if d['op']=='load' and d['size']==4:
   f3={1:4,2:5,4:2}[d['width']];check(int.from_bytes(raw[a-pc:a-pc+4],'little')&0x707f==(f3<<12|3),'setupservices unsignedtypedload');typed.append(a-pc)
 return b,n,typed


def cfg(n):
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jr':check(d['rs1']==1,'setupservices RET RA');q=[];rets.append(a)
  elif op in ('jal','jalr','call_indirect'):
   check(d['rd']==1 and op!='call_indirect','setupservices onlylinkedknowncall');target=d.get('target')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'setupservices directPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append((a,target))
  check(all(z in n for z in q),'setupservices localCFG');e[a]=q
 return e,calls,rets


def reachable(e,start):
 seen=set();todo=[start]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 return seen


def path(e,start,end):
 seen=set();q=deque([(start,[start])])
 while q:
  a,p=q.popleft()
  if a==end:return p
  if a not in seen:seen.add(a);q.extend((z,p+[z]) for z in e[a])
 return None


def reaching(e,n,start,at,reg,preserved_calls=()):
 pred={a:[] for a in e}
 for a,zs in e.items():
  for z in zs:pred[z].append(a)
 todo=pred[at][:];seen=set();defs=set();entry=at==start
 while todo:
  a=todo.pop();d=n[a]
  if d.get('rd')==reg or (reg==10 and d['op'] in ('jal','jalr','call_indirect') and a not in preserved_calls):defs.add(a-start);continue
  if a==start:entry=True
  if a not in seen:seen.add(a);todo.extend(pred[a])
 return defs,entry


def own_frame(n,pc,size,saved,allocation,deallocation,ret):
 stores={(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2}
 loads={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}
 check(stores==loads==set(saved),'setupservices ownframe save/load')
 check([(a-pc,d['imm']) for a,d in n.items() if d.get('rd')==2]==[(allocation,-size),(deallocation,size)],'setupservices ownSPbalanced')
 check(n[pc+ret]['op']=='jr','setupservices ownRET')


def service_bodies(data,mem,index):
 bs={}
 for k,part in enumerate(PARTS):
  pc,src,z=STARTS[index][k],SOURCES[index][k],SIZES[k];raw=init.binding.take(data,src,z)
  check(sparse.captured(mem,src,z)==raw,'setupservices all reusedbytes strictHEX')
  b,n,typed=guard(raw,part,index);e,calls,rets=cfg(n)
  check(reachable(e,pc)==set(n),'setupservices full syntacticentryreach')
  expected=[(pc+44,STARTS[index][2])] if part=='dispatch' else []
  check(calls==expected,'setupservices exactsingle nestedchannelcall')
  bs[part]=dict(start=pc,source=src,bytes=z,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,returns=rets,typed_load_offsets=typed,reused_complete_body=True)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy'];src=int(f['source'],16);dst=int(f['destination'],16);pc=STARTS[index][1]
 check(src+pc-dst==SOURCES[index][1] and dst<=pc and pc+250<=int(mapping['first_copy_end_exclusive'],16),'setupservices completeRAMbody startupcopymapping')
 return bs


def joined(data,index,bs):
 pc=previous.STARTS[index];setup=previous.body(init.binding.take(data,pc,previous.SIZE),index);sn={d['pc']:d for d in setup['instructions']};se=setup['CFG'];parts={r:{d['pc']:d for d in b['instructions']} for r,b in bs.items()}
 # Registrar's unique store is indexed by the explicit setup A1=0.
 rp=bs['registrar']['start'];rn=parts['registrar'];re={a:list(z) for a,z in bs['registrar']['CFG'].items()}
 check(rn[rp]['imm']==4 and rn[rp+2]['op']=='bltu' and rn[rp+2]['rs2']==11 and rn[rp+18]['op']=='store','setupservices registrar unsignedindex/store')
 check(reaching(se,sn,pc,pc+0x344,10)==({0x322},False) and reaching(se,sn,pc,pc+0x344,11)==({0x308},False),'setupservices registrar actualargdefinitions')
 callback=sn[pc+0x304]['imm']+sn[pc+0x322]['imm'];check(callback==(0x55480,0x5555e)[index] and sn[pc+0x308]['imm']==0,'setupservices literalcallback/index0')
 check(rn[rp+6]['imm']+rn[rp+12]['imm']==0x200031c8+80*index,'setupservices exactregistrarslot0')
 check(all(d.get('rd') not in (1,2,3,8,9,*range(18,28),10) for d in rn.values()),'setupservices registrar preservesA0/S/RA/SP/GP')
 check(not(rn[rp]['imm']<sn[pc+0x308]['imm']),'setupservices literal unsignedindexzero comparison');re[rp+2]=[rp+6]
 registrar_route=path(re,rp,rp+20);check(registrar_route==[rp+o for o in (0,2,6,10,12,16,18,20)],'setupservices indexzero stores withoutcallbackinvocation')
 # All setup RAM admissions pass a concrete zero mode and separate byte samples.
 for call,o0,o1,o2 in ((0x358,0x350,0x34c,0x348),(0x5a6,0x572,0x592,0x58e)):
  for r,o in ((10,o0),(11,o1),(12,o2)):check(reaching(se,sn,pc,pc+call,r)==({o},False),'setupservices exactRAMargdefs')
  check(sn[pc+o0]['imm']==0 and sn[pc+o1]['width']==sn[pc+o2]['width']==1 and sn[pc+o1]['imm']==128 and sn[pc+o2]['imm']==17,'setupservices RAMzero/byteargs')
 dp=bs['dispatch']['start'];dn=parts['dispatch'];de={a:list(z) for a,z in bs['dispatch']['CFG'].items()}
 check(dn[dp+16]['op']=='bnez' and dn[dp+16]['rs1']==10,'setupservices RAMmodebranch')
 de[dp+16]=[dp+18];seen=reachable(de,dp);zero={a:[z for z in de[a] if z in seen] for a in de if a in seen};zn={a:dn[a] for a in zero}
 check(not any(dp+o in seen for o in (126,132,164,174,216,238,244)),'setupservices nonzeroRAMmodes excluded by actualzeroargs')
 check(reaching(zero,zn,dp,dp+44,10)==({32},False) and dn[dp+32]['op']=='mv' and dn[dp+32]['rs2']==15 and reaching(zero,zn,dp,dp+32,15)==({18},False),'setupservices childA0fromsavedentryA1')
 check(dn[dp+18]['rs2']==11 and reaching(zero,zn,dp,dp+18,11)==(set(),True),'setupservices childmode originaldispatchA1')
 check(reaching(zero,zn,dp,dp+44,11)==({34},False) and dn[dp+34]['rs2']==12 and reaching(zero,zn,dp,dp+34,12)==(set(),True),'setupservices childduration originaldispatchA2')
 check(reaching(zero,zn,dp,dp+124,10)==({44},False),'setupservices RAMRET forwardschannelA0')
 check(dn[dp+20]['imm']==dn[dp+112]['imm']==100 and dn[dp+20]['rs1']==14 and dn[dp+112]['rs1']==13,'setupservices twoheldT100 polls distinctcaptures')
 check(dn[dp+36]['imm']==2 and dn[dp+36]['rs2']==0 and dn[dp+76]['imm']==5 and dn[dp+80]['imm']==1,'setupservices orderedcontextclear offsets')
 check(dn[dp+86]['imm']==0 and dn[dp+86]['rs2']==14 and dn[dp+84]['imm']==2,'setupservices postchildfreshT0=2')
 own_frame(dn,dp,16,((8,8),(1,12),(9,4)),0,122,124)
 check({d['rd'] for d in dn.values() if d.get('rd',0)} & {3,18,19,20,21,22,23,24,25,26,27}==set(),'setupservices RAMotherS/GPnonwrites')
 cycles=[sorted(a-dp for a in g) for g in dispatch.previous.sccs(zero) if len(g)>1 or g[0] in zero[g[0]]]
 check(sorted(cycles)==[[20,22],list(range(100,116,2))],'setupservices zeroRAM exacttwocycles')
 for a,z in ((20,22),(100,114)):
  check(dp+a in seen and dp+z in seen,'setupservices zeroRAM poll admission')
 # Channel's full existing paths pin the last A0 definition to a word load.
 cb=bs['channel'];cp=cb['start'];cn=parts['channel'];paths=channel.paths(cb);scalar=channel.scalar_certificates(cb);reply={}
 for mode,load in ((0,0x120),(1,0x4a),(2,0xee),(3,0xba)):
  for desc in (0,1):
   key=f'mode{mode}_descriptor{desc}';seq=paths[key];check(cn[cp+load]['width']==4 and cn[cp+load]['imm']==12 and cn[cp+load]['rs1']==13,'setupservices fullcapturedH12reply')
   check([o for o in seq if cn[cp+o].get('rd')==13 and o<load]==[0xa,0x14,0x36] if desc else [o for o in seq if cn[cp+o].get('rd')==13 and o<load]==[0x36],'setupservices replybase fromfirstHslot;descriptor earlierA3 overwritten')
   check(cn[cp+0x36]['op']=='load' and cn[cp+0x36]['imm']==1340+80*index,'setupservices channel capturedHslot')
   check(not any(cn[cp+o].get('rd')==10 for o in seq[seq.index(load)+1:]),'setupservices channel normalRET keepsfullword')
   reply[key]=dict(load=load,RET=seq[-1],word_width=4,base_definition=0x36)
 check(set(cb['returns'])=={cp+0x78,cp+0xe4} and cb['calls']==[],'setupservices channel nochild')
 zp=bs['reset']['start'];nn=parts['reset'];check({d['rd'] for d in nn.values() if d.get('rd',0)}=={12,13,14,15},'setupservices reset onlyA2..A5defs')
 check(all(d.get('rs1')!=10 and d.get('rs2')!=10 for d in nn.values()),'setupservices reset notreadA0')
 check(reaching(se,sn,pc,pc+0x38c,10,(pc+0x360,pc+0x344))==({0x358,0x5a6},False),'setupservices setupRET throughA0preserving reset joinslastRAMdispatch')
 check(nn[zp+94]['op']=='beqz' and nn[zp+104]['op']==nn[zp+114]['op']=='store','setupservices descriptor twoORstores remainpossible')
 return dict(setup_start=pc,setup_sha256=setup['sha256'],registrar=dict(callback=callback,index=0,slot=0x200031c8+80*index,syntactic_route=[a-rp for a in registrar_route],A0_unchanged=True,does_not_invoke_callback=True),
  RAM_calls=[0x358,0x5a6],RAM_zero_mode_CFG=zero,RAM_zero_mode_instruction_offsets=sorted(a-dp for a in seen),RAM_zero_mode_cyclic_SCC_offsets=sorted(cycles),RAM_child_args=['freshsetupU8P128','separatelyfreshsetupU8P17','entryA2ignoredbychannel'],RAM_RET_A0_definition=44,RAM_frame_bytes=16,
  channel_paths=paths,channel_reply_definitions=reply,channel_scalars=scalar,reset_A0_read_or_write=False,reset_nonzero_descriptor_ORstores_notexcluded=True,
  setup_RET_A0_reaching_RAM_calls=[0x358,0x5a6],conditional_normal_return_reply='last channel full U32[initialcapturedH+12] sampled after its R0 writes; reset leaves A0 unchanged',
  required_premises=['matching candidate/startupmapping and immutablecode','all nestedaccesses/normalreturns incl polls','callee_savedregister/frame preservation and no adverse aliasing','no interveningcode/IRQ/trap changes to proved GPR/frame flow'],
  actualinstalledbinding_MMIO_completion_pointeridentity_fullownership_polltermination_proved=False)


def domains():
 counts=[0]*4;cases=0
 for mode in range(256):
  kind=1 if mode==1 else 3 if mode==3 else 2 if mode&2 else 0;counts[kind]+=1
  A,B=((16,476),(8,404),(128,1820),(32,1304))[kind]
  for length in range(256):
   for s in (0,1,127,255):
    expr=(2*(s+158+8*(length+10)),2*(s+158+4*(length+11)),2*(s+190+8*(8*(length+2)+74)),2*(s+190+2*(8*(length+2)+215)))[kind]
    check(expr==A*length+2*s+B and 404<=expr<=34970,'setupservices byteargs durationfamily');cases+=1
 check(counts==[127,1,127,1],'setupservices actualbyte-modepartition')
 return dict(byte_mode_partition=counts,mode_header_s10_boundary_cases=cases,byte_args_do_not_prove_buffer_capacity_or_physical_duration=True,closed_host_scalar_identities_only=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs=service_bodies(data,mem,index)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,joins=joined(data,index,bs),new_original_byte_coverage=0,reused_service_bytes=728,reused_service_instructions=273)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-setup-services-original-static-join-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),reused_complete_service_bytes=1456,reused_complete_service_instructions=546,new_original_byte_coverage=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['actualinstalledprovider/startup/registrationorder andtableconsumer invocation','P76/P168 bufferallocation/capacity/nonaliasing/fullconsumption-release','T100/contextbitwriters/pollprogress/IRQordering andphysicalMMIO/FENCE.I effects'])


def tests(carriers):
 total=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);_,n,loads=guard(raw,part,i);pc=STARTS[i][k]
   for a,d in n.items():
    o,z=a-pc,d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:guard(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('setupservices instructionmutation escaped')
    total+=1
   for o in loads:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:guard(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('setupservices typedmutation escaped')
    typed+=1
 check((total,typed)==(546,40),'setupservices all546instruction40typedmutations')
 print(f'PASS:{total} instruction/{typed} typed-load mutations rejected;complete reusedservices')
 return typed


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();ledger['typed_mutation_count']=tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'setupservices exactledger')
 print('PASS:1456B/546i reusedcomplete services;setup zero-mode/registrar/channel/reset/normalRET joins;strictHEX/exactledger')
 print('PASS:NO target execution/emulation;installedbinding/polltermination/physicaleffects/fullownership UNPROVED')


if __name__=='__main__':main()
