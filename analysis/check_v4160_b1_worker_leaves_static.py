"""Offline worker popcount, field clamps, grouped timer update and collision helper.
Original operands/immutable CFGs and closed host scalar/interval identities only.
No target execution/emulation, mutable object/list/clock/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_query_worker_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS={**previous.FIELDS,'sra':('rd','rs1','rs2')}
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-worker-leaves-static.json')
ROLES=('pop','config','group','collision')
SIZES={'pop':80,'config':200,'group':218,'collision':172}
STARTS=({'pop': 359128, 'config': 352148, 'group': 275918, 'collision': 352890}, {'pop': 359448, 'config': 352468, 'group': 276058, 'collision': 353210})
COUNTS={'pop': 33, 'config': 65, 'group': 75, 'collision': 56}
HASHES=({'pop': '1550f4b01eba5e1387db7248b8c59ea4ad41469869056efd88b3f143218fe5ec', 'config': 'f1c3a5d460d83b5f8bb29d3163d61d62ff71684089fea97ce7f63ef1338dcaa0', 'group': '553c155d0b120c72e1bcdd7e57a5dbd31317054604c7ec4ee3dcc519b636fb33', 'collision': '76bc718a63bafc8011dce63ddd482fed16a3f0d000d8b7333405074ff090e3d6'}, {'pop': '1550f4b01eba5e1387db7248b8c59ea4ad41469869056efd88b3f143218fe5ec', 'config': 'f1c3a5d460d83b5f8bb29d3163d61d62ff71684089fea97ce7f63ef1338dcaa0', 'group': 'c5f7113fc53f4867934a06a64cb08704f45ad2bffb931e1706e2e83351a984f8', 'collision': '993ba21c022dad0d8e2730bc2db08160b2957ac6e2d7637e46fda9e78041a50a'})
LITERALS={
'pop':"""
000 load 15 10 1 1
002 load 14 10 2 1
004 load 13 10 4 1
006 slli 15 15 8
008 slli 14 14 16
00a add 15 15 14
00c load 14 10 0 1
00e andi 13 13 31
010 li 16 1
012 add 15 15 14
014 load 14 10 3 1
016 addi 11 0 32
01a li 10 0
01c slli 14 14 24
01e add 15 15 14
020 li 14 0
022 sll 12 16 14
026 and 12 12 15
028 beqz 12 48
02a addi 10 10 1
02c andi 10 10 255
030 addi 14 14 1
032 bne 14 11 34
036 li 15 0
038 li 12 8
03a sra 14 13 15
03e andi 14 14 1
040 beqz 14 72
042 addi 10 10 1
044 andi 10 10 255
048 addi 15 15 1
04a bne 15 12 58
04e jr 1
""",
'config':"""
000 load 14 10 470 2
004 load 15 10 474 2
008 addi 2 2 -16
00a store 2 1 12 4
00c bgeu 14 15 18
010 mv 15 14
012 load 12 10 326 1
016 slli 14 15 16
01a li 13 2
01c srli 14 14 16
01e bne 12 13 148
022 lui 13 4096
024 addi 13 13 -1392
028 bgeu 14 13 46
02c mv 15 13
02e slli 14 15 16
032 srli 14 14 16
034 load 15 10 486 2
038 beq 15 14 70
03c li 15 1
03e store 10 14 486 2
042 store 10 15 124 1
046 load 14 10 466 2
04a load 15 10 478 2
04e bgeu 14 15 84
052 mv 15 14
054 load 12 10 327 1
058 slli 14 15 16
05c li 13 2
05e srli 14 14 16
060 bne 12 13 174
064 lui 13 4096
066 addi 13 13 -1392
06a bgeu 14 13 112
06e mv 15 13
070 slli 14 15 16
074 srli 14 14 16
076 load 15 10 482 2
07a beq 15 14 136
07e li 15 1
080 store 10 14 482 2
084 store 10 15 124 1
088 jal 1 351722
08c load 1 2 12 4
08e li 10 0
090 addi 2 2 16
092 jr 1
094 lui 15 4096
096 addi 12 15 -1976
09a bgeu 12 14 52
09e load 13 10 256 4
0a2 addi 15 15 -2048
0a6 and 15 15 13
0a8 bnez 15 52
0aa mv 14 12
0ac jump 52
0ae lui 15 4096
0b0 addi 12 15 -1976
0b4 bgeu 12 14 118
0b8 load 13 10 256 4
0bc addi 15 15 -2048
0c0 and 15 15 13
0c2 bnez 15 118
0c4 mv 14 12
0c6 jump 118
""",
'group':"""
000 addi 2 2 -32
002 store 2 18 16 4
004 lui 14 1073889280
008 store 2 1 28 4
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 19 12 4
010 store 2 20 8 4
012 load 18 14 524 4
016 store 14 0 524 4
01a fence.i 
01e addi 14 10 -16
022 andi 14 14 255
026 li 15 31
028 bltu 15 14 206
02c li 13 12
02e mul 13 10 13
032 lui 15 536883200
036 load 14 15 556 4
03a add 14 14 13
03c load 15 14 0 4
03e beqz 15 206
040 srli 9 10 4
044 li 8 1
046 andi 10 10 15
048 sll 10 8 10
04c slli 8 10 16
050 srli 8 8 16
052 mv 19 11
054 mv 10 9
056 mv 11 8
058 auipc 1 536596480
05c jalr 1 1 -786
060 mv 20 10
062 beqz 10 180
064 mv 11 8
066 mv 10 9
068 jal 1 275850
06a lui 15 536883200
06e load 15 15 480 4
072 lui 9 536883200
076 addi 9 9 564
07a call_indirect 1 15
07c load 15 9 8 2
07e mv 8 10
080 li 13 0
082 mul 11 15 19
086 addi 12 0 1600
08a mulhu 15 15 19
08e addi 10 11 800
092 sltu 11 10 11
096 add 11 11 15
098 jal 1 450330
09c add 15 10 8
0a0 mv 14 15
0a2 load 13 9 4 4
0a4 bltu 15 10 172
0a8 bltu 15 13 176
0ac sub 14 15 13
0b0 store 20 14 8 4
0b4 lui 15 1073889280
0b8 store 15 18 524 4
0bc li 10 0
0be load 1 2 28 4
0c0 load 8 2 24 4
0c2 load 9 2 20 4
0c4 load 18 2 16 4
0c6 load 19 2 12 4
0c8 load 20 2 8 4
0ca addi 2 2 32
0cc jr 1
0ce lui 15 1073889280
0d2 store 15 18 524 4
0d6 li 10 2
0d8 jump 190
""",
'collision':"""
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 addi 9 9 952
00c load 14 9 180 2
010 store 2 1 12 4
012 store 2 8 8 4
014 li 15 1
016 bgeu 15 14 92
01a mv 8 10
01c load 15 10 482 2
020 load 10 10 486 2
024 lui 14 536883200
028 lui 12 999424
02c add 15 15 10
02e load 10 14 572 2
032 addi 15 15 625
036 addi 12 12 576
03a mulhsu 11 15 10
03e li 13 0
040 mul 10 10 15
044 jal 1 450330
048 load 12 8 85 1
04c load 17 9 156 4
050 li 13 1
052 addi 12 12 -1
054 addi 6 0 40
058 bltu 13 12 102
05c load 1 2 12 4
05e load 8 2 8 4
060 load 9 2 4 4
062 addi 2 2 16
064 jr 1
066 mul 14 13 6
06a load 15 8 144 4
06e li 11 -1
070 add 14 14 15
072 mv 15 17
074 bnez 15 124
076 store 8 13 86 2
07a jump 92
07c bne 8 15 132
080 load 15 8 0 4
082 beqz 15 118
084 load 28 15 140 4
088 load 16 8 140 4
08c bne 28 16 160
090 load 16 15 144 4
094 sub 11 16 14
098 bltu 14 16 160
09c sub 11 14 16
0a0 bltu 11 10 168
0a4 load 15 15 0 4
0a6 jump 116
0a8 addi 13 13 1
0aa jump 88
""",
}
PATCHES={'pop': {}, 'config': {136: ('jal', [1, 352042])}, 'group': {54: ('load', [14, 15, 636, 4]), 92: ('jalr', [1, 1, -926]), 104: ('jal', [1, 275990]), 110: ('load', [15, 15, 560, 4]), 118: ('addi', [9, 9, 644]), 152: ('jal', [1, 450826])}, 'collision': {8: ('addi', [9, 9, 1032]), 46: ('load', [10, 14, 652, 2]), 68: ('jal', [1, 450826])}}
TYPED={'pop': [], 'config': [(0, 5), (4, 5), (18, 4), (52, 5), (70, 5), (74, 5), (84, 4), (118, 5), (158, 2), (184, 2)], 'group': [(18, 2), (54, 2), (110, 2)], 'collision': [(12, 5), (28, 5), (32, 5), (46, 5), (72, 4), (76, 2), (106, 2), (132, 2), (136, 2), (144, 2)]}
QK={'pop': [(0, '1c31', 'qk.c.lbu'), (2, '3821', 'qk.c.lbu'), (4, '5421', 'qk.c.lbu'), (12, '1821', 'qk.c.lbu'), (20, '3831', 'qk.c.lbu')], 'config': [], 'group': [(124, '9e24', 'qk.c.lhu')], 'collision': []}
STORES={'pop': [], 'config': [(10, 2, 1, 12, 4), (62, 10, 14, 486, 2), (66, 10, 15, 124, 1), (128, 10, 14, 482, 2), (132, 10, 15, 124, 1)], 'group': [(2, 2, 18, 16, 4), (8, 2, 1, 28, 4), (10, 2, 8, 24, 4), (12, 2, 9, 20, 4), (14, 2, 19, 12, 4), (16, 2, 20, 8, 4), (22, 14, 0, 524, 4), (176, 20, 14, 8, 4), (184, 15, 18, 524, 4), (210, 15, 18, 524, 4)], 'collision': [(2, 2, 9, 4, 4), (16, 2, 1, 12, 4), (18, 2, 8, 8, 4), (118, 8, 13, 86, 2)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'workerleaves literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'workerleaves completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'workerleaves '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'workerleaves completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'workerleaves typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'workerleaves exactQK')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'workerleaves RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr','call_indirect'):
   check(d['rd']==1,'workerleaves allcallslinked');target=d.get('target','freshA5')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'workerleaves linkedPCpair');target=(a-4+u['imm']+d['imm'])&0xfffffffe
   elif op=='call_indirect':check(d['rs1']==15,'workerleaves loadedA5clock')
   calls.append(dict(offset=a-pc,target=target))
  check(op not in ('ecall','mret','csr') and all(z in n for z in q),'workerleaves closedCFG');e[a]=q
 expected={'pop':[],'config':[(0x88,0x55dea+320*index)],'group':[(0x5c,0x20000314),(0x68,0x4358a+140*index),(0x7a,'freshA5'),(0x98,0x6df1a+496*index)],'collision':[(0x44,0x6df1a+496*index)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[{'pop':0x4e,'config':0x92,'group':0xcc,'collision':0x64}[role]],'workerleaves exactcalls/RET')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'workerleaves allreachable includingpostRET')
 common=previous.previous.previous.previous.previous.previous.previous.previous.previous.previous.previous.dispatch.common;groups=common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]]
 check(bool(cycles)==(role in ('pop','collision')),'workerleaves cycleclassification')
 check((sum(map(len,e.values())),sorted(map(len,cycles)))=={'pop':(36,[7,7]),'config':(76,[]),'group':(79,[]),'collision':(63,[22])}[role],'workerleaves exactedge/SCCcensus')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'workerleaves allstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,returns=rets,cyclic_SCCs=cycles,stores=stores,complete_local_body=True,actual_callee_or_list_return_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ret=pc+b['returns'][0]
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  raise RuntimeError('workerleaves no syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,ret)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'workerleaves all-edge witness');walks.append([a-pc for a in p])
 if role=='pop':
  check([(o,d['imm'],d['width']) for o,d in n.items() if d['op']=='load']==[(0,1,1),(2,2,1),(4,4,1),(0xc,0,1),(0x14,3,1)],'workerleaves fivefreshbytes loadorder')
  check(n[0xe]['imm']==31 and n[0x16]['imm']==32 and n[0x38]['imm']==8 and n[0x1a]['imm']==n[0x20]['imm']==n[0x36]['imm']==0,'workerleaves popcount37inputs/loopinits')
  check(n[0x30]['rd']==14 and n[0x30]['imm']==1 and n[0x32]['target']==pc+0x22 and n[0x48]['rd']==15 and n[0x48]['imm']==1 and n[0x4a]['target']==pc+0x3a,'workerleaves fixed32+8counts')
  check(not b['stores'] and not b['calls'] and {d['rd'] for d in n.values() if 'rd'in d}=={10,11,12,13,14,15,16},'workerleaves noframe/store/call/Sdefinitions')
  info=dict(input_extent=5,source_bits=[0,36],normal_reply_interval=[0,37],loop_counts=[32,8],fifthbyte_mask=31,no_direct_memory_writes=True)
 elif role=='config':
  check(n[0]['imm']==470 and n[4]['imm']==474 and n[0x46]['imm']==466 and n[0x4a]['imm']==478 and n[0xc]['op']==n[0x4e]['op']=='bgeu','workerleaves twoseparate unsignedmin lanes')
  check(n[0x12]['imm']==326 and n[0x54]['imm']==327 and n[0x1a]['imm']==n[0x5c]['imm']==2,'workerleaves exactmode2 tests')
  check(n[0x22]['imm']+n[0x24]['imm']==n[0x64]['imm']+n[0x66]['imm']==2704 and n[0x94]['imm']+n[0x96]['imm']==n[0xae]['imm']+n[0xb0]['imm']==2120 and n[0x94]['imm']+n[0xa2]['imm']==n[0xae]['imm']+n[0xbc]['imm']==2048,'workerleaves floor/cap/bit11constants')
  check(n[0x9e]['imm']==n[0xb8]['imm']==256 and n[0x3e]['imm']==486 and n[0x80]['imm']==482 and n[0x42]['imm']==n[0x84]['imm']==124,'workerleaves updatesandchangeflag1')
  check(n[0x3c]['imm']==n[0x7e]['imm']==1 and n[0x8e]['imm']==0 and not any(d.get('rd')==10 for o,d in n.items() if o<0x88),'workerleaves childreceivesP thenforced0')
  info=dict(frame_bytes=16,object_explicit_extent=488,mode2_floor=2704,othermode_cap_if_bit11clear=2120,halfword_outputs=[486,482],change_flag=124,normal_reply=0,child_may_change_fields_or_retain_P=True)
 elif role=='group':
  check(n[0x1e]['imm']==-16 and n[0x22]['imm']==255 and n[0x26]['imm']==31 and n[0x28]['target']==pc+0xce,'workerleaves low8guard notfullI')
  check(n[0x2e]['rs1']==10 and n[0x40]['rs1']==10 and n[0x40]['imm']==4 and n[0x46]['imm']==15,'workerleaves arena/task usefullindex beforelow4mask')
  check(n[0x52]['rs2']==11 and n[0x60]['rs2']==10 and n[0xb0]['rs1']==20 and n[0xb0]['imm']==8,'workerleaves heldV/heldL8')
  check(n[0x62]['target']==pc+0xb4 and n[0xbc]['imm']==0 and n[0xd6]['imm']==2,'workerleaves missinglookup still0/guard2')
  check(n[0x7c]['imm']==8 and n[0x82]['op']=='mul' and n[0x8a]['op']=='mulhu' and n[0x8e]['imm']==800 and n[0x86]['imm']==1600 and n[0x80]['imm']==0 and n[0x92]['op']=='sltu','workerleaves K*V+800 divisor1600 pair')
  check(n[0x9c]['op']=='add' and n[0xa2]['imm']==4 and n[0xa4]['op']==n[0xa8]['op']=='bltu' and n[0xac]['op']=='sub','workerleaves clockreply+opaquequotient oneperiodsubtract')
  check(n[0x12]['imm']==n[0x16]['imm']==n[0xb8]['imm']==n[0xd2]['imm']==524 and n[0x1a]['op']=='fence.i','workerleaves controlsave/restore')
  info=dict(frame_bytes=32,gate='low8(I-16)<=31',generic_fullindex_not_bounded_to47=True,worker_byteindex_admitted=[16,47],worker_task_interval=[1,2],normal_replies=[0,2],L_validity_across_clear_clock_arithmetic_unproved=True)
 else:
  check(n[0xc]['imm']==180 and n[0x14]['imm']==1 and n[0x16]['target']==pc+0x5c and n[0x1c]['imm']==482 and n[0x20]['imm']==486 and n[0x32]['imm']==625,'workerleaves countguard/positive halfwordsum')
  check(n[0x3a]['op']=='mulhsu' and n[0x40]['op']=='mul' and n[0x3e]['imm']==0 and n[0x28]['imm']+n[0x36]['imm']==1000000,'workerleaves nonnegativeMULHSU fullpair')
  check(not any(d.get('rd')==10 for o,d in n.items() if o>0x44) and n[0x1a]['rs2']==10,'workerleaves returnsentryP oncountgate/opaqueDotherwise')
  check(n[0x48]['imm']==85 and n[0x52]['imm']==-1 and n[0x50]['imm']==1 and n[0x54]['imm']==40 and n[0x58]['op']=='bltu','workerleaves byte-minus1 unsignedbound')
  check(n[0x4c]['imm']==156 and n[0x72]['rs2']==17 and n[0x66]['op']=='mul' and n[0x6a]['imm']==144,'workerleaves capturedhead restart/candidate+40i')
  check(n[0x84]['imm']==n[0x88]['imm']==140 and n[0x90]['imm']==144 and n[0xa0]['op']=='bltu' and n[0x6e]['imm']==-1 and n[0x8c]['target']==pc+0xa0,'workerleaves metric initializedonce/carryonmismatch/strictD')
  check([(o,d['rs1'],d['imm']) for o,d in n.items() if d['op']=='store' and d['rs1']!=2]==[(0x76,8,86)] and n[0x76]['width']==2 and n[0xa8]['imm']==1,'workerleaves onlyacceptedcandidate halfwordstore')
  info=dict(frame_bytes=16,object_explicit_extent=488,normal_reply='entryP ifcapturedcount<=1 elseopaque arithmeticD',local_halfword_store=86,byte85zero_bound=4294967295,finite_list_or_write_on_everyreturn_proved=False)
 selected=[c['offset'] for c in b['calls']]+[d['pc']-pc for d in b['instructions'] if d['op']=='store' and d['rs1']!=2]
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),cyclic_SCC_offsets=[[a-pc for a in g] for g in b['cyclic_SCCs']],selected_entry_exit_walks={hex(o):[v-pc for v in path(pc,pc+o)+path(pc+o,ret)[1:]] for o in selected},facts=info,actual_sourceinitialization_alias_or_complete_lifetime_proved=False)


def domains():
 for x in range(65536):
  word=x|(x<<16)
  for b in (0,1,31,255):
   low37=word|((b&31)<<32);count=2*x.bit_count()+(b&31).bit_count();check(count==low37.bit_count() and 0<=count<=37,'workerleaves disjointpopcount lane identities')
 for b in range(256):check((b&31).bit_count()<=5 and sum(((b&31)>>i)&1 for i in range(8))==(b&31).bit_count(),'workerleaves fifthbytemask/8positions')
 for v in range(65536):
  for mode in (0,1,2,255):
   for bit in (0,1):
    q=max(v,2704) if mode==2 else (min(v,2120) if not bit else v)
    check(0<=q<=65535 and (mode!=2 or q>=2704) and (mode==2 or bit or q<=2120),'workerleaves closedlane bounds')
 for i in range(256):check((((i-16)&255)<=31)==(16<=i<=47),'workerleaves bytecaller groupadmission')
 for hi in (0,1,0xffffff):
  for lo in range(256):
   full=(hi<<8)|lo;check((((full-16)&255)<=31)==(16<=lo<=47),'workerleaves genericguard onlylowbyte')
 check((((0x110-16)&255)<=31) and 0x110>>4==17,'workerleaves generic task outside1/2 witness')
 check(65535*0xffffffff+800<2**48 and 65535*(65535+65535+625)<2**34,'workerleaves full64request nooverflow')
 for b in range(256):
  bound=(b-1)&0xffffffff;check((1<bound)==(b==0 or b>=3),'workerleaves collisionloop byteunderflowgate')
 for d in (0,1,0x7fffffff,0xffffffff):
  check(not (0xffffffff<d),'workerleaves initialmetric neverconflicts')
  for carried in (d,0xffffffff):check(not (carried<d),'workerleaves previouslyacceptedmetric staysacceptedonmismatch')
 check(37<256 and 5+32==37 and ((1<<37)-1).bit_count()==37,'workerleaves countbyte no wrap/zero stillpossible')
 return dict(popcount_word_family_cases=262144,popcount_fifthbyte_cases=256,popcount_reply_interval=[0,37],count_zero_not_excluded=True,config_lane_cases=524288,config_floor=2704,config_cap=2120,generic_index_high_samples=[0,1,16777215],collision_bytebound_cases=256,byte85zero_candidate_upper_exclusive=4294967295,worker_object_nested_minimum=488,only_closed_scalar_identities=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'workerleaves fullstrictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()}
 wp=previous.STARTS[index]['worker'];wr=init.binding.take(data,wp,832);check(sparse.captured(mem,wp,832)==wr,'workerleaves fullworkercaller HEX');wb=previous.body(wr,'worker',index);wn={d['pc']-wp:d for d in wb['instructions']}
 expected={'pop':0x1b6,'config':0x212,'group':0xea,'collision':0x134}
 for role,o in expected.items():check(next(c['target'] for c in wb['calls'] if c['offset']==o)==bs[role]['start'],'workerleaves exactcaller target '+role)
 check(wn[0x198]['imm']==312 and wn[0x1b4]['rs2']==9 and wn[0x1bc]['imm']==301 and wn[0x1bc]['rs2']==10,'workerleaves popcall->P301writer')
 check(wn[0xc0]['imm']==40 and wn[0xbc]['imm']==92 and wn[0xce]['imm']==4 and wn[0xd8]['imm']==-2,'workerleaves groupactualbyteindex/fullscalarargument')
 import check_v4160_b1_b120_target_static as b120
 bp=b120.STARTS[index];br=init.binding.take(data,bp,1000);check(sparse.captured(mem,bp,1000)==br,'workerleaves B120fullHEX');bb=b120.body(br,index);bn={d['pc']-bp:d for d in bb['instructions']}
 check(next(c['target'] for c in bb['calls'] if c['offset']==0x44)==bs['pop']['start'] and bn[0x2a]['imm']==160 and bn[0x4a]['imm']==129 and bn[0x4a]['rs2']==10,'workerleaves otherpopcaller N129')
 # Reuse immediate original timer/arithmetic leaves without re-running a timer.
 import check_v4160_timer_helpers_static as timer
 src,clear,head,count,table,lh,ch=timer.DETAILS[index];lr=init.binding.take(data,src,30);cl=init.binding.take(data,clear,68)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];fs=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(fs+0x20000314-dest==src and dest<=0x20000314 and 0x20000314+30<=end and sparse.captured(mem,src,30)==lr and sha256(lr).hexdigest()==lh,'workerleaves lookupfullfirstcopy/HEX/identity')
 check(sparse.captured(mem,clear,68)==cl and sha256(cl).hexdigest()==ch,'workerleaves clearfullHEX/identity')
 check(bs['group']['calls'][0]['target']==0x20000314 and bs['group']['calls'][1]['target']==clear,'workerleaves groupedtimer exactlookup/clear')
 import check_v4160_registration_return_chain_static as arithmetic
 ap=0x6df1a+496*index;ar=init.binding.take(data,ap,914);check(sparse.captured(mem,ap,914)==ar,'workerleaves arithmeticfullHEX');ab=arithmetic.arithmetic(ar,ap)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_worker=dict(start=wp,bytes=832,sha256=wb['sha256']),reused_B120=dict(start=bp,bytes=1000,sha256=bb['sha256']),reused_timer=dict(lookup_source=src,lookup_target=0x20000314,lookup_bytes=30,lookup_sha256=lh,clear_target=clear,clear_bytes=68,clear_sha256=ch),reused_arithmetic=dict(start=ap,bytes=914,sha256=ab['sha256'],new_domains_quotient_proved=False),
  contracts=['pop reads5freshbytes order1/2/4/0/3,heldLE32 plusbyte4&31,counts32+8positions ->popcountlow37,range0..37 no stores/frame/calls. WorkerP301 andB120N129 low8writer losesnobits undermatchingbody/preservation,notuniversalfieldinvariant orpositivecount',
   'configindependentlanes min(P470,P474)->P486 usingfreshP326;min(P466,P478)->P482 usingfreshP327. mode2 floor2704;otherwise value>2120 freshP256bit11clear caps2120. Changedfield writesP124=1,unchanged neverlocallyclearsit. child55dea/55f2a(P) thenforced0;postchildvalues/retention unknown',
   'group gate low8(I-16)<=31,notfullI;arena+low32(12I) occupantnonnull;taskfullI>>4 andmask1<<(I&15). WorkerU8P40 restrictsactualI16..47/task1..2,notgenerichelper. Guardfail2,lookupnull0 no rewrite',
   'groupnonnullL pointervalue heldacrossclear,clock,arithmetic requests beforeL8 store:capturedV timesfreshU16K+800 pair dividedby1600 request,replyopaque;addheldclock,onesubtractfreshperiod whencarryor>=. No proofL alive,lookupstatus/effect,physicaltiming/modnormalization. Controlword restoresnormalpaths',
   'collision count<=1returnsentryP withoutPdataaccess;elsehelper(K*(U16P482+U16P486+625),div1000000) replyD heldA0,thenbyteP85minus1 unsignedbound. b0->ffffffff,b1/2 skipscan,innerlinkedlist nofinitebound',
   'collision candidatei start1,deadline=low32(freshP144+40i),restartcapturedhead eachattempt,skipself. metricstartsffffffff oncepercandidate,equalP140 replacesitbyunsignedabsdifference;unequalP140 carriespreviousmetric whichalready>=D. metric<D rejects incrementsi. Nullend storeslow16i P86. Otherreturnsdo notlocallywriteP86;returnisopaqueD notcandidate/status',
   'nestedconfig/collisionrequirelocalPextent488 vsworkerlocal402,notactualallocationorwholechainextentproof. actualbinding/fieldpreservation/heap/nodeownership/listfiniteness/ambientpointervisibility/fullasynclifetimes remain'],
  actual_installedbinding_output_persistence_timer_or_registry_progress_pointer_nonretention_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-worker-popcount-config-group-collision-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=1340,complete_phase_body_instructions=458,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['configcallee55dea/55f2a andothernestedsubmit helpers','group post-clear/clock/arithmetic L lifetime,actualclock/arena/recordbindings','5d006/5d14e,fieldwriters/countpositivity andfullobjectconsumption/releaseorder'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('workerleaves instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('workerleaves typedmutation escaped')
    typed+=1
 check((mutated,typed)==(458,46),'workerleaves mutationcensus')
 print('PASS:458 instruction/46 typed-load mutations rejected;popcount/clamp/group/collision completecontracts')


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
 else:check(OUT.read_bytes()==encoded,'workerleaves exactledger replay')
 print('PASS:1340B/458i complete workerleaves;strictHEX;P301/N129/field/heldnode joins;exactledger')
 print('PASS:NO target execution/emulation;provider/fieldstability/ownership/full lifetimes UNPROVED')


if __name__=='__main__':main()
