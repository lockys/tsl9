"""Offline key allocation/registry source and submission tail contracts.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable registry/heap/clock/provider/packet model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_key_submit_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-key-source-tail-static.json')
ROLES=('source','tail')
SIZES={'source':188,'tail':168}
STARTS=({'source': 358754, 'tail': 354070}, {'source': 359074, 'tail': 354390})
COUNTS={'source': 64, 'tail': 50}
HASHES=({'source': '14d55c249afdcfe89ccf1c5ab596c56c0ebbb13bc681207c1de861c2d3878e6b', 'tail': '859f5c4eb6a556cab741f2b5269de1fc747ae1964058c659a17178a4214801c9'}, {'source': '105fcebc32c94cd5c73e8a79c4794ac5a9e610d2d528bc2f0a82271f333004e5', 'tail': '4c9689d7c96505ca930e884a432b92bf115a0ea2625d0861f77f50774adbc7a1'})
LITERALS={
'source':"""
000 addi 2 2 -16
002 addi 11 0 611
006 addi 10 0 488
00a store 2 1 12 4
00c store 2 8 8 4
00e store 2 9 4 4
010 auipc 1 536510464
014 jalr 1 1 1742
018 addi 12 0 488
01c li 11 0
01e mv 8 10
020 auipc 1 536514560
024 jalr 1 1 -1510
028 li 10 0
02a beqz 8 92
02c lui 9 536883200
030 addi 15 9 952
034 load 13 15 156 4
038 addi 9 9 952
03c beqz 13 106
03e mv 14 13
040 li 15 1
042 load 12 14 8 2
044 beq 12 15 166
048 load 14 14 0 4
04a bnez 14 66
04c store 8 15 8 2
04e bnez 15 144
050 mv 10 8
052 auipc 1 536510464
056 jalr 1 1 1884
05a load 10 8 8 2
05c load 1 2 12 4
05e load 8 2 8 4
060 load 9 2 4 4
062 addi 2 2 16
064 jr 1
066 mv 14 13
068 jump 66
06a li 15 1
06c store 8 15 8 2
06e store 9 8 156 4
072 store 9 8 160 4
076 store 9 15 180 2
07a jal 1 358564
07e load 15 9 160 4
082 store 15 0 0 4
086 store 8 0 10 1
08a store 8 0 14 1
08e jump 90
090 load 15 9 160 4
094 store 15 8 0 4
096 load 15 9 180 2
09a store 9 8 160 4
09e addi 15 15 1
0a0 store 9 15 180 2
0a4 jump 126
0a6 addi 14 15 1
0aa slli 15 14 16
0ae slli 12 14 16
0b2 srli 15 15 16
0b4 bge 12 0 102
0b8 li 15 0
0ba jump 76
""",
'tail':"""
000 lui 14 536883200
004 addi 14 14 564
008 load 12 14 12 1
00a lui 15 536883200
00e lui 13 536883200
012 addi 15 15 952
016 beqz 12 82
018 load 12 13 1260 4
01c addi 2 2 -16
01e store 2 1 12 4
020 bnez 12 52
022 load 14 14 4 4
024 store 15 14 176 4
028 lui 14 536875008
02c addi 14 14 1000
030 store 13 14 1260 4
034 load 10 13 1260 4
038 store 15 0 164 4
03c jal 1 278226
040 load 1 2 12 4
042 lui 15 3758153728
046 lui 14 33554432
04a store 15 14 516 4
04e addi 2 2 16
050 jr 1
052 load 12 14 8 2
054 store 15 0 164 4
058 load 15 10 134 2
05c mv 11 10
05e store 13 0 1260 4
062 mul 15 15 12
066 lui 12 999424
06a load 13 10 144 4
06e addi 10 12 575
072 addi 12 12 576
076 add 15 15 10
078 divu 15 15 12
07c lui 12 536883200
080 load 12 12 515 1
084 add 12 12 15
086 bltu 13 12 162
08a load 14 11 140 4
08e lui 10 536875008
092 sub 12 13 12
096 addi 10 10 910
09a addi 13 11 41
09e jal 0 275476
0a2 load 15 14 4 4
0a4 add 13 13 15
0a6 jump 138
""",
}
PATCHES={'source': {20: ('jalr', [1, 1, 1422]), 36: ('jalr', [1, 1, -1830]), 48: ('addi', [15, 9, 1032]), 56: ('addi', [9, 9, 1032]), 86: ('jalr', [1, 1, 1564]), 122: ('jal', [1, 358884])}, 'tail': {4: ('addi', [14, 14, 644]), 18: ('addi', [15, 15, 1032]), 24: ('load', [12, 13, 1340, 4]), 48: ('store', [13, 14, 1340, 4]), 52: ('load', [10, 13, 1340, 4]), 60: ('jal', [1, 278366]), 94: ('store', [13, 0, 1340, 4]), 128: ('load', [12, 12, 595, 1]), 158: ('jal', [0, 275616])}}
TYPED={'source': [(52, 2), (126, 2), (144, 2), (150, 5)], 'tail': [(24, 2), (52, 2), (88, 5), (106, 2), (128, 4), (138, 2)]}
QK={'source': [(66, '1227', 'qk.c.lhu'), (76, '1ea4', 'qk.c.sh'), (90, '0a24', 'qk.c.lhu'), (108, '1ea4', 'qk.c.sh')], 'tail': [(8, '5027', 'qk.c.lbu'), (82, '1227', 'qk.c.lhu')]}
STORES={'source': [(10, 2, 1, 12, 4), (12, 2, 8, 8, 4), (14, 2, 9, 4, 4), (76, 8, 15, 8, 2), (108, 8, 15, 8, 2), (110, 9, 8, 156, 4), (114, 9, 8, 160, 4), (118, 9, 15, 180, 2), (130, 15, 0, 0, 4), (134, 8, 0, 10, 1), (138, 8, 0, 14, 1), (148, 15, 8, 0, 4), (154, 9, 8, 160, 4), (160, 9, 15, 180, 2)], 'tail': [(30, 2, 1, 12, 4), (36, 15, 14, 176, 4), (48, 13, 14, 1260, 4), (56, 15, 0, 164, 4), (74, 15, 14, 516, 4), (84, 15, 0, 164, 4), (94, 13, 0, 1260, 4)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*vals=row.split();o=int(off,16);vals=list(map(int,vals))
  if index and o in PATCHES[role]:op,vals=PATCHES[role][o]
  check(len(vals)==len(FIELDS[op]),'source-tail literalfields');f=dict(zip(FIELDS[op],vals));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'source-tail fullboundaries '+role)
 for a,f in s.items():init.g(n,a,'source-tail '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'source-tail completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'source-tail typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'source-tail exactQK')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];qs=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'source-tail RET RA');rets.append(a-pc);qs=[]
  elif op in BRANCHES:qs.append(d['target'])
  elif op=='jump':qs=[d['target']]
  elif op in ('jal','jalr'):
   target=d.get('target')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and d['rd']==d['rs1']==u['rd']==1,'source-tail linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   if d['rd']==0:check(role=='tail' and op=='jal','source-tail onlyproducer unlinkedtail');tails.append(dict(offset=a-pc,target=target,new_link=False));qs=[]
   else:check(d['rd']==1,'source-tail linkedcall');calls.append(dict(offset=a-pc,target=target))
  check(op not in ('call_indirect','csr','mret','ecall') and all(z in n for z in qs),'source-tail closedCFG');e[a]=qs
 expected={'source':[(0x14,0x20000040),(0x24,0x2000039c),(0x56,0x20000110),(0x7a,0x578a4+320*index)],'tail':[(0x3c,0x43ed2+140*index)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[0x64 if role=='source' else 0x50] and tails==([dict(offset=0x9e,target=0x43414+140*index,new_link=False)] if role=='tail' else []),'source-tail exactcalls/returns/tails')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'source-tail allreachable includingpostRET')
 common=previous.previous.previous.previous.previous.previous.previous.dispatch.common;groups=common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]]
 check(bool(cycles)==(role=='source'),'source-tail cycleclassification')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expectedstores=[tuple((*v[:3],v[3]+80*index,v[4])) if role=='tail' and v[0] in (0x30,0x5e) else v for v in STORES[role]]
 check(stores==expectedstores and len(stores)==(14 if role=='source' else 7),'source-tail allstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,cyclic_SCCs=cycles,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,actual_registry_or_provider_progress_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=[a for a,qs in e.items() if not qs]
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 def finish(a):
  ps=[p for z in ends if (p:=path(a,z)) is not None];check(bool(ps),'source-tail suffix witness');return min(ps,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'source-tail all-edge witness');walks.append([a-pc for a in p])
 points=([0x14,0x24,0x56,0x5a,0x6e,0x72,0x94,0xa0,0xa6,0xb8] if role=='source' else [0x1c,0x24,0x30,0x3c,0x4a,0x50,0x52,0x5e,0x9e,0xa2])
 selected={hex(o):[a-pc for a in path(pc,pc+o)+finish(pc+o)[1:]] for o in points}
 if role=='source':
  check(n[2]['imm']==611 and n[6]['imm']==n[0x18]['imm']==488 and n[0x1c]['imm']==0 and n[0x1e]['rs2']==10,'source-tail allocate488/fill beforeguard')
  check(b['CFG'][pc+0x24]==[pc+0x28] and n[0x2a]['rs1']==8 and n[0x2a]['target']==pc+0x5c,'source-tail heldP nullguard afterfill')
  check([o for o,d in n.items() if d.get('rd')==8]==[0x1e,0x5e] and n[0x34]['imm']==156 and n[0x34]['rd']==13,'source-tail heldP/capturedhead')
  check([o for o,d in n.items() if d.get('rd')==13]==[0x34] and n[0x66]['rs2']==13 and n[0x68]['target']==pc+0x42,'source-tail restart originalhead notfreshglobal')
  check(n[0x40]['imm']==1 and n[0xa6]['imm']==1 and n[0xaa]['imm']==n[0xae]['imm']==n[0xb2]['imm']==16 and n[0xb4]['op']=='bge' and n[0xb8]['imm']==0,'source-tail candidate0x8000 stop')
  check(n[0x4c]['imm']==n[0x6c]['imm']==n[0x5a]['imm']==8 and n[0x4c]['width']==n[0x6c]['width']==n[0x5a]['width']==2,'source-tail assigned/finalfreshID field')
  check(n[0x50]['rs2']==8 and n[0x56]['op']=='jalr' and e[pc+0x56]==[pc+0x5a],'source-tail postrelease request freshIDread')
  check(not any(d.get('rd')==10 for o,d in n.items() if 0x2a<=o<0x7a and o not in (0x50,0x5a)) and n[0x28]['imm']==0,'source-tail emptyhelper A0zero notP')
  check(n[0x6e]['imm']==156 and n[0x72]['imm']==160 and n[0x76]['imm']==180 and n[0x96]['imm']==180 and n[0x9e]['imm']==1,'source-tail head/tail/count stores')
  check(n[0x7e]['imm']==160 and n[0x82]['rs1']==15 and n[0x82]['rs2']==0 and n[0x86]['imm']==10 and n[0x8a]['imm']==14,'source-tail zero freshTail.next/P10/P14')
  info=dict(frame_bytes=16,requested_allocation_bytes=488,allocation_tag=611,head_snapshot_retained_across_scan=True,candidate_interval=[1,32767],max_candidate_increments_before_sentinel=32767,linked_list_visit_or_whole_return_bound_proved=False,post_release_request_P8_read=True,return_is_fresh_U16P8_not_pointer=True,object_explicit_extent=15)
 else:
  check(n[8]['imm']==12 and n[0x16]['target']==pc+0x52 and n[0x1c]['imm']==-16 and n[0x4e]['imm']==16,'source-tail frameonlyflagset')
  check(n[0x24]['imm']==176 and n[0x22]['imm']==4 and n[0x28]['imm']+n[0x2c]['imm']==0x200013e8 and n[0x34]['imm']==n[0x18]['imm']==n[0x30]['imm']==n[0x5e]['imm'],'source-tail slot/freshreload/literal')
  check(n[0x4a]['imm']==516 and n[0x42]['imm']+516==0xe000e204 and n[0x46]['imm']==0x02000000,'source-tail fixed numericalcontrolstore')
  check(n[0x52]['width']==n[0x58]['width']==2 and n[0x52]['imm']==8 and n[0x58]['imm']==134 and n[0x6a]['imm']==144,'source-tail two U16product/deadlineword')
  check(n[0x66]['imm']+n[0x6e]['imm']==999999 and n[0x66]['imm']+n[0x72]['imm']==1000000 and n[0x76]['op']=='add' and n[0x78]['op']=='divu','source-tail wrapbefore unsigneddivide')
  check(n[0x86]['op']=='bltu' and n[0xa2]['imm']==4 and n[0xa4]['op']=='add' and n[0xa6]['target']==pc+0x8a,'source-tail onlyone unsignedcompensation')
  check(n[0x5c]['rs2']==10 and n[0x8a]['imm']==140 and n[0x92]['op']=='sub' and n[0x96]['imm']+n[0x8e]['imm']==0x2000138e and n[0x9a]['imm']==41,'source-tail producer5argumenttuple')
  check(not any(d.get('rd') in (1,2) for o,d in n.items() if o>=0x52),'source-tail producer path frameless linkpreserved')
  check(not any(d.get('rd')==10 for o,d in n.items() if 0x40<=o<=0x50),'source-tail ordinaryRET keepshelperA0')
  info=dict(flagset_frame_bytes=16,flagclear_frame_bytes=0,object_explicit_extent=148,slot_literal=0x200013e8,producer_callback_argument=0x2000138e,recordproducer_pointer_argument='originalW',optional_index_output='W+41',actual_callback_invocation_or_retention_proved=False)
 check((len(walks),len(selected))==({'source':(69,10),'tail':(51,10)}[role]),'source-tail full edge/selectedpath census')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks=selected,cyclic_SCC_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']],facts=info,scope='original immutable CFG; selected syntactic paths are not feasible-execution or lifetime proofs')


def domains():
 for c in range(1,32768):
  nxt=(c+1)&65535;shift=(c+1)<<16&0xffffffff
  check((shift<0x80000000)==(c<32767) and (nxt==32768)==(c==32767),'source-tail candidate15bit/sentinel')
 for old in range(65536):check(((old+1)&65535)==(old+1)%65536,'source-tail registry countlow16 wraps')
 maxproduct=65535*65535;check(maxproduct==4294836225<2**32 and 2**32-999999==4293967297,'source-tail U16product/addoverflowthreshold')
 cases=0
 for h in range(65536):
  for k in (0,1,65535):
   p=h*k;s=(p+999999)&0xffffffff;q=s//1000000
   check(0<=q<=4294 and q+255<=4549,'source-tail scaledceilingbyte bound')
   if p<=4293967296:check(q==(p+999999)//1000000,'source-tail nonoverflow ceiling identity')
   else:check(q==0 and (p+999999)//1000000>=4294,'source-tail wrapped product breaksceiling')
   cases+=1
 check((maxproduct+999999)//1000000==4295 and ((maxproduct+999999)&0xffffffff)//1000000==0,'source-tail maximumproduct ceilingcounterexample')
 for t in (0,1,4548,4549,0xffffffff):
  for d in (0,1,4549):
   for period in (0,1,0xffffffff):
    adj=(t+(period if t<d else 0))&0xffffffff;delta=(adj-d)&0xffffffff
    check(0<=delta<=0xffffffff,'source-tail singlecorrection/subtractionmod32')
 check(((0+0-1)&0xffffffff)==0xffffffff,'source-tail onceadjust insufficientperiod witness')
 check(488%4==0 and 488>52 and 611!=0,'source-tail allocatorrequest scalarbounds')
 return dict(candidate_transition_cases=32767,admitted_candidate_interval=[1,32767],exhaustion_sentinel=32768,count_increment_cases=65536,requested_bytes=488,rounded_request=488,product_domain='allU16H times sampledK0/1/65535,closedglobalbounds notallU16pairs',product_family_cases=cases,deadline_numerical_interval=[0,4549],overflow_product_lower_bound=4293967297,maximumproduct_wrapped_quotient=0,maximumproduct_mathematical_ceiling=4295,delay_may_wrap_despite_single_period_addition=True,no_registry_state_or_clock_execution=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,SIZES[role])==raw,'source-tail fullstrictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()};sb=bs['source'];sn={d['pc']-sb['start']:d for d in sb['instructions']};tb=bs['tail'];tn={d['pc']-tb['start']:d for d in tb['instructions']}
 # Complete immediate callers prove linked source and unlinked tail, not actual installation.
 callers={}
 for role in ('key','submit'):
  pc=previous.STARTS[index][role];raw=init.binding.take(data,pc,previous.SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'source-tail caller strictHEX');callers[role]=previous.body(raw,role,index)
 check(callers['key']['calls'][0]['target']==sb['start'] and callers['submit']['tails'][0]['target']==tb['start'],'source-tail exactupstreamjoins')
 import check_v4160_allocation_core_static as alloc
 import check_v4160_allocator_static as release
 import check_v4160_config_buffer_source_static as fill
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16);reused={}
 for name,target,z,digest,fn in (
  ('allocate',alloc.ENTRY,208,alloc.DETAILS[index][-1],lambda r:alloc.decode(r)),
  ('release',release.ENTRY,212,release.DETAILS[index][-1],lambda r:release.decode(r)),
  ('fill',fill.FILL_PC,46,fill.FILL_SHA,lambda r:fill.fill_contract(r))):
  source=src+target-dest;raw=init.binding.take(data,source,z);check(dest<=target and target+z<=end and sparse.captured(mem,source,z)==raw and sha256(raw).hexdigest()==digest,'source-tail completeRAM firstcopy/identity '+name);v=fn(raw)
  if name!='fill':
   expected=alloc.specs(alloc.DETAILS[index]) if name=='allocate' else release.specifications(release.DETAILS[index]);check(v.keys()==expected.keys(),'source-tail reusedboundaries '+name)
   for a,f in expected.items():check(all(v[a].get(k)==val for k,val in f.items()),'source-tail reusedoperand '+name)
  reused[name]=dict(source=source,target=target,bytes=z,sha256=digest,actual_binding_proved=False)
 import check_v4160_record_producer_static as producer
 pp,digest=producer.DETAILS[index];raw=init.binding.take(data,pp,268);check(sparse.captured(mem,pp,268)==raw,'source-tail recordproducer strictHEX');C=producer.init.DETAILS[index][5];M=C-80;Pslot=C+64;pb=producer.body(raw,pp,M,Pslot,digest)
 check(tb['tails'][0]['target']==pp and tn[0x96]['imm']+tn[0x8e]['imm']!=0 and pb['record_stores'][1]['value']=='saved entry A1','source-tail producer retainsW inrecord4 conditionalstatus0')
 B=0x200033b8+80*index;D=0x20003234+80*index;slot=0x200034ec+80*index
 check(sn[0x2c]['imm']+sn[0x30]['imm']==B and tn[0]['imm']+tn[4]['imm']==D and tn[0xe]['imm']+tn[0x18]['imm']==slot and tn[0x7c]['imm']+tn[0x80]['imm']==0x20003203+80*index,'source-tail exactB/D/slot/byteaddresses')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_callers={r:dict(start=b['start'],bytes=b['bytes'],sha256=b['sha256']) for r,b in callers.items()},reused_RAM=reused,reused_recordproducer=dict(start=pp,bytes=268,sha256=digest,metadata_base=M,arena_pointer_slot=Pslot,record_argument_word_offset=4),addresses=dict(B=B,D=D,slot=slot),
  contracts=['source alloc488/tag611;holdP;fill(P,0,488) beforePnullguard;matchingfill null skipsdata butstillcontrolwordwrites;nonnull normalcompletion mayzero488 onlyvalid/noninterferingextent premises',
   'Pnonnull capturehead B156 once;empty ID1/headP/tailP/count1,call578a4/579e4 withA0zero notP;nonempty candidates1..32767 freshU16node8,matchincrement/restartcapturedhead,missfollownext,no finite list proof',
   'candidatefound writesP8,appendsP tofreshB160tail.next,updatesB160/countlow16;freshB160.nextzero thenP10/P14zero. Exhaustion writesP8zero/private release(P),thenfreshP8 read:neitherzero reply norvalid postrelease access proved',
   'source returnsfreshU16P8 notallocationpointer. Parentholds thisreplyK,lookup andseparateallocation canfollow;K doesnotprove originalnode stillalive/linked/samenode onlaterlookup',
   'tail flagD12nonzero:frame16,readslot;zero snapshot copiesD4 toB176/publish200013e8,thenfreshslot->43ed2/43f5e;clearB164,ordinarycallreply preservedacrossfixednumericstoree000e204=02000000 andframeRET',
   'tail flagD12zero:frameless,clearB164/slot;Q=floor(low32(U16D8*U16W134+999999)/1000000);deadlineQ+freshglobalbyte;readT=W144;ifT<deadline addfreshD4 oncemod32;delaylow32(adjustedT-deadline)',
   'framelessunlinkedproducer(2000138e,originalW,delay,W41,freshU32W140);matchingproducerstatus0 storescallback/ W pointer/metadata torecord0/4/8 andoptionalindexbyte toW41. This isconditional pointer retention,notnoescape oractualeventdelivery',
   'twoRAMliterals200013e8/2000138e differ;actualcode/MEPC routing,slot/type/otherwriters/clock/heap/registry/ownership/asyncconsumptionandfulllifetime unproved'],
  actual_installedbinding_zeroing_registry_progress_callback_execution_safe_postrelease_read_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-key-registry-source-and-submission-tail-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=712,complete_phase_body_instructions=228,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['sourcefirstregistryhelper578a4/579e4 andRAMliterals2000138e/200013e8','recordconsumer/MEPC/scheduler route and pointerownership/releaseorder','5d006/5d14e andnestedsubmithelpers,actualbindings/fullobjectextents/lifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('source-tail instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('source-tail typedmutation escaped')
    typed+=1
 check((mutated,typed)==(228,20),'source-tail mutationcensus')
 print('PASS:228 instruction/20 typed-load mutations rejected;registry ID/release-read/tail pointer-retention boundaries')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'source-tail exactledger replay')
 print('PASS:712B/228i complete keysource/submittail;strictHEX;alloc/fill/release/recordproducer joins;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/registryprogress/ownership/full lifetimes UNPROVED')


if __name__=='__main__':main()
