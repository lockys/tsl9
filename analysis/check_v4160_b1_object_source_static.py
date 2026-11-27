"""Offline B88 -> B100 object provenance and complete postpublication service.
Original operands/immutable CFG/frame/def-use and host scalar identities only.
No target execution/emulation, mutable memory/provider/callback/IRQ model.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_b1_setup_event_static as previous
import check_v4160_list_origin_static as origin
import check_v4160_list_direct_callbacks_static as direct
init,sparse,check=previous.init,previous.sparse,previous.check
decode=previous.previous.decode
OUT=Path(__file__).with_name('v4160-b1-object-source-static.json')
STARTS=(0x43edc,0x43f68)
HASHES=('e8f5b85ed22445c9a799760de1e3a007ae4c4c319f90340529d9362cd74b7d73','8a0492d7dec2d40cff8320828979124193d58e898aa5be51dbf7c33b2dbc4133')
FIELDS={**previous.callback.FIELDS,'sub':('rd','rs1','rs2')}
BRANCHES={'beqz','bgeu','bge'}
LITERALS='''
000 lui 15 536883200
004 addi 14 15 492
008 load 14 14 44 4
00a beqz 14 104
00c addi 2 2 -16
00e store 2 8 8 4
010 store 2 9 4 4
012 store 2 18 0 4
014 store 2 1 12 4
016 addi 18 15 492
01a call_indirect 1 14
01c lui 15 536883200
020 addi 14 15 412
024 load 14 14 8 2
026 mv 8 10
028 addi 9 15 412
02c beqz 14 92
02e mv 15 14
030 bgeu 14 10 54
034 mv 15 10
036 slli 15 15 16
038 srli 15 15 16
03a mv 13 14
03c bgeu 8 14 66
040 mv 13 8
042 slli 13 13 16
044 srli 13 13 16
046 sub 15 15 13
048 li 14 20
04a bge 14 15 92
04e load 15 18 48 4
052 beqz 15 86
054 call_indirect 1 15
056 jal 1 410032
05a store 9 8 8 2
05c load 1 2 12 4
05e load 8 2 8 4
060 load 9 2 4 4
062 load 18 2 0 4
064 addi 2 2 16
066 jr 1
068 jr 1
'''


def guard(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s={}
 for row in LITERALS.splitlines():
  if not row:continue
  off,op,*args=row.split();o=int(off,16);v=list(map(int,args));check(len(v)==len(FIELDS[op]),'objectsource literalfields');d=dict(zip(FIELDS[op],v));d['op']=op
  if index and o in (4,0x16,0x20,0x28):d['imm']+=80
  if index and o==0x56:d['target']+=234
  if op in BRANCHES:d['target']+=pc
  s[pc+o]=d
 check(n.keys()==s.keys(),'objectsource completeboundaries')
 for a,d in s.items():init.g(n,a,'objectsource '+hex(a-pc),**d)
 check(raw[0x24:0x26].hex()=='1a27' and n[pc+0x24].get('mnemonic')=='qk.c.lhu','objectsource QK LHU notFP')
 check(raw[0x5a:0x5c].hex()=='82a4' and n[pc+0x5a].get('mnemonic')=='qk.c.sh','objectsource QK SH savedreply')
 check(int.from_bytes(raw[0x4e:0x52],'little')&0x707f==0x2003,'objectsource typedwordload')
 check((len(raw),len(n),sha256(raw).hexdigest())==(106,42,HASHES[index]),'objectsource fullidentity')
 return n


def body(raw,index):
 pc=STARTS[index];n=guard(raw,index);e={};calls=[]
 for a,d in n.items():
  q=[a+d['size']];op=d['op']
  if op in BRANCHES:q.append(d['target'])
  elif op=='jr':check(d['rs1']==1,'objectsource RET RA');q=[]
  elif op in ('jal','call_indirect'):calls.append(dict(offset=a-pc,target=d['target'] if op=='jal' else 'capturedA4' if d['rs1']==14 else 'freshA5'))
  check(all(z in n for z in q),'objectsource completeCFG');e[a]=q
 check(calls==[dict(offset=0x1a,target='capturedA4'),dict(offset=0x54,target='freshA5'),dict(offset=0x56,target=0x641b0+234*index)],'objectsource exactcalls')
 def paths(a):
  check(a not in active,'objectsource DAG');active.add(a)
  out=[[a]] if not e[a] else [[a]+q for z in e[a] for q in paths(z)];active.remove(a);return out
 active=set();walks=paths(pc);check(len(walks)==14 and set().union(*map(set,walks))==set(n),'objectsource all14syntacticpaths/42nodes')
 for w in walks:
  offsets=[a-pc for a in w];framed=0xc in offsets
  check((offsets[-1]==0x66)==framed and (0x64 in offsets)==framed,'objectsource disjointframed/framelessRET')
  check((0x5a in offsets)==(0x56 in offsets) and (0x5a not in offsets or offsets.index(0x56)<offsets.index(0x5a)),'objectsource storeafterrequiredlinkedcall')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==[(0xe,2,8,8,4),(0x10,2,9,4,4),(0x12,2,18,0,4),(0x14,2,1,12,4),(0x5a,9,8,8,2)],'objectsource exactfourframe/onefixedhalfwordstores')
 check([(a-pc,d['imm']) for a,d in n.items() if d.get('rd')==2]==[(0xc,-16),(0x64,16)],'objectsource balancedSP')
 check(sorted((d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2)==[(1,12),(8,8),(9,4),(18,0)],'objectsource allsavedrestored')
 b=dict(start=pc,bytes=106,sha256=HASHES[index],instructions=list(n.values()),CFG=e)
 for o,r,h in ((0x5a,8,{0x26}),(0x5a,9,{0x28}),(0x4e,18,{0x16})):
  check(previous.reaching(b,o,r,False)==(h,False),'objectsource capturedregisterdefuse')
 check(previous.reaching(b,0x1a,10)==(set(),True),'objectsource firstprovider receivesinheritedA0 notforcedzero')
 for o in (0x30,0x3c):check(previous.reaching(b,o,10)==({0x1a},False),'objectsource comparisonsusefullfirstreply')
 return dict(**b,calls=calls,stores=stores,syntactic_normalreturn_paths=[[a-pc for a in w] for w in walks],frame_bytes_on_nonnullprovider=16,
  contracts=['providerSlot=G+536/616;capturednonnullword calledwithoutnewA0;nullprovider ->framelessRET retainsentryA0',
   'L=freshU16[M8] sampledafterprovider;X=fullproviderA0 savedS0;M=G412/492',
   'Lzero skipsalllatercalls/store. OtherwiseD=low16(maxU32(X,L))-low16(minU32(X,L)),signedrange-65535..65535;D>20 admitsservices',
   'freshU32[G540/620] optionalhook thenrequiredlinked641b0/6429a;low16(savedX) storedM8 onlyafterbothrequiredreturns',
   'no explicitB88/B100 store;unknowncallee effects/retention remain. ReturnA0entry ifnullprovider,firstreply ifskipservices,RFcallee reply ifservices;notfixedstatus'],
  actualbinding_sideeffects_pollreturn_fullpointerpreservation_proved=False)


def compact(b,guardname):
 return {**{k:v for k,v in b.items() if k!='instructions'},'instruction_count':len(b['instructions']),'complete_guard':guardname}


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,106);check(sparse.captured(mem,pc,106)==raw,'objectsource newbody fullstrictHEX');new=body(raw,index);B=0x200033b8+80*index
 reused={};original={}
 for part,src,z,fn,gn in [('creator',origin.STARTS[index][1],194,lambda r:origin.body(r,'creator',index),'check_v4160_list_origin_static.py'),('bit0',direct.STARTS[index][0],666+8*index,lambda r:direct.body(r,'bit0',index),'check_v4160_list_direct_callbacks_static.py'),('bit1',direct.STARTS[index][1],60,lambda r:direct.body(r,'bit1',index),'check_v4160_list_direct_callbacks_static.py')]:
  r=init.binding.take(data,src,z);check(sparse.captured(mem,src,z)==r,'objectsource reusedfullbodystrictHEX');b=fn(r);original[part]={d['pc']-src:d for d in b['instructions']};reused[part]=compact(b,gn)
 c,a,b=(original[p] for p in ('creator','bit0','bit1'));ap=direct.STARTS[index][0]
 check(c[98]['op']=='store' and c[98]['rs2']==8 and c[98]['rs1']==9 and c[98]['imm']==88 and c[96]['target']==origin.STARTS[index][1]+176,'objectsource creatorheadnull B88publication')
 check(not any(d['op']=='store' and d['rs1']==9 and d['imm']==88 for o,d in c.items() if o>=176),'objectsource appenddoesnotpublishB88')
 check(c[64]['op']=='mv' and c[64]['rs2']==10 and c[82]['rd']==1,'objectsource creatorallocatorN acrossfill conditionalS0preservation')
 check(not any(d['op']=='store' and d['rs1']==8 and d['imm']<=12<d['imm']+d['width'] for d in c.values()),'objectsource creatorexplicitNstoresexcludeN12')
 check(a[14]['imm']==88 and a[14]['rd']==8 and a[20]['op']=='beq' and a[28]['op']=='bne' and a[24]['imm']==12 and a[24]['width']==1 and a[26]['imm']==1,'objectsource bit0Nnonnull/N12onegate')
 check(a[112]['op']=='store' and (a[112]['rs1'],a[112]['rs2'],a[112]['imm'],a[112]['width'])==(18,8,100,4),'objectsource capturedNtoB100')
 ab=dict(start=ap,CFG={int(k,16):[int(z,16) for z in qs] for k,qs in reused['bit0']['conditional_CFG'].items()},instructions=list(a.values()))
 # Reaching utility uses absolute instruction PCs, retained in the reused rows.
 check(previous.reaching(ab,112,8,False)==({14},False) and previous.reaching(ab,112,18,False)==({102},False),'objectsource exactheldN/B definitionatpublication')
 check(a[124]['target']==pc and a[128]['op']=='store' and a[128]['rs2']==0 and a[128]['imm']==952+80*index,'objectsource postpublicationservice beforeB0clear')
 check(previous.reaching(ab,124,10)==(set(),True),'objectsource postservice firstprovider inheritsbit0entryA0')
 check(b[12]['imm']==100 and b[12]['width']==4 and b[18]['imm']==12 and b[20]['target']==direct.STARTS[index][1]+52,'objectsource bit1freshB100/N12gate')
 hook=previous.callback;hr=init.binding.take(data,hook.STARTS[index],hook.SIZES[index]);tr=init.binding.take(data,hook.TABLES[index],52);check(sparse.captured(mem,hook.STARTS[index],len(hr))==hr and sparse.captured(mem,hook.TABLES[index],52)==tr,'objectsource hookreader fullstrictHEX');hb=hook.body(hr,tr,index);hn={d['pc']-hook.STARTS[index]:d for d in hb['instructions']};check(hn[0xe]['imm']==100 and hn[0xe]['rd']==8,'objectsource eventhook samefreshB100source')
 fixedstore=0x20003000+412+80*index+8
 for slot in (B+88,B+100):check(fixedstore+2<=slot or slot+4<=fixedstore,'objectsource solefixedhalfwordstore disjointB88/B100')
 return dict(label=init.binding.PROFILES[index][0],B=B,slots=dict(B88=B+88,B100=B+100),new_postpublication_service=new,reused_bodies=reused,
  eventhook_reader=dict(start=hook.STARTS[index],bytes=hook.SIZES[index],sha256=hb['sha256'],load_offset=0xe,Nsource=B+100,complete_guard='check_v4160_callback_dispatch_static.py'),
  provenance=['creatornonzeroallocationreplyN ->matchingfill returns ->freshheadzero ->B88=N beforedefaults',
   'laterbit0freshB88;nonnull/N12one andthreefreshglobalgates admit B100=heldN beforepostpublicationcall',
   'latereventhook andbit1 separatelyfreshloadB100;actualequalityneedspublicationorder,slotstability andretainedvalidN'],
  zero_fill_gap='Ifmatchingfillzeroes192B andN12unchanged,creatorexplicitstoresleaveN12=0,so bit0N12==1 gatefails;otherwriter/order required',
  actualsetupPidentity_allwriters_eventorder_nodevalidity_retention_completeownership_proved=False)


def domains():
 cases=0
 for L in range(65536):
  for X in (0,1,20,21,65535,65536,65556,0x10064,0xffffffff):
   hi=max(X,L)&65535;lo=min(X,L)&65535;D=hi-lo
   check(-65535<=D<=65535,'objectsource signedlow16diff range')
   if X<=65535:check(D==abs(X-L),'objectsource boundedreply actualabsolute difference')
   cases+=1
 check(((max(65536,100)&65535)-(min(65536,100)&65535))==-100,'objectsource highwordcounterexample notlow16abs')
 check(((max(65557,1)&65535)-(min(65557,1)&65535))==20,'objectsource >20strictboundary highwordreply')
 return dict(U16L_and_fullreply_boundary_cases=cases,fullreply_notrestrictedtoU16=True,comparison_uses_full_unsigned_order_then_truncated_subtraction=True,closed_host_scalar_identities_only=True,no_targetstate_model=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-object-source-postpublication-service-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),newly_guarded_candidate_bytes=212,newly_guarded_candidate_instructions=84,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,target_network=False,remaining=['providerG536/616 andoptionalhookG540/620 bindings/effects','B88/B100allwriters andN12onewriter/actualeventorder','allocationvalidity/sourceidentity/nonalias/retainedN/notificationlifetimes','full641b0/6429a returns underactualstate/IRQ/pollprogress'])


def tests(carriers):
 total=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],106);n=guard(raw,i)
  for d in n.values():
   o,z=d['pc']-STARTS[i],d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('objectsource instructionmutation escaped')
   total+=1
  bad=bytearray(raw);bad[0x4f]^=0x40
  try:guard(bad,i)
  except RuntimeError:pass
  else:raise RuntimeError('objectsource typedmutation escaped')
  typed+=1
 check((total,typed)==(84,2),'objectsource mutationcensus');print('PASS:84 instruction/2 typed-load mutations rejected;212B complete new candidate service')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APPidentity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDKidentity');carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidateidentity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'objectsource exactledger')
 print('PASS:B88->B100->independentreaders;new106B/42i each;strictHEX/14paths/frame/signeddiff/exactledger')
 print('PASS:NO target execution/emulation;actualbinding/N12writer/order/retention/fullownership UNPROVED')


if __name__=='__main__':main()
