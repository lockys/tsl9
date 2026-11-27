"""Offline complete B120 callback target: flag waits, requests and return boundaries.
Original operands, immutable CFGs and host bit/interval identities only.
No target execution/emulation, mutable clock/RAM/MMIO/callback/packet model.
"""
import argparse,json
from collections import deque
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_packet_fields_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-b120-target-static.json')
STARTS=(0x5d5c4,0x5d70c)
HASHES=('bbca085b27e8f09910c6478da5268d93c0146ccfecf8fd2e710e840b31002d8a', '44d07da9a4bfa893ed7935c16b34938f64b83ca78dd000afdf6f399445f65cb6')
LITERAL="""
000 load 15 10 124 1
004 beq 15 0 998
008 addi 2 2 -32
00a store 2 8 24 4
00c store 2 1 28 4
00e store 2 9 20 4
010 store 2 18 16 4
012 store 2 19 12 4
014 store 2 20 8 4
016 li 14 18
018 mv 8 10
01a bne 15 14 82
01e load 14 10 130 2
022 load 15 10 136 2
026 bne 14 15 82
02a addi 9 10 160
02e lui 11 536883200
032 li 12 5
034 addi 11 11 1214
038 mv 10 9
03a auipc 1 536489984
03e jalr 1 1 -716
042 mv 10 9
044 jal 1 359128
048 li 15 4
04a store 8 10 129 1
04e store 8 15 124 1
052 mv 10 8
054 auipc 1 536494080
058 jalr 1 1 446
05c li 10 2
05e jal 1 409306
062 load 14 8 172 4
066 lui 18 536883200
06a load 15 8 124 1
06e load 13 18 480 4
072 beq 14 0 634
076 li 14 3
078 bne 15 14 330
07c li 15 4
07e store 8 15 124 1
082 load 15 8 84 4
084 ori 15 15 8
088 store 8 15 84 4
08a lui 15 536883200
08e addi 15 15 952
092 load 14 15 125 1
096 andi 14 14 2
098 beqz 14 146
09a load 14 15 125 1
09e andi 14 14 252
0a2 store 15 14 125 1
0a6 call_indirect 1 13
0a8 lui 15 536883200
0ac addi 15 15 564
0b0 load 13 15 8 2
0b2 load 14 8 134 2
0b6 store 8 10 148 4
0ba load 15 15 4 4
0bc mul 14 14 13
0c0 addi 13 0 800
0c4 addi 14 14 400
0c8 divu 14 14 13
0cc add 13 10 14
0d0 mv 12 13
0d2 bltu 13 10 218
0d6 bltu 13 15 222
0da sub 12 13 15
0de lui 13 536883200
0e2 load 13 13 515 1
0e6 store 8 12 152 4
0ea bltu 12 13 324
0ee sub 12 12 13
0f0 lui 10 380928
0f4 addi 13 8 125
0f8 mv 11 8
0fa addi 10 10 1476
0fe jal 1 275476
102 lui 15 536883200
106 lui 10 380928
10a addi 15 15 1300
10e li 14 11
110 addi 10 10 -1612
114 store 15 14 7 1
116 auipc 1 536489984
11a jalr 1 1 176
11e lui 15 536883200
122 load 15 15 1340 4
126 li 14 2
128 store 15 14 108 4
12a load 15 8 136 2
12e load 1 2 28 4
130 load 9 2 20 4
132 addi 15 15 1
134 store 8 15 136 2
138 load 8 2 24 4
13a load 18 2 16 4
13c load 19 2 12 4
13e load 20 2 8 4
140 addi 2 2 32
142 jr 1
144 sub 15 15 13
146 add 12 12 15
148 jump 240
14a load 19 8 152 4
14e lui 9 536883200
152 call_indirect 1 13
154 addi 9 9 564
158 bltu 19 10 420
15c lui 15 536883200
160 load 15 15 515 1
164 sub 10 19 10
168 bltu 15 10 370
16c li 15 1
16e bltu 15 10 426
172 load 15 8 134 2
176 load 14 9 8 2
178 mul 15 15 14
17c addi 14 0 800
180 addi 15 15 400
184 load 12 9 4 4
186 divu 15 15 14
18a load 14 8 152 4
18e add 14 14 15
190 mv 13 14
192 bltu 14 15 410
196 bltu 14 12 414
19a sub 13 14 12
19e store 8 13 152 4
1a2 jump 298
1a4 load 15 9 4 4
1a6 add 19 19 15
1a8 jump 348
1aa load 13 8 172 4
1ae load 11 9 4 4
1b0 store 13 0 9 1
1b4 load 12 9 8 2
1b6 load 15 8 134 2
1ba load 14 8 152 4
1be mul 15 15 12
1c2 addi 12 0 800
1c6 store 8 14 148 4
1ca addi 15 15 400
1ce divu 15 15 12
1d2 add 14 14 15
1d4 mv 12 14
1d6 bltu 14 15 478
1da bltu 14 11 482
1de sub 12 14 11
1e2 load 15 9 12 1
1e4 store 8 12 152 4
1e8 beqz 15 522
1ea addi 15 0 -89
1ee lui 10 536879104
1f2 store 13 15 10 1
1f4 addi 10 10 -854
1f8 jal 1 278226
1fc lui 15 3758153728
200 lui 14 33554432
204 store 15 14 516 4
208 jump 298
20a load 15 18 480 4
20e call_indirect 1 15
210 mv 19 10
212 load 15 18 480 4
216 call_indirect 1 15
218 beq 19 10 530
21c load 15 18 480 4
220 load 19 8 148 4
224 call_indirect 1 15
226 bltu 19 10 628
22a lui 15 536883200
22e li 14 11
230 addi 15 15 1300
234 store 15 14 7 1
236 lui 15 999424
23a addi 15 15 576
23e sub 10 19 10
242 mulhu 11 10 15
246 load 12 9 8 2
248 li 13 0
24a mul 10 10 15
24e jal 1 450330
252 lui 15 536883200
256 load 15 15 1340 4
25a lui 14 32768
25c slli 10 10 1
25e store 15 14 8 4
260 store 15 10 108 4
262 lui 10 380928
266 addi 10 10 -1612
26a auipc 1 536489984
26e jalr 1 1 -164
272 jump 298
274 load 15 9 4 4
276 add 19 19 15
278 jump 554
27a li 14 3
27c bne 15 14 788
280 li 15 4
282 store 8 15 124 1
286 load 15 8 84 4
288 ori 15 15 8
28c store 8 15 84 4
28e lui 15 536883200
292 addi 15 15 952
296 load 14 15 125 1
29a andi 14 14 2
29c beqz 14 662
29e load 14 15 125 1
2a2 andi 14 14 252
2a6 store 15 14 125 1
2aa call_indirect 1 13
2ac lui 15 536883200
2b0 addi 15 15 564
2b4 load 13 15 8 2
2b6 load 14 8 134 2
2ba store 8 10 148 4
2be load 15 15 4 4
2c0 mul 14 14 13
2c4 addi 13 0 800
2c8 addi 14 14 400
2cc divu 14 14 13
2d0 add 13 10 14
2d4 mv 12 13
2d6 bltu 13 10 734
2da bltu 13 15 738
2de sub 12 13 15
2e2 lui 13 536883200
2e6 load 13 13 515 1
2ea store 8 12 152 4
2ee bltu 12 13 782
2f2 sub 12 12 13
2f4 lui 10 380928
2f8 addi 13 8 125
2fc mv 11 8
2fe addi 10 10 1476
302 jal 1 275476
306 mv 10 8
308 jal 1 380934
30c jump 298
30e sub 15 15 13
310 add 12 12 15
312 jump 756
314 call_indirect 1 13
316 mv 9 10
318 load 15 18 480 4
31c call_indirect 1 15
31e beq 9 10 792
322 load 15 18 480 4
326 load 19 8 152 4
32a lui 9 536883200
32e call_indirect 1 15
330 addi 9 9 564
334 bltu 19 10 856
338 lui 15 536883200
33c load 15 15 515 1
340 sub 10 19 10
344 load 19 9 8 2
348 bltu 15 10 846
34c bnez 10 862
34e load 15 8 134 2
352 mul 15 15 19
356 jump 380
358 load 15 9 4 4
35a add 19 19 15
35c jump 824
35e lui 18 536883200
362 addi 14 18 952
366 load 15 14 125 1
36a mv 12 19
36c li 13 0
36e ori 15 15 1
372 store 14 15 125 1
376 lui 14 999424
37a addi 14 14 576
37e mulhu 11 10 14
382 lui 15 536883200
386 load 20 15 1340 4
38a lui 15 32768
38c store 20 15 8 4
390 mul 10 10 14
394 jal 1 450330
398 slli 10 10 1
39a store 20 10 108 4
39e addi 14 18 952
3a2 load 15 14 125 1
3a6 andi 15 15 2
3a8 beqz 15 930
3aa load 15 14 125 1
3ae load 12 9 4 4
3b0 andi 15 15 252
3b4 store 14 15 125 1
3b8 load 15 8 134 2
3bc addi 14 0 800
3c0 mul 15 15 19
3c4 addi 15 15 400
3c8 divu 15 15 14
3cc load 14 8 152 4
3d0 add 14 14 15
3d2 mv 13 14
3d4 bltu 14 15 988
3d8 bltu 14 12 992
3dc sub 13 14 12
3e0 store 8 13 152 4
3e4 jump 774
3e6 jr 1
"""
V140_PATCHES={52: ('addi', [11, 11, 1294]), 62: ('jalr', [1, 1, -1044]), 68: ('jal', [1, 359448]), 88: ('jalr', [1, 1, 118]), 94: ('jal', [1, 409540]), 110: ('load', [13, 18, 560, 4]), 142: ('addi', [15, 15, 1032]), 172: ('addi', [15, 15, 644]), 226: ('load', [13, 13, 595, 1]), 250: ('addi', [10, 10, 1804]), 254: ('jal', [1, 275616]), 266: ('addi', [15, 15, 1380]), 272: ('addi', [10, 10, -1284]), 282: ('jalr', [1, 1, -152]), 290: ('load', [15, 15, 1420, 4]), 340: ('addi', [9, 9, 644]), 352: ('load', [15, 15, 595, 1]), 504: ('jal', [1, 278366]), 522: ('load', [15, 18, 560, 4]), 530: ('load', [15, 18, 560, 4]), 540: ('load', [15, 18, 560, 4]), 560: ('addi', [15, 15, 1380]), 590: ('jal', [1, 450826]), 598: ('load', [15, 15, 1420, 4]), 614: ('addi', [10, 10, -1284]), 622: ('jalr', [1, 1, -492]), 658: ('addi', [15, 15, 1032]), 688: ('addi', [15, 15, 644]), 742: ('load', [13, 13, 595, 1]), 766: ('addi', [10, 10, 1804]), 770: ('jal', [1, 275616]), 776: ('jal', [1, 381262]), 792: ('load', [15, 18, 560, 4]), 802: ('load', [15, 18, 560, 4]), 816: ('addi', [9, 9, 644]), 828: ('load', [15, 15, 595, 1]), 866: ('addi', [14, 18, 1032]), 902: ('load', [20, 15, 1420, 4]), 916: ('jal', [1, 450826]), 926: ('addi', [14, 18, 1032])}
TYPED=[(0, 4), (30, 5), (34, 5), (98, 2), (106, 4), (110, 2), (146, 4), (154, 4), (178, 5), (226, 4), (290, 2), (298, 5), (330, 2), (352, 4), (370, 5), (394, 2), (426, 2), (438, 5), (442, 2), (522, 2), (530, 2), (540, 2), (544, 2), (598, 2), (662, 4), (670, 4), (694, 5), (742, 4), (792, 2), (802, 2), (806, 2), (828, 4), (836, 5), (846, 5), (870, 4), (902, 2), (930, 4), (938, 4), (952, 5), (972, 2)]
QK=[(176, '9627', 'qk.c.lhu'), (276, 'f8b3', 'qk.c.sb'), (374, '9a24', 'qk.c.lhu'), (436, '9224', 'qk.c.lhu'), (482, 'dc24', 'qk.c.lbu'), (498, 'bca6', 'qk.c.sb'), (564, 'f8b3', 'qk.c.sb'), (582, '9224', 'qk.c.lhu'), (692, '9627', 'qk.c.lhu')]
STORE_SITES=[(10, 2, 8, 24, 4), (12, 2, 1, 28, 4), (14, 2, 9, 20, 4), (16, 2, 18, 16, 4), (18, 2, 19, 12, 4), (20, 2, 20, 8, 4), (74, 8, 10, 129, 1), (78, 8, 15, 124, 1), (126, 8, 15, 124, 1), (136, 8, 15, 84, 4), (162, 15, 14, 125, 1), (182, 8, 10, 148, 4), (230, 8, 12, 152, 4), (276, 15, 14, 7, 1), (296, 15, 14, 108, 4), (308, 8, 15, 136, 2), (414, 8, 13, 152, 4), (432, 13, 0, 9, 1), (454, 8, 14, 148, 4), (484, 8, 12, 152, 4), (498, 13, 15, 10, 1), (516, 15, 14, 516, 4), (564, 15, 14, 7, 1), (606, 15, 14, 8, 4), (608, 15, 10, 108, 4), (642, 8, 15, 124, 1), (652, 8, 15, 84, 4), (678, 15, 14, 125, 1), (698, 8, 10, 148, 4), (746, 8, 12, 152, 4), (882, 14, 15, 125, 1), (908, 20, 15, 8, 4), (922, 20, 10, 108, 4), (948, 14, 15, 125, 1), (992, 8, 13, 152, 4)]


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);values=list(map(int,values))
  if index and o in V140_PATCHES:op,values=V140_PATCHES[o]
  check(len(values)==len(FIELDS[op]),'B120 literalfields');d=dict(zip(FIELDS[op],values));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+o]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'B120 fullboundaries')
 for a,f in s.items():init.g(n,a,'B120 operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(1000,307,HASHES[index]),'B120 fullidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'B120 typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B120 exactQKwidth')
 edges={};calls=[]
 for a,d in n.items():
  op=d['op'];q=[] if op=='jr' else [a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  if op=='jump':q=[d['target']]
  if op=='jr':check(d['rs1']==1,'B120 ordinaryRET')
  if op=='jal':check(d['rd']==1,'B120 noexternaltaillink');calls.append(dict(offset=a-pc,target=d['target']))
  if op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B120 linkedPCpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  if op=='call_indirect':check(d['rd']==1,'B120 indirectlink');calls.append(dict(offset=a-pc,target='capturedA3' if d['rs1']==13 else 'freshclockA5'))
  check(op not in ('csr','ecall','mret') and all(z in n for z in q),'B120 fullclosedCFG');edges[a]=q
 expected=[(0x3e,0x20000332),(0x44,0x57ad8+320*index),(0x58,0x200017d6),(0x5e,0x63eda+234*index),(0xa6,'capturedA3'),(0xfe,0x43414+140*index),(0x11a,0x2000078a),(0x152,'capturedA3'),(0x1f8,0x43ed2+140*index),(0x20e,'freshclockA5'),(0x216,'freshclockA5'),(0x224,'freshclockA5'),(0x24e,0x6df1a+496*index),(0x26e,0x2000078a),(0x2aa,'capturedA3'),(0x302,0x43414+140*index),(0x308,0x5d006+328*index),(0x314,'capturedA3'),(0x31c,'freshclockA5'),(0x32e,'freshclockA5'),(0x394,0x6df1a+496*index)]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'B120 all21 linkedcalls')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and [a-pc for a,q in edges.items() if not q]==[0x142,0x3e6],'B120 allreachable/twoRET')
 groups=previous.previous.dispatch.common.sccs(edges);cycles=[g for g in groups if len(g)>1 or g[0] in edges[g[0]]]
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==STORE_SITES and len(stores)==35,'B120 all35store sites')
 check(sum(d['op']=='load' for d in n.values())==62 and sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[1,2,8,9,10,11,12,13,14,15,18,19,20],'B120 all62loads/exactGPRdefs')
 return dict(start=pc,bytes=1000,sha256=HASHES[index],instructions=list(n.values()),CFG=edges,local_CFG=edges,cyclic_SCCs=cycles,calls=calls,stores=stores,returns=[pc+0x142,pc+0x3e6],complete_local_body=True,actual_finite_return_proved=False)


