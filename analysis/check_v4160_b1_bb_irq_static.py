"""Offline complete BB IRQ handler, JT1 publication and conditional clock join.
Original instruction/CFG/frame/def-use and closed host scalar proofs only.
No target execution/emulation, mutable target/IRQ/provider model or hardware.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_dispatch_sources_static as previous
init,sparse,check=previous.init,previous.sparse,previous.check
FIELDS={**previous.FIELDS,'mret':()}
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-bb-irq-static.json')
STARTS=(0x2000251c,0x20002568)
SOURCES=(0x4278c,0x42818)
SIZE=244
COUNT=91
HASHES=('cf352c99db6874cad72f119877d237369da50ebe36744f8357e70dba1d495a80', 'bd976e26e9884c0c8823d2ff5199454e457921cd98ea75614b8c36d8721dd3b3')
LITERALS="""
000 lui 13 536883200
004 load 14 13 1288 4
008 addi 2 2 -16
00a store 2 18 0 4
00c load 15 14 56 4
00e store 2 1 12 4
010 store 2 8 8 4
012 srli 15 15 6
014 store 2 9 4 4
016 andi 15 15 1
018 mv 18 13
01a beqz 15 150
01c addi 15 0 96
020 lui 8 536883200
024 store 14 15 56 4
026 load 15 8 1300 1
02a addi 9 8 1300
02e andi 15 15 64
032 beqz 15 76
034 lui 15 536883200
038 load 15 15 480 4
03c call_indirect 1 15
03e store 9 10 28 4
040 load 15 8 1300 1
044 andi 15 15 191
048 store 8 15 1300 1
04c load 15 8 1300 1
050 andi 15 15 32
054 beqz 15 116
056 load 15 8 1300 1
05a lui 14 536883200
05e load 14 14 1340 4
062 andi 15 15 223
066 store 8 15 1300 1
06a load 15 9 20 4
06c lui 13 32768
06e store 14 13 8 4
070 slli 15 15 1
072 store 14 15 108 4
074 load 15 9 4 1
076 andi 15 15 64
07a bnez 15 150
07c li 15 1
07e store 9 15 5 1
080 lui 15 536883200
084 load 15 15 1340 4
088 lui 14 8192
08a store 15 14 8 4
08c addi 14 0 -64
090 store 9 14 4 1
092 load 14 9 16 4
094 store 15 14 100 4
096 load 14 18 1288 4
09a load 15 14 56 4
09c srli 15 15 4
09e andi 15 15 1
0a0 beqz 15 178
0a2 li 15 16
0a4 store 14 15 56 4
0a6 lui 15 536883200
0aa addi 15 15 1300
0ae li 13 1
0b0 store 15 13 4 1
0b2 load 15 14 56 4
0b4 srli 15 15 7
0b6 andi 15 15 1
0b8 beqz 15 204
0ba addi 15 0 128
0be store 14 15 56 4
0c0 lui 15 536883200
0c4 addi 15 15 1300
0c8 li 14 1
0ca store 15 14 4 1
0cc lui 15 536883200
0d0 load 15 15 1284 4
0d4 load 14 15 4 4
0d6 srli 14 14 1
0d8 andi 14 14 1
0da beqz 14 232
0dc load 14 15 4 4
0de andi 14 14 -3
0e0 store 15 14 4 4
0e2 load 14 15 4 4
0e4 andi 14 14 -2
0e6 store 15 14 4 4
0e8 load 1 2 12 4
0ea load 8 2 8 4
0ec load 9 2 4 4
0ee load 18 2 0 4
0f0 addi 2 2 16
0f2 jr 1
"""
PATCHES={4: ('load', [14, 13, 1368, 4]), 38: ('load', [15, 8, 1380, 1]), 42: ('addi', [9, 8, 1380]), 56: ('load', [15, 15, 560, 4]), 64: ('load', [15, 8, 1380, 1]), 72: ('store', [8, 15, 1380, 1]), 76: ('load', [15, 8, 1380, 1]), 86: ('load', [15, 8, 1380, 1]), 94: ('load', [14, 14, 1420, 4]), 102: ('store', [8, 15, 1380, 1]), 132: ('load', [15, 15, 1420, 4]), 150: ('load', [14, 18, 1368, 4]), 170: ('addi', [15, 15, 1380]), 196: ('addi', [15, 15, 1380]), 208: ('load', [15, 15, 1364, 4])}
TYPED=[(4, 2), (38, 4), (56, 2), (64, 4), (76, 4), (86, 4), (94, 2), (132, 2), (150, 2), (208, 2)]
QK=[(116, 'dc20', 'qk.c.lbu'), (126, 'dcb0', 'qk.c.sb'), (144, 'd8a0', 'qk.c.sb'), (176, 'd4a3', 'qk.c.sb'), (202, 'd8a3', 'qk.c.sb')]
STORES=[(10, 2, 18, 0, 4), (14, 2, 1, 12, 4), (16, 2, 8, 8, 4), (20, 2, 9, 4, 4), (36, 14, 15, 56, 4), (62, 9, 10, 28, 4), (72, 8, 15, 1300, 1), (102, 8, 15, 1300, 1), (110, 14, 13, 8, 4), (114, 14, 15, 108, 4), (126, 9, 15, 5, 1), (138, 15, 14, 8, 4), (144, 9, 14, 4, 1), (148, 15, 14, 100, 4), (164, 14, 15, 56, 4), (176, 15, 13, 4, 1), (190, 14, 15, 56, 4), (202, 15, 14, 4, 1), (224, 15, 14, 4, 4), (230, 15, 14, 4, 4)]
SHIM_HASH='f7a24c86bf0be9fc86c0c96ee6947f62ee99e3e99f8f703419047c350557611e'


def decode(raw,pc):
 n={};o=0
 while o<len(raw):
  z=4 if int.from_bytes(raw[o:o+2],'little')&3==3 else 2;chunk=raw[o:o+z];check(len(chunk)==z,'BB completeinstruction')
  if chunk==bytes.fromhex('73002030'):d=dict(pc=pc+o,bytes=chunk.hex(),size=4,op='mret')
  else:d=previous.decode(chunk,pc+o)[pc+o]
  n[pc+o]=d;o+=z
 return n


def guard(raw,index):
 pc=STARTS[index];n=decode(raw,pc);spec={}
 for row in LITERALS.splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES:op,v=PATCHES[o]
  check(len(v)==len(FIELDS[op]),'BB literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'BB completeboundaries')
 for a,f in spec.items():init.g(n,a,'BB '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNT,HASHES[index]),'BB completeidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'BB typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'BB QK exactwidth/sign')
 return n


def body(raw,index):
 pc=STARTS[index];n=guard(raw,index);e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  elif op=='jr':check(d['rs1']==1,'BB RET throughRA');q=[];rets.append(a-pc)
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'BB soleclock linkedcall');calls.append(a-pc)
  check(op not in ('ecall','mret','csr','jal','jalr','jump') and all(z in n for z in q),'BB closednormalentry CFG');e[a]=q
 check(calls==[0x3c] and rets==[0xf2],'BB exactcall/RET census')
 active=set();seen=set()
 def visit(a):
  check(a not in active,'BB localCFGacyclic')
  if a in seen:return
  active.add(a)
  for z in e[a]:visit(z)
  active.remove(a);seen.add(a)
 visit(pc);check(seen==set(n),'BB allnodesreachable fromnormalentry')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==[(o,b,r,v+80*index if o in (0x48,0x66) else v,w) for o,b,r,v,w in STORES],'BB all20stores')
 check(not any(d.get('rd') in (3,10,11) for d in n.values()),'BB no localGP/A0/A1 definitions')
 return dict(start=pc,source=SOURCES[index],bytes=len(raw),sha256=HASHES[index],instructions=list(n.values()),CFG=e,linked_call_offsets=calls,returns=rets,stores=stores,complete_normal_entry_body=True,unrelated_entries_after_local_RET_not_claimed=True,local_CFG_acyclic=True,actual_interrupt_arrival_or_callee_completion_proved=False)


def certificates(b):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};pred={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].append(a)
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,pc+0xf2)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'BB alledgewitness');walks.append([v-pc for v in p])
 def count(a,blocked=()):
  cache={}
  def f(a):
   if a in blocked:return 0
   if a not in cache:cache[a]=1 if not e[a] else sum(f(z) for z in e[a])
   return cache[a]
  return f(a)
 def last_before(a):
  todo=pred[a][:];seen=set();defs=set();entry=(a==pc)
  while todo:
   a=todo.pop();d=n[a-pc]
   if d.get('rd')==10 or d['op']=='call_indirect':defs.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(pred[a])
  return defs,entry
 check((len(walks),count(pc))==(97,72),'BB exactedge/pathcensus')
 check(last_before(pc+0x3c)==(set(),True) and last_before(pc+0x3e)==({0x3c},False) and last_before(pc+0xf2)==({0x3c},True),'BB ambientclockarg/replycapture/RET defuse')
 check([(o,d['imm']) for o,d in n.items() if d.get('rd')==2]==[(8,-16),(0xf0,16)],'BB exactframeSPdefinitions')
 saves={(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2};loads={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}
 check(saves==loads=={(18,0),(9,4),(8,8),(1,12)},'BB fourexactframepairs')
 for o,d in n.items():
  if d['op'] in ('load','store') and d['rs1']==2:check(count(pc,blocked=[pc+8])==0 and path(pc+0xf0,pc+o) is None,'BB allocationdominatesaccess/no postdeallocframeaccess')
 check(count(pc,blocked=[pc+0xf0])==0,'BB deallocdominatesRET')
 # S1 is assigned only on the initial bit6 arm; all its body dereferences
 # precede the epilogue restore and require that definition on local paths.
 check([o for o,d in n.items() if d.get('rd')==9]==[0x2a,0xec],'BB S1 definitioncensus')
 for o,d in n.items():
  if d['op'] in ('load','store') and d['rs1']==9:
   check(path(pc,pc+o) is not None,'BB S1 coveredaccess')
   # Remove the S1 definition and check reachability of this access.
   seen=set();todo=[pc]
   while todo:
    a=todo.pop()
    if a==pc+0x2a or a in seen:continue
    seen.add(a);todo.extend(e[a])
   check(pc+o not in seen,'BB Hformation dominatesS1dereference')
 check(n[4]['imm']==n[0x96]['imm'] and n[0x1a]['target']==pc+0x96 and n[0x24]['imm']==56 and n[0x1c]['imm']==96,'BB initialbit6 gates heldR0 literal96')
 check(n[0x2e]['imm']==64 and n[0x44]['imm']==191 and n[0x50]['imm']==32 and n[0x62]['imm']==223,'BB freshH0flagbits')
 check(n[0x6c]['imm']==32768 and n[0x70]['imm']==1 and n[0x72]['imm']==108 and n[0x88]['imm']==8192 and n[0x8c]['imm']==-64,'BB literalTstores andcontextbyte192')
 check(n[0xa2]['imm']==16 and n[0xba]['imm']==128 and n[0xb2]['rs1']==14 and n[0x9a]['rs1']==14,'BB freshsameR1statussamples notcombined')
 check(n[0xd0]['imm']!=n[4]['imm'] and n[0xde]['imm']==-3 and n[0xe4]['imm']==-2 and n[0xdc]['imm']==n[0xe2]['imm']==4,'BB distinctK/2freshRMWloads')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),syntactic_DAG_paths=count(pc),frame_bytes=16,saved_register_offsets=sorted(saves),clock_A0='ambient entry A0;no local normalization',normal_RET_A0='ambient entry A0 if no clock call,else opaque clock reply',S1_H_formation_dominates_all_body_uses=True,normal_frame_restore_only_under_valid_frames_and_callee_preservation=True,walks_are_not_target_traces=True,physical_MMIO_W1C_timing_or_interrupt_ABI_proved=False)


def shim(raw):
 pc=0x1873e;n=decode(raw,pc);spec={0:dict(op='lui',rd=15,imm=0x20000000),4:dict(op='load',rd=15,rs1=15,imm=4,width=4),6:dict(op='call_indirect',rd=1,rs1=15),8:dict(op='mret')}
 check(n.keys()=={pc+o for o in spec},'BB APPshim boundaries')
 for o,f in spec.items():init.g(n,pc+o,'BB APPshim '+hex(o),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(12,4,SHIM_HASH),'BB APPshim identity')
 check(not any(d.get('rd') in (2,3,10,11) for d in n.values()),'BB APPshim noframe/GP/A0/A1shaping')
 return dict(start=pc,bytes=12,sha256=SHIM_HASH,instructions=list(n.values()),call_target='fresh U32[20000004] & ~1',link=0x18746,postcall_exit='MRET with no local A0 read/restore',ordinary_RET_or_hardware_interrupt_ABI_claim=False)


def reused_joins(image,data,mem,index,b):
 import check_v4160_dispatch_origin_mask_static as origin
 import check_v4160_radio_config_chain_static as radio
 import check_v4160_service_provider_link_static as provider
 import check_v4160_config_gates_static as config
 def take(pc,z):
  raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'BB reusedstrictHEX');return raw
 jt1,jt2,_=origin.DETAILS[index];detail=origin.init.DETAILS[index];ip=detail[0];ib=origin.initializer_body(take(ip,114),ip,detail,jt1,jt2)
 word=ib['JT_words'][1];check(word['address']=='0x20000004' and int(word['value'],16)==b['start'] and ib['pointer_publication_precedes_code_copy'],'BB exactJT1publisher/earlypublication')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];dst=int(fc['destination'],16);src=int(fc['source'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(dst<=b['start'] and b['start']+244<=end and src+b['start']-dst==b['source'],'BB fullfirstcopy mapping')
 pp=radio.DETAILS[index][0][0];rb=radio.body(take(pp,118),'parent',index);rn={d['pc']-pp:d for d in rb['instructions']};G=0x20003000;delta=80*index
 check(rn[16]['imm']+rn[20]['imm']==0x40024300 and rn[28]['imm']==1284+delta and rn[32]['imm']==512 and rn[40]['imm']==1340+delta and rn[56]['imm']==256 and rn[66]['imm']==1288+delta,'BB matchingradio K/T/R sourceconstants')
 check(all(int(c['pc'],16)>pp+66 for c in rb['calls']),'BB pointerstores before radiofirstlinkedcall')
 # Read-only APP clock source and explicit configuration publication. The
 # mutable copy/binding and whether these events actually happen stay unproved.
 reader=provider.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,provider.APP_HASHES[1])
 ac=provider.body(image[0x19bba-0x8000:0x19bce-0x8000],'APP_call',0x19bba,provider.APP_HASHES[0]);an={d['pc']:d for d in ac['instructions']}
 check((0x19bba+an[0x19bba]['imm']+an[0x19bbe]['imm'])&0xffffffff==0x191c6,'BB APPconfig readerliteral')
 rp,rz,*_=config.DETAILS[index];cb=config.body(take(rp,rz),index);check(int(cb['service_word'],16)==G+480+delta and init.binding.word(data,0x40074)==rp,'BB freshclockslot/sourceconfigentry')
 nn={d['pc']:d for d in reader['instructions']};check(not reader['calls'] and not any(d['op']=='store' or d.get('rd') in (1,2,3,8,9,*range(18,28)) for d in nn.values()),'BB matchingAPPreader noframe/stores/Sregescape')
 first_A0=min(a for a,d in nn.items() if d.get('rd')==10)
 check(first_A0==0x191c6+48 and nn[first_A0]['op']=='load' and not any(d.get('rs1')==10 or d.get('rs2')==10 for a,d in nn.items() if a<first_A0),'BB reader overwritesambientA0 before firstinputuse')
 return dict(initializer=dict(start=ip,bytes=114,sha256=ib['sha256'],JT1_word=word,first_copy_transfer_pc=ib['first_copy_transfer_pc'],code_ready_at_publication_proved=False),first_copy=fc,first_copy_end_exclusive=mapping['first_copy_end_exclusive'],
  reused_radio_parent=dict(start=pp,bytes=118,sha256=rb['sha256'],R_slot=G+1288+delta,R_nominal_value=0x40024100,T_slot=G+1340+delta,T_nominal_value=0x40024200,K_slot=G+1284+delta,K_nominal_value=0x40024300),
  conditional_clock=dict(slot=G+480+delta,APP_reader=dict(start=0x191c6,bytes=90,sha256=reader['sha256'],calls=0,stores=0,entry_A0_not_published_or_retained_locally=True,read_retry_termination_proved=False),APP_config_prefix=dict(start=0x19bba,bytes=20,sha256=ac['sha256']),candidate_config=dict(start=rp,bytes=rz,sha256=cb['sha256']),full_copy_binding_ordering_and_noninterference_required=True),
  actual_loaded_code_or_pointer_stability_physical_register_effects_and_complete_interrupt_frame_lifetime_proved=False)


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,SOURCES[index],244);check(sparse.captured(mem,SOURCES[index],244)==raw,'BB completebodystrictHEX');b=body(raw,index)
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificate=certificates(b),source_joins=reused_joins(image,data,mem,index,b),
  contracts=['R0=freshG1288/1368;R0+56 bit6 ->W32[R0+56]=96 thenH=G1300/1380 actions;else skiptofreshR1 phase',
   'freshH0bit6 ->freshclockG480/560(ambientA0,A1),storeopaqueA0 toH28,freshH0 AND191 store;no call nullguard. Independently freshH0bit5 ->anotherfreshbyte AND223 thenT0=freshG1340/1420,T0+8=32768,T0+108=low32(H20<<1)',
   'freshH4bit6 clear ->H5=1,T1=freshG1340/1420,T1+8=8192,H4=192,T1+100=freshH16. InitialR0bit6 gates this entireHactionregion',
   'freshR1=G1288/1368;freshR1+56bit4 ->literal16store andH4=1;freshsameR1+56bit7 ->literal128store andH4=1. PriorR0/R1 identity orcoherentsamples notassumed',
   'freshK=G1284/1364;freshK4bit1 set ->freshK4 AND-3 store,thenfreshK4 AND-2 store. These aretwo separateRMWs,not atomic clearingbothbits',
   'matchingAPPreader191c6 hasno stores/calls/frame orSregwrites anddoesnotretainambientA0 locally;its hardware read-retry loops maynotfinish. Genericfreshclocktarget remainsunknown absentinstalledbinding',
   'BB normalRET onlyafter restoring16Bframe. APPshim ignores scalarreply beforeMRET butdoesnotlocallyrestoreA0;hardware/shadowbank/IRQABI and interruptedstatepreservation unproved. No directJT120 call inthisbody;opaqueclocktransitivebehaviour notexcluded'],
  full_interrupt_scheduling_provider_binding_and_pointer_lifetimes_proved=False)


def domains():
 for byte in range(256):
  check((byte&191)==(byte&~64) and (byte&223)==(byte&~32),'BB byte flag masks')
  check(0<=byte&64<=64 and (192&64)==64 and (192&32)==0,'BB context192 literal bits')
 for word in range(65536):
  check(((word&~2)&~1)==(word&~3),'BB stable-sample twoRMW scalaridentity')
  check(((word<<1)&0xffffffff)==word*2,'BB low16 sample shiftidentity')
 return dict(all_U8_flag_cases=256,stable_word_low16_cases=65536,actual_two_fresh_reads_may_differ=True,low32_shift_formula='low32(U32H20 <<1);not a bound on actualsource',stable_scalar_identity_not_atomic_MMIO_effect=True,closed_host_scalar_identities_only=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes);sh=shim(image[0x1873e-0x8000:0x1874a-0x8000]);v=image[0x8134-0x8000:0x8138-0x8000];check(int.from_bytes(v,'little')==sh['start'],'BB exactAPPvector8134')
 return dict(schema='TSL9-complete-BB-IRQ-normal-entry-and-JT1-clock-source-static-v1',APP_sha256=sha256(image).hexdigest(),APP_vector=dict(address=0x8134,bytes=v.hex(),target=sh['start']),APP_shim=sh,profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_candidate_complete_body_bytes=488,new_candidate_complete_body_instructions=182,APP_shim_verified_bytes=12,APP_shim_verified_instructions=4,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['actual RAMJT1 installedcode and publication/copy/IRQordering','generic clock binding and physicalreadloop progress','other context/registerpointer writers,aliasing/reentry andhardwareABI','JT120 actualcallers andfullnode/callback consumption-release lifetimes'])


def tests(image,carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],244);n=guard(raw,i)
  for d in n.values():
   o=d['pc']-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('BB instructionmutation escaped')
   mutated+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('BB typedmutation escaped')
   typed+=1
 raw=image[0x1873e-0x8000:0x1874a-0x8000]
 for d in shim(raw)['instructions']:
  o=d['pc']-0x1873e;bad=bytearray(raw);bad[o]^=4
  try:shim(bad)
  except RuntimeError:pass
  else:raise RuntimeError('BB shim mutation escaped')
  mutated+=1
 check((mutated,typed)==(186,20),'BB mutationcensus')
 print('PASS:186 instruction/20 typed-load mutations rejected;complete BB handlers+APPshim')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'BB exactledger replay')
 print('PASS:488B/182i BB complete bodies+12B/4i APPshim;strictHEX/runtimePC/JT1/clock joins;exactledger')
 print('PASS:NO target execution/emulation;actualIRQordering/installedbinding/hardwareABI/full lifetimes UNPROVED')


if __name__=='__main__':main()
