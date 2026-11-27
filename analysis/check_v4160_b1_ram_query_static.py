"""Offline complete mapped query and borrowed output initialization contracts.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable frame/object/clock/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_ram_record_callback_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-ram-query-static.json')
ENTRY=0x20001122
SOURCES=(0x41392,0x413d2)
SIZE=620
COUNT=196
HASHES=('f47b72fc04b007332db9c78181bbb3b7d0792633b788d862291a97eab16f947e', 'd23a270456fb3aa70120adfaec7fe698b7f072c4fd75d35beb5a7678d78de6a5')
LITERAL="""
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 18 16 4
006 store 2 19 12 4
008 store 2 1 28 4
00a store 2 9 20 4
00c store 2 20 8 4
00e store 2 21 4 4
010 store 2 22 0 4
012 load 14 10 11 1
014 li 15 1
016 mv 8 10
018 mv 18 11
01a load 19 10 144 4
01e bne 14 15 520
022 load 15 10 128 2
026 load 22 10 60 2
02a lui 20 536883200
02e addi 13 20 564
032 load 21 13 8 2
036 addi 20 20 564
03a bgeu 15 22 472
03e load 13 10 16 1
040 bne 13 14 472
044 load 14 10 280 4
048 bne 14 0 472
04c load 14 10 164 4
050 bne 14 0 472
054 load 13 10 15 1
056 li 14 7
058 bne 13 14 472
05c load 10 10 58 2
05e sub 22 22 15
062 addi 15 0 1250
066 mul 10 10 22
06a load 9 8 148 4
06e lui 12 999424
072 addi 12 12 576
076 li 13 0
078 mul 10 10 15
07c lui 15 536883200
080 load 15 15 514 1
084 divu 9 10 9
088 mulhu 11 21 10
08c add 9 9 15
08e slli 9 9 16
090 srli 9 9 16
092 store 8 9 134 2
096 mul 10 21 10
09a auipc 1 3758542848
09e jalr 1 1 -674
0a2 add 19 19 10
0a4 sltu 10 19 10
0a8 add 10 10 11
0aa mv 14 19
0ac load 15 20 4 4
0b0 bnez 10 182
0b2 bltu 19 15 186
0b6 sub 14 19 15
0ba mul 9 9 21
0be lui 13 999424
0c2 addi 15 13 575
0c6 addi 13 13 576
0ca store 18 14 0 4
0ce add 9 9 15
0d0 divu 9 9 13
0d4 slli 15 22 1
0d8 add 15 15 9
0da bltu 14 15 460
0de sub 14 14 15
0e0 store 18 14 0 4
0e4 lui 19 536883200
0e8 load 15 19 480 4
0ec load 9 18 0 4
0f0 call_indirect 1 15
0f2 bltu 9 10 526
0f6 sub 10 9 10
0fa bge 10 0 436
0fe load 15 19 480 4
102 lui 22 536883200
106 addi 22 22 564
10a call_indirect 1 15
10c load 14 18 0 4
110 bltu 10 14 538
114 sub 10 10 14
116 load 15 8 62 2
118 load 14 22 8 2
11c slli 15 15 3
11e mul 15 15 14
122 addi 14 0 800
126 addi 15 15 400
12a divu 15 15 14
12e bltu 15 10 548
132 lui 20 999424
136 addi 21 20 575
13a addi 20 20 576
13e load 15 8 64 2
142 addi 15 15 1
144 store 8 15 64 2
148 load 15 8 320 1
14c bnez 15 338
14e mv 10 8
150 jal 1 536876230
152 mv 10 8
154 auipc 1 3758444544
158 jalr 1 1 1788
15c bnez 10 574
15e load 13 8 144 4
162 load 15 8 140 4
166 load 14 22 4 4
16a add 15 15 13
16c mv 10 15
16e bltu 15 13 374
172 bltu 15 14 378
176 sub 10 15 14
17a load 15 8 31 1
17c load 9 8 134 2
180 store 8 10 144 4
184 addi 15 15 1
186 store 8 15 31 1
188 load 15 22 8 2
18c mul 9 9 15
190 add 9 9 21
192 divu 9 9 20
196 bltu 10 9 604
19a sub 9 10 9
19e load 15 19 480 4
1a2 store 18 9 0 4
1a6 call_indirect 1 15
1a8 bltu 9 10 612
1ac sub 10 9 10
1b0 blt 10 0 318
1b4 lui 15 536883200
1b8 load 15 15 515 1
1bc bltu 15 10 576
1c0 lui 15 536883200
1c4 store 15 8 1116 4
1c8 li 10 0
1ca jump 576
1cc load 13 20 4 4
1d0 sub 15 13 15
1d4 add 14 14 15
1d6 jump 224
1d8 load 15 8 134 2
1dc lui 14 999424
1e0 mul 9 15 21
1e4 addi 15 14 575
1e8 add 15 15 9
1ea addi 9 14 576
1ee divu 9 15 9
1f2 bltu 19 9 512
1f6 sub 9 19 9
1fa store 18 9 0 4
1fe jump 228
200 load 15 20 4 4
204 add 19 19 15
206 jump 502
208 store 11 19 0 4
20c jump 228
20e lui 15 536883200
212 load 15 15 568 4
216 add 9 9 15
218 jump 246
21a load 15 22 4 4
21e sub 15 15 14
220 add 10 10 15
222 jump 278
224 li 11 8
226 mv 10 8
228 auipc 1 3758444544
22c jalr 1 1 1452
230 store 8 10 43 1
234 lui 15 536883200
238 load 15 15 544 4
23c bnez 15 596
23e li 10 -1
240 load 1 2 28 4
242 load 8 2 24 4
244 load 9 2 20 4
246 load 18 2 16 4
248 load 19 2 12 4
24a load 20 2 8 4
24c load 21 2 4 4
24e load 22 2 0 4
250 addi 2 2 32
252 jr 1
254 li 11 2
256 li 10 5
258 call_indirect 1 15
25a jump 574
25c sub 9 14 9
260 add 9 9 10
262 jump 414
264 load 15 22 4 4
268 add 9 9 15
26a jump 428
"""
PATCH={46: ('addi', [13, 20, 644]), 54: ('addi', [20, 20, 644]), 128: ('load', [15, 15, 594, 1]), 158: ('jalr', [1, 1, -178]), 232: ('load', [15, 19, 560, 4]), 254: ('load', [15, 19, 560, 4]), 262: ('addi', [22, 22, 644]), 340: ('auipc', [1, 3758448640]), 344: ('jalr', [1, 1, -1988]), 414: ('load', [15, 19, 560, 4]), 440: ('load', [15, 15, 595, 1]), 452: ('store', [15, 8, 1196, 4]), 530: ('load', [15, 15, 648, 4]), 556: ('jalr', [1, 1, 1772]), 568: ('load', [15, 15, 624, 4])}
TYPED=[(26, 2), (34, 5), (38, 5), (50, 5), (68, 2), (76, 2), (106, 2), (128, 4), (172, 2), (232, 2), (236, 2), (254, 2), (268, 2), (280, 5), (318, 5), (328, 4), (350, 2), (354, 2), (358, 2), (380, 5), (392, 5), (414, 2), (440, 4), (460, 2), (472, 5), (512, 2), (530, 2), (538, 2), (568, 2), (612, 2)]
QK=[(18, '3835', 'qk.c.lbu'), (62, '1429', 'qk.c.lbu'), (84, '7435', 'qk.c.lbu'), (92, '2a3d', 'qk.c.lhu'), (278, '7e3c', 'qk.c.lhu'), (378, '7c3c', 'qk.c.lbu'), (390, '7cbc', 'qk.c.sb')]
STORES=[(2, 2, 8, 24, 4), (4, 2, 18, 16, 4), (6, 2, 19, 12, 4), (8, 2, 1, 28, 4), (10, 2, 9, 20, 4), (12, 2, 20, 8, 4), (14, 2, 21, 4, 4), (16, 2, 22, 0, 4), (146, 8, 9, 134, 2), (202, 18, 14, 0, 4), (224, 18, 14, 0, 4), (324, 8, 15, 64, 2), (384, 8, 10, 144, 4), (390, 8, 15, 31, 1), (418, 18, 9, 0, 4), (452, 15, 8, 1116, 4), (506, 18, 9, 0, 4), (520, 11, 19, 0, 4), (560, 8, 10, 43, 1)]


def specs(index):
 out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCH:op,v=PATCH[o]
  check(len(v)==len(FIELDS[op]),'RAMquery literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=ENTRY
  out[ENTRY+o]=f
 return out


def body(raw,index):
 pc=ENTRY;n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'RAMquery completeboundaries')
 for a,f in s.items():init.g(n,a,'RAMquery operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNT,HASHES[index]),'RAMquery completeidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'RAMquery typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'RAMquery exactQK')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];qs=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'RAMquery RET RA');qs=[];rets.append(a-pc)
  elif op in BRANCHES:qs.append(d['target'])
  elif op=='jump':qs=[d['target']]
  elif op in ('jal','jalr','call_indirect'):
   check(d['rd']==1,'RAMquery allcallslinked');target=d.get('target','freshA5')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'RAMquery linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   elif op=='call_indirect':check(d['rs1']==15,'RAMquery loadedA5 call')
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('ecall','mret','csr') and all(z in n for z in qs),'RAMquery closedCFG');e[a]=qs
 expected=[(0x9e,0x6df1a+496*index),(0xf0,'freshA5'),(0x10a,'freshA5'),(0x150,0x200014c6),(0x158,0x56972+320*index),(0x1a6,'freshA5'),(0x22c,0x568f6+320*index),(0x258,'freshA5')]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[0x252],'RAMquery all8calls/soleRET')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'RAMquery fullreachability includingpostRET')
 common=previous.previous.previous.previous.previous.previous.previous.previous.previous.dispatch.common;groups=common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]];check(len(cycles)==1,'RAMquery oneupdate SCC')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];expectedstores=[tuple((*v[:3],v[3]+80*index,v[4])) if v[0]==0x1c4 else v for v in STORES]
 check(stores==expectedstores and len(stores)==19 and len(TYPED)==30 and len(QK)==7,'RAMquery store/typed/QK census')
 return dict(start=pc,source=SOURCES[index],bytes=SIZE,sha256=HASHES[index],instructions=list(n.values()),CFG=e,local_CFG=e,cyclic_SCCs=cycles,calls=calls,returns=rets,stores=stores,complete_local_body=True,actual_clock_callee_or_whole_return_proved=False)


def reachable(e,start,blocked=()):
 seen=set();todo=[start];blocked=set(blocked)
 while todo:
  a=todo.pop()
  if a not in seen and a not in blocked:seen.add(a);todo.extend(e[a])
 return seen


def certificates(b,index):
 pc=ENTRY;e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']}
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  raise RuntimeError('RAMquery no syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,pc+0x252)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'RAMquery all-edge witness');walks.append([a-pc for a in p])
 writes=[o for o,d in n.items() if d['op']=='store' and d['rs1'] in (11,18)]
 check(writes==[0xca,0xe0,0x1a2,0x1fa,0x208] and all(n[o]['imm']==0 and n[o]['width']==4 for o in writes),'RAMquery all5 Outword stores')
 frontier=[0xe0,0x1fa,0x208];seen=reachable(e,pc,{pc+o for o in frontier})
 protected=[0xec,0xf0,0x10a,0x10c,0x1a6,0x252]
 check(all(pc+o not in seen for o in protected),'RAMquery outputstore cut before reads/clocks/RET')
 check([o for o,d in n.items() if d.get('rd')==18]==[0x18,0x246] and n[0x18]['rs2']==11,'RAMquery heldOut initial/restore only')
 branch208=path(pc,pc+0x208);check(not any(n[a-pc].get('rd')==11 or n[a-pc]['op'] in ('jal','jalr','call_indirect') for a in branch208),'RAMquery alternateA1 isoriginalOut')
 check(n[0x208]['rs1']==11 and n[0x208]['rs2']==19 and n[0x1a]['imm']==144 and n[0x1a]['rd']==19,'RAMquery modealternate storescapturedP144')
 check(n[0x12]['imm']==11 and n[0x14]['imm']==1 and n[0x1e]['target']==pc+0x208,'RAMquery firstmodegate')
 check(n[0x22]['imm']==128 and n[0x26]['imm']==60 and n[0x3a]['op']=='bgeu' and n[0x3a]['target']==pc+0x1d8 and n[0x40]['target']==n[0x48]['target']==n[0x50]['target']==n[0x58]['target']==pc+0x1d8,'RAMquery recalcgate fallbackjoin')
 check(n[0x3e]['imm']==16 and n[0x40]['rs2']==14 and n[0x44]['imm']==280 and n[0x4c]['imm']==164 and n[0x54]['imm']==15 and n[0x56]['imm']==7,'RAMquery exactspecialgatefield reads')
 check(n[0x5c]['imm']==58 and n[0x62]['imm']==1250 and n[0x66]['op']==n[0x78]['op']=='mul' and n[0x6a]['imm']==148 and n[0x84]['op']=='divu' and n[0x92]['imm']==134,'RAMquery wrappedproduct/DIVUzero/no denominatorguard')
 check(n[0x88]['op']=='mulhu' and n[0x96]['op']=='mul' and n[0x88]['rs1']==n[0x96]['rs1']==21 and n[0x76]['imm']==0 and n[0x6e]['imm']+n[0x72]['imm']==1000000,'RAMquery full64pair ofcapturedK andwrappedN')
 check(n[0xa4]['op']=='sltu' and n[0xa8]['op']=='add' and n[0xb0]['rs1']==10 and n[0xb2]['op']=='bltu' and n[0xb6]['op']=='sub','RAMquery opaquehelperreply/highcarry/onesubtraction')
 check(n[0xc2]['imm']+n[0xbe]['imm']==n[0x1e4]['imm']+n[0x1dc]['imm']==999999 and n[0xc6]['imm']+n[0xbe]['imm']==n[0x1ea]['imm']+n[0x1dc]['imm']==1000000,'RAMquery three scalerconstants')
 check(n[0xf2]['op']=='bltu' and n[0xfa]['op']=='bge' and n[0x1b0]['op']=='blt' and n[0x1b0]['target']==pc+0x13e,'RAMquery unsignedfixup vs signedloop')
 check(n[0x110]['op']=='bltu' and n[0x11c]['imm']==3 and n[0x122]['imm']==800 and n[0x126]['imm']==400 and n[0x12e]['target']==pc+0x224,'RAMquery widegapthreshold/action')
 check(n[0x13e]['imm']==n[0x144]['imm']==64 and n[0x142]['imm']==1 and n[0x148]['imm']==320 and n[0x14c]['target']==pc+0x152,'RAMquery U16counter/optionalcall')
 check(n[0x15c]['target']==pc+0x23e and n[0x180]['imm']==144 and n[0x17a]['imm']==n[0x186]['imm']==31 and n[0x184]['imm']==1,'RAMquery childnonzero minus1/updateP144/P31')
 check(n[0x1c4]['rs2']==8 and n[0x1c4]['imm']+n[0x1c0]['imm']==0x2000345c+80*index and n[0x1c8]['imm']==0,'RAMquery Ppublication before forced0')
 check(n[0x230]['imm']==43 and n[0x224]['imm']==8 and n[0x238]['imm']==544+80*index and n[0x254]['imm']==2 and n[0x256]['imm']==5 and n[0x23e]['imm']==-1,'RAMquery action8/optionalhook5,2/forcedminus1')
 check(not any(d.get('rd')==10 for o,d in n.items() if 0x240<=o<=0x252),'RAMquery epilogue preservesR')
 preds={a:set() for a in e}
 for a,qs in e.items():
  for q in qs:preds[q].add(a)
 check(preds[pc+0x1b4]=={pc+0xfa,pc+0x1b0} and e[pc+0xfa][1]==e[pc+0x1b0][0]==pc+0x1b4 and n[0xfa]['rs1']==n[0x1b0]['rs1']==10 and n[0xfa]['rs2']==n[0x1b0]['rs2']==0,'RAMquery terminalresidual signednonnegative enteringthreshold')
 check(n[0x1bc]['rs2']==10 and n[0x1bc]['target']==pc+0x240 and not any(d.get('rd')==10 for o,d in n.items() if 0x1b4<=o<=0x1bc),'RAMquery ordinarypositive R preserved ifaboveU8threshold')
 points=[0xca,0xe0,0x1fa,0x208,0xf0,0x10a,0x13e,0x150,0x158,0x1a2,0x1a6,0x1c4,0x1c8,0x22c,0x230,0x23e,0x258]
 check(len(walks)==218 and len(points)==17,'RAMquery full edge/path census')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks={hex(o):[a-pc for a in path(pc,pc+o)+path(pc+o,pc+0x252)[1:]] for o in points},cyclic_SCC_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']],all_output_store_offsets=writes,initial_output_store_cut=frontier,cut_unreachable_offsets=protected,all_normal_entry_RET_paths_cross_initial_output_store=True,normal_R_domain=dict(forced=[0,4294967295],ordinary_positive_interval=[1,2147483647]),object_explicit_extent=321,output_writable_extent=4,frame_bytes=32,query_pointer_nonretention_or_lastwriter_stability_proved=False)


def domains():
 for h in range(65536):
  for d in (1,65535):
   n=(h*d*1250)&0xffffffff;check(h*d<2**32 and n==(h*d*1250)%2**32,'RAMquery recalc two lowword products')
   for k in (0,1,65535):check(n*k<2**48 and ((n*k>>32)<<32)+(n*k&0xffffffff)==n*k,'RAMquery helper request fullpair')
 for byte in range(256):check((0xffffffff+byte)&65535==(byte-1)&65535,'RAMquery DIVUzero plusbyte low16')
 maxp=65535*65535;check(maxp<2**32 and maxp+999999>0xffffffff and ((maxp+999999)&0xffffffff)//1000000==0,'RAMquery ceiling overflow witness')
 for h in range(65536):
  check((h+1)&65535==(h+1)%65536,'RAMquery U16counter wrap')
 for c in range(256):check((c+1)&255==(c+1)%256,'RAMquery bytecounter wrap')
 # Child reply words stay opaque; only scalar word/carry/subtract identities.
 family=(0,1,0x7fffffff,0x80000000,0xffffffff)
 pairs=0
 for base in family:
  for lo in family:
   low=(base+lo)&0xffffffff;carry=int(low<lo);check(carry==int(base+lo>0xffffffff),'RAMquery lowadd carry')
   for high in family:
    h=(high+carry)&0xffffffff;check(0<=h<=0xffffffff,'RAMquery highreplycarry also wraps');pairs+=1
 check(((0xffffffff+1)&0xffffffff)==0,'RAMquery highcarry cannot imply fullwide nonzero')
 check(32+12==44 and set(range(44,48)).isdisjoint(range(32)),'RAMquery callerSP12 outside32B queryframe')
 return dict(recalc_H_delta_family_cases=131072,delta_samples=[1,65535],allH16=True,helper_pair_family_cases=393216,K_samples=[0,1,65535],DIVU_zero_word=4294967295,DIVUzero_byte_cases=256,counter16_cases=65536,counter8_cases=256,opaque_reply_carry_family_cases=pairs,whole_clock_or_object_state_executed=False,arithmetic_reply_quotient_or_physicaltime_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16);source=SOURCES[index];raw=init.binding.take(data,source,SIZE)
 check(src+ENTRY-dest==source and dest<=ENTRY and ENTRY+SIZE<=end and sparse.captured(mem,source,SIZE)==raw,'RAMquery completefirstcopy/strictHEX');b=body(raw,index);cert=certificates(b,index);n={d['pc']-ENTRY:d for d in b['instructions']}
 callers={}
 for role in previous.ROLES:
  cp=previous.STARTS[role];cs=previous.SOURCES[index][role];cr=init.binding.take(data,cs,previous.SIZES[role]);check(sparse.captured(mem,cs,len(cr))==cr and src+cp-dest==cs and cp+len(cr)<=end,'RAMquery caller fullfirstcopy/HEX');cb=previous.body(cr,role,index);cn={d['pc']-cp:d for d in cb['instructions']}
  calloff,argoff=(0xc,4) if role=='record' else (0x5c,0x58)
  check(next(c['target'] for c in cb['calls'] if c['offset']==calloff)==ENTRY and cn[argoff]['rs1']==2 and cn[argoff]['imm']==12,'RAMquery exactborrowedframe join '+role)
  callers[role]=dict(start=cp,bytes=cb['bytes'],sha256=cb['sha256'],caller_SP_offset=12,query_SP_offset=44,conditional_initial_output_store_cut=cert['initial_output_store_cut'],lastwriter_or_actualinitialization_not_unconditional=True)
 # Query's forced-zero handoff joins the existing mapped callback's fresh object load.
 import check_v4160_ram_callback_prefix_static as prefix
 detail=prefix.DETAILS[index];ps=detail[0];pr=init.binding.take(data,ps,82);check(sparse.captured(mem,ps,82)==pr and src+0x20000d50-dest==ps and 0x20000d50+82<=end,'RAMquery handoff prefix fullfirstcopy/HEX');pb=prefix.window(pr,'prefix',0x20000d50,detail,detail[4][0]);pn={d['pc']-0x20000d50:d for d in pb['instructions']}
 check(pn[4]['imm']+pn[8]['imm']+pn[14]['imm']==n[0x1c0]['imm']+n[0x1c4]['imm']==0x2000345c+80*index and pn[14]['rd']==8,'RAMquery forcedzero P->global->freshcleanupP')
 import check_v4160_registration_return_chain_static as arith
 ap=0x6df1a+496*index;ar=init.binding.take(data,ap,914);check(sparse.captured(mem,ap,914)==ar,'RAMquery arithmetic fullstrictHEX');ab=arith.arithmetic(ar,ap)
 # P8 action is the already complete threshold leaf, not an invented status ABI.
 import check_v4160_threshold_message_static as threshold
 tp=threshold.STARTS[index][0];tr=init.binding.take(data,tp,124);check(sparse.captured(mem,tp,124)==tr,'RAMquery threshold fullstrictHEX');th=threshold.body(tr,'threshold',index)
 check(b['calls'][6]['target']==tp and n[0x224]['imm']==8 and n[0x226]['rs2']==8,'RAMquery exactaction(P,8)join')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=cert,reused_callers=callers,reused_callback_prefix=dict(target=0x20000d50,source=ps,bytes=82,sha256=detail[4][0],complete_function=False,object_pointer_global=0x2000345c+80*index),reused_arithmetic=dict(start=ap,bytes=914,sha256=ab['sha256'],new_operand_domain_quotient_proved=False),reused_threshold=dict(start=tp,bytes=124,sha256=th['sha256']),
  contracts=['Out=entryA1 heldS2,exact5wordstore sites;frontierE0/1FA/208 cutsallRET andfirstoutputread/clockcalls;P11!=1 directlystorescapturedP144,othermode1 branches computeandstorebeforecommonclock. No localP/Outnullguards',
   'thisconditionally closes callerSP12preinitgap foractualmatchingqueryordinaryreturn/validOut/frame/callee/code/aliaspreservation;notlastwriterstability,unknownretention orblanket semanticcontentproof',
   'mode1 recalcgates P128<P60,P16=1,P280=0,P164=0,P15=7;elsefallbackscaledP134 fromcapturedQ8. RecalcN=low32(U16P58*(P60-P128)*1250),DIVU byU32P148 nozeroguard,low16(quotient+freshbyte)->P134',
   'helperrequest pair=capturedU16Q8*N over1000000;actualreplywords opaque. AddcapturedP144+replylow,carry+replyhigh wraps;subtractfreshQ4onceifhighnonzero orlow>=Q4. InterimOutthenadjustedOut;not fullmodnormalization',
   'firstclockloadthenOutreadthenindirectcall;independentfreshclock andfreshOut later. Signed residual decidesrepeat;P64/P31wrap,P144onesubtractupdate,optionalRAM200014c6(P),linked56972/56ab2(P)nonzero->forcedffffffff. No finiteprogressbound',
   'terminalthreshold enteronlysignednonnegative residual;unsignedresidual>freshbyte returns1..7fffffff;elsepublishheldP atG1116/G1196 thenforce0. Largegapaction(P,8)->P43low8,optionalfreshhook(5,2),forceffffffff regardlesshookreply',
   'recordcaller R0 immediatelyrequests20000d50 whichfreshloads samepublishedglobal asP;selectorR0 publishes20000d50 throughsetter forlaterroute. Sameaddress notunconditionalsameobject/lifetime acrosswriters/asyncorder',
   'localOutwordwrites do notexclude callee seeingOut viaambientA1/dynamicalias;Pglobalstore isexplicitpointerretention. CalleeS/SP/RA/frame/code,object321B/Out4B,MMIO/alias/clock/hook/provider/ownership fullconditions remain'],
  actual_installedbinding_output_lastwriter_querytermination_pointer_nonretention_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-query-output-initialization-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=1240,complete_phase_body_instructions=392,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['RAM200014c6 and56972/56ab2 nestedquery callees,436a8/43734 downstream','clock/failurehook actualbindings/sourcewriters and query/cleanup/recordownership order','5d006/5d14e andoptional6430e/638ea helpers/fullobjectlifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],SIZE);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-ENTRY;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('RAMquery instructionmutation escaped')
   mutated+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('RAMquery typedmutation escaped')
   typed+=1
 check((mutated,typed)==(392,60),'RAMquery mutationcensus')
 print('PASS:392 instruction/60 typed-load mutations rejected;Out store-cut/borrowedSP12/global P handoff')


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
 else:check(OUT.read_bytes()==encoded,'RAMquery exactledger replay')
 print('PASS:1240B/392i complete RAMquery;strictHEX/fullfirstcopy;Out-storecut/SP12/P handoff;exactledger')
 print('PASS:NO target execution/emulation;provider/clockprogress/outputstability/full lifetimes UNPROVED')


if __name__=='__main__':main()
