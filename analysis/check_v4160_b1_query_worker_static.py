"""Offline complete query worker and record reschedule contracts.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable object/list/clock/provider/event model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_ram_query_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-query-worker-static.json')
ROLES=('worker','reschedule')
SIZES={'worker':832,'reschedule':128}
STARTS=({'worker': 354674, 'reschedule': 276136}, {'worker': 354994, 'reschedule': 276276})
COUNTS={'worker': 266, 'reschedule': 48}
HASHES=({'worker': '650ca752b602db340847d97634defb747e8215d08f7f0eb37c0637dcefbc4016', 'reschedule': 'a2cca1464a7ba296829f51a5c84acf5f1c75cfd32bc2e5b46ce254875b4d1346'}, {'worker': '7be1ba7cddf453cc1b659977441d20ae043975c19eef07bf0499c00ceb418500', 'reschedule': '13a04434d8c937d3721ec1c92d807df255a84c21df17419a5486c0617ff362d3'})
LITERALS={
'worker':"""
000 load 15 10 10 1
002 beq 15 0 828
006 load 15 10 128 2
00a addi 2 2 -16
00c store 2 8 8 4
00e store 2 1 12 4
010 store 2 9 4 4
012 addi 15 15 1
014 store 10 15 128 2
018 load 15 10 15 1
01a store 10 0 24 1
01e mv 8 10
020 andi 14 15 2
024 bnez 14 76
026 load 14 10 64 2
02a li 15 5
02c bltu 15 14 52
030 li 10 0
032 jump 66
034 addi 11 0 62
038 jal 1 354550
03c store 8 10 43 1
040 li 10 2
042 load 1 2 12 4
044 load 8 2 8 4
046 load 9 2 4 4
048 addi 2 2 16
04a jr 1
04c andi 14 15 32
050 beqz 14 168
052 andi 15 15 -33
056 store 10 15 15 1
058 load 15 10 160 4
05c load 14 10 11 1
05e store 10 0 43 1
062 ori 15 15 4
066 store 10 15 160 4
06a li 15 1
06c bne 14 15 168
070 load 15 10 58 2
072 addi 12 0 1250
076 load 14 10 148 4
07a mul 15 15 12
07e divu 15 15 14
082 lui 14 536883200
086 load 13 14 514 1
08a load 14 10 55 1
08e addi 13 13 80
092 mul 14 14 12
096 add 15 15 13
098 slli 15 15 16
09a srli 15 15 16
09c store 10 15 132 2
0a0 slli 15 15 1
0a2 add 15 15 14
0a4 store 10 15 130 2
0a8 load 15 8 17 1
0aa andi 15 15 1
0ac beqz 15 374
0ae load 15 8 94 2
0b2 load 14 8 64 2
0b6 bne 15 14 770
0ba load 15 8 60 2
0bc load 11 8 92 2
0c0 load 10 8 40 1
0c4 store 8 15 96 2
0c8 load 15 8 85 1
0cc store 8 11 62 2
0ce slli 11 11 4
0d0 store 8 15 55 1
0d4 load 15 8 86 2
0d8 addi 11 11 -2
0da lui 9 536883200
0de store 8 15 56 2
0e0 load 15 8 90 2
0e4 addi 9 9 564
0e8 store 8 15 60 2
0ea jal 1 275918
0ee load 14 8 11 1
0f0 store 8 0 128 2
0f4 load 15 8 56 2
0f6 bne 14 0 682
0fa load 14 9 8 2
0fc load 12 9 4 4
0fe mul 15 15 14
102 addi 14 0 800
106 addi 15 15 400
10a divu 15 15 14
10e load 14 8 144 4
112 addi 15 15 20
114 add 14 14 15
116 mv 13 14
118 bltu 14 15 288
11c bltu 14 12 292
120 sub 13 14 12
124 load 15 8 88 2
128 store 8 13 144 4
12c store 8 15 58 2
12e load 15 8 29 1
130 beqz 15 312
132 mv 10 8
134 jal 1 352890
138 load 14 9 8 2
13a load 15 8 58 2
13c addi 13 0 800
140 store 8 0 34 2
144 mul 15 15 14
148 divu 12 15 13
14c remu 15 15 13
150 addi 13 0 1250
154 store 8 12 140 4
158 mul 15 15 13
15c div 15 15 14
160 store 8 15 32 2
162 load 15 8 64 2
166 store 8 15 36 2
168 load 15 8 15 1
16a ori 15 15 32
16e store 8 15 15 1
170 load 15 8 17 1
172 andi 15 15 -2
174 store 8 15 17 1
176 load 15 8 17 1
178 andi 15 15 2
17a beqz 15 452
17c load 14 8 302 2
180 load 15 8 64 2
184 sub 13 14 15
188 slli 12 13 16
18c blt 12 0 780
190 bne 14 15 452
194 li 15 0
196 li 16 0
198 addi 9 8 312
19c store 8 15 312 4
1a0 store 8 16 316 4
1a4 li 12 5
1a6 addi 11 8 296
1aa mv 10 9
1ac auipc 1 536518656
1b0 jalr 1 1 -2028
1b4 mv 10 9
1b6 jal 1 359128
1ba load 15 8 17 1
1bc store 8 10 301 1
1c0 andi 15 15 -3
1c2 store 8 15 17 1
1c4 load 15 8 17 1
1c6 andi 14 15 16
1ca beqz 14 568
1cc load 13 8 332 2
1d0 load 14 8 64 2
1d4 sub 12 13 14
1d8 slli 11 12 16
1dc blt 11 0 780
1e0 bne 13 14 568
1e4 andi 15 15 -17
1e6 store 8 15 17 1
1e8 load 15 8 330 1
1ec beqz 15 508
1ee andi 14 15 2
1f2 beq 14 0 800
1f6 li 15 1
1f8 store 8 15 326 1
1fc load 15 8 331 1
200 beqz 15 528
202 andi 14 15 2
206 beq 14 0 814
20a li 15 1
20c store 8 15 327 1
210 mv 10 8
212 jal 1 352148
216 load 15 8 124 1
21a beqz 15 552
21c load 15 8 160 4
220 ori 15 15 256
224 store 8 15 160 4
228 load 15 8 160 4
22c store 8 0 43 1
230 ori 15 15 512
234 store 8 15 160 4
238 load 15 8 17 1
23a andi 14 15 32
23e beqz 14 630
240 lui 14 536883200
244 load 14 14 1036 4
248 addi 12 0 88
24c load 13 14 4 1
24e load 14 14 40 4
250 mul 13 13 12
254 add 14 14 13
256 load 13 14 28 2
258 load 14 8 64 2
25c sub 14 13 14
260 slli 12 14 16
264 blt 12 0 630
268 load 14 8 332 2
26c bne 14 13 630
270 andi 15 15 -33
274 store 8 15 17 1
276 load 15 8 42 1
27a andi 15 15 64
27e beq 15 0 48
282 load 14 8 70 2
286 load 15 8 64 2
28a bne 14 15 48
28e load 14 8 16 1
290 addi 15 0 74
294 bne 14 15 668
298 li 15 1
29a store 8 15 16 1
29c load 15 8 164 4
2a0 ori 15 15 1024
2a4 store 8 15 164 4
2a8 jump 48
2aa load 14 8 398 1
2ae load 12 8 88 2
2b2 andi 14 14 8
2b4 beqz 14 720
2b6 load 13 8 64 2
2ba load 14 8 400 2
2be load 11 8 58 2
2c0 sub 14 14 13
2c2 mul 14 14 11
2c6 div 14 14 12
2ca add 14 14 13
2cc store 8 14 400 2
2d0 beqz 15 766
2d2 load 14 9 8 2
2d4 load 11 9 4 4
2d6 mul 15 14 15
2da addi 14 0 800
2de addi 15 15 400
2e2 divu 15 15 14
2e6 load 14 8 144 4
2ea add 14 14 15
2ec mv 13 14
2ee bltu 14 15 758
2f2 bltu 14 11 762
2f6 sub 13 14 11
2fa store 8 13 144 4
2fe store 8 12 58 2
300 jump 312
302 sub 15 15 14
304 slli 14 15 16
308 bge 14 0 374
30c addi 11 0 40
310 mv 10 8
312 jal 1 354550
316 store 8 10 43 1
31a addi 10 0 40
31e jump 66
320 andi 15 15 4
322 beqz 15 808
324 li 15 2
326 jump 504
328 store 8 0 326 1
32c jump 508
32e andi 15 15 4
330 beqz 15 822
332 li 15 2
334 jump 524
336 store 8 0 327 1
33a jump 528
33c li 10 1
33e jr 1
""",
'reschedule':"""
000 addi 2 2 -32
002 store 2 18 16 4
004 lui 15 1073889280
008 store 2 1 28 4
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 19 12 4
010 load 18 15 524 4
014 store 15 0 524 4
018 fence.i 
01c li 15 15
01e bltu 15 10 116
022 li 14 12
024 mul 14 10 14
028 lui 15 536883200
02c load 15 15 556 4
030 add 15 15 14
032 load 15 15 0 4
034 beqz 15 116
036 li 8 1
038 sll 8 8 10
03c slli 8 8 16
03e srli 8 8 16
040 mv 9 11
042 li 10 0
044 mv 11 8
046 auipc 1 536596480
04a jalr 1 1 -986
04e mv 19 10
050 beqz 10 92
052 mv 11 8
054 li 10 0
056 jal 1 275850
058 store 19 9 8 4
05c lui 15 1073889280
060 store 15 18 524 4
064 li 10 0
066 load 1 2 28 4
068 load 8 2 24 4
06a load 9 2 20 4
06c load 18 2 16 4
06e load 19 2 12 4
070 addi 2 2 32
072 jr 1
074 lui 15 1073889280
078 store 15 18 524 4
07c li 10 2
07e jump 102
""",
}
PATCHES={'worker': {56: ('jal', [1, 354870]), 134: ('load', [13, 14, 594, 1]), 228: ('addi', [9, 9, 644]), 234: ('jal', [1, 276058]), 308: ('jal', [1, 353210]), 428: ('auipc', [1, 536514560]), 432: ('jalr', [1, 1, 1748]), 438: ('jal', [1, 359448]), 530: ('jal', [1, 352468]), 580: ('load', [14, 14, 1116, 4]), 786: ('jal', [1, 354870])}, 'reschedule': {44: ('load', [15, 15, 636, 4]), 74: ('jalr', [1, 1, -1126]), 86: ('jal', [1, 275990])}}
TYPED={'worker': [(6, 5), (38, 5), (88, 2), (118, 2), (134, 4), (138, 4), (174, 5), (178, 5), (188, 5), (192, 4), (200, 4), (212, 5), (224, 5), (270, 2), (292, 5), (354, 5), (380, 5), (384, 5), (460, 5), (464, 5), (488, 4), (508, 4), (534, 4), (540, 2), (552, 2), (580, 2), (600, 5), (616, 5), (630, 4), (642, 5), (646, 5), (668, 2), (682, 4), (686, 5), (694, 5), (698, 5), (742, 2)], 'reschedule': [(16, 2), (44, 2)]}
QK={'worker': [(0, '3c25', 'qk.c.lbu'), (24, '7c35', 'qk.c.lbu'), (86, '7cb5', 'qk.c.sb'), (92, '3835', 'qk.c.lbu'), (112, '3e3d', 'qk.c.lhu'), (168, '1c38', 'qk.c.lbu'), (186, '5e3c', 'qk.c.lhu'), (204, '6ebc', 'qk.c.sh'), (222, '1ebc', 'qk.c.sh'), (232, '5ebc', 'qk.c.sh'), (238, '3834', 'qk.c.lbu'), (244, '1e3c', 'qk.c.lhu'), (250, '9a24', 'qk.c.lhu'), (300, '3ebc', 'qk.c.sh'), (302, '5c3c', 'qk.c.lbu'), (312, '9a24', 'qk.c.lhu'), (314, '3e3c', 'qk.c.lhu'), (352, '1eb0', 'qk.c.sh'), (358, '5eb0', 'qk.c.sh'), (360, '7c34', 'qk.c.lbu'), (366, '7cb4', 'qk.c.sb'), (368, '1c38', 'qk.c.lbu'), (372, '1cb8', 'qk.c.sb'), (374, '1c38', 'qk.c.lbu'), (442, '1c38', 'qk.c.lbu'), (450, '1cb8', 'qk.c.sb'), (452, '1c38', 'qk.c.lbu'), (486, '1cb8', 'qk.c.sb'), (568, '1c38', 'qk.c.lbu'), (588, '5423', 'qk.c.lbu'), (598, '562f', 'qk.c.lhu'), (628, '1cb8', 'qk.c.sb'), (654, '1828', 'qk.c.lbu'), (666, '1ca8', 'qk.c.sb'), (702, '2e3c', 'qk.c.lhu'), (722, '9a24', 'qk.c.lhu'), (766, '32bc', 'qk.c.sh')], 'reschedule': []}
STORES={'worker': [(12, 2, 8, 8, 4), (14, 2, 1, 12, 4), (16, 2, 9, 4, 4), (20, 10, 15, 128, 2), (26, 10, 0, 24, 1), (60, 8, 10, 43, 1), (86, 10, 15, 15, 1), (94, 10, 0, 43, 1), (102, 10, 15, 160, 4), (156, 10, 15, 132, 2), (164, 10, 15, 130, 2), (196, 8, 15, 96, 2), (204, 8, 11, 62, 2), (208, 8, 15, 55, 1), (222, 8, 15, 56, 2), (232, 8, 15, 60, 2), (240, 8, 0, 128, 2), (296, 8, 13, 144, 4), (300, 8, 15, 58, 2), (320, 8, 0, 34, 2), (340, 8, 12, 140, 4), (352, 8, 15, 32, 2), (358, 8, 15, 36, 2), (366, 8, 15, 15, 1), (372, 8, 15, 17, 1), (412, 8, 15, 312, 4), (416, 8, 16, 316, 4), (444, 8, 10, 301, 1), (450, 8, 15, 17, 1), (486, 8, 15, 17, 1), (504, 8, 15, 326, 1), (524, 8, 15, 327, 1), (548, 8, 15, 160, 4), (556, 8, 0, 43, 1), (564, 8, 15, 160, 4), (628, 8, 15, 17, 1), (666, 8, 15, 16, 1), (676, 8, 15, 164, 4), (716, 8, 14, 400, 2), (762, 8, 13, 144, 4), (766, 8, 12, 58, 2), (790, 8, 10, 43, 1), (808, 8, 0, 326, 1), (822, 8, 0, 327, 1)], 'reschedule': [(2, 2, 18, 16, 4), (8, 2, 1, 28, 4), (10, 2, 8, 24, 4), (12, 2, 9, 20, 4), (14, 2, 19, 12, 4), (20, 15, 0, 524, 4), (88, 19, 9, 8, 4), (96, 15, 18, 524, 4), (120, 15, 18, 524, 4)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'queryworker literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'queryworker completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'queryworker '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'queryworker completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'queryworker typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'queryworker exactQK')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'queryworker RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   check(d['rd']==1,'queryworker allcallslinked')
   if op=='jal':target=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'queryworker linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('ecall','mret','csr','call_indirect') and all(z in n for z in q),'queryworker closedCFG');e[a]=q
 expected={'worker':[(0x38,0x568f6+320*index),(0xea,0x435ce+140*index),(0x134,0x5627a+320*index),(0x1b0,0x20000332),(0x1b6,0x57ad8+320*index),(0x212,0x55f94+320*index),(0x312,0x568f6+320*index)],'reschedule':[(0x4a,0x20000314),(0x56,0x4358a+140*index)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==([0x4a,0x33e] if role=='worker' else [0x72]),'queryworker exactcalls/RETs')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'queryworker allreachable/postRET')
 common=previous.previous.previous.previous.previous.previous.previous.previous.previous.previous.dispatch.common;groups=common.sccs(e);check(all(len(g)==1 and g[0] not in e[g[0]] for g in groups),'queryworker localCFG acyclic')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role] and len(stores)==(44 if role=='worker' else 9),'queryworker allstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,returns=rets,stores=stores,complete_local_body=True,local_CFG_acyclic=True,actual_callee_or_chain_completion_proved=False)


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
  ps=[p for z in ends if (p:=path(a,z)) is not None];check(bool(ps),'queryworker suffix');return min(ps,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'queryworker all-edge witness');walks.append([a-pc for a in p])
 # Count DAG paths and trace last A0 definitions backwards; no path explosion,
 # register-file execution, or target-state model. Calls count as opaque A0 defs.
 def countpaths(start,stop=None,blocked=()):
  cache={};blocked=set(blocked)
  def f(a):
   if a in blocked:return 0
   if a==stop:return 1
   if a in cache:return cache[a]
   cache[a]=(0 if stop is not None else 1) if not e[a] else sum(f(q) for q in e[a]);return cache[a]
  return f(start)
 preds={a:set() for a in e}
 for a,qs in e.items():
  for q in qs:preds[q].add(a)
 defs={pc+o for o,d in n.items() if d.get('rd')==10 or d['op'] in ('jal','jalr','call_indirect')}
 lastdefs=set();todo=ends[:];seen=set()
 while todo:
  a=todo.pop()
  if a in defs:lastdefs.add(a-pc);continue
  if a not in seen:seen.add(a);todo.extend(preds[a])
 codes={0x30:0,0x40:2,0x31a:40,0x33c:1} if role=='worker' else {0x64:0,0x7c:2}
 check(lastdefs==set(codes),'queryworker allreturn lastdefs areforcedconstants includingopaquechildreplies')
 last={}
 for o,code in codes.items():
  check(n[o]['imm']==code,'queryworker statusliteral');ways=countpaths(pc,pc+o)*countpaths(pc+o,blocked=defs-{pc+o});last[str(code)]=last.get(str(code),0)+ways
 total=countpaths(pc);check(total==sum(last.values()),'queryworker allDAGpaths classifiedbystatus')
 if role=='worker':
  check(set(last)=={'0','1','2','40'},'queryworker exactstatusdomain')
  check(n[0]['imm']==10 and n[2]['target']==pc+0x33c and n[0xa]['imm']==-16,'queryworker inactiveframeless1')
  check(n[0x12]['imm']==1 and n[0x14]['imm']==128 and n[0x1a]['imm']==24 and n[0x1a]['rs2']==0,'queryworker predecision counter/byteclear')
  check(n[0x20]['imm']==2 and n[0x26]['imm']==64 and n[0x2a]['imm']==5 and n[0x34]['imm']==62 and n[0x40]['imm']==2,'queryworker missingflag threshold62 vsreturn0')
  check(n[0x4c]['imm']==32 and n[0x52]['imm']==-33 and n[0x56]['imm']==15 and n[0x66]['imm']==160 and n[0x62]['imm']==4,'queryworker bit5 consumption/directflags')
  check(n[0x70]['imm']==58 and n[0x76]['imm']==148 and n[0x7e]['op']=='divu' and n[0x8e]['imm']==80 and n[0x9c]['imm']==132 and n[0xa4]['imm']==130,'queryworker localmode1 division/halfwordstores')
  check(n[0x144]['op']=='mul' and n[0x148]['op']=='divu' and n[0x14c]['op']=='remu' and n[0x15c]['op']=='div' and n[0x150]['imm']==1250,'queryworker remainder scaled signedDIV zero notguarded')
  check(n[0x188]['imm']==n[0x1d8]['imm']==n[0x304]['imm']==16 and n[0x18c]['op']==n[0x1dc]['op']=='blt' and n[0x308]['op']=='bge','queryworker signedlow16 scheduledcomparisons')
  check(n[0x30c]['imm']==40 and n[0x31a]['imm']==40,'queryworker sharedlateaction40')
  check(n[0x19c]['imm']==312 and n[0x1a0]['imm']==316 and n[0x194]['imm']==n[0x196]['imm']==0 and n[0x1a4]['imm']==5 and n[0x1a6]['imm']==296 and n[0x1bc]['imm']==301,'queryworker zeromask8/copy5/bytehelperreply')
  check(n[0x1f8]['imm']==n[0x328]['imm']==326 and n[0x20c]['imm']==n[0x336]['imm']==327 and n[0x1e8]['imm']==330 and n[0x1fc]['imm']==331,'queryworker optionaloutputs separatebytes andzero input skip')
  check(n[0x244]['imm']==1036+80*(b['start']!=STARTS[0]['worker']) and n[0x248]['imm']==88 and n[0x256]['imm']==28,'queryworker externalindexedsource notobjectextentproof')
  check(n[0x282]['imm']==70 and n[0x286]['imm']==64 and n[0x290]['imm']==74 and n[0x29a]['imm']==16 and n[0x2a0]['imm']==1024,'queryworker tailconditionalP16/P164')
  check(n[0x2ba]['imm']==n[0x2cc]['imm']==400 and n[0x2c6]['op']=='div','queryworker separateP400 signedDIV')
  info=dict(frame_bytes=16,inactive_frameless_return=1,normal_statuses=[0,1,2,40],explicit_object_extent=402,partial_updates_precede_nonzero_return=True,no_local_P_nullguard=True)
 else:
  check(set(last)=={'0','2'},'reschedule exactstatusdomain')
  check(n[0x10]['imm']==n[0x14]['imm']==n[0x60]['imm']==n[0x78]['imm']==524 and n[0x18]['op']=='fence.i','reschedule control-beforeguards/restore')
  check(n[0x1c]['imm']==15 and n[0x1e]['op']=='bltu' and n[0x1e]['target']==pc+0x74 and n[0x22]['imm']==12 and n[0x2c]['imm']==556+80*(b['start']!=STARTS[0]['reschedule']),'reschedule fullindex guard/arena word')
  check(n[0x32]['imm']==0 and n[0x34]['target']==pc+0x74 and n[0x40]['rs2']==11 and n[0x42]['imm']==n[0x54]['imm']==0 and n[0x44]['rs2']==n[0x52]['rs2']==8,'reschedule heldscalar/lookup-clear task0 mask')
  check(n[0x4e]['rs2']==10 and n[0x50]['target']==pc+0x5c and n[0x58]['rs1']==19 and n[0x58]['rs2']==9 and n[0x58]['imm']==8,'reschedule null lookup skipsrewrite still0')
  check(e[pc+0x56]==[pc+0x58] and n[0x60]['rs2']==18 and n[0x78]['rs2']==18,'reschedule retainedL write afteropaqueclear thenrestore')
  info=dict(frame_bytes=32,normal_statuses=[0,2],admitted_fullword_index=[0,15],arena_access_end_exclusive=184,lookup_null_can_return0=True,only_dynamic_output='U32[heldLookupL+8]=heldentryA1 afterclear',actual_rewrite_or_L_lifetime_proved=False)
 check((len(walks),total)==({'worker':(299,78534),'reschedule':(50,4)}[role]),'queryworker complete edge/DAG census')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),all_local_DAG_path_count=total,last_A0_definition_offsets=sorted(lastdefs),syntactic_status_path_counts=last,selected_entry_exit_walks={hex(c['offset']):[v-pc for v in path(pc,pc+c['offset'])+finish(pc+c['offset'])[1:]] for c in b['calls']},facts=info,syntax_path_feasibility_or_callee_success_proved=False)


def domains():
 indices=[]
 for i in range(256):
  if i<=15:
   mask=(1<<i)&65535;check(mask and mask.bit_count()==1 and 12*i+4<=184,'reschedule mask/arena footprint');indices.append([i,mask,12*i])
 check(len(indices)==16,'reschedule alluint8caller IDs admittedsubset')
 for x in range(65536):
  check((x+1)&65535==(x+1)%65536,'worker U16increment')
  sign=(x if x<32768 else x-65536);check((sign<0)==(x>=32768),'worker signed16 difference')
 for b in range(256):check((0xffffffff+b+80)&65535==(b+79)&65535,'worker DIVUzero plusbyte80 low16')
 for k in range(65536):
  for h in (0,1,799,65535):
   p=h*k;num=(p%800)*1250;check(p<2**32 and 0<=num<=998750<2**31,'worker positive remainder-DIV numerator')
   if k:check(0<=num//k<=998750,'worker signedDIV positive operands')
   else:check(num==0 and (-1)&65535==65535,'worker K0 DIV low16ffff')
 for a in range(256):
  for b in range(256):
   c=(a+b)&255;out=c if c<=36 else c-37;check(0<=out<=218,'reusedselector initial count mayexceed36')
 check(set(range(312,320))-set(range(312,317))=={317,318,319},'worker zero8-copy5 tailbytes')
 check((0xffff+1)&65535==0 and ((1<<31)*65535)&0xffffffff==0x80000000,'worker signedP400 lowword cannegative')
 return dict(admitted_indices_masks=indices,worker_counter_signed16_cases=65536,worker_DIVUzero_byte_cases=256,worker_H_samples=[0,1,799,65535],worker_allK16_Hsample_pairs=262144,selector_byte_pair_cases=65536,selector_initial_count_interval=[0,218],selector_A0_not_success=True,closed_scalar_identities_only=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'queryworker fullstrictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()}
 qr=init.binding.take(data,previous.SOURCES[index],620);check(sparse.captured(mem,previous.SOURCES[index],620)==qr,'queryworker querycaller fullstrictHEX');qb=previous.body(qr,index);qn={d['pc']-previous.ENTRY:d for d in qb['instructions']}
 check(qb['calls'][4]['target']==STARTS[index]['worker'] and qn[0x152]['rs2']==8 and qn[0x15c]['op']=='bnez' and qn[0x15c]['target']==previous.ENTRY+0x23e,'queryworker nonzero worker ->queryforcedffffffff')
 callback=previous.previous;cp=callback.STARTS['record'];cr=init.binding.take(data,callback.SOURCES[index]['record'],90);check(sparse.captured(mem,callback.SOURCES[index]['record'],90)==cr,'reschedule callbackcaller fullstrictHEX');cb=callback.body(cr,'record',index);cn={d['pc']-cp:d for d in cb['instructions']}
 check(cb['calls'][1]['target']==STARTS[index]['reschedule'] and cn[0x34]['imm']==41 and cn[0x32]['imm']==12,'reschedule actualfreshID/calculatedSP12 args')
 import check_v4160_timer_helpers_static as timer
 src,clear,head,count,table,lh,ch=timer.DETAILS[index];lr=init.binding.take(data,src,30);cl=init.binding.take(data,clear,68)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];fs=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(fs+0x20000314-dest==src and dest<=0x20000314 and 0x20000314+30<=end and sparse.captured(mem,src,30)==lr and sha256(lr).hexdigest()==lh,'reschedule full lookup firstcopy/HEX/identity')
 check(sparse.captured(mem,clear,68)==cl and sha256(cl).hexdigest()==ch,'reschedule eventclear completeHEX/identity');ln=timer.decode(lr,0x20000314);clear_nodes=timer.decode(cl,clear)
 check(timer.outer.normalized(lr,((4,4),))==timer.outer.normalized(timer.LOOKUP,((4,4),)) and timer.outer.normalized(cl,((20,4),(36,4)))==timer.outer.normalized(timer.CLEAR,((20,4),(36,4))),'reschedule complete reusedtimer templates')
 check(bs['reschedule']['calls']==[dict(offset=0x4a,target=0x20000314),dict(offset=0x56,target=clear)],'reschedule bothreusedleaf joins')
 import check_v4160_local_selector_static as selector
 source,lp,l1,l2,sh=selector.DETAILS[index];sr=init.binding.take(data,source,166);ll=init.binding.take(data,lp,44)
 check(fs+0x200014c6-dest==source and 0x200014c6+166<=end and sparse.captured(mem,source,166)==sr and sparse.captured(mem,lp,44)==ll,'queryworker selector/shift fullfirstcopy/strictHEX')
 sb=selector.body(sr,'selector',0x200014c6,sh,(l1,l2));sl=selector.body(ll,'leaf',lp,selector.LEAF_HASH)
 check(qn[0x14e]['rs2']==qn[0x152]['rs2']==8 and qb['CFG'][previous.ENTRY+0x150]==[previous.ENTRY+0x152],'queryworker selectorA0reply notconsumed beforeargreset')
 import check_v4160_threshold_message_static as threshold
 tp=threshold.STARTS[index][0];tr=init.binding.take(data,tp,124);check(sparse.captured(mem,tp,124)==tr,'queryworker threshold completeHEX');th=threshold.body(tr,'threshold',index)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_querycaller=dict(start=previous.ENTRY,bytes=620,sha256=qb['sha256']),reused_recordcaller=dict(start=cp,bytes=90,sha256=cb['sha256']),reused_timer=dict(lookup=dict(start=0x20000314,source=src,bytes=30,sha256=lh),clear=dict(start=clear,bytes=68,sha256=ch)),reused_selector=dict(start=0x200014c6,source=source,bytes=166,sha256=sh,shift_start=lp,shift_bytes=44,shift_sha256=selector.LEAF_HASH,scalar_reply_ignored_by_query=True),reused_threshold=dict(start=tp,bytes=124,sha256=th['sha256']),
  contracts=['worker freshP10zero returns1 beforeframe. Elseframe16,incU16P128/clearP24 beforedecisions;P15bit1clear andP64<=5 returns0,elseaction(P,62)->P43low8 then2. Otherlate schedulefail callsaction(P,40)->P43low8 then40. All remaining ordinary exits force0',
   'worker modefields/gates/stores/callees retained complete;flagbytes17 independentlyfresh forbits0/1/4/5. Signed16 scheduleddifferences,notphysicaldeadline oratomiccoherentflags. Configpath updatesP132/P130 DIVU0 permitted;remainderpath usesDIV0->ffff;separateP400signedproduct/DIV alsozerounguarded',
   'worker maskpath zeroP312/P316,copy5(P312,P296),map57ad8(P312)low8->P301,clearP17bit1; P326/P327 separateconditionalwriters fromP330/P331,zero inputs skipstores. Objectlocalextent402,externalindexedsource/pointers unguarded,unknowncallees/alias/frame/retention remain',
   'query selector200014c6 writesP311/P310 andreturnslastprobe bit;queryimmediatelysetsA0=heldP thenworker,so no selector scalar-success gate. Actualfield preservation notimplied;worker0allowsquerycontinue,worker1/2/40 allmappedtoqueryffffffff afterpartialupdates',
   'reschedule controlword capture/zero/FENCE beforefullI<=15 andU32[arena+12I]!=0 guards;fail2. Accepted lookup(0,low16(1<<I)),L0stillreturn0. Lnonnull clearEvent(0,mask),ignoreclearreply,storeheldV toheldL8,normalreturn0. Lvalidity afterclear andactualrewrite notproved',
   'recordcallback usesfreshU8P41 asI andadjustedSP12word asV;matchingreschedule ordinaryreply0or2 propagated,handler ignoresit. Arenaoccupancy doesnotprove lookup success,nonnullbase/extent/ownership orcompletedcallback/payloadlifetime'],
  actual_installedbinding_extent_heapownership_rewrite_delivery_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-query-worker-and-record-reschedule-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=1920,complete_phase_body_instructions=628,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['worker435ce/5627a/55f94 and57ad8/57c18 mapper nestedcontracts','post-clear lookupnode L lifetime andactualarena/timer/query/recordidentity','5d006/5d14e,clock/failurehookbindings/otherwriters/fullpointerlifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('queryworker instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('queryworker typedmutation escaped')
    typed+=1
 check((mutated,typed)==(628,78),'queryworker mutationcensus')
 print('PASS:628 instruction/78 typed-load mutations rejected;complete workerstatus/reschedule guards andretainednode boundary')


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
 else:check(OUT.read_bytes()==encoded,'queryworker exactledger replay')
 print('PASS:1920B/628i complete worker/reschedule;strictHEX;selector/query/timer joins;allDAGstatuses;exactledger')
 print('PASS:NO target execution/emulation;provider/lookupownership/fieldstability/full lifetimes UNPROVED')


if __name__=='__main__':main()
