"""Offline key producer and object submission contracts.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable object/list/clock/provider/heap model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
# Preserve the complete existing evidence ancestry despite Python import depth.
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_record_parse_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-key-submit-static.json')
ROLES=('submit','key')
SIZES={'submit':256,'key':416}
STARTS=({'submit': 367934, 'key': 368228}, {'submit': 368262, 'key': 368556})
COUNTS={'submit': 84, 'key': 128}
HASHES=({'submit': '04495bb17de06b293cc6ba62cbab96955ea29ecd0d10e3f87c43fdae7127036b', 'key': '3c8747eda3d345a3209b9f47f4806a92b08bdb4bc4cd8301f77aeffa08ba8629'}, {'submit': 'fdca926a1ae7a94c751e448588e5eadf02122eb105c95339c62175a3a25ba7bc', 'key': '0af112f23da7ff660c5a917bd8ae74b7e8b3286deee5053aa12bf191251cb12f'})
LITERALS={
'submit':"""
000 addi 2 2 -32
002 store 2 9 20 4
004 lui 9 536883200
008 store 2 19 12 4
00a addi 19 9 952
00e load 15 19 3 1
012 store 2 18 16 4
014 lui 18 536883200
018 store 2 1 28 4
01a store 2 8 24 4
01c store 2 20 8 4
01e addi 18 18 564
022 load 14 10 58 2
024 store 10 15 47 1
028 load 15 18 8 2
02c addi 20 0 800
030 mv 8 10
032 mul 14 14 15
036 lui 12 999424
03a addi 12 12 576
03e li 13 0
040 li 11 0
042 addi 9 9 952
046 divu 14 14 20
04a store 10 14 140 4
04e addi 10 0 300
052 mul 10 15 10
056 jal 1 450330
05a store 8 10 132 2
05e mv 10 8
060 jal 1 353062
064 load 14 18 8 2
068 load 15 8 58 2
06a addi 13 0 1250
06e mv 10 8
070 mul 15 15 14
074 remu 15 15 20
078 mul 15 15 13
07c div 15 15 14
080 store 8 15 32 2
082 load 15 8 132 2
086 slli 15 15 1
088 store 8 15 130 2
08c jal 1 351548
090 mv 10 8
092 jal 1 352348
096 load 11 8 62 2
098 mv 10 8
09a slli 11 11 4
09c addi 11 11 -2
09e slli 11 11 16
0a0 srli 11 11 16
0a2 jal 1 351488
0a6 mv 10 8
0a8 jal 1 359208
0ac li 15 24
0ae store 8 15 309 1
0b2 lui 15 536883200
0b6 load 15 15 1252 4
0ba store 19 8 168 4
0be andi 15 15 2
0c0 beqz 15 228
0c2 lui 18 536883200
0c6 addi 18 18 492
0ca load 15 18 52 4
0ce beqz 15 228
0d0 load 11 8 152 4
0d4 li 10 13
0d6 call_indirect 1 15
0d8 load 15 18 52 4
0dc load 11 8 156 4
0e0 li 10 14
0e2 call_indirect 1 15
0e4 mv 10 8
0e6 load 8 2 24 4
0e8 store 9 0 14 2
0ec store 9 0 16 4
0f0 load 1 2 28 4
0f2 load 9 2 20 4
0f4 load 18 2 16 4
0f6 load 19 2 12 4
0f8 load 20 2 8 4
0fa addi 2 2 32
0fc jal 0 354070
""",
'key':"""
000 addi 2 2 -32
002 store 2 19 12 4
004 store 2 1 28 4
006 store 2 8 24 4
008 store 2 9 20 4
00a store 2 18 16 4
00c jal 1 358754
010 mv 19 10
012 beqz 10 124
014 jal 1 358474
018 mv 8 10
01a beq 10 0 412
01e li 15 16
020 store 10 15 10 2
022 addi 15 0 -80
026 store 10 15 14 1
028 lui 18 536883200
02c li 15 1
02e store 10 15 16 1
030 addi 15 18 492
034 load 15 15 16 2
036 addi 14 0 260
03a addi 18 18 492
03e addi 15 15 5
040 mv 10 15
042 slli 15 15 16
044 srli 15 15 16
046 bgeu 14 15 78
04a addi 10 0 260
04e slli 14 10 16
052 srli 14 14 16
054 addi 15 0 64
058 bgeu 14 15 96
05c addi 10 0 64
060 slli 10 10 16
062 addi 11 0 589
066 srli 10 10 16
068 auipc 1 536502272
06c jalr 1 1 372
070 store 8 10 272 4
074 bnez 10 140
076 load 10 8 8 2
078 jal 1 358986
07c load 1 2 28 4
07e load 8 2 24 4
080 mv 10 19
082 load 9 2 20 4
084 load 18 2 16 4
086 load 19 2 12 4
088 addi 2 2 32
08a jr 1
08c lui 15 536883200
090 load 15 15 1336 4
094 lui 9 536883200
098 addi 14 9 952
09c load 13 14 220 4
0a0 store 8 15 276 4
0a4 load 15 14 216 4
0a8 load 14 14 1 1
0aa store 8 13 252 4
0ae store 8 15 248 4
0b2 addi 9 9 952
0b6 bnez 14 192
0b8 andi 15 15 -193
0bc store 8 15 248 4
0c0 load 15 8 252 4
0c4 load 14 8 248 4
0c8 store 8 0 326 2
0cc store 8 15 268 4
0d0 load 15 9 58 2
0d2 store 8 14 264 4
0d6 load 14 8 46 1
0da store 8 15 324 2
0de load 15 9 74 1
0e2 ori 14 14 -63
0e6 store 8 14 46 1
0ea store 8 15 361 1
0ee load 15 8 164 4
0f2 load 14 9 208 4
0f6 ori 13 15 64
0fa store 8 13 164 4
0fe slli 13 14 6
102 bge 13 0 270
106 ori 15 15 80
10a store 8 15 164 4
10e load 15 9 82 1
112 beqz 15 290
114 load 15 8 164 4
118 lui 14 4194304
11c or 15 15 14
11e store 8 15 164 4
122 li 15 -1
124 store 8 15 64 2
128 store 8 15 38 2
12a store 8 15 40 1
12e lui 15 4096
130 addi 15 15 -1096
134 store 8 15 74 2
138 mv 10 8
13a jal 1 352426
13e load 10 18 20 1
142 store 8 10 322 1
146 jal 1 407910
14a li 15 20
14c store 8 15 391 1
150 addi 15 0 40
154 store 8 15 389 1
158 addi 15 0 1776
15c store 8 15 376 2
160 addi 15 0 127
164 store 8 15 378 1
168 lui 15 4294955008
16a addi 15 15 -326
16e store 8 15 380 2
172 load 15 8 252 4
176 store 8 10 323 1
17a store 8 10 384 1
17e store 8 10 385 1
182 store 8 10 386 1
186 store 8 10 387 1
18a andi 15 15 128
18e beqz 15 406
190 li 15 1
192 store 8 15 398 1
196 store 9 0 8 2
19a jump 124
19c li 19 1
19e jump 124
""",
}
PATCHES={'submit': {10: ('addi', [19, 9, 1032]), 30: ('addi', [18, 18, 644]), 66: ('addi', [9, 9, 1032]), 86: ('jal', [1, 450826]), 96: ('jal', [1, 353382]), 140: ('jal', [1, 351868]), 146: ('jal', [1, 352668]), 162: ('jal', [1, 351808]), 168: ('jal', [1, 359528]), 182: ('load', [15, 15, 1332, 4]), 198: ('addi', [18, 18, 572]), 252: ('jal', [0, 354390])}, 'key': {12: ('jal', [1, 359074]), 20: ('jal', [1, 358794]), 48: ('addi', [15, 18, 572]), 58: ('addi', [18, 18, 572]), 108: ('jalr', [1, 1, 44]), 120: ('jal', [1, 359306]), 144: ('load', [15, 15, 1416, 4]), 152: ('addi', [14, 9, 1032]), 178: ('addi', [9, 9, 1032]), 314: ('jal', [1, 352746]), 326: ('jal', [1, 408144])}}
TYPED={'submit': [(14, 4), (40, 5), (100, 5), (130, 5), (182, 2), (202, 2), (208, 2), (216, 2), (220, 2)], 'key': [(144, 2), (156, 2), (164, 2), (192, 2), (196, 2), (214, 4), (222, 4), (238, 2), (242, 2), (270, 4), (276, 2), (318, 4), (370, 2)]}
QK={'submit': [(34, '3a3d', 'qk.c.lhu'), (104, '3e3c', 'qk.c.lhu'), (128, '1eb0', 'qk.c.sh'), (150, '6e3c', 'qk.c.lhu')], 'key': [(32, '3ea5', 'qk.c.sh'), (38, '7ca5', 'qk.c.sb'), (46, '1ca9', 'qk.c.sb'), (52, '9e2b', 'qk.c.lhu'), (118, '0a24', 'qk.c.lhu'), (168, '1833', 'qk.c.lbu'), (208, 'be3c', 'qk.c.lhu'), (296, '7eb0', 'qk.c.sh')]}
STORES={'submit': [(2, 2, 9, 20, 4), (8, 2, 19, 12, 4), (18, 2, 18, 16, 4), (24, 2, 1, 28, 4), (26, 2, 8, 24, 4), (28, 2, 20, 8, 4), (36, 10, 15, 47, 1), (74, 10, 14, 140, 4), (90, 8, 10, 132, 2), (128, 8, 15, 32, 2), (136, 8, 15, 130, 2), (174, 8, 15, 309, 1), (186, 19, 8, 168, 4), (232, 9, 0, 14, 2), (236, 9, 0, 16, 4)], 'key': [(2, 2, 19, 12, 4), (4, 2, 1, 28, 4), (6, 2, 8, 24, 4), (8, 2, 9, 20, 4), (10, 2, 18, 16, 4), (32, 10, 15, 10, 2), (38, 10, 15, 14, 1), (46, 10, 15, 16, 1), (112, 8, 10, 272, 4), (160, 8, 15, 276, 4), (170, 8, 13, 252, 4), (174, 8, 15, 248, 4), (188, 8, 15, 248, 4), (200, 8, 0, 326, 2), (204, 8, 15, 268, 4), (210, 8, 14, 264, 4), (218, 8, 15, 324, 2), (230, 8, 14, 46, 1), (234, 8, 15, 361, 1), (250, 8, 13, 164, 4), (266, 8, 15, 164, 4), (286, 8, 15, 164, 4), (292, 8, 15, 64, 2), (296, 8, 15, 38, 2), (298, 8, 15, 40, 1), (308, 8, 15, 74, 2), (322, 8, 10, 322, 1), (332, 8, 15, 391, 1), (340, 8, 15, 389, 1), (348, 8, 15, 376, 2), (356, 8, 15, 378, 1), (366, 8, 15, 380, 2), (374, 8, 10, 323, 1), (378, 8, 10, 384, 1), (382, 8, 10, 385, 1), (386, 8, 10, 386, 1), (390, 8, 10, 387, 1), (402, 8, 15, 398, 1), (406, 9, 0, 8, 2)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'key-submit literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'key-submit completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'key-submit '+role+' operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'key-submit completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'key-submit typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'key-submit exactQK')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'key-submit ordinaryRET');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr','call_indirect'):
   target=d['target'] if op=='jal' else 'freshA5'
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and d['rd']==d['rs1']==u['rd']==1,'key-submit linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   if d['rd']==0:check(role=='submit' and op=='jal','key-submit onlyunlinkedtail');tails.append(dict(offset=a-pc,target=target,new_link=False));q=[]
   else:check(d['rd']==1 and (op!='call_indirect' or d['rs1']==15),'key-submit linkedcall');calls.append(dict(offset=a-pc,target=target))
  check(op not in ('csr','ecall','mret') and all(z in n for z in q),'key-submit closedCFG');e[a]=q
 expected={
 'submit':[(0x56,0x6df1a+496*index),(0x60,0x56326+320*index),(0x8c,0x55d3c+320*index),(0x92,0x5605c+320*index),(0xa2,0x55d00+320*index),(0xa8,0x57b28+320*index),(0xd6,'freshA5'),(0xe2,'freshA5')],
 'key':[(0xc,0x57962+320*index),(0x14,0x5784a+320*index),(0x6c,0x20000040),(0x78,0x57a4a+320*index),(0x13a,0x560aa+320*index),(0x146,0x63966+234*index)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and tails==([dict(offset=0xfc,target=0x56716+320*index,new_link=False)] if role=='submit' else []) and rets==([] if role=='submit' else [0x8a]),'key-submit exact calls/tails/RET')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'key-submit fullreachability')
 groups=previous.previous.previous.previous.previous.previous.dispatch.common.sccs(e);check(all(len(g)==1 and g[0] not in e[g[0]] for g in groups),'key-submit acyclic localCFG')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'key-submit exactallstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,local_CFG_acyclic=True,actual_chain_return_or_pointer_lifetime_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};end=pc+(0xfc if role=='submit' else 0x8a)
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((q,p+[q]) for q in e[a])
  raise RuntimeError('key-submit no syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,end)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'key-submit all-edge syntaxwitness');walks.append([a-pc for a in p])
 def walk(choices):
  a=pc;p=[]
  while True:
   o=a-pc;check(o not in p,'key-submit finite selectedwalk');p.append(o)
   if not e[a]:break
   if o in choices:q=pc+choices[o];check(q in e[a],'key-submit selectededge')
   else:check(len(e[a])==1,'key-submit missingchoice '+hex(o));q=e[a][0]
   a=q
  return p
 if role=='submit':
  selected={
   'no-global-flag':walk({0xc0:0xe4}),
   'first-null-hook':walk({0xc0:0xc2,0xce:0xe4}),
   'two-callback-sites':walk({0xc0:0xc2,0xce:0xd0})}
  check(n[0x22]['imm']==58 and n[0x28]['imm']==n[0x64]['imm']==8 and n[0x68]['imm']==58,'key-submit independent U16samples')
  check(n[0x2c]['imm']==800 and n[0x46]['op']=='divu' and n[0x74]['op']=='remu' and n[0x7c]['op']=='div' and n[0x6a]['imm']==1250,'key-submit exactdivision signedness/constants')
  check(n[0x4e]['imm']==300 and n[0x3a]['imm']+n[0x36]['imm']==1000000 and n[0x3e]['imm']==n[0x40]['imm']==0,'key-submit arithmetic request pair')
  check(n[0x24]['imm']==47 and n[0x4a]['imm']==140 and n[0x5a]['imm']==132 and n[0x80]['imm']==32 and n[0x88]['imm']==130,'key-submit localarithmetic writes')
  check(n[0x96]['imm']==62 and n[0x9a]['imm']==4 and n[0x9c]['imm']==-2 and n[0x9e]['imm']==n[0xa0]['imm']==16,'key-submit low16(16H-2)argument')
  check(n[0xb6]['imm']==1252+80*(pc!=STARTS[0]['submit']) and n[0xbe]['imm']==2 and n[0xba]['rs2']==8 and n[0xba]['imm']==168,'key-submit global bit1 andWpointer publication')
  check(n[0xca]['imm']==n[0xd8]['imm']==52 and n[0xd0]['imm']==152 and n[0xdc]['imm']==156 and n[0xd4]['imm']==13 and n[0xe0]['imm']==14,'key-submit twofresh hook/wordarguments')
  check(e[pc+0xd6]==[pc+0xd8] and e[pc+0xd8]==[pc+0xdc] and e[pc+0xdc]==[pc+0xe0] and e[pc+0xe0]==[pc+0xe2],'key-submit no second-null guard')
  check(n[0xe4]['rs2']==8 and n[0xe8]['rs2']==n[0xec]['rs2']==0 and n[0xe8]['imm']==14 and n[0xec]['imm']==16 and n[0xfa]['imm']==32,'key-submit Wargument/globalszero/framebeforetail')
  info=dict(object_minimum_extent=310,explicit_pointer_publication='B+168=entryW before optionalcallbacks',hook_slot_reads_independent=True,second_hook_null_guard=False,return_description='no localRET;frame-restoredtail(heldW),tailreply/retentionunknown',local_store_count=15)
 else:
  base={0x12:0x14,0x1a:0x1e,0x46:0x4a,0x58:0x60,0x74:0x8c,0xb6:0xc0,0x102:0x10e,0x112:0x122,0x18e:0x196}
  selected={name:walk(base|patch) for name,patch in {
   'upstream-zero':{0x12:0x7c},'lookup-null':{0x1a:0x19c},'allocation-null':{0x74:0x76},
   'allocation-nonnull':{},'all-optional-writes':{0xb6:0xb8,0x102:0x106,0x112:0x114,0x18e:0x190},'upperclamp-skipped':{0x46:0x4e},'lowerclamp-used':{0x46:0x4e,0x58:0x5c}}.items()}
  check([o for o,d in n.items() if d.get('rd')==19]==[0x10,0x86,0x19c] and n[0x80]['rs2']==19 and n[0x19c]['imm']==1,'key-submit retained originalkey exceptlookupmiss1')
  check(n[0x34]['imm']==16 and n[0x3e]['imm']==5 and n[0x36]['imm']==n[0x4a]['imm']==260 and n[0x54]['imm']==n[0x5c]['imm']==64 and n[0x62]['imm']==589,'key-submit wrappedclamp allocator tuple')
  check(n[0x70]['imm']==272 and n[0x70]['rs2']==10 and n[0x74]['op']=='bnez' and n[0x76]['imm']==8,'key-submit nullreply storedbefore cleanupIDread')
  check(n[0x196]['rs2']==0 and n[0x196]['imm']==8 and n[0x13e]['imm']==20 and n[0x142]['imm']==322,'key-submit clearB8 andfreshF20 publication')
  check(n[0xc8]['width']==2 and n[0xc8]['imm']==326 and n[0xfa]['imm']==n[0x10a]['imm']==n[0x11e]['imm']==164,'key-submit exact maskword +zero326pair')
  check(n[0xf6]['imm']==64 and n[0x106]['imm']==80 and n[0x102]['op']=='bge' and n[0xfe]['imm']==6 and n[0x118]['imm']==0x400000,'key-submit bit25 OR80 fresh/held distinction')
  check(n[0x146]['op']=='jal' and n[0x176]['rs2']==n[0x17a]['rs2']==n[0x17e]['rs2']==n[0x182]['rs2']==n[0x186]['rs2']==10,'key-submit same replybyte in5stores')
  info=dict(object_minimum_extent=399,separate_allocation_size_interval=[64,260],allocation_reply_field=272,allocation_null_can_return_original_nonzero_key=True,lookup_miss_returns1=True,return_not_allocation_pointer=True,local_store_count=39)
 check((len(walks),len(selected))==({'submit':(85,3),'key':(136,7)}[role]),'key-submit complete edge/path census')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks=selected,facts=info,scope='immutable CFG/operands only; predicatefeasibility, sourcecontents, actualcallee/binding/preservation/alias conditional')


def domains():
 req=[]
 for h in range(65536):
  r=(h+5)&65535;q=max(64,min(260,r));check(64<=q<=260,'key-submit allocation clampbound');req.append(q)
  if h>=65531:check(q==64,'key-submit high-end wrap tolowerclamp')
  check((16*h-2)&65535==((16*h-2)%65536),'key-submit submit low16 argument')
  check(((2*h)&65535)==((2*h)%65536),'key-submit doubledhalfword wraps')
 check(req[0]==64 and req[59]==64 and req[255]==260 and req[65530]==260 and req[65531:]==[64]*5,'key-submit clampboundary witnesses')
 check(65535*65535<2**32 and (65535*65535)//800==5368545,'key-submit unsignedword product/nooverflow')
 for r in range(800):check(0<=r*1250<=998750<2**31,'key-submit signedDIV numerator nonnegative')
 cases=0
 for k in range(65536):
  for h in (0,1,799,65535):
   p=h*k;rem=p%800;num=rem*1250
   check(p<2**32 and 0<=rem<800,'key-submit sampledproduct/freshscalar family')
   if k:check(0<=num//k<=998750,'key-submit positive K DIV range')
   else:check(num==0 and (-1)&65535==65535,'key-submit RV32 DIVbyzero value encodesffff')
   cases+=1
 for bit in range(32):check(bool(((1<<bit)<<6)&0x80000000)==(bit==25),'key-submit signshift6 selectsbit25')
 for low in range(256):check((low|-63)&255==low|193,'key-submit byte ORminus63 exactlyORc1')
 for h in range(65536):check(300*h<2**32 and 300*h<=19660500,'key-submit helper lowword bound nohighproduct')
 return dict(allocation_clamp_cases=65536,allocation_request_interval=[64,260],allocation_wrap_source_interval=[65531,65535],allocation_tag=589,submit_product_max=4294836225,submit_W140_max=5368545,remainder_cases=800,nonzeroK_signedDIV_numerator_interval=[0,998750],sampled_H_by_all_K_cases=cases,sampled_H_values=[0,1,799,65535],K_zero_RV32_signedDIV=-1,K_zero_W32_low16=65535,helper_request='(300*capturedU16K,0,1000000,0);actualA0replylow16 storedW132,quotientnotprovedforthisdomain',source_scalar_identities_only=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,SIZES[role])==raw,'key-submit complete strictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()};key=bs['key'];kn={d['pc']-key['start']:d for d in key['instructions']};sub=bs['submit'];sn={d['pc']-sub['start']:d for d in sub['instructions']}
 # Adjacent prologue is excluded from the complete key body, not silently decoded as part of it.
 nxt=key['start']+416;after=init.binding.take(data,nxt,8);check(sparse.captured(mem,nxt,8)==after and after[:4]==bytes.fromhex('411106c6'),'key-submit followingfunction prologue excluded')
 parser=previous;pp=parser.STARTS[index];pr=init.binding.take(data,pp,388);check(sparse.captured(mem,pp,388)==pr,'key-submit parser fullstrictHEX');pb=parser.body(pr,index);pn={d['pc']-pp:d for d in pb['instructions']}
 check(pb['calls'][3]['target']==key['start'] and pb['calls'][6]['target']==sub['start'] and pn[0x120]['rs2']==8 and pn[0x9e]['rs2']==10,'key-submit caller exact linkedbodies/objectcapture')
 check(pb['CFG'][pp+0x96]==[pp+0x9a] and pb['calls'][4]['target']==key['calls'][1]['target'],'key-submit inner/outer lookup sameimplementation notsameobservation')
 record=previous.previous.previous;lookup=record.completion.ramrequest;lp=lookup.STARTS[index][2];lr=init.binding.take(data,lp,24);check(sparse.captured(mem,lp,24)==lr,'key-submit lookup strictHEX');lb=lookup.body(lr,'lookup',index)
 # Reuse complete cleanup; no new release-success claim follows from a call.
 import check_v4160_task5_removal_static as removal
 rp=removal.STARTS[index][0];rr=init.binding.take(data,rp,122);check(sparse.captured(mem,rp,122)==rr,'key-submit removal strictHEX');rb=removal.body(rr,'remove',index)
 check(key['calls'][3]['target']==rp and key['CFG'][key['start']+0x78]==[key['start']+0x7c],'key-submit cleanupnormalreply immediately ignored bykeyepilogue')
 import check_v4160_allocation_core_static as alloc
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16);asrc=src+alloc.ENTRY-dest;ar=init.binding.take(data,asrc,208)
 check(asrc==alloc.DETAILS[index][0] and dest<=alloc.ENTRY and alloc.ENTRY+208<=end and sparse.captured(mem,asrc,208)==ar and sha256(ar).hexdigest()==alloc.DETAILS[index][-1],'key-submit complete allocator original/firstcopy')
 an=alloc.decode(ar);expected=alloc.specs(alloc.DETAILS[index]);check(an.keys()==expected.keys(),'key-submit allocatorboundaries')
 for a,f in expected.items():alloc.message.guard(an,a,'key-submit allocatoroperand',**f)
 check(kn[0x68]['op']=='auipc' and key['calls'][2]['target']==alloc.ENTRY,'key-submit private allocator join')
 B=0x20003000+952+80*index;F=0x20003000+492+80*index;Kslot=0x20003000+572+80*index
 check(sn[0xa]['imm']+sn[4]['imm']==B and sn[0xc6]['imm']+sn[0xc2]['imm']==F and sn[0x1e]['imm']+sn[0x14]['imm']+8==Kslot and kn[0x30]['imm']+kn[0x28]['imm']==F,'key-submit fixedcontextaddresses')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_parser=dict(start=pp,bytes=388,sha256=pb['sha256']),reused_lookup=lb,reused_removal=dict(start=rp,bytes=122,sha256=rb['sha256']),reused_allocation_core=dict(target=alloc.ENTRY,source=asrc,bytes=208,sha256=sha256(ar).hexdigest()),addresses=dict(B=B,F=F,Kslot=Kslot),
  contracts=['keyproducer first57962/57aa2 replyK capturedS3; K0returns0;nonzero lookupK;lookupnull overwritesS3=1 andreturns1;nonnullW requestseparateallocation andordinaryreturnsoriginalK evenallocationnull/cleanupnormalreturn',
   'separateallocation requestA0=clamp(low16(freshU16F16+5),64,260),A1=589;replyPstoredW272 beforenulltest. Pnonnull causesmany Wstores andunknowncallees; no zero-fill,actualextentorfullinitializationproof',
   'key W276=freshglobalword,W252/W248=freshB220/B216;conditionalfreshB1zero masksW248bits6/7;fresh W252/W248 copiedW268/W264. Later W164 held/fresh ORs64/80/00400000;W326U16zero;constants/returnedlow8stores perexactoperands',
   'key Wminimum399bytes,notcoveredbyseparate64..260B allocation;allocationcore fallback/ownership/realbindings unproved. Cleanup mayunlink/releasematchingnode; originalK returndoesnotprovefirstlookupW stillalive orouterlookupfindssamenode',
   'submit W47=freshB3;W140=floor(firstU16W58*firstU16Kslot/800);W132=low16 actual arithmeticreply for300*Kslot over1000000. LaterindependentK/W58 give W32=low16(signedDIV((product%800)*1250,K));K0 DIVreply-1,notfault;W130=low16(2*freshW132)',
   'submitlinked callees receiveW,onewithlow16(16*freshU16W62-2);statusrepliesunused. PublishW toB168 beforeoptionalcallbacks;globalbit1 andfirstfreshF52nonnullgate firstcall(13,freshW152);reloadF52 withoutnullguard secondcall(14,freshW156)',
   'submitclearsB14U16/B16word,restores32Bframe,unlinkedtail56716/56856(heldW),nolocalRET/scalarreply. Unknowntail/provider/aliases/frame/object/codeandcallbackpreservation preventfullownership/noescape/returnproof',
   'parser receiveskeyreturn thenfreshouterlookup; its laterexplicitW326/327 bytewrites canoverwritekey SH0(W326) onlyifactualobjectidentity/order/preservation hold. Sameimplementation doesnotprovesamenode orretention'],
  actual_installedbinding_lookup_identity_allocation_success_sourceinitialization_tail_completion_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-key-producer-and-submit-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=1344,complete_phase_body_instructions=424,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['upstream57962/57aa2 key source andsubmit tail56716/56856','submit/key nestedhelpers andfreshcallbackslot writers','5d006/5d14e fullfollowup,actualbindings/objectextent/ownership/messageconsumption/fullpointerlifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('key-submit instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('key-submit typedmutation escaped')
    typed+=1
 check((mutated,typed)==(424,44),'key-submit mutationcensus')
 print('PASS:424 instruction/44 typed-load mutations rejected;key return/allocation clamp/submit pointer andcallback boundaries')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,tail,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'key-submit exactledger replay')
 print('PASS:1344B/424i complete key/submit;strictHEX;full firstcopy/core/lookup/cleanup joins;exactledger')
 print('PASS:NO target execution/emulation;actualprovider/callbackretention/lookupidentity/full lifetimes UNPROVED')


if __name__=='__main__':main()
