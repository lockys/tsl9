"""Offline B1 destination-task writers and complete registered handler.
Original operands/CFG, immutable branch paths and host scalar certificates.
No target execution/emulation or provider/RAM/heap/queue/callback model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_callback_lookup_post_static as previous
import check_v4160_id10_nv_initialization_static as role10
import check_v4160_id9_vector_dispatch_static as role9
import check_v4160_message_receive_static as receiver
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-task-route-static.json')
PARTS=('setter','wrapperA','wrapperB','handler')
STARTS=((0x4cfc6,0x6c0c6,0x6c0f0,0x6cc4c),(0x4d05e,0x6c2aa,0x6c2d4,0x6ce38))
SIZES=(10,42,42,458)
HASHES=(('62b1ddcb47cf0a2831ff25016c66f70c70838059efcb5371e5f00b6ce72c6de5', '13c92f5ec5c0cee1cce22623b84e49f5d3df19ff50a96b36dced7dbb0af96bc8', '1d87e85786a8c67f2fabb2c4ad33319b710fcb59b889af8e07d8daf30e8fa8a8', '4778d792104d13d2e8f222e7d4981bfcb16b1efcc5c82384b1c7f6301b731fb5'), ('08568b7f514b6335b40f665d9b0c5373908380caa63e1e61af20b63e0eede85d', 'b6b10a5a754b96c0ef006b0d80ebd195e08a5efe7b42d905fd33f6f7fbd85cca', 'd97e671758b30f5f948586240f54441f5406a8be369b63266419d9cd8e433e08', '23753efd57f99fb026f3c9f127ae9f8d009b12cb5ba264cc5d08861772fe0b93'))
COUNTS=((3, 15, 15, 158), (3, 15, 15, 158))
QK=({'setter': (), 'wrapperA': ((12, '0c20', 'qk.c.lbu'), (30, '0820', 'qk.c.lbu')), 'wrapperB': ((12, '0c20', 'qk.c.lbu'), (30, '0820', 'qk.c.lbu')), 'handler': ((46, '1c21', 'qk.c.lbu'), (72, '5821', 'qk.c.lbu'), (80, '2a21', 'qk.c.lhu'), (88, 'cc20', 'qk.c.lbu'), (134, '5c21', 'qk.c.lbu'), (138, '1225', 'qk.c.lhu'), (140, '6e21', 'qk.c.lhu'), (142, '2a21', 'qk.c.lhu'), (216, '8823', 'qk.c.lbu'), (306, 'ca23', 'qk.c.lhu'), (326, 'ca23', 'qk.c.lhu'), (384, '9086', 'qk.c.lbusp'), (386, '1c86', 'qk.c.lbusp'), (398, 'ae27', 'qk.c.lhu'))}, {'setter': (), 'wrapperA': ((12, '0c20', 'qk.c.lbu'), (30, '0820', 'qk.c.lbu')), 'wrapperB': ((12, '0c20', 'qk.c.lbu'), (30, '0820', 'qk.c.lbu')), 'handler': ((46, '1c21', 'qk.c.lbu'), (72, '5821', 'qk.c.lbu'), (80, '2a21', 'qk.c.lhu'), (88, 'cc20', 'qk.c.lbu'), (134, '5c21', 'qk.c.lbu'), (138, '1225', 'qk.c.lhu'), (140, '6e21', 'qk.c.lhu'), (142, '2a21', 'qk.c.lhu'), (216, '8823', 'qk.c.lbu'), (306, 'ca23', 'qk.c.lhu'), (326, 'ca23', 'qk.c.lhu'), (384, '9086', 'qk.c.lbusp'), (386, '1c86', 'qk.c.lbusp'), (398, 'ae27', 'qk.c.lhu'))})
TYPED=({'setter': (), 'wrapperA': (), 'wrapperB': (), 'handler': ((30, 4), (160, 4), (170, 4), (234, 2), (246, 5), (250, 2), (298, 2), (318, 2), (336, 4), (354, 5), (406, 5), (436, 4))}, {'setter': (), 'wrapperA': (), 'wrapperB': (), 'handler': ((30, 4), (160, 4), (170, 4), (234, 2), (246, 5), (250, 2), (298, 2), (318, 2), (336, 4), (354, 5), (406, 5), (436, 4))})
LITERALS=(
{
'setter':'''
000 lui 15 536883200
004 store 15 10 -288 1
008 jr 1
''',
'wrapperA':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 8 8 -62
00c load 11 8 0 1
00e lui 15 536883200
012 store 15 10 -28 4
016 li 10 24
018 store 2 1 12 4
01a jal 1 288006
01e load 10 8 0 1
020 load 8 2 8 4
022 load 1 2 12 4
024 addi 2 2 16
026 jal 0 315334
''',
'wrapperB':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 8 8 -62
00c load 11 8 0 1
00e lui 15 536883200
012 store 15 10 -32 4
016 li 10 24
018 store 2 1 12 4
01a jal 1 288006
01e load 10 8 0 1
020 load 8 2 8 4
022 load 1 2 12 4
024 addi 2 2 16
026 jal 0 315334
''',
'handler':'''
000 addi 2 2 -48
002 slli 15 11 16
006 store 2 8 40 4
008 store 2 1 44 4
00a store 2 9 36 4
00c store 2 18 32 4
00e store 2 19 28 4
010 store 2 20 24 4
012 srai 15 15 16
014 mv 8 11
016 bge 15 0 184
01a lui 15 536883200
01e load 10 15 -62 1
022 auipc 1 536424448
026 jalr 1 1 1566
02a mv 9 10
02c beqz 10 112
02e load 15 10 0 1
030 addi 14 0 177
034 beq 15 14 134
038 addi 14 0 208
03c beq 15 14 100
040 addi 14 0 176
044 bne 15 14 106
048 load 14 10 4 1
04a li 15 30
04c bne 14 15 88
050 load 10 10 2 2
052 li 11 0
054 jal 1 442284
058 load 11 9 4 1
05a addi 10 9 8
05e jal 1 305082
062 jump 106
064 jal 1 444772
068 beqz 10 112
06a mv 10 9
06c jal 1 274874
070 lui 9 32768
072 xor 9 9 8
074 load 1 2 44 4
076 load 8 2 40 4
078 mv 10 9
07a load 18 2 32 4
07c load 9 2 36 4
07e load 19 2 28 4
080 load 20 2 24 4
082 addi 2 2 48
084 jr 1
086 load 15 10 4 1
088 bnez 15 106
08a load 12 10 8 2
08c load 11 10 6 2
08e load 10 10 2 2
090 lui 18 536883200
094 addi 18 18 -44
098 store 18 0 0 1
09c jal 1 442434
0a0 load 15 18 0 1
0a4 beqz 15 106
0a6 lui 15 536883200
0aa load 10 15 -272 1
0ae store 18 0 0 1
0b2 jal 1 279312
0b6 jump 106
0b8 andi 15 11 2
0bc beqz 15 224
0be li 11 0
0c0 li 10 0
0c2 jal 1 439646
0c6 lui 15 536883200
0ca xori 9 8 2
0ce addi 15 15 -62
0d2 li 11 1
0d4 bnez 10 216
0d6 li 11 2
0d8 load 10 15 0 1
0da jal 1 275786
0de jump 116
0e0 andi 15 11 1
0e4 beqz 15 442
0e6 lui 19 536883200
0ea load 15 19 -36 4
0ee lui 9 536883200
0f2 addi 19 19 -36
0f6 load 20 15 4 2
0fa load 15 9 -40 4
0fe addi 9 9 -40
102 bnez 15 290
104 lui 14 536883200
108 lui 12 454656
10c lui 11 65536
10e addi 14 14 -24
112 li 13 2
114 addi 12 12 -1424
118 addi 11 11 -1
11a li 10 1
11c jal 1 311046
120 store 9 10 0 4
122 load 11 9 0 4
124 xori 8 8 1
128 bnez 11 350
12a load 15 19 0 4
12e li 12 0
130 li 11 1
132 load 10 15 4 2
134 slli 9 8 16
138 srli 9 9 16
13a jal 1 440186
13e load 15 19 0 4
142 li 12 0
144 li 11 3
146 load 10 15 4 2
148 jal 1 440186
14c lui 15 536883200
150 load 10 15 -272 1
154 jal 1 279312
158 jal 1 438240
15c jump 116
15e lui 18 536883200
162 load 12 18 -24 2
166 addi 17 0 255
16a li 16 2
16c li 15 0
16e addi 14 2 14
172 addi 13 2 12
174 mv 10 20
176 jal 1 312336
17a addi 18 18 -24
17e bnez 10 404
180 load 12 2 13 1
182 load 15 2 12 1
184 slli 12 12 8
186 or 12 12 15
188 beqz 12 404
18a load 15 9 0 4
18c mv 10 20
18e load 11 15 10 2
190 jal 1 442434
194 load 10 9 0 4
196 load 12 18 0 2
19a lui 11 65536
19c li 13 0
19e addi 11 11 -1
1a0 jal 1 312158
1a4 store 9 10 0 4
1a6 slli 9 8 16
1aa srli 9 9 16
1ac beqz 10 298
1ae lui 15 536883200
1b2 li 11 1
1b4 load 10 15 -62 1
1b8 jump 218
1ba andi 15 11 4
1be li 9 0
1c0 beq 15 0 116
1c4 xori 9 11 4
1c8 jump 116
''',
},
{
'setter':'''
000 lui 15 536883200
004 store 15 10 -208 1
008 jr 1
''',
'wrapperA':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 8 8 18
00c load 11 8 0 1
00e lui 15 536883200
012 store 15 10 52 4
016 li 10 24
018 store 2 1 12 4
01a jal 1 288158
01e load 10 8 0 1
020 load 8 2 8 4
022 load 1 2 12 4
024 addi 2 2 16
026 jal 0 315486
''',
'wrapperB':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 lui 8 536883200
008 addi 8 8 18
00c load 11 8 0 1
00e lui 15 536883200
012 store 15 10 48 4
016 li 10 24
018 store 2 1 12 4
01a jal 1 288158
01e load 10 8 0 1
020 load 8 2 8 4
022 load 1 2 12 4
024 addi 2 2 16
026 jal 0 315486
''',
'handler':'''
000 addi 2 2 -48
002 slli 15 11 16
006 store 2 8 40 4
008 store 2 1 44 4
00a store 2 9 36 4
00c store 2 18 32 4
00e store 2 19 28 4
010 store 2 20 24 4
012 srai 15 15 16
014 mv 8 11
016 bge 15 0 184
01a lui 15 536883200
01e load 10 15 18 1
022 auipc 1 536424448
026 jalr 1 1 1074
02a mv 9 10
02c beqz 10 112
02e load 15 10 0 1
030 addi 14 0 177
034 beq 15 14 134
038 addi 14 0 208
03c beq 15 14 100
040 addi 14 0 176
044 bne 15 14 106
048 load 14 10 4 1
04a li 15 30
04c bne 14 15 88
050 load 10 10 2 2
052 li 11 0
054 jal 1 442768
058 load 11 9 4 1
05a addi 10 9 8
05e jal 1 305234
062 jump 106
064 jal 1 445264
068 beqz 10 112
06a mv 10 9
06c jal 1 275014
070 lui 9 32768
072 xor 9 9 8
074 load 1 2 44 4
076 load 8 2 40 4
078 mv 10 9
07a load 18 2 32 4
07c load 9 2 36 4
07e load 19 2 28 4
080 load 20 2 24 4
082 addi 2 2 48
084 jr 1
086 load 15 10 4 1
088 bnez 15 106
08a load 12 10 8 2
08c load 11 10 6 2
08e load 10 10 2 2
090 lui 18 536883200
094 addi 18 18 36
098 store 18 0 0 1
09c jal 1 442918
0a0 load 15 18 0 1
0a4 beqz 15 106
0a6 lui 15 536883200
0aa load 10 15 -192 1
0ae store 18 0 0 1
0b2 jal 1 279460
0b6 jump 106
0b8 andi 15 11 2
0bc beqz 15 224
0be li 11 0
0c0 li 10 0
0c2 jal 1 440130
0c6 lui 15 536883200
0ca xori 9 8 2
0ce addi 15 15 18
0d2 li 11 1
0d4 bnez 10 216
0d6 li 11 2
0d8 load 10 15 0 1
0da jal 1 275926
0de jump 116
0e0 andi 15 11 1
0e4 beqz 15 442
0e6 lui 19 536883200
0ea load 15 19 44 4
0ee lui 9 536883200
0f2 addi 19 19 44
0f6 load 20 15 4 2
0fa load 15 9 40 4
0fe addi 9 9 40
102 bnez 15 290
104 lui 14 536883200
108 lui 12 454656
10c lui 11 65536
10e addi 14 14 56
112 li 13 2
114 addi 12 12 -928
118 addi 11 11 -1
11a li 10 1
11c jal 1 311198
120 store 9 10 0 4
122 load 11 9 0 4
124 xori 8 8 1
128 bnez 11 350
12a load 15 19 0 4
12e li 12 0
130 li 11 1
132 load 10 15 4 2
134 slli 9 8 16
138 srli 9 9 16
13a jal 1 440670
13e load 15 19 0 4
142 li 12 0
144 li 11 3
146 load 10 15 4 2
148 jal 1 440670
14c lui 15 536883200
150 load 10 15 -192 1
154 jal 1 279460
158 jal 1 438724
15c jump 116
15e lui 18 536883200
162 load 12 18 56 2
166 addi 17 0 255
16a li 16 2
16c li 15 0
16e addi 14 2 14
172 addi 13 2 12
174 mv 10 20
176 jal 1 312488
17a addi 18 18 56
17e bnez 10 404
180 load 12 2 13 1
182 load 15 2 12 1
184 slli 12 12 8
186 or 12 12 15
188 beqz 12 404
18a load 15 9 0 4
18c mv 10 20
18e load 11 15 10 2
190 jal 1 442918
194 load 10 9 0 4
196 load 12 18 0 2
19a lui 11 65536
19c li 13 0
19e addi 11 11 -1
1a0 jal 1 312310
1a4 store 9 10 0 4
1a6 slli 9 8 16
1aa srli 9 9 16
1ac beqz 10 298
1ae lui 15 536883200
1b2 li 11 1
1b4 load 10 15 18 1
1b8 jump 218
1ba andi 15 11 4
1be li 9 0
1c0 beq 15 0 116
1c4 xori 9 11 4
1c8 jump 116
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B1route literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1route typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1route completeboundaries')
 for a,f in s.items():init.g(n,a,'B1route '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1route Xwchc encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1route completeidentity')
 edges={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1route ordinaryRET');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   row=dict(offset=a-pc,target=d['target'])
   if d['rd']==0:tails.append(dict(**row,new_link=False));q=[]
   else:check(d['rd']==1,'B1route linkedcall');calls.append(row)
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1route adjacentpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1route closedlocalCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'B1route complete reachable localDAG')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 if part=='setter':
  check(not calls and not tails and rets==[pc+8] and stores==[dict(offset=4,base=15,source=10,imm=-288+80*index,bytes=1)],'B1route setter single taskbytestore')
 elif part.startswith('wrapper'):
  check(calls==[dict(offset=0x1a,target=0x46506+152*index)] and tails==[dict(offset=0x26,target=STARTS[index][0],new_link=False)] and not rets,'B1route wrapper tablecall->settertail')
  check(len(stores)==3 and [(d['source'],d['imm']) for d in stores if d['base']==2]==[(8,8),(1,12)],'B1route wrapperframe andsavedentryA0word')
 else:
  targets=[(0x26,0x2000028c),(0x54,0x6bfac+484*index),(0x5e,0x4a7ba+152*index),(0x64,0x6c964+492*index),
   (0x6c,0x431ba+140*index),(0x9c,0x6c042+484*index),(0xb2,0x44310+148*index),(0xc2,0x6b55e+484*index),
   (0xda,0x4354a+140*index),(0x11c,0x4bf06+152*index),(0x13a,0x6b77a+484*index),(0x148,0x6b77a+484*index),
   (0x154,0x44310+148*index),(0x158,0x6afe0+484*index),(0x176,0x4c410+152*index),(0x190,0x6c042+484*index),(0x1a0,0x4c35e+152*index)]
  check(calls==[dict(offset=o,target=t) for o,t in targets] and not tails and rets==[pc+0x84],'B1route all17handlercalls andreturn')
  check(len(stores)==10 and [d['offset'] for d in stores if d['base']!=2]==[0x98,0xae,0x120,0x1a4],'B1route allnonframe stores')
  saved={(1,44),(8,40),(9,36),(18,32),(19,28),(20,24)}
  check({(d['source'],d['imm']) for d in stores if d['base']==2}==saved and {(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and d['imm']>=24}==saved,'B1route48Bframe savedrestore')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part!='handler':return {'ordinary':common.walk(b,{})}
 base={0x16:0x1a,0x2c:0x2e,0x34:0x86}
 selected={
  'bit15_receive0':{0x16:0x1a,0x2c:0x70},
  'B1_statusnonzero_cleanup':{**base,0x88:0x6a},
  'B1_status0_process_flag0_cleanup':{**base,0x88:0x8a,0xa4:0x6a},
  'B1_status0_process_flag_nonzero_notify_cleanup':{**base,0x88:0x8a,0xa4:0xa6},
  'unknown_type_cleanup':{0x16:0x1a,0x2c:0x2e,0x34:0x38,0x3c:0x40,0x44:0x6a},
  'D0_retention_reply0_no_cleanup':{0x16:0x1a,0x2c:0x2e,0x34:0x38,0x3c:0x64,0x68:0x70},
  'no_supported_event_reply0':{0x16:0xb8,0xbc:0xe0,0xe4:0x1ba,0x1c0:0x74}}
 ps={label:common.walk(b,c) for label,c in selected.items()}
 for label in ('B1_statusnonzero_cleanup','B1_status0_process_flag0_cleanup','B1_status0_process_flag_nonzero_notify_cleanup'):
  seq=ps[label];check(0x6c in seq and seq.index(0x6c)<seq.index(0x70),'B1route selectedB1 always cleanup beforeXOR')
 check(0x9c not in ps['B1_statusnonzero_cleanup'] and 0x9c in ps['B1_status0_process_flag0_cleanup'],'B1route fresh M4 gate')
 seq=ps['B1_status0_process_flag_nonzero_notify_cleanup'];check(seq.index(0x98)<seq.index(0x9c)<seq.index(0xae)<seq.index(0xb2)<seq.index(0x6c),'B1route flagclear/call/refetch/notify/free order')
 # In selected B1 walk, message reads through M=A0 occur only at M0,M4,M8,M6,M2, before A0 becomes an ID.
 n={v['pc']-b['start']:v for v in b['instructions']};reads=[(o,n[o]['imm'],n[o]['width']) for o in seq if n[o]['op']=='load' and n[o]['rs1']==10]
 check(reads==[(0x2e,0,1),(0x86,4,1),(0x8a,8,2),(0x8c,6,2),(0x8e,2,2)],'B1route selectedmessage field census noM1/M5')
 return ps


def domains():
 for low in range(65536):
  signed=low if low<32768 else low-65536;check((signed<0)==bool(low&0x8000),'B1route bit15 signed16 eventgate')
  check((low^0x8000)&0x8000 == (0 if low&0x8000 else 0x8000),'B1route bit15 XOR exact')
 for high in (0,1,0xffff):
  for low in (0,1,0x7fff,0x8000,0xffff):
   E=(high<<16)|low;check(((E^0x8000)>>16)==high,'B1route fullword upperbits preserved')
 for byte in range(256):check((byte==177)==(byte==0xb1),'B1route discriminator U8only')
 for low in range(65536):check((low&255)==(low%256),'B1route setters low8 fullinput')
 check(set((0,4,8,9,6,7,2,3)).isdisjoint((1,5)),'B1route selectedfield footprint excludes M1/M5')
 return dict(event_low16_cases=65536,setter_low16_cases=65536,message_discriminator_cases=256,
  selected_B1_reply='fullentryE XOR8000 evenif receivenull or cleanupfails normally',
  source_snapshots='registrationreply ->savedIDbyte,wrapperR0->index24,wrapperR1->producertask,producerT0/T1,consumerR2 allseparate; equalityneeds preservation',
  postmessage_projection=dict(M0='00B1 producerSH;consumerreadsU8M0only',M2='low16originalID0',M6='low16originalID1',M8='low16packedvalue',M4='producer0;consumerfreshzero gate',M5='notread byselectedB1 path'),
  runtime_delivery_or_wholecallback_success_proved=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  pc=STARTS[index][k];raw=init.binding.take(data,pc,SIZES[k]);check(sparse.captured(mem,pc,SIZES[k])==raw,'B1route wholeoriginalHEX backing');bs[part]=body(raw,part,index)
 n={part:{v['pc']-b['start']:v for v in b['instructions']} for part,b in bs.items()};G=0x20003000;rolebyte=G-62+80*index;dest=G-288+80*index
 check(n['setter'][0]['imm']+n['setter'][4]['imm']==dest,'B1route taskcell identity')
 for part in ('wrapperA','wrapperB'):
  w=n[part];check(w[4]['imm']+w[8]['imm']==rolebyte and w[0xc]['rd']==11 and w[0x1e]['rd']==10 and w[0x16]['imm']==24,'B1route distinct taskbyte reads andindex24')
  check(w[0xe]['imm']+w[0x12]['imm']==G+(-28 if part=='wrapperA' else -32)+80*index and w[0x12]['rs2']==10,'B1route storeoriginalA0pointerword')
 h=n['handler'];check(h[0x1a]['imm']+h[0x1e]['imm']==rolebyte and h[0x30]['imm']==177 and h[0x86]['imm']==4,'B1route handler task/type/status sources')
 check(h[0x90]['imm']+h[0x94]['imm']==G-44+80*index and h[0xa6]['imm']+h[0xaa]['imm']==G-272+80*index,'B1route flag and distinctnotifytask source')
 prod=parent['bodies']['post'];pn={v['pc']-prod['start']:v for v in prod['instructions']}
 check(pn[4]['imm']+pn[8]['imm']==dest and pn[0x30]['imm']==177 and pn[0x36]['imm']==4,'B1route producer taskcell/type/M4zero join')
 # Reuse original conditional ID10 registration and saved-input initializer, without asserting actual count/startup.
 ep=role9.STARTS[index][-1];outer=role9.body(init.binding.take(data,ep,16),'next_outer',index);on={v['pc']-ep:v for v in outer['instructions']}
 check(on[0]['imm']+on[4]['imm']==bs['handler']['start'] and on[8]['target']==role9.role.DETAILS[index]['reg'] and on[12]['target']==role10.STARTS[index][0],'B1route handler registration->initializer exactjoins')
 ip=role10.STARTS[index][0];ir=init.binding.take(data,ip,28);ib=role10.body(ir,'initializer',index);inn={v['pc']-ip:v for v in ib['instructions']}
 check(inn[4]['rs2']==10 and inn[4]['imm']==12 and inn[10]['rs1']==2 and inn[10]['imm']==12 and inn[18]['imm']+G==rolebyte,'B1route IDbyte source savedregistrationA0 notallocatorreply')
 rb=role9.registration.body(init.binding.take(data,role9.role.DETAILS[index]['reg'],48),index)
 check(sparse.captured(mem,ep,16)==init.binding.take(data,ep,16) and sparse.captured(mem,ip,28)==ir,'B1route reusedorigin strictHEX')
 # Reuse complete receive/unlink and public release, preserving private-release/lifetime boundaries.
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy']
 check(int(first['source'],16)+0x2000028c-int(first['destination'],16)==receiver.SOURCES[index][0] and 0x2000028c+136<=int(mapping['first_copy_end_exclusive'],16),'B1route complete receiver firstcopy mapping')
 receive=receiver.body(init.binding.take(data,receiver.SOURCES[index][0],136),'receive',index)
 free=receiver.previous.dealloc;fp=free.DETAILS[index][0];fr=init.binding.take(data,fp,len(free.FREE));fn=decode(fr,fp)
 check(free.normalized(fr,((62,8),))==free.normalized(free.FREE,((62,8),)) and free.auipc_call(fr,62,fp+62)==0x20000110,'B1route completepublicrelease reuse')
 check(sparse.captured(mem,fp,len(fr))==fr and sparse.captured(mem,receiver.SOURCES[index][0],136)==init.binding.take(data,receiver.SOURCES[index][0],136),'B1route receive/free strictoriginalHEX')
 check(bs['handler']['calls'][0]['target']==0x2000028c and next(c['target'] for c in bs['handler']['calls'] if c['offset']==0x6c)==fp,'B1route selectedreceive/free targets')
 freewalk=[0,2,4,6,10,12,16,20,24,42,46,50,62,66]
 check(not any(fn[fp+o].get('rd')==10 for o in freewalk),'B1route publicrelease forwardsM unchanged')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},
  globals=dict(role_task_byte=rolebyte,B1_producer_task_byte=dest,wrapperA_word=G-28+80*index,wrapperB_word=G-32+80*index,B1_flag=G-44+80*index,other_notify_task_byte=G-272+80*index),
  reused=dict(registration=dict(start=role9.role.DETAILS[index]['reg'],sha256=rb['sha256'],new_code_bytes_counted=0),outer_window=dict(start=ep,sha256=outer['sha256'],complete_function=False,new_code_bytes_counted=0),
   initializer=dict(start=ip,sha256=ib['sha256'],new_code_bytes_counted=0),receive=dict(start=0x2000028c,bytes=136,sha256=receive['sha256'],new_code_bytes_counted=0),publicrelease=dict(start=fp,bytes=len(fr),sha256=sha256(fr).hexdigest(),new_code_bytes_counted=0)),
  registration_composition='underpreviouscount10/capacity/table/context preservation registration writesrow10=handler,returns10;initializer preservesinputA0 acrosssetup andstoreslow8torolebyte beforeNVloadtail. TransientFF andunknowncalleesremain; noactualinstalledregistration claim',
  writer_contract=['bothwrappers capturefirstfreshrolebyte R0toA1;storeoriginalentryA0value toseparateglobalword;call46506/4659e(A0=24,A1=R0),otherargsambient',
   'aftercall freshrolebyte R1toA0,restoreframe,unlinkedtailsetter. SetterSB low8A0toproducertaskcell;returnA0unchanged. NoR0/R1equalityorallwritersproof'],
  B1_contract=['entrylow16event bit15 ->receive(freshrolebyte),not entryA0 task. Receivenull ->no free; fullE XOR8000 normalreply',
   'nonnullM: freshU8M0==B1 select;freshU8M4nonzero ->cleanup. Zero ->freshU16M8,M6,M2 toA2,A1,A0,clearflag,call6c042/6c226',
   'ignorechildreply;freshflag0 ->cleanup;nonnullflag ->freshdistincttaskbyte,clearflagbefore44310/443a4,then cleanup',
   'cleanup receives originalcapturedM,not childreply;publicrelease normalreturns then fullE XOR8000. M1/M5 notread selectedpath;no local Mbody rewrite or explicitownershiptransfer',
   'othermessage/eventpaths fullypinned syntactically butcallee semantics opaque;notgeneralizedcleanup: D0 childreply0 explicitly skips commoncleanup'],
  lifetime_boundary='matchingreceive unlinks andmarksownerFF beforeM return;publicrelease forwardsM toprivate release. Existing conditional interior-pointer proof applies onlywithheap/header/extent andpreservation premises; noactualfree/delivery/retention completion proved',
  premises='conditionalcandidateISA/startup/queue/providers;normalcallee/context/S/SP/RA/savedframepreservation;validcode/node/header/M>=10/frame/global extents;finitevalidqueue;noadversealias/wrap/IRQ/DMA/reentry;freshsource equality separatelyrequired',
  actual_installed_binding_allwriters_delivery_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-task-writer-registered-consumer-static-v1',APP_sha256=sha256(image).hexdigest(),
  profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_new_body_bytes=1104,complete_new_body_instructions=382,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['6c042/6c226 and44310/443a4 downstream effects','wrapperactualcallers andtaskbytepreservation/allwriters','actualprovider/queue/heap/privatefree lifetime'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1route instructionmutation escaped')
    mutations+=1
   for o,f in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1route typedmutation escaped')
    typed+=1
 check((mutations,typed)==(382,24),'B1route mutation census');domains()
 print('PASS:382 instruction/24 typed-load mutations rejected;65536 event/setter andB1 field/cleanup certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1route exactledger replay')
 print('PASS:1104B/382i complete writers/handler;strict HEX;ID10/source/producer/B1/receive/free joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,allwriters,downstream effects andpointerlifetime UNPROVED')


if __name__=='__main__':main()
