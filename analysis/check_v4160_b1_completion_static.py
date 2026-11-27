"""Offline complete completion callback: packet-field producers and flag ordering.
Original operands/immutable CFG and host bit/interval certificates only.
No target execution/emulation, packet replay or mutable target-state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_channel_static as previous
import check_v4160_b1_request_config_static as config
import check_v4160_b1_request_leaves_static as cleanup
import check_v4160_constructor_consumer_tail_static as ramrequest
import check_v4160_large_consumer_service_static as service
import check_v4160_b1_selector_transform_static as leaves
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-completion-static.json')
STARTS=(0x65de6,0x65ed0)
SIZE=430
HASHES=('3d8188cd12d88a9eba8f4b8be41a05d52e7424ee07d56f19ceebbefed73d8c47', '3dec350b190cc4e87370a3ec45bd575cbe3b8cf9e66b5a6a2dfd3905be3a8926')
COUNTS=(156, 156)
TYPED=(((42, 4), (64, 4), (170, 4), (182, 4), (212, 2), (378, 4)), ((42, 4), (64, 4), (170, 4), (182, 4), (212, 2), (378, 4)))
QK=(((12, 'bc20', 'qk.c.lbu'), (86, 'bc30', 'qk.c.lbu'), (128, '3820', 'qk.c.lbu'), (202, 'bc20', 'qk.c.lbu'), (230, '3c38', 'qk.c.lbu'), (240, '1cbf', 'qk.c.sb'), (242, '5c28', 'qk.c.lbu'), (250, '3caf', 'qk.c.sb'), (252, '5c38', 'qk.c.lbu'), (262, '3cbf', 'qk.c.sb'), (264, '1428', 'qk.c.lbu'), (266, '7c34', 'qk.c.lbu'), (272, '1c38', 'qk.c.lbu'), (278, '3c28', 'qk.c.lbu'), (286, '7438', 'qk.c.lbu'), (288, '7c28', 'qk.c.lbu'), (294, '1c2c', 'qk.c.lbu'), (300, '1c3c', 'qk.c.lbu'), (342, '3c2c', 'qk.c.lbu')), ((12, 'bc20', 'qk.c.lbu'), (86, 'bc30', 'qk.c.lbu'), (128, '3820', 'qk.c.lbu'), (202, 'bc20', 'qk.c.lbu'), (230, '3c38', 'qk.c.lbu'), (240, '1cbf', 'qk.c.sb'), (242, '5c28', 'qk.c.lbu'), (250, '3caf', 'qk.c.sb'), (252, '5c38', 'qk.c.lbu'), (262, '3cbf', 'qk.c.sb'), (264, '1428', 'qk.c.lbu'), (266, '7c34', 'qk.c.lbu'), (272, '1c38', 'qk.c.lbu'), (278, '3c28', 'qk.c.lbu'), (286, '7438', 'qk.c.lbu'), (288, '7c28', 'qk.c.lbu'), (294, '1c2c', 'qk.c.lbu'), (300, '1c3c', 'qk.c.lbu'), (342, '3c2c', 'qk.c.lbu')))
LITERALS=(
'''
000 addi 2 2 -32
002 store 2 9 20 4
004 lui 9 536883200
008 addi 9 9 1300
00c load 15 9 2 1
00e store 2 18 16 4
010 store 2 1 28 4
012 lui 18 536883200
016 store 2 8 24 4
018 store 2 19 12 4
01a store 2 20 8 4
01c andi 15 15 1
01e addi 18 18 1376
022 beq 15 0 404
026 lui 19 536883200
02a load 10 19 1344 1
02e li 12 0
030 addi 11 0 32
034 srai 10 10 4
036 andi 10 10 3
038 store 9 0 2 1
03c jal 1 408660
040 load 11 19 1344 1
044 addi 12 0 255
048 li 10 1
04a srai 11 11 4
04c andi 11 11 3
04e auipc 1 536465408
052 jalr 1 1 -1914
056 load 15 9 3 1
058 andi 15 15 1
05a beq 15 0 404
05e load 10 9 36 4
060 store 9 0 3 1
064 li 13 0
066 li 12 0
068 li 11 0
06a store 9 0 2 1
06e auipc 1 536461312
072 jalr 1 1 2022
076 mv 20 10
078 bne 10 0 404
07c load 8 9 36 4
07e li 15 5
080 load 14 8 2 1
082 bne 14 15 404
086 lui 11 536883200
08a li 12 6
08c addi 11 11 516
090 addi 10 8 9
094 auipc 1 536453120
098 jalr 1 1 1480
09c li 15 1
09e bne 10 15 404
0a2 load 15 9 32 4
0a4 li 14 6
0a6 li 11 0
0a8 store 15 14 0 4
0aa load 10 19 1344 1
0ae srai 10 10 4
0b0 andi 10 10 3
0b2 jal 1 408334
0b6 load 11 19 1344 1
0ba li 12 0
0bc li 10 3
0be srai 11 11 4
0c0 andi 11 11 3
0c2 auipc 1 536465408
0c6 jalr 1 1 -2030
0ca load 15 9 2 1
0cc andi 15 15 1
0ce beqz 15 404
0d0 lui 15 536883200
0d4 load 15 15 480 4
0d8 store 9 0 2 1
0dc call_indirect 1 15
0de store 18 10 8 4
0e2 jal 1 415430
0e6 load 15 8 19 1
0e8 addi 14 19 1344
0ec store 14 0 1 1
0f0 store 14 15 25 1
0f2 load 15 8 20 1
0f4 store 18 0 13 1
0f8 li 12 0
0fa store 14 15 26 1
0fc load 15 8 21 1
0fe addi 19 19 1344
102 addi 11 0 32
106 store 14 15 27 1
108 load 13 8 16 1
10a load 15 8 15 1
10c slli 13 13 8
10e or 13 13 15
110 load 15 8 17 1
112 slli 15 15 16
114 or 13 13 15
116 load 15 8 18 1
118 slli 15 15 24
11a or 15 15 13
11c store 14 15 8 4
11e load 13 8 23 1
120 load 15 8 22 1
122 slli 13 13 8
124 or 13 13 15
126 load 15 8 24 1
128 slli 15 15 16
12a or 13 13 15
12c load 15 8 25 1
12e store 18 0 17 1
132 slli 15 15 24
134 or 15 15 13
136 store 14 15 20 4
138 li 14 0
13a srl 13 15 14
13e andi 13 13 1
140 beqz 13 330
142 addi 20 20 1
144 andi 20 20 255
148 li 12 1
14a addi 14 14 1
14c bne 14 11 314
150 beqz 12 342
152 store 18 20 17 1
156 load 15 8 26 1
158 lui 10 536883200
15c addi 11 8 3
160 store 19 15 24 1
164 li 12 6
166 li 15 2
168 addi 10 10 1404
16c store 18 15 12 1
170 auipc 1 536453120
174 jalr 1 1 988
178 load 8 2 24 4
17a load 10 18 16 1
17e load 1 2 28 4
180 load 9 2 20 4
182 load 18 2 16 4
184 load 19 2 12 4
186 load 20 2 8 4
188 addi 12 0 40
18c li 11 4
18e addi 2 2 32
190 jal 0 276264
194 jal 1 409176
198 load 1 2 28 4
19a load 8 2 24 4
19c li 15 -1
19e store 18 15 12 1
1a2 load 9 2 20 4
1a4 load 18 2 16 4
1a6 load 19 2 12 4
1a8 load 20 2 8 4
1aa addi 2 2 32
1ac jr 1
''',
'''
000 addi 2 2 -32
002 store 2 9 20 4
004 lui 9 536883200
008 addi 9 9 1380
00c load 15 9 2 1
00e store 2 18 16 4
010 store 2 1 28 4
012 lui 18 536883200
016 store 2 8 24 4
018 store 2 19 12 4
01a store 2 20 8 4
01c andi 15 15 1
01e addi 18 18 1456
022 beq 15 0 404
026 lui 19 536883200
02a load 10 19 1424 1
02e li 12 0
030 addi 11 0 32
034 srai 10 10 4
036 andi 10 10 3
038 store 9 0 2 1
03c jal 1 408894
040 load 11 19 1424 1
044 addi 12 0 255
048 li 10 1
04a srai 11 11 4
04c andi 11 11 3
04e auipc 1 536461312
052 jalr 1 1 2024
056 load 15 9 3 1
058 andi 15 15 1
05a beq 15 0 404
05e load 10 9 36 4
060 store 9 0 3 1
064 li 13 0
066 li 12 0
068 li 11 0
06a store 9 0 2 1
06e auipc 1 536461312
072 jalr 1 1 1864
076 mv 20 10
078 bne 10 0 404
07c load 8 9 36 4
07e li 15 5
080 load 14 8 2 1
082 bne 14 15 404
086 lui 11 536883200
08a li 12 6
08c addi 11 11 596
090 addi 10 8 9
094 auipc 1 536453120
098 jalr 1 1 1246
09c li 15 1
09e bne 10 15 404
0a2 load 15 9 32 4
0a4 li 14 6
0a6 li 11 0
0a8 store 15 14 0 4
0aa load 10 19 1424 1
0ae srai 10 10 4
0b0 andi 10 10 3
0b2 jal 1 408568
0b6 load 11 19 1424 1
0ba li 12 0
0bc li 10 3
0be srai 11 11 4
0c0 andi 11 11 3
0c2 auipc 1 536461312
0c6 jalr 1 1 1908
0ca load 15 9 2 1
0cc andi 15 15 1
0ce beqz 15 404
0d0 lui 15 536883200
0d4 load 15 15 560 4
0d8 store 9 0 2 1
0dc call_indirect 1 15
0de store 18 10 8 4
0e2 jal 1 415664
0e6 load 15 8 19 1
0e8 addi 14 19 1424
0ec store 14 0 1 1
0f0 store 14 15 25 1
0f2 load 15 8 20 1
0f4 store 18 0 13 1
0f8 li 12 0
0fa store 14 15 26 1
0fc load 15 8 21 1
0fe addi 19 19 1424
102 addi 11 0 32
106 store 14 15 27 1
108 load 13 8 16 1
10a load 15 8 15 1
10c slli 13 13 8
10e or 13 13 15
110 load 15 8 17 1
112 slli 15 15 16
114 or 13 13 15
116 load 15 8 18 1
118 slli 15 15 24
11a or 15 15 13
11c store 14 15 8 4
11e load 13 8 23 1
120 load 15 8 22 1
122 slli 13 13 8
124 or 13 13 15
126 load 15 8 24 1
128 slli 15 15 16
12a or 13 13 15
12c load 15 8 25 1
12e store 18 0 17 1
132 slli 15 15 24
134 or 15 15 13
136 store 14 15 20 4
138 li 14 0
13a srl 13 15 14
13e andi 13 13 1
140 beqz 13 330
142 addi 20 20 1
144 andi 20 20 255
148 li 12 1
14a addi 14 14 1
14c bne 14 11 314
150 beqz 12 342
152 store 18 20 17 1
156 load 15 8 26 1
158 lui 10 536883200
15c addi 11 8 3
160 store 19 15 24 1
164 li 12 6
166 li 15 2
168 addi 10 10 1484
16c store 18 15 12 1
170 auipc 1 536453120
174 jalr 1 1 754
178 load 8 2 24 4
17a load 10 18 16 1
17e load 1 2 28 4
180 load 9 2 20 4
182 load 18 2 16 4
184 load 19 2 12 4
186 load 20 2 8 4
188 addi 12 0 40
18c li 11 4
18e addi 2 2 32
190 jal 0 276404
194 jal 1 409410
198 load 1 2 28 4
19a load 8 2 24 4
19c li 15 -1
19e store 18 15 12 1
1a2 load 9 2 20 4
1a4 load 18 2 16 4
1a6 load 19 2 12 4
1a8 load 20 2 8 4
1aa addi 2 2 32
1ac jr 1
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'completion literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'completion fullboundaries')
 for a,f in s.items():init.g(n,a,'completion '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'completion typedload')
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'completion QK raw/width')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'completion fullidentity')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'completion RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   check(d['rd'] in (0,1),'completion link')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','completion pair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'completion clocklink');calls.append(dict(offset=a-pc,target='freshclockslot;no nullguard'))
  check(all(z in n for z in q),'completion closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 cut={a:[z for z in qs if (a-pc,z-pc)!=(0x14c,0x13a)] for a,qs in e.items()}
 expected=[(0x3c,0x63c54+234*index),(0x52,0x200026ba+76*index),(0x72,0x2000263a+76*index),(0x98,0x20000442),(0xb2,0x63b0e+234*index),(0xc6,0x200026ba+76*index),(0xdc,'freshclockslot;no nullguard'),(0xe2,0x656c6+234*index),(0x174,0x20000332),(0x194,0x63e58+234*index)]
 check(seen==set(n) and not common.acyclic(e) and common.acyclic(cut) and calls==[dict(offset=o,target=t) for o,t in expected],'completion fullCFG/cyclecut/all10calls')
 check(rets==[pc+0x1ac] and tails==[dict(offset=0x190,target=0x43728+140*index,new_link=False)],'completion soleRET/restoredtimer tail')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 frame=[(2,2,9,20,4),(0xe,2,18,16,4),(0x10,2,1,28,4),(0x16,2,8,24,4),(0x18,2,19,12,4),(0x1a,2,20,8,4)]
 other=[(0x38,9,0,2,1),(0x60,9,0,3,1),(0x6a,9,0,2,1),(0xa8,15,14,0,4),(0xd8,9,0,2,1),(0xde,18,10,8,4),(0xec,14,0,1,1),(0xf0,14,15,25,1),(0xf4,18,0,13,1),(0xfa,14,15,26,1),(0x106,14,15,27,1),(0x11c,14,15,8,4),(0x12e,18,0,17,1),(0x136,14,15,20,4),(0x152,18,20,17,1),(0x160,19,15,24,1),(0x16c,18,15,12,1),(0x19e,18,15,12,1)]
 check([d for d in stores if d[1]==2]==frame and [d for d in stores if d[1]!=2]==other and len(stores)==24,'completion allstores/frame')
 return dict(start=pc,bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,returns=rets,tails=tails,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 base={0x22:0x26,0x5a:0x5e,0x78:0x7c,0x82:0x86,0x9e:0xa2,0xce:0xd0,0x140:0x14a,0x14c:0x150,0x150:0x156}
 out={}
 for gate in (0x22,0x5a,0x78,0x82,0x9e,0xce):out['failure_'+hex(gate)]=common.walk(b,{**base,gate:0x194})
 out['success_zero_mask_template']=common.walk(b,base)
 # Immutable 32-bit scan witness; bit outcomes are certificate choices, never target state.
 for name,choices in (('success_zero_mask',{0x140:0x14a,0x150:0x156}),('success_full_mask',{0x140:0x142,0x150:0x152})):
  seq=common.walk(b,{**base,**choices});a=seq.index(0x13a);z=seq.index(0x14c)
  seq=seq[:a]+seq[a:z+1]*32+seq[z+1:];pc=b['start'];e=b['CFG']
  check(all(pc+q in e[pc+p] for p,q in zip(seq,seq[1:])) and seq.count(0x13a)==32,'completion32scan syntacticwitness');out[name]=seq
 for name,seq in out.items():
  if name.startswith('failure'):
   check(seq.index(0x194)<seq.index(0x19e) and seq[-1]==0x1ac,'completion failure resetbeforeFF/RET')
  else:
   check(seq.index(0xdc)<seq.index(0xde)<seq.index(0xe2)<seq.index(0xe6)<seq.index(0xfa)<seq.index(0x136)<seq.index(0x16c)<seq.index(0x174)<seq.index(0x18e)<seq.index(0x190),'completion clock/baseline/cleanup/packet/flag/copy/restoredtail order')
 return out


def producer_certificates(b):
 n={d['pc']-b['start']:d for d in b['instructions']}
 mapping={0xe6:(19,0xf0,25),0xf2:(20,0xfa,26),0xfc:(21,0x106,27),0x156:(26,0x160,24)}
 for load,(packetoff,store,field) in mapping.items():check(n[load]['rs1']==8 and n[load]['imm']==packetoff and n[load]['width']==1 and n[store]['imm']==field and n[store]['width']==1,'completion packetbyte producer')
 for offsets,poff,dest in (((0x10a,0x108,0x110,0x116),15,0x11c),((0x120,0x11e,0x126,0x12c),22,0x136)):
  check([n[o]['imm'] for o in offsets]==list(range(poff,poff+4)) and all(n[o]['rs1']==8 and n[o]['width']==1 for o in offsets),'completion independent packetbytes pack')
  check(n[dest]['rs2']==15 and n[dest]['width']==4,'completion constructedword store')
 check(n[0x76]['rd']==20 and n[0x76]['rs2']==10 and n[0x78]['op']=='bne' and n[0x78]['rs1']==10 and n[0x78]['rs2']==0,'completion successrequirescountseedzero')
 check([o for o,d in n.items() if d.get('rd')==20]==[0x76,0x142,0x144,0x186,0x1a8],'completion countseed/increment/restore only')
 check(n[0xf8]['rd']==12 and n[0xf8]['imm']==0 and n[0x102]['rd']==11 and n[0x102]['imm']==32 and n[0x138]['rd']==14 and n[0x138]['imm']==0 and n[0x14a]['imm']==1 and n[0x144]['imm']==255,'completion finitepopcount anchors')
 check(not any(d.get('rd')==15 for o,d in n.items() if 0x136<=o<0x156) and n[0x13a]['rs1']==15,'completion count sameheldword as F20store')
 return dict(byte_fields=[dict(packet_offset=v[0],field_offset=v[2]) for v in mapping.values()],word_fields={8:list(range(15,19)),20:list(range(22,26))},
  mask_publication='SB0C17 thenSWheldW F20 then32bitcount ->ifnonzero SBC17count;zeroW leavesinitialclear',
  conditional_C17_equals_popcount_stored_W=True,K_positive_checked=False,packet_minimum_direct_extent=27,packet_reads_coherent_or_lifetime_proved=False)


def domains():
 masks=0
 for low in range(65536):
  for word in (low,low|(low<<16)):
   count=sum((word>>i)&1 for i in range(32));check(count==word.bit_count() and 0<=count<=32 and count&255==count,'completion popcount/byte no wrap');masks+=1
 for byte in range(256):check(byte&255==byte,'completion packetK canincludezero no localreject')
 for a in (0,1,127,255):
  for b in range(256):
   for c,d in ((0,0),(255,255)):
    packed=a|(b<<8)|(c<<16)|(d<<24);check(packed.to_bytes(4,'little')==bytes((a,b,c,d)),'completion LEpack fields')
 check(2!=0 and 255!=0 and 0!=2,'completion nonzeroflags success2/fail255 bothdifferfromwait0')
 return dict(mask_family_cases=masks,mask_domain='all16bitmasks andduplicated16bitmasks,notall32bitmasks',K_byte_cases=256,popcount_range=[0,32],
  successful_producer_invariant='understoredW/C17preservation,completedproducer yieldsC17=popcountW;partialpublication/externalwriters/otherpaths canbreaklaterfreshpair',
  C12_success=2,C12_failure=255,C12_success_before_copy_and_timer=True,no_event_delivery_or_wholecallback_progress_proved=True,target_execution_or_emulation=False)


def reuse(data,mem,index):
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];out={}
 for part,target,z,fn in (('RAMservice',service.STARTS[index][4],128,lambda raw:service.body(raw,'RAMservice',index)),('RAMrequest',ramrequest.STARTS[index][3],250,lambda raw:ramrequest.body(raw,'ramtail',index)),('comparator',0x20000442,72,lambda raw:leaves.comparator.body(raw,'comparator',index)),('copy',0x20000332,58,lambda raw:leaves.copier.body(raw,'copy',0x20000332,18,init.binding.COPY_HASH))):
  src=int(first['source'],16)+target-int(first['destination'],16);raw=init.binding.take(data,src,z)
  check(sparse.captured(mem,src,z)==raw and target+z<=int(mapping['first_copy_end_exclusive'],16),'completion reusedRAM fullHEX/affine mapping');out[part]=dict(source=src,target=target,body=fn(raw),new_code_bytes_counted=0,actual_binding_proved=False)
 for part,pc,z,fn in (('config',config.STARTS[index],278,lambda raw:config.body(raw,index)),('channel',previous.STARTS[index],326,lambda raw:previous.body(raw,index)),('cleanup',cleanup.STARTS[index][0],148,lambda raw:cleanup.body(raw,'inner',index))):
  raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'completion reusedcallee fullHEX');out[part]=dict(target=pc,body=fn(raw),new_code_bytes_counted=0)
 srv=out['RAMservice']['body'];s=dict(srv,CFG=srv['local_CFG'],tails=[])
 out['RAMservice_zero_args_paths']={str(bit):common.walk(s,{0xe:0x7c if bit else 0x10,0x10:0x18,0x18:0x46,0x46:0x66}) for bit in (0,1)}
 for seq in out['RAMservice_zero_args_paths'].values():check(not any(d['pc']-srv['start'] in seq and d['op']=='load' and d['rs1']==10 for d in srv['instructions']),'completion decoder zeroargs no packetdereference')
 return out


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE)
 check(sparse.captured(mem,STARTS[index],SIZE)==raw,'completion strictoriginalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;S=G+1300+80*index;F=G+1344+80*index;C=G+1376+80*index
 check(n[4]['imm']+n[8]['imm']==S and n[0x12]['imm']+n[0x1e]['imm']==C and n[0x26]['imm']+n[0xe8]['imm']==F and n[0x26]['imm']+n[0xfe]['imm']==F,'completion fixedS/F/C')
 check(n[0x64]['imm']==n[0x66]['imm']==n[0x68]['imm']==0 and n[0x5e]['imm']==36 and n[0x7c]['imm']==36 and n[0x80]['imm']==2 and n[0x7e]['imm']==5 and n[0x9c]['imm']==1,'completion gates andfresh packetpointer')
 check(n[0x86]['imm']+n[0x8c]['imm']==G+516+80*index and n[0x8a]['imm']==6 and n[0x90]['imm']==9 and n[0x168]['imm']+n[0x158]['imm']==C+28 and n[0x15c]['imm']==3 and n[0x164]['imm']==6,'completion compare/copy tupleorigins')
 check(n[0x166]['imm']==2 and n[0x19c]['imm']==-1 and n[0x17a]['imm']==16 and n[0x188]['imm']==40 and n[0x18c]['imm']==4,'completion flagwrites/timertail args')
 attempt=previous.previous.previous.previous.previous
 ar=init.binding.take(data,attempt.STARTS[index],502);caller=attempt.body(ar,index);cn={d['pc']-caller['start']:d for d in caller['instructions']}
 check(sparse.captured(mem,attempt.STARTS[index],502)==ar and cn[0x1ba]['imm']+cn[0x1c0]['imm']==b['start'] and cn[0x1da]['imm']==cn[0x1ea]['imm']==12,'completion exactregisteredliteral/waitfield join')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),producer_certificates=producer_certificates(b),reused=reuse(data,mem,index),
  reused_attempt=dict(start=caller['start'],bytes=502,new_code_bytes_counted=0),nominal_globals=dict(status=S,config=F,context=C,completion=C+12),
  contract=['sixgates:initialS2bit0,afterconfig+RAMmode1freshS3bit0,RAMservice(S36,0,0,0)==0,freshpacketS36byte2==5,compare(packet+9,fixed6bytes,6)==1,afterchannel+RAMmode3freshS2bit0;anyfail reset thenSBFFC12 thenordinaryRETliveA0',
   'RAMservice matchingzeroargs no packetA0dereference/nooptionaloutwrites;status0/1 fromfreshR words,0 writesC11;packetP reloadedS36 aftercall,notassumedearlierpointer',
   'success clockcall no nullguard ->SWC8,thencleanup inner whichmayreleaseC4 BEFORE savedP readsresume;S0registerpreservation alone doesnotprovePcontentslifetime/disjointfromreleasedobject',
   'packet19/20/21 ->F25/26/27;F1=0,C13=0;packet15..18->LEwordF8;packet22..25->heldW/F20;C17clear thenpopcountheldW0..32;packet26->F24. No Kzero guard',
   'successC12=2 BEFOREcopy(C28,P+3,6) andrestoredframe timertail(freshC16,4,40);failureC12=255 AFTERresetreturn. Nonzero flagdoesnotprovefinalcopy/timer/delivery ororiginalwaitingthreadobservesit',
   'actualcallbackdispatch maynotoccur ormayprecedeouterclearC12;noatomicity/happens-before/progressproof. ProducercompletedpairC17/popcountW notuniversalacrosspartialpublication/writers/freshreads'],
  premises='conditionalcandidateISA/API/firstcopy/installedcallbackandproviders;validframe/global/packetextent27/helperextents;ordinarycalleeS/SP/RA/frame andsavedPobjectpreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalityseparate',
  actual_callback_delivery_provider_binding_positive_K_packet_lifetime_pollprogress_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-completion-callback-field-producers-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=860,complete_phase_body_instructions=312,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['actualpacketS36 producers/extent/lifetime andconfigurationfieldreachability','callbackdelivery/outerC12clear ordering andotherwriters','actualinstalledproviders/physicaleffects/pollprogress/fullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('completion instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('completion typedmutation escaped')
   typed+=1
 check((mutations,typed)==(312,12),'completion mutationcensus')
 print('PASS:312 instruction/12 typed-load mutations rejected;complete CFG/frame/store/gate/fieldproducer certificates')


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
 else:check(OUT.read_bytes()==encoded,'completion exactledger replay')
 print('PASS:860B/312i completecallback;strictHEX;131072 popcountmasks;K/mask/divisor producers andcompletion ordering;exactledger')
 print('PASS:NO target execution/emulation;actualdelivery/Kpositive/pointerlifetimes/pollprogress UNPROVED')


if __name__=='__main__':main()
