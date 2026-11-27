"""Offline ID11 B0 consumer and selected-word release wrapper contracts.
Original complete operands, immutable CFG paths and host scalar equations only.
No target execution/emulation, provider, RAM/heap/list or hardware model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_task8_forward_static as previous
import check_v4160_id11_outer_tail_static as origin
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-typeb0-consumer-static.json')
PARTS=('handler','releasewrapper')
STARTS=((0x4d1b0,0x4a7ba),(0x4d248,0x4a852))
SIZES=(780,28)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('e6dcfe72e9043b2490505b1ac7f313a843626ea532c0c77c68b855ac0635b08d', '772d44d3dc47d5311512b64fd11e34fb06d1dc1f75dd87cfffc7d439a57c2e11'), ('e31639d7312496348ca334dd153889cdb88ef00a5f6bd168633ce7c2f2c435c5', 'c6af516ea0cc40b70b92c49decaa4692f4d55bdadd50ee4dce0ed5307a31d6c4'))
COUNTS=((277, 11), (277, 11))
TYPED_LOADS=({'handler': ((14, 4), (168, 4), (386, 4), (390, 5), (570, 4), (574, 5), (642, 2)), 'releasewrapper': ()}, {'handler': ((14, 4), (168, 4), (386, 4), (390, 5), (570, 4), (574, 5), (642, 2)), 'releasewrapper': ()})
LITERALS=(
{
'handler':'''
000 slli 15 11 16
004 srai 15 15 16
006 bge 15 0 776
00a lui 15 536883200
00e load 10 15 -289 1
012 addi 2 2 -48
014 store 2 8 40 4
016 store 2 22 16 4
018 store 2 1 44 4
01a store 2 9 36 4
01c store 2 18 32 4
01e store 2 19 28 4
020 store 2 20 24 4
022 store 2 21 20 4
024 mv 22 11
026 auipc 1 536555520
02a jalr 1 1 182
02e mv 8 10
030 beqz 10 122
032 load 14 10 0 1
034 addi 15 0 176
038 bne 14 15 116
03c lui 9 536883200
040 li 15 1
042 addi 9 9 -124
046 store 2 15 9 1
048 load 15 9 0 4
04a store 2 0 10 2
04e bnez 15 148
050 jal 1 317784
054 lui 11 16384
056 addi 11 11 1795
05a auipc 1 536555520
05e jalr 1 1 -458
062 store 9 10 0 4
064 bnez 10 148
066 load 15 2 9 1
068 beqz 15 116
06a load 11 8 4 1
06c addi 10 8 8
070 jal 1 305082
074 mv 10 8
076 jal 1 274874
07a load 1 2 44 4
07c load 8 2 40 4
07e lui 10 32768
080 xor 10 22 10
084 load 9 2 36 4
086 load 18 2 32 4
088 load 19 2 28 4
08a load 20 2 24 4
08c load 21 2 20 4
08e load 22 2 16 4
090 addi 2 2 48
092 jr 1
094 lui 20 536883200
098 li 12 24
09a li 11 0
09c addi 10 20 340
0a0 auipc 1 536555520
0a4 jalr 1 1 332
0a8 load 18 8 4 1
0ac li 15 2
0ae addi 9 20 340
0b2 mv 19 20
0b4 addi 21 20 340
0b8 bne 18 15 268
0bc jal 1 317784
0be store 9 10 0 2
0c0 load 10 8 2 2
0c2 addi 11 20 340
0c6 jal 1 282074
0ca load 14 8 2 2
0cc load 15 9 0 2
0ce load 13 8 8 2
0d0 bnez 10 232
0d2 bltu 13 15 216
0d6 store 8 15 8 2
0d8 load 11 8 8 2
0da mv 10 14
0dc jal 1 303616
0e0 mv 10 8
0e2 jal 1 302932
0e6 jump 102
0e8 bltu 13 15 238
0ec store 8 15 8 2
0ee load 15 8 8 2
0f0 li 11 22
0f2 addi 13 19 340
0f6 li 12 3
0f8 mv 10 14
0fa store 21 15 0 2
0fe jal 1 303284
102 li 11 3
104 beqz 10 224
106 addi 10 19 340
10a jump 450
10c li 15 6
10e bne 18 15 320
112 addi 11 2 10
116 mv 10 8
118 jal 1 313338
11c mv 9 10
11e beqz 10 224
120 li 15 22
122 bne 9 15 510
126 addi 18 18 1
128 load 10 8 2 2
12a andi 18 18 255
12e li 11 22
130 addi 13 19 340
134 mv 12 18
136 jal 1 303284
13a mv 11 18
13c beqz 10 224
13e jump 262
140 li 15 8
142 bne 18 15 338
146 addi 11 2 10
14a mv 10 8
14c jal 1 314516
150 jump 284
152 li 15 10
154 bne 18 15 456
158 load 10 8 8 2
15a addi 11 2 12
15c auipc 1 536555520
160 jalr 1 1 1852
164 mv 18 10
166 beq 10 0 664
16a load 10 8 2 2
16c lui 12 65536
16e addi 13 2 14
172 li 14 21
174 addi 12 12 -1
176 li 11 11
178 jal 1 303706
17c store 9 10 4 4
17e mv 13 10
180 beqz 10 504
182 load 17 8 4 1
186 load 16 2 14 2
18a load 12 2 12 2
18c load 10 8 2 2
18e li 15 0
190 addi 14 20 340
194 mv 11 18
196 jal 1 312336
19a mv 9 10
19c bne 10 0 634
1a0 load 10 8 2 2
1a2 addi 11 20 340
1a6 jal 1 282546
1aa beqz 10 224
1ac load 10 8 2 2
1ae addi 13 20 340
1b2 li 12 11
1b4 li 11 22
1b6 jal 1 303284
1ba beqz 10 224
1bc li 11 11
1be addi 10 20 340
1c2 jal 1 305082
1c6 jump 224
1c8 li 15 12
1ca bne 18 15 672
1ce load 10 8 8 2
1d0 addi 11 2 12
1d2 auipc 1 536555520
1d6 jalr 1 1 1734
1da mv 9 10
1dc beqz 10 664
1de load 10 8 2 2
1e0 lui 12 65536
1e2 addi 13 2 14
1e6 li 14 22
1e8 addi 12 12 -1
1ea li 11 13
1ec jal 1 303706
1f0 store 21 10 4 4
1f4 mv 13 10
1f6 bnez 10 570
1f8 load 15 8 8 2
1fa li 9 17
1fc store 2 15 10 2
1fe load 14 8 1 1
200 li 15 20
202 beq 14 15 224
206 load 15 8 4 1
208 load 10 8 2 2
20a addi 11 19 340
20e store 21 15 0 1
212 load 15 2 10 2
214 store 21 9 4 1
218 store 21 15 2 2
21c jal 1 280780
220 beq 10 0 224
224 load 10 8 2 2
226 addi 13 19 340
22a li 12 1
22c li 11 22
22e jal 1 303284
232 beq 10 0 224
236 li 11 1
238 jump 262
23a load 17 8 4 1
23e load 16 2 14 2
242 load 15 8 10 2
244 load 12 2 12 2
246 load 10 8 2 2
248 mv 11 9
24a addi 14 20 340
24e jal 1 312336
252 mv 9 10
254 bnez 10 634
256 load 10 8 2 2
258 addi 11 20 340
25c jal 1 282630
260 beq 10 0 224
264 load 10 8 2 2
266 li 11 22
268 addi 13 20 340
26c li 12 13
26e jal 1 303284
272 li 11 13
274 beq 10 0 224
278 jump 262
27a li 15 22
27c bne 9 15 642
280 li 9 0
282 load 10 21 4 4
286 auipc 1 536555520
28a jalr 1 1 -806
28e beq 9 0 224
292 load 15 8 8 2
294 store 2 15 10 2
296 jump 510
298 load 15 8 8 2
29a li 9 1
29c store 2 15 10 2
29e jump 510
2a0 li 15 14
2a2 bne 18 15 690
2a6 addi 11 2 10
2aa mv 10 8
2ac jal 1 313002
2b0 jump 284
2b2 li 15 16
2b4 bne 18 15 708
2b8 addi 11 2 10
2bc mv 10 8
2be jal 1 314026
2c2 jump 284
2c4 li 15 18
2c6 bne 18 15 730
2ca addi 12 2 9
2ce addi 11 2 10
2d2 mv 10 8
2d4 jal 1 310726
2d8 jump 284
2da li 15 22
2dc bne 18 15 758
2e0 addi 11 2 10
2e4 mv 10 8
2e6 jal 1 310488
2ea mv 9 10
2ec bne 10 0 288
2f0 store 2 0 9 1
2f4 jump 224
2f6 li 15 24
2f8 bne 18 15 224
2fc addi 11 2 10
300 mv 10 8
302 jal 1 310214
306 jump 284
308 li 10 0
30a jr 1
''',
'releasewrapper':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 jal 1 302540
008 beqz 10 22
00a load 1 2 12 4
00c addi 2 2 16
00e auipc 6 536567808
012 jalr 0 6 -1720
016 load 1 2 12 4
018 addi 2 2 16
01a jr 1
''',
},
{
'handler':'''
000 slli 15 11 16
004 srai 15 15 16
006 bge 15 0 776
00a lui 15 536883200
00e load 10 15 -209 1
012 addi 2 2 -48
014 store 2 8 40 4
016 store 2 22 16 4
018 store 2 1 44 4
01a store 2 9 36 4
01c store 2 18 32 4
01e store 2 19 28 4
020 store 2 20 24 4
022 store 2 21 20 4
024 mv 22 11
026 auipc 1 536555520
02a jalr 1 1 30
02e mv 8 10
030 beqz 10 122
032 load 14 10 0 1
034 addi 15 0 176
038 bne 14 15 116
03c lui 9 536883200
040 li 15 1
042 addi 9 9 -44
046 store 2 15 9 1
048 load 15 9 0 4
04a store 2 0 10 2
04e bnez 15 148
050 jal 1 317936
054 lui 11 16384
056 addi 11 11 1795
05a auipc 1 536555520
05e jalr 1 1 -610
062 store 9 10 0 4
064 bnez 10 148
066 load 15 2 9 1
068 beqz 15 116
06a load 11 8 4 1
06c addi 10 8 8
070 jal 1 305234
074 mv 10 8
076 jal 1 275014
07a load 1 2 44 4
07c load 8 2 40 4
07e lui 10 32768
080 xor 10 22 10
084 load 9 2 36 4
086 load 18 2 32 4
088 load 19 2 28 4
08a load 20 2 24 4
08c load 21 2 20 4
08e load 22 2 16 4
090 addi 2 2 48
092 jr 1
094 lui 20 536883200
098 li 12 24
09a li 11 0
09c addi 10 20 420
0a0 auipc 1 536555520
0a4 jalr 1 1 180
0a8 load 18 8 4 1
0ac li 15 2
0ae addi 9 20 420
0b2 mv 19 20
0b4 addi 21 20 420
0b8 bne 18 15 268
0bc jal 1 317936
0be store 9 10 0 2
0c0 load 10 8 2 2
0c2 addi 11 20 420
0c6 jal 1 282222
0ca load 14 8 2 2
0cc load 15 9 0 2
0ce load 13 8 8 2
0d0 bnez 10 232
0d2 bltu 13 15 216
0d6 store 8 15 8 2
0d8 load 11 8 8 2
0da mv 10 14
0dc jal 1 303768
0e0 mv 10 8
0e2 jal 1 303084
0e6 jump 102
0e8 bltu 13 15 238
0ec store 8 15 8 2
0ee load 15 8 8 2
0f0 li 11 22
0f2 addi 13 19 420
0f6 li 12 3
0f8 mv 10 14
0fa store 21 15 0 2
0fe jal 1 303436
102 li 11 3
104 beqz 10 224
106 addi 10 19 420
10a jump 450
10c li 15 6
10e bne 18 15 320
112 addi 11 2 10
116 mv 10 8
118 jal 1 313490
11c mv 9 10
11e beqz 10 224
120 li 15 22
122 bne 9 15 510
126 addi 18 18 1
128 load 10 8 2 2
12a andi 18 18 255
12e li 11 22
130 addi 13 19 420
134 mv 12 18
136 jal 1 303436
13a mv 11 18
13c beqz 10 224
13e jump 262
140 li 15 8
142 bne 18 15 338
146 addi 11 2 10
14a mv 10 8
14c jal 1 314668
150 jump 284
152 li 15 10
154 bne 18 15 456
158 load 10 8 8 2
15a addi 11 2 12
15c auipc 1 536555520
160 jalr 1 1 1700
164 mv 18 10
166 beq 10 0 664
16a load 10 8 2 2
16c lui 12 65536
16e addi 13 2 14
172 li 14 21
174 addi 12 12 -1
176 li 11 11
178 jal 1 303858
17c store 9 10 4 4
17e mv 13 10
180 beqz 10 504
182 load 17 8 4 1
186 load 16 2 14 2
18a load 12 2 12 2
18c load 10 8 2 2
18e li 15 0
190 addi 14 20 420
194 mv 11 18
196 jal 1 312488
19a mv 9 10
19c bne 10 0 634
1a0 load 10 8 2 2
1a2 addi 11 20 420
1a6 jal 1 282694
1aa beqz 10 224
1ac load 10 8 2 2
1ae addi 13 20 420
1b2 li 12 11
1b4 li 11 22
1b6 jal 1 303436
1ba beqz 10 224
1bc li 11 11
1be addi 10 20 420
1c2 jal 1 305234
1c6 jump 224
1c8 li 15 12
1ca bne 18 15 672
1ce load 10 8 8 2
1d0 addi 11 2 12
1d2 auipc 1 536555520
1d6 jalr 1 1 1582
1da mv 9 10
1dc beqz 10 664
1de load 10 8 2 2
1e0 lui 12 65536
1e2 addi 13 2 14
1e6 li 14 22
1e8 addi 12 12 -1
1ea li 11 13
1ec jal 1 303858
1f0 store 21 10 4 4
1f4 mv 13 10
1f6 bnez 10 570
1f8 load 15 8 8 2
1fa li 9 17
1fc store 2 15 10 2
1fe load 14 8 1 1
200 li 15 20
202 beq 14 15 224
206 load 15 8 4 1
208 load 10 8 2 2
20a addi 11 19 420
20e store 21 15 0 1
212 load 15 2 10 2
214 store 21 9 4 1
218 store 21 15 2 2
21c jal 1 280928
220 beq 10 0 224
224 load 10 8 2 2
226 addi 13 19 420
22a li 12 1
22c li 11 22
22e jal 1 303436
232 beq 10 0 224
236 li 11 1
238 jump 262
23a load 17 8 4 1
23e load 16 2 14 2
242 load 15 8 10 2
244 load 12 2 12 2
246 load 10 8 2 2
248 mv 11 9
24a addi 14 20 420
24e jal 1 312488
252 mv 9 10
254 bnez 10 634
256 load 10 8 2 2
258 addi 11 20 420
25c jal 1 282778
260 beq 10 0 224
264 load 10 8 2 2
266 li 11 22
268 addi 13 20 420
26c li 12 13
26e jal 1 303436
272 li 11 13
274 beq 10 0 224
278 jump 262
27a li 15 22
27c bne 9 15 642
280 li 9 0
282 load 10 21 4 4
286 auipc 1 536555520
28a jalr 1 1 -958
28e beq 9 0 224
292 load 15 8 8 2
294 store 2 15 10 2
296 jump 510
298 load 15 8 8 2
29a li 9 1
29c store 2 15 10 2
29e jump 510
2a0 li 15 14
2a2 bne 18 15 690
2a6 addi 11 2 10
2aa mv 10 8
2ac jal 1 313154
2b0 jump 284
2b2 li 15 16
2b4 bne 18 15 708
2b8 addi 11 2 10
2bc mv 10 8
2be jal 1 314178
2c2 jump 284
2c4 li 15 18
2c6 bne 18 15 730
2ca addi 12 2 9
2ce addi 11 2 10
2d2 mv 10 8
2d4 jal 1 310878
2d8 jump 284
2da li 15 22
2dc bne 18 15 758
2e0 addi 11 2 10
2e4 mv 10 8
2e6 jal 1 310640
2ea mv 9 10
2ec bne 10 0 288
2f0 store 2 0 9 1
2f4 jump 224
2f6 li 15 24
2f8 bne 18 15 224
2fc addi 11 2 10
300 mv 10 8
302 jal 1 310366
306 jump 284
308 li 10 0
30a jr 1
''',
'releasewrapper':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 jal 1 302692
008 beqz 10 22
00a load 1 2 12 4
00c addi 2 2 16
00e auipc 6 536567808
012 jalr 0 6 -1872
016 load 1 2 12 4
018 addi 2 2 16
01a jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B0 literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'B0 typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B0 complete boundaries '+part)
 for a,f in s.items():init.g(n,a,'B0 operand '+part+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B0 completeidentity '+part)
 edges={};calls=[];tails=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B0 ordinaryRET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   if op=='jal':target=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1'],'B0 adjacentaddresspair')
    target=(a-4+u['imm']+d['imm'])&0xfffffffe
   check(d['rd'] in (0,1),'B0 link classification')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=target,new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=target))
  check(all(z in n for z in q),'B0 completeclosedlocalCFG');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'B0 completereachableDAG')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 if part=='handler':
  check(len(stores)==24 and len(calls)==33 and not tails and returns==[pc+0x92,pc+0x30a],'B0 exactstore/call/returncensus')
  saves={(v['rs2'],v['imm']) for a,v in n.items() if a<pc+0x24 and v['op']=='store'}
  restores={(v['rd'],v['imm']) for a,v in n.items() if pc+0x7a<=a<=pc+0x8e and v['op']=='load' and v['rs1']==2}
  check(saves==restores=={(1,44),(8,40),(9,36),(18,32),(19,28),(20,24),(21,20),(22,16)},'B0 48Bframe saves/restores')
  msgstores=[d for d in stores if d['base']==8]
  check(msgstores==[dict(offset=0xd6,base=8,source=15,imm=8,bytes=2),dict(offset=0xec,base=8,source=15,imm=8,bytes=2)],'B0 exactdirectmessage mutationstoU16M8only')
 else:
  check(calls==[dict(offset=4,target=previous.STARTS[index][1])] and tails==[dict(offset=0x12,target=0x20000110,new_link=False)],'B0 leafselectedword ->privatefreeunlinkedtail')
  check(returns==[pc+0x1a] and stores==[dict(offset=2,base=2,source=1,imm=12,bytes=4)],'B0 releasewrapper exactsavedRA/store/RET')
  check(n[pc+0xa]['rd']==1 and n[pc+0xc]['imm']==16 and n[pc+0x16]['rd']==1 and n[pc+0x18]['imm']==16,'B0 releasewrapper restoresbeforetailorRET')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=returns,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def witnesses(h,w):
 common_entry={6:0xa,0x30:0x32,0x38:0x3c}
 allocated={**common_entry,0x4e:0x94}
 selectors={0xb8:0x10c,0x10e:0x140,0x142:0x152,0x154:0x1c8,0x1ca:0x2a0,0x2a2:0x2b2,0x2b4:0x2c4}
 chosen={
  'no_bit15':common.walk(h,{6:0x308}),
  'receive_null':common.walk(h,{6:0xa,0x30:0x7a}),
  'other_type':common.walk(h,{6:0xa,0x30:0x32,0x38:0x74}),
  'B0_cachednull_allocnull_flag1':common.walk(h,{**common_entry,0x4e:0x50,0x64:0x66,0x68:0x6a}),
  'B0_cachednull_allocnull_flag0':common.walk(h,{**common_entry,0x4e:0x50,0x64:0x66,0x68:0x74}),
  'opcode18_helper_getsflag_thenzero':common.walk(h,{**allocated,**selectors,0x2c6:0x2ca,0x11e:0xe0,0x68:0x74}),
  'opcode22_helperzero_clearsflag':common.walk(h,{**allocated,**selectors,0x2c6:0x2da,0x2dc:0x2e0,0x2ec:0x2f0,0x68:0x74}),
  'unsupported_opcode_cleanup':common.walk(h,{**allocated,**selectors,0x2c6:0x2da,0x2dc:0x2f6,0x2f8:0xe0,0x68:0x6a})}
 seqs=task8.v34.allocation.previous.dag_paths(h)
 for seq in seqs:
  if 0x32 in seq:check(0x76 in seq and 0x80 in seq and seq.index(0x76)<seq.index(0x80),'B0 allnonnullmessagepaths publiccleanupthenfullXOR')
  if 0x30 in seq:check(0x80 in seq,'B0 bit15receive pathsXOR')
  if 0x70 in seq:check(seq[seq.index(0x68)+1]==0x6a and seq.index(0x70)<seq.index(0x76),'B0 freshflag gatesselectedwordreleasebeforepubliccleanup')
  if 0x2f0 in seq:check(0x2e6 in seq and seq[seq.index(0x2ec)+1]==0x2f0,'B0 explicitflagclear onlycase22normal0branch')
 check(0x70 in chosen['B0_cachednull_allocnull_flag1'] and 0x70 not in chosen['B0_cachednull_allocnull_flag0'],'B0 commonflag independent of cachedallocation failure')
 check(0x2ca in chosen['opcode18_helper_getsflag_thenzero'],'B0 case18 passesborrowedflagaddress')
 check(0x70 not in chosen['opcode22_helperzero_clearsflag'] and 0x76 in chosen['opcode22_helperzero_clearsflag'],'B0 case22directflagclear allowsmessagecleanup while skippingselectedwordcall')
 zero=common.walk(w,{8:0x16});tail=common.walk(w,{8:0xa})
 wn={d['pc']-w['start']:d for d in w['instructions']}
 check(not any(wn[o].get('rd')==10 for o in tail[tail.index(4)+1:]),'B0 selectedwordforwardedunchangedtotail')
 return {'selected_handler_paths':chosen,'syntactic_DAG_paths':len(seqs),'allpaths_sha256':sha256(json.dumps(seqs,separators=(',',':')).encode()).hexdigest(),
  'releasewrapper_zero_RET':zero,'releasewrapper_nonzero_unlinked_tail':tail,
  'actual_path_feasibility_privatefree_completion_or_payload_lifetime_proved':False}


CASE_ROWS=((2,0xbc,0x4d958),(6,0x118,0x4c7fa),(8,0x14c,0x4cc94),(10,0x160,0x20000a48),(12,0x1d6,0x20000a48),
 (14,0x2ac,0x4c6aa),(16,0x2be,0x4caaa),(18,0x2d4,0x4bdc6),(22,0x2e6,0x4bcd8),(24,0x302,0x4bbc6))


def domains():
 for low in range(65536):
  signed=low if low<32768 else low-65536
  check((signed<0)==bool(low&0x8000),'B0 signextendedlow16eventbit15')
 for E in (0x8000,0x8001,0x18000,0xffff8001):check((E^0x8000)&0xffff0000==E&0xffff0000,'B0 full32XOR preserveshigh16')
 fromcaller=previous.previous.domains()['other_callback_opcodes'];dispatch={r[0] for r in CASE_ROWS}
 check(set(fromcaller)-{4,30}==dispatch,'B0 stablecalleropcodes exactlymatch10consumer cases')
 for old in range(65536):
  for count in (0,1,65535):check(0<=min(old,count)<=65535,'B0 opcode2unsignedhalfwordminimum domain')
 check(1+1+2<=4 and set(range(9,16)).isdisjoint(range(16,48)),'B0 flags/halfwords ownframe avoidsavedslots')
 check(8+24==32 and all(8+off+4<=32 for off in (0,4,8,12)),'B0 forwardcopiedrecord/selectedwordgeometry conditional')
 return {'event_low16_cases':65536,'opcode2_halfword_minimum_samples':196608,'stablecaller_case_opcodes':sorted(dispatch),
  'consumer_unknown_type_freshness_retention_or_body_extent_proved':False}


def profile(data,hexraw,index,parent):
 bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
 h,w=bs['handler'],bs['releasewrapper'];hp,wp=STARTS[index];hn={d['pc']-hp:d for d in h['instructions']}
 delta=152*index;G=0x20003000;receivebyte=G-289+80*index;sendbyte=G-274+80*index;cached=G-124+80*index;scratch=G+340+80*index
 check(hn[0xe]['imm']+G==receivebyte and hn[0x42]['imm']+G==cached,'B0 receiveIDbyte/cachedstatepointer roles')
 check(hn[0x9c]['imm']+G==hn[0xae]['imm']+G==hn[0xb4]['imm']+G==scratch,'B0 shared24Bscratchbase')
 check(hn[0x34]['imm']==176 and hn[0x46]['imm']==9 and hn[0x40]['imm']==1 and hn[0x4a]['imm']==10,'B0 typegate andflag1/halfword0 initialization')
 callmap={r['offset']:r['target'] for r in h['calls']}
 expected={0x2a:0x2000028c,0x50:0x4d958+delta,0x5e:0x20000040,0x70:wp,0x76:0x431ba+140*index,0xa4:0x2000039c,
  0xbc:0x4d958+delta,0xc6:0x44dda+148*index,0xdc:0x4a200+delta,0xe2:0x49f54+delta,0xfe:0x4a0b4+delta,
  0x118:0x4c7fa+delta,0x136:0x4a0b4+delta,0x14c:0x4cc94+delta,0x160:0x20000a48,0x178:0x4a25a+delta,
  0x196:0x4c410+delta,0x1a6:0x44fb2+148*index,0x1b6:0x4a0b4+delta,0x1c2:wp,0x1d6:0x20000a48,0x1ec:0x4a25a+delta,
  0x21c:0x448cc+148*index,0x22e:0x4a0b4+delta,0x24e:0x4c410+delta,0x25c:0x45006+148*index,0x26e:0x4a0b4+delta,
  0x28a:0x20000110,0x2ac:0x4c6aa+delta,0x2be:0x4caaa+delta,0x2d4:0x4bdc6+delta,0x2e6:0x4bcd8+delta,0x302:0x4bbc6+delta}
 check(callmap==expected,'B0 all33originalcallee targets version-specific deltas')
 check(hn[0x6c]['imm']==8 and hn[0x6a]['imm']==4 and hn[0x80]['op']=='xor','B0 cleanuporiginalM8record/opcode thenfull32XOR')
 check(hn[0x2ca]['imm']==9 and hn[0x2ce]['imm']==10 and hn[0x2f0]['rs2']==0 and hn[0x2f0]['imm']==9,'B0 case18 borrowedflag;case22directclear')
 check(hn[0x282]['imm']==4 and hn[0x282]['rs1']==21,'B0 separateprivatefree usesfreshscratch4 notoriginalM8')
 check(all(hn[o]['op']=='bltu' and (hn[o]['rs1'],hn[o]['rs2'])==(13,15) for o in (0xd2,0xe8)) and all(hn[o]['rs2']==15 and hn[o]['rs1']==8 and hn[o]['imm']==8 for o in (0xd6,0xec)),'B0 opcode2 capturedunsignedminimum conditionalstore operands')
 # Prior initializer and registration proofs establish matching conditional ID11.
 op=origin.STARTS[index][0];ob=origin.body(init.binding.take(data,op,62),'initializer',index);on={d['pc']-op:d for d in ob['instructions']}
 check(on[20]['imm']+G==receivebyte and on[40]['imm']+G==sendbyte and on[20]['rs2']==on[40]['rs2']==8,'B0 twofreshIDbytes derivefromsame preservedentryS0')
 d=origin.role.DETAILS[index];outer=origin.role.body(init.binding.take(data,d['entry'],112),'entry',index);en={x['pc']-d['entry']:x for x in outer['instructions']}
 check(en[88]['imm']+en[92]['imm']==hp and en[96]['target']==d['reg'] and en[100]['target']==op,'B0 conditionalregisteredID11matchinghandler/initializer')
 cb=previous.previous.body(init.binding.take(data,previous.previous.STARTS[index],438),index);cn={x['pc']-cb['start']:x for x in cb['instructions']}
 check(cn[0xc0]['imm']+G==cn[0xc8]['imm']+G==sendbyte,'B0 senderdestination source joinsID11publication')
 check(parent['bodies']['forwarder']['start']==previous.STARTS[index][0],'B0 parentforwarder identityjoin')
 # Reuse existing pointer leaf proof and original public message cleanup body.
 leaf=previous.body(init.binding.take(data,previous.STARTS[index][1],126),'pointerleaf',index);previous.leaf_intervals(leaf)
 public=common.dealloc.DETAILS[index][0];pubraw=init.binding.take(data,public,78)
 check(public==expected[0x76] and sha256(pubraw).hexdigest()==common.dealloc.DETAILS[index][-2],'B0 publiccleanup unchanged')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for part,b in bs.items():
  check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'B0 originalstrictHEX backing')
  receipts.append({'part':part,'source':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
 casefront=[dict(opcode=o,first_call_offset=off,target=callmap[off],nested_effects_proved=False) for o,off,_ in CASE_ROWS]
 return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{part:common.certificates(b) for part,b in bs.items()},
  'witnesses':witnesses(h,w),'case_call_frontier':casefront,'globals':dict(receive_task_byte=receivebyte,B0_send_task_byte=sendbyte,cached_state_pointer=cached,scratch24=scratch),
  'conditional_task_source':{'initializer_start':op,'initializer_sha256':ob['sha256'],'outer_start':d['entry'],'outer_sha256':outer['sha256'],'selected_ID':11,'received_and_sent_byte_equality_only_if_preserved':True,'actualinstalledbinding_allwriters_orqueueprogress_proved':False},
  'handler_contract':['noentrybit15 ->0 beforeframe;bit15 receivesfreshsavedIDbyte;null ->fullE XOR8000;nonnulltype!=B0 ->publiccleanuporiginalM thenXOR',
   'typeB0 initializesSP9releaseflag1,SP10halfword0;cachedstate0 ->sizegetter thenallocation(tag4703),storesreply. Null afterallocation stilljoinsflagcleanup',
   'cachedstatepresent ->fillsharedscratch24zero,readfreshM4opcode;10knowncases plusdefault. Nestedcaseeffects remainopaque;opcode2canchangeU16M8;10/12haveextrascratch/privatecleanup',
   'opcode18 helper explicitlyborrowsSP9flagandSP10halfword;opcode22 helperreturn0 writesSP9=0. Commoncaseposthelper49f54(M) remainsopaque',
   'commonfreshflag9nonzero ->releasewrapper(M8,freshU8M4);thenalwayspubliccleanuporiginalM andfullE XOR8000. No localstatus19skip ofmessagecleanup/eventXOR',
   'releasewrapper selectsword viareadonlyleaf;zero ->RET;nonzero restoreRA/SP thenunlinkedtailprivatefree(selectedwordunchanged). Selectiondoesnotproveoriginalpayloadidentity orvalidfreebase'],
  'ownership_boundary':'knownforwarderbody32 includescopied24Brecord;B0commoncleanupselectswordfromM8 notM8itself. Unknowncasehelpers maymutate/retainrecords/flag;explicitflagclear suppressesonecallattempt,notactualhandoffproof. Publiccleanup andprivateeffects notcomplete lifetimeclosure.',
  'premises':'conditionalcandidateISA/task/provider/queuebindings;validmessage/frame/scratch/cache/header/selectedwordextents;ordinarynestedreturns,S/SP/RA/savedframepreservation;noadversealias/IRQ/DMA/reentry;freshidentity/opcode/taskvalues separatelyretained',
  'actual_installed_binding_payload_ownership_or_nonretention_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-ID11-B0consumer-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':1616,'complete_body_instructions':576,'C_reconstruction_coverage_changed':False,
  'remaining':['casehelpers especially18/22 andposthelper49f54','cachedallocation sizegetter andscratch/privatefreecontracts','actualinstalledprovider,allwriters,queueprogress andpayload/borrowedpointerlifetime'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k])
   for a,d in decode(raw,STARTS[i][k]).items():
    off=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B0 instructionmutation escaped')
    mutations+=1
   for off,_ in TYPED_LOADS[i][part]:
    bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError as ex:check('typedload encoding' in str(ex),'B0 typedguard')
    else:raise RuntimeError('B0 typedmutation escaped')
    typed+=1
 check((mutations,typed)==(576,14),'B0 instruction/typedmutationcensus');domains()
 print('PASS:576 instruction/'+str(typed)+' typed-load mutations rejected;event/U16/calleropcode/frame domains')


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
 else:check(OUT.read_bytes()==encoded,'B0 exactledgerreplay')
 print('PASS:1616B/576i complete B0consumer/releasewrapper;strict HEX;ID11source,flags andcleanupjoins;exact ledger')
 print('PASS:NO target execution/emulation;caseeffects,actualbindings,release completion andpayloadlifetime UNPROVED')


if __name__=='__main__':main()
