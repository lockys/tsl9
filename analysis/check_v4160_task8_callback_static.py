"""Offline task8 other-callback and immutable dispatch-table contracts.
Original operands, CFG data and host scalar/interval equations only.
No target execution/emulation, callbacks, provider, RAM/heap or hardware model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_task8_aux_static as previous
init,sparse,check=previous.init,previous.sparse,previous.check
common=previous.common
task8=previous.previous
OUT=Path(__file__).with_name('v4160-task8-callback-static.json')
STARTS=(0x4b944,0x4b9dc)
SIZE=438
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
def decode(raw,pc):
 out={};off=0
 while off<len(raw):
  z=2 if int.from_bytes(raw[off:off+2],'little')&3!=3 else 4;chunk=raw[off:off+z];check(len(chunk)==z,'callback complete encoding');w=int.from_bytes(chunk,'little');a=pc+off
  if z==2 and w&0xf863==0x8060:
   d=dict(pc=a,bytes=chunk.hex(),size=2,op='store',rs1=2,rs2=8+((w>>2)&7),imm=((w>>8&7)<<1)+((w>>7&1)<<4),width=2,mnemonic='qk.c.shsp')
  else:d=previous.decode(chunk,a)[a]
  out[a]=d;off+=z
 return out
HASHES=('83706af97ef3445288fb177af660f13990772c3bc0db444611724856b9a4a02d', 'c335066433387ca0532a797525b4c0be7c667400dc96da22c9a29dafc95bb277')
TYPED_LOADS=(((106, 2), (174, 4), (192, 4), (236, 2), (244, 2), (368, 4)), ((106, 2), (174, 4), (192, 4), (236, 2), (244, 2), (368, 4)))
TABLE_STARTS=(0x6e3b0,0x6e5a0)
TABLE_HASHES=('eb442019b836e5bcdd4eeb52e8280c4ab64cf0b37a34e0ff3d3e809f828f7dfa', '3e2c9c8c78c2166aa2e84910d0f285533a04ee62cd682bea7c99a451ecafa566')
TABLE_ROWS=(((282052, 307936), (282102, 311368), (282212, 311322), (282382, 311276), (282524, 313980), (282600, 313980), (282682, 313826), (282382, 311192), (282834, 311968), (0, 0), (282896, 312106), (283000, 308058)), ((282200, 308088), (282250, 311520), (282360, 311474), (282530, 311428), (282672, 314132), (282748, 314132), (282830, 313978), (282530, 311344), (282982, 312120), (0, 0), (283044, 312258), (283148, 308210)))
LITERALS=(
'''
000 addi 2 2 -96
002 store 2 9 84 4
004 store 2 19 76 4
006 store 2 1 92 4
008 store 2 8 88 4
00a store 2 18 80 4
00c store 2 20 72 4
00e store 2 21 68 4
010 store 2 22 64 4
012 store 2 23 60 4
014 mv 9 11
016 load 11 11 2 1
018 li 15 30
01a mv 19 10
01c bne 11 15 106
020 auipc 1 536563712
024 jalr 1 1 184
028 mv 8 10
02a bnez 10 70
02c li 8 0
02e mv 10 8
030 load 1 2 92 4
032 load 8 2 88 4
034 load 9 2 84 4
036 load 18 2 80 4
038 load 19 2 76 4
03a load 20 2 72 4
03c load 21 2 68 4
03e load 22 2 64 4
040 load 23 2 60 4
042 addi 2 2 96
044 jr 1
046 load 15 10 2 1
048 li 14 1
04a addi 15 15 2
04c andi 15 15 255
050 bgeu 14 15 44
054 load 10 10 3 1
056 li 14 0
058 li 13 30
05a li 12 0
05c mv 11 19
05e jal 1 302666
062 mv 10 8
064 jal 1 309388
068 jump 44
06a load 22 9 0 4
06e lui 15 16777216
072 addi 15 15 -256
076 lui 14 1179648
07a and 15 22 15
07e addi 14 14 256
082 mv 21 12
084 li 18 0
086 beq 15 14 188
08a store 2 11 12 4
08c auipc 1 536563712
090 jalr 1 1 76
094 mv 18 10
096 load 11 2 12 4
098 beqz 10 188
09a load 12 10 4 1
09c beqz 12 188
09e slli 15 12 24
0a2 srai 15 15 24
0a4 blt 15 0 44
0a8 mv 10 19
0aa jal 1 302800
0ae load 15 18 4 1
0b2 ori 15 15 -128
0b6 store 18 15 4 1
0ba jump 44
0bc lui 20 536883200
0c0 load 14 20 -274 1
0c4 addi 15 0 255
0c8 addi 20 20 -274
0cc li 8 6
0ce beq 14 15 46
0d2 li 15 24
0d4 bltu 15 11 46
0d8 srli 15 11 1
0dc addi 15 15 -1
0de slli 14 15 3
0e2 lui 15 450560
0e6 addi 15 15 944
0ea add 15 15 14
0ec load 16 15 0 4
0f0 beq 16 0 46
0f4 load 23 15 4 4
0f8 beq 23 0 46
0fc slli 22 22 16
0fe srli 22 22 16
102 beq 22 0 268
106 li 15 18
108 bne 11 15 46
10c load 13 9 4 2
10e load 12 9 8 4
110 load 11 9 1 1
112 load 10 9 0 1
114 addi 14 2 24
116 call_indirect 1 16
118 mv 8 10
11a bnez 10 46
11c addi 11 2 24
11e mv 10 19
120 call_indirect 1 23
122 mv 8 10
124 beqz 10 360
126 load 15 9 1 1
128 bne 15 0 46
12c load 15 9 2 1
12e store 2 10 20 1
132 li 14 14
134 store 2 15 16 1
138 bne 15 14 356
13c load 14 2 24 4
13e load 15 14 1 1
140 load 14 14 0 1
142 slli 15 15 8
144 or 15 15 14
146 addi 11 2 16
148 mv 10 19
14a store 2 15 18 2
14c jal 1 280780
150 beq 10 0 44
154 addi 13 2 16
156 li 12 1
158 li 11 22
15a mv 10 19
15c jal 1 303284
160 mv 8 10
162 jump 46
164 load 15 2 24 2
166 jump 326
168 load 13 9 2 1
16a li 15 4
16c beq 13 15 44
170 load 10 20 0 1
174 addi 14 2 24
176 li 12 0
178 mv 11 19
17a jal 1 302666
17e mv 8 10
180 bne 10 0 46
184 load 11 9 2 1
186 addi 10 2 24
188 jal 1 302540
18c beqz 10 402
18e store 21 0 0 1
192 load 14 9 0 4
194 lui 15 16777216
198 addi 15 15 -256
19c and 14 14 15
19e lui 15 1179648
1a2 addi 15 15 256
1a6 beq 14 15 44
1aa beq 18 0 44
1ae load 15 9 2 1
1b0 store 18 15 4 1
1b4 jump 46
''',
'''
000 addi 2 2 -96
002 store 2 9 84 4
004 store 2 19 76 4
006 store 2 1 92 4
008 store 2 8 88 4
00a store 2 18 80 4
00c store 2 20 72 4
00e store 2 21 68 4
010 store 2 22 64 4
012 store 2 23 60 4
014 mv 9 11
016 load 11 11 2 1
018 li 15 30
01a mv 19 10
01c bne 11 15 106
020 auipc 1 536563712
024 jalr 1 1 32
028 mv 8 10
02a bnez 10 70
02c li 8 0
02e mv 10 8
030 load 1 2 92 4
032 load 8 2 88 4
034 load 9 2 84 4
036 load 18 2 80 4
038 load 19 2 76 4
03a load 20 2 72 4
03c load 21 2 68 4
03e load 22 2 64 4
040 load 23 2 60 4
042 addi 2 2 96
044 jr 1
046 load 15 10 2 1
048 li 14 1
04a addi 15 15 2
04c andi 15 15 255
050 bgeu 14 15 44
054 load 10 10 3 1
056 li 14 0
058 li 13 30
05a li 12 0
05c mv 11 19
05e jal 1 302818
062 mv 10 8
064 jal 1 309540
068 jump 44
06a load 22 9 0 4
06e lui 15 16777216
072 addi 15 15 -256
076 lui 14 1179648
07a and 15 22 15
07e addi 14 14 256
082 mv 21 12
084 li 18 0
086 beq 15 14 188
08a store 2 11 12 4
08c auipc 1 536563712
090 jalr 1 1 -76
094 mv 18 10
096 load 11 2 12 4
098 beqz 10 188
09a load 12 10 4 1
09c beqz 12 188
09e slli 15 12 24
0a2 srai 15 15 24
0a4 blt 15 0 44
0a8 mv 10 19
0aa jal 1 302952
0ae load 15 18 4 1
0b2 ori 15 15 -128
0b6 store 18 15 4 1
0ba jump 44
0bc lui 20 536883200
0c0 load 14 20 -194 1
0c4 addi 15 0 255
0c8 addi 20 20 -194
0cc li 8 6
0ce beq 14 15 46
0d2 li 15 24
0d4 bltu 15 11 46
0d8 srli 15 11 1
0dc addi 15 15 -1
0de slli 14 15 3
0e2 lui 15 450560
0e6 addi 15 15 1440
0ea add 15 15 14
0ec load 16 15 0 4
0f0 beq 16 0 46
0f4 load 23 15 4 4
0f8 beq 23 0 46
0fc slli 22 22 16
0fe srli 22 22 16
102 beq 22 0 268
106 li 15 18
108 bne 11 15 46
10c load 13 9 4 2
10e load 12 9 8 4
110 load 11 9 1 1
112 load 10 9 0 1
114 addi 14 2 24
116 call_indirect 1 16
118 mv 8 10
11a bnez 10 46
11c addi 11 2 24
11e mv 10 19
120 call_indirect 1 23
122 mv 8 10
124 beqz 10 360
126 load 15 9 1 1
128 bne 15 0 46
12c load 15 9 2 1
12e store 2 10 20 1
132 li 14 14
134 store 2 15 16 1
138 bne 15 14 356
13c load 14 2 24 4
13e load 15 14 1 1
140 load 14 14 0 1
142 slli 15 15 8
144 or 15 15 14
146 addi 11 2 16
148 mv 10 19
14a store 2 15 18 2
14c jal 1 280928
150 beq 10 0 44
154 addi 13 2 16
156 li 12 1
158 li 11 22
15a mv 10 19
15c jal 1 303436
160 mv 8 10
162 jump 46
164 load 15 2 24 2
166 jump 326
168 load 13 9 2 1
16a li 15 4
16c beq 13 15 44
170 load 10 20 0 1
174 addi 14 2 24
176 li 12 0
178 mv 11 19
17a jal 1 302818
17e mv 8 10
180 bne 10 0 46
184 load 11 9 2 1
186 addi 10 2 24
188 jal 1 302692
18c beqz 10 402
18e store 21 0 0 1
192 load 14 9 0 4
194 lui 15 16777216
198 addi 15 15 -256
19c and 14 14 15
19e lui 15 1179648
1a2 addi 15 15 256
1a6 beq 14 15 44
1aa beq 18 0 44
1ae load 15 9 2 1
1b0 store 18 15 4 1
1b4 jump 46
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'callback literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for off,f3 in TYPED_LOADS[index]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'callback typed load encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'callback complete instruction boundaries')
 for a,f in s.items():init.g(n,a,'callback operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(438,160,HASHES[index]),'callback complete identity')
 edges={};calls=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'callback ordinary RET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'callback linked direct call');calls.append({'offset':a-pc,'target':d['target']})
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','callback adjacent linked provider pair')
   calls.append({'offset':a-pc,'target':(a-4+u['imm']+d['imm'])&0xfffffffe})
  elif op=='call_indirect':
   check(d['rd']==1 and d['rs1'] in (16,23),'callback linked row pointer');calls.append({'offset':a-pc,'target':'fresh captured X'+str(d['rs1'])+' & ~1','indirect':True})
  check(all(b in n for b in q),'callback closed local CFG');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'callback complete reachable DAG')
 targets=[(0x24,0x20000a1c),(0x5e,0x49e4a+152*index),(0x64,0x4b88c+152*index),(0x90,0x20000a1c),(0xaa,0x49ed0+152*index),
  (0x116,'fresh captured X16 & ~1'),(0x120,'fresh captured X23 & ~1'),(0x14c,0x448cc+148*index),(0x15c,0x4a0b4+152*index),
  (0x17a,0x49e4a+152*index),(0x188,0x49dcc+152*index)]
 check(calls==[dict(offset=o,target=t,**({'indirect':True} if isinstance(t,str) else {})) for o,t in targets],'callback complete call census')
 stores=[{'offset':a-pc,'base':d['rs1'],'source':d['rs2'],'imm':d['imm'],'bytes':d['width']} for a,d in n.items() if d['op']=='store']
 check(len(stores)==16 and returns==[pc+0x44],'callback exact stores and singleRET')
 nonframe=[d for d in stores if d['base']!=2]
 check(nonframe==[dict(offset=0xb6,base=18,source=15,imm=4,bytes=1),dict(offset=0x18e,base=21,source=0,imm=0,bytes=1),dict(offset=0x1b0,base=18,source=15,imm=4,bytes=1)],'callback connection writes and sole borrowed releaseflag clear')
 check(n[pc+0x82]['rs2']==12 and n[pc+0x82]['rd']==21,'callback capture original A2 only on non30 route')
 saves={(d['source'],d['imm']) for d in stores if d['offset']<0x14}
 restores={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and pc+0x30<=d['pc']<=pc+0x40}
 check(saves==restores=={(1,92),(8,88),(9,84),(18,80),(19,76),(20,72),(21,68),(22,64),(23,60)},'callback saved frame layout')
 return {'start':pc,'bytes':438,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':edges,
  'calls':calls,'tails':[],'returns':returns,'stores':stores,'complete_local_body':True,'target_execution_or_emulation':False}


def paths(b):
 # Selections describe immutable CFG edges, not sampled target register states.
 table={0x1c:0x6a,0x86:0x8a,0x98:0xbc,0xce:0xd2,0xd4:0xd8,0xf0:0xf4,0xf8:0xfc,0x102:0x10c}
 decoded={**table,0x11a:0x11c}
 success={**decoded,0x124:0x168,0x16c:0x170}
 selected={
  'opcode30_lookup_null':{0x1c:0x20,0x2a:0x2c},
  'opcode30_helper_reply_ignored':{0x1c:0x20,0x2a:0x46,0x50:0x54},
  'taskFF_fixed6':{0x1c:0x6a,0x86:0xbc,0xce:0x2e},
  'connection_signedbyte_fixed0':{0x1c:0x6a,0x86:0x8a,0x98:0x9a,0x9c:0x9e,0xa4:0x2c},
  'row_decoder_nonzero':{**table,0x11a:0x2e},
  'row_handler_nonzero_flag_nonzero':{**decoded,0x124:0x126,0x128:0x2e},
  'row_handler_nonzero_report_zero':{**decoded,0x124:0x126,0x128:0x12c,0x138:0x164,0x150:0x2c},
  'row_handler_nonzero_report_sender':{**decoded,0x124:0x126,0x128:0x12c,0x138:0x164,0x150:0x154},
  'row_handler_success_opcode4':{**decoded,0x124:0x168,0x16c:0x2c},
  'forward_helper_nonzero':{**success,0x180:0x2e},
  'forward_helper_zero_leaf_zero':{**success,0x180:0x184,0x18c:0x192,0x1a6:0x1aa,0x1aa:0x2c},
  'forward_helper_zero_leaf_nonzero_clear':{**success,0x180:0x184,0x18c:0x18e,0x1a6:0x1aa,0x1aa:0x2c}}
 chosen={k:common.walk(b,v) for k,v in selected.items()}
 allpaths=task8.v34.allocation.previous.dag_paths(b);pc=b['start'];n={v['pc']-pc:v for v in b['instructions']}
 origins={}
 for seq in allpaths:
  before=seq[:seq.index(0x2e)];defs=[o for o in before if n[o].get('rd')==8];check(bool(defs),'callback reply source exists')
  last=defs[-1];origins[last]=origins.get(last,0)+1
  check(last in (0x2c,0xcc,0x118,0x122,0x160,0x17e),'callback exact reply origin frontier')
  if 0x18e in seq:
   check(last in (0x17e,0x2c) and seq.index(0x17a)<seq.index(0x180)<seq.index(0x188)<seq.index(0x18c)<seq.index(0x18e),'callback direct clear requires helper0 andleafnonzero;optional fixed0 epilogue')
   check(seq[seq.index(0x180)+1]==0x184 and seq[seq.index(0x18c)+1]==0x18e,'callback explicit successbranch thenleafbranch')
  if 0x1c in seq and seq[seq.index(0x1c)+1]==0x20:check(last==0x2c and 0x18e not in seq,'callback opcode30 fixed0 noflagclear')
  for lookup in (0x24,0x90):
   if lookup in seq:check(not any(n[o].get('rd')==12 for o in seq[:seq.index(lookup)]),'callback originalA2 still ambient at firstlookup;arity notproved')
 check(0x18e not in chosen['forward_helper_nonzero'] and 0x18e in chosen['forward_helper_zero_leaf_nonzero_clear'],'callback nonzero helper cannot directclear')
 check(0x118 in chosen['row_decoder_nonzero'] and 0x18e not in chosen['row_decoder_nonzero'],'callback rowdecoder nonzero bypasses clear')
 check(0x150 in chosen['row_handler_nonzero_report_zero'] and 0x2c in chosen['row_handler_nonzero_report_zero'],'callback reportzero overwrites nonzero rowreply')
 return {'selected':chosen,'syntactic_DAG_paths':len(allpaths),'reply_origin_offsets':sorted(origins),'reply_origin_path_counts':origins,
  'allpaths_sha256':sha256(json.dumps(allpaths,separators=(',',':')).encode()).hexdigest(),
  'nonzero19_possible_only_from_opaque_reply_origins':[0x118,0x122,0x160,0x17e],
  'normalreturn_preservation_and_noadversealias_required':True,'actual_path_feasibility_lifetime_or_ownership_proved':False}


def domains():
 mask=0x14300001;odd=[];other=[];reports=[]
 for op in range(64):
  special=(op<=28 and bool(mask>>op&1)) or ((op-31)&255)<=32
  if special:reports.append(op)
  elif op&1:odd.append(op)
  else:other.append(op)
 check(other==[2,4,6,8,10,12,14,16,18,22,24,30],'callback full parent low6 classification')
 rows=[]
 for op in other:
  if op==30:continue
  k=(op>>1)-1;check(0<=k<12 and 8*k+8<=96,'callback actualcaller table extent')
  check(op!=20,'callback null row20 not passed by unchangedparenttuple');rows.append([op,k])
 check(len(rows)==11 and len(odd)==14 and len(reports)==38,'callback caller domain census')
 for op in (0,1):check((((op>>1)-1)&0xffffffff)<<3&0xffffffff==0xfffffff8,'callback generic lowerbound absent beforetableload')
 for byte in range(256):check((((byte+2)&255)<=1)==(byte in (254,255)),'callback opcode30 connectionbyte gate')
 check(8*11+8==96,'callback complete data table interval')
 check(set(range(16,21))&set(range(60,96))==set() and set(range(24,48))&set(range(60,96))==set(),'callback report/output frame avoids saved slots only under24Boutputextent')
 return {'parent_opcode_cases':64,'other_callback_opcodes':other,'odd_callback_opcodes':odd,'report_mask_opcodes':reports,
  'table_opcode_index_pairs':rows,'generic0_1_table_displacement_mod32':0xfffffff8,'connection_byte_cases':256,
  'borrowed_frame':{'report_written_bytes':[16,18,19,20],'report_bytes17_21_22_23_not_written_here':True,'output_pointer_offset':24,'saved_slots':[60,95]},
  'actual_callee_output_extent_or_table_pointer_atomicity_proved':False}


def table_body(data,index):
 pc=TABLE_STARTS[index];raw=init.binding.take(data,pc,96)
 check(sha256(raw).hexdigest()==TABLE_HASHES[index],'callback table identity')
 rows=tuple(tuple(int.from_bytes(raw[o+j:o+j+4],'little') for j in (0,4)) for o in range(0,96,8))
 check(rows==TABLE_ROWS[index],'callback exact immutable pointer pairs')
 check(rows[9]==(0,0) and all(a and b and a%2==b%2==0 for k,(a,b) in enumerate(rows) if k!=9),'callback allnonzero evenpairs except opcode20')
 return {'start':pc,'bytes':96,'sha256':sha256(raw).hexdigest(),'rows':[{'opcode':2*(k+1),'decoder':a,'handler':b} for k,(a,b) in enumerate(rows)],
  'original_data_only_not_executed':True,'actual_runtime_pointer_binding_or_same_snapshot_proved':False}


def profile(data,hexraw,index,parent):
 pc=STARTS[index];raw=init.binding.take(data,pc,SIZE);b=body(raw,index);n={v['pc']-pc:v for v in b['instructions']};table=table_body(data,index)
 check(n[0xe2]['imm']+n[0xe6]['imm']==TABLE_STARTS[index] and n[0xd8]['imm']==1 and n[0xdc]['imm']==-1 and n[0xde]['imm']==3,'callback original table base/index operands')
 check(n[0xc0]['imm']+0x20003000==n[0xc8]['imm']+0x20003000==0x20002eee+80*index,'callback fresh task selectorbyte')
 check(n[0xfc]['imm']==n[0xfe]['imm']==16 and n[0x106]['imm']==18,'callback low16word gate exception18')
 check(n[0x10c]['imm']==4 and n[0x10e]['imm']==8 and n[0x110]['imm']==1 and n[0x112]['imm']==0 and n[0x114]['imm']==24,'callback rowdecoder argument offsets')
 check(n[0x11c]['imm']==24 and n[0x11e]['rs2']==19,'callback rowhandler(ID,outputSP24)')
 check(n[0x134]['imm']==16 and n[0x12e]['imm']==20 and n[0x14a]['imm']==18 and n[0x14a]['width']==2,'callback partial reportrecord with SHSP18')
 check(n[0x16a]['imm']==4 and n[0x180]['target']==pc+0x2e and n[0x18c]['target']==pc+0x192,'callback forwardfailure skipssoleclear')
 # Reuse the full source setter/resource proofs, without claiming all writers.
 route=task8.route8;resources=route.body(init.binding.take(data,route.STARTS[index][2],266),'resources',index)
 rn={v['pc']-int(resources['start'],16):v for v in resources['instructions']}
 check(rn[184]['imm']+rn[188]['imm']==pc and rn[192]['target']==route.STARTS[index][3],'callback resource publishes matching original pointer via hookA')
 setter=route.body(init.binding.take(data,route.STARTS[index][3],10),'hook_A',index)
 check(setter['instructions'][1]['imm']+0x20003000==0x20002f70+80*index,'callback setter slot matches task8 otherword')
 # Parent handler callsites borrow tupleSP20 andflagSP11; parent auxprofile is separate.
 h=task8.body(init.binding.take(data,task8.STARTS[index][0],312),'handler',index)
 hn={v['pc']-h['start']:v for v in h['instructions']}
 check(hn[0x10e]['imm']+0x20003000==0x20002f70+80*index and hn[0x116]['imm']==11 and hn[0x11a]['imm']==20,'callback consumer slot and borrowed arguments join')
 check(hn[0x11e]['op']=='beqz' and hn[0x120]['rs2']==10 and hn[0xb8]['target']==h['start']+0xc8,'callback nonzero result replaceshandlerR and19 skipscleanup/XOR')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for label,start,size in [('callback',pc,SIZE),('pointer_table',table['start'],96)]:
  check(sparse.captured(mem,start,size)==init.binding.take(data,start,size),'callback complete strict HEX backing '+label)
  receipts.append({'part':label,'source':start,'bytes':size,'all_bytes_captured':True})
 return {'label':init.binding.PROFILES[index][0],'body':b,'table':table,'HEX_capture_receipts':receipts,'CFG_certificate':common.certificates(b),'paths':paths(b),
  'source_publication':{'resources_start':resources['start'],'resources_sha256':resources['sha256'],'setter_start':setter['start'],'setter_sha256':setter['sha256'],'slot':0x20002f70+80*index,'allwriters_or_installedbinding_proved':False},
  'normal_return_contract':[
   'opcode30 useslookup(ID,30),conditionalhelper(conn3,ID,0,30,0),thenconnhelper;alwayslocalreturn0,no directflagclear;helper repliesignored',
   'non30 captureswordtuple0 andoriginalA2flagpointer. Maskedprefix00120100 skipslookup;otherwise lookup(ID,initialopcode). Nonzero connectionbyte4 ->fixed0,possiblynestedcall andbit7write',
   'table path requires fresh taskbyte!=255,initialopcode<=24,twononnullrowpointers andcapturedlow16word0==0 unlessopcode18;failurefixed6. No genericlowerboundguard',
   'rowdecoder(freshtuple0,tuple1,tuple8,U16tuple4,SP24);nonzeroreplypropagated. Zero ->rowhandler(originalID,SP24)',
   'rowhandlernonzero:freshtuple1nonzero ->propagate;elseformpartialreportSP16. Report0 ->fixed0;reportnonzero ->helper(ID,22,1,SP16),propagatefullreply',
   'rowhandler0:opcode4 ->fixed0;elsehelper(freshtaskbyte,ID,0,freshopcode,SP24);nonzeroreplypropagates beforeclear. Helper0 ->leaf(SP24,freshopcode);leafnonzero clearsU8[originalA2] to0',
   'afterleaf path optionally storefreshopcode to cachedconnection4,thenreturn0. No directtuplewrite orpayloadfree;unknown row/nestedcalleeeffects andpointerretention remainunproved'],
  'status19_composition':'onlyopaque rowdecoder,rowhandler,report-sender orforward-helper replies canlocallypropagate19;all direct19paths bypasssoleflagclear. Underparentpreservation, freshflag1+M8nonnull stillattemptprivatepayloadrelease BEFORE savedR19 skipspublicmessagecleanup andeventXOR. Thisisnotsafe retainedmessageproof.',
  'ambient_argument_boundary':'originalA2releaseflag address remains live at bothfirstlookup callsites024/090. OnlyA0/A1areexplicitlyprepared;unknownlookupABI/effects cannotruleoutreceiptorretentionofambientA2. No transitive noescape claim.',
  'premises':'conditionalcandidateISA/code/source/providerbindings;validframe/global/tuple/connection/table accesses;normalcalleeS/SP/RA andsavedframepreservation;noadversealias/IRQ/DMA/reentry;tablepairidentity separatelyretained;borrowedoutputs notassumednonretained',
  'actual_installed_binding_payload_ownership_or_nonretention_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-task8-othercallback-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':876,'complete_body_instructions':320,'original_table_data_bytes':192,'C_reconstruction_coverage_changed':False,
  'remaining':['134Bforwardhelper/126Bpointerleaf andothernestedcallees','11rowdecoder/handlercontracts andothercallbacksource','actualinstalledprovider,otherwriters,payloadandborrowedstackretention'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=typed=table_mutations=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE)
  for a,v in decode(raw,STARTS[i]).items():
   off=a-STARTS[i];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('callback instruction mutation escaped')
   mutations+=1
  for off,_ in TYPED_LOADS[i]:
   bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError as ex:check('typed load encoding' in str(ex),'callback typed guard')
   else:raise RuntimeError('callback typed mutation escaped')
   typed+=1
  for o in range(0,96,4):
   bad=bytearray(data);bad[TABLE_STARTS[i]-0x40000+o]^=1
   try:table_body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('callback data pointer mutation escaped')
   table_mutations+=1
 for r in range(8,16):
  for imm in range(0,32,2):
   w=0x8060|((r-8)<<2)|((imm>>1&7)<<8)|((imm>>4)<<7);v=decode(w.to_bytes(2,'little'),0x1000)[0x1000]
   check((v['op'],v['rs1'],v['rs2'],v['imm'],v['width'])==('store',2,r,imm,2),'callback QKSHSP operandvector')
 check((mutations,typed,table_mutations)==(320,12,48),'callback mutation census');domains()
 print('PASS:320 instruction/12 typed-load/48 table-pointer mutations rejected;128 QKSHSP decodevectors;calleropcode/table/frame domains')


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
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
 td=(init.timer.REF/'RISCVInstrInfoXwch.td').read_text(encoding='utf-8');stack=td.split('class QKStackInst',1)[1].split('//===',1)[0];shsp=td.split('def QK_C_SHSP',1)[1].split('\n}',1)[0]
 check(all(s in stack for s in ('let Inst{15-11} = 0b10000','let Inst{6-5} = funct2','let Inst{4-2} = rd_rs2','let Inst{1-0} = 0b00')),'callback retained official QKStack encoding')
 check(all(s in shsp for s in ('QKStackInst<0b11','GPRC:$rd_rs2','SPMem:$rs1','let Inst{10-8} = imm{3-1}','let Inst{7} = imm{4}')),'callback retained official QKSHSP encoding')
 ledger['QKSHSP_encoding']={'mask':0xf863,'match':0x8060,'rs2':'8+bits4:2','imm':'bits10:8->3:1,bit7->4,bit0zero','original_word':0x81fc,'original_rs2':15,'original_offset':18,'vector_cases':128,'target_executed':False}
 tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'callback exact ledger replay')
 print('PASS:876B/320i complete othercallback +192B original tables;strict HEX;soleflagclear,status19 andsource/consumer joins;exact ledger')
 print('PASS:NO target execution/emulation;row/nestedcalleeeffects,actualbindings andpointer ownership/nonretention UNPROVED')


if __name__=='__main__':main()
