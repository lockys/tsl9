"""Offline RF task/request and callback17 -> APP retry/completion composition.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation, queue/timer/heap/provider/hardware model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_binding_order_static as previous
import check_v4160_payload_consumers_static as consumers
import check_v4160_timer_start_setup_static as timer
import check_v4160_dispatch_origin_mask_static as stopproof
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-callback-consume-static.json')
PARTS=('task','request')
STARTS=((0x65920,0x657d8),(0x65a0a,0x658c2))
SIZES=(248,328)
HASHES=(('be6e8e7481c7ad0e445cdb638a1a898397b31a000260f7b65b05fe7d1a2849c1', '16fdf9c0a1cb8ebbf1cde270c16ad763c92002b8a76bcd1259f7dd462985dd65'), ('f27c1f87671e16542d09f0a634afb49628e21335231532bd0e020947b22b9cda', 'd0975becaead8791d5404a4b6f446b3b1f26dbc006ad68011608176749d44484'))
COUNTS=((81, 126), (81, 126))
QK=({'task': ((22, 'd827', 'qk.c.lbu'), (28, 'd827', 'qk.c.lbu'), (30, '882b', 'qk.c.lbu'), (94, 'd827', 'qk.c.lbu'), (100, 'd827', 'qk.c.lbu'), (102, '882b', 'qk.c.lbu'), (180, 'dc27', 'qk.c.lbu'), (216, 'fc33', 'qk.c.lbu')), 'request': ((30, '5c27', 'qk.c.lbu'), (46, 'fc33', 'qk.c.lbu'), (58, '082b', 'qk.c.lbu'), (136, '3c20', 'qk.c.lbu'), (226, '3c30', 'qk.c.lbu'), (240, 'dc24', 'qk.c.lbu'), (244, '8828', 'qk.c.lbu'), (250, 'dca4', 'qk.c.sb'))}, {'task': ((22, 'd827', 'qk.c.lbu'), (28, 'd827', 'qk.c.lbu'), (30, '882b', 'qk.c.lbu'), (94, 'd827', 'qk.c.lbu'), (100, 'd827', 'qk.c.lbu'), (102, '882b', 'qk.c.lbu'), (180, 'dc27', 'qk.c.lbu'), (216, 'fc33', 'qk.c.lbu')), 'request': ((30, '5c27', 'qk.c.lbu'), (46, 'fc33', 'qk.c.lbu'), (58, '082b', 'qk.c.lbu'), (136, '3c20', 'qk.c.lbu'), (226, '3c30', 'qk.c.lbu'), (240, 'dc24', 'qk.c.lbu'), (244, '8828', 'qk.c.lbu'), (250, 'dca4', 'qk.c.sb'))})
TYPED=({'task': ((50, 4), (122, 4), (228, 4)), 'request': ((142, 2), (182, 4), (204, 4), (258, 2), (274, 2), (292, 2))}, {'task': ((50, 4), (122, 4), (228, 4)), 'request': ((142, 2), (182, 4), (204, 4), (258, 2), (274, 2), (292, 2))})
LITERALS=(
{
'task':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 1 12 4
006 andi 15 11 1
00a mv 8 11
00c beqz 15 80
00e lui 15 536883200
012 addi 15 15 1376
016 load 14 15 12 1
018 andi 14 14 2
01a beqz 14 68
01c load 14 15 12 1
01e load 10 15 16 1
020 addi 12 0 80
024 slli 15 14 24
028 srai 15 15 24
02a bge 15 0 62
02e lui 15 536883200
032 load 12 15 1369 1
036 addi 15 0 160
03a mul 12 12 15
03e li 11 4
040 jal 1 276264
044 xori 10 8 1
048 load 1 2 12 4
04a load 8 2 8 4
04c addi 2 2 16
04e jr 1
050 andi 15 11 2
054 beqz 15 150
056 lui 15 536883200
05a addi 15 15 1376
05e load 14 15 12 1
060 andi 14 14 4
062 beqz 14 144
064 load 14 15 12 1
066 load 10 15 16 1
068 addi 12 0 160
06c slli 15 14 24
070 srai 15 15 24
072 bge 15 0 138
076 lui 15 536883200
07a load 12 15 1369 1
07e addi 15 0 160
082 mul 12 12 15
086 addi 12 12 40
08a li 11 8
08c jal 1 276264
090 xori 10 8 2
094 jump 72
096 andi 15 11 4
09a beqz 15 166
09c jal 1 415704
0a0 xori 10 8 4
0a4 jump 72
0a6 andi 15 11 8
0aa beqz 15 196
0ac lui 15 536883200
0b0 addi 15 15 1376
0b4 load 15 15 12 1
0b6 andi 15 15 4
0b8 beqz 15 190
0ba jal 1 415578
0be xori 10 8 8
0c2 jump 72
0c4 andi 15 11 16
0c8 li 10 0
0ca beqz 15 72
0cc jal 1 278236
0d0 lui 15 536883200
0d4 addi 15 15 1300
0d8 load 15 15 7 1
0da li 14 8
0dc bne 14 15 242
0e0 lui 15 536883200
0e4 load 10 15 1392 1
0e8 addi 12 0 1600
0ec li 11 16
0ee jal 1 276264
0f2 xori 10 8 16
0f6 jump 72
''',
'request':'''
000 addi 2 2 -48
002 store 2 9 36 4
004 lui 9 536883200
008 store 2 1 44 4
00a store 2 8 40 4
00c store 2 18 32 4
00e store 2 19 28 4
010 store 2 20 24 4
012 store 2 21 20 4
014 store 2 22 16 4
016 store 2 23 12 4
018 store 2 24 8 4
01a addi 14 9 1376
01e load 15 14 12 1
020 andi 15 15 2
022 beq 15 0 304
026 lui 8 536883200
02a addi 15 8 1300
02e load 15 15 7 1
030 li 13 3
032 addi 8 8 1300
036 bne 13 15 88
03a load 10 14 16 1
03c li 11 4
03e load 8 2 40 4
040 load 1 2 44 4
042 load 9 2 36 4
044 load 18 2 32 4
046 load 19 2 28 4
048 load 20 2 24 4
04a load 21 2 20 4
04c load 22 2 16 4
04e load 23 2 12 4
050 load 24 2 8 4
052 addi 2 2 48
054 jal 0 275786
058 li 10 13
05a lui 20 4294959104
05c addi 9 9 1376
060 jal 1 409306
064 li 19 8
066 lui 22 536883200
06a lui 18 536883200
06e addi 20 20 -1
070 lui 23 8192
072 addi 12 0 128
076 li 11 0
078 li 10 0
07a lui 21 4096
07c jal 1 411540
080 addi 24 0 -128
084 addi 21 21 -110
088 load 15 8 2 1
08a andi 15 15 1
08c bnez 15 182
08e load 15 18 1340 4
092 load 15 15 100 4
094 bnez 15 136
096 addi 19 19 -1
098 bne 19 0 114
09c load 8 2 40 4
09e load 1 2 44 4
0a0 load 9 2 36 4
0a2 load 18 2 32 4
0a4 load 19 2 28 4
0a6 load 20 2 24 4
0a8 load 21 2 20 4
0aa load 22 2 16 4
0ac load 23 2 12 4
0ae load 24 2 8 4
0b0 addi 2 2 48
0b2 jal 0 415578
0b6 load 10 22 1344 1
0ba li 12 0
0bc addi 11 0 255
0c0 srai 10 10 4
0c2 andi 10 10 3
0c4 store 8 0 2 1
0c8 jal 1 408660
0cc load 11 22 1344 1
0d0 addi 12 0 255
0d4 li 10 1
0d6 srai 11 11 4
0d8 andi 11 11 3
0da auipc 1 536465408
0de jalr 1 1 -504
0e2 load 15 8 3 1
0e4 andi 15 15 1
0e6 beqz 15 254
0e8 store 8 0 3 1
0ec jal 1 410634
0f0 load 15 9 12 1
0f2 li 11 1
0f4 load 10 9 16 1
0f6 ori 15 15 128
0fa store 9 15 12 1
0fc jump 62
0fe jal 1 410634
102 load 15 18 1340 4
106 load 14 15 12 4
108 and 13 14 20
10c store 15 13 12 4
10e nop 
110 nop 
112 load 15 18 1340 4
116 store 15 23 8 4
11a store 8 24 4 1
11e store 15 21 100 4
122 store 15 14 12 4
124 load 15 18 1340 4
128 load 15 15 100 4
12a beqz 15 142
12c nop 
12e jump 292
130 load 1 2 44 4
132 load 8 2 40 4
134 load 9 2 36 4
136 load 18 2 32 4
138 load 19 2 28 4
13a load 20 2 24 4
13c load 21 2 20 4
13e load 22 2 16 4
140 load 23 2 12 4
142 load 24 2 8 4
144 addi 2 2 48
146 jr 1
''',
},
{
'task':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 1 12 4
006 andi 15 11 1
00a mv 8 11
00c beqz 15 80
00e lui 15 536883200
012 addi 15 15 1456
016 load 14 15 12 1
018 andi 14 14 2
01a beqz 14 68
01c load 14 15 12 1
01e load 10 15 16 1
020 addi 12 0 80
024 slli 15 14 24
028 srai 15 15 24
02a bge 15 0 62
02e lui 15 536883200
032 load 12 15 1449 1
036 addi 15 0 160
03a mul 12 12 15
03e li 11 4
040 jal 1 276404
044 xori 10 8 1
048 load 1 2 12 4
04a load 8 2 8 4
04c addi 2 2 16
04e jr 1
050 andi 15 11 2
054 beqz 15 150
056 lui 15 536883200
05a addi 15 15 1456
05e load 14 15 12 1
060 andi 14 14 4
062 beqz 14 144
064 load 14 15 12 1
066 load 10 15 16 1
068 addi 12 0 160
06c slli 15 14 24
070 srai 15 15 24
072 bge 15 0 138
076 lui 15 536883200
07a load 12 15 1449 1
07e addi 15 0 160
082 mul 12 12 15
086 addi 12 12 40
08a li 11 8
08c jal 1 276404
090 xori 10 8 2
094 jump 72
096 andi 15 11 4
09a beqz 15 166
09c jal 1 415938
0a0 xori 10 8 4
0a4 jump 72
0a6 andi 15 11 8
0aa beqz 15 196
0ac lui 15 536883200
0b0 addi 15 15 1456
0b4 load 15 15 12 1
0b6 andi 15 15 4
0b8 beqz 15 190
0ba jal 1 415812
0be xori 10 8 8
0c2 jump 72
0c4 andi 15 11 16
0c8 li 10 0
0ca beqz 15 72
0cc jal 1 278376
0d0 lui 15 536883200
0d4 addi 15 15 1380
0d8 load 15 15 7 1
0da li 14 8
0dc bne 14 15 242
0e0 lui 15 536883200
0e4 load 10 15 1472 1
0e8 addi 12 0 1600
0ec li 11 16
0ee jal 1 276404
0f2 xori 10 8 16
0f6 jump 72
''',
'request':'''
000 addi 2 2 -48
002 store 2 9 36 4
004 lui 9 536883200
008 store 2 1 44 4
00a store 2 8 40 4
00c store 2 18 32 4
00e store 2 19 28 4
010 store 2 20 24 4
012 store 2 21 20 4
014 store 2 22 16 4
016 store 2 23 12 4
018 store 2 24 8 4
01a addi 14 9 1456
01e load 15 14 12 1
020 andi 15 15 2
022 beq 15 0 304
026 lui 8 536883200
02a addi 15 8 1380
02e load 15 15 7 1
030 li 13 3
032 addi 8 8 1380
036 bne 13 15 88
03a load 10 14 16 1
03c li 11 4
03e load 8 2 40 4
040 load 1 2 44 4
042 load 9 2 36 4
044 load 18 2 32 4
046 load 19 2 28 4
048 load 20 2 24 4
04a load 21 2 20 4
04c load 22 2 16 4
04e load 23 2 12 4
050 load 24 2 8 4
052 addi 2 2 48
054 jal 0 275926
058 li 10 13
05a lui 20 4294959104
05c addi 9 9 1456
060 jal 1 409540
064 li 19 8
066 lui 22 536883200
06a lui 18 536883200
06e addi 20 20 -1
070 lui 23 8192
072 addi 12 0 128
076 li 11 0
078 li 10 0
07a lui 21 4096
07c jal 1 411774
080 addi 24 0 -128
084 addi 21 21 -110
088 load 15 8 2 1
08a andi 15 15 1
08c bnez 15 182
08e load 15 18 1420 4
092 load 15 15 100 4
094 bnez 15 136
096 addi 19 19 -1
098 bne 19 0 114
09c load 8 2 40 4
09e load 1 2 44 4
0a0 load 9 2 36 4
0a2 load 18 2 32 4
0a4 load 19 2 28 4
0a6 load 20 2 24 4
0a8 load 21 2 20 4
0aa load 22 2 16 4
0ac load 23 2 12 4
0ae load 24 2 8 4
0b0 addi 2 2 48
0b2 jal 0 415812
0b6 load 10 22 1424 1
0ba li 12 0
0bc addi 11 0 255
0c0 srai 10 10 4
0c2 andi 10 10 3
0c4 store 8 0 2 1
0c8 jal 1 408894
0cc load 11 22 1424 1
0d0 addi 12 0 255
0d4 li 10 1
0d6 srai 11 11 4
0d8 andi 11 11 3
0da auipc 1 536465408
0de jalr 1 1 -662
0e2 load 15 8 3 1
0e4 andi 15 15 1
0e6 beqz 15 254
0e8 store 8 0 3 1
0ec jal 1 410868
0f0 load 15 9 12 1
0f2 li 11 1
0f4 load 10 9 16 1
0f6 ori 15 15 128
0fa store 9 15 12 1
0fc jump 62
0fe jal 1 410868
102 load 15 18 1420 4
106 load 14 15 12 4
108 and 13 14 20
10c store 15 13 12 4
10e nop 
110 nop 
112 load 15 18 1420 4
116 store 15 23 8 4
11a store 8 24 4 1
11e store 15 21 100 4
122 store 15 14 12 4
124 load 15 18 1420 4
128 load 15 15 100 4
12a beqz 15 142
12c nop 
12e jump 292
130 load 1 2 44 4
132 load 8 2 40 4
134 load 9 2 36 4
136 load 18 2 32 4
138 load 19 2 28 4
13a load 20 2 24 4
13c load 21 2 20 4
13e load 22 2 16 4
140 load 23 2 12 4
142 load 24 2 8 4
144 addi 2 2 48
146 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1consume literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1consume typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1consume completeboundaries')
 for a,f in s.items():init.g(n,a,'B1consume '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1consume Xwchc raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1consume fullidentity')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1consume RET RA');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   check(d['rd'] in (0,1),'B1consume call/tail link')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1consume adjacentcallpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1consume closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'B1consume all localnodes reachable')
 if part=='request':
  cuts={(0x94,0x88),(0x98,0x72),(0x12a,0x8e),(0x12e,0x124)}
  cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in e.items()}
  check(not common.acyclic(e) and common.acyclic(cut),'B1consume request four exactcyclecuts')
  for o in (0x10e,0x110,0x12c):check(raw[o:o+2]==bytes.fromhex('0100') and n[pc+o]['op']=='nop','B1consume retainedhint bytes')
 else:check(common.acyclic(e),'B1consume task DAG')
 tasktargets=[(0x40,0x43728+140*index),(0x8c,0x43728+140*index),(0x9c,0x657d8+234*index),(0xba,0x6575a+234*index),(0xcc,0x43edc+140*index),(0xee,0x43728+140*index)]
 requesttargets=[(0x60,0x63eda+234*index),(0x7c,0x64794+234*index),(0xc8,0x63c54+234*index),(0xde,0x200026ba+76*index),(0xec,0x6440a+234*index),(0xfe,0x6440a+234*index)]
 expected=tasktargets if part=='task' else requesttargets
 check(calls==[dict(offset=o,target=t) for o,t in expected],'B1consume allcalltargets')
 expectedtails=[] if part=='task' else [dict(offset=0x54,target=0x4354a+140*index,new_link=False),dict(offset=0xb2,target=0x6575a+234*index,new_link=False)]
 check(tails==expectedtails and rets==[pc+(0x4e if part=='task' else 0x146)],'B1consume alltails/RET')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 saved=[d for d in stores if d['base']==2];frames={(8,8),(1,12)} if part=='task' else {(9,36),(1,44),(8,40),(18,32),(19,28),(20,24),(21,20),(22,16),(23,12),(24,8)}
 check(len(saved)==len(frames) and {(d['source'],d['imm']) for d in saved}==frames and all(d['bytes']==4 for d in saved),'B1consume exactframe saves')
 expectedstores=[] if part=='task' else [(0xc4,8,0,2,1),(0xe8,8,0,3,1),(0xfa,9,15,12,1),(0x10c,15,13,12,4),(0x116,15,23,8,4),(0x11a,8,24,4,1),(0x11e,15,21,100,4),(0x122,15,14,12,4)]
 check([d for d in stores if d['base']!=2]==[dict(offset=o,base=r,source=v,imm=x,bytes=z) for o,r,v,x,z in expectedstores],'B1consume allnonframe stores')
 if part=='task':check([a-pc for a,d in n.items() if d.get('rd')==8]==[0xa,0x4a],'B1consume fullE heldS0')
 else:check([a-pc for a,d in n.items() if d.get('rd')==19]==[0x46,0x64,0x96,0xa4,0x138],'B1consume outercounter solelocaldefinition/decrement/restores')
 return dict(start=pc,source=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,tails=tails,returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def valid_path(b,seq):
 e=b['CFG'];pc=b['start'];check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1consume immutablepath');return seq


def paths(b,part):
 if part=='task':
  choices={'event1_no_timer':{0xc:0xe,0x1a:0x44},'event1_fixed_delay':{0xc:0xe,0x1a:0x1c,0x2a:0x3e},'event1_variable_delay':{0xc:0xe,0x1a:0x1c,0x2a:0x2e},
   'event2_no_timer':{0xc:0x50,0x54:0x56,0x62:0x90},'event2_fixed_delay':{0xc:0x50,0x54:0x56,0x62:0x64,0x72:0x8a},'event2_variable_delay':{0xc:0x50,0x54:0x56,0x62:0x64,0x72:0x76},
   'event4_request':{0xc:0x50,0x54:0x96,0x9a:0x9c},'event8_skiphelper':{0xc:0x50,0x54:0x96,0x9a:0xa6,0xaa:0xac,0xb8:0xbe},
   'event8_helper':{0xc:0x50,0x54:0x96,0x9a:0xa6,0xaa:0xac,0xb8:0xba},
   'event16_no_timer':{0xc:0x50,0x54:0x96,0x9a:0xa6,0xaa:0xc4,0xca:0xcc,0xdc:0xf2},
   'event16_timer':{0xc:0x50,0x54:0x96,0x9a:0xa6,0xaa:0xc4,0xca:0xcc,0xdc:0xe0},'unrecognized0':{0xc:0x50,0x54:0x96,0x9a:0xa6,0xaa:0xc4,0xca:0x48}}
  return {name:common.walk(b,c) for name,c in choices.items()}
 base={0x22:0x26,0x36:0x58,0x8c:0x8e,0x94:0x96,0x98:0x9c}
 choices={'initial_gateclear_RET':{0x22:0x130},'state3_tail_setevent4':{0x22:0x26,0x36:0x3a},'single_attempt_template_tail':base,
  'status_success_tail_setevent1':{**base,0x8c:0xb6,0xe6:0xe8},
  'status_wait_then_exit_tail':{**base,0x8c:0xb6,0xe6:0xfe,0x12a:0x8e}}
 ps={name:common.walk(b,c) for name,c in choices.items()}
 seq=ps['single_attempt_template_tail'];a=seq.index(0x72);z=seq.index(0x98)
 ps['eight_counter_exits_tail']=valid_path(b,seq[:a]+seq[a:z+1]*8+seq[z+1:])
 check(ps['eight_counter_exits_tail'].count(0x7c)==8 and ps['eight_counter_exits_tail'].count(0x96)==8,'B1consume boundedcounter witness conditionalonpoll exit')
 seq=ps['status_wait_then_exit_tail'];j=seq.index(0x12a)
 ps['inner_wait_one_nonzero_then_zero']=valid_path(b,seq[:j+1]+[0x12c,0x12e,0x124,0x128,0x12a]+seq[j+1:])
 check(0x60 not in ps['state3_tail_setevent4'] and 0x60 in ps['single_attempt_template_tail'],'B1consume state3 defers beforecommand13')
 check(all(o in ps['status_success_tail_setevent1'] for o in (0xe8,0xec,0xfa,0xfc,0x3e,0x52,0x54)),'B1consume writes precedetail restoredframe')
 return ps


def app_body(image,role):
 _,pc,z,count,stores,digest=next(d for d in consumers.DETAILS if d[0]==role)
 old=consumers.body(consumers.take(image,pc,z),role,pc,z,count,stores,digest);n={d['pc']:d for d in old['instructions']}
 e={int(a,16):[int(q,16) for q in qs] for a,qs in old['conditional_normal_return_CFG'].items()};tails=[];rets=[]
 for a,d in n.items():
  external=[q for q in e[a] if q not in n]
  if external:check(len(e[a])==1 and d['op']=='jal' and d['rd']==0,'B1consume APP directtail shape');tails.append(dict(offset=a-pc,target=external[0],new_link=False));e[a]=[]
  if d['op']=='jr':
   if d['rs1']==1:rets.append(a)
   else:check(d['rs1']==6,'B1consume APP capturedT1tail');tails.append(dict(offset=a-pc,target='capturedT1 & ~1',new_link=False))
 return dict(start=pc,bytes=z,sha256=digest,instructions=old['instructions'],CFG=e,calls=old['calls'],tails=tails,returns=rets,complete_local_body=True,new_code_bytes_counted=0,target_execution_or_emulation=False)


def app_paths(bodies):
 s,r,f,t=(bodies[k] for k in ('status','retry','finish','task'))
 out={'status17':common.walk(s,{2:6,6:0xa,0x12:0x16}),
  'retry_old1_finish1':common.walk(r,{0x16:0x18}),'retry_other_start':common.walk(r,{0x16:0x1e}),
  'finish_callback_null':common.walk(f,{0x36:0x4c}),'finish_callback_tail1':common.walk(f,{0x36:0x3a}),
  'APP_task_bit1_finish1':common.walk(t,{0x10:0x30,0x34:0x64,0x6a:0x6c})}
 sn={d['pc']-s['start']:d for d in s['instructions']};check(not any(sn[o]['op']=='load' and sn[o]['rs1']==12 for o in out['status17']),'B1consume status17 noA2dereference')
 check(out['status17'][-1]==0x16 and out['retry_old1_finish1'][-1]==0x1a and out['retry_other_start'][-1]==0x32,'B1consume callback17 exacttails')
 seq=out['finish_callback_tail1'];check(seq.index(0x18)<seq.index(0x1e)<seq.index(0x26)<seq.index(0x32)<seq.index(0x44)<seq.index(0x48)<seq.index(0x4a),'B1consume stop-beforeclears/capture-beforeclear-before-restoredtail')
 check(0x6e in out['APP_task_bit1_finish1'] and 0x72 in out['APP_task_bit1_finish1'],'B1consume APPtimer task finishreply overwritten')
 return out


def domains():
 counts=[0]*6
 for E in range(65536):
  k=next((j for j in range(5) if E&(1<<j)),5);counts[k]+=1
  reply=E^(1<<k) if k<5 else 0
  check((not(reply&(1<<k))) if k<5 else reply==0,'B1consume RFtask lowestrecognizedbit reply')
 check(counts==[32768,16384,8192,4096,2048,2048],'B1consume RFtask prioritypartition')
 for original in range(256):
  u=(original-1)&255;check((u==0)==(original==1),'B1consume APP onlyold1 completion')
  check(original or u==255,'B1consume originalzero wraps255')
  check(original*160<=40800 and original*160+40<=40840,'B1consume variableRF delays scalar bounds')
  signed=((original<<24)&0xffffffff);signed=signed-2**32 if signed>=2**31 else signed
  check((signed>=0)==(original<128),'B1consume freshflagbyte signbit predicate')
 for q in range(9):check(8-q>=0 and ((8-q)==0)==(q==8),'B1consume eight exits counteralgebra;notpoll termination')
 for x in range(256):check((x>>4)&3 in range(4),'B1consume request freshconfig two-bit requests')
 check(17!=2 and 17>=2 and (17-17)&255==0 and 0<=1,'B1consume RF17 APPclassifier')
 check(0x8001^1==0x8000 and 0x8001^0x8000==1,'B1consume RFtask vsAPPtask differentpriorities')
 check(0xffffe000-1==0xffffdfff and 0x1000-110==3986 and 0x2000==8192 and (-128)&255==128,'B1consume request masks/writes')
 check(3!=4 and set(range(0x2000c7a4,0x2000c7aa)).isdisjoint(range(0x20003540,0x20003584)),'B1consume nominalAPP/RF config/task fields separate')
 return dict(RF_event_low16_cases=65536,RF_priority_partition=counts,RF_reply='fullentryE XORlowest recognizedbit1/2/4/8/16;none0,notAPPbit15priority',
  APP_retry_byte_cases=256,APP_counter0_wraps_to=255,APP_completion_only_old=1,RF_delay_byte_cases=256,RF_variable_delay_bounds=[40800,40840],
  request_outer_exits=8,unbounded_inner_poll_possible=True,task_ID_sources='RF C+16 vsAPP fresh2000c7a0;no valueequality claimed',
  request_precheck_and_RF_fresh_state='requeststate!=3 alone doesnotestablish laterRFstate;withstableequalstate callback17excluded here;B1core lacks earlierguard',target_execution_or_emulation=False)


def profile(image,data,hexraw,index,parent,app):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,STARTS[index][k],SIZES[k]);check(sparse.captured(mem,STARTS[index][k],SIZES[k])==raw,'B1consume fullcandidate originalHEX');bs[part]=body(raw,part,index)
 n={part:{d['pc']-b['start']:d for d in b['instructions']} for part,b in bs.items()};t,r=n['task'],n['request']
 C=0x20003560+80*index;S=0x20003514+80*index;F=C-32;Rslot=0x2000353c+80*index
 check(t[0xe]['imm']+t[0x12]['imm']==C and t[0x2e]['imm']+t[0x32]['imm']==F+25 and t[0xd0]['imm']+t[0xd4]['imm']==S and t[0xe0]['imm']+t[0xe4]['imm']==C+16,'B1consume RFtimer state sources')
 check(t[0x1e]['imm']==t[0x66]['imm']==16 and t[0x18]['imm']==2 and t[0x60]['imm']==4 and t[0x3e]['imm']==4 and t[0x8a]['imm']==8 and t[0xec]['imm']==16,'B1consume RFtask taskID/event masks')
 check(t[0x20]['imm']==80 and t[0x68]['imm']==160 and t[0x36]['imm']==t[0x7e]['imm']==160 and t[0x86]['imm']==40 and t[0xe8]['imm']==1600,'B1consume RFtask delay args')
 check(r[4]['imm']+r[0x1a]['imm']==C and r[0x26]['imm']+r[0x2a]['imm']==S and r[0x6a]['imm']+r[0x8e]['imm']==Rslot,'B1consume request context/source')
 check(r[0x58]['imm']==13 and r[0x64]['imm']==8 and r[0x72]['imm']==128 and r[0x7c]['target']==0x64794+234*index and r[0xc2]['imm']==r[0xd8]['imm']==3,'B1consume request command/outercount/extractors')
 check(r[0x3c]['imm']==4 and r[0xf2]['imm']==1 and r[0xfa]['imm']==12 and r[0xf6]['imm']==128 and r[0x12a]['op']=='beqz','B1consume deferred/retrysetevent andpoll direction')
 check(r[0x5a]['imm']+r[0x6e]['imm']==0xffffdfff and r[0x7a]['imm']+r[0x84]['imm']==3986 and r[0x70]['imm']==8192,'B1consume dynamiccontrol write values')
 role=parent['bodies']['role'];rolen={d['pc']-role['start']:d for d in role['instructions']}
 check(rolen[0x20]['imm']+rolen[0x26]['imm']==bs['task']['start'] and rolen[0x36]['imm']==16 and next(c['target'] for c in bs['task']['calls'] if c['offset']==0x9c)==bs['request']['start'],'B1consume registeredtask/request sourcejoin')
 # Parent still carries preceding inner-command evidence via its dependency; revalidate just the full RF body here.
 inner=previous.previous;rf=inner.rf;rfpc=rf.DETAILS[index][0][0];rfraw=init.binding.take(data,rfpc,198)
 check(sparse.captured(mem,rfpc,198)==rfraw,'B1consume reusedRF originalHEX');RF=rf.body(rfraw,'rf',index)
 rn={d['pc']-rfpc:d for d in RF['instructions']}
 check(bs['request']['calls'][0]['target']==rfpc and rn[0x46]['imm']==rn[0x48]['imm']==0 and rn[0x4a]['imm']==17 and rn[0x42]['imm']+0x20003000==F+16,'B1consume command13 callback17 exactslot/tuple')
 slotbytes=init.binding.take(data,0x40058,8);check(sparse.captured(mem,0x40058,8)==slotbytes,'B1consume timerAPI slotbytes')
 startpc=int.from_bytes(slotbytes[:4],'little');stoppc=int.from_bytes(slotbytes[4:],'little')
 check(startpc==timer.DETAILS[index][0] and stoppc==0x439a8+140*index,'B1consume rawtimer candidatebinding')
 startraw=init.binding.take(data,startpc,332);stopraw=init.binding.take(data,stoppc,108)
 check(sparse.captured(mem,startpc,332)==startraw and sparse.captured(mem,stoppc,108)==stopraw,'B1consume reusedtimers fulloriginalHEX')
 startbody=timer.body(startraw,'service',index)
 outer=stopproof.init.timer.outer.DETAILS[index]
 stopbody=stopproof.stop_body(stopraw,stoppc,outer[2],0x4358a+140*index,outer[-1])
 lookup=timer.body(init.binding.take(data,0x40584+64*index,30),'lookup',index)
 check(startbody['complete_function'] and stopbody['bytes']==108 and lookup['complete_function'],'B1consume reusedtimer completecontracts')
 check(sparse.captured(mem,0x40584+64*index,30)==init.binding.take(data,0x40584+64*index,30),'B1consume lookupleaf fulloriginalHEX')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},
  reused_APP=app,APP_paths=app_paths(app),reused_RF=dict(start=rfpc,bytes=198,sha256=sha256(rfraw).hexdigest(),new_code_bytes_counted=0),
  reused_timers=dict(start=startbody,stop=stopbody,lookup=lookup,new_code_bytes_counted=0,installed_binding_proved=False),
  globals=dict(RF_context=C,RF_status=S,RF_config=F,RF_task_byte=C+16,APP_task_byte=0x2000c7a0,APP_callback_word=0x2000c7a4,APP_retry_byte=0x2000c7a8,APP_length_byte=0x2000c7a9),
  RFtask_contract=['fullEheldS0,lowestrecognizedbit1/2/4/8/16 priority;returnfullE XORselectedmask afterchildren,evenifrequestfailed;no recognizedbit ->0. No task-localnonframe stores',
   'event1:freshC12bit1 enables timer(freshC16,4,80 or160*freshF25);event2:freshC12bit2 enables timer(freshC16,8,160 or160*freshF25+40);bit7 selector isanotherfreshC12 read',
   'event4 ->request657d8/658c2;event8 freshC12bit2 ->6575a/65844;event16 ->43edc/43f68 thenfreshstatus7==8 ->timer(freshC16,16,1600). Allchildrepliesignored'],
  request_contract=['48Bframe/10savedwords;freshC12bit1clear ->ordinaryRET withthenliveA0. Elsefreshstatus7==3 ->restoreframe andunlinkedset_event(freshC16,4),notstart_timer',
   'non3 ->command13,thenoutercounter8;eachadmittedattempt64794/6487e(0,0,128). Freshstatus2bit0clear ->freshU32[Rslot]+100:nonzero retry statuspoll,zero decrementoutercounter;8exits ->restoredtail6575a/65844',
   'status2bit0set ->clearstatus2;63c54/63d3e(freshF0bits4..5,255,0);RAM200026ba/20002706(1,independentlyfreshF0bits4..5,255)',
   'freshstatus3bit0set ->clearstatus3,6440a/644f4(),freshC12OR80,storeC12,restoreframe andset_event(freshC16,1)',
   'else6440a;captureP0=freshRslot,A4=freshwordP0+12;SW(A4&FFFFDFFF)P0+12;freshP1Rslot ->SW8192P1+8,SB80status4,SW3986P1+100,SWsavedA4P1+12;P0neednotequalP1',
   'innerpoll repeatedlyfreshRslot+100 untilzero,thenbacktofirstword100test. No poll timeout/monotonicprogress proof;outer8 alone notwholefunctionbound'],
  APP_callback17_contract=['RFexplicit(17,0,0) withmatchingglobalcallback174ee ->statussubtract17/mask255 thenunlinkedtail17442;thispath hasnoA2dereferences,so no packet read inferredfromnullA2',
   'retry freshold=U8C7A8;u=(old-1)&255,SBbeforebranch. old1 ->tailfinish173ee(1);old0wrap255 andallotheroldvalues ->tailfresh40058(freshAPPtask,1,2)',
   'finish savesentry1;fresh4005c(freshAPPtask,2),ignore scalar;clearC7A8 thenclearC7A9;capturefreshU32C7A4 intoT1;null RETthenliveA0,nonnullclearC7A4 andrestoreframe thenunlinkedcapturedT1(1)',
   'APPtask17476 consumesbit15first,thenbit0,thenbit1;selectedbit1 callsfinish(1) andoverwritesreplywithfullE XOR2. Actualtimerdelivery/taskidentity notproved'],
  composition=['RF taskbyteC16 andAPPtaskbyteC7A0 aredifferentcells/registrations;eachreadfresh,no taskvalueequality orsameeventqueueclaim',
   'requestearlierstate7!=3 mayexcludeRFcallback17 ONLYwithseparateprooflaterRFstate7equal. LaterRFfreshstate3 notassumed;B1core command13 callerhasnoearlierrequestguard',
   'RFcallback17 maythereforeleadAPPtimer/stop/externalcompletion requestsbefore RF commandreturns,underactualbinding/state/calleereturnpremises;corelaterignorescommandscalarandforces0',
   'completioncapture-andclearnotatomic;slotclearedbeforeexternaltail doesnotexcludeotherwriters/reentry;callerRF/request framesmayremainactivewhilefinishownframealreadyrestored',
   'timers arematchedcandidate contracts,not scheduling/delivery/cancel/persistence acknowledgements;unknownrequestcallees/alias retainfullpointerlifetime frontier'],
  premises='conditionalcandidateISA/providers/firstcopymapping/API/callbackbinding;validcode/frame/global/dynamicword/object extents;ordinarycalleeS/SP/RA/savedframepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalities separate',
  actual_event_delivery_timer_units_callback_execution_poll_progress_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);app={r:app_body(image,r) for r in ('status','retry','finish','task')}
 return dict(schema='TSL9-B1-RFtask-callback17-consumption-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i,parent['profiles'][i],app) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=1152,complete_phase_body_instructions=414,reused_APP_unique_bytes=332,reused_timer_lookup_bytes=940,reused_RF_bytes=396,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['6575a/65844,64794/6487e,63c54/63d3e,6440a/644f4 andRAM200026ba/20002706 effects','actualstate/flags/writers andtimer/eventdelivery ordering','actualproviderbinding andfullborrowedpointer/reentrant callbacklifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1consume instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1consume typedmutation escaped')
    typed+=1
 check((mutations,typed)==(414,18),'B1consume instruction/typed census');domains()
 print('PASS:414 instruction/18 typed-load mutations rejected;65536 RFpriority cases;256 retry/delay bytes;callback/order/frame certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1consume exactledger replay')
 print('PASS:1152B/414i complete RFtask/request;strict HEX;callback17/APP retry-completion/timer joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbinding/eventdelivery/pollprogress/pointerlifetimes UNPROVED')


if __name__=='__main__':main()
