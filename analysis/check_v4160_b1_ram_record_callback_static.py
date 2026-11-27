"""Offline mapped record callback and registry-minimum callback contracts.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable registry/clock/output/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_key_source_tail_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-ram-record-callback-static.json')
ROLES=('record','select')
SIZES={'record':90,'select':222}
STARTS={'record': 536875918, 'select': 536876008}
SOURCES=({'record': 267774, 'select': 267864}, {'record': 267838, 'select': 267928})
COUNTS={'record': 35, 'select': 78}
HASHES=({'record': '88e7fb2ca7f89d257d394dbdfbb3270cdb03662d0a9960f3827493bddb48a494', 'select': '02c6793e01138e18b25b8b992cf92d9bb071b3beb1c22477d97c6aa3a55aeae6'}, {'record': 'c83d852956f14db700bfa1bc2dc1762104749842e5c4381c86326abc4fa89989', 'select': 'fdfdfaf7c180b688de91c28fd39c2a4665d04f77973a21d26e61d6a0780f09d5'})
LITERALS={
'record':"""
000 beqz 10 88
002 addi 2 2 -32
004 addi 11 2 12
006 store 2 8 24 4
008 store 2 1 28 4
00a mv 8 10
00c jal 1 536875298
00e beqz 10 84
010 li 15 -1
012 beq 10 15 64
016 lui 13 536883200
01a addi 13 13 492
01e load 15 13 23 1
020 load 13 13 40 4
022 load 14 2 12 4
024 beqz 13 40
026 srli 15 15 1
028 bltu 14 15 72
02c sub 15 14 15
030 store 2 15 12 4
032 load 11 2 12 4
034 load 10 8 41 1
038 auipc 1 3758366720
03c jalr 1 1 738
040 load 1 2 28 4
042 load 8 2 24 4
044 addi 2 2 32
046 jr 1
048 lui 13 536883200
04c load 13 13 568 4
050 add 14 14 13
052 jump 44
054 jal 1 536874320
056 jump 64
058 jr 1
""",
'select':"""
000 lui 15 536883200
004 addi 2 2 -48
006 addi 14 15 952
00a store 2 18 32 4
00c load 18 14 156 4
010 store 2 1 44 4
012 store 2 8 40 4
014 store 2 9 36 4
016 store 2 19 28 4
018 store 2 20 24 4
01a store 2 21 20 4
01c li 14 2
01e beq 18 0 126
022 lui 9 536883200
026 addi 21 15 952
02a addi 15 9 1300
02e load 15 15 7 1
030 li 13 5
032 addi 9 9 1300
036 li 14 3
038 beq 13 15 126
03c load 15 9 12 4
03e mv 20 10
040 beqz 15 86
042 auipc 1 3758501888
046 jalr 1 1 -284
04a auipc 1 3758497792
04e jalr 1 1 1208
052 store 9 0 12 4
056 li 19 -1
058 addi 11 2 12
05a mv 10 18
05c jal 1 536875298
05e bnez 10 146
060 lui 10 536875008
064 addi 10 10 -688
068 jal 1 536872842
06c li 15 8
06e store 9 15 4 1
070 lui 15 536883200
074 load 15 15 1340 4
078 li 14 2
07a store 15 14 100 4
07c li 14 3
07e load 1 2 44 4
080 load 8 2 40 4
082 load 9 2 36 4
084 load 18 2 32 4
086 load 19 2 28 4
088 load 20 2 24 4
08a load 21 2 20 4
08c mv 10 14
08e addi 2 2 48
090 jr 1
092 bgeu 10 19 154
096 load 8 2 12 4
098 mv 19 10
09a load 18 18 0 4
09e bne 18 0 88
0a2 li 15 -1
0a4 addi 14 0 255
0a8 beq 19 15 126
0ac li 15 4
0ae bgeu 15 8 208
0b2 addi 15 8 -5
0b6 store 20 15 0 4
0ba store 21 15 176 4
0be li 14 0
0c0 bnez 15 126
0c2 lui 15 536883200
0c6 load 15 15 568 4
0ca store 20 15 0 4
0ce jump 126
0d0 lui 15 536883200
0d4 load 15 15 568 4
0d8 addi 15 15 -5
0da add 15 15 8
0dc jump 182
""",
}
PATCHES={'record': {26: ('addi', [13, 13, 572]), 60: ('jalr', [1, 1, 878]), 76: ('load', [13, 13, 648, 4])}, 'select': {6: ('addi', [14, 15, 1032]), 38: ('addi', [21, 15, 1032]), 42: ('addi', [15, 9, 1380]), 50: ('addi', [9, 9, 1380]), 70: ('jalr', [1, 1, -50]), 78: ('jalr', [1, 1, 1442]), 116: ('load', [15, 15, 1420, 4]), 198: ('load', [15, 15, 648, 4]), 212: ('load', [15, 15, 648, 4])}}
TYPED={'record': [(52, 4), (76, 2)], 'select': [(12, 2), (116, 2), (154, 2), (198, 2), (212, 2)]}
QK={'record': [(30, 'fc3a', 'qk.c.lbu')], 'select': [(46, 'fc33', 'qk.c.lbu'), (110, 'dca0', 'qk.c.sb')]}
STORES={'record': [(6, 2, 8, 24, 4), (8, 2, 1, 28, 4), (48, 2, 15, 12, 4)], 'select': [(10, 2, 18, 32, 4), (16, 2, 1, 44, 4), (18, 2, 8, 40, 4), (20, 2, 9, 36, 4), (22, 2, 19, 28, 4), (24, 2, 20, 24, 4), (26, 2, 21, 20, 4), (82, 9, 0, 12, 4), (110, 9, 15, 4, 1), (122, 15, 14, 100, 4), (182, 20, 15, 0, 4), (186, 21, 15, 176, 4), (202, 20, 15, 0, 4)]}


def specs(role,index):
 pc=STARTS[role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'RAMrecord literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'RAMrecord completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'RAMrecord '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'RAMrecord completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'RAMrecord typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'RAMrecord exactQK')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'RAMrecord RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   check(d['rd']==1,'RAMrecord allcallslinked')
   if op=='jal':target=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'RAMrecord linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('call_indirect','ecall','mret','csr') and all(z in n for z in q),'RAMrecord closedCFG');e[a]=q
 expected={'record':[(0xc,0x20001122),(0x3c,0x436a8+140*index),(0x54,0x20000d50)],'select':[(0x46,0x6430e+234*index),(0x4e,0x638ea+234*index),(0x5c,0x20001122),(0x68,0x2000078a)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==([0x46,0x58] if role=='record' else [0x90]),'RAMrecord exactcalls/RET')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'RAMrecord allreachable includingpostRET')
 common=previous.previous.previous.previous.previous.previous.previous.previous.dispatch.common;groups=common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]]
 check(bool(cycles)==(role=='select'),'RAMrecord registryloop onlyselect')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'RAMrecord allstores')
 return dict(start=pc,source=SOURCES[index][role],bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,returns=rets,cyclic_SCCs=cycles,stores=stores,complete_local_body=True,actual_installedbinding_queryoutputs_or_progress_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=[a for a,q in e.items() if not q]
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 def finish(a):
  ps=[p for z in ends if (p:=path(a,z)) is not None];check(bool(ps),'RAMrecord suffix');return min(ps,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'RAMrecord edgewitness');walks.append([a-pc for a in p])
 def select(choices):
  a=pc;p=[]
  while True:
   o=a-pc;check(o not in p,'RAMrecord selectedwalk finite');p.append(o)
   if not e[a]:break
   if o in choices:q=pc+choices[o];check(q in e[a],'RAMrecord selectededge')
   else:check(len(e[a])==1,'RAMrecord missingchoice '+hex(o));q=e[a][0]
   a=q
  return p
 if role=='record':
  base={0:2,0xe:0x10,0x12:0x16,0x24:0x28,0x28:0x2c}
  chosen={k:select(base|v) for k,v in {'nullentry':{0:0x58},'query0':{0xe:0x54},'query-1':{0x12:0x40},'other-fullbyte':{},'other-halfbyte':{0x24:0x26},'other-adjustonce':{0x28:0x48}}.items()}
  check(n[4]['rs1']==2 and n[4]['imm']==12 and n[0x22]['rs1']==2 and n[0x22]['imm']==12,'RAMrecord borrowedSP12 output read')
  check([o for o,d in n.items() if d['op']=='store' and d['rs1']==2]==[6,8,0x30] and n[0x30]['imm']==12,'RAMrecord noSP12localinitialization beforequery/read')
  check(n[0xa]['rd']==8 and n[0xa]['rs2']==10 and n[0x34]['rs1']==8 and n[0x34]['imm']==41,'RAMrecord heldP laterIDbyte')
  check(n[0xe]['target']==pc+0x54 and n[0x10]['imm']==-1 and n[0x12]['target']==pc+0x40,'RAMrecord fullRzero/minus1 branches')
  check(n[0x1e]['imm']==23 and n[0x20]['imm']==40 and n[0x26]['imm']==1 and n[0x24]['target']==pc+0x28,'RAMrecord independentbyte/wordthreshold')
  check(n[0x4c]['imm']==568+80*(SOURCES[0]['record']!=b['source']) and n[0x50]['op']=='add' and n[0x52]['target']==pc+0x2c and n[0x2c]['op']=='sub','RAMrecord singlewrapadjust then subtract')
  check(n[0x32]['imm']==12 and n[0x32]['rd']==11 and n[0x34]['rd']==10,'RAMrecord helper argsID/calculatedword')
  check(not any(d.get('rd')==10 for o,d in n.items() if 0x40<=o<=0x46) and n[0x58]['op']=='jr','RAMrecord childreply orentry0 propagated')
  info=dict(frame_bytes=32,nullentry_frameless=True,object_explicit_extent=42,local_SP12_preinitialization=False,query_output_initialization_or_nonretention_proved=False,return_description='null0;queryminus1 ffffffff;query0 oradjustedbranch actualchildA0')
 else:
  base={0x1e:0x22,0x38:0x3c,0x40:0x56,0x5e:0x92,0x92:0x96,0x9e:0xa2,0xa8:0xac,0xae:0xb2,0xc0:0x7e}
  chosen={k:select(base|v) for k,v in {'empty2':{0x1e:0x7e},'flag5-status3':{0x38:0x7e},'optionalprecalls':{0x40:0x42},'query0-status3':{0x5e:0x60},'allminus1-status255':{0x92:0x9a,0xa8:0x7e},'selectedXabove5':{},'selectedX5-outputoverwrite':{0xc0:0xc2},'selectedXbelow5':{0xae:0xd0}}.items()}
  check(n[0xc]['imm']==156 and n[0xc]['rd']==18 and n[0x9a]['rs1']==n[0x9a]['rd']==18 and n[0x9a]['imm']==0,'RAMrecord capturedhead/freshnext afterquery')
  check(n[0x56]['imm']==-1 and n[0x92]['op']=='bgeu' and n[0x92]['rs1']==10 and n[0x92]['rs2']==19 and n[0x98]['rs2']==10,'RAMrecord strictunsigned reply minimum/ties')
  check([o for o,d in n.items() if d.get('rd')==19]==[0x56,0x86,0x98] and [o for o,d in n.items() if d.get('rd')==8]==[0x80,0x96],'RAMrecord selectedSP12 hasonlystrictmin definition')
  check(n[0x58]['imm']==12 and n[0x58]['rs1']==2 and n[0x96]['imm']==12 and not any(d['op']=='store' and d['rs1']==2 and d['imm']<=12<d['imm']+d['width'] for d in n.values()),'RAMrecord selectSP12 neverlocallyinitialized')
  check(n[0x3e]['rs2']==10 and n[0xb6]['rs1']==n[0xca]['rs1']==20 and n[0xba]['imm']==176,'RAMrecord borrowedentryoutput vsB176 scalar')
  check(n[0x1c]['imm']==2 and n[0x36]['imm']==n[0x7c]['imm']==3 and n[0xa4]['imm']==255 and n[0xbe]['imm']==0 and n[0x8c]['rs2']==14,'RAMrecord allstatus definitions')
  check(n[0x3c]['imm']==12 and n[0x52]['rs2']==0 and n[0x52]['imm']==12,'RAMrecord optionaltwo-call gate/clear')
  check(n[0x60]['imm']+n[0x64]['imm']==0x20000d50 and n[0x6c]['imm']==8 and n[0x6e]['imm']==4 and n[0x78]['imm']==2 and n[0x7a]['imm']==100,'RAMrecord query0 setter/statusstores')
  check(n[0xac]['imm']==4 and n[0xb2]['imm']==-5 and n[0xd8]['imm']==-5 and n[0xda]['rs2']==8,'RAMrecord Xthreshold/sub5 adjustment')
  check(n[0xc0]['rs1']==15 and n[0xc0]['target']==pc+0x7e and n[0xca]['rs1']==20 and not any(d['op']=='store' and d['rs1']==21 for o,d in n.items() if o>=0xc2),'RAMrecord computedYzero overwritesonlycalleroutput')
  check(n[0x3e]['rd']==20 and n[0x46]['op']=='jalr','RAMrecord optionalopaquechild observesentryoutputA0')
  info=dict(frame_bytes=48,output_minimum_writable_bytes=4,local_output_nullguard=False,local_SP12_preinitialization=False,query_output_initialization_or_nonretention_proved=False,positive_replies_selected_interval=[1,4294967294],ties_keep_first_captured_output=True,B176_stores_scalar_not_outputpointer=True,statuses=[2,3,255,0],registry_termination_proved=False)
 check((len(walks),len(chosen))==({'record':(38,6),'select':(86,8)}[role]),'RAMrecord full edge/path census')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks=chosen,cyclic_SCC_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']],facts=info,actual_pathfeasibility_outputinitialization_or_complete_lifetime_proved=False)


def domains():
 for c in range(256):
  for mode in (0,1,0xffffffff):
   a=c if mode==0 else c>>1;check(0<=a<=255 and (mode==0 or a<=127),'RAMrecord byte/fullwordmode threshold')
 for t in (0,1,127,255,0xffffffff):
  for a in (0,1,127,255):
   for m in (0,1,0xffffffff):
    x=(t+(m if t<a else 0)-a)&0xffffffff;check(0<=x<=0xffffffff,'RAMrecord adjustonce/subtractmod32')
 check((0+0-1)&0xffffffff==0xffffffff,'RAMrecord onceaddition maystillunderflow')
 family=(0,1,2,0x7fffffff,0x80000000,0xfffffffe,0xffffffff)
 for r in family:
  check((r!=0 and r<0xffffffff)==(1<=r<=0xfffffffe),'RAMrecord initialmin unsignedadmission')
  for best in family:
   check((r!=0 and r<best)==(0<r<best),'RAMrecord strictmin/tie predicate')
 for x in range(65536):
  for period in (0,1,5,0xffffffff):
   y=(x-5)&0xffffffff if x>=5 else (period-5+x)&0xffffffff
   check(0<=y<=0xffffffff,'RAMrecord selectorborrowedoutput formula')
 check(5-5==0 and ((0xffffffff-5+0)&0xffffffff)==0xfffffffa,'RAMrecord zeroresult/underflow witnesses')
 return dict(threshold_byte_mode_cases=768,minimum_reply_family=list(family),minimum_pair_cases=49,selected_output_sample_domain='allX0..65535 with period0/1/5/ffffffff;closedU32 formula bounds,notallU32pairs',selected_output_family_cases=262144,select_Y_formula='X>=5:X-5;else low32(freshperiod-5+X);storeY toOut andB176;ifY0freshperiod2 overwritesOutonly',zero_Y_possible_X=5,caller_output_and_B176_may_differ=True,closed_scalar_identities_only=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16);bs={}
 for role in ROLES:
  pc=STARTS[role];source=SOURCES[index][role];raw=init.binding.take(data,source,SIZES[role]);check(src+pc-dest==source and dest<=pc and pc+len(raw)<=end and sparse.captured(mem,source,len(raw))==raw,'RAMrecord fullfirstcopy/strictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()}
 # Revalidate literal producer, whose code mapping is not proof of later RAM identity.
 tp=previous.STARTS[index]['tail'];tr=init.binding.take(data,tp,168);check(sparse.captured(mem,tp,168)==tr,'RAMrecord full literalproducer strictHEX');tb=previous.body(tr,'tail',index);tn={d['pc']-tp:d for d in tb['instructions']}
 check(tn[0x28]['imm']+tn[0x2c]['imm']==STARTS['select'] and tn[0x8e]['imm']+tn[0x96]['imm']==STARTS['record'],'RAMrecord exactpublished/tailcallback literals')
 import check_v4160_hook_lifetime_static as hook
 hs,delta,sh,ch=hook.DETAILS[index];hr=init.binding.take(data,hs,22);check(sparse.captured(mem,hs,22)==hr and src+0x2000078a-dest==hs,'RAMrecord setter fullfirstcopy/HEX');hb=hook.body(hr,'setter',0x2000078a,delta,sh)
 import check_v4160_record_producer_static as producer
 import check_v4160_builtin_record_handlers_static as handlers
 pp,digest=producer.DETAILS[index];C=producer.init.DETAILS[index][5];M=C-80;Pslot=C+64;pr=init.binding.take(data,pp,268);check(sparse.captured(mem,pp,268)==pr,'RAMrecord producer fullHEX');pb=producer.body(pr,pp,M,Pslot,digest)
 hp=handlers.post.DETAILS[index][4];fr=init.binding.word(data,0x40068);hraw=init.binding.take(data,hp,130);check(sparse.captured(mem,hp,130)==hraw,'RAMrecord handler0 fullHEX');handler=handlers.body(hraw,hp,0,Pslot-0x20003000,fr,handlers.DIGESTS[index][0])
 check(handler['record_callback']['A0']=='fresh U32[selected record+4]' and handler['record_callback']['pointer_source']=='selected record+0' and not handler['record_callback']['scalar_A0_reply_used'],'RAMrecord record4->W callback andignoredscalarreply')
 check(pb['record_stores'][0]['value']=='saved entry A0' and pb['record_stores'][1]['value']=='saved entry A1','RAMrecord producer callback/pointer composition')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_literalproducer=dict(start=tp,bytes=168,sha256=tb['sha256']),reused_hooksetter=dict(source=hs,target=0x2000078a,bytes=22,sha256=sh),reused_producer=dict(start=pp,bytes=268,sha256=digest),reused_handler0=dict(start=hp,bytes=130,sha256=handler['sha256'],record_callback=handler['record_callback'],clear_condition=handler['clear_condition']),
  contracts=['recordcallback Pnull returns0frameless;nonnull frame32 query20001122(P,SP12) withno localpreinit;R0calls20000d50 withA0zero,returnsactualchildreply;Rffffffff returnsunchanged;othersconsumeunknownqueryoutputSP12',
   'recordother R:sampleU8F23 andindependentU32F40;thresholdbyte orbyte>>1;freshT=SP12;ifT<threshold addfreshglobalperiodoncemod32;subtractthreshold;call436a8/43734(freshU8P41,calculatedword);actualreplypropagated',
   'selectframe48 captureB156head,empty2;freshI7=5 ->3;otherwiseholdentryOut,optional I12nonzero requests6430e/643f8(Out,ambient),then638ea/639d4(previousreply,ambient),clearI12. NoOutputnullguard ortransitivenonescapeproof',
   'selectloop query20001122(node,SP12);R0setter2000078a(20000d50),I4=8,freshH100=2,return3;Rnonzero strictunsignedbelowbest selectsSP12word andR;tieskeepfirst,ffffffffneverselects;freshnode.next readafterquery no cycle/extent/lifetimebound',
   'allnonzeroqueries ffffffff andnormalfiniteend ->255,nooutputstores;elseX=selectedqueryoutput,Y=X>=5?X-5:low32(freshperiod-5+X). StoreYthroughOut thenB176;Yzero reloadperiod andoverwriteOutonly;return0,no actualoutputvalueoratomicpair proof underalias/externalwrites',
   'underactualsamearena/index/code/binding/preservation/recordmetadata,producerstores literal2000138e andW inrecord0/4;handler0 laterusesrecord0 ascallback andrecord4 asA0. Returnscalarignored;freshrecord8zero thenrecord0/4clear,notfullWfree orcompletedasynclifetime',
   'RAMquery20001122/outputcontract,downstream436a8,optionalcallees,MEPC/slotroute/otherwriters/registryshape/sourcevalidity/pointerretention andfulllifetimes unproved'],
  actual_installedbinding_query_outputinitialization_record_identity_callback_execution_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-mapped-record-and-minimum-callback-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=624,complete_phase_body_instructions=226,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['RAM20001122 query outputs/SP12 initialization/retention and436a8/43734 downstream','optional6430e/638ea helpers,MEPC/slot/record route and releaseorder','5d006/5d14e andnestedsubmithelpers,actualbindings/ownership/fullpointerlifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[role];raw=init.binding.take(data,SOURCES[i][role],SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('RAMrecord instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('RAMrecord typedmutation escaped')
    typed+=1
 check((mutated,typed)==(226,14),'RAMrecord mutationcensus')
 print('PASS:226 instruction/14 typed-load mutations rejected;RAM callback query/output/registry/record boundaries')


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
 else:check(OUT.read_bytes()==encoded,'RAMrecord exactledger replay')
 print('PASS:624B/226i complete mappedRAM callbacks;strictHEX/fullfirstcopy;record/handler/queryfrontier;exactledger')
 print('PASS:NO target execution/emulation;queryoutputs/providerbindings/ownership/full lifetimes UNPROVED')


if __name__=='__main__':main()
