"""Offline complete inner block I/O provider and command13 composition.
Original bytes/operands/CFG and host scalar/interval certificates only.
No target execution/emulation, hardware/crypto/provider/RAM state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_worker_static as previous
import check_v4160_rf_tail_return_static as rf
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,BRANCHES=previous.common,previous.BRANCHES
FIELDS={**previous.FIELDS,'nop':()}
OUT=Path(__file__).with_name('v4160-b1-inner-static.json')
STARTS=(0x200022be,0x2000230a)
SOURCES=(0x4252e,0x425ba)
SIZE=360
HASHES=('0c64a96bcd53534dfb7d1727d8995ccef3add0a2095304f67329aa6480281f3a', '3e705fa75087c6efb627aad518e863c3f9917bad0936d65a3e503643f435886b')
COUNTS=(158, 158)
QK=(((18, '1831', 'qk.c.lbu'), (46, '5831', 'qk.c.lbu'), (74, '1835', 'qk.c.lbu'), (102, '5835', 'qk.c.lbu'), (118, '6835', 'qk.c.lbu'), (128, '9831', 'qk.c.lbu'), (130, 'a821', 'qk.c.lbu'), (138, '8821', 'qk.c.lbu'), (142, 'a831', 'qk.c.lbu'), (150, 'd831', 'qk.c.lbu'), (152, 'e821', 'qk.c.lbu'), (160, 'c821', 'qk.c.lbu'), (164, 'e831', 'qk.c.lbu'), (172, '9835', 'qk.c.lbu'), (174, 'a825', 'qk.c.lbu'), (182, '8825', 'qk.c.lbu'), (186, 'a835', 'qk.c.lbu'), (194, 'd835', 'qk.c.lbu'), (196, 'e825', 'qk.c.lbu'), (204, 'c825', 'qk.c.lbu'), (206, 'ec35', 'qk.c.lbu'), (252, '1ca2', 'qk.c.sb'), (262, '1cb2', 'qk.c.sb'), (272, '3ca2', 'qk.c.sb'), (282, '3cb2', 'qk.c.sb'), (290, '58a2', 'qk.c.sb'), (296, '58b2', 'qk.c.sb'), (302, '78a2', 'qk.c.sb'), (308, '78b2', 'qk.c.sb'), (312, '18a6', 'qk.c.sb'), (318, '18b6', 'qk.c.sb'), (324, '38a6', 'qk.c.sb'), (330, '38b6', 'qk.c.sb'), (334, '58a6', 'qk.c.sb'), (340, '58b6', 'qk.c.sb'), (346, '78a6', 'qk.c.sb'), (352, '7cb6', 'qk.c.sb')), ((18, '1831', 'qk.c.lbu'), (46, '5831', 'qk.c.lbu'), (74, '1835', 'qk.c.lbu'), (102, '5835', 'qk.c.lbu'), (118, '6835', 'qk.c.lbu'), (128, '9831', 'qk.c.lbu'), (130, 'a821', 'qk.c.lbu'), (138, '8821', 'qk.c.lbu'), (142, 'a831', 'qk.c.lbu'), (150, 'd831', 'qk.c.lbu'), (152, 'e821', 'qk.c.lbu'), (160, 'c821', 'qk.c.lbu'), (164, 'e831', 'qk.c.lbu'), (172, '9835', 'qk.c.lbu'), (174, 'a825', 'qk.c.lbu'), (182, '8825', 'qk.c.lbu'), (186, 'a835', 'qk.c.lbu'), (194, 'd835', 'qk.c.lbu'), (196, 'e825', 'qk.c.lbu'), (204, 'c825', 'qk.c.lbu'), (206, 'ec35', 'qk.c.lbu'), (252, '1ca2', 'qk.c.sb'), (262, '1cb2', 'qk.c.sb'), (272, '3ca2', 'qk.c.sb'), (282, '3cb2', 'qk.c.sb'), (290, '58a2', 'qk.c.sb'), (296, '58b2', 'qk.c.sb'), (302, '78a2', 'qk.c.sb'), (308, '78b2', 'qk.c.sb'), (312, '18a6', 'qk.c.sb'), (318, '18b6', 'qk.c.sb'), (324, '38a6', 'qk.c.sb'), (330, '38b6', 'qk.c.sb'), (334, '58a6', 'qk.c.sb'), (340, '58b6', 'qk.c.sb'), (346, '78a6', 'qk.c.sb'), (352, '7cb6', 'qk.c.sb')))
TYPED=(((4, 2), (20, 4), (30, 4), (36, 4), (48, 4), (58, 4), (64, 4), (76, 4), (86, 4), (92, 4), (104, 4), (114, 4), (238, 2), (254, 2), (264, 2), (274, 2), (284, 2)), ((4, 2), (20, 4), (30, 4), (36, 4), (48, 4), (58, 4), (64, 4), (76, 4), (86, 4), (92, 4), (104, 4), (114, 4), (238, 2), (254, 2), (264, 2), (274, 2), (284, 2)))
LITERALS=(
'''
000 lui 13 536883200
004 load 15 13 1284 4
008 addi 14 0 256
00c store 15 14 0 4
00e store 15 0 0 4
012 load 14 10 1 1
014 load 16 10 2 1
018 slli 14 14 8
01a slli 16 16 16
01c add 14 14 16
01e load 16 10 0 1
022 add 14 14 16
024 load 16 10 3 1
028 slli 16 16 24
02a add 14 14 16
02c store 15 14 40 4
02e load 14 10 5 1
030 load 16 10 6 1
034 slli 14 14 8
036 slli 16 16 16
038 add 14 14 16
03a load 16 10 4 1
03e add 14 14 16
040 load 16 10 7 1
044 slli 16 16 24
046 add 14 14 16
048 store 15 14 44 4
04a load 14 10 9 1
04c load 16 10 10 1
050 slli 14 14 8
052 slli 16 16 16
054 add 14 14 16
056 load 16 10 8 1
05a add 14 14 16
05c load 16 10 11 1
060 slli 16 16 24
062 add 14 14 16
064 store 15 14 48 4
066 load 14 10 13 1
068 load 16 10 14 1
06c slli 14 14 8
06e slli 16 16 16
070 add 14 14 16
072 load 16 10 12 1
076 load 10 10 15 1
078 add 14 14 16
07a slli 10 10 24
07c add 14 14 10
07e store 15 14 52 4
080 load 14 11 1 1
082 load 10 11 2 1
084 slli 14 14 8
086 slli 10 10 16
088 add 14 14 10
08a load 10 11 0 1
08c add 14 14 10
08e load 10 11 3 1
090 slli 10 10 24
092 add 14 14 10
094 store 15 14 24 4
096 load 14 11 5 1
098 load 10 11 6 1
09a slli 14 14 8
09c slli 10 10 16
09e add 14 14 10
0a0 load 10 11 4 1
0a2 add 14 14 10
0a4 load 10 11 7 1
0a6 slli 10 10 24
0a8 add 14 14 10
0aa store 15 14 28 4
0ac load 14 11 9 1
0ae load 10 11 10 1
0b0 slli 14 14 8
0b2 slli 10 10 16
0b4 add 14 14 10
0b6 load 10 11 8 1
0b8 add 14 14 10
0ba load 10 11 11 1
0bc slli 10 10 24
0be add 14 14 10
0c0 store 15 14 32 4
0c2 load 14 11 13 1
0c4 load 10 11 14 1
0c6 slli 14 14 8
0c8 slli 10 10 16
0ca add 14 14 10
0cc load 10 11 12 1
0ce load 11 11 15 1
0d0 add 14 14 10
0d2 slli 11 11 24
0d4 add 14 14 11
0d6 store 15 14 36 4
0d8 load 14 15 4 4
0da andi 14 14 -3
0dc store 15 14 4 4
0de load 14 15 4 4
0e0 ori 14 14 1
0e4 store 15 14 4 4
0e6 load 14 15 0 4
0e8 ori 14 14 1
0ec store 15 14 0 4
0ee load 14 13 1284 4
0f2 load 15 14 4 4
0f4 andi 15 15 1
0f6 bnez 15 356
0f8 load 15 14 24 4
0fa li 10 0
0fc store 12 15 0 1
0fe load 15 13 1284 4
102 load 15 15 24 4
104 srli 15 15 8
106 store 12 15 1 1
108 load 15 13 1284 4
10c load 15 15 24 4
10e srli 15 15 16
110 store 12 15 2 1
112 load 15 13 1284 4
116 load 15 15 24 4
118 srli 15 15 24
11a store 12 15 3 1
11c load 15 13 1284 4
120 load 14 15 28 4
122 store 12 14 4 1
124 load 14 15 28 4
126 srli 14 14 8
128 store 12 14 5 1
12a load 14 15 28 4
12c srli 14 14 16
12e store 12 14 6 1
130 load 14 15 28 4
132 srli 14 14 24
134 store 12 14 7 1
136 load 14 15 32 4
138 store 12 14 8 1
13a load 14 15 32 4
13c srli 14 14 8
13e store 12 14 9 1
140 load 14 15 32 4
142 srli 14 14 16
144 store 12 14 10 1
146 load 14 15 32 4
148 srli 14 14 24
14a store 12 14 11 1
14c load 14 15 36 4
14e store 12 14 12 1
150 load 14 15 36 4
152 srli 14 14 8
154 store 12 14 13 1
156 load 14 15 36 4
158 srli 14 14 16
15a store 12 14 14 1
15c load 15 15 36 4
15e srli 15 15 24
160 store 12 15 15 1
162 jr 1
164 nop 
166 jump 238
''',
'''
000 lui 13 536883200
004 load 15 13 1364 4
008 addi 14 0 256
00c store 15 14 0 4
00e store 15 0 0 4
012 load 14 10 1 1
014 load 16 10 2 1
018 slli 14 14 8
01a slli 16 16 16
01c add 14 14 16
01e load 16 10 0 1
022 add 14 14 16
024 load 16 10 3 1
028 slli 16 16 24
02a add 14 14 16
02c store 15 14 40 4
02e load 14 10 5 1
030 load 16 10 6 1
034 slli 14 14 8
036 slli 16 16 16
038 add 14 14 16
03a load 16 10 4 1
03e add 14 14 16
040 load 16 10 7 1
044 slli 16 16 24
046 add 14 14 16
048 store 15 14 44 4
04a load 14 10 9 1
04c load 16 10 10 1
050 slli 14 14 8
052 slli 16 16 16
054 add 14 14 16
056 load 16 10 8 1
05a add 14 14 16
05c load 16 10 11 1
060 slli 16 16 24
062 add 14 14 16
064 store 15 14 48 4
066 load 14 10 13 1
068 load 16 10 14 1
06c slli 14 14 8
06e slli 16 16 16
070 add 14 14 16
072 load 16 10 12 1
076 load 10 10 15 1
078 add 14 14 16
07a slli 10 10 24
07c add 14 14 10
07e store 15 14 52 4
080 load 14 11 1 1
082 load 10 11 2 1
084 slli 14 14 8
086 slli 10 10 16
088 add 14 14 10
08a load 10 11 0 1
08c add 14 14 10
08e load 10 11 3 1
090 slli 10 10 24
092 add 14 14 10
094 store 15 14 24 4
096 load 14 11 5 1
098 load 10 11 6 1
09a slli 14 14 8
09c slli 10 10 16
09e add 14 14 10
0a0 load 10 11 4 1
0a2 add 14 14 10
0a4 load 10 11 7 1
0a6 slli 10 10 24
0a8 add 14 14 10
0aa store 15 14 28 4
0ac load 14 11 9 1
0ae load 10 11 10 1
0b0 slli 14 14 8
0b2 slli 10 10 16
0b4 add 14 14 10
0b6 load 10 11 8 1
0b8 add 14 14 10
0ba load 10 11 11 1
0bc slli 10 10 24
0be add 14 14 10
0c0 store 15 14 32 4
0c2 load 14 11 13 1
0c4 load 10 11 14 1
0c6 slli 14 14 8
0c8 slli 10 10 16
0ca add 14 14 10
0cc load 10 11 12 1
0ce load 11 11 15 1
0d0 add 14 14 10
0d2 slli 11 11 24
0d4 add 14 14 11
0d6 store 15 14 36 4
0d8 load 14 15 4 4
0da andi 14 14 -3
0dc store 15 14 4 4
0de load 14 15 4 4
0e0 ori 14 14 1
0e4 store 15 14 4 4
0e6 load 14 15 0 4
0e8 ori 14 14 1
0ec store 15 14 0 4
0ee load 14 13 1364 4
0f2 load 15 14 4 4
0f4 andi 15 15 1
0f6 bnez 15 356
0f8 load 15 14 24 4
0fa li 10 0
0fc store 12 15 0 1
0fe load 15 13 1364 4
102 load 15 15 24 4
104 srli 15 15 8
106 store 12 15 1 1
108 load 15 13 1364 4
10c load 15 15 24 4
10e srli 15 15 16
110 store 12 15 2 1
112 load 15 13 1364 4
116 load 15 15 24 4
118 srli 15 15 24
11a store 12 15 3 1
11c load 15 13 1364 4
120 load 14 15 28 4
122 store 12 14 4 1
124 load 14 15 28 4
126 srli 14 14 8
128 store 12 14 5 1
12a load 14 15 28 4
12c srli 14 14 16
12e store 12 14 6 1
130 load 14 15 28 4
132 srli 14 14 24
134 store 12 14 7 1
136 load 14 15 32 4
138 store 12 14 8 1
13a load 14 15 32 4
13c srli 14 14 8
13e store 12 14 9 1
140 load 14 15 32 4
142 srli 14 14 16
144 store 12 14 10 1
146 load 14 15 32 4
148 srli 14 14 24
14a store 12 14 11 1
14c load 14 15 36 4
14e store 12 14 12 1
150 load 14 15 36 4
152 srli 14 14 8
154 store 12 14 13 1
156 load 14 15 36 4
158 srli 14 14 16
15a store 12 14 14 1
15c load 15 15 36 4
15e srli 15 15 24
160 store 12 15 15 1
162 jr 1
164 nop 
166 jump 238
''',
)

OUTPUT_STORES=(0xfc,0x106,0x110,0x11a,0x122,0x128,0x12e,0x134,0x138,0x13e,0x144,0x14a,0x14e,0x154,0x15a,0x160)
OUTPUT_READS=(0xf8,0x102,0x10c,0x116,0x120,0x124,0x12a,0x130,0x136,0x13a,0x140,0x146,0x14c,0x150,0x156,0x15c)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1inner literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1inner typedload encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'B1inner completeboundaries')
 for a,f in s.items():init.g(n,a,'B1inner operand '+hex(a-pc),**f)
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1inner Xwchc bytes/width')
 check(raw[0x164:0x166]==bytes.fromhex('0100') and n[pc+0x164]['op']=='nop','B1inner exact retained wait-hint encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'B1inner fullidentity')
 e={};rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1inner RET RA');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  else:check(op not in ('jal','jalr','call_indirect'),'B1inner no calls')
  check(all(z in n for z in q),'B1inner closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and rets==[pc+0x162],'B1inner all localnodes/RET')
 cut={a:[z for z in qs if (a-pc,z-pc)!=(0x166,0xee)] for a,qs in e.items()}
 check(not common.acyclic(e) and common.acyclic(cut),'B1inner exactpollbackedge')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 words=[d for d in stores if d['bytes']==4]
 expected=[(0xc,14,0),(0xe,0,0),(0x2c,14,40),(0x48,14,44),(0x64,14,48),(0x7e,14,52),(0x94,14,24),(0xaa,14,28),(0xc0,14,32),(0xd6,14,36),(0xdc,14,4),(0xe4,14,4),(0xec,14,0)]
 check(words==[dict(offset=o,base=15,source=r,imm=x,bytes=4) for o,r,x in expected],'B1inner all13wordstores throughinitialP')
 bytesout=[d for d in stores if d['bytes']==1]
 check(bytesout==[dict(offset=o,base=12,source=15 if j<4 or j==15 else 14,imm=j,bytes=1) for j,o in enumerate(OUTPUT_STORES)] and len(stores)==29,'B1inner all16 ascending outputstores/29total')
 check(len([d for d in n.values() if d['op']=='load'])==58 and {d['rd'] for d in n.values() if 'rd' in d}=={10,11,13,14,15,16},'B1inner load/definedGPR census;O/S/SP/RA preserved locally')
 check([a-pc for a,d in n.items() if d.get('rd')==13]==[0] and n[pc+0xfa]['op']=='li' and n[pc+0xfa]['imm']==0 and max(a-pc for a,d in n.items() if d.get('rd')==10)==0xfa,'B1inner globalbase heldA3 andnormalreply0 beforeoutputs')
 return dict(start=pc,source=SOURCES[index],bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=[],tails=[],returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def provider_paths(b):
 done=common.walk(b,{0xf6:0xf8});j=done.index(0xf6)
 loop=[0x164,0x166,0xee,0xf2,0xf4,0xf6]
 out={'first_sample_bit0_clear':done}
 for count in (1,2):
  seq=done[:j+1]+loop*count+done[j+1:];pc=b['start'];e=b['CFG']
  check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1inner immutable repeatedpoll witness')
  check(seq.count(0xee)==count+1 and seq.count(0xfc)==1,'B1inner freshpointer eachpoll/oneoutput path');out[str(count)+'_set_samples_then_clear']=seq
 check(not(set(loop)&(set(OUTPUT_READS)|set(OUTPUT_STORES))),'B1inner waitloop cannotoutput untilexit')
 return out


def old_body(data,hexmem,role,index):
 pc=rf.DETAILS[index][0][rf.ROLES.index(role)];z=rf.SIZES[rf.ROLES.index(role)];raw=init.binding.take(data,pc,z)
 check(sparse.captured(hexmem,pc,z)==raw,'B1inner reusedRF/reset completeoriginalHEX')
 old=rf.body(raw,role,index)
 return dict(start=pc,source=pc,bytes=z,sha256=sha256(raw).hexdigest(),instructions=old['instructions'],CFG=rf.edge_map(old),calls=old['calls'],tails=[],returns=[int(old['local_RET'],16)],
  complete_local_body=True,new_code_bytes_counted=0,target_execution_or_emulation=False)


def command_paths(b):
 # All choices below retain saved command13 and omit dedicated command6/7 arms.
 base={0x26:0x28,0x50:0x90,0x92:0xa4}
 endings={'fresh_state6_latch':{0xa6:0xb8,0xba:0xbc},'fresh_state7_latch':{0xa6:0xaa,0xac:0xb8,0xba:0xbc},
  'fresh_state8_latch':{0xa6:0xaa,0xac:0xb0,0xb4:0xb8,0xba:0xbc},'matched_state_latch_already_nonzero':{0xa6:0xb8,0xba:0x70},
  'three_fresh_state_misses':{0xa6:0xaa,0xac:0xb0,0xb4:0x70}}
 out={'low2_zero_skips_callback_reset':common.walk(b,{0x26:0x7c})}
 for cb,target in [('callback',0x3e),('no_callback',0x4e)]:
  for name,choices in endings.items():out[cb+'_'+name]=common.walk(b,{**base,0x3a:target,**choices})
 for name,seq in out.items():
  check(0x54 not in seq and 0x96 not in seq and seq[-1]==0x8e and 0x84 in seq,'B1inner command13 excludescommand6/7arms;allnormalpaths restorecapturedcontrol')
  if name!='low2_zero_skips_callback_reset':check(0x74 in seq and 0x78 in seq,'B1inner nonzero-low2 selectedpaths clearflag/callreset')
  check((0x4c in seq)==name.startswith('callback_'),'B1inner onlyinitialstate3 admitscallback17')
  check((0xbe in seq)==name.endswith('_latch') and (0xc2 in seq)==name.endswith('_latch'),'B1inner latchstoresselected together')
 return out


def domains():
 pairs=0
 for lo in range(256):
  for hi in range(256):
   check((lo+(hi<<8))==(lo|(hi<<8)) and (lo+(hi<<8))<65536,'B1inner disjointbyte addition no carry');pairs+=1
 for shift in (0,8,16,24):
  for value in range(256):check(((value<<shift)>>shift)&255==value and value<<shift<=0xffffffff,'B1inner lane placement/extraction')
 for a in range(4):
  for b in range(a+1,4):check((255<<(8*a))&(255<<(8*b))==0,'B1inner fourlane disjointmasks')
 for value in (0,1,255,256,0x01020304,0x7fffffff,0x80000000,0xffffffff):
  check(sum(((value>>(8*k))&255)<<(8*k) for k in range(4))==value,'B1inner littleendian scalar reconstruction samples')
 for value in range(256):
  check((value&1)!=0 if value%2 else (value&1)==0,'B1inner pollbit algebra')
  check((value&3) in range(4) and ((value&0xfd)&2)==0 and (value|1)&1==1,'B1inner low2/clear1/set0 scalars')
 check(13!=6 and 13!=7 and 0x40024000+768==0x40024300 and 0x40024000+512==0x40024200,'B1inner command13/sourcepublications')
 for j in range(3):check(45+(2-j)-32==15-j and 15-j in (13,14,15),'B1inner reverseoutput joinsprovider13..15')
 check(set(range(16)).isdisjoint(set(range(16,32))) and set(range(16,32)).isdisjoint(set(range(32,48))),'B1inner worker twoinputs/output disjointrelativeintervals')
 return dict(byte_addition_pairs=pairs,lane_values=1024,packing='four disjoint U8 lanes b0+(b1<<8)+(b2<<16)+(b3<<24);fresh byte observations;not hardwarealgorithm',
  input_blocks=[[0,16],[16,32]],output_block=[32,48],pollbit_U8_cases=256,
  output_observations=16,output_snapshot_coherence_proved=False,worker_output_index_order=[15,14,13],
  command13='initiallow2zero short-circuits;otherwise state3callback17 possible;laterfresh6/7/8+latch decisions independent',
  target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,SOURCES[index],SIZE)
 check(sparse.captured(mem,SOURCES[index],SIZE)==raw,'B1inner fullprovider originalHEX');b=body(raw,index);n={d['pc']-pc:d for d in b['instructions']}
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy']
 check(int(f['source'],16)+pc-int(f['destination'],16)==SOURCES[index] and pc+SIZE<=int(mapping['first_copy_end_exclusive'],16),'B1inner complete firstcopyprovider mapping')
 slot=0x20003504+80*index;check(n[0]['imm']+n[4]['imm']==slot,'B1inner dynamicpointer slot')
 check([(o,d['rd']) for o,d in n.items() if d['op']=='load' and d['rs1']==13]==[(4,15),(0xee,14),(0xfe,15),(0x108,15),(0x112,15),(0x11c,15)],'B1inner exact pointerreload schedule')
 inputgroups=[]
 for reg,base,offsets in [(10,40,(0x2c,0x48,0x64,0x7e)),(11,24,(0x94,0xaa,0xc0,0xd6))]:
  loads=[(o,d) for o,d in n.items() if d['op']=='load' and d['rs1']==reg and d['width']==1]
  check(len(loads)==16 and [d['imm'] for _,d in loads]==[4*j+k for j in range(4) for k in (1,2,0,3)],'B1inner input freshbyte order')
  for j,store in enumerate(offsets):check(n[store]['imm']==base+4*j and n[store]['rs1']==15,'B1inner packed input word destinations')
  inputgroups.append(dict(original_argument='A0' if reg==10 else 'A1',fresh_byte_offsets=[d['imm'] for _,d in loads],word_offsets=[base+4*j for j in range(4)]))
 check(n[8]['imm']==256 and n[0xda]['imm']==-3 and n[0xe0]['imm']==n[0xe8]['imm']==1 and n[0xf4]['imm']==1 and n[0xf6]['op']=='bnez','B1inner orderedcontrols/pollmask')
 observations=[]
 for j,(load,store) in enumerate(zip(OUTPUT_READS,OUTPUT_STORES)):
  d=n[load];check(d['op']=='load' and d['width']==4 and d['imm']==24+4*(j//4) and n[store]['imm']==j,'B1inner onefreshword peroutputbyte')
  if j%4:check(n[store-2]['op']=='srli' and n[store-2]['imm']==8*(j%4),'B1inner byte extraction shift')
  observations.append(dict(output_byte=j,word_read_offset=load,pointer_observation='successfulpoll' if j==0 else 'freshslot_for_byte'+str(j) if j<4 else 'freshslot_for_byte4_heldthrough15',dynamic_word_offset=d['imm'],shift=8*(j%4),store_offset=store))
 check([o for o,d in n.items() if o>=0x11c and d.get('rd')==15]==[0x11c,0x15c,0x15e],'B1inner finalpointer heldthroughoutput4..15')
 check(parent['bodies']['core']['calls'][1]['target']==pc and parent['bodies']['worker']['calls'][4]['target']==parent['bodies']['core']['start'],'B1inner actualcore/worker providerjoin')
 command=old_body(data,mem,'rf',index);reset=old_body(data,mem,'reset',index)
 cn={d['pc']-command['start']:d for d in command['instructions']};rn={d['pc']-reset['start']:d for d in reset['instructions']}
 check([o for o,d in cn.items() if d.get('rd')==9]==[0x34,0x88] and cn[0x4e]['imm']==6 and cn[0x90]['imm']==7,'B1inner savedcommand13 across callback/reset')
 check(cn[0x42]['imm']+0x20003000==0x20003550+80*index and cn[0x46]['imm']==0 and cn[0x48]['imm']==0 and cn[0x4a]['imm']==17,'B1inner callback freshslot/explicit17,0,0')
 check(not any(d.get('rd')==10 for d in reset['instructions']) and cn[0x84]['rs2']==18 and cn[0x84]['imm']==524,'B1inner reset noA0definitions/controlrestore source')
 resets={str(bit3)+'_'+str(descriptor):common.walk(reset,{0x1c:0x1e if bit3 else 0x26,0x5e:0x60 if descriptor else 0x74}) for bit3 in (0,1) for descriptor in (0,1)}
 for name,seq in resets.items():check((0x68 in seq)==name.endswith('_1') and (0x72 in seq)==name.endswith('_1'),'B1inner descriptor gates both dynamic ORstores')
 pub=rf.previous;pubpc=pub.DETAILS[index][0][0];pubraw=init.binding.take(data,pubpc,pub.SIZES[0])
 check(sparse.captured(mem,pubpc,pub.SIZES[0])==pubraw,'B1inner reusedpublication completeoriginalHEX');published=pub.body(pubraw,'parent',index)
 pn={d['pc']-pubpc:d for d in published['instructions']}
 check(pn[16]['imm']+pn[20]['imm']==0x40024300 and pn[24]['imm']+pn[28]['imm']==slot and pn[28]['rs2']==13,'B1inner exactsource40024300 publication')
 check(pn[16]['imm']+pn[32]['imm']==0x40024200 and pn[36]['imm']+pn[40]['imm']==0x2000353c+80*index,'B1inner exactRFcontext publication')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificate=common.certificates(b),paths=provider_paths(b),input_byte_groups=inputgroups,output_observations=observations,
  reused_command=command,reused_reset=reset,command13_paths=command_paths(command),reset_paths=resets,
  reused_pointer_publication=dict(start=pubpc,bytes=len(pubraw),sha256=sha256(pubraw).hexdigest(),provider_slot=slot,provider_pointer=0x40024300,RF_slot=0x2000353c+80*index,RF_pointer=0x40024200,new_code_bytes_counted=0,publication_preserved_at_B1_call_proved=False),
  provider_contract=['no calls/frame/null/lengthguard;initialP=freshU32slot20003504/20003554;SW100 thenSW0 atP0;freshA0bytes16 packtoP40..52,thenfreshA1bytes16 packtoP24..36',
   'three independent RMW samples:clearbit1 P4,thenOR1 P4,thenOR1 P0;no hardwarecompletion inferredfromthewrites',
   'eachpoll freshpointervia globalslot,readfreshword+4;bit0set->retainedhint/jump,retry;clear->output.No timeout/counter/progress proof;pointermaychangebetweenreads',
   'output16ascendingSBs from16 independent freshwordreads offsets24,28,32,36. Byte0 useslastpollpointer;bytes1,2,3 eachreloadpointer;byte4 reloadcapturedpointerheldthroughbyte15',
   'localA0=0 beforefirstoutputstore,nolaterA0def;normalRET afterall16stores;noactualphysicalresult/coherentsnapshot proof'],
  command13_contract=['reusedcompleteRF198B/reset130B;state1 premise frominitializer notinheritedbyB1. Low2zero restorescapturedcontrol snapshot andreturnswithoutcallback/reset',
   'low2nonzero savescommand13;initialfreshstate7==3 invokesfreshslot20003550/200035a0(17,0,0) withoutnullguard;replyignoredbyoutercore butRFscalarcanreflectcallback',
   'saved13 excludescommand6/7arms;three laterfreshstate7 samples test6,7,8 insequence. Match->freshlatch9==0 ->storeanotherfreshstate7 tofield8,setfield9=1;matchedbyte neednotequallatchedbyte',
   'allselectednonzero-low2 paths clearflag20002efc/20002f4c,callresetthenrestorecaptured4002420c word. Resetdescriptor nonnull mayperformtwo dynamicORstores;resetdoesnotdefineA0',
   'firstcallback andreset mayhaveeffects;separatefreshsamples/controlwrites do notprovehardware restoration,ABI preservation,outputvalidity ornoescape'],
  composition=['core originaltriple(W,W16,W32) passedtoRAMprovider aftercommand13returns;provider normalreturnwritesW32..47 under valid extents,not a hardwarealgorithm/outputvalueproof',
   'worker reverse outputW45..47 ->callerSP12/13/14 receivesprovider bytes15/14/13,which originate fromthree distinctfreshword+36 observations atfinalheldpointer',
   'initializer encodes40024300/40024200 pointerpublications;laterwriters/timing/physicalmapping/actualinstalledRAMcopy notproved. Do not substitute sourcepublicationforactualruntimebinding',
   'allborrowed pointer lifetimes/ABI/framepreservation dependoncallees/alias/IRQ/DMA/reentrypremises;no storedglobaloriginalinput/outputpointer inthisprovider,nottransitive no-retentionproof'],
  premises='conditionalcandidateISA/firstcopymapping/providers;validcode/frame/global/dynamicword/input16+16/output16 extents;ordinarycallreturns/S/SP/RA/framepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalities separate',
  actual_installed_provider_hardware_algorithm_coherent_result_poll_termination_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-inner-provider-command13-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=720,complete_phase_body_instructions=316,reused_command_reset_publication_bytes=892,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['actualpointer/callback writers andfullinitialization ordering','polling progress andphysicalword interface outputsemantics','actualquery/configvalues/reachability andfullborrowedpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1inner instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('B1inner typedmutation escaped')
   typed+=1
 check((mutations,typed)==(316,34),'B1inner mutationcensus');domains()
 print('PASS:316 instruction/34 typed-load mutations rejected;65536 bytepairs;1024 lanevalues;poll/command13/index certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1inner exactledger replay')
 print('PASS:720B/316i complete innerprovider;strict HEX/mapping;16freshoutputs/poll/sourcepublication andcommand13 joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbinding/hardwarealgorithm/coherentoutput/termination/lifetimes UNPROVED')


if __name__=='__main__':main()
