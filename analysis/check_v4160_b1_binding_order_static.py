"""Offline RF configuration publication and conditional initialization order.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation, callback/provider/heap/hardware state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_inner_static as previous
import check_v4160_payload_consumers_static as consumers
import check_v4160_b1_selector_callees_static as callees
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-binding-order-static.json')
PARTS=('config','role','setup')
STARTS=((0x64bae,0x66056,0x8e88),(0x64c98,0x66194,0x8e88))
SIZES=(318,66,384)
HASHES=(('0e73a5cebf069a716f6967b386c8cc9de529e25608933422eda98997a0ec9bf4', '36d01f733b49e82f9acb498331c8390c5ab1950b8c30d548952019b4f2d5d9d5', 'a6a0c6e308fb8480b628dc3b08e5aa9f1dcd0b1c1d879d37466a0eba9d16c542'), ('a864e180da29434561f5dd159314d187904b5262d8b95cda0c3c289f1ffb1974', 'e159bf0c99161e18d1de10f70e267853669a42879ab24cc9d28fbf5ecd91fe57', 'a6a0c6e308fb8480b628dc3b08e5aa9f1dcd0b1c1d879d37466a0eba9d16c542'))
COUNTS=((112, 22, 126), (112, 22, 126))
QK=({'config': ((16, '1c21', 'qk.c.lbu'), (76, '9c3f', 'qk.c.lbu'), (88, '1cbc', 'qk.c.sb'), (90, '3c2c', 'qk.c.lbu'), (96, '3cac', 'qk.c.sb'), (98, '3c3c', 'qk.c.lbu'), (104, '3cbc', 'qk.c.sb'), (106, '5c2c', 'qk.c.lbu'), (112, '5cac', 'qk.c.sb'), (114, '5c3c', 'qk.c.lbu'), (120, '5cbc', 'qk.c.sb'), (122, '9c20', 'qk.c.lbu'), (148, '1cb0', 'qk.c.sb'), (186, '483c', 'qk.c.lbu'), (204, '1c30', 'qk.c.lbu'), (208, 'fcb4', 'qk.c.sb')), 'role': ((54, '08a8', 'qk.c.sb'),), 'setup': ((198, '8385', 'lb'),)}, {'config': ((16, '1c21', 'qk.c.lbu'), (76, '9c3f', 'qk.c.lbu'), (88, '1cbc', 'qk.c.sb'), (90, '3c2c', 'qk.c.lbu'), (96, '3cac', 'qk.c.sb'), (98, '3c3c', 'qk.c.lbu'), (104, '3cbc', 'qk.c.sb'), (106, '5c2c', 'qk.c.lbu'), (112, '5cac', 'qk.c.sb'), (114, '5c3c', 'qk.c.lbu'), (120, '5cbc', 'qk.c.sb'), (122, '9c20', 'qk.c.lbu'), (148, '1cb0', 'qk.c.sb'), (186, '483c', 'qk.c.lbu'), (204, '1c30', 'qk.c.lbu'), (208, 'fcb4', 'qk.c.sb')), 'role': ((54, '08a8', 'qk.c.sb'),), 'setup': ((198, '8385', 'lb'),)})
TYPED=({'config': ((174, 4),), 'role': (), 'setup': ((42, 2), (48, 2), (54, 2), (60, 2), (92, 2), (112, 2), (126, 2), (142, 2), (154, 2), (178, 4), (198, 0), (202, 2), (222, 2), (238, 2), (246, 2), (268, 2), (290, 2), (304, 2), (330, 4), (356, 2))}, {'config': ((174, 4),), 'role': (), 'setup': ((42, 2), (48, 2), (54, 2), (60, 2), (92, 2), (112, 2), (126, 2), (142, 2), (154, 2), (178, 4), (198, 0), (202, 2), (222, 2), (238, 2), (246, 2), (268, 2), (290, 2), (304, 2), (330, 4), (356, 2))})
LITERALS=(
{
'config':'''
000 load 15 10 16 4
002 beq 15 0 314
006 addi 2 2 -16
008 store 2 9 4 4
00a store 2 1 12 4
00c store 2 8 8 4
00e store 2 18 0 4
010 load 15 10 0 1
012 mv 9 10
014 andi 15 15 64
018 beqz 15 32
01a load 15 10 4 4
01c li 10 2
01e beqz 15 214
020 lui 18 536883200
024 addi 12 0 32
028 li 11 0
02a addi 10 18 1344
02e auipc 1 536457216
032 jalr 1 1 1984
036 addi 12 0 32
03a mv 11 9
03c addi 10 18 1344
040 auipc 1 536457216
044 jalr 1 1 1860
048 addi 15 18 1344
04c load 15 15 25 1
04e addi 8 18 1344
052 bnez 15 90
054 addi 15 0 40
058 store 8 15 25 1
05a load 15 8 26 1
05c bnez 15 98
05e li 15 8
060 store 8 15 26 1
062 load 15 8 27 1
064 bnez 15 106
066 li 15 17
068 store 8 15 27 1
06a load 15 8 28 1
06c bnez 15 114
06e li 15 -5
070 store 8 15 28 1
072 load 15 8 29 1
074 bnez 15 122
076 li 15 -5
078 store 8 15 29 1
07a load 15 9 0 1
07c andi 15 15 64
080 beqz 15 150
082 load 15 8 4 4
084 lui 14 2404352
088 addi 14 14 -353
08c bltu 14 15 226
090 addi 15 0 37
094 store 8 15 1 1
096 lui 9 536883200
09a addi 15 9 1376
09e load 10 15 4 4
0a0 addi 9 9 1376
0a4 beqz 10 174
0a6 auipc 1 536457216
0aa jalr 1 1 1212
0ae load 15 18 1344 1
0b2 store 9 0 4 4
0b6 andi 15 15 1
0b8 beqz 15 204
0ba load 10 8 29 1
0bc addi 11 0 73
0c0 addi 10 10 2
0c2 auipc 1 536457216
0c6 jalr 1 1 976
0ca store 9 10 4 4
0cc load 15 8 1 1
0ce li 10 0
0d0 store 9 15 15 1
0d2 load 15 8 8 4
0d4 store 9 15 20 4
0d6 load 1 2 12 4
0d8 load 8 2 8 4
0da load 9 2 4 4
0dc load 18 2 0 4
0de addi 2 2 16
0e0 jr 1
0e2 lui 14 2424832
0e6 addi 13 14 1167
0ea bltu 13 15 260
0ee lui 14 4292567040
0f2 addi 14 14 -1744
0f6 add 15 15 14
0f8 addi 14 0 2000
0fc divu 15 15 14
100 addi 15 15 -1
102 jump 148
104 addi 14 14 1168
108 bne 15 14 274
10c addi 15 0 38
110 jump 148
112 lui 14 2478080
116 addi 14 14 1919
11a bltu 14 15 308
11e lui 14 4292567040
122 addi 14 14 -1744
126 add 15 15 14
128 addi 14 0 2000
12c divu 15 15 14
130 addi 15 15 -2
132 jump 148
134 addi 15 0 39
138 jump 148
13a li 10 1
13c jr 1
''',
'role':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 store 2 8 8 4
006 jal 1 410264
00a lui 8 536883200
00e addi 10 8 1376
012 addi 12 0 36
016 li 11 0
018 auipc 1 536453120
01c jalr 1 1 814
020 lui 10 417792
024 li 15 -1
026 addi 10 10 -1760
02a store 8 15 1376 4
02e jal 1 277582
032 addi 8 8 1376
036 store 8 10 16 1
038 load 1 2 12 4
03a load 8 2 8 4
03c li 10 0
03e addi 2 2 16
040 jr 1
''',
'setup':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 262144
008 load 15 8 72 4
00a lui 12 4096
00c store 2 1 28 4
00e addi 12 12 -1972
012 li 11 0
014 auipc 10 536879104
018 addi 10 10 752
01c store 2 9 20 4
01e call_indirect 1 15
020 jal 1 104930
024 jal 1 105238
028 jal 1 36986
02a load 15 8 416 4
02e call_indirect 1 15
030 load 15 8 428 4
034 call_indirect 1 15
036 load 15 8 448 4
03a call_indirect 1 15
03c load 15 8 128 4
040 auipc 10 4294963200
044 addi 10 10 1868
048 call_indirect 1 15
04a store 3 10 157 1
04e li 15 6
050 store 2 15 12 2
054 addi 15 0 1000
058 store 2 15 14 2
05c load 15 8 372 4
060 auipc 12 69632
064 addi 12 12 -252
068 li 11 13
06a addi 10 0 774
06e call_indirect 1 15
070 load 15 8 372 4
074 addi 12 2 12
076 li 11 2
078 addi 10 0 785
07c call_indirect 1 15
07e load 15 8 372 4
082 addi 12 2 14
086 li 11 2
088 addi 10 0 786
08c call_indirect 1 15
08e load 15 8 340 4
092 addi 11 0 160
096 li 10 3
098 call_indirect 1 15
09a load 15 8 340 4
09e addi 11 0 160
0a2 li 10 4
0a4 call_indirect 1 15
0a6 li 10 1
0a8 jal 1 35694
0aa addi 15 3 84
0ae load 15 15 0 4
0b0 li 14 3
0b2 load 15 15 7 1
0b6 andi 15 15 3
0b8 beq 15 14 214
0bc auipc 14 73728
0c0 addi 14 14 -1040
0c4 add 15 15 14
0c6 load 11 15 0 1
0ca load 15 8 340 4
0ce li 10 25
0d0 slli 11 11 16
0d2 srli 11 11 16
0d4 call_indirect 1 15
0d6 lui 8 262144
0da store 2 0 14 1
0de load 15 8 360 4
0e2 addi 12 2 14
0e6 li 11 1
0e8 addi 10 0 1024
0ec call_indirect 1 15
0ee load 15 8 196 4
0f2 li 9 -2
0f4 call_indirect 1 15
0f6 load 15 8 128 4
0fa auipc 10 4294963200
0fe addi 10 10 1682
102 call_indirect 1 15
104 store 3 10 148 1
108 store 3 9 150 2
10c load 15 8 128 4
110 auipc 10 4294963200
114 addi 10 10 1660
118 call_indirect 1 15
11a store 3 10 152 1
11e store 3 9 154 2
122 load 15 8 312 4
126 lui 10 65536
128 addi 11 3 128
12c addi 10 10 -1
12e call_indirect 1 15
130 load 15 8 304 4
134 auipc 13 69632
138 addi 13 13 -448
13c li 12 16
13e li 11 4
140 addi 10 3 0
144 call_indirect 1 15
146 load 15 8 80 4
148 li 11 8
14a load 10 3 157 1
14e call_indirect 1 15
150 jal 1 75014
154 jal 1 95720
158 load 15 8 72 4
15a li 12 3
15c li 11 0
15e addi 10 3 144
162 call_indirect 1 15
164 load 15 8 128 4
168 auipc 10 0
16c addi 10 10 -878
170 call_indirect 1 15
172 load 1 2 28 4
174 load 8 2 24 4
176 store 3 10 144 1
17a load 9 2 20 4
17c addi 2 2 32
17e jr 1
''',
},
{
'config':'''
000 load 15 10 16 4
002 beq 15 0 314
006 addi 2 2 -16
008 store 2 9 4 4
00a store 2 1 12 4
00c store 2 8 8 4
00e store 2 18 0 4
010 load 15 10 0 1
012 mv 9 10
014 andi 15 15 64
018 beqz 15 32
01a load 15 10 4 4
01c li 10 2
01e beqz 15 214
020 lui 18 536883200
024 addi 12 0 32
028 li 11 0
02a addi 10 18 1424
02e auipc 1 536457216
032 jalr 1 1 1750
036 addi 12 0 32
03a mv 11 9
03c addi 10 18 1424
040 auipc 1 536457216
044 jalr 1 1 1626
048 addi 15 18 1424
04c load 15 15 25 1
04e addi 8 18 1424
052 bnez 15 90
054 addi 15 0 40
058 store 8 15 25 1
05a load 15 8 26 1
05c bnez 15 98
05e li 15 8
060 store 8 15 26 1
062 load 15 8 27 1
064 bnez 15 106
066 li 15 17
068 store 8 15 27 1
06a load 15 8 28 1
06c bnez 15 114
06e li 15 -5
070 store 8 15 28 1
072 load 15 8 29 1
074 bnez 15 122
076 li 15 -5
078 store 8 15 29 1
07a load 15 9 0 1
07c andi 15 15 64
080 beqz 15 150
082 load 15 8 4 4
084 lui 14 2404352
088 addi 14 14 -353
08c bltu 14 15 226
090 addi 15 0 37
094 store 8 15 1 1
096 lui 9 536883200
09a addi 15 9 1456
09e load 10 15 4 4
0a0 addi 9 9 1456
0a4 beqz 10 174
0a6 auipc 1 536457216
0aa jalr 1 1 978
0ae load 15 18 1424 1
0b2 store 9 0 4 4
0b6 andi 15 15 1
0b8 beqz 15 204
0ba load 10 8 29 1
0bc addi 11 0 73
0c0 addi 10 10 2
0c2 auipc 1 536457216
0c6 jalr 1 1 742
0ca store 9 10 4 4
0cc load 15 8 1 1
0ce li 10 0
0d0 store 9 15 15 1
0d2 load 15 8 8 4
0d4 store 9 15 20 4
0d6 load 1 2 12 4
0d8 load 8 2 8 4
0da load 9 2 4 4
0dc load 18 2 0 4
0de addi 2 2 16
0e0 jr 1
0e2 lui 14 2424832
0e6 addi 13 14 1167
0ea bltu 13 15 260
0ee lui 14 4292567040
0f2 addi 14 14 -1744
0f6 add 15 15 14
0f8 addi 14 0 2000
0fc divu 15 15 14
100 addi 15 15 -1
102 jump 148
104 addi 14 14 1168
108 bne 15 14 274
10c addi 15 0 38
110 jump 148
112 lui 14 2478080
116 addi 14 14 1919
11a bltu 14 15 308
11e lui 14 4292567040
122 addi 14 14 -1744
126 add 15 15 14
128 addi 14 0 2000
12c divu 15 15 14
130 addi 15 15 -2
132 jump 148
134 addi 15 0 39
138 jump 148
13a li 10 1
13c jr 1
''',
'role':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 store 2 8 8 4
006 jal 1 410498
00a lui 8 536883200
00e addi 10 8 1456
012 addi 12 0 36
016 li 11 0
018 auipc 1 536453120
01c jalr 1 1 496
020 lui 10 417792
024 li 15 -1
026 addi 10 10 -1526
02a store 8 15 1456 4
02e jal 1 277722
032 addi 8 8 1456
036 store 8 10 16 1
038 load 1 2 12 4
03a load 8 2 8 4
03c li 10 0
03e addi 2 2 16
040 jr 1
''',
'setup':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 262144
008 load 15 8 72 4
00a lui 12 4096
00c store 2 1 28 4
00e addi 12 12 -1972
012 li 11 0
014 auipc 10 536879104
018 addi 10 10 752
01c store 2 9 20 4
01e call_indirect 1 15
020 jal 1 104930
024 jal 1 105238
028 jal 1 36986
02a load 15 8 416 4
02e call_indirect 1 15
030 load 15 8 428 4
034 call_indirect 1 15
036 load 15 8 448 4
03a call_indirect 1 15
03c load 15 8 128 4
040 auipc 10 4294963200
044 addi 10 10 1868
048 call_indirect 1 15
04a store 3 10 157 1
04e li 15 6
050 store 2 15 12 2
054 addi 15 0 1000
058 store 2 15 14 2
05c load 15 8 372 4
060 auipc 12 69632
064 addi 12 12 -252
068 li 11 13
06a addi 10 0 774
06e call_indirect 1 15
070 load 15 8 372 4
074 addi 12 2 12
076 li 11 2
078 addi 10 0 785
07c call_indirect 1 15
07e load 15 8 372 4
082 addi 12 2 14
086 li 11 2
088 addi 10 0 786
08c call_indirect 1 15
08e load 15 8 340 4
092 addi 11 0 160
096 li 10 3
098 call_indirect 1 15
09a load 15 8 340 4
09e addi 11 0 160
0a2 li 10 4
0a4 call_indirect 1 15
0a6 li 10 1
0a8 jal 1 35694
0aa addi 15 3 84
0ae load 15 15 0 4
0b0 li 14 3
0b2 load 15 15 7 1
0b6 andi 15 15 3
0b8 beq 15 14 214
0bc auipc 14 73728
0c0 addi 14 14 -1040
0c4 add 15 15 14
0c6 load 11 15 0 1
0ca load 15 8 340 4
0ce li 10 25
0d0 slli 11 11 16
0d2 srli 11 11 16
0d4 call_indirect 1 15
0d6 lui 8 262144
0da store 2 0 14 1
0de load 15 8 360 4
0e2 addi 12 2 14
0e6 li 11 1
0e8 addi 10 0 1024
0ec call_indirect 1 15
0ee load 15 8 196 4
0f2 li 9 -2
0f4 call_indirect 1 15
0f6 load 15 8 128 4
0fa auipc 10 4294963200
0fe addi 10 10 1682
102 call_indirect 1 15
104 store 3 10 148 1
108 store 3 9 150 2
10c load 15 8 128 4
110 auipc 10 4294963200
114 addi 10 10 1660
118 call_indirect 1 15
11a store 3 10 152 1
11e store 3 9 154 2
122 load 15 8 312 4
126 lui 10 65536
128 addi 11 3 128
12c addi 10 10 -1
12e call_indirect 1 15
130 load 15 8 304 4
134 auipc 13 69632
138 addi 13 13 -448
13c li 12 16
13e li 11 4
140 addi 10 3 0
144 call_indirect 1 15
146 load 15 8 80 4
148 li 11 8
14a load 10 3 157 1
14e call_indirect 1 15
150 jal 1 75014
154 jal 1 95720
158 load 15 8 72 4
15a li 12 3
15c li 11 0
15e addi 10 3 144
162 call_indirect 1 15
164 load 15 8 128 4
168 auipc 10 0
16c addi 10 10 -878
170 call_indirect 1 15
172 load 1 2 28 4
174 load 8 2 24 4
176 store 3 10 144 1
17a load 9 2 20 4
17c addi 2 2 32
17e jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1bind literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1bind typedload signedness/encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1bind fullboundaries')
 for a,f in s.items():init.g(n,a,'B1bind '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1bind retained load/extension mnemonic')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1bind fullidentity')
 e={};calls=[];indirect=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1bind RET RA');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'B1bind ordinary linked JAL');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1bind adjacent callpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'B1bind indirect A5');indirect.append(dict(offset=a-pc,register=15))
  check(all(z in n for z in q),'B1bind closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and common.acyclic(e),'B1bind fullreachable DAG')
 expected={'config':[(0x32,0x2000039c),(0x44,0x20000332),(0xaa,0x20000110),(0xc6,0x20000040)],
  'role':[(6,0x64298+234*index),(0x1c,0x2000039c),(0x2e,0x43c4e+140*index)],
  'setup':[(0x20,0x199e2),(0x24,0x19b16),(0x28,0x907a),(0xa8,0x8b6e),(0x150,0x12506),(0x154,0x175e8)]}[part]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and len(indirect)==(20 if part=='setup' else 0),'B1bind allcalls')
 check(rets==[pc+o for o in {'config':[0xe0,0x13c],'role':[0x40],'setup':[0x17e]}[part]],'B1bind allreturns')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 frames={'config':{(9,4),(1,12),(8,8),(18,0)},'role':{(1,12),(8,8)},'setup':{(8,24),(1,28),(9,20)}}
 saved=[d for d in stores if d['base']==2 and d['source'] in {1,8,9,18}]
 check(len(saved)==len(frames[part]) and {(d['source'],d['imm']) for d in saved}==frames[part] and all(d['bytes']==4 for d in saved),'B1bind exactframe saves')
 if part=='config':
  expectedstores=[(0x58,8,15,25,1),(0x60,8,15,26,1),(0x68,8,15,27,1),(0x70,8,15,28,1),(0x78,8,15,29,1),(0x94,8,15,1,1),
   (0xb2,9,0,4,4),(0xca,9,10,4,4),(0xd0,9,15,15,1),(0xd4,9,15,20,4)]
  check([d for d in stores if d['base']!=2]==[dict(offset=o,base=r,source=v,imm=x,bytes=z) for o,r,v,x,z in expectedstores] and len(stores)==14,'B1bind config10nonframe/14total stores')
 elif part=='role':check(len(stores)==4 and [d['offset'] for d in stores if d['base']!=2]==[0x2a,0x36],'B1bind role context/task stores')
 else:
  check(len(stores)==12 and [(d['imm'],d['bytes']) for d in stores if d['base']==3]==[(157,1),(148,1),(150,2),(152,1),(154,2),(144,1)],'B1bind setup own GPstores')
  check([a-pc for a,d in n.items() if d.get('rd')==8]==[4,0xd6,0x174],'B1bind S0 table40000 untilrestore conditionaloncallees')
 return dict(start=pc,source=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,indirect_calls=indirect,tails=[],returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part=='role':return dict(all_normal_callees=common.walk(b,{}))
 if part=='setup':return {name:common.walk(b,{0xb8:target}) for name,target in [('optional_param25_skipped',0xd6),('optional_param25_included',0xbc)]}
 base={2:6,0x18:0x20,0x80:0x96,0xa4:0xae,0xb8:0xcc}
 actual={**base,0x52:0x5a,0x5c:0x5e,0x64:0x66,0x6c:0x6e,0x74:0x76,0xb8:0xba}
 choices={'callbackword0_reply1':{2:0x13a},'bit6_set_aux0_reply2':{2:6,0x18:0x1a,0x1e:0xd6},
  'APP_record_defaults_allocate_scalar_ignored':actual,'APP_record_oldcontext_release':{**actual,0xa4:0xa6},
  'all_defaults_localcopy_noalloc':base,
  'all_preset_localcopy_noalloc':{**base,0x52:0x5a,0x5c:0x62,0x64:0x6a,0x6c:0x72,0x74:0x7a},
  'channel_low_default37':{**base,0x80:0x82,0x8c:0x90},
  'channel_first_division':{**base,0x80:0x82,0x8c:0xe2,0xea:0xee},
  'channel_special38':{**base,0x80:0x82,0x8c:0xe2,0xea:0x104,0x108:0x10c},
  'channel_second_division':{**base,0x80:0x82,0x8c:0xe2,0xea:0x104,0x108:0x112,0x11a:0x11e},
  'channel_high_default39':{**base,0x80:0x82,0x8c:0xe2,0xea:0x104,0x108:0x112,0x11a:0x134}}
 ps={name:common.walk(b,choice) for name,choice in choices.items()}
 for name in ('callbackword0_reply1','bit6_set_aux0_reply2'):check(not set(ps[name])&{c['offset'] for c in b['calls']},'B1bind early rejects nochildren/publication')
 seq=ps['APP_record_defaults_allocate_scalar_ignored']
 check(seq.index(0x32)<seq.index(0x44)<seq.index(0xc6)<seq.index(0xca)<seq.index(0xce),'B1bind fill-copy-allocate-publish-forced0 order')
 check(0x58 not in seq and all(o in seq for o in (0x60,0x68,0x70,0x78)),'B1bind APPpreserves25/defaults26..29')
 return ps


def reachable(edges,start,blocked):
 seen=set();todo=[start]
 while todo:
  p=todo.pop()
  if p in seen or p in blocked:continue
  seen.add(p);todo.extend(edges[p])
 return seen


def domains():
 mask=0xffffffff;thresholds=(0x24b000-353,0x250000+1167,0x250000+1168,0x25d000+1919)
 t0,t1,t2,t3=thresholds;negative=(0xffdb6000-1744)&mask;offset=(-negative)&mask
 check(thresholds==(2403999,2425999,2426000,2479999) and offset==2402000 and t2==t1+1,'B1bind channel rawthresholds/subtract literal')
 intervals=((0,t0),(t0+1,t1),(t2,t2),(t2+1,t3),(t3+1,mask))
 check(sum(hi-lo+1 for lo,hi in intervals)==2**32 and all(intervals[j][1]+1==intervals[j+1][0] for j in range(4)),'B1bind fullU32 channel intervalpartition')
 counts=[0,0];seen={37,38,39}
 for lo,hi,adjust,k in ((t0+1,t1,1,0),(t2+1,t3,2,1)):
  for x in range(lo,hi+1):
   value=(((x+negative)&mask)//2000-adjust)&mask
   check((x+negative)&mask==x-offset and 0<=value<=36,'B1bind channel admitteddivision no wrapping');seen.add(value);counts[k]+=1
 check(counts==[22000,53999] and seen==set(range(40)),'B1bind channel intermediate cases/range')
 for flags in range(256):
  for aux_nonzero in (False,True):check((not(flags&64) or aux_nonzero)==(flags&64==0 or aux_nonzero),'B1bind firstaux guardscalar')
 check(0x2501&255==1 and 1&64==0 and 1&1==1 and 251+2==253,'B1bind actualAPP flags/allocation size')
 protected=set(range(16,20));defaults={25,26,27,28,29};direct_fields=defaults|{1}
 check(protected.isdisjoint(direct_fields) and len(protected)==4 and 32+4>max(protected),'B1bind configcallback disjointlocaldefaults/context')
 for index in range(2):
  F=0x20003540+80*index;C=F+32;slot=F+16
  check(slot==0x20003550+80*index and F<=slot and slot+4<=F+32 and C==F+32,'B1bind copyrecord/callback/rolecontext adjacency')
  check(set(range(slot,slot+4)).isdisjoint(range(C,C+36)),'B1bind rolefill36 doesnotclear callback')
 callback=0x174ee;octets=[(callback>>(8*j))&255 for j in range(4)]
 check(octets==[238,116,1,0] and sum(v<<(8*j) for j,v in enumerate(octets))==callback,'B1bind callback littleendian lanes')
 check(set(range(32)).isdisjoint(range(36,48)) and set(range(16,20))<=set(range(32)),'B1bind constructorrecord/saveframe intervals')
 return dict(channel_thresholds=thresholds,channel_U32_intervals=intervals,channel_division_cases=75999,channel_possible_values=list(range(40)),physical_channel_units_proved=False,
  initial_flag_aux_scalar_cases=512,actual_APP_record_flags_byte=1,actual_APP_callback=callback,callback_littleendian_bytes=octets,
  actual_APP_conditional_defaults={25:4,26:8,27:17,28:251,29:251},actual_APP_conditional_allocate_request=[253,73],
  callback_publication='clear32 thenforwardcopy32;callback4 bytes sequential,not atomicpointerpublicationproof',target_execution_or_emulation=False)


def profile(image,data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  pc=STARTS[index][k];raw=image[pc-0x8000:pc-0x8000+SIZES[k]] if part=='setup' else init.binding.take(data,pc,SIZES[k])
  if part!='setup':check(sparse.captured(mem,pc,SIZES[k])==raw,'B1bind fullcandidate originalHEX')
  bs[part]=body(raw,part,index)
 n={part:{d['pc']-b['start']:d for d in b['instructions']} for part,b in bs.items()};cfg,role,setup=n['config'],n['role'],n['setup']
 F=0x20003540+80*index;C=F+32;callback_slot=F+16
 check(cfg[0x20]['imm']+cfg[0x2a]['imm']==F and cfg[0x3c]['imm']==cfg[0x2a]['imm'] and cfg[0x96]['imm']+cfg[0x9a]['imm']==C,'B1bind configrecord/context addresses')
 check(cfg[0]['imm']==16 and cfg[0x14]['imm']==64 and cfg[0x24]['imm']==cfg[0x36]['imm']==32 and cfg[0x3a]['rs2']==9,'B1bind callback/aux/fillcopy arguments')
 check([cfg[o]['imm']&255 for o in (0x54,0x5e,0x66,0x6e,0x76)]==[40,8,17,251,251] and cfg[0xba]['imm']==29 and cfg[0xc0]['imm']==2 and cfg[0xbc]['imm']==73,'B1bind defaults/freshcfg29 allocator')
 check(cfg[0xce]['imm']==0 and cfg[0x13a]['imm']==1 and cfg[0x1c]['imm']==2 and cfg[0xca]['rs2']==10,'B1bind three localstatuses/no allocationnullguard')
 check(role[0xa]['imm']+role[0xe]['imm']==C and role[0x12]['imm']==36 and role[0x24]['imm']==-1 and role[0x36]['imm']==16 and role[0x3c]['imm']==0,'B1bind role clears36/contextFFF/taskbyte/forced0')
 task_callback=role[0x20]['imm']+role[0x26]['imm'];check(task_callback==0x65920+234*index,'B1bind task registration callback value')
 slots=init.binding.take(data,0x401c0,8);check(sparse.captured(mem,0x401c0,8)==slots,'B1bind rawAPI table slots originalHEX')
 check(int.from_bytes(slots[:4],'little')==bs['role']['start'] and int.from_bytes(slots[4:],'little')==bs['config']['start'],'B1bind candidate role/config table identity')
 check(setup[4]['imm']==0x40000 and setup[0x36]['imm']==448 and setup[0x6a]['imm']==774 and setup[0x154]['target']==0x175e8,'B1bind actualAPP slot401c0/param774/constructor joins')
 e=bs['setup']['CFG'];entry=bs['setup']['start'];ctor=entry+0x154
 for off in (0x3a,0x6e):check(ctor not in reachable(e,entry,{entry+off}),'B1bind earlierrole/param774 dominateconstructor onnormalcall edges')
 for seq in paths(bs['setup'],'setup').values():check(seq.index(0x3a)<seq.index(0x6e)<seq.index(0x154),'B1bind bothsetup paths encodedorder')
 detail=next(d for d in consumers.DETAILS if d[0]=='constructor');_,cp,z,count,stores,digest=detail
 ctorbody=consumers.body(consumers.take(image,cp,z),'constructor',cp,z,count,stores,digest);cn={d['pc']-cp:d for d in ctorbody['instructions']}
 check(cp+92+cn[92]['imm']+cn[96]['imm']==0x174ee and cn[100]['imm']==16 and cn[108]['imm']==452 and cn[112]['rs2']==2,'B1bind realAPP callbackSP16 and401c4(SP)')
 check(cn[82]['imm']+cn[84]['imm']==0x2501 and cn[88]['width']==2 and cn[102]['imm']==4 and cn[104]['imm']==25,'B1bind APP recordflag/byte25 constants')
 # Reuse already complete fill/copy contracts and conditional first-copy mapping.
 cmod=callees
 check(cmod.PARTS==('poolfind','output','veneer','check3'),'B1bind selected existingleaf proof module')
 f=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];reuse={}
 for name,target,length in [('fill',0x2000039c,46),('copy',0x20000332,58)]:
  src=int(f['source'],16)+target-int(f['destination'],16);r=init.binding.take(data,src,length)
  check(sparse.captured(mem,src,length)==r,'B1bind reusedleaf originalHEX')
  if name=='fill':cmod.previous.previous.fill_source.fill_contract(r)
  else:cmod.previous.copier.body(r,'copy',target,18,init.binding.COPY_HASH)
  reuse[name]=dict(source=src,target=target,bytes=length,sha256=sha256(r).hexdigest(),new_code_bytes_counted=0,installed_binding_proved=False)
 rfstart=parent['reused_command']['start'];rn={d['pc']-rfstart:d for d in parent['reused_command']['instructions']}
 check(0x20003000+rn[0x42]['imm']==callback_slot,'B1bind RF consumer callback slot exactwriter join')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},reused_constructor=ctorbody,reused_leaves=reuse,
  globals=dict(config=F,context=C,callback_word=callback_slot),candidate_API_slots={'401c0':bs['role']['start'],'401c4':bs['config']['start']},
  config_contract=['firstinputword16read before inputpointer/nullguard;callbackword0 ->1 withoutframe/children. Nonzero ->16Bframe;freshbyte0bit6set andfreshword4zero ->2 beforepublication',
   'fill(F,0,32),copy(F,original_input,32),ignore replies. Fivefreshbytezero guards defaultF25..29 to40/8/17/251/251;laterfreshoriginalinputbyte0bit6 mayenable numericchannelwriteF1 fromfreshF4',
   'oldfreshC4nonnull ->private-release(oldpointer),ignore reply;freshF0sample,SW0C4;samplebit0set ->allocate(2+freshU8F29,73),SWreturnedpointerC4 withoutnullcheck',
   'freshF1->C15,freshF8->C20,return0 evenifallocation0. Directpostcopy storesdonotoverlapF16..19;privatefree/allocator alias/retention effectsremainunproved'],
  role_contract=['firstdirectcallpublicationparent64298/64382 includingits tail mustnormallyreturn;thenfill(C,0,36),SWFFFFFFFF C0,registertask65920/65a0a,SB low8replyC16,return0',
   'C36clear disjointfromconfigF32/callbackwordF16;roleinitdoesnotlocallyclear RFcallbackword. Unknownpubtail/registration callees maywrite elsewhere'],
  APP_order_contract=['complete8e88setup:underS0table40000 preservation,fresh401c0 call8ec2 precedesparam774call8ef6 anddirect175e8call8fdc;earliercalls dominateconstructor inconditionalnormal-returnCFG',
   'singlelocalbranch8f40 onlyskipsoptionalparam25call8f5c andjoins8f5e;bothpaths retainrole->param774->constructor order;not an observedboot orcallee-returnproof',
   '175e8 builds32B record in48Bframe,callback174ee atSP16,SH2501SP0,SB4SP25 aftermatchingfill32;fresh401c4(SP) occurswhileframe live,thenconstructor restoresframe',
   'ifstableAPPframe/referencehelpers/normalcallees,configadmitsflag1/callback174ee,defaults25..29=4,8,17,251,251;requestedallocation253/tag73. Actualconfigreturn0 doesnotproveallocation orbinding success'],
  lifetime_contract=['candidatefill32 clearscallbackword beforecopy32 publishesfourlittleendian callbackbytes16..19 sequentially;no atomicpublication or concurrentconsumer exclusionproof',
   'originalAPP stackrecord pointer borrowedbyconfig;copycandidate writesbyvalue,postcopylocalcode retainsnooriginalinputpointer in globals. Ambientregisters/unknownlatecallees maystillretainit',
   'thisspecificlaterconstructor publicationcannotretroactivelysupplyearlierroleinit callbacks inthesameorderedinvocation;earliercallbackwordneednotzero:priorinitialization/otherwriters/indirectentries remainpossible',
   'F16 callback atB1 RFcall dependsactual401c4/provider/RAMbinding,copyvalidity,alllaterwriters/order/IRQ/DMA/reentry preservation;freshRF state3 notinheritedfromsourceinitialstate1'],
  premises='conditionalcandidateISA/API/firstcopymapping/providerbinding;validcode/frame/config/context/sourceextents;ordinarycalleeS/SP/RA/framepreservation;GP-dependentstoreaddresses notassumed;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalities separate',
  actual_installed_binding_boot_order_source_pointer_nonescape_or_complete_callback_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-RF-config-publication-order-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_unique_body_bytes=1152,complete_phase_unique_body_instructions=394,APP_setup_counted_once=True,reused_constructor_bytes=126,reused_fill_copy_bytes=208,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['callback174ee consumer timing andother RFconfig callers/writers','latercallback/globalpointer preservation andactualinstalledAPI/RAMbinding','fullsource/heap/callback lifetime andinitialization reentry'])


def tests(image,carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   if part=='setup' and i==1:continue
   pc=STARTS[i][k];raw=image[pc-0x8000:pc-0x8000+SIZES[k]] if part=='setup' else init.binding.take(data,pc,SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,pc).items():
    o=a-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1bind instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1bind typedmutation escaped')
    typed+=1
 check((mutations,typed)==(394,22),'B1bind uniqueinstruction/typed census');domains()
 print('PASS:394 instruction/22 typed-load mutations rejected;75999 channel scalars;512 guardcases;callback/frame/order certificates')


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
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers)
 encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'B1bind exactledger replay')
 print('PASS:1152B/394i unique complete RFconfig/role/APPsetup;strict HEX;callback174ee source andconditionalorder;exact ledger')
 print('PASS:NO target execution/emulation;actualbinding/boot/concurrentpublication/completepointerlifetime UNPROVED')


if __name__=='__main__':main()
