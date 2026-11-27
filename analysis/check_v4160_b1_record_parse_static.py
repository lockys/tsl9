"""Offline record-parse gates, object byte writers and conditional leaf composition.
Original bytes/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable object/queue/heap/clock/provider model.
"""
import argparse,json
from collections import deque
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_notify_selection_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-record-parse-static.json')
STARTS=(0x5c830,0x5c978)
HASHES=('1f0dc9a985fc982c1eb33503cbd3287ce4ed545f835136660c2c46c9659e90b0', '5b87a0fc1e923429e3dff4c4d5340feecf3e02645f16a31609d83f9004b272c4')
LITERAL="""
000 addi 2 2 -32
002 store 2 9 20 4
004 mv 9 10
006 load 10 10 80 4
008 li 13 0
00a li 12 0
00c li 11 0
00e store 2 18 16 4
010 store 2 1 28 4
012 store 2 8 24 4
014 store 2 19 12 4
016 auipc 1 536502272
01a jalr 1 1 -524
01e li 18 1
020 bnez 10 84
022 load 8 9 80 4
024 li 13 8
026 li 18 7
028 load 15 8 0 1
02a andi 15 15 15
02c store 9 15 19 1
02e load 14 8 1 1
030 store 9 14 18 1
032 bne 15 13 84
036 load 19 8 2 1
03a srli 18 19 6
03e bne 18 0 372
042 addi 15 19 1
046 bne 14 15 376
04a load 14 8 3 1
04c li 15 3
04e beq 14 15 100
052 li 18 17
054 load 1 2 28 4
056 load 8 2 24 4
058 mv 10 18
05a load 9 2 20 4
05c load 18 2 16 4
05e load 19 2 12 4
060 addi 2 2 32
062 jr 1
064 load 10 9 176 4
068 li 12 6
06a addi 11 8 4
06e addi 10 10 4
070 auipc 1 536494080
074 jalr 1 1 -1118
078 beqz 10 82
07a li 12 6
07c addi 11 8 10
080 addi 10 9 54
084 auipc 1 536494080
088 jalr 1 1 -1138
08c beq 10 0 380
090 li 15 13
092 bne 19 15 384
096 jal 1 368228
09a jal 1 358474
09e mv 8 10
0a0 beqz 10 362
0a2 load 13 9 176 4
0a6 load 14 9 36 4
0a8 load 15 9 76 4
0aa li 16 0
0ac store 10 14 136 4
0b0 load 14 13 24 4
0b2 lui 11 536883200
0b6 addi 11 11 1214
0ba store 10 14 152 4
0be load 14 13 20 4
0c0 addi 10 10 312
0c4 store 10 14 -156 4
0c8 load 14 15 21 1
0ca store 10 14 -257 1
0ce load 14 15 23 1
0d0 load 12 15 22 1
0d2 slli 14 14 8
0d4 or 14 14 12
0d6 store 10 14 -256 2
0da load 14 15 25 1
0dc load 12 15 24 1
0de slli 14 14 8
0e0 or 14 14 12
0e2 store 10 14 -254 2
0e6 load 14 15 27 1
0e8 load 12 15 26 1
0ea slli 14 14 8
0ec or 14 14 12
0ee store 10 14 -252 2
0f2 load 14 15 28 1
0f4 load 15 15 29 1
0f6 li 12 5
0f8 slli 15 15 8
0fa or 15 15 14
0fc store 10 15 -250 2
100 load 15 13 28 1
102 store 10 16 4 4
106 store 10 15 -259 1
10a li 15 0
10c store 10 15 0 4
10e auipc 1 536494080
112 jalr 1 1 -1548
116 li 15 1
118 store 8 15 320 1
11c load 15 9 128 1
120 mv 10 8
122 store 8 15 326 1
126 store 8 15 327 1
12a jal 1 367934
12e lui 15 536883200
132 addi 14 15 952
136 load 14 14 224 4
13a addi 19 15 952
13e andi 14 14 512
142 beqz 14 338
144 load 10 8 8 2
146 addi 12 0 41
14a addi 11 0 128
14e jal 1 385960
152 load 15 19 216 4
156 slli 14 15 17
15a bge 14 0 362
15e load 10 8 8 2
160 li 12 20
162 addi 11 0 128
166 jal 1 385960
16a load 15 9 172 4
16e li 14 3
170 store 15 14 11 1
172 jump 84
174 li 18 5
176 jump 84
178 li 18 25
17a jump 84
17c li 18 18
17e jump 84
180 li 18 24
182 jump 84
"""
PATCH={26: ('jalr', [1, 1, -776]), 116: ('jalr', [1, 1, -1446]), 136: ('jalr', [1, 1, -1466]), 150: ('jal', [1, 368556]), 154: ('jal', [1, 358794]), 182: ('addi', [11, 11, 1294]), 274: ('jalr', [1, 1, -1876]), 298: ('jal', [1, 368262]), 306: ('addi', [14, 15, 1032]), 314: ('addi', [19, 15, 1032]), 334: ('jal', [1, 386288]), 358: ('jal', [1, 386288])}
TYPED=[(54, 4), (100, 2), (162, 2), (284, 4), (310, 2), (338, 2), (362, 2)]
QK=[(40, '1c20', 'qk.c.lbu'), (44, 'bcb8', 'qk.c.sb'), (46, '1830', 'qk.c.lbu'), (48, 'b8a8', 'qk.c.sb'), (74, '3830', 'qk.c.lbu'), (200, 'd83b', 'qk.c.lbu'), (206, 'f83b', 'qk.c.lbu'), (208, 'f02b', 'qk.c.lbu'), (218, '983f', 'qk.c.lbu'), (220, '902f', 'qk.c.lbu'), (230, 'b83f', 'qk.c.lbu'), (232, 'b02f', 'qk.c.lbu'), (242, 'd82f', 'qk.c.lbu'), (244, 'dc3f', 'qk.c.lbu'), (256, 'dc2e', 'qk.c.lbu'), (324, '0a24', 'qk.c.lhu'), (350, '0a24', 'qk.c.lhu'), (368, 'b8b7', 'qk.c.sb')]
STORES=[(2, 2, 9, 20, 4), (14, 2, 18, 16, 4), (16, 2, 1, 28, 4), (18, 2, 8, 24, 4), (20, 2, 19, 12, 4), (44, 9, 15, 19, 1), (48, 9, 14, 18, 1), (172, 10, 14, 136, 4), (186, 10, 14, 152, 4), (196, 10, 14, -156, 4), (202, 10, 14, -257, 1), (214, 10, 14, -256, 2), (226, 10, 14, -254, 2), (238, 10, 14, -252, 2), (252, 10, 15, -250, 2), (258, 10, 16, 4, 4), (262, 10, 15, -259, 1), (268, 10, 15, 0, 4), (280, 8, 15, 320, 1), (290, 8, 15, 326, 1), (294, 8, 15, 327, 1), (368, 15, 14, 11, 1)]


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*vals=row.split();o=int(off,16);vals=list(map(int,vals))
  if index and o in PATCH:op,vals=PATCH[o]
  check(len(vals)==len(FIELDS[op]),'recordparse literalfields');f=dict(zip(FIELDS[op],vals));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'recordparse fullboundaries')
 for a,f in s.items():init.g(n,a,'recordparse operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(388,138,HASHES[index]),'recordparse completeidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'recordparse typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'recordparse exactQK')
 e={};calls=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'recordparse RET RA');q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   check(d['rd']==1,'recordparse allcalls linked')
   if op=='jal':target=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'recordparse PCrelativepair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('call_indirect','csr','mret','ecall') and all(z in n for z in q),'recordparse closedCFG');e[a]=q
 expected=[(0x1a,0x2000263a+76*index),(0x74,0x20000442),(0x88,0x20000442),(0x96,0x59e64+328*index),(0x9a,0x5784a+320*index),(0x112,0x20000332),(0x12a,0x59d3e+328*index),(0x14e,0x5e3a8+328*index),(0x166,0x5e3a8+328*index)]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'recordparse all9calls')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and [a-pc for a,q in e.items() if not q]==[0x62],'recordparse complete reachability/soleRET')
 groups=previous.previous.previous.previous.previous.dispatch.common.sccs(e)
 check(all(len(g)==1 and g[0] not in e[g[0]] for g in groups),'recordparse acyclic localCFG')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==STORES and len(stores)==22 and len(TYPED)==7 and len(QK)==18,'recordparse stores/typed/QK census')
 return dict(start=pc,bytes=388,sha256=HASHES[index],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,stores=stores,returns=[0x62],complete_local_body=True,local_CFG_acyclic=True,actual_callee_or_wholechain_return_proved=False)