def certificates(b):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=b['returns']
 def path(a,z):
  q=deque([(a,[a])]);seen=set()
  while q:
   p,s=q.popleft()
   if p==z:return s
   if p not in seen:seen.add(p);q.extend((v,s+[v]) for v in e[p])
  return None
 def suffix(a):
  ss=[s for z in ends if (s:=path(a,z)) is not None];check(bool(ss),'B120 exitwitness');return min(ss,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   w=path(pc,a)+[z]+suffix(z)[1:];check(all(v in e[u] for u,v in zip(w,w[1:])),'B120 all-edge syntaxwitness');walks.append([p-pc for p in w])
 pred={a:set() for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].add(a)
 dom={a:({pc} if a==pc else set(e)) for a in e};changed=True
 while changed:
  changed=False
  for a in e:
   if a==pc:continue
   d={a}|set.intersection(*(dom[z] for z in pred[a]))
   if d!=dom[a]:dom[a]=d;changed=True
 frame={pc+o for o in (8,0xa,0xc,0xe,0x10,0x12,0x14)}
 check(all(frame<=dom[pc+c['offset']] for c in b['calls']) and frame<=dom[pc+0x142] and pc+8 not in dom[pc+0x3e6],'B120 frame dominatescalls/normalRET only')
 check(n[0]['rs1']==10 and n[0]['imm']==124 and n[4]['target']==pc+0x3e6 and n[0x3e6]['op']=='jr','B120 N124zero rawentryRET noframe/A0defs')
 check([o for o in n if 0x12a<=o<=0x142 and n[o]['op']=='call_indirect']==[] and n[0x12a]['imm']==n[0x134]['imm']==136 and n[0x132]['imm']==1 and n[0x134]['width']==2,'B120 normalRET U16increment')
 waits=[]
 for w,f,st,base in ((0x92,0x9a,0xa2,0x8e),(0x296,0x29e,0x2a6,0x292),(0x3a2,0x3aa,0x3b4,0x39e)):
  check(n[w]['op']=='load' and n[w]['imm']==n[f]['imm']==n[st]['imm']==125 and n[w]['width']==1 and n[w+4]['imm']==2 and n[w+6]['target']==pc+w,'B120 freshbit1wait')
  mask=0x3b0 if w==0x3a2 else f+4
  check(n[mask]['imm']==252 and n[st]['width']==1 and n[base]['imm']==952+80*(pc==STARTS[1]),'B120 ownfreshclear andfixedBbase')
  check({pc+base,pc+w,pc+f,pc+mask}<=dom[pc+st] and n[st]['rs1']==n[w]['rs1'],'B120 base/read/mask precedesclear')
  waits.append(dict(wait=w,branch=w+6,fresh_clear_read=f,mask=mask,store=st,base_definition=base))
 clockA3=previous.reaching_definitions(b,13,[0xa6,0x152,0x2aa,0x314]);check(all(v==[0x6e] for v in clockA3.values()),'B120 fourcalls capturedA3 fromoneclockload')
 fresh={0x20e:0x20a,0x216:0x212,0x224:0x21c,0x31c:0x318,0x32e:0x322}
 rd=previous.reaching_definitions(b,15,list(fresh))
 for call,load in fresh.items():check(rd[hex(call)]==[load] and n[load]['imm']==480+80*(pc==STARTS[1]) and n[load]['rs1']==18,'B120 fivefreshclockcalls uniqueexplicitdefinitions')
 for br,target in ((0x218,0x212),(0x31e,0x318)):check(n[br]['target']==pc+target and n[br]['op']=='beq','B120 clockequality backedge')
 cycle_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']]
 check(cycle_offsets==[[0x92,0x96,0x98],[0x212,0x216,0x218],[0x296,0x29a,0x29c],[0x318,0x31c,0x31e],[0x3a2,0x3a6,0x3a8]] and len(walks)==336,'B120 exactfive3nodecycles/336edges')
 selected={hex(o):[a-pc for a in path(pc,pc+o)+suffix(pc+o)[1:]] for o in (0x92,0xa2,0x218,0x296,0x2a6,0x31e,0x372,0x3a2,0x3b4,0x142,0x3e6)}
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks=selected,cyclic_SCC_offsets=cycle_offsets,wait_clear_sites=waits,captured_clock_definitions=clockA3,fresh_clock_definitions=rd,actual_feasibility_progress_or_atomicity_proved=False)


