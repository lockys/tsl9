"""Offline fallback writes and complete shared dispatch-tail cleanup contracts.
Original operands/immutable CFGs and closed host integer identities only.
No target execution/emulation, mutable object/list/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_gate_source_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-fallback-tail-static.json')
ROLES=('fallback','sharedtail')
SIZES={'fallback':32,'sharedtail':278}
STARTS=({'fallback': 369214, 'sharedtail': 354238}, {'fallback': 369542, 'sharedtail': 354558})
COUNTS={'fallback': 13, 'sharedtail': 92}
HASHES=({'fallback': 'c9f3c11f23cddab788ad0e379d0a7affc0314cbcb2aad860e26c38e230eaba0f', 'sharedtail': '6ce581828abfacbadf5ddd64971c3dbb4bca00622e700f65d8a507440f4b93a4'}, {'fallback': 'c9f3c11f23cddab788ad0e379d0a7affc0314cbcb2aad860e26c38e230eaba0f', 'sharedtail': '1be1d0b910792b4ef0c2ba9774cce81b7315d32bfe26f22df4c58298229ee8a7'})
LITERALS={
'fallback':"""
000 li 15 2
002 store 10 15 21 1
004 load 15 10 272 4
008 beqz 15 28
00a li 14 7
00c store 15 14 2 1
00e load 15 10 272 4
012 load 14 10 45 1
016 li 10 0
018 store 15 14 3 1
01a jr 1
01c li 10 1
01e jr 1
""",
'sharedtail':"""
000 lui 15 536883200
004 load 14 15 1256 4
008 addi 2 2 -32
00a store 2 9 20 4
00c store 2 18 16 4
00e lui 9 536883200
012 store 2 1 28 4
014 store 2 8 24 4
016 store 2 19 12 4
018 mv 18 10
01a addi 9 9 564
01e beqz 14 156
020 mv 19 15
022 lui 15 536883200
026 load 14 15 1132 2
02a li 15 1
02c bne 14 15 156
030 load 15 9 8 2
032 load 8 18 134 2
036 load 10 10 144 4
03a mul 8 8 15
03e lui 15 999424
042 addi 14 15 575
046 addi 15 15 576
04a add 8 8 14
04c divu 8 8 15
050 bltu 10 8 224
054 lui 15 536883200
058 load 15 15 480 4
05c sub 8 10 8
060 call_indirect 1 15
062 bltu 8 10 230
066 sub 15 8 10
06a lui 14 536883200
06e load 8 14 515 1
072 load 19 19 1256 4
076 li 10 0
078 srli 8 8 1
07a bgeu 8 15 154
07e lui 10 999424
082 sub 8 15 8
086 addi 10 10 576
08a mulhu 11 8 10
08e load 12 9 8 2
090 li 13 0
092 mul 10 8 10
096 jal 1 450330
09a call_indirect 1 19
09c addi 15 0 -80
0a0 store 18 15 14 1
0a4 load 15 9 12 1
0a6 beqz 15 246
0a8 li 10 0
0aa auipc 1 536518656
0ae jalr 1 1 -222
0b2 lui 15 536883200
0b6 store 15 0 1116 4
0ba lui 15 536883200
0be load 10 15 1260 4
0c2 jal 1 278226
0c6 load 1 2 28 4
0c8 load 8 2 24 4
0ca lui 15 3758153728
0ce lui 14 33554432
0d2 store 15 14 516 4
0d6 load 9 2 20 4
0d8 load 18 2 16 4
0da load 19 2 12 4
0dc addi 2 2 32
0de jr 1
0e0 load 15 9 4 4
0e2 add 10 10 15
0e4 jump 84
0e6 sub 14 10 8
0ea li 15 0
0ec bge 14 0 106
0f0 load 15 9 4 4
0f2 add 8 8 15
0f4 jump 102
0f6 load 15 18 41 1
0fa load 8 2 24 4
0fc li 11 1
0fe load 1 2 28 4
100 load 9 2 20 4
102 load 18 2 16 4
104 load 19 2 12 4
106 sll 11 11 15
10a slli 11 11 16
10c srli 11 11 16
10e li 10 0
110 addi 2 2 32
112 jal 0 275786
""",
}
PATCHES={'fallback': {}, 'sharedtail': {4: ('load', [14, 15, 1336, 4]), 26: ('addi', [9, 9, 644]), 38: ('load', [14, 15, 1212, 2]), 88: ('load', [15, 15, 560, 4]), 110: ('load', [8, 14, 595, 1]), 114: ('load', [19, 19, 1336, 4]), 150: ('jal', [1, 450826]), 174: ('jalr', [1, 1, -542]), 182: ('store', [15, 0, 1196, 4]), 190: ('load', [10, 15, 1340, 4]), 194: ('jal', [1, 278366]), 274: ('jal', [0, 275926])}}
TYPED={'fallback': [(4, 2), (14, 2), (18, 4)], 'sharedtail': [(4, 2), (38, 5), (50, 5), (54, 2), (88, 2), (110, 4), (114, 2), (190, 2), (246, 4)]}
QK={'fallback': [(2, '5cb9', 'qk.c.sb'), (12, 'b8a3', 'qk.c.sb'), (24, 'b8b3', 'qk.c.sb')], 'sharedtail': [(48, '9e24', 'qk.c.lhu'), (142, '9224', 'qk.c.lhu'), (164, 'dc24', 'qk.c.lbu')]}
STORES={'fallback': [(2, 10, 15, 21, 1), (12, 15, 14, 2, 1), (24, 15, 14, 3, 1)], 'sharedtail': [(10, 2, 9, 20, 4), (12, 2, 18, 16, 4), (18, 2, 1, 28, 4), (20, 2, 8, 24, 4), (22, 2, 19, 12, 4), (160, 18, 15, 14, 1), (182, 15, 0, 1116, 4), (210, 15, 14, 516, 4)]}

SLICE_NAMES=('resume', 'retry', 'parentA_exit', 'parentB_exit')
SLICE_SIZES={'resume': 6, 'retry': 18, 'parentA_exit': 26, 'parentB_exit': 34}
SLICE_STARTS=({'resume': 399342, 'retry': 399260, 'parentA_exit': 367614, 'parentB_exit': 399762}, {'resume': 399576, 'retry': 399494, 'parentA_exit': 367942, 'parentB_exit': 399996})
SLICE_COUNTS={'resume': 3, 'retry': 6, 'parentA_exit': 12, 'parentB_exit': 16}
SLICE_HASHES=({'resume': '6d3d9696bb5e755c16716374964ef610e70e948a5fede9c57f116bb0d3db55b7', 'retry': '7b01b059b6d184ba2eb25e85fd9de6a06d65627c3547139dec1860067d1be48f', 'parentA_exit': '7ea5577243d497feb6bcb0f2110d6d6a846f8107acc41f56cc5f3f53f4ba5722', 'parentB_exit': '41de5b2ba1c4cb29223361988c7cce33ed1aa58374af96a419e14c36f1d0d3d9'}, {'resume': '6d3d9696bb5e755c16716374964ef610e70e948a5fede9c57f116bb0d3db55b7', 'retry': 'a9d6baec08d0a75c63b0901de96663911eaecea074ee08fb57c70bdce0c474f7', 'parentA_exit': '0c8d99403177bf6f5ea9b893fbeea58ebf92f694edae533923174a0e71cfe023', 'parentB_exit': '31130158e0dc27cd2263dbd8f8db566a82866c9fa84cb39c73c78254b284a09d'})
SLICE_LITERALS={
'resume':"""
000 load 15 8 22 1
002 bnez 15 -82
004 jump -350
""",
'retry':"""
000 load 15 8 76 1
004 andi 15 15 1
006 beq 15 0 -268
00a mv 10 8
00c jal 1 352582
010 jump -268
""",
'parentA_exit':"""
000 mv 10 8
002 load 8 2 40 4
004 load 1 2 44 4
006 load 9 2 36 4
008 load 18 2 32 4
00a load 19 2 28 4
00c load 20 2 24 4
00e load 21 2 20 4
010 load 22 2 16 4
012 load 23 2 12 4
014 addi 2 2 48
016 jal 0 354238
""",
'parentB_exit':"""
000 mv 10 8
002 load 8 2 72 4
004 load 1 2 76 4
006 load 9 2 68 4
008 load 18 2 64 4
00a load 19 2 60 4
00c load 20 2 56 4
00e load 21 2 52 4
010 load 22 2 48 4
012 load 23 2 44 4
014 load 24 2 40 4
016 load 25 2 36 4
018 load 26 2 32 4
01a load 27 2 28 4
01c addi 2 2 80
01e jal 0 354238
""",
}
SLICE_PATCHES={'resume': {}, 'retry': {12: ('jal', [1, 352902])}, 'parentA_exit': {22: ('jal', [0, 354558])}, 'parentB_exit': {30: ('jal', [0, 354558])}}
SLICE_TYPED={'resume': [], 'retry': [(0, 4)], 'parentA_exit': [], 'parentB_exit': []}


def guard(raw,role,index,selected=False):
 starts,sizes,counts,hashes,rows,patch,typed=(SLICE_STARTS,SLICE_SIZES,SLICE_COUNTS,SLICE_HASHES,SLICE_LITERALS,SLICE_PATCHES,SLICE_TYPED) if selected else (STARTS,SIZES,COUNTS,HASHES,LITERALS,PATCHES,TYPED)
 pc=starts[index][role];n=decode(raw,pc);spec={}
 for row in rows[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in patch[role]:op,v=patch[role][o]
  check(len(v)==len(FIELDS[op]),'fallbacktail literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'fallbacktail completeboundaries '+role)
 for a,f in spec.items():init.g(n,a,'fallbacktail '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(sizes[role],counts[role],hashes[index][role]),'fallbacktail completeidentity '+role)
 for o,f3 in typed[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'fallbacktail typedload')
 if not selected:
  for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'fallbacktail exactQK')
 return n


def body(raw,role,index):
 pc=STARTS[index][role];n=guard(raw,role,index);e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'fallbacktail RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal' and d['rd']==0:q=[];tails.append(dict(offset=a-pc,target=d['target']))
  elif op in ('jal','jalr','call_indirect'):
   check(d['rd']==1,'fallbacktail linkedcall');target=d.get('target')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'fallbacktail linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   elif op=='call_indirect':check(d['rs1'] in (15,19),'fallbacktail indirectregister');target='freshClockA5' if d['rs1']==15 else 'freshDelayCallbackS3'
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('ecall','mret','csr') and all(z in n for z in q),'fallbacktail closedlocalCFG');e[a]=q
 expected=[] if role=='fallback' else [(0x60,'freshClockA5'),(0x96,0x6df1a+496*index),(0x9a,'freshDelayCallbackS3'),(0xae,0x2000078a),(0xc2,0x43ed2+140*index)]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and tails==([] if role=='fallback' else [dict(offset=0x112,target=0x4354a+140*index)]),'fallbacktail exactcalls/tail')
 check(rets==([0x1a,0x1e] if role=='fallback' else [0xde]),'fallbacktail exactRETs')
 seen=set();active=set()
 def visit(a):
  check(a not in active,'fallbacktail localCFG acyclic')
  if a in seen:return
  active.add(a)
  for z in e[a]:visit(z)
  active.remove(a);seen.add(a)
 visit(pc);check(seen==set(n),'fallbacktail allreachable includingpostRET')
 check(sum(map(len,e.values()))==(12 if role=='fallback' else 97),'fallbacktail exactedgecensus')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expectedstores=[(o,b,s,v+80*index if role=='sharedtail' and o==0xb6 else v,w) for o,b,s,v,w in STORES[role]]
 check(stores==expectedstores,'fallbacktail allstores')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,local_CFG_acyclic=True,actual_callee_or_wholechain_completion_proved=False)


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
  ps=[p for z in ends if (p:=path(a,z)) is not None];check(bool(ps),'fallbacktail localexit suffix');return min(ps,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'fallbacktail all-edge witness');walks.append([a-pc for a in p])
 def countpaths(a,z=None,blocked=()):
  cache={};blocked=set(blocked)
  def f(a):
   if a in blocked:return 0
   if a==z:return 1
   if a in cache:return cache[a]
   cache[a]=(int(z is None) if not e[a] else sum(f(v) for v in e[a]));return cache[a]
  return f(a)
 preds={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:preds[z].append(a)
 def last_before(a,reg=10):
  hits=set();entry=False;todo=preds[a][:];seen=set()
  while todo:
   a=todo.pop();d=n[a-pc]
   if d.get('rd')==reg or (reg==10 and d['op'] in ('jal','jalr','call_indirect') and d['rd']==1):hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(preds[a])
  return hits,entry
 if role=='fallback':
  check(n[0]['imm']==2 and n[2]['imm']==21 and n[4]['imm']==n[0xe]['imm']==272 and n[8]['target']==pc+0x1c,'fallbacktail unconditional21/twopointers/firstguard')
  check(n[0xa]['imm']==7 and n[0xc]['rs1']==15 and n[0xc]['imm']==2 and n[0x12]['imm']==45 and n[0x18]['rs1']==15 and n[0x18]['imm']==3,'fallbacktail splitpointee stores')
  check({d['rd'] for d in n.values() if 'rd'in d}=={10,14,15} and not b['calls'] and not b['tails'],'fallbacktail noframe/SP/RA/S/call/pointerpublication')
  check(last_before(pc+0x1a)==({0x16},False) and n[0x16]['imm']==0 and last_before(pc+0x1e)==({0x1c},False) and n[0x1c]['imm']==1,'fallbacktail exactnormal0/1')
  check(countpaths(pc,pc+0x1e,blocked=[pc+2])==0 and path(pc+0xc,pc+0x1e) is None and path(pc+0x18,pc+0x1e) is None,'fallbacktail rejectedstillwrites21 butnopointeestores')
  facts=dict(frame_bytes=0,direct_P_extent=276,first_pointee_extent=3,second_pointee_extent=4,first_pointer_checked_only=True,second_pointer_reloaded_without_nullguard=True,normal_values=[0,1],every_normal_arm_writes_P21_2=True,no_local_allocation_release_or_fullpointer_store=True,indirect_store_alias_or_pointee_validity_proved=False)
 else:
  check(n[4]['imm']==n[0x72]['imm'] and n[4]['rd']==14 and n[0x72]['rd']==19 and n[0x1e]['target']==pc+0x9c and n[0x2a]['imm']==1 and n[0x2c]['target']==pc+0x9c,'fallbacktail firsthookgate vsfreshactualcallback')
  check(n[0x30]['imm']==n[0x8e]['imm']==8 and n[0x32]['imm']==134 and n[0x36]['imm']==144 and n[0x3a]['op']=='mul' and n[0x4c]['op']=='divu' and n[0x3e]['imm']+n[0x42]['imm']==999999 and n[0x3e]['imm']+n[0x46]['imm']==1000000,'fallbacktail low32ceilrequest notfull64')
  check(n[0x50]['op']=='bltu' and n[0xe0]['imm']==n[0xf0]['imm']==4 and n[0xe2]['op']=='add' and n[0x5c]['op']=='sub' and n[0x62]['op']=='bltu' and n[0xe6]['op']=='sub' and n[0xec]['op']=='bge','fallbacktail oneperiod/signedwrappedclockdelta')
  check(last_before(pc+0x60)==({0x36,0xe2},False),'fallbacktail clockreceivesheldbaseAdjusted notresidual')
  check(n[0x6e]['width']==1 and n[0x78]['imm']==1 and n[0x76]['imm']==0 and n[0x7a]['op']=='bgeu' and n[0x82]['op']=='sub' and n[0x8a]['op']=='mulhu' and n[0x92]['op']=='mul' and n[0x90]['imm']==0,'fallbacktail threshold/full64request/freshdivisor')
  check(last_before(pc+0x9a)==({0x76,0x96},False),'fallbacktail callbackA0 zerooropaquehelperreply')
  check(n[0x9c]['imm']==-80 and n[0xa0]['imm']==14 and n[0xa0]['rs1']==18 and n[0xa4]['imm']==12 and n[0xa6]['target']==pc+0xf6,'fallbacktail commonP14thenfreshD12')
  check(last_before(pc+0xae)==({0xa8},False) and n[0xa8]['imm']==0 and n[0xb6]['rs2']==0 and n[0xb6]['imm']==n[4]['imm']-140,'fallbacktail setterzero beforeB164clear')
  check(last_before(pc+0xc2)==({0xbe},False) and n[0xbe]['imm']==n[4]['imm']+4 and last_before(pc+0xde)==({0xc2},False),'fallbacktail freshservicearg andopaqueRET')
  check(n[0xca]['imm']+n[0xd2]['imm']==0xe000e204 and n[0xce]['imm']==0x02000000,'fallbacktail fixednumericcontrolstore')
  check(n[0xf6]['imm']==41 and n[0xfc]['imm']==1 and n[0x106]['op']=='sll' and n[0x10a]['imm']==n[0x10c]['imm']==16 and last_before(pc+0x112)==({0x10e},False) and n[0x10e]['imm']==0,'fallbacktail eventtask0/low16maskedshift')
  for z in ends:check(countpaths(pc,z,blocked=[pc+0xa0])==0,'fallbacktail P14store dominatesnormalexits')
  check(countpaths(pc,pc+0xde,blocked=[pc+0xb6])==0 and countpaths(pc,pc+0xde,blocked=[pc+0xd2])==0 and path(pc+0xb6,pc+0x112) is None and path(pc+0xd2,pc+0x112) is None,'fallbacktail slotclear/controlstore onlynormalRET arm')
  check(n[8]['imm']==-32 and n[0xdc]['imm']==n[0x110]['imm']==32,'fallbacktail balancedframe twoexits')
  for o,d in n.items():
   if d['op'] in ('load','store') and d['rs1']==2:check(countpaths(pc,pc+o,blocked=[pc+8])==0,'fallbacktail frameallocation dominatesSPaccess')
  check(countpaths(pc+8,pc+0xde,blocked=[pc+0xdc])==0 and countpaths(pc+8,pc+0x112,blocked=[pc+0x110])==0,'fallbacktail eachallocated exit deallocates')
  facts=dict(frame_bytes=32,direct_P_extent=148,every_normal_exit_writes_P14_176=True,D12_nonzero_arm=['matchinghooksetter(0)','B164=0','service43ed2(freshG1260)','W32[E000E204]=02000000','RET withopaqueservicereply'],D12_zero_arm=['freshP41','restoreframe','tail event(0,low16(1<<(j&31)))'],D12zero_has_no_direct_B164_clear=True,delay_callback_slot_is_not_registered_hook_slot=True,no_local_release_request_or_pointer_lifetime_proof=True)
 check(countpaths(pc)==(2 if role=='fallback' else 28),'fallbacktail exactDAGpathcensus')
 selected=[c['offset'] for c in b['calls']+b['tails']]+[d['pc']-pc for d in b['instructions'] if d['op']=='store' and d['rs1']!=2]
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),all_local_DAG_path_count=countpaths(pc),exit_syntactic_path_counts={hex(a-pc):countpaths(pc,a) for a in ends},selected_entry_exit_walks={hex(o):[v-pc for v in path(pc,pc+o)+finish(pc+o)[1:]] for o in selected},facts=facts,walks_not_feasibleinputs_or_runtimeprogress=True)


def slice_guard(raw,role,index):
 pc=SLICE_STARTS[index][role];n=guard(raw,role,index,True);e={};frontier=set();calls=[];tails=[]
 for a,d in n.items():
  q=[a+d['size']]
  if d['op'] in BRANCHES:q.append(d['target'])
  elif d['op']=='jump':q=[d['target']]
  elif d['op']=='jal':
   if d['rd']==0:q=[];tails.append(d['target'])
   else:check(d['rd']==1,'fallbacktail selectedlinkedcall');calls.append(d['target'])
  e[a]=q;frontier.update(z for z in q if z not in n)
 if role=='resume':check(n[pc]['imm']==22 and n[pc+2]['rs1']==15 and n[pc+2]['target']==SLICE_STARTS[index]['retry'],'fallbacktail freshP22 controlsresume notreply')
 elif role=='retry':check(n[pc]['imm']==76 and n[pc+4]['imm']==1 and calls==[0x56146+320*index] and n[pc+10]['op']=='mv' and n[pc+10]['rd']==10 and n[pc+10]['rs2']==8,'fallbacktail freshP76bit0 retry(P)')
 else:
  check(n[pc]['op']=='mv' and n[pc]['rd']==10 and n[pc]['rs2']==8 and tails==[STARTS[index]['sharedtail']],'fallbacktail parentepilogue holdsP thenunlinked sharedtail')
  sp=[d for d in n.values() if d.get('rd')==2];check(len(sp)==1 and sp[0]['imm']==(48 if role=='parentA_exit' else 80),'fallbacktail outerframe restored before new32frame')
 return dict(start=pc,bytes=len(raw),sha256=SLICE_HASHES[index][role],instructions=list(n.values()),selected_CFG=e,outside_window_frontier=sorted(frontier),calls=calls,tails=tails,complete_parent_function_claim=False)


def unused_fallback_reply(data,index,mem):
 pc=previous.PARENT_STARTS[index][1];raw=init.binding.take(data,pc,2280);check(sparse.captured(mem,pc,2280)==raw,'fallbacktail parentB fullstrictHEX');parent=previous.parent_census(raw,index,1);n=decode(raw,pc);start=0x617de+234*index
 seen=set();todo=[start];kills=set();uses=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  seen.add(a);d=n[a];op=d['op']
  if d.get('rs1')==10 or d.get('rs2')==10 or (op in ('jal','jalr','call_indirect')):uses.append(a-pc);continue
  if d.get('rd')==10:kills.add(a-pc);continue
  qs=[a+d['size']]
  if op in BRANCHES:qs.append(d['target'])
  elif op=='jump':qs=[d['target']]
  check(all(z in n for z in qs),'fallbacktail replydefuse staysinparent');todo.extend(qs)
 check(not uses and kills=={0x49e,0x572},'fallbacktail calleroldreply killed before anylocalread/opaque call')
 return dict(parent_identity=parent,start=start,A0_kill_offsets=sorted(kills),possible_A0_reads_or_calls_before_kill=uses,static_liveness_only=True,no_parent_loopprogress_or_other_semantics_proved=True)


def reused_services(data,index,mem):
 import check_v4160_hook_lifetime_static as hook
 import check_v4160_linked_node_consumer_static as event
 import check_v4160_registration_return_chain_static as arithmetic
 hs,delta,sh,_=hook.DETAILS[index];hr=init.binding.take(data,hs,22);check(sparse.captured(mem,hs,22)==hr,'fallbacktail setterfullHEX');hb=hook.body(hr,'setter',0x2000078a,delta,sh)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+0x2000078a-int(fc['destination'],16)==hs and 0x2000078a+22<=int(mapping['first_copy_end_exclusive'],16),'fallbacktail setterfullfirstcopy')
 ep=0x4354a+140*index;er=init.binding.take(data,ep,64);check(sparse.captured(mem,ep,64)==er,'fallbacktail eventfullHEX');eb=event.event_body(er,ep,0x2000319c+80*index,event.DETAILS[index][3])
 ap=0x6df1a+496*index;ar=init.binding.take(data,ap,914);check(sparse.captured(mem,ap,914)==ar,'fallbacktail arithmeticfullHEX');ab=arithmetic.arithmetic(ar,ap)
 slot=0x20003000+delta;delay_slot=0x20003000+1256+80*index;current=0x200033b8+80*index+164
 check(len({slot,slot+4,delay_slot,current})==4,'fallbacktail distinctcallback/currentobjectcells')
 return dict(setter=dict(source=hs,target=0x2000078a,bytes=22,sha256=hb['sha256'],registered_hook_slot=slot,adjacent_flag=slot+4,zero_argument_clears_pointer_not_flag=True),event=dict(start=ep,bytes=64,sha256=eb['sha256'],task0_normal_values=[0,3],task0_success_requires_fresh_count_nonzero=True,no_local_callback_or_release_call=True),arithmetic=dict(start=ap,bytes=914,sha256=ab['sha256'],new_domain_quotient_or_zero_divisor_behaviour_proved=False),delay_callback_slot=delay_slot,current_object_slot=current,actual_installedbindings_or_inflight_callback_quiescence_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'fallbacktail completebody strictHEX');bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()};slices={}
 for role in SLICE_NAMES:
  pc=SLICE_STARTS[index][role];raw=init.binding.take(data,pc,SLICE_SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'fallbacktail selectedslice strictHEX');slices[role]=slice_guard(raw,role,index)
 dp=previous.STARTS[index]['dispatchB'];dr=init.binding.take(data,dp,64);check(sparse.captured(mem,dp,64)==dr,'fallbacktail reusedcallwindow HEX');db=previous.window(dr,'dispatchB',index);dn={d['pc']-dp:d for d in db['instructions']}
 check(next(c['target'] for c in db['calls'] if c['offset']==0x2c)==bs['fallback']['start'] and dn[0x30]['target']==slices['resume']['start'],'fallbacktail exactcaller/helper/postreturn joins')
 source=previous.source_joins(init.binding.APP.read_bytes(),data,hexraw,index,mem);check(source['key_allocated_other_buffer_field']==272 and source['key_object_field']==276,'fallbacktail allocationfield distinctfromRXsource')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,selected_parent_windows=slices,reused_caller=dict(start=dp,bytes=64,sha256=db['sha256']),reply_liveness_certificate=unused_fallback_reply(data,index,mem),reused_services=reused_services(data,index,mem),reused_buffer_publication=source,
  contracts=['fallback unconditionalP21=2;firstX0=U32P272 null->1;nonnull SB X0+2=7,thenfreshX1=U32P272,freshP45,SB X1+3=low8P45,return0. Firstguard doesnotcheck secondpointer;firststore mayalias P272/P45. No localcalls/frame/free/fullpointerstore. Matchingstableupstream64..260 allocationcanfit4bytes,notactualextent/livenessproof',
   'parentB fallbackreply killed before anylocalA0read/opaque call;freshP22 thenfreshP76bit0 decides selectedretry56146/56286(P),neithercallee reply determines selectedbranch. Afterwards joinenterslargerparentloops,notdirectguaranteedtail. Bothparentepilogues retainP asA0 andrestore48/80frames beforeunlinkedsharedtail allocating32',
   'sharedtail H0=G1256/1336 gate andmodeG1132/1212==1 selectoptionalclock/delaycallback. q=floor(low32(U16P134*U16D8+999999)/1e6);baseP144<q addsfreshD4once. C=low32(adjustedbase-q);clockA0 receivesadjustedbase',
   'clockreplyT opaque:unsignedC>=T ->C-T;else signed low32(T-C)>=0 ->0;else addfreshD4once thenC-T. Freshthreshold=U8G515/595>>1;freshH1 samedelaycallbackslotmaydifferfromH0;R<=threshold passesA0=0,elsehelper full64(R-threshold)*1e6 dividedbyfreshU16D8 request thenopaqueA0 toH1. NoH1nullrecheck/newdomainquotient/physicaltime ormodnormalization proof',
   'everyordinarylocalexit firstSB P14=176 thenfreshU8D12. Nonzero:matchedhooksetter(0) clearsregisteredhookpointer butnotadjacentflag;thenlocalB164=0,freshG1260->service43ed2/43f5e,A0replypropagatedthroughfixednumericstoreE000E204=02000000 andRET. Delaycallbackslot differs registeredhookslot',
   'D12zero:nodirectB164clear orfixednumericstore;freshj=U8P41;restore32frame;tail event(0,low16(1<<(j&31))). Matchingevent normal0/3 basedfreshcount>0,zero maskdoesnotguardeventpointer. Noapplicationcallback/free inmatched eventleaf,notwholechaindisposal/ownershipproof',
   'pointerclears arepublicationchanges notfree,callbackdrainingorownershiptransfer. Opaque clock/delaycallback/service43ed2 andsourcewriters mayretain/modify/release objects;validframe/object/pointees/actualbindings/inflightcallbacks/fullnodeconsumption-lifetimes remain'],actual_binding_object_identity_extent_inflightcallbacks_release_and_complete_lifetime_proved=False)


def domains():
 cases=0
 for h in range(65536):
  for k in (0,1,32768,65535):
   product=h*k;raw=(product+999999)&0xffffffff;q=raw//1000000;check(product<=0xffffffff and 0<=q<=4294,'fallbacktail sampledK/allh unsignedq bounds');cases+=1
 check(((65535*65535+999999)&0xffffffff)==868928 and 868928//1000000==0,'fallbacktail closedwrap witness notactualrecord')
 for j in range(256):
  s=j&31;mask=(1<<s)&65535;check((mask==0)==(s>=16) and (mask==0 or mask.bit_count()==1),'fallbacktail low5shift/low16eventmask')
 for v in range(256):check(0<=v>>1<=127,'fallbacktail thresholdbyte halfrange')
 check(0xffffffff*1000000<2**52 and (0xffffffff*1000000)>>32==999999,'fallbacktail high/lowfullnumerator interval')
 for d in (1,0x7fffffff,0x80000000,0xffffffff):
  signed=d if d<0x80000000 else d-(1<<32)
  check((signed>=0)==(d<0x80000000),'fallbacktail wrappedpositive difference signedbit boundary')
 check(64<=260 and 4<=64 and 148==144+4 and 276==272+4,'fallbacktail requirednumericextents only')
 return dict(q_family_cases=cases,K_samples=[0,1,32768,65535],all_U16_h_in_each_family=True,q_interval=[0,4294],closed_wrap_witness={'h':65535,'K':65535,'wrapped_numerator':868928,'q':0},witness_is_not_reachable_object_or_runtime_observation=True,threshold_interval=[0,127],event_index_cases=256,event_mask_zero_if_low5_index16to31=True,full_requested_numerator_max=0xffffffff*1000000,actualsource_or_complete_clockprogress_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-fallback-and-complete-shared-tail-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_complete_body_bytes=620,new_complete_body_instructions=210,selected_previously_censused_parent_bytes=168,selected_parent_instruction_guards=74,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['actualP272allocation/secondreload identity/aliasing/sourceextent','actualparentreachability/retry56146/56286 and43ed2/service sideeffects','actualclock/delaycallback/registeredhookbinding,inflightcallbacks,publicationclear-vs-free/fullownership'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for selected,roles,starts,sizes,typedmap in ((False,ROLES,STARTS,SIZES,TYPED),(True,SLICE_NAMES,SLICE_STARTS,SLICE_SIZES,SLICE_TYPED)):
   for role in roles:
    pc=starts[i][role];raw=init.binding.take(data,pc,sizes[role]);n=guard(raw,role,i,selected)
    for d in n.values():
     o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
     try:guard(bad,role,i,selected)
     except RuntimeError:pass
     else:raise RuntimeError('fallbacktail instructionmutation escaped')
     mutated+=1
    for o,_ in typedmap[role]:
     bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
     try:guard(bad,role,i,selected)
     except RuntimeError:pass
     else:raise RuntimeError('fallbacktail typedmutation escaped')
     typed+=1
 check((mutated,typed)==(284,26),'fallbacktail mutationcensus')
 print('PASS:284 instruction/26 typed-load mutations rejected;complete fallback/sharedtail and selected joins')


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
 else:check(OUT.read_bytes()==encoded,'fallbacktail exactledger replay')
 print('PASS:620B/210i complete bodies+168B/74i parent joins;strictHEX;callback/current-slot/event contracts;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/aliasing/ingresslength/full ownership-lifetimes UNPROVED')


if __name__=='__main__':main()