def certificates(b):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']}
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((q,p+[q]) for q in e[a])
  raise RuntimeError('recordparse missing syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,pc+0x62)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'recordparse all-edge witnesses');walks.append([a-pc for a in p])
 # Immutable branch choices for each status path, never a target-state replay.
 def witness(choices):
  a=pc;walk=[]
  while True:
   o=a-pc;check(o not in walk,'recordparse acyclic selectedwalk');walk.append(o)
   if not e[a]:break
   if o in choices:z=pc+choices[o];check(z in e[a],'recordparse selectededge')
   else:check(len(e[a])==1,'recordparse missing branchchoice '+hex(o));z=e[a][0]
   a=z
  return walk
 base={0x20:0x22,0x32:0x36,0x3e:0x42,0x46:0x4a,0x4e:0x64,0x78:0x7a,0x8c:0x90,0x92:0x96,0xa0:0x16a}
 cases={
  '1-service-nonzero':{0x20:0x54},
  '7-low4-not8':{0x32:0x54},
  '5-byte2-high2-nonzero':{0x3e:0x174},
  '25-byte1-notbyte2plus1':{0x46:0x178},
  '17-byte3-not3':{0x4e:0x52},
  '17-firstcompare-zero':{0x78:0x52},
  '18-secondcompare-zero':{0x8c:0x17c},
  '24-byte2-not13':{0x92:0x180},
  '0-lookup-null':{},
  '0-lookup-nonnull-noevents':{0xa0:0xa2,0x142:0x152,0x15a:0x16a},
  '0-lookup-nonnull-both-events':{0xa0:0xa2,0x142:0x144,0x15a:0x15e}}
 selected={k:witness(base|v) for k,v in cases.items()}
 check(len(walks)==148 and len(selected)==11,'recordparse complete edge/status witness census')
 check([o for o,d in n.items() if d.get('rd')==18]==[0x1e,0x26,0x3a,0x52,0x5c,0x174,0x178,0x17c,0x180],'recordparse allstatus definitions')
 check(n[0x58]['op']=='mv' and n[0x58]['rd']==10 and n[0x58]['rs2']==18 and not any(d.get('rd')==10 for o,d in n.items() if 0x5a<=o<=0x62),'recordparse sole common statusreturn')
 assigned={0x1e:1,0x26:7,0x3a:0,0x52:17,0x174:5,0x178:25,0x17c:18,0x180:24}
 # +052 is an assignment to S2 too; its spelling remains pinned by full literals.
 for label,walk in selected.items():
  writes=[assigned[o] for o in walk if o in assigned]
  check(writes and writes[-1]==int(label.split('-')[0]),'recordparse status/witness relation '+label)
 check(n[0x3a]['imm']==6 and n[0x42]['imm']==1 and n[0x90]['imm']==13,'recordparse type/length necessarygates')
 check(n[0x2c]['imm']==19 and n[0x30]['imm']==18 and n[0x28]['imm']==0 and n[0x2e]['imm']==1,'recordparse prevalidation N19/N18 publications')
 check(n[0x22]['rd']==8 and n[0x22]['imm']==80 and n[0x9e]['rd']==8 and n[0x9e]['rs2']==10,'recordparse S0 rolechange packet->lookupresult')
 check([o for o,d in n.items() if d.get('rd')==8]==[0x22,0x56,0x9e],'recordparse exactS0 reachingdefinitions')
 check(n[0xa0]['target']==pc+0x16a and n[0x16a]['imm']==172 and n[0x170]['imm']==11 and n[0x16e]['imm']==3,'recordparse nullW stillchild11=3')
 # Direct object offsets computed from one W plus312, independently of pointer state.
 obj=[(0xac,136,4),(0xba,152,4),(0xc4,156,4),(0xca,55,1),(0xd6,56,2),(0xe2,58,2),(0xee,60,2),(0xfc,62,2),(0x102,316,4),(0x106,53,1),(0x10c,312,4),(0x118,320,1),(0x122,326,1),(0x126,327,1)]
 for o,off,w in obj:
  d=n[o];bias=312 if d['rs1']==10 and o>=0xc4 else 0
  check(d['op']=='store' and d['rs1'] in (8,10) and bias+d['imm']==off and d['width']==w,'recordparse object store geometry '+hex(o))
 check(n[0xc0]['rd']==10 and n[0xc0]['rs1']==10 and n[0xc0]['imm']==312 and n[0x10a]['imm']==n[0xaa]['imm']==0,'recordparse W312 directzero words')
 check(n[0xf6]['imm']==5 and n[0x11c]['imm']==128 and n[0x122]['rs2']==n[0x126]['rs2']==15,'recordparse copy5 /same capturedN128byte')
 check(n[0x13e]['imm']==512 and n[0x156]['imm']==17 and n[0x15a]['op']=='bge','recordparse independent bit9/bit14 eventgates')
 check(n[0x146]['imm']==41 and n[0x160]['imm']==20 and n[0x14a]['imm']==n[0x162]['imm']==128,'recordparse event scalarcode tuples')
 check(n[0x144]['imm']==n[0x15e]['imm']==8 and n[0x144]['width']==n[0x15e]['width']==2,'recordparse freshlookupobjectIDreads')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_status_walks=selected,explicit_object_stores=obj,source_extents=dict(packet_P=16,fresh_N176_Q=29,fresh_N76_T=30,lookup_W=328,N=180,child=12),scope='original immutable CFG; paths require predicate/callee/extent/preservation premises, not actual executions')