def domains():
 for x in range(256):
  check((x&252)&3==0 and (x&252)&252==x&252,'B120 lowtwo clear mask')
  check((x|1)&1==1 and (x|2)&2==2 and (x|8)&8==8,'B120 arming/IRQ differentbit identities')
 for x in range(65536):check(((x+1)&65535)==(x+1)%65536,'B120 U16counter wrap')
 max_round=(65535*65535+400)//800;check(65535*65535+400<2**32 and max_round==5368545,'B120 U16pairproductplus400 neveroverflowsU32')
 for x in range(65536):
  for y in (0,1,255,32768,65535):check(((x*y+400)&0xffffffff)//800==(x*y+400)//800,'B120 roundedU16pair scalaridentity')
 for d in (0,1,65535,0x7fffffff,0xffffffff):
  wide=d*1000000;check(wide<2**52 and ((wide>>32)<<32)+(wide&0xffffffff)==wide,'B120 MULHU/MUL numeratorpair')
 check(100-10!=100%10,'B120 onesubtract notgenericmodulo withoutadditionalrange invariant')
 return dict(mask_byte_cases=256,U16counter_cases=65536,U16pair_rounding_cases=327680,rounded_product_interval=[0,max_round],fullword_numerator_upper_bound_exclusive=2**52,
  helper_call_argument_domain='A1:A0=U32delta*1000000;A3:A2=zeroextendedU16K;Kpositive notguarded;config-specifichelperreplyproof doesnotcoverthisdomain',
  corrected_scalars_are_not_proven_generic_modulo_time_or_monotonic_clock_values=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,1000)
 check(sparse.captured(mem,pc,1000)==raw,'B120 complete strictHEX');b=body(raw,index);cert=certificates(b);n={d['pc']-pc:d for d in b['instructions']}
 pp=previous.STARTS[index][1];pr=init.binding.take(data,pp,18);check(sparse.captured(mem,pp,18)==pr,'B120 reusedpublisher strictHEX');pub=previous.body(pr,1,index);pn={d['pc']-pp:d for d in pub['instructions']}
 B=0x200033b8+80*index;check(pn[0]['imm']+pn[8]['imm']==pc and pn[4]['imm']+pn[0xc]['imm']==B+120,'B120 publisher joinscomplete1000Btarget notparser')
 dispatch=previous.previous.dispatch;dp=dispatch.STARTS[index];dr=init.binding.take(data,dp,dispatch.SIZES[index]);tr=init.binding.take(data,dispatch.TABLES[index],52)
 check(sparse.captured(mem,dp,len(dr))==dr and sparse.captured(mem,dispatch.TABLES[index],52)==tr,'B120 reuseddispatch/table strictHEX');db=dispatch.body(dr,tr,index);dn={d['pc']-dp:d for d in db['instructions']};call=0x372+2*index;load=call-4
 check(dn[load]['imm']==120 and dn[call]['op']=='call_indirect' and dn[call-2]['rs2']==8,'B120 dispatcher freshword/entryN joins')
 check(previous.reaching_definitions(db,9,[load])=={hex(load):[0x28]},'B120 dispatch fixedBsource conditionalcallee preservation')
 irq=previous.previous;ip=irq.STARTS[index];ir=init.binding.take(data,irq.SOURCES[index],446);check(sparse.captured(mem,irq.SOURCES[index],446)==ir,'B120 reusedIRQzero strictHEX');ib=irq.body(ir,index);inn={d['pc']-ip:d for d in ib['instructions']}
 check(inn[0x130]['imm']+0x20003000==B and inn[0x140]['imm']==2 and inn[0x144]['imm']==125,'B120 IRQOR2 actualsamefixedB125')
 hook=irq.previous.hook;hs,delta,sh,_=hook.DETAILS[index];hr=init.binding.take(data,hs,22);check(sparse.captured(mem,hs,22)==hr,'B120 reusedsetter strictHEX');setter=hook.body(hr,'setter',0x2000078a,delta,sh)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(src+0x2000078a-dest==hs and 0x2000078a+22<=end,'B120 setter firstcopy')
 callback=0x5c9b4+328*index
 check(n[0x106]['imm']+n[0x110]['imm']==n[0x262]['imm']+n[0x266]['imm']==callback,'B120 bothsetter literal actualtarget')
 check(n[0xf0]['imm']+n[0xfa]['imm']==n[0x2f4]['imm']+n[0x2fe]['imm']==pc and n[0xf4]['imm']==n[0x2f8]['imm']==125,'B120 explicitself/N125 borrowedarguments')
 check(n[0x236]['imm']+n[0x23a]['imm']==n[0x376]['imm']+n[0x37a]['imm']==1000000 and n[0x242]['op']==n[0x37e]['op']=='mulhu' and n[0x24a]['op']==n[0x390]['op']=='mul' and n[0x248]['imm']==n[0x36c]['imm']==0,'B120 encodedwideproduct/helperhighdivisorzero')
 check(n[0x1fc]['imm']+n[0x204]['imm']==0xe000e204 and n[0x200]['imm']==0x02000000,'B120 fixedCPUaddress wordstore notphysicaleffect')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=cert,reused_publisher=pub,reused_dispatch=dict(start=dp,bytes=len(dr),sha256=db['sha256'],B120_load=dn[load],B120_call=dn[call]),
  reused_IRQ=dict(start=ip,bytes=446,sha256=ib['sha256'],B125_OR2_store=inn[0x144]),reused_setter=setter,hook_callback_literal=callback,
  contract=['entryN124zero ->REToriginalA0=N,noframe/call/datastore;nonzero32Bframe RA/S0..S4;normalRET freshN136incrementlow16,restoreframe,thenliveA0notfixedstatus',
   'optionalN124==18 andfreshU16N130==freshU16N136 ->copy5(N160,fixedsource),callee57ad8/57c18(N160),N129=low8reply,N124=4;laterfreshN124 independent',
   'three fixedB125bit1 pollingloops;afterexit separatelyfreshB125 AND252 clearbits0/1. IRQzeroOR2 fitsbit1 underactualorder/retention,notatomicconsume/progress guarantee;thirdpath ownOR1 beforehelperandwait',
   'fourindirectcalls useA3 capturedoncefromclockslot beforebranch;fiveothercalls havefreshslot loads;two equalitypollcycles havenotimeout/no monotonicclock proof',
   'N134 andscaleU16 products+400 fitU32, DIVU800 rounding to0..5368545 underlivecallee preservation;oneconditionalmod32subtract isnotproven genericmodulo/invariant',
   'twoMULHU/MUL requestspassU32delta*1000000 asA1:A0,zeroextendedU16K asA3:A2;Kzero notexcluded;callee6df1a/6e10a replydomain notcovered byconfig-specific proof;H108=low32(2*thenA0)',
   'service43414/434a0 receives(selfliteral,N,livecomputedA2,N125address);no pointersave/noescape guarantee. RAMsetterreceives5c9b4/5cafc,notcompletion65de6;S7=11 writtenbeforepublication onsomepaths',
   'no directS36/N80packetread inthisbody;writesN160viarequestedcopy,metadataN124/129/136/148/152/84 andthroughfreshN172+9/+10;N172maydifferfromearliergate. Noactualbufferproducer/extent/identity proved'],
  required_explicit_N_extent=176,dynamic_N172_required_extent=11,actual_installed_binding_provider_effects_clock_progress_pointer_retention_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-B120-target-waits-requests-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=2000,complete_phase_body_instructions=614,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['privatecallees200017d6/43414/5d006 andpublishedcallback5c9b4/5cafc','arithmetichelper newfullwordnumerator/zero-divisor domain','actualdata producer/ingresslength/provider/callbackorder/fullownershiplifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],1000);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-STARTS[i];size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B120 instructionmutation escaped')
   mutations+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B120 typedmutation escaped')
   typed+=1
 check((mutations,typed)==(614,80),'B120 mutationcensus')
 print('PASS:614 instruction/80 typed-load mutations rejected;fullCFG/store/frame/wait/captured-vs-fresh clock certificates')


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
 else:check(OUT.read_bytes()==encoded,'B120 exactledger replay')
 print('PASS:2000B/614i complete B120targets;strictHEX;three B125wait/clear joins;all-edge witnesses;exactledger')
 print('PASS:NO target execution/emulation;actualproviders/clockprogress/dataextent/order/lifetimes UNPROVED')


if __name__=='__main__':main()
