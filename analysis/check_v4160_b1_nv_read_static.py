"""Offline complete NV read wrapper: original operands and immutable CFG paths.
Host scalar/interval certificates only; no target/provider/NV/RAM execution/model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_selector_callees_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-nv-read-static.json')
STARTS=(0x440c2,0x44156)
SIZE=590
HASHES=('da39a7b5c448cd6b60d0279fdb0154c7c1f6e9677a45247d19ab8865ab18ed88', '1d0923aeb246862f51a9899730743ae2e252a4c4759bf541bd868429a8fd699b')
COUNTS=(202, 202)
QK=(((158, 'b821', 'qk.c.lbu'), (168, '9e21', 'qk.c.lhu'), (442, 'b423', 'qk.c.lbu'), (448, '9623', 'qk.c.lhu'), (506, 'ac33', 'qk.c.lbu'), (554, '3023', 'qk.c.lbu'), (560, '1223', 'qk.c.lhu'), (586, '3c33', 'qk.c.lbu')), ((158, 'b821', 'qk.c.lbu'), (168, '9e21', 'qk.c.lhu'), (442, 'b423', 'qk.c.lbu'), (448, '9623', 'qk.c.lhu'), (506, 'ac33', 'qk.c.lbu'), (554, '3023', 'qk.c.lbu'), (560, '1223', 'qk.c.lhu'), (586, '3c33', 'qk.c.lbu')))
TYPED=(((42, 2), (66, 2), (78, 5), (102, 5), (106, 2), (110, 2), (118, 2), (122, 2), (140, 5), (224, 5), (246, 5), (252, 2), (256, 2), (278, 5), (300, 5), (322, 5), (358, 5), (386, 2), (392, 5), (412, 5), (416, 2), (472, 2), (510, 2), (534, 2)), ((42, 2), (66, 2), (78, 5), (102, 5), (106, 2), (110, 2), (118, 2), (122, 2), (140, 5), (224, 5), (246, 5), (252, 2), (256, 2), (278, 5), (300, 5), (322, 5), (358, 5), (386, 2), (392, 5), (412, 5), (416, 2), (472, 2), (510, 2), (534, 2)))
LITERALS=(
'''
000 addi 2 2 -32
002 store 2 19 12 4
004 lui 19 536883200
008 addi 15 19 492
00c load 15 15 8 4
00e store 2 9 20 4
010 store 2 18 16 4
012 store 2 20 8 4
014 store 2 1 28 4
016 store 2 8 24 4
018 store 2 21 4 4
01a store 2 22 0 4
01c mv 20 10
01e mv 9 11
020 mv 18 12
022 beq 15 0 530
026 addi 19 19 492
02a load 14 19 56 4
02e beq 14 0 338
032 addi 14 0 511
036 bltu 14 10 342
03a lui 8 536883200
03e addi 14 8 412
042 load 21 14 32 4
046 addi 8 8 412
04a bne 21 0 218
04e load 10 19 12 2
052 lui 11 20480
054 addi 11 11 -511
058 auipc 1 536592384
05c jalr 1 1 -218
060 store 8 10 32 4
062 mv 12 10
064 beqz 10 338
066 load 11 19 12 2
06a load 15 19 56 4
06e load 10 19 8 4
072 srli 11 11 2
074 call_indirect 1 15
076 load 15 19 8 4
07a load 21 8 32 4
07e store 8 15 36 4
080 li 15 2
082 bne 20 15 266
086 li 15 16
088 bne 9 15 338
08c load 11 19 12 2
090 li 15 4
092 addi 11 11 -64
096 div 11 11 15
09a slli 11 11 2
09c add 11 11 21
09e load 14 11 2 1
0a0 addi 15 0 90
0a4 bne 14 15 330
0a8 load 15 11 0 2
0aa bne 15 20 330
0ae mv 10 18
0b0 mv 12 9
0b2 addi 11 11 4
0b4 auipc 1 536592384
0b8 jalr 1 1 444
0bc load 15 8 32 4
0be mv 10 21
0c0 bne 15 21 482
0c4 li 10 0
0c6 load 1 2 28 4
0c8 load 8 2 24 4
0ca load 9 2 20 4
0cc load 18 2 16 4
0ce load 19 2 12 4
0d0 load 20 2 8 4
0d2 load 21 2 4 4
0d4 load 22 2 0 4
0d6 addi 2 2 32
0d8 jr 1
0da load 14 8 36 4
0dc beq 15 14 128
0e0 load 10 19 12 2
0e4 lui 11 20480
0e6 addi 11 11 -510
0ea auipc 1 536592384
0ee jalr 1 1 -364
0f2 mv 21 10
0f4 beqz 10 338
0f6 load 11 19 12 2
0fa mv 12 10
0fc load 15 19 56 4
100 load 10 19 8 4
104 srli 11 11 2
106 call_indirect 1 15
108 jump 128
10a li 15 3
10c bne 20 15 290
110 li 15 16
112 bne 9 15 338
116 load 11 19 12 2
11a addi 11 11 -44
11e andi 11 11 -4
120 jump 156
122 li 15 4
124 bne 20 15 308
128 bne 9 20 338
12c load 11 19 12 2
130 addi 11 11 -24
132 jump 286
134 addi 15 0 256
138 bne 20 15 338
13c li 15 8
13e bltu 15 9 338
142 load 11 19 12 2
146 addi 11 11 -16
148 jump 286
14a load 15 8 32 4
14c mv 10 21
14e bne 15 21 520
152 li 10 10
154 jump 198
156 lui 21 28672
158 bgeu 10 21 492
15c addi 21 10 -512
160 li 14 6
162 div 21 21 14
166 load 14 19 12 2
16a lui 22 536883200
16e mul 21 21 14
172 add 21 21 15
174 addi 15 22 412
178 load 15 15 36 4
17a addi 22 22 412
17e bne 15 21 392
182 load 8 22 32 4
186 bnez 8 428
188 load 10 19 12 2
18c addi 11 0 78
190 auipc 1 536592384
194 jalr 1 1 -530
198 mv 8 10
19a beqz 10 338
19c load 11 19 12 2
1a0 load 15 19 56 4
1a4 mv 12 10
1a6 srli 11 11 2
1a8 mv 10 21
1aa call_indirect 1 15
1ac li 11 4
1ae addi 14 0 90
1b2 srli 11 11 2
1b4 slli 15 11 2
1b8 add 15 15 8
1ba load 13 15 2 1
1bc bne 13 14 510
1c0 load 13 15 0 2
1c2 bne 13 20 506
1c6 addi 11 11 1
1c8 slli 11 11 2
1ca mv 12 9
1cc add 11 11 8
1ce mv 10 18
1d0 auipc 1 536592384
1d4 jalr 1 1 160
1d8 load 15 22 32 4
1dc beq 15 8 196
1e0 mv 10 8
1e2 auipc 1 536592384
1e6 jalr 1 1 -404
1ea jump 196
1ec lui 14 32768
1ee addi 14 14 -2
1f0 bltu 14 10 338
1f4 sub 21 10 21
1f8 jump 358
1fa load 11 15 3 1
1fc jump 434
1fe load 15 22 32 4
202 beq 15 8 338
206 mv 10 8
208 auipc 1 536592384
20c jalr 1 1 -442
210 jump 338
212 lui 15 536883200
216 load 11 15 444 4
21a beqz 11 338
21c li 15 4
21e addi 13 0 90
222 srli 15 15 2
224 slli 14 15 2
228 add 14 14 11
22a load 12 14 2 1
22c bne 12 13 338
230 load 12 14 0 2
232 bne 12 20 586
236 addi 15 15 1
238 slli 15 15 2
23a mv 12 9
23c add 11 11 15
23e mv 10 18
240 auipc 1 536592384
244 jalr 1 1 48
248 jump 196
24a load 15 14 3 1
24c jump 546
''',
'''
000 addi 2 2 -32
002 store 2 19 12 4
004 lui 19 536883200
008 addi 15 19 572
00c load 15 15 8 4
00e store 2 9 20 4
010 store 2 18 16 4
012 store 2 20 8 4
014 store 2 1 28 4
016 store 2 8 24 4
018 store 2 21 4 4
01a store 2 22 0 4
01c mv 20 10
01e mv 9 11
020 mv 18 12
022 beq 15 0 530
026 addi 19 19 572
02a load 14 19 56 4
02e beq 14 0 338
032 addi 14 0 511
036 bltu 14 10 342
03a lui 8 536883200
03e addi 14 8 492
042 load 21 14 32 4
046 addi 8 8 492
04a bne 21 0 218
04e load 10 19 12 2
052 lui 11 20480
054 addi 11 11 -511
058 auipc 1 536592384
05c jalr 1 1 -366
060 store 8 10 32 4
062 mv 12 10
064 beqz 10 338
066 load 11 19 12 2
06a load 15 19 56 4
06e load 10 19 8 4
072 srli 11 11 2
074 call_indirect 1 15
076 load 15 19 8 4
07a load 21 8 32 4
07e store 8 15 36 4
080 li 15 2
082 bne 20 15 266
086 li 15 16
088 bne 9 15 338
08c load 11 19 12 2
090 li 15 4
092 addi 11 11 -64
096 div 11 11 15
09a slli 11 11 2
09c add 11 11 21
09e load 14 11 2 1
0a0 addi 15 0 90
0a4 bne 14 15 330
0a8 load 15 11 0 2
0aa bne 15 20 330
0ae mv 10 18
0b0 mv 12 9
0b2 addi 11 11 4
0b4 auipc 1 536592384
0b8 jalr 1 1 296
0bc load 15 8 32 4
0be mv 10 21
0c0 bne 15 21 482
0c4 li 10 0
0c6 load 1 2 28 4
0c8 load 8 2 24 4
0ca load 9 2 20 4
0cc load 18 2 16 4
0ce load 19 2 12 4
0d0 load 20 2 8 4
0d2 load 21 2 4 4
0d4 load 22 2 0 4
0d6 addi 2 2 32
0d8 jr 1
0da load 14 8 36 4
0dc beq 15 14 128
0e0 load 10 19 12 2
0e4 lui 11 20480
0e6 addi 11 11 -510
0ea auipc 1 536592384
0ee jalr 1 1 -512
0f2 mv 21 10
0f4 beqz 10 338
0f6 load 11 19 12 2
0fa mv 12 10
0fc load 15 19 56 4
100 load 10 19 8 4
104 srli 11 11 2
106 call_indirect 1 15
108 jump 128
10a li 15 3
10c bne 20 15 290
110 li 15 16
112 bne 9 15 338
116 load 11 19 12 2
11a addi 11 11 -44
11e andi 11 11 -4
120 jump 156
122 li 15 4
124 bne 20 15 308
128 bne 9 20 338
12c load 11 19 12 2
130 addi 11 11 -24
132 jump 286
134 addi 15 0 256
138 bne 20 15 338
13c li 15 8
13e bltu 15 9 338
142 load 11 19 12 2
146 addi 11 11 -16
148 jump 286
14a load 15 8 32 4
14c mv 10 21
14e bne 15 21 520
152 li 10 10
154 jump 198
156 lui 21 28672
158 bgeu 10 21 492
15c addi 21 10 -512
160 li 14 6
162 div 21 21 14
166 load 14 19 12 2
16a lui 22 536883200
16e mul 21 21 14
172 add 21 21 15
174 addi 15 22 492
178 load 15 15 36 4
17a addi 22 22 492
17e bne 15 21 392
182 load 8 22 32 4
186 bnez 8 428
188 load 10 19 12 2
18c addi 11 0 78
190 auipc 1 536592384
194 jalr 1 1 -678
198 mv 8 10
19a beqz 10 338
19c load 11 19 12 2
1a0 load 15 19 56 4
1a4 mv 12 10
1a6 srli 11 11 2
1a8 mv 10 21
1aa call_indirect 1 15
1ac li 11 4
1ae addi 14 0 90
1b2 srli 11 11 2
1b4 slli 15 11 2
1b8 add 15 15 8
1ba load 13 15 2 1
1bc bne 13 14 510
1c0 load 13 15 0 2
1c2 bne 13 20 506
1c6 addi 11 11 1
1c8 slli 11 11 2
1ca mv 12 9
1cc add 11 11 8
1ce mv 10 18
1d0 auipc 1 536592384
1d4 jalr 1 1 12
1d8 load 15 22 32 4
1dc beq 15 8 196
1e0 mv 10 8
1e2 auipc 1 536592384
1e6 jalr 1 1 -552
1ea jump 196
1ec lui 14 32768
1ee addi 14 14 -2
1f0 bltu 14 10 338
1f4 sub 21 10 21
1f8 jump 358
1fa load 11 15 3 1
1fc jump 434
1fe load 15 22 32 4
202 beq 15 8 338
206 mv 10 8
208 auipc 1 536592384
20c jalr 1 1 -590
210 jump 338
212 lui 15 536883200
216 load 11 15 524 4
21a beqz 11 338
21c li 15 4
21e addi 13 0 90
222 srli 15 15 2
224 slli 14 15 2
228 add 14 14 11
22a load 12 14 2 1
22c bne 12 13 338
230 load 12 14 0 2
232 bne 12 20 586
236 addi 15 15 1
238 slli 15 15 2
23a mv 12 9
23c add 11 11 15
23e mv 10 18
240 auipc 1 536592384
244 jalr 1 1 -100
248 jump 196
24a load 15 14 3 1
24c jump 546
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1NV literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1NV typedload encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'B1NV complete boundaries')
 for a,f in s.items():init.g(n,a,'B1NV operand '+hex(a-pc),**f)
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1NV Xwchc load encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'B1NV completeidentity')
 edges={};calls=[];indirect=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1NV RET RA');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1NV adjacent callpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':
   check(d['rd']==1 and d['rs1']==15,'B1NV indirect RA/A5');indirect.append(dict(offset=a-pc,register=15,bit0_cleared=True))
  else:check(op!='jal','B1NV no unlisted directJAL')
  check(all(z in n for z in q),'B1NV closedCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1NV all localnodes reachable')
 cuts={(0x1fc,0x1b2),(0x24c,0x222)}
 cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in edges.items()}
 check(not common.acyclic(edges) and common.acyclic(cut),'B1NV exact two rowloop cuts')
 expected=[(0x5c,0x20000040),(0xb8,0x20000332),(0xee,0x20000040),(0x194,0x20000040),(0x1d4,0x20000332),(0x1e6,0x20000110),(0x20c,0x20000110),(0x244,0x20000332)]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and [d['offset'] for d in indirect]==[0x74,0x106,0x1aa] and rets==[pc+0xd8],'B1NV all direct/indirect/return sites')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 frames={(19,12),(9,20),(18,16),(20,8),(1,28),(8,24),(21,4),(22,0)}
 saved=[d for d in stores if d['base']==2]
 check(len(saved)==8 and {(d['source'],d['imm']) for d in saved}==frames and all(d['bytes']==4 for d in saved),'B1NV full32B savedframe')
 check([d for d in stores if d['base']!=2]==[dict(offset=0x60,base=8,source=10,imm=32,bytes=4),dict(offset=0x7e,base=8,source=15,imm=36,bytes=4)],'B1NV exact two nonframe context stores')
 check([a-pc for a,d in n.items() if d.get('rd')==18]==[0x20,0xcc] and [a-pc for a,d in n.items() if d.get('rd')==9]==[0x1e,0xca],'B1NV entryoutput/length heldS2/S1 untilrestore')
 return dict(start=pc,source=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,indirect_calls=indirect,tails=[],returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def valid_path(b,seq):
 pc=b['start'];e=b['CFG'];check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1NV immutable path');return seq


def paths(b):
 low={0x22:0x26,0x2e:0x32,0x36:0x3a}
 high={0x22:0x26,0x2e:0x32,0x36:0x156,0x158:0x15c}
 ram={0x22:0x212,0x21a:0x21c,0x22c:0x230,0x232:0x236}
 choices={
  'configured_missing_callback':{0x22:0x26,0x2e:0x152},
  'low_initial_alloc_fail':{**low,0x64:0x152},
  'low_initial_callback_match_keep':{**low,0x64:0x66,0xc0:0xc4},
  'low_initial_callback_match_free':{**low,0x64:0x66,0xc0:0x1e2},
  'low_cached_owner_match':{**low,0x4a:0xda,0xdc:0x80,0xc0:0xc4},
  'low_owner_mismatch_temp_alloc_fail':{**low,0x4a:0xda,0xdc:0xe0,0xf4:0x152},
  'low_owner_mismatch_temp_match_free':{**low,0x4a:0xda,0xdc:0xe0,0xf4:0xf6,0xc0:0x1e2},
  'low_ID2_wronglength':{**low,0x88:0x152},
  'low_ID3_match':{**low,0x82:0x10a,0x10c:0x110,0x112:0x116,0xc0:0xc4},
  'low_ID4_match':{**low,0x82:0x10a,0x10c:0x122,0x124:0x128,0x128:0x12c,0xc0:0xc4},
  'low_ID256_match':{**low,0x82:0x10a,0x10c:0x122,0x124:0x134,0x138:0x13c,0x13e:0x142,0xc0:0xc4},
  'low_other_ID_rejected':{**low,0x82:0x10a,0x10c:0x122,0x124:0x134,0x138:0x152},
  'low_bad_marker_free':{**low,0xa4:0x14a,0x14e:0x208},
  'high_new_alloc_fail':{**high,0x17e:0x188,0x19a:0x152},
  'high_new_callback_match_free':{**high,0x17e:0x188,0x19a:0x19c,0x1dc:0x1e0},
  'high_cached_match_keep':{**high,0x17e:0x182,0x186:0x1ac,0x1dc:0xc4},
  'high_cached_marker_fail_keep':{**high,0x17e:0x182,0x186:0x1ac,0x1bc:0x1fe,0x202:0x152},
  'high_new_marker_fail_free':{**high,0x17e:0x188,0x19a:0x19c,0x1bc:0x1fe,0x202:0x206},
  'high_upper_domain_match':{**high,0x158:0x1ec,0x1f0:0x1f4,0x17e:0x182,0x186:0x1ac,0x1dc:0xc4},
  'high_upper_rejected':{**high,0x158:0x1ec,0x1f0:0x152},
  'RAM_null':{0x22:0x212,0x21a:0x152},
  'RAM_marker_fail':{**ram,0x22c:0x152},'RAM_firstmatch':ram}
 ps={label:common.walk(b,c) for label,c in choices.items()}
 for label,source,branch,loop in [('RAM_one_mismatch_then_match','RAM_firstmatch',0x232,[0x24a,0x24c,0x222,0x224,0x228,0x22a,0x22c,0x230,0x232]),
  ('high_one_mismatch_then_match','high_cached_match_keep',0x1c2,[0x1fa,0x1fc,0x1b2,0x1b4,0x1b8,0x1ba,0x1bc,0x1c0,0x1c2])]:
  seq=ps[source];j=seq.index(branch);ps[label]=valid_path(b,seq[:j+1]+loop+seq[j+1:])
 check(all(a not in ps['RAM_firstmatch'] for a in (0x5c,0x74,0x106,0x194,0x1aa,0x1e6,0x20c)),'B1NV RAM route no alloc/callback/release')
 check(0x194 not in ps['high_cached_match_keep'] and 0x1aa not in ps['high_cached_match_keep'] and 0x1e6 not in ps['high_cached_match_keep'],'B1NV cached match path skipsalloc/read/free')
 return ps


def domains():
 mask=0xffffffff;page_cases=0
 for identity in range(512,0x7000):
  j=(identity-512)//6
  check(0<=j<=4693 and 512+6*j<=identity<512+6*(j+1),'B1NV configured lowpage quotient bounds');page_cases+=1
 for identity in range(0x7000,0x7fff):
  check(0<=identity-0x7000<=4094,'B1NV upperpage index bounds');page_cases+=1
 paired=[]
 for i in range(255):
  a,b=512+6*i,515+6*i
  check(a!=b and (a-512)//6==(b-512)//6==i and b<0x7000 and 0x7000+i<=0x7ffe,'B1NV B1 samepage/distinctfullID')
  paired.append([i,a,b,0x7000+i])
 for x in range(65536):check(x>>2==x//4 and (x>>2)*4<=x<(x>>2)*4+4,'B1NV U16 callback count truncation')
 # Complete integer domain for the signed special-ID2 size adjustment.
 for x in range(65536):
  y=x-64;q=(abs(y)//4)*(-1 if y<0 else 1)
  check(-16<=q<=16367 and abs(y-4*q)<=3 and (y-4*q==0 or (y-4*q>0)==(y>0)),'B1NV signedDIV truncates towardzero')
  check((4*q)&mask==((q&mask)<<2)&mask,'B1NV lowID2 modulo32 shift')
 displacements={}
 for q in range(256):
  off=(q>>2)<<2
  check(off==q&252 and off+4==((q>>2)+1)<<2,'B1NV rowheader/payload absoluteoffset')
  displacements.setdefault(off,[]).append(q)
 check(len(displacements)==64 and all(len(v)==4 for v in displacements.values()) and set(displacements[4])=={4,5,6,7},'B1NV offset64classes/no forcedprogress')
 # Pointer arithmetic interval obligations, not a simulated page or NV buffer.
 check(4+16==20 and 4+64==68 and 252+4+64==320,'B1NV needed source endpoints')
 check(0x7000-512+0x7fff-0x7000==page_cases==32255,'B1NV accepted configured highID census')
 return dict(configured_high_IDs=page_cases,B1_indices=255,B1_paired_numeric_requests=paired,U16_callback_count_cases=65536,U16_special_ID2_signed_DIV_cases=65536,
  U8_next_offset_cases=256,next_header_displacement_classes=64,next_header='base+(freshU8header3 & 252);absolute base,not relativecurrentrow',
  no_progress_certificate='fresh displacement4..7 maps backtoinitialheader base+4;no localcounter/extent/visitedguard;not a runtime reachability claim',
  copy_extent='fullentryL forwarded to matching bytecopy;B1L16 or64 ->payload+L localextent obligation',
  callback_extent='freshU16F12>>2 is a distinct numericargument;no physicalunits/writeextent/retention claim',target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,SIZE)
 check(sparse.captured(mem,pc,SIZE)==raw,'B1NV completeoriginal sparseHEX');b=body(raw,index);n={d['pc']-pc:d for d in b['instructions']}
 G=0x20003000;F=G+492+80*index;C=G+412+80*index
 check(n[4]['imm']+n[8]['imm']==F and n[0x26]['imm']==492+80*index and n[0x3a]['imm']+n[0x3e]['imm']==C and n[0x16a]['imm']+n[0x174]['imm']==C,'B1NV sameconfig/context allbranches')
 check(n[0x212]['imm']+n[0x216]['imm']==C+32,'B1NV no-base uses sameC32')
 check([n[a]['imm'] for a in (0x2a,0x6a,0xfc,0x1a0)]==[56]*4 and [n[a]['imm'] for a in (0x72,0x104,0x1a6)]==[2]*3,'B1NV freshcallback reload/countshift')
 check([n[a]['rs2'] for a in (0x1c,0x1e,0x20)]==[10,11,12],'B1NV entryID/L/O saves')
 check([n[a]['rs2'] for a in (0xb0,0x1ca,0x23a)]==[9]*3 and [n[a]['rs2'] for a in (0xae,0x1ce,0x23e)]==[18]*3,'B1NV fullL/originalO atallcopies')
 check(n[0x52]['imm']+n[0x54]['imm']==0x4e01 and n[0xe4]['imm']+n[0xe6]['imm']==0x4e02 and n[0x18c]['imm']==78,'B1NV allocationtags')
 check(n[0xc4]['imm']==0 and n[0x152]['imm']==10 and n[0x15c]['imm']==-512 and n[0x160]['imm']==6 and n[0x162]['op']=='div' and n[0x1ec]['imm']+n[0x1ee]['imm']==0x7ffe,'B1NV numericbounds/div/forcedstatus')
 for marker,key,nxt,reg in [(0x1ba,0x1c0,0x1fa,15),(0x22a,0x230,0x24a,14)]:
  check((n[marker]['rs1'],n[marker]['imm'],n[marker]['width'])==(reg,2,1) and (n[key]['rs1'],n[key]['imm'],n[key]['width'])==(reg,0,2) and (n[nxt]['rs1'],n[nxt]['imm'],n[nxt]['width'])==(reg,3,1),'B1NV row layout/width')
 check(n[0x1ae]['imm']==n[0x21e]['imm']==90 and n[0x1b8]['rs2']==8 and n[0x228]['rs2']==11,'B1NV mark5A/fixedbase scans')
 out=parent['bodies']['output']
 check(out['calls'][0]['target']==pc,'B1NV optionaloutput exactNVjoin')
 s=previous.specs('output',index);start=out['start'];check(s[start+0x22]['imm']==16 and s[start+0x20]['rs2']==2,'B1NV optionaloutput args')
 # Previous phase already checks selector/updater call sites. Revalidate these original full bodies here without adding code bytes.
 selector=previous.previous.body(init.binding.take(data,previous.previous.SOURCES[index][1],234),'selector',index)
 upmod=previous.previous.previous
 update=upmod.body(init.binding.take(data,upmod.STARTS[index][1],upmod.SIZES[1]),'update',index)
 check(next(d['target'] for d in selector['calls'] if d['offset']==0xae)==pc and [d['target'] for d in update['calls'] if d['offset'] in (0x1e,0x50)]==[pc,pc],'B1NV selector/updater exactjoins')
 reuse=parent['reused_leaves']['copy'];check(reuse['target']==0x20000332,'B1NV priorcompletecopy mapping')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificate=common.certificates(b),paths=paths(b),globals=dict(config=F,context=C,buffer_word=C+32,owner_word=C+36),reused_copy=dict(reuse,new_code_bytes_counted=0),
  entry_contract=['captureID,L,O inS4,S1,S2;firstF8null ->RAMroute;nonnull ->initialF56nonnull guard;allnormal localreturns forced0 or10',
   'threecallback sites freshlyreloadF56 withoutanothernullguard;callback/allocator/copy/privatefree repliesignoredexceptallocatornull. No O-null or L-bounds guard'],
  configured_high_contract=['ID512..6FFF ->page=firstF8+U16F12*trunc_signed((ID-512)/6)mod32;ID7000..7FFE ->firstF8+U16F12*(ID-7000)mod32;higherIDs10',
   'ifcapturedC36==page andfreshC32nonnull reuseP;elseallocate(freshU16F12,78),null10;freshF56(page,freshU16F12>>2,P);replyignored.Pnotpublishedbythisbranch',
   'scanheader startsP4;freshU8H2!=5A ->fail;elsefreshU16H0==fullID ->copy(O,H4,L);mismatchfreshU8H3 ->nextheaderP+(q&252). No scanextent/progressguard',
   'aftercopy:comparefreshC32withcapturedP,equal skipsrelease;differentprivatefree(P);return0. Markerfailure samepointercomparison/free then10. Pointerequality isnotownershipproof'],
  configured_low_contract=['ID0..511:loadC32;ifnull allocate(freshU16F12,4E01),publishreturntoC32 BEFORNullguard;nonnull ->freshF56(freshF8,freshU16F12>>2,P),thenfreshC32becomeslocalP andfreshF8storedC36',
   'existingP/C36==firstF8 reusesP;owner mismatch allocates(freshU16F12,4E02)temporary,callbackwithfreshF8/count/P,doesnotpublishtemporary',
   'ID2requiresL16,headerP+4*trunc_signed((freshU16F12-64)/4);ID3L16 ->P+((size-44)&~3);ID4L4 ->P+((size-24)&~3);ID256L<=8 ->P+((size-16)&~3);otherIDs10 AFTERpossibleallocation/callback',
   'same5A/U16fullID headercheck,copy(O,H4,L),freshC32comparison/conditionalprivatefreeP andforced0/10;specialheaderarithmeticoffersnoextent guarantee'],
  RAM_contract=['firstF8zero ->P=freshC32;null10;else same5A/U16fullID/absoluteU8nextoffsetscan;matchcopy(O,H4,L)then0,markerfail10',
   'noallocator,F56callbackorprivatefreeinthisroute;doesnotproveP/headers/payload/alias/actualinstalledprovider valid'],
  B1_composition=['512+6*i and515+6*i share configuredpagei,butfulloriginalIDs aredistinctrowkeys;no additional source+3 offsetinNVwrapper.B1 i<=254;7000+i uses separatepagei',
   'B1 L16/L64 reachesbytecopyunchanged;NVallocations/callbackcount insteaduse independentfreshsettingU16F12. MatchingcopyneedsL initializedsourcebytes andvalidnonnulloutput fordata proof',
   'zero statusdoesnotproveinitializedoutput:opaque callbackreplyignored,cached/RAMroutesnocallback;matchingcopy may skip payload transfer onnull while NVwrapper stillreturns0.MatchingRAMcopy guards/hardwareeffectsremainconditional'],
  pointer_contract=['originalO onlysavedinS2,forwardedto copy;no directglobalOstore inthiswrapper. Callbackreceivesheap/cacheP,notOinA2;ambientcallerregisters/alias maystillcarrypointers',
   'lowbranchpublishesallocatorpointerC32andfreshconfigbaseC36;hightemporarymaybefreedaftercopy accordingtofreshC32equality;no actualrelease/ownership/noescape/nonretention/complete lifetime proof'],
  premises='conditionalcandidateISA/firstcopymapping/providerbinding;validcode/frame/config/context/cache/row/payload/outputextents;ordinaryS/SP/RA/savedframepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshreadsnotassumedstable',
  physical_NV_units_callback_output_installed_binding_scan_termination_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-NVread-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_new_body_bytes=1180,complete_new_body_instructions=404,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['completeNVwrite4435c/443f0 branches','worker51f78/52020 andcore outputcontracts','actualF56/F60/config/contextwriter/providerbinding andfullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1NV instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1NV typedmutation escaped')
   typed+=1
 check((mutations,typed)==(404,48),'B1NV mutationcensus');domains()
 print('PASS:404 instruction/48 typed-load mutations rejected;32255 highIDs;255 B1 indexjoins;U16 count/signedDIV andU8 offset certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1NV exactledger replay')
 print('PASS:1180B/404i complete NVread;strict HEX;allbranches/calls/2loops;B1 copies andpagejoins;exact ledger')
 print('PASS:NO target execution/emulation;provider output,installedbinding,retention andtermination UNPROVED')


if __name__=='__main__':main()