def domains():
 counts={}
 for b2 in range(256):
  check((b2>>6==0)==(b2<64),'recordparse byte2 high2 gate')
  if b2<64:check(1<=b2+1<=64,'recordparse lengthadd no wrap')
 accepted=[(b1,b2) for b1 in range(256) for b2 in range(256) if b2<64 and b1==b2+1 and b2==13]
 check(accepted==[(14,13)],'recordparse captured lengthtuple necessary notsource extentproof')
 for lo in range(256):
  for hi in range(256):
   packed=lo|(hi<<8);check(packed.to_bytes(2,'little')==bytes((lo,hi)),'recordparse four LE16 bytepair identities')
 for bit in range(32):
  check(bool(((1<<bit)<<17)&0x80000000)==(bit==14),'recordparse sign of slli17 is bit14')
 direct={(o+j) for o,z in ((312,4),(316,4)) for j in range(z)}
 check(direct==set(range(312,320)) and set(range(312,317))<=direct,'recordparse zero8/copy5 ranges')
 check(list(range(317,320))==sorted(direct-set(range(312,317))),'recordparse trailing3 remainzero conditionalcopy')
 for h in range(16):check(h&15==h,'recordparse headerlow4 closed')
 return dict(byte2_domain_cases=256,length_byte_pair_cases=65536,necessary_admitted_tuple=dict(P1=14,P2=13),packed_LE16_cases=65536,flag_basis_cases=32,copy5_extent=[312,317],zero8_extent=[312,320],trailing_zero_bytes_after_matching_copy=[317,318,319],actual_source_length_initialization_or_object_validity_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,388);check(sparse.captured(mem,pc,388)==raw,'recordparse full strictHEX');b=body(raw,index);n={d['pc']-pc:d for d in b['instructions']};cert=certificates(b)
 record=previous.previous;cp=record.STARTS[index];cr=init.binding.take(data,cp,1618);check(sparse.captured(mem,cp,1618)==cr,'recordparse full recordcaller strictHEX');cb=record.body(cr,index);cn={d['pc']-cp:d for d in cb['instructions']}
 check(next(c['target'] for c in cb['calls'] if c['offset']==0x33a)==pc and cn[0x338]['rs2']==8,'recordparse caller forwardsN')
 check(cb['CFG'][cp+0x33a]==[cp+0x33e] and not any(d.get('rd')==10 or d.get('rs1')==10 or d.get('rs2')==10 for o,d in cn.items() if 0x33e<=o<=0x350),'recordparse immediatecaller ignoresA0 beforeindexadvance')
 check(cn[0x33e]['imm']==9 and cn[0x34c]['imm']==9 and cn[0x346]['imm']==1 and cn[0x348]['imm']==255,'recordparse independent postreply cursoradvance modulo256')
 completion=record.completion;mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16);leaves={}
 for name,target,z,fn in (
  ('service',completion.service.STARTS[index][4],128,lambda r:completion.service.body(r,'RAMservice',index)),
  ('comparator',0x20000442,72,lambda r:completion.leaves.comparator.body(r,'comparator',index)),
  ('copy',0x20000332,58,lambda r:completion.leaves.copier.body(r,'copy',0x20000332,18,init.binding.COPY_HASH))):
  source=src+target-dest;r=init.binding.take(data,source,z);check(dest<=target and target+z<=end and sparse.captured(mem,source,z)==r,'recordparse full reusedRAM/strictHEX/firstcopy');v=fn(r);leaves[name]=dict(target=target,source=source,bytes=z,sha256=v['sha256'],instructions=v['instructions'],actual_binding_proved=False)
 check(b['calls'][0]['target']==leaves['service']['target'] and all(n[o]['imm']==0 for o in (8,0xa,0xc)) and n[6]['imm']==80,'recordparse service(N80,0,0,0) notcopy')
 check(n[0x64]['imm']==176 and n[0x68]['imm']==6 and n[0x6a]['imm']==n[0x6e]['imm']==4 and n[0x7a]['imm']==6 and n[0x7c]['imm']==10 and n[0x80]['imm']==54,'recordparse two exact comparator tuples')
 look=completion.ramrequest;lp=look.STARTS[index][2];lr=init.binding.take(data,lp,24);check(sparse.captured(mem,lp,24)==lr,'recordparse lookup fullstrictHEX');lb=look.body(lr,'lookup',index)
 check(b['calls'][4]['target']==lp and b['CFG'][pc+0x96]==[pc+0x9a] and not any(pc+0x96<a<pc+0x9a for a in b['CFG']),'recordparse producerreply directly becomes fulllookupkey')
 builder=previous.queue;bp=builder.STARTS[index][1];br=init.binding.take(data,bp,102);check(sparse.captured(mem,bp,102)==br,'recordparse builder fullstrictHEX');bb=builder.body(br,'builder',index)
 check(b['calls'][-1]['target']==b['calls'][-2]['target']==bp,'recordparse same eventbuilder both callsites')
 globalcopy=0x20003000+n[0xb6]['imm'];B=0x20003000+n[0x132]['imm'];check(globalcopy==0x200034be+80*index and B==0x200033b8+80*index,'recordparse exact fixedsource/Bcontext')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=cert,reused_recordcaller=dict(start=cp,bytes=1618,sha256=cb['sha256']),reused_RAM_leaves=leaves,reused_lookup=lb,reused_eventbuilder=dict(start=bp,bytes=102,sha256=bb['sha256']),fixed_copy5_source=globalcopy,
  contracts=['service(N80,0,0,0) skips packet dereference/optionaloutputs under matching128Bleaf, returns0/1 basedonfreshcontrolstatus; nonzero ->parser1',
   'freshN80=P; publishN19=low4P0 andN18=P1 beforevalidation; guards low4P0=8,P2<64,P1=P2+1,P3=3,compare(Q+4,P+4,6)!=0,compare(N+54,P+10,6)!=0,P2=13; earlystatuses1/7/5/25/17/18/24 no rollback',
   'matching comparator returns0/1 withnull-success; nonzero alone not proof of nonnull/valid bytes/equality. Accepted capturedP1/P2 scalarpair14/13 notactualextent/headertruth',
   '59e64/59fac receives last comparatorreplyA0 andthen-live otherGPRs; its fullreply becomes fullword lookupkey5784a/5798a. Lookup follows globalhead andU16node8 equality, no allocation. Listfinite/keyproducer/pointerownership unproved',
   'lookupnull skipsall Wstores/copy/events but joins freshN172 child11=3,RET0; lookupnonnull W explicitstores+copy5 region; W at least328bytes,heldQfromfreshN176 extent29,TfromfreshN76 extent30',
   'W136=N36,W152=Q24word,W156=Q20word,W53=Q28byte,W55=T21,W56..63 packedT22..29; W312/W316zero then copy5(W312,fixedglobal,5),W320=1,W326/W327=samecapturedN128',
   'submit59d3e/59e86(W),normalreply ignored; freshB224bit9 optionallybuilder(U16W8,128,41),independentfreshB216bit14 optionallybuilder(U16W8,128,20). Buildervisiblemessage80,code29hex/14hex,IDlo,IDhi undermatchingallocation/copy/send; noqueuedeliveryproof',
   'caller ignores parserA0 thenadvancesheldtable9 modulo256; no successgate. Allcrosscallee/frame/SP/S/RA/object/global/alias/sourcepreservation andactualbindings conditional; no complete lifetime proof'],
  actual_binding_payload_extent_initialized_contents_allocation_queue_delivery_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-record-parse-object-writers-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=776,complete_phase_body_instructions=276,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['59e64/59fac keyproducer and59d3e/59e86 submission sideeffects','5d006/5d14e full followup andsourcewriters','actualprovider bindings/validlengths/lookupownership/pointerlifetimes/messageconsumption'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],388);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('recordparse instructionmutation escaped')
   mutated+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('recordparse typedmutation escaped')
   typed+=1
 check((mutated,typed)==(276,14),'recordparse mutationcensus')
 print('PASS:276 instruction/14 typed-load mutations rejected;full recordparse gates/status/objectwriters')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
 check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,tail,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'recordparse exactledger replay')
 print('PASS:776B/276i complete recordparse;strictHEX;9calls/22stores perprofile;status/lookup/caller;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/lookupownership/sourceextent/lifetimes UNPROVED')


if __name__=='__main__':main()
