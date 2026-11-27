"""Offline notifier input-slice and private bounded selector contracts.
Original operands/immutable CFGs and host bit/interval identities only.
No target execution/emulation, mutable packet/heap/queue/selector model.
"""
import argparse,json
from collections import deque
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_record_callback_static as previous
import check_v4160_threshold_message_static as queue
import check_v4160_message_marker_static as allocator
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS={**previous.FIELDS,'remu':('rd','rs1','rs2')}
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-notify-selection-static.json')
ROLES=('notify','select','shift')
SIZES={'notify':94,'select':618,'shift':44}
COUNTS={'notify':37,'select':222,'shift':15}
STARTS=({'notify': 339328, 'select': 536877014, 'shift': 450242}, {'notify': 339496, 'select': 536877014, 'shift': 450738})
SOURCES=({'notify': 339328, 'select': 268870, 'shift': 450242}, {'notify': 339496, 'select': 268934, 'shift': 450738})
HASHES=({'notify': '9f6a43f6460036b64ee672cc4d68d747cc60a1246d9422a613524ddc18ef291e', 'select': 'b9bfbe010c9970a978106f6a2cdeda1e34dfe74d3fe39cd99845fd1d4aed413a', 'shift': '1eb4d7b36ea3c0fd97d6c5e13c51cd41901375aea68054d52fa1f0572a047a92'}, {'notify': 'c0cd9e88e6f89fbacc430706c94d6353a8cf408f028324b15658f754e6266833', 'select': '3c8378a23d504390b25576c852f6026c369a1a20cffaba88fd9590503bf95304', 'shift': '1eb4d7b36ea3c0fd97d6c5e13c51cd41901375aea68054d52fa1f0572a047a92'})
LITERALS={
'notify':"""
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 addi 9 9 940
00c load 14 9 7 1
00e store 2 1 12 4
010 store 2 8 8 4
012 addi 15 0 255
016 beq 14 15 84
01a mv 8 10
01c li 10 6
01e auipc 1 536530944
022 jalr 1 1 1176
026 mv 11 10
028 beqz 10 84
02a addi 15 0 -48
02e store 10 15 0 1
030 addi 15 0 39
034 store 10 0 1 1
038 store 10 15 2 1
03a load 15 8 1 1
03c store 10 15 3 1
03e load 15 8 2 1
040 store 10 15 4 1
042 load 15 8 3 1
044 store 10 15 5 1
046 load 8 2 8 4
048 load 10 9 7 1
04a load 1 2 12 4
04c load 9 2 4 4
04e addi 2 2 16
050 jal 0 274952
054 load 1 2 12 4
056 load 8 2 8 4
058 load 9 2 4 4
05a addi 2 2 16
05c jr 1
""",
'select':"""
000 load 15 10 140 4
004 load 12 10 136 2
008 addi 2 2 -48
00a srli 13 15 16
00e xor 13 13 15
010 slli 13 13 16
012 srli 13 13 16
014 xor 12 12 13
016 srai 14 12 7
01a srai 15 12 5
01e andi 15 15 2
020 andi 14 14 1
022 or 14 14 15
024 srai 15 12 3
028 andi 15 15 4
02a or 14 14 15
02c srai 15 12 1
030 andi 15 15 8
032 or 14 14 15
034 slli 15 12 1
038 andi 15 15 16
03a or 14 14 15
03c slli 15 12 3
040 andi 15 15 32
044 or 14 14 15
046 slli 15 12 5
04a srli 11 12 8
04e andi 15 15 64
052 slli 12 12 7
054 or 14 14 15
056 andi 12 12 255
05a or 14 14 12
05c srai 15 11 5
060 srai 12 11 3
064 andi 12 12 4
066 andi 15 15 2
068 or 15 15 12
06a srai 12 11 7
06e or 15 15 12
070 srai 12 11 1
074 andi 12 12 8
076 or 15 15 12
078 slli 12 11 1
07c andi 12 12 16
07e or 15 15 12
080 slli 12 11 3
084 andi 12 12 32
088 or 15 15 12
08a slli 12 11 5
08e andi 12 12 64
092 slli 11 11 7
094 or 15 15 12
096 andi 11 11 255
09a or 15 15 11
09c slli 15 15 8
09e li 12 17
0a0 or 14 14 15
0a2 mul 14 14 12
0a6 store 2 8 40 4
0a8 mv 8 10
0aa store 2 9 36 4
0ac store 2 20 24 4
0ae store 2 21 20 4
0b0 load 20 8 160 4
0b4 load 21 8 164 4
0b8 store 2 22 16 4
0ba store 2 1 44 4
0bc add 14 14 13
0be slli 14 14 16
0c0 srli 14 14 16
0c2 srai 15 14 7
0c6 srai 10 14 5
0ca andi 10 10 2
0cc andi 15 15 1
0ce or 15 15 10
0d0 srai 10 14 3
0d4 andi 10 10 4
0d6 or 15 15 10
0d8 srai 10 14 1
0dc andi 10 10 8
0de or 15 15 10
0e0 slli 10 14 1
0e4 andi 10 10 16
0e6 or 15 15 10
0e8 slli 10 14 3
0ec andi 10 10 32
0f0 or 15 15 10
0f2 slli 10 14 5
0f6 srli 11 14 8
0fa andi 10 10 64
0fe slli 14 14 7
100 or 15 15 10
102 andi 14 14 255
106 or 15 15 14
108 srai 10 11 3
10c srai 14 11 5
110 andi 10 10 4
112 andi 14 14 2
114 or 14 14 10
116 srai 10 11 7
11a or 14 14 10
11c srai 10 11 1
120 andi 10 10 8
122 or 14 14 10
124 slli 10 11 1
128 andi 10 10 16
12a or 14 14 10
12c slli 10 11 3
130 andi 10 10 32
134 or 14 14 10
136 slli 10 11 5
13a andi 10 10 64
13e slli 11 11 7
140 or 14 14 10
142 andi 11 11 255
146 or 14 14 11
148 slli 14 14 8
14a or 15 15 14
14c mul 15 15 12
150 store 2 18 32 4
152 store 2 19 28 4
154 store 2 23 12 4
156 store 2 24 8 4
158 add 15 15 13
15a slli 15 15 16
15c srli 15 15 16
15e srai 14 15 7
162 srai 10 15 5
166 andi 10 10 2
168 andi 14 14 1
16a or 14 14 10
16c srai 10 15 3
170 andi 10 10 4
172 or 14 14 10
174 srai 10 15 1
178 andi 10 10 8
17a or 14 14 10
17c slli 10 15 1
180 andi 10 10 16
182 or 14 14 10
184 slli 10 15 3
188 andi 10 10 32
18c or 14 14 10
18e slli 10 15 5
192 srli 11 15 8
196 andi 10 10 64
19a slli 15 15 7
19c or 14 14 10
19e andi 15 15 255
1a2 or 15 15 14
1a4 srai 10 11 3
1a8 srai 14 11 5
1ac andi 10 10 4
1ae andi 14 14 2
1b0 or 14 14 10
1b2 srai 10 11 7
1b6 or 14 14 10
1b8 srai 10 11 1
1bc andi 10 10 8
1be or 14 14 10
1c0 slli 10 11 1
1c4 andi 10 10 16
1c6 or 14 14 10
1c8 slli 10 11 3
1cc andi 10 10 32
1d0 or 14 14 10
1d2 slli 10 11 5
1d6 andi 10 10 64
1da slli 11 11 7
1dc or 14 14 10
1de andi 11 11 255
1e2 or 14 14 11
1e4 slli 14 14 8
1e6 or 15 15 14
1e8 mul 15 15 12
1ec addi 12 0 37
1f0 mv 10 20
1f2 mv 11 21
1f4 add 15 15 13
1f6 xor 13 13 15
1f8 slli 9 13 16
1fc srli 9 9 16
1fe remu 12 9 12
202 andi 22 12 255
206 auipc 1 3758538752
20a jalr 1 1 1254
20e andi 10 10 1
210 bnez 10 586
212 load 15 8 129 1
216 li 18 0
218 li 19 0
21a mul 9 15 9
21e addi 24 0 37
222 srli 9 9 16
224 mv 12 18
226 mv 10 20
228 mv 11 21
22a auipc 1 3758538752
22e jalr 1 1 1218
232 andi 10 10 1
234 andi 23 18 255
238 beqz 10 580
23a beq 9 19 614
23e addi 19 19 1
240 andi 19 19 255
244 addi 18 18 1
246 bne 18 24 548
24a store 8 22 126 1
24e load 1 2 44 4
250 load 8 2 40 4
252 load 9 2 36 4
254 load 18 2 32 4
256 load 19 2 28 4
258 load 20 2 24 4
25a load 21 2 20 4
25c load 22 2 16 4
25e load 23 2 12 4
260 load 24 2 8 4
262 addi 2 2 48
264 jr 1
266 mv 22 23
268 jump 586
""",
'shift':"""
000 beqz 12 28
002 addi 15 0 32
006 sub 15 15 12
008 bge 0 15 30
00c srl 10 10 12
010 sll 15 11 15
014 srl 12 11 12
018 or 10 10 15
01a mv 11 12
01c jr 1
01e addi 10 12 -32
022 li 12 0
024 srl 10 11 10
028 mv 11 12
02a jump 28
""",
}
PATCHES={'notify': {8: ('addi', [9, 9, 1020]), 34: ('jalr', [1, 1, 1008]), 80: ('jal', [0, 275092])}, 'select': {522: ('jalr', [1, 1, 1750]), 558: ('jalr', [1, 1, 1714])}, 'shift': {}}
TYPED={'notify': [], 'select': [(0, 2), (4, 5), (176, 2), (180, 2), (530, 4)], 'shift': []}
QK={'notify': [(12, 'f830', 'qk.c.lbu'), (46, '1ca1', 'qk.c.sb'), (56, '3ca1', 'qk.c.sb'), (58, '1c30', 'qk.c.lbu'), (60, '3cb1', 'qk.c.sb'), (62, '3c20', 'qk.c.lbu'), (64, '5ca1', 'qk.c.sb'), (66, '3c30', 'qk.c.lbu'), (68, '5cb1', 'qk.c.sb'), (72, 'e830', 'qk.c.lbu')], 'select': [], 'shift': []}
STORES={'notify': [(2, 2, 9, 4, 4), (14, 2, 1, 12, 4), (16, 2, 8, 8, 4), (46, 10, 15, 0, 1), (52, 10, 0, 1, 1), (56, 10, 15, 2, 1), (60, 10, 15, 3, 1), (64, 10, 15, 4, 1), (68, 10, 15, 5, 1)], 'select': [(166, 2, 8, 40, 4), (170, 2, 9, 36, 4), (172, 2, 20, 24, 4), (174, 2, 21, 20, 4), (184, 2, 22, 16, 4), (186, 2, 1, 44, 4), (336, 2, 18, 32, 4), (338, 2, 19, 28, 4), (340, 2, 23, 12, 4), (342, 2, 24, 8, 4), (586, 8, 22, 126, 1)], 'shift': []}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);values=list(map(int,values))
  if index and o in PATCHES[role]:op,values=PATCHES[role][o]
  check(len(values)==len(FIELDS[op]),'notify-select literalfields');d=dict(zip(FIELDS[op],values));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+o]=d
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'notify-select fullboundaries '+role)
 for a,f in s.items():init.g(n,a,'notify-select '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'notify-select fullidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'notify-select typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'notify-select exactQKbyte')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'notify-select ordinaryRET');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(role=='notify' and d['rd']==0,'notify-select sender unlinkedtail');tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','notify-select linkedPCpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(op not in ('call_indirect','csr','mret','ecall') and all(z in n for z in q),'notify-select closedCFG');e[a]=q
 expectedcalls={'notify':[dict(offset=0x22,target=0x20000236)],'select':[dict(offset=o,target=STARTS[index]['shift']) for o in (0x20a,0x22e)],'shift':[]}[role]
 check(calls==expectedcalls and rets==[{'notify':0x5c,'select':0x264,'shift':0x1c}[role]] and tails==([dict(offset=0x50,target=0x43208+140*index,new_link=False)] if role=='notify' else []),'notify-select exactcalls/RET/tail '+role)
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'notify-select fullreachability includingafterRET')
 groups=previous.previous.previous.previous.dispatch.common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]]
 check(bool(cycles)==(role=='select'),'notify-select onlyselectorcycles')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==[tuple(x) for x in STORES[role]],'notify-select allstores '+role)
 if role=='shift':check(not stores and not any(d['op']=='load' for d in n.values()) and {d['rd'] for d in n.values() if 'rd'in d}<={10,11,12,15},'notify-select shift onlycaller-savedGPR/no memory')
 return dict(start=pc,source=SOURCES[index][role],bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,cyclic_SCCs=cycles,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=[a for a,q in e.items() if not q]
 def path(a,z):
  q=deque([(a,[a])]);seen=set()
  while q:
   p,s=q.popleft()
   if p==z:return s
   if p not in seen:seen.add(p);q.extend((v,s+[v]) for v in e[p])
  return None
 def suffix(a):
  ss=[s for z in ends if (s:=path(a,z)) is not None];check(bool(ss),'notify-select exitwitness');return min(ss,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   w=path(pc,a)+[z]+suffix(z)[1:];check(all(v in e[u] for u,v in zip(w,w[1:])),'notify-select all-edge syntaxwitness');walks.append([p-pc for p in w])
 check(len(walks)=={'notify':37,'select':225,'shift':16}[role],'notify-select full CFG edge census')
 info={}
 if role=='notify':
  explicit=[(o,d['imm']) for o,d in n.items() if d['op']=='load' and d['rs1']==8]
  check(explicit==[(0x3a,1),(0x3e,2),(0x42,3)],'notify-select inputonlybytes1/2/3 not0')
  check(n[0x1a]['rd']==8 and n[0x1a]['rs2']==10 and n[0x1c]['imm']==6 and n[0x26]['rd']==11 and n[0x26]['rs2']==10,'notify-select capturedinput/allocate6/A1M')
  check(n[0x2a]['imm']==-48 and n[0x30]['imm']==39 and n[0x48]['imm']==n[0xc]['imm']==7 and n[0x48]['rs1']==9,'notify-select sixbyteprefix/freshtaskread')
  check([o for o,d in n.items() if d.get('rd')==11]==[0x26],'notify-select messagepointerA1held tosender')
  check([o for o,d in n.items() if d['op']=='store' and d['rs1']==2]==[2,0xe,0x10] and n[0x4e]['imm']==n[0x5a]['imm']==16,'notify-select two frame-restored exits')
  info=dict(explicit_input_read_offsets=[1,2,3],source_byte0_read=False,visible_message_byte_sources=['F0hex',0,39,'fresh input1','fresh input2','fresh input3'],task_snapshots_independent=True)
 elif role=='select':
  check(n[0x9e]['imm']==17 and n[0x1ec]['imm']==37 and n[0x21e]['imm']==37 and n[0x1fe]['op']=='remu','notify-select roundfactor and37indexdomain')
  check([o for o,d in n.items() if d.get('rd')==18]==[0x216,0x244,0x254],'notify-select finitecounter definitions')
  check(n[0x216]['imm']==0 and n[0x244]['imm']==1 and n[0x246]['op']=='bne' and n[0x246]['target']==pc+0x224,'notify-select37loop rank')
  check(n[0x20e]['imm']==n[0x232]['imm']==1 and n[0x24a]['rs1']==8 and n[0x24a]['imm']==126 and n[0x24a]['rs2']==22,'notify-select bitreply vsselectedindexstore')
  check(n[0x202]['rd']==22 and n[0x266]['op']=='mv' and n[0x266]['rd']==22 and n[0x266]['rs2']==23 and n[0x268]['target']==pc+0x24a,'notify-select late match block beyondRET')
  check([o for o,d in n.items() if d['op']=='store' and d['rs1']!=2]==[0x24a] and [o for o,d in n.items() if d['op']=='load' and d['rs1']!=2]==[0,4,0xb0,0xb4,0x212],'notify-select exactinput/outputfootprint')
  check(n[0x212]['imm']==129 and n[0x21a]['op']=='mul' and n[0x222]['imm']==16,'notify-select conditionalfreshN129 rank')
  check([o for o,d in n.items() if d.get('rd')==20]==[0xb0,0x258] and [o for o,d in n.items() if d.get('rd')==21]==[0xb4,0x25a],'notify-select heldmaskword definitions')
  check(n[0x206]['op']==n[0x22a]['op']=='auipc' and n[0x1f0]['rs2']==n[0x226]['rs2']==20 and n[0x1f2]['rs2']==n[0x228]['rs2']==21,'notify-select onlyscalarwordpair passedtochild')
  info=dict(scan_indices=[0,36],max_scan_calls=37,max_total_shift_calls=38,fallback_keeps_original_index=True,callee_reply_is_last_tested_bit_not_selected_index=True,output_N126_extent=127,input_extent=168,held_mask_observed_bits=[0,36])
 else:
  check(n[0x1e]['imm']==-32 and n[0x22]['imm']==0 and n[0x24]['op']=='srl' and n[0x28]['rs2']==12,'notify-select upperlane path andpostRET block')
  info=dict(admitted_parent_shift_counts=[0,36],logical_pair_shift_proved_only_in_this_domain=True)
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_entry_exit_walks={hex(a-pc):[p-pc for p in path(pc,a)+suffix(a)[1:]] for a in ([pc+b['returns'][0]]+[pc+c['offset'] for c in b['calls']]+[pc+t['offset'] for t in b['tails']])},cyclic_SCC_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']],facts=info,actual_input_identity_binding_or_external_preservation_proved=False)


def reverse8(x):
 return ((x>>7)&1)|((x>>5)&2)|((x>>3)&4)|((x>>1)&8)|((x<<1)&16)|((x<<3)&32)|((x<<5)&64)|((x<<7)&128)


def domains():
 for x in range(256):check(reverse8(x)==sum(((x>>i)&1)<<(7-i) for i in range(8)),'notify-select closedbytebitpermutation')
 for x in range(65536):
  y=reverse8(x&255)|(reverse8(x>>8)<<8);check((reverse8(y&255)|(reverse8(y>>8)<<8))==x,'notify-select byte-lane reversal involution')
  check(0<=x%37<=36 and ((255*x)>>16)<=254,'notify-select seed/rank bounds')
  for k in (0,1,0x1234,65535):check((17*y+k)&65535==(17*y+k)%65536,'notify-select roundmod16 identity')
 shiftcases=0
 for count in range(37):
  for bit in range(64):
   wide=1<<bit;lo=wide&0xffffffff;hi=wide>>32
   if count==0:outlo,outhi=lo,hi
   elif count<32:outlo=((lo>>count)|(hi<<(32-count)))&0xffffffff;outhi=hi>>count
   else:outlo=hi>>(count-32);outhi=0
   check(outlo+(outhi<<32)==wide>>count,'notify-select two-lane logicalshift basisproof')
   check(outlo&1==((wide&((1<<37)-1))>>count)&1,'notify-select onlylow37maskbits observable');shiftcases+=1
 for r in range(38):check(r<=37 and (r&255)==r,'notify-select ordinal/no bytewrap in37iterations')
 accepted=0
 for task in range(256):
  for count in range(256):accepted+=int(2<task<count)
 check(accepted==31878,'notify-select independent sender task/countdomain')
 check(6+8==14 and (0xf000|6)==0xf006 and ((14<<16)|0xf006)==0x000ef006,'notify-select allocate6 core/tag/failurehint')
 return dict(byte_permutation_cases=256,word_permutation_cases=65536,roundmod16_cases=262144,shift_basis_cases=shiftcases,admitted_shift_count_interval=[0,36],sender_task_count_pairs=65536,accepted_task_count_pairs=accepted,
  scalar_formula='K=low16(N140 XOR(N140>>16));x=N136 XOR K;three times x=low16(17*per_byte_reverse16(x)+K);s=low16(x XOR K);initial=s%37;rank=floor(freshU8N129*s/65536) onlyafterinitialbitclear',
  rank_interval=[0,254],mask_selection_scope='scan0..36,lasttestedbitreturned,selectedindexstoredN126;no input-state replay or selector execution',message_visible_length=6,message_prefix=[240,0,39],source_offsets=[1,2,3],core_request=dict(size=14,tag=0xf006),complete_runtime_object_extent_initialized_source_or_delivery_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  src=SOURCES[index][role];raw=init.binding.take(data,src,SIZES[role]);check(sparse.captured(mem,src,SIZES[role])==raw,'notify-select complete strictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()};nt=bs['notify'];nn={d['pc']-nt['start']:d for d in nt['instructions']};sel=bs['select'];sn={d['pc']-sel['start']:d for d in sel['instructions']}
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(src+sel['start']-dest==SOURCES[index]['select'] and sel['start']+618<=end,'notify-select complete private firstcopymapping')
 cbpc=previous.STARTS[index];cbr=init.binding.take(data,cbpc,1618);check(sparse.captured(mem,cbpc,1618)==cbr,'notify-select fullcaller strictHEX');cb=previous.body(cbr,index);cn={d['pc']-cbpc:d for d in cb['instructions']}
 check(next(c['target'] for c in cb['calls'] if c['offset']==0x624)==nt['start'] and cn[0x614]['imm']==12 and cn[0x61a]['imm']==13 and cn[0x616]['imm']==14 and cn[0x622]['imm']==15,'notify-select parentSP12 input1/2/3 exactlySP13/14/15')
 check(cn[0x628]['op']=='store' and cn[0x628]['rs2']==0 and cn[0x628]['imm']==10 and cb['CFG'][cbpc+0x624]==[cbpc+0x628],'notify-select caller clearschild10 regardlessnormal notificationreply')
 stack=[d for d in cb['stores'] if d[1]==2];check(not any(imm<=12<imm+width for _,_,_,imm,width in stack),'notify-select callerSP12localgap stillnotreadbycallee')
 up=previous.previous;upc=up.STARTS[index];ur=init.binding.take(data,upc,1000);check(sparse.captured(mem,upc,1000)==ur,'notify-select B120fullcaller strictHEX');ub=up.body(ur,index);un={d['pc']-upc:d for d in ub['instructions']}
 check(next(c['target'] for c in ub['calls'] if c['offset']==0x58)==sel['start'] and un[0x52]['rs2']==8 and un[0x5c]['imm']==2,'notify-select privatecaller N andignoredA0 beforecommand2')
 check(cn[0x110]['imm']==126 and cn[0x114]['imm']==127,'notify-select N126 laterlow7operand conditionalidentity')
 ar=init.binding.take(data,src+allocator.ENTRY-dest,allocator.LENGTH);check(ar==allocator.MSG and sparse.captured(mem,src+allocator.ENTRY-dest,allocator.LENGTH)==ar,'notify-select reusedmessageallocator exactbody/strictHEX');an=allocator.decode(ar,allocator.ENTRY)
 check(dest<=allocator.ENTRY and allocator.ENTRY+allocator.LENGTH<=end,'notify-select full allocator firstcopy extent')
 for a,f in allocator.message_specs().items():allocator.guard(an,a,'notify-select allocatoroperand',**f)
 sender=queue.body(init.binding.take(data,queue.SOURCES[index][2],146),'sender',index);append=queue.body(init.binding.take(data,queue.SOURCES[index][3],26),'append',index)
 check(sparse.captured(mem,sender['source'],146)==init.binding.take(data,sender['source'],146) and sparse.captured(mem,append['source'],26)==init.binding.take(data,append['source'],26),'notify-select sender/append strictHEX')
 check(nt['tails'][0]['target']==sender['start'] and src+append['start']-dest==append['source'],'notify-select exacttail/appendfirstcopy')
 check(dest<=append['start'] and append['start']+26<=end,'notify-select full append firstcopy extent')
 task=0x20003000+nn[8]['imm']+7;check(task==0x200033b3+80*index,'notify-select fixedtaskbyte')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_recordcaller=dict(start=cbpc,bytes=1618,sha256=cb['sha256'],stack13=cn[0x61a],stack14=cn[0x616],stack15=cn[0x622]),reused_B120caller=dict(start=upc,bytes=1000,sha256=ub['sha256']),reused_allocator=dict(source=src+allocator.ENTRY-dest,target=allocator.ENTRY,bytes=86,sha256=allocator.MSG_SHA),reused_sender=dict(start=sender['start'],bytes=146,sha256=sender['sha256']),reused_append=dict(start=append['start'],source=append['source'],bytes=26,sha256=append['sha256']),notification_task_byte=task,
  contract=['notifier firsttask255 ->normalRETentryQ,no Qreads;elseallocate6;null ->RET0;nonnullM visiblebytesF0,00,27,Q1,Q2,Q3;onlyexplicitQreads1..3 andno localQpointerstore/downstreamQargument',
   'fresh taskbyte afterallocation,notentrysnapshot,thenframe-restored unlinkedtail sender(freshtask,M). Sender canreject/release-request,queueappend/event areconditional,no actualdelivery/free proof',
   'recordcaller Q=SP12 mapsreads toSP13/14/15 localstores;SP12notreadbythismatchingnotifier;source/frame/callee/alias andproviderpreservation stillrequired. Caller clearschild10 afterany normalreply,notdeliverysuccess',
   'private618B scalar/bitselection usescapturedN140/N136/N160/N164 andconditionalfreshN129;only nonframe storebyteN126. Initialbitset commitsinitialindex;otherwise scans0..36,ordinal0..37 withmatchingpure44Bshifter,up to38totalcalls',
   'selectionchild onlyGPRpair shifts admitted0..36,no memory/frame/calls;parent AND1 testslow37maskbits. Onmatch choosescurrentindex;exhaustkeepsinitialindex evenunset. A0lasttestedbit notindex orsuccess;N168extent stillneededforfullwordloads',
   'B120 ignoresprivateA0 bysetting2 beforeitsnextcall. LatercallbackreadsN126&127;actualsameN/fieldretention/provider andglobalorder unproved;privateborrowedpointer noescape beyondlocalinstructions notclaimed'],
  actual_installedbinding_queue_delivery_sourceinitialization_pointer_nonretention_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-notifier-source-slice-and-private-selector-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=1512,complete_phase_body_instructions=548,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['private43414/5c830/5d006 andsourcewriters/actualbindings','notificationmessage taskconsumer/release andcompleteownership','actualRXdataextent/TXdelivery/callbackorder/fullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,SOURCES[i][role],SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('notify-select instructionmutation escaped')
    mutations+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('notify-select typedmutation escaped')
    typed+=1
 check((mutations,typed)==(548,10),'notify-select mutationcensus')
 print('PASS:548 instruction/10 typed-load mutations rejected;notifier input slice/message tail/private selector/shifter certificates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
 check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,tail,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
  check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
 coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
 encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'notify-select exactledger replay')
 print('PASS:1512B/548i complete notifier/selector/shift;strictHEX;SP13..15 ->message6;N126 selection;exactledger')
 print('PASS:NO target execution/emulation;actualqueue/provider/ownership/dataextent/lifetimes UNPROVED')


if __name__=='__main__':main()
