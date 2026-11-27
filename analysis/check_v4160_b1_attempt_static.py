"""Offline complete RF attempt helper and request128 contracts.
Original operands, immutable CFG paths and host scalar certificates only.
No target execution/emulation, mutable state model or hardware access.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_request_config_static as previous
import check_v4160_hook_lifetime_static as hook
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-attempt-static.json')
STARTS=(0x64794,0x6487e)
SIZE=502
HASHES=('a6cca690a5d804d47ba120b8036611fafcab9feecc11cf94898541b1959df398', '124fa3f989acf2bd4b495952914b0783ba70094c33bca9fae85cb2d524d035d7')
COUNTS=(175, 175)
TYPED=(((70, 2), (84, 2), (122, 2), (154, 2), (164, 2), (252, 2), (292, 2), (300, 2), (330, 4), (342, 2), (358, 2), (412, 2), (422, 4), (434, 2), (470, 2), (490, 4)), ((70, 2), (84, 2), (122, 2), (154, 2), (164, 2), (252, 2), (292, 2), (300, 2), (330, 4), (342, 2), (358, 2), (412, 2), (422, 4), (434, 2), (470, 2), (490, 4)))
QK=(((56, '3c2c', 'qk.c.lbu'), (112, '0830', 'qk.c.lbu'), (202, '7c27', 'qk.c.lbu'), (212, '7ca7', 'qk.c.sb'), (238, '04b1', 'qk.c.sb'), (274, '78b0', 'qk.c.sb')), ((56, '3c2c', 'qk.c.lbu'), (112, '0830', 'qk.c.lbu'), (202, '7c27', 'qk.c.lbu'), (212, '7ca7', 'qk.c.sb'), (238, '04b1', 'qk.c.sb'), (274, '78b0', 'qk.c.sb')))
LITERALS=(
'''
000 addi 2 2 -64
002 store 2 9 52 4
004 store 2 22 32 4
006 store 2 23 28 4
008 store 2 1 60 4
00a store 2 8 56 4
00c store 2 18 48 4
00e store 2 19 44 4
010 store 2 20 40 4
012 store 2 21 36 4
014 addi 15 0 128
018 mv 23 10
01a mv 9 11
01c mv 22 12
01e bne 12 15 80
022 lui 8 536883200
026 li 18 15
028 addi 8 8 1344
02c auipc 1 536469504
030 jalr 1 1 1420
034 bgeu 18 10 44
038 load 15 8 26 1
03a slli 15 15 5
03c addi 15 15 -16
03e bltu 15 10 44
042 lui 15 536883200
046 load 15 15 1340 4
04a addi 14 0 160
04e store 15 14 100 4
050 lui 20 536883200
054 load 14 20 1288 4
058 lui 21 536883200
05c addi 8 21 1344
060 load 15 14 44 4
062 li 11 0
064 lui 19 536883200
068 andi 15 15 -4
06a ori 15 15 1
06e store 14 15 44 4
070 load 10 8 1 1
072 lui 18 536883200
076 jal 1 410442
07a load 15 20 1288 4
07e lui 12 3342336
082 load 14 15 0 4
084 andi 14 14 -385
088 store 15 14 0 4
08a load 14 15 0 4
08c andi 14 14 -385
090 ori 14 14 256
094 store 15 14 0 4
096 lui 14 536883200
09a load 13 14 1424 4
09e load 14 13 8 4
0a0 or 14 14 12
0a2 store 13 14 8 4
0a4 load 14 19 1340 4
0a8 addi 13 0 90
0ac store 14 13 80 4
0ae load 13 8 8 4
0b0 store 15 13 8 4
0b2 load 13 8 12 4
0b4 lui 8 536883200
0b8 addi 8 8 1300
0bc store 15 13 4 4
0be load 15 14 4 4
0c0 ori 15 15 1
0c4 store 14 15 4 4
0c6 addi 14 18 1376
0ca load 15 14 14 1
0cc addi 18 18 1376
0d0 ori 15 15 2
0d4 store 14 15 14 1
0d6 addi 15 22 -1
0da andi 15 15 255
0de li 14 1
0e0 bltu 14 15 396
0e4 load 10 8 32 4
0e6 mv 12 9
0e8 mv 11 23
0ea store 10 22 0 1
0ee store 10 9 1 1
0f0 addi 10 10 2
0f2 auipc 1 536461312
0f6 jalr 1 1 -1364
0fa load 14 8 32 4
0fc load 15 19 1340 4
100 slli 11 9 16
104 srli 11 11 16
106 store 15 14 112 4
108 store 8 0 2 1
10c li 14 3
10e store 8 0 3 1
112 store 8 14 7 1
114 addi 14 0 128
118 bne 22 14 422
11c load 14 15 100 4
11e bnez 14 284
120 lui 15 536883200
124 load 15 15 480 4
128 store 2 11 12 4
12a call_indirect 1 15
12c load 14 18 8 4
130 load 11 2 12 4
132 bltu 10 14 408
136 sub 10 10 14
138 load 15 8 32 4
13a lui 9 8388608
13e srli 10 10 3
140 addi 14 9 767
144 slli 10 10 24
146 or 10 10 14
148 store 15 10 0 4
14a load 10 21 1344 1
14e srai 10 10 4
150 andi 10 10 3
152 jal 1 408334
156 load 15 20 1288 4
15a load 14 15 0 4
15c or 14 14 9
15e store 15 14 0 4
160 load 14 15 44 4
162 andi 14 14 -4
164 store 15 14 44 4
166 load 15 19 1340 4
16a store 8 0 5 1
16e store 8 0 1 1
172 li 14 2
174 store 15 14 0 4
176 load 1 2 60 4
178 load 8 2 56 4
17a load 9 2 52 4
17c load 18 2 48 4
17e load 19 2 44 4
180 load 20 2 40 4
182 load 21 2 36 4
184 load 22 2 32 4
186 load 23 2 28 4
188 addi 2 2 64
18a jr 1
18c addi 15 0 128
190 bne 22 15 250
194 li 9 2
196 jump 250
198 lui 15 536883200
19c load 15 15 568 4
1a0 sub 15 15 14
1a2 add 10 10 15
1a4 jump 312
1a6 load 10 21 1344 1
1aa srai 10 10 4
1ac andi 10 10 3
1ae jal 1 408334
1b2 load 15 20 1288 4
1b6 lui 13 8388608
1ba lui 10 417792
1be load 14 15 0 4
1c0 addi 10 10 -538
1c4 or 14 14 13
1c6 store 15 14 0 4
1c8 load 14 15 44 4
1ca andi 14 14 -4
1cc store 15 14 44 4
1ce auipc 1 536461312
1d2 jalr 1 1 -472
1d6 load 15 19 1340 4
1da store 18 0 12 1
1de store 8 0 5 1
1e2 store 8 0 1 1
1e6 li 14 2
1e8 store 15 14 0 4
1ea load 15 18 12 1
1ee andi 15 15 255
1f2 beqz 15 490
1f4 jump 374
''',
'''
000 addi 2 2 -64
002 store 2 9 52 4
004 store 2 22 32 4
006 store 2 23 28 4
008 store 2 1 60 4
00a store 2 8 56 4
00c store 2 18 48 4
00e store 2 19 44 4
010 store 2 20 40 4
012 store 2 21 36 4
014 addi 15 0 128
018 mv 23 10
01a mv 9 11
01c mv 22 12
01e bne 12 15 80
022 lui 8 536883200
026 li 18 15
028 addi 8 8 1424
02c auipc 1 536469504
030 jalr 1 1 1262
034 bgeu 18 10 44
038 load 15 8 26 1
03a slli 15 15 5
03c addi 15 15 -16
03e bltu 15 10 44
042 lui 15 536883200
046 load 15 15 1420 4
04a addi 14 0 160
04e store 15 14 100 4
050 lui 20 536883200
054 load 14 20 1368 4
058 lui 21 536883200
05c addi 8 21 1424
060 load 15 14 44 4
062 li 11 0
064 lui 19 536883200
068 andi 15 15 -4
06a ori 15 15 1
06e store 14 15 44 4
070 load 10 8 1 1
072 lui 18 536883200
076 jal 1 410676
07a load 15 20 1368 4
07e lui 12 3342336
082 load 14 15 0 4
084 andi 14 14 -385
088 store 15 14 0 4
08a load 14 15 0 4
08c andi 14 14 -385
090 ori 14 14 256
094 store 15 14 0 4
096 lui 14 536883200
09a load 13 14 1504 4
09e load 14 13 8 4
0a0 or 14 14 12
0a2 store 13 14 8 4
0a4 load 14 19 1420 4
0a8 addi 13 0 90
0ac store 14 13 80 4
0ae load 13 8 8 4
0b0 store 15 13 8 4
0b2 load 13 8 12 4
0b4 lui 8 536883200
0b8 addi 8 8 1380
0bc store 15 13 4 4
0be load 15 14 4 4
0c0 ori 15 15 1
0c4 store 14 15 4 4
0c6 addi 14 18 1456
0ca load 15 14 14 1
0cc addi 18 18 1456
0d0 ori 15 15 2
0d4 store 14 15 14 1
0d6 addi 15 22 -1
0da andi 15 15 255
0de li 14 1
0e0 bltu 14 15 396
0e4 load 10 8 32 4
0e6 mv 12 9
0e8 mv 11 23
0ea store 10 22 0 1
0ee store 10 9 1 1
0f0 addi 10 10 2
0f2 auipc 1 536461312
0f6 jalr 1 1 -1598
0fa load 14 8 32 4
0fc load 15 19 1420 4
100 slli 11 9 16
104 srli 11 11 16
106 store 15 14 112 4
108 store 8 0 2 1
10c li 14 3
10e store 8 0 3 1
112 store 8 14 7 1
114 addi 14 0 128
118 bne 22 14 422
11c load 14 15 100 4
11e bnez 14 284
120 lui 15 536883200
124 load 15 15 560 4
128 store 2 11 12 4
12a call_indirect 1 15
12c load 14 18 8 4
130 load 11 2 12 4
132 bltu 10 14 408
136 sub 10 10 14
138 load 15 8 32 4
13a lui 9 8388608
13e srli 10 10 3
140 addi 14 9 767
144 slli 10 10 24
146 or 10 10 14
148 store 15 10 0 4
14a load 10 21 1424 1
14e srai 10 10 4
150 andi 10 10 3
152 jal 1 408568
156 load 15 20 1368 4
15a load 14 15 0 4
15c or 14 14 9
15e store 15 14 0 4
160 load 14 15 44 4
162 andi 14 14 -4
164 store 15 14 44 4
166 load 15 19 1420 4
16a store 8 0 5 1
16e store 8 0 1 1
172 li 14 2
174 store 15 14 0 4
176 load 1 2 60 4
178 load 8 2 56 4
17a load 9 2 52 4
17c load 18 2 48 4
17e load 19 2 44 4
180 load 20 2 40 4
182 load 21 2 36 4
184 load 22 2 32 4
186 load 23 2 28 4
188 addi 2 2 64
18a jr 1
18c addi 15 0 128
190 bne 22 15 250
194 li 9 2
196 jump 250
198 lui 15 536883200
19c load 15 15 648 4
1a0 sub 15 15 14
1a2 add 10 10 15
1a4 jump 312
1a6 load 10 21 1424 1
1aa srai 10 10 4
1ac andi 10 10 3
1ae jal 1 408568
1b2 load 15 20 1368 4
1b6 lui 13 8388608
1ba lui 10 417792
1be load 14 15 0 4
1c0 addi 10 10 -304
1c4 or 14 14 13
1c6 store 15 14 0 4
1c8 load 14 15 44 4
1ca andi 14 14 -4
1cc store 15 14 44 4
1ce auipc 1 536461312
1d2 jalr 1 1 -706
1d6 load 15 19 1420 4
1da store 18 0 12 1
1de store 8 0 5 1
1e2 store 8 0 1 1
1e6 li 14 2
1e8 store 15 14 0 4
1ea load 15 18 12 1
1ee andi 15 15 255
1f2 beqz 15 490
1f4 jump 374
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'attempt literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'attempt fullboundaries')
 for a,f in s.items():init.g(n,a,'attempt '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'attempt typedload')
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'attempt QK raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'attempt fullidentity')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'attempt RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'attempt no unlinkedtail');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','attempt adjacentpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'attempt indirectlink');calls.append(dict(offset=a-pc,target='freshU32[clockslot];no nullguard'))
  check(all(z in n for z in q),'attempt closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 cuts={(0x34,0x2c),(0x3e,0x2c),(0x11e,0x11c),(0x1f2,0x1ea)}
 cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in e.items()}
 check(seen==set(n) and not common.acyclic(e) and common.acyclic(cut) and rets==[pc+0x18a],'attempt reachability/soleRET/fourcyclecuts')
 expected=[(0x30,0x20002d4c+76*index),(0x76,0x6434a+234*index),(0xf6,0x20000332),(0x12a,'freshU32[clockslot];no nullguard'),(0x152,0x63b0e+234*index),(0x1ae,0x63b0e+234*index),(0x1d2,0x2000078a)]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'attempt all7calls')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 frame=[(2,2,9,52,4),(4,2,22,32,4),(6,2,23,28,4),(8,2,1,60,4),(10,2,8,56,4),(12,2,18,48,4),(14,2,19,44,4),(16,2,20,40,4),(18,2,21,36,4),(0x128,2,11,12,4)]
 other=[(0x4e,15,14,100,4),(0x6e,14,15,44,4),(0x88,15,14,0,4),(0x94,15,14,0,4),(0xa2,13,14,8,4),(0xac,14,13,80,4),(0xb0,15,13,8,4),(0xbc,15,13,4,4),(0xc4,14,15,4,4),(0xd4,14,15,14,1),(0xea,10,22,0,1),(0xee,10,9,1,1),(0x106,15,14,112,4),(0x108,8,0,2,1),(0x10e,8,0,3,1),(0x112,8,14,7,1),(0x148,15,10,0,4),(0x15e,15,14,0,4),(0x164,15,14,44,4),(0x16a,8,0,5,1),(0x16e,8,0,1,1),(0x174,15,14,0,4),(0x1c6,15,14,0,4),(0x1cc,15,14,44,4),(0x1da,18,0,12,1),(0x1de,8,0,5,1),(0x1e2,8,0,1,1),(0x1e8,15,14,0,4)]
 check([d for d in stores if d[1]==2]==frame and [d for d in stores if d[1]!=2]==other,'attempt all38stores')
 check([a-pc for a,d in n.items() if d.get('rd')==22]==[0x1c,0x184] and [a-pc for a,d in n.items() if d.get('rd')==23]==[0x18,0x186],'attempt fullentrymode/input saved')
 return dict(start=pc,bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,returns=rets,tails=[],stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 base={0x1e:0x22,0x34:0x38,0x3e:0x42,0xe0:0x18c,0x190:0x194,0x118:0x11c,0x11e:0x120,0x132:0x136}
 out={'request128_direct_delta':common.walk(b,base),'request128_wrapped_delta':common.walk(b,{**base,0x132:0x198})}
 alt={0x1e:0x50,0xe0:0xe4,0x118:0x1a6,0x1f2:0x1f4}
 out['non128_lowbyte1or2_copy']=common.walk(b,alt)
 out['non128_other_bypasscopy']=common.walk(b,{**alt,0xe0:0x18c,0x190:0xfa})
 for name,seq in out.items():
  check(seq[-1]==0x18a and all(o in seq for o in (0x76,0x106,0x108,0x10e,0x112)),'attempt commoncalls/publication/framepath')
  if name.startswith('request128'):
   check(all(o not in seq for o in (0xe4,0xea,0xee,0xf6,0x1ae,0x1d2,0x1da,0x1ea)) and all(o in seq for o in (0x30,0x4e,0x194,0x11c,0x12a,0x128,0x130,0x148,0x152)),'attempt request128 bypasscopy/alternatepoll')
   n={d['pc']-b['start']:d for d in b['instructions']};j=seq.index(0x152)
   check(not any(n[o].get('rd')==10 for o in seq[j+1:]),'attempt finalchannel scalar notoverwritten')
   check(seq.index(0x106)<seq.index(0x11c)<seq.index(0x12a)<seq.index(0x148)<seq.index(0x152)<seq.index(0x174),'attempt pointerpoll/clock/packet/cleanup order')
  else:check(0x30 not in seq and 0x12a not in seq and 0x1d2 in seq and 0x1ea in seq,'attempt non128 setter/latchwait')
 return out


def domains():
 bounds=[]
 for x in range(256):
  limit=((x<<5)-16)&0xffffffff
  for sample in {0,1,15,16,17,limit,(limit-1)&0xffffffff,(limit+1)&0xffffffff,0xffffffff}:
   accepted=sample>15 and sample<=limit
   check(accepted==(16<=sample<=limit),'attempt unsigned admission interval')
  bounds.append(dict(flag_byte=x,limit=limit,accepted_integer_count=max(0,limit-15)))
 check(bounds[0]['limit']==0xfffffff0 and bounds[0]['accepted_integer_count']==4294967265 and bounds[1]['limit']==16 and bounds[255]['limit']==8144,'attempt underflow/singlepoint/maxbyte admission')
 short=[x for x in range(65536) if ((x-1)&255)<=1]
 check(len(short)==512 and short[:4]==[1,2,257,258] and 128 not in short,'attempt lowbytecopy vsfull128 predicates')
 check((128-1)&255==127 and 127>1 and (2<<16)>>16==2,'attempt request savedA1 forced2')
 for d in range(65536):check((((d>>3)<<24)|0x008002ff)&0xffffffff==((((d&2047)>>3)<<24)|0x008002ff),'attempt projected timestamp bits3..10')
 for t in (0,1,15,16,255,0x7fffffff,0xffffffff):
  for b in (0,1,16,0x7fffffff,0xffffffff):
   for m in (0,1,255,0xffffffff):
    v=(t-b if t>=b else t+m-b)&0xffffffff
    check(v==((t-b)&0xffffffff if t>=b else (t+m-b)%2**32),'attempt one-wrapform mod32;no +1')
 return dict(admission_byte_cases=256,admission_boundaries=bounds,copy_gate_low16_cases=65536,copy_gate_hits=512,
  timestamp_delta_cases=65536,timestamp_formula='low32(((D>>3)<<24) OR008002FF);D=T-B ifunsignedT>=B else low32(T+freshM-B);no +1',
  target_execution_or_emulation=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE)
 check(sparse.captured(mem,STARTS[index],SIZE)==raw,'attempt strict originalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;F=G+1344+80*index;S=G+1300+80*index;C=G+1376+80*index;Hslot=G+1340+80*index;Rslot=G+1288+80*index
 check(n[0x22]['imm']+n[0x28]['imm']==F and n[0x58]['imm']+n[0x5c]['imm']==F and n[0xb4]['imm']+n[0xb8]['imm']==S and n[0x72]['imm']+n[0xcc]['imm']==C,'attempt F/S/Csources')
 check(n[0x42]['imm']+n[0x46]['imm']==Hslot and n[0x50]['imm']+n[0x54]['imm']==Rslot and n[0x120]['imm']+n[0x124]['imm']==G+480+80*index and n[0x198]['imm']+n[0x19c]['imm']==G+568+80*index,'attempt freshH/R/clock/modulus sources')
 check(n[0x26]['imm']==15 and n[0x38]['imm']==26 and n[0x3a]['imm']==5 and n[0x3c]['imm']==-16 and n[0x4a]['imm']==160 and n[0xa8]['imm']==90 and n[0x194]['imm']==2,'attempt sampler/request constants')
 check(n[0x13a]['imm']+n[0x140]['imm']==0x008002ff and n[0x13e]['imm']==3 and n[0x144]['imm']==24 and n[0x7e]['imm']==0x330000,'attempt timestamp/control constant operands')
 caller=previous.previous.previous;pc=caller.STARTS[index][1];request=caller.body(init.binding.take(data,pc,328),'request',index)
 check(sparse.captured(mem,pc,328)==init.binding.take(data,pc,328),'attempt callerstrictHEX')
 rn={d['pc']-pc:d for d in request['instructions']}
 check(next(c['target'] for c in request['calls'] if c['offset']==0x7c)==STARTS[index] and rn[0x72]['imm']==128 and rn[0x76]['imm']==rn[0x78]['imm']==0,'attempt actual requesttuple join')
 source,delta,digest,_=hook.DETAILS[index];setterraw=init.binding.take(data,source,22)
 check(sparse.captured(mem,source,22)==setterraw,'attempt setter originalHEX');setter=hook.body(setterraw,'setter',0x2000078a,delta,digest)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy']
 check(int(first['source'],16)+0x2000078a-int(first['destination'],16)==source and 0x2000078a+22<=int(mapping['first_copy_end_exclusive'],16),'attempt setter firstcopy affine mapping')
 check(n[0x1ba]['imm']+n[0x1c0]['imm']==0x65de6+234*index,'attempt non128 callbackliteral')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),reused_request=dict(start=pc,bytes=328,new_code_bytes_counted=0),
  reused_setter=setter,setter_source=source,nominal_globals=dict(config=F,status=S,context=C,H_pointer_slot=Hslot,R_pointer_slot=Rslot,clockslot=G+480+80*index,moduluslike_word=G+568+80*index),
  request128_contract=['saveentryA0/A1/A2 inS7/S1/S6;full128 ->repeatedRAMsampler20002d4c/20002d98;unsignedR<=15 retry,else freshF26 boundlow32(32*byte-16);R>boundretry;byte0underflowsFFFFfff0;no timeout',
   'accepted ->freshH word100=160;common6434a/64434(freshF1,0,thenliveA2);R44low2set1;twoindependentR0reads masked-385 thenOR256;descriptorword8OR330000;freshH80=90;R8=F8,R4=F12;H4OR1;freshC14OR2',
   'low8(mode-1)<=1 alone enables header/copy;full128 excludesit,doesnotlocallydereferencenull entryA0here. Full128 forcesS1=2;freshS32 pointer ->freshH112,clearS2/S3,S7=3',
   'heldH capturedat+fc polledatword100 until0,noHslotreloadinside;freshclockslot indirectcall no nullguard;A1=2 spilledSP12 thenreloaded;freshC8 baseline/fullunsigned clockreply T',
   'T>=B:D=T-B;elseD=low32(T+freshM-B),no+1;freshS32pointer word0=low32(((D>>3)<<24)|008002FF). Not physicaltime units/monotonicity',
   'call63b0e/63bf8(freshF0bits4..5,A1=2,thenliveA2);laterfreshR0OR00800000,R44low2clear;clearS5/S1;freshH0=2;restoreframe,RETthenliveA0 oflastchannelhelper,notforced0'],
  other_mode_contract=['non128 bypassesadmissionsampler;copygate low8(mode-1)<=1 includes257/258 etc,notonlyfull1/2;headerbytes mode/entryA1 thenRAMcopy(P+2,entryA0,entryA1)',
   'non128 aftercommon publication ->channelhelper;controlbit23set/low2clear;RAM2000078a(callbackliteral65de6/65ed0);directclearC12,S5,S1,H0=2;waitfreshC12nonzero,thenRET',
   'matchedcandidate setter storescallbackliteral to20002ef8/20002f48 and1toflag+4;no directC12write/progressguarantee. Setter leavesA0literal;actualinstalledbinding/callbackconsumer outsidephase'],
  premises='conditionalcandidateISA/API/mapping;validcode/frame/global/dynamicobject/payloadextents;ordinarycalleeS/SP/RA/spills preservation;no adversealias/wrap/IRQ/DMA/reentry;eachsnapshot equalityseparate',
  actual_binding_sampler_or_clock_semantics_pollprogress_pointer_retention_and_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-attempt-request128-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=1004,complete_phase_body_instructions=350,reused_request_bytes=656,reused_setter_bytes=44,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['RAMadmissionsampler,6434a/64434,63b0e/63bf8 completecontracts andclockbinding','callback65de6/65ed0 andC12writers/progress','actualinstalledproviders andfullpointer/frameborrow lifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('attempt instruction mutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('attempt typed mutation escaped')
   typed+=1
 check((mutations,typed)==(350,32),'attempt mutationcensus');domains()
 print('PASS:350 instruction/32 typed-load mutations rejected;256 admission bytes/65536 copygate modes/65536 deltas;CFG/frame/call/store certificates')


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
 else:check(OUT.read_bytes()==encoded,'attempt exactledger replay')
 print('PASS:1004B/350i complete attempt helper;strict HEX;request128 andsetter joins;exactledger')
 print('PASS:NO target execution/emulation;binding/clock/sampler/pollprogress/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
