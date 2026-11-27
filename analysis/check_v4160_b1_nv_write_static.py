"""Offline complete NV write wrapper: original operands and immutable CFG paths.
Host scalar/interval certificates only; no target/provider/NV/RAM execution/model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_nv_read_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-nv-write-static.json')
STARTS=(0x4435c,0x443f0)
SIZE=606
HASHES=('4e16c01e8de9a4b22d0002c2e1ab9bfaf2929325a69ccd6ab4c0ab4175013113', 'ce30b96e7368c260bc7ed3d14a5e6caaa2ec7f21ed2b684aa21dbd9c033c6c15')
COUNTS=(210, 210)
QK=(((116, '4a24', 'qk.c.lhu'), (146, '3ca1', 'qk.c.sb'), (166, '4a24', 'qk.c.lhu'), (188, '4e24', 'qk.c.lhu'), (220, '4a24', 'qk.c.lhu'), (242, '4a24', 'qk.c.lhu'), (262, '4a24', 'qk.c.lhu'), (284, '5a24', 'qk.c.lhu'), (340, '3023', 'qk.c.lbu'), (350, '3033', 'qk.c.lbu'), (390, '4a24', 'qk.c.lhu'), (412, '4e24', 'qk.c.lhu'), (432, '0ea3', 'qk.c.sh'), (442, '5224', 'qk.c.lhu'), (476, '34b3', 'qk.c.sb'), (520, '3023', 'qk.c.lbu'), (530, '3033', 'qk.c.lbu'), (544, '0ea3', 'qk.c.sh'), (554, '6824', 'qk.c.lbu'), (556, '5e24', 'qk.c.lhu'), (586, '5224', 'qk.c.lhu'), (588, '6c24', 'qk.c.lbu')), ((116, '4a24', 'qk.c.lhu'), (146, '3ca1', 'qk.c.sb'), (166, '4a24', 'qk.c.lhu'), (188, '4e24', 'qk.c.lhu'), (220, '4a24', 'qk.c.lhu'), (242, '4a24', 'qk.c.lhu'), (262, '4a24', 'qk.c.lhu'), (284, '5a24', 'qk.c.lhu'), (340, '3023', 'qk.c.lbu'), (350, '3033', 'qk.c.lbu'), (390, '4a24', 'qk.c.lhu'), (412, '4e24', 'qk.c.lhu'), (432, '0ea3', 'qk.c.sh'), (442, '5224', 'qk.c.lhu'), (476, '34b3', 'qk.c.sb'), (520, '3023', 'qk.c.lbu'), (530, '3033', 'qk.c.lbu'), (544, '0ea3', 'qk.c.sh'), (554, '6824', 'qk.c.lbu'), (556, '5e24', 'qk.c.lhu'), (586, '5224', 'qk.c.lhu'), (588, '6c24', 'qk.c.lbu')))
TYPED=(((14, 2), (96, 2), (132, 2), (192, 2), (308, 2), (316, 2), (346, 5), (416, 2), (496, 2), (526, 5)), ((14, 2), (96, 2), (132, 2), (192, 2), (308, 2), (316, 2), (346, 5), (416, 2), (496, 2), (526, 5)))
LITERALS=(
'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 536883200
008 addi 15 8 492
00c store 2 21 4 4
00e load 21 15 8 4
012 store 2 9 20 4
014 store 2 18 16 4
016 store 2 19 12 4
018 store 2 1 28 4
01a store 2 20 8 4
01c mv 18 10
01e mv 9 11
020 mv 19 12
022 addi 8 8 492
026 beq 21 0 480
02a load 15 8 60 4
02c bnez 15 66
02e li 10 10
030 load 1 2 28 4
032 load 8 2 24 4
034 load 9 2 20 4
036 load 18 2 16 4
038 load 19 2 12 4
03a load 20 2 8 4
03c load 21 2 4 4
03e addi 2 2 32
040 jr 1
042 load 15 8 56 4
044 beqz 15 46
046 addi 15 0 511
04a bltu 15 10 268
04e lui 20 536883200
052 addi 15 20 412
056 load 15 15 32 4
058 addi 20 20 412
05c beqz 15 166
05e load 10 8 8 4
060 load 15 20 36 4
064 bne 15 10 188
068 li 15 2
06a bne 18 15 208
06e li 15 16
070 bne 9 15 46
074 load 10 8 12 2
076 li 15 4
078 addi 10 10 -64
07c div 10 10 15
080 slli 15 10 2
084 load 10 20 32 4
088 mv 12 9
08a mv 11 19
08c add 10 10 15
08e addi 15 0 90
092 store 10 15 2 1
094 store 10 18 0 2
098 addi 10 10 4
09a auipc 1 536592384
09e jalr 1 1 -196
0a2 li 10 0
0a4 jump 48
0a6 load 10 8 12 2
0a8 addi 11 0 78
0ac auipc 1 536592384
0b0 jalr 1 1 -968
0b4 store 20 10 32 4
0b8 bnez 10 94
0ba jump 46
0bc load 11 8 12 2
0be load 15 8 56 4
0c0 load 12 20 32 4
0c4 srli 11 11 2
0c6 call_indirect 1 15
0c8 load 15 8 8 4
0ca store 20 15 36 4
0ce jump 104
0d0 li 15 3
0d2 bne 18 15 232
0d6 li 15 16
0d8 bne 9 15 46
0dc load 10 8 12 2
0de addi 10 10 -44
0e2 andi 15 10 -4
0e6 jump 132
0e8 li 15 4
0ea bne 18 15 248
0ee bne 9 18 46
0f2 load 10 8 12 2
0f4 addi 10 10 -24
0f6 jump 226
0f8 addi 15 0 256
0fc bne 18 15 46
100 li 15 8
102 bltu 15 9 46
106 load 10 8 12 2
108 addi 10 10 -16
10a jump 226
10c lui 15 28672
10e bgeu 10 15 376
112 addi 15 10 -512
116 li 14 6
118 div 15 15 14
11c load 14 8 12 2
11e lui 20 536883200
122 mul 15 15 14
126 add 21 21 15
128 addi 15 20 412
12c load 15 15 32 4
12e addi 20 20 412
132 beqz 15 390
134 load 15 20 36 4
138 bne 15 21 412
13c load 10 20 32 4
140 li 13 4
142 addi 16 0 90
146 addi 11 0 255
14a srli 15 13 2
14e slli 14 15 2
152 add 14 14 10
154 load 12 14 2 1
156 bne 12 16 442
15a load 17 14 0 2
15e load 12 14 3 1
160 bne 17 18 434
164 sub 13 12 13
168 blt 13 9 432
16c addi 15 15 1
16e slli 15 15 2
170 mv 12 9
172 mv 11 19
174 add 10 10 15
176 jump 154
178 lui 14 32768
17a addi 14 14 -2
17c bltu 14 10 46
180 sub 15 10 15
184 jump 284
186 load 10 8 12 2
188 addi 11 0 78
18c auipc 1 536592384
190 jalr 1 1 -1192
194 store 20 10 32 4
198 bnez 10 308
19a jump 46
19c load 11 8 12 2
19e load 15 8 56 4
1a0 load 12 20 32 4
1a4 srli 11 11 2
1a6 mv 10 21
1a8 call_indirect 1 15
1aa store 20 21 36 4
1ae jump 316
1b0 store 14 11 0 2
1b2 slli 13 12 16
1b6 srli 13 13 16
1b8 jump 330
1ba load 12 8 12 2
1bc add 11 13 9
1c0 addi 11 11 4
1c2 addi 12 12 -64
1c6 bgeu 11 12 46
1ca addi 12 9 3
1ce andi 12 12 -4
1d0 addi 12 12 4
1d2 add 13 13 12
1d4 store 14 16 2 1
1d8 store 14 18 0 2
1dc store 14 13 3 1
1de jump 364
1e0 lui 20 536883200
1e4 addi 15 20 412
1e8 load 15 15 32 4
1ea addi 20 20 412
1ee beqz 15 554
1f0 load 10 20 32 4
1f4 li 13 4
1f6 addi 16 0 90
1fa addi 11 0 255
1fe srli 15 13 2
202 slli 14 15 2
206 add 14 14 10
208 load 12 14 2 1
20a bne 12 16 586
20e load 17 14 0 2
212 load 12 14 3 1
214 bne 17 18 546
218 sub 13 12 13
21c bge 13 9 364
220 store 14 11 0 2
222 slli 13 12 16
226 srli 13 13 16
228 jump 510
22a load 10 8 14 1
22c load 15 8 12 2
22e addi 11 0 78
232 mul 10 10 15
236 slli 10 10 16
238 srli 10 10 16
23a auipc 1 536592384
23e jalr 1 1 -1366
242 store 20 10 32 4
246 bnez 10 496
248 jump 46
24a load 12 8 12 2
24c load 11 8 14 1
24e mul 11 11 12
252 add 12 13 9
256 addi 12 12 4
258 bltu 11 12 46
25c jump 458
''',
'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 536883200
008 addi 15 8 572
00c store 2 21 4 4
00e load 21 15 8 4
012 store 2 9 20 4
014 store 2 18 16 4
016 store 2 19 12 4
018 store 2 1 28 4
01a store 2 20 8 4
01c mv 18 10
01e mv 9 11
020 mv 19 12
022 addi 8 8 572
026 beq 21 0 480
02a load 15 8 60 4
02c bnez 15 66
02e li 10 10
030 load 1 2 28 4
032 load 8 2 24 4
034 load 9 2 20 4
036 load 18 2 16 4
038 load 19 2 12 4
03a load 20 2 8 4
03c load 21 2 4 4
03e addi 2 2 32
040 jr 1
042 load 15 8 56 4
044 beqz 15 46
046 addi 15 0 511
04a bltu 15 10 268
04e lui 20 536883200
052 addi 15 20 492
056 load 15 15 32 4
058 addi 20 20 492
05c beqz 15 166
05e load 10 8 8 4
060 load 15 20 36 4
064 bne 15 10 188
068 li 15 2
06a bne 18 15 208
06e li 15 16
070 bne 9 15 46
074 load 10 8 12 2
076 li 15 4
078 addi 10 10 -64
07c div 10 10 15
080 slli 15 10 2
084 load 10 20 32 4
088 mv 12 9
08a mv 11 19
08c add 10 10 15
08e addi 15 0 90
092 store 10 15 2 1
094 store 10 18 0 2
098 addi 10 10 4
09a auipc 1 536592384
09e jalr 1 1 -344
0a2 li 10 0
0a4 jump 48
0a6 load 10 8 12 2
0a8 addi 11 0 78
0ac auipc 1 536592384
0b0 jalr 1 1 -1116
0b4 store 20 10 32 4
0b8 bnez 10 94
0ba jump 46
0bc load 11 8 12 2
0be load 15 8 56 4
0c0 load 12 20 32 4
0c4 srli 11 11 2
0c6 call_indirect 1 15
0c8 load 15 8 8 4
0ca store 20 15 36 4
0ce jump 104
0d0 li 15 3
0d2 bne 18 15 232
0d6 li 15 16
0d8 bne 9 15 46
0dc load 10 8 12 2
0de addi 10 10 -44
0e2 andi 15 10 -4
0e6 jump 132
0e8 li 15 4
0ea bne 18 15 248
0ee bne 9 18 46
0f2 load 10 8 12 2
0f4 addi 10 10 -24
0f6 jump 226
0f8 addi 15 0 256
0fc bne 18 15 46
100 li 15 8
102 bltu 15 9 46
106 load 10 8 12 2
108 addi 10 10 -16
10a jump 226
10c lui 15 28672
10e bgeu 10 15 376
112 addi 15 10 -512
116 li 14 6
118 div 15 15 14
11c load 14 8 12 2
11e lui 20 536883200
122 mul 15 15 14
126 add 21 21 15
128 addi 15 20 492
12c load 15 15 32 4
12e addi 20 20 492
132 beqz 15 390
134 load 15 20 36 4
138 bne 15 21 412
13c load 10 20 32 4
140 li 13 4
142 addi 16 0 90
146 addi 11 0 255
14a srli 15 13 2
14e slli 14 15 2
152 add 14 14 10
154 load 12 14 2 1
156 bne 12 16 442
15a load 17 14 0 2
15e load 12 14 3 1
160 bne 17 18 434
164 sub 13 12 13
168 blt 13 9 432
16c addi 15 15 1
16e slli 15 15 2
170 mv 12 9
172 mv 11 19
174 add 10 10 15
176 jump 154
178 lui 14 32768
17a addi 14 14 -2
17c bltu 14 10 46
180 sub 15 10 15
184 jump 284
186 load 10 8 12 2
188 addi 11 0 78
18c auipc 1 536592384
190 jalr 1 1 -1340
194 store 20 10 32 4
198 bnez 10 308
19a jump 46
19c load 11 8 12 2
19e load 15 8 56 4
1a0 load 12 20 32 4
1a4 srli 11 11 2
1a6 mv 10 21
1a8 call_indirect 1 15
1aa store 20 21 36 4
1ae jump 316
1b0 store 14 11 0 2
1b2 slli 13 12 16
1b6 srli 13 13 16
1b8 jump 330
1ba load 12 8 12 2
1bc add 11 13 9
1c0 addi 11 11 4
1c2 addi 12 12 -64
1c6 bgeu 11 12 46
1ca addi 12 9 3
1ce andi 12 12 -4
1d0 addi 12 12 4
1d2 add 13 13 12
1d4 store 14 16 2 1
1d8 store 14 18 0 2
1dc store 14 13 3 1
1de jump 364
1e0 lui 20 536883200
1e4 addi 15 20 492
1e8 load 15 15 32 4
1ea addi 20 20 492
1ee beqz 15 554
1f0 load 10 20 32 4
1f4 li 13 4
1f6 addi 16 0 90
1fa addi 11 0 255
1fe srli 15 13 2
202 slli 14 15 2
206 add 14 14 10
208 load 12 14 2 1
20a bne 12 16 586
20e load 17 14 0 2
212 load 12 14 3 1
214 bne 17 18 546
218 sub 13 12 13
21c bge 13 9 364
220 store 14 11 0 2
222 slli 13 12 16
226 srli 13 13 16
228 jump 510
22a load 10 8 14 1
22c load 15 8 12 2
22e addi 11 0 78
232 mul 10 10 15
236 slli 10 10 16
238 srli 10 10 16
23a auipc 1 536592384
23e jalr 1 1 -1514
242 store 20 10 32 4
246 bnez 10 496
248 jump 46
24a load 12 8 12 2
24c load 11 8 14 1
24e mul 11 11 12
252 add 12 13 9
256 addi 12 12 4
258 bltu 11 12 46
25c jump 458
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1NVwrite literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1NVwrite typedload encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'B1NVwrite full boundaries')
 for a,f in s.items():init.g(n,a,'B1NVwrite operand '+hex(a-pc),**f)
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1NVwrite Xwchc raw/offset/width')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'B1NVwrite fullidentity')
 edges={};calls=[];indirect=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1NVwrite RET RA');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1NVwrite callpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':
   check(d['rd']==1 and d['rs1']==15,'B1NVwrite RA/A5 indirect');indirect.append(dict(offset=a-pc,register=15,bit0_cleared=True))
  else:check(op!='jal','B1NVwrite no unlistedJAL')
  check(all(z in n for z in q),'B1NVwrite closedCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1NVwrite all nodes reachable')
 cuts={(0x1b8,0x14a),(0x228,0x1fe)}
 cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in edges.items()}
 check(not common.acyclic(edges) and common.acyclic(cut),'B1NVwrite exactly two rowloop cuts')
 check(calls==[dict(offset=o,target=t) for o,t in [(0x9e,0x20000332),(0xb0,0x20000040),(0x190,0x20000040),(0x23e,0x20000040)]] and [d['offset'] for d in indirect]==[0xc6,0x1a8] and rets==[pc+0x40],'B1NVwrite allcall/return sites;no privatefree')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 saved=[d for d in stores if d['base']==2];frames={(8,24),(21,4),(9,20),(18,16),(19,12),(1,28),(20,8)}
 check(len(saved)==7 and {(d['source'],d['imm']) for d in saved}==frames and all(d['bytes']==4 for d in saved),'B1NVwrite frame7words')
 expected=[(0x92,10,15,2,1),(0x94,10,18,0,2),(0xb4,20,10,32,4),(0xca,20,15,36,4),(0x194,20,10,32,4),(0x1aa,20,21,36,4),
  (0x1b0,14,11,0,2),(0x1d4,14,16,2,1),(0x1d8,14,18,0,2),(0x1dc,14,13,3,1),(0x220,14,11,0,2),(0x242,20,10,32,4)]
 check([d for d in stores if d['base']!=2]==[dict(offset=o,base=r,source=v,imm=x,bytes=z) for o,r,v,x,z in expected] and len(stores)==19,'B1NVwrite exact12nonframe/19total stores')
 check([a-pc for a,d in n.items() if d.get('rd')==19]==[0x20,0x38] and [a-pc for a,d in n.items() if d.get('rd')==9]==[0x1e,0x34],'B1NVwrite originalinput/fullL heldS3/S1')
 return dict(start=pc,source=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,indirect_calls=indirect,tails=[],returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def valid_path(b,seq):
 pc=b['start'];e=b['CFG'];check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1NVwrite immutable path');return seq


def paths(b):
 low={0x26:0x2a,0x2c:0x42,0x44:0x46,0x4a:0x4e,0x5c:0x5e,0x64:0x68}
 high={0x26:0x2a,0x2c:0x42,0x44:0x46,0x4a:0x10c,0x10e:0x112,0x132:0x134,0x138:0x13c,0x156:0x15a,0x160:0x164,0x168:0x16c}
 ram={0x26:0x1e0,0x1ee:0x1f0,0x20a:0x20e,0x214:0x218,0x21c:0x16c}
 choices={
  'configured_noF60':{0x26:0x2a,0x2c:0x2e},'configured_noF56':{0x26:0x2a,0x2c:0x42,0x44:0x2e},
  'low_cached_ID2_write':low,'low_initial_alloc_fail':{**low,0x5c:0xa6,0xb8:0xba},
  'low_initial_callback_write':{**low,0x5c:0xa6,0xb8:0x5e,0x64:0xbc},'low_owner_callback_write':{**low,0x64:0xbc},
  'low_ID3_write':{**low,0x6a:0xd0,0xd2:0xd6},'low_ID4_write':{**low,0x6a:0xd0,0xd2:0xe8,0xea:0xee},
  'low_ID256_write':{**low,0x6a:0xd0,0xd2:0xe8,0xea:0xf8,0xfc:0x100},
  'low_badID':{**low,0x6a:0xd0,0xd2:0xe8,0xea:0xf8,0xfc:0x2e},'low_badlength':{**low,0x70:0x2e},
  'high_cached_match_copy':high,'high_alloc_fail':{**high,0x132:0x186,0x198:0x19a},
  'high_alloc_callback_match':{**high,0x132:0x186,0x198:0x134,0x138:0x19c},'high_owner_callback_match':{**high,0x138:0x19c},
  'high_upper_match':{**high,0x10e:0x178,0x17c:0x180},'high_upper_reject':{**high,0x10e:0x178,0x17c:0x2e},
  'high_append_rejected':{**high,0x156:0x1ba,0x1c6:0x2e},'high_append_copy':{**high,0x156:0x1ba,0x1c6:0x1ca},
  'RAM_existing_match':ram,'RAM_alloc_fail':{**ram,0x1ee:0x22a,0x246:0x248},'RAM_alloc_match':{**ram,0x1ee:0x22a,0x246:0x1f0},
  'RAM_append_rejected':{**ram,0x20a:0x24a,0x258:0x2e},'RAM_append_copy':{**ram,0x20a:0x24a,0x258:0x25c}}
 ps={label:common.walk(b,c) for label,c in choices.items()}
 for label,source,branch,loop in [
  ('high_one_key_mismatch_then_match','high_cached_match_copy',0x160,[0x1b2,0x1b6,0x1b8,0x14a,0x14e,0x152,0x154,0x156,0x15a,0x15e,0x160]),
  ('high_one_insufficient_then_match','high_cached_match_copy',0x168,[0x1b0,0x1b2,0x1b6,0x1b8,0x14a,0x14e,0x152,0x154,0x156,0x15a,0x15e,0x160,0x164,0x168]),
  ('RAM_one_key_mismatch_then_match','RAM_existing_match',0x214,[0x222,0x226,0x228,0x1fe,0x202,0x206,0x208,0x20a,0x20e,0x212,0x214]),
  ('RAM_one_insufficient_then_match','RAM_existing_match',0x21c,[0x220,0x222,0x226,0x228,0x1fe,0x202,0x206,0x208,0x20a,0x20e,0x212,0x214,0x218,0x21c])]:
  seq=ps[source];j=seq.index(branch);ps[label]=valid_path(b,seq[:j+1]+loop+seq[j+1:])
 check(all(a not in ps['RAM_existing_match'] for a in (0xc6,0x1a8,0xb0,0x190,0x23e)),'B1NVwrite RAMreuse noalloc/callback')
 check(0x1b0 in ps['high_one_insufficient_then_match'] and 0x220 in ps['RAM_one_insufficient_then_match'],'B1NVwrite bothkey-tombstone paths')
 check(all(0x9e in ps[k] for k in ('low_cached_ID2_write','high_cached_match_copy','high_append_copy','RAM_existing_match','RAM_append_copy')),'B1NVwrite allcopy paths sharedcall')
 return ps


def domains():
 mask=0xffffffff;accepted={16:0,64:0}
 for q in range(256):
  for nxt in range(256):
   delta=nxt-q;word=delta&mask;signed=word if word<2**31 else word-2**32
   check(signed==delta and -255<=delta<=255,'B1NVwrite signednext-minusrawQ domain')
   for L in (16,64):
    ok=signed>=L;check(ok==(nxt>=q+L),'B1NVwrite B1 existingrow signedguard')
    accepted[L]+=ok
 check(accepted=={16:28920,64:18528},'B1NVwrite exactcapacity-pair census')
 for q in range(256):
  check((q>>2)*4==q&252,'B1NVwrite header usesalignedrawQ')
  for L in (16,64):
   step=(((L+3)&mask)&~3)+4;nextword=(q+step)&mask
   check(step==L+4 and (nextword&255)==(q+L+4)%256,'B1NVwrite B1 nextfield narrowing')
 for L in range(65536):
  record=((L+3)&~3)+4
  check(record%4==0 and L+4<=record<=L+7,'B1NVwrite boundedL alignment overhead')
  check(record==4+((L+3)//4)*4,'B1NVwrite alignment equivalence')
 # Numeric product certificates only. All products fit U32; allocator narrows to U16.
 samples=(0,1,63,64,65,255,256,257,512,1024,32768,65535)
 product_cases=0
 for count in range(256):
  for size in samples:
   product=count*size
   check(0<=product<=255*65535<2**32 and (product&65535)==product%65536,'B1NVwrite RAM alloc low16 vsappendfullproduct');product_cases+=1
 check(255*65535==16711425 and (128*512)&65535==0,'B1NVwrite product limit/narrowing differs')
 # Boundary comparison difference, independently of any actual buffer/config value.
 for endpoint in range(256):
  check(not(endpoint<endpoint) and endpoint<=endpoint,'B1NVwrite configured strict/RAM inclusive endpoint')
 for i in range(255):check(0x7000<=0x7000+i<=0x7ffe,'B1NVwrite B1 numericIDdomain')
 return dict(rawQ_next_U8_pairs=65536,existingrow_accept_counts=accepted,B1_nextfield_cases=512,bounded_U16_L_alignment_cases=65536,
  RAM_product_sample_cases=product_cases,RAM_count_domain='allU8',RAM_size_samples=samples,RAM_fullproduct_max=16711425,
  allocation='RAM allocation low16(count*size),append guard full product;different fresh field reads',
  existingrow_guard='S32(U8next-rawQ)>=S32(fullL);B1L64 ispositive;no payloadextent guaranteefromthisdifference alone',
  append_guard='configured:U32(rawQ+L+4)<U32(freshU16size-64);RAM:U32(rawQ+L+4)<=freshU8count*freshU16size',
  append_next='low8(U32(rawQ+4+(U32(L+3)&~3)));no guard afterrounding/narrowing',
  no_progress_or_bounds_proof='nextbyte can revisit headers;rawQ andalignedheader differ;guard usesrawQ;no visited/extent/iteration checks',target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,SIZE)
 check(sparse.captured(mem,pc,SIZE)==raw,'B1NVwrite fulloriginal sparseHEX');b=body(raw,index);n={d['pc']-pc:d for d in b['instructions']}
 G=0x20003000;F=G+492+80*index;C=G+412+80*index
 check(n[4]['imm']+n[8]['imm']==F and n[0x22]['imm']==492+80*index and n[0x4e]['imm']+n[0x52]['imm']==C and n[0x11e]['imm']+n[0x128]['imm']==C and n[0x1e0]['imm']+n[0x1e4]['imm']==C,'B1NVwrite config/context addresses')
 check(parent['globals']['config']==F and parent['globals']['context']==C,'B1NVwrite sameNVread context')
 check(n[0x2a]['imm']==60 and [n[a]['imm'] for a in (0x42,0xbe,0x19e)]==[56]*3 and len(b['indirect_calls'])==2,'B1NVwrite F60 onlyguard;F56 reloadedatbothcalls')
 check([n[a]['rs2'] for a in (0x1c,0x1e,0x20)]==[10,11,12] and n[0x88]['rs2']==9 and n[0x8a]['rs2']==19 and n[0x170]['rs2']==9 and n[0x172]['rs2']==19,'B1NVwrite retainedfullID/L/input copyargs')
 check(n[0x2e]['imm']==10 and n[0xa2]['imm']==0 and n[0xa8]['imm']==n[0x188]['imm']==n[0x22e]['imm']==78,'B1NVwrite normalstatuses/alloctag')
 check(n[0x168]['op']=='blt' and n[0x21c]['op']=='bge' and n[0x1c6]['op']=='bgeu' and n[0x258]['op']=='bltu','B1NVwrite signedexisting/unsignedappend strictness')
 check(n[0x146]['imm']==n[0x1fa]['imm']==255 and n[0x1b0]['width']==n[0x220]['width']==2 and n[0x1b0]['imm']==n[0x220]['imm']==0,'B1NVwrite SH00FF key notmarker/FFFF')
 check(n[0x142]['imm']==n[0x1f6]['imm']==90 and n[0x1dc]['width']==1 and n[0x1dc]['imm']==3 and n[0x1ce]['imm']==-4 and n[0x1d0]['imm']==4,'B1NVwrite appendmarker/nextbyte/alignment')
 check([n[a]['imm'] for a in (0x22a,0x24c)]==[14]*2 and [n[a]['imm'] for a in (0x22c,0x24a)]==[12]*2 and n[0x236]['imm']==n[0x238]['imm']==16 and n[0x24e]['op']=='mul','B1NVwrite RAMlow16allocation/fullproductappend distinction')
 upmod=previous.previous.previous.previous
 update=upmod.body(init.binding.take(data,upmod.STARTS[index][1],upmod.SIZES[1]),'update',index)
 un={d['pc']-update['start']:d for d in update['instructions']}
 check(next(d['target'] for d in update['calls'] if d['offset']==0x9e)==pc and un[0x96]['imm']==16 and un[0x98]['imm']==64 and un[0x9c]['rs2']==8 and un[0x44]['imm']==0x7000,'B1NVwrite actualupdater (7000+i,64,SP16) join')
 notify=upmod.body(init.binding.take(data,upmod.STARTS[index][2],upmod.SIZES[2]),'notify',index)
 check(next(d['target'] for d in update['calls'] if d['offset']==0xaa)==notify['start'] and sum(d['op']=='call_indirect' and d['rs1']==14 for d in notify['instructions'])==1,'B1NVwrite laternotifier separatefromwrite wrapper')
 reuse=parent['reused_copy'];check(reuse['target']==0x20000332,'B1NVwrite reusedcopy mapping')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificate=common.certificates(b),paths=paths(b),globals=dict(config=F,context=C,buffer_word=C+32,owner_word=C+36),reused_copy=dict(reuse,new_code_bytes_counted=0),
  entry_contract=['captureID,L,input inS2/S1/S3;firstF8zero ->RAM;configured requiresF60nonnull thenF56nonnull;allnormal localreturns forced0 or10',
   'F60 isonlyguard,notcalledhere;onlyindirectcalls freshF56 reloadedwithoutnewnullguard;no privatefree inthisbody;no physicalNVwrite/persistence proof'],
  configured_low_contract=['C32null ->allocate(freshU16F12,78),publishC32 BEFOREnulltest;nonnullpath fetchfreshF8 andC36;owner mismatch ->F56(capturedfreshF8,freshU16F12>>2,freshC32),ignore reply;publishpostcallbackfreshF8 toC36',
   'ID2L16 headeroffset4*trunc_signed((freshU16F12-64)/4);ID3L16 (size-44)&~3;ID4L4 (size-24)&~3;ID256L<=8 (size-16)&~3;other/badL10 afterpossiblecache/callbackeffects',
   'freshC32+offset=H;SB5A H2 thenSHlow16ID H0 then copy(H4,originalinput,fullL),ignorecopyreply,return0;no prior marker/key validation'],
  configured_high_contract=['ID512..6FFF ->page=firstF8+freshU16F12*trunc_signed((ID-512)/6)mod32;7000..7FFE ->firstF8+size*(ID-7000)mod32;above10',
   'C32null ->allocate(freshU16F12,78),publishC32 beforetest;fetchC36;ifowner!=page ->freshF56(page,freshU16F12>>2,freshC32),ignore reply,store savedpageC36;thenfreshC32 isscanbaseB',
   'initialrawQ4,H=B+(rawQ>>2)*4;marker5A ->freshU16key/freshU8next;keymismatch rawQ=next. KeymatchS32(next-rawQ)<S32(L) ->SH255 H0 thenrawQ=next,continue;elsecopyexistingpayload',
   'firstmarker!=5A ->appendonlyifU32(rawQ+L+4)<U32(freshU16F12-64);equalrejects;no size>=64 prerequisite orpostroundingextent proof'],
  RAM_contract=['C32null ->allocate(low16(freshU8F14*freshU16F12),78),publishC32 beforetest;nonnull ->rereadC32scanbase. No callback/ownerupdate/fill/init here',
   'sameheader/key/next/signedcapacity scan andSH255 key oninsufficientmatch;appendguard usesfullfreshU8F14*freshU16F12 >=U32(rawQ+L+4),equalityaccepted',
   'guardfullproduct differsfromallocationlow16 andusesotherfreshreads;notproof ofallocated extent,initializedcache orvalidsource/destination'],
  shared_copy_append=['existingmatch copiesB+(rawQ&~3)+4,originalinput,L;guarddifference next-rawQdoesnotestablish completepayloadextent/headerseparation',
   'append step=U32((U32(L+3)&~3)+4);newnext=U32(rawQ+step);SB5A H2,SHlow16ID H0,SBlow8newnext H3 BEFOREcopy;no rollback ornextfieldrange/postrounding check',
   'allbranches useonecopy20000332,ignoreitsreply,then0.Matchingcopy may skiptransferonnull;0isnotproof ofinitializedpayload orphysicalcommit',
   'keytombstone is00FF (FF00 littleendian),notFFFF andnotmarkerinvalidating;priorSH/cache/owner/header effects mayremainonlater10'],
  B1_composition=['updater write(7000+i,64,SP16),i<=254 ->configuredupperpageindexi;actualread/write/copy/provider/extents remainconditional',
   'afterwrite returnsupdater independentlycallsnotifier44310/443a4 whichmaycallF60 andprivatefree/contextclear;notifierreply/ownership/freshpointeridentity separatelyconditional',
   'originalinputonlyheldS3andforwardedcopy,notdirectglobalpointerstore;cacheallocatorresultsC32 andpage/ownerC36arepublished;ambientregisters/alias/callees maystillretainborrowedpointers'],
  premises='conditionalcandidateISA/providers/firstcopymapping;validcode/frame/config/context/cache/header/payload/inputextents;ordinarycalleeS/SP/RA/framepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalities separate',
  physical_NV_write_actual_F60_binding_scan_termination_noescape_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-NVwrite-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_new_body_bytes=1212,complete_new_body_instructions=420,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['worker51f78/52020 andcore outputcontracts','actualF56/F60/config/contextwriter/providerbinding','callers/configsource constraints andfullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1NVwrite instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1NVwrite typedmutation escaped')
   typed+=1
 check((mutations,typed)==(420,20),'B1NVwrite mutationcensus');domains()
 print('PASS:420 instruction/20 typed-load mutations rejected;65536 rawQ/next pairs;alignment/product/strictness certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1NVwrite exactledger replay')
 print('PASS:1212B/420i complete NVwrite;strict HEX;allcalls/19stores/2loops;B1 write/notifier join;exact ledger')
 print('PASS:NO target execution/emulation;physicalcommit/providerbinding,termination andpointerlifetime UNPROVED')


if __name__=='__main__':main()
