"""Offline B1 update dispatch, flag writer and callback notification.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation or provider/RAM/NV/callback/heap model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_task_route_static as previous
import check_v4160_n136_predicate_static as predicate
import check_v4160_config_buffer_source_static as fill_source
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-downstream-static.json')
PARTS=('dispatch','update','notify')
STARTS=((0x6c042,0x6b83e,0x44310),(0x6c226,0x6ba22,0x443a4))
SIZES=(132,234,76)
HASHES=(('298c44d066a0dd6beda671dd54b708315203f722ce6bb1deab26805f8f8bf2f3', '07cc6e160cac7386259c6a24f8c01c7a58a6e273db2d7b6f52cc9933ce003ec6', 'ff234764266498871b46f3f4bcea032559f5f0a23821d101d6d7d1586cb33dd7'), ('bacf9b7cefafe982fd81d29d54d1c28b94fb7a81af36bb57d7fbdb25d917e2f5', '8953725e234c5bf0c41597da60af6c896b0c10ebeb5a25d451f3a3b319c42692', 'f470dcdfe4c91c86a33d8e4a0f4472a2621ba2565fe697487684156c43a5e7d0'))
COUNTS=((52, 87, 29), (52, 87, 29))
QK=({'dispatch': ((42, '4831', 'qk.c.lbu'),), 'update': ((182, '8e22', 'qk.c.lhu'), (200, '9623', 'qk.c.lhu'), (218, '3c23', 'qk.c.lbu'), (224, '24a3', 'qk.c.sb')), 'notify': ((40, 'ce27', 'qk.c.lhu'),)}, {'dispatch': ((42, '4831', 'qk.c.lbu'),), 'update': ((182, '8e22', 'qk.c.lhu'), (200, '9623', 'qk.c.lhu'), (218, '3c23', 'qk.c.lbu'), (224, '24a3', 'qk.c.sb')), 'notify': ((40, 'ce27', 'qk.c.lhu'),)})
TYPED=({'dispatch': ((56, 4), (96, 4)), 'update': ((166, 4),), 'notify': ()}, {'dispatch': ((56, 4), (96, 4)), 'update': ((166, 4),), 'notify': ()})
LITERALS=(
{
'dispatch':'''
000 addi 2 2 -32
002 lui 15 65536
004 store 2 18 16 4
006 store 2 19 12 4
008 store 2 1 28 4
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 20 8 4
010 addi 15 15 -1
012 mv 18 11
014 mv 19 12
016 beq 10 15 122
01a auipc 1 536432640
01e jalr 1 1 -1480
022 li 9 20
024 beqz 10 104
026 addi 11 10 6
02a load 10 10 5 1
02c li 12 0
02e li 9 21
030 jal 1 441916
034 lui 15 536883200
038 load 15 15 -63 1
03c bgeu 10 15 104
040 mv 12 19
042 mv 11 18
044 jal 1 440382
048 li 9 0
04a jump 104
04c mv 12 19
04e mv 11 18
050 mv 10 8
052 jal 1 440382
056 beqz 10 90
058 li 9 0
05a addi 8 8 1
05c andi 8 8 255
060 load 15 20 -63 1
064 bltu 8 15 76
068 load 1 2 28 4
06a load 8 2 24 4
06c mv 10 9
06e load 18 2 16 4
070 load 9 2 20 4
072 load 19 2 12 4
074 load 20 2 8 4
076 addi 2 2 32
078 jr 1
07a li 8 0
07c li 9 21
07e lui 20 536883200
082 jump 96
''',
'update':'''
000 addi 2 2 -96
002 store 2 8 88 4
004 mv 8 10
006 li 10 6
008 mul 10 8 10
00c store 2 9 84 4
00e store 2 18 80 4
010 mv 9 12
012 mv 18 11
014 mv 12 2
016 li 11 16
018 store 2 1 92 4
01a addi 10 10 512
01e jal 1 278722
022 beqz 10 50
024 li 10 0
026 load 1 2 92 4
028 load 8 2 88 4
02a load 9 2 84 4
02c load 18 2 80 4
02e addi 2 2 96
030 jr 1
032 li 12 6
034 addi 11 0 255
038 mv 10 2
03a auipc 1 536432640
03e jalr 1 1 -956
042 bnez 10 36
044 lui 15 28672
046 add 8 8 15
048 addi 12 2 16
04a addi 11 0 64
04e mv 10 8
050 jal 1 278722
054 beqz 10 90
056 li 10 1
058 jump 38
05a addi 10 2 16
05c jal 1 438082
060 bne 18 0 176
064 addi 12 0 64
068 li 11 0
06a addi 10 2 16
06c auipc 1 536432640
070 jalr 1 1 -1006
074 bnez 10 86
076 addi 12 0 64
07a li 11 0
07c addi 10 2 16
07e auipc 1 536432640
082 jalr 1 1 -1312
086 lui 15 536883200
08a li 14 1
08c addi 10 2 16
08e store 15 14 -44 1
092 jal 1 438082
096 addi 12 2 16
098 addi 11 0 64
09c mv 10 8
09e jal 1 279388
0a2 lui 15 536883200
0a6 load 10 15 -272 1
0aa jal 1 279312
0ae jump 86
0b0 addi 15 2 16
0b2 addi 12 2 80
0b4 mv 13 15
0b6 load 11 13 0 2
0b8 mv 14 13
0ba beq 11 18 218
0be addi 13 13 4
0c0 bne 12 13 182
0c4 li 10 0
0c6 beqz 9 38
0c8 load 13 15 0 2
0ca mv 14 15
0cc beqz 13 214
0ce addi 15 15 4
0d0 bne 12 15 200
0d4 jump 36
0d6 store 15 18 0 2
0da load 15 14 2 1
0dc beq 15 9 86
0e0 store 14 9 2 1
0e2 bnez 9 134
0e4 store 14 0 0 2
0e8 jump 134
''',
'notify':'''
000 lui 15 536883200
004 addi 15 15 492
008 load 14 15 8 4
00a beqz 14 74
00c load 14 15 60 4
00e beqz 14 74
010 li 13 1
012 bne 10 13 74
016 addi 2 2 -16
018 store 2 8 8 4
01a lui 8 536883200
01e addi 8 8 412
022 load 12 8 32 4
024 store 2 1 12 4
026 beqz 12 66
028 load 11 15 12 2
02a load 10 8 36 4
02c srli 11 11 2
02e call_indirect 1 14
030 load 10 8 32 4
032 auipc 1 536592384
036 jalr 1 1 -562
03a store 8 0 32 4
03e store 8 0 36 4
042 load 1 2 12 4
044 load 8 2 8 4
046 addi 2 2 16
048 jr 1
04a jr 1
''',
},
{
'dispatch':'''
000 addi 2 2 -32
002 lui 15 65536
004 store 2 18 16 4
006 store 2 19 12 4
008 store 2 1 28 4
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 20 8 4
010 addi 15 15 -1
012 mv 18 11
014 mv 19 12
016 beq 10 15 122
01a auipc 1 536432640
01e jalr 1 1 -1964
022 li 9 20
024 beqz 10 104
026 addi 11 10 6
02a load 10 10 5 1
02c li 12 0
02e li 9 21
030 jal 1 442400
034 lui 15 536883200
038 load 15 15 17 1
03c bgeu 10 15 104
040 mv 12 19
042 mv 11 18
044 jal 1 440866
048 li 9 0
04a jump 104
04c mv 12 19
04e mv 11 18
050 mv 10 8
052 jal 1 440866
056 beqz 10 90
058 li 9 0
05a addi 8 8 1
05c andi 8 8 255
060 load 15 20 17 1
064 bltu 8 15 76
068 load 1 2 28 4
06a load 8 2 24 4
06c mv 10 9
06e load 18 2 16 4
070 load 9 2 20 4
072 load 19 2 12 4
074 load 20 2 8 4
076 addi 2 2 32
078 jr 1
07a li 8 0
07c li 9 21
07e lui 20 536883200
082 jump 96
''',
'update':'''
000 addi 2 2 -96
002 store 2 8 88 4
004 mv 8 10
006 li 10 6
008 mul 10 8 10
00c store 2 9 84 4
00e store 2 18 80 4
010 mv 9 12
012 mv 18 11
014 mv 12 2
016 li 11 16
018 store 2 1 92 4
01a addi 10 10 512
01e jal 1 278870
022 beqz 10 50
024 li 10 0
026 load 1 2 92 4
028 load 8 2 88 4
02a load 9 2 84 4
02c load 18 2 80 4
02e addi 2 2 96
030 jr 1
032 li 12 6
034 addi 11 0 255
038 mv 10 2
03a auipc 1 536432640
03e jalr 1 1 -1440
042 bnez 10 36
044 lui 15 28672
046 add 8 8 15
048 addi 12 2 16
04a addi 11 0 64
04e mv 10 8
050 jal 1 278870
054 beqz 10 90
056 li 10 1
058 jump 38
05a addi 10 2 16
05c jal 1 438566
060 bne 18 0 176
064 addi 12 0 64
068 li 11 0
06a addi 10 2 16
06c auipc 1 536432640
070 jalr 1 1 -1490
074 bnez 10 86
076 addi 12 0 64
07a li 11 0
07c addi 10 2 16
07e auipc 1 536432640
082 jalr 1 1 -1796
086 lui 15 536883200
08a li 14 1
08c addi 10 2 16
08e store 15 14 36 1
092 jal 1 438566
096 addi 12 2 16
098 addi 11 0 64
09c mv 10 8
09e jal 1 279536
0a2 lui 15 536883200
0a6 load 10 15 -192 1
0aa jal 1 279460
0ae jump 86
0b0 addi 15 2 16
0b2 addi 12 2 80
0b4 mv 13 15
0b6 load 11 13 0 2
0b8 mv 14 13
0ba beq 11 18 218
0be addi 13 13 4
0c0 bne 12 13 182
0c4 li 10 0
0c6 beqz 9 38
0c8 load 13 15 0 2
0ca mv 14 15
0cc beqz 13 214
0ce addi 15 15 4
0d0 bne 12 15 200
0d4 jump 36
0d6 store 15 18 0 2
0da load 15 14 2 1
0dc beq 15 9 86
0e0 store 14 9 2 1
0e2 bnez 9 134
0e4 store 14 0 0 2
0e8 jump 134
''',
'notify':'''
000 lui 15 536883200
004 addi 15 15 572
008 load 14 15 8 4
00a beqz 14 74
00c load 14 15 60 4
00e beqz 14 74
010 li 13 1
012 bne 10 13 74
016 addi 2 2 -16
018 store 2 8 8 4
01a lui 8 536883200
01e addi 8 8 492
022 load 12 8 32 4
024 store 2 1 12 4
026 beqz 12 66
028 load 11 15 12 2
02a load 10 8 36 4
02c srli 11 11 2
02e call_indirect 1 14
030 load 10 8 32 4
032 auipc 1 536592384
036 jalr 1 1 -710
03a store 8 0 32 4
03e store 8 0 36 4
042 load 1 2 12 4
044 load 8 2 8 4
046 addi 2 2 16
048 jr 1
04a jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B1down literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1down typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1down fullboundaries')
 for a,f in s.items():init.g(n,a,'B1down '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1down Xwchc encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1down completeidentity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1down ordinaryRET');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'B1down linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==14,'B1down capturedcallback');calls.append(dict(offset=a-pc,target='captured U32[config+60] & ~1'))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1down adjacentpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1down closedlocalCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1down allnodesreachable')
 cuts={'dispatch':((0x64,0x4c),),'update':((0xc0,0xb6),(0xd0,0xc8)),'notify':()}[part]
 cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in edges.items()}
 check(common.acyclic(cut) and common.acyclic(edges)==(part=='notify'),'B1down exactloop cuts')
 expected={'dispatch':[(0x1e,0x20000a94),(0x30,0x6be3c+484*index),(0x44,STARTS[index][1]),(0x52,STARTS[index][1])],
  'update':[(0x1e,0x440c2+148*index),(0x3e,0x200004bc),(0x50,0x440c2+148*index),(0x5c,0x6af42+484*index),(0x70,0x200004bc),(0x82,0x2000039c),(0x92,0x6af42+484*index),(0x9e,0x4435c+148*index),(0xaa,STARTS[index][2])],
  'notify':[(0x2e,'captured U32[config+60] & ~1'),(0x36,0x20000110)]}[part]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'B1down exactallcalltargets')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 expected_saved={'dispatch':{(1,28),(8,24),(9,20),(18,16),(19,12),(20,8)},'update':{(1,92),(8,88),(9,84),(18,80)},'notify':{(1,12),(8,8)}}[part]
 check({(d['source'],d['imm']) for d in stores if d['base']==2}==expected_saved,'B1down savedframe census')
 if part=='dispatch':check(len(stores)==6 and rets==[pc+0x78],'B1down dispatch frameonly stores')
 elif part=='update':check(len(stores)==8 and [d['offset'] for d in stores if d['base']!=2]==[0x8e,0xd6,0xe0,0xe4] and rets==[pc+0x30],'B1down updater flag/key/value/clear stores')
 else:check(len(stores)==4 and [d['imm'] for d in stores if d['base']!=2]==[32,36] and rets==[pc+0x48,pc+0x4a],'B1down notifier pendingpairclear stores')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part=='dispatch':
  choices={'lookupnull20':{0x16:0x1a,0x24:0x68},'indexout21':{0x16:0x1a,0x24:0x26,0x3c:0x68},'singleupdate_replyignored0':{0x16:0x1a,0x24:0x26,0x3c:0x40},
   'all_count0_reply21':{0x16:0x7a,0x64:0x68}}
 elif part=='notify':
  choices={'configgate0':{0xa:0x4a},'callback0':{0xa:0xc,0xe:0x4a},'selector_not1':{0xa:0xc,0xe:0x10,0x12:0x4a},'pendingnull':{0xa:0xc,0xe:0x10,0x12:0x16,0x26:0x42},'callback_release_clear':{0xa:0xc,0xe:0x10,0x12:0x16,0x26:0x28}}
 else:
  base={0x22:0x32,0x42:0x44,0x54:0x5a}
  choices={'firstreadnonzero_reply0':{0x22:0x24},'prefix_allFF_reply0':{0x22:0x32,0x42:0x24},'secondreadnonzero_reply1':{0x22:0x32,0x42:0x44,0x54:0x56},
   'key0_tableall0_reply1':{**base,0x60:0x64,0x74:0x56},'key0_clear_flag_save':{**base,0x60:0x64,0x74:0x76},
   'found_samevalue_reply1':{**base,0x60:0xb0,0xba:0xda,0xdc:0x56},'found_change_nonzero_flag_save':{**base,0x60:0xb0,0xba:0xda,0xdc:0xe0,0xe2:0x86},
   'found_change0_clearkey_flag_save':{**base,0x60:0xb0,0xba:0xda,0xdc:0xe0,0xe2:0xe4}}
 ps={label:common.walk(b,c) for label,c in choices.items()}
 if part=='notify':
  s=ps['callback_release_clear'];check(s.index(0x2e)<s.index(0x30)<s.index(0x36)<s.index(0x3a)<s.index(0x3e),'B1down callback->freshpointer->release->clears order')
 if part=='update':
  s=ps['found_change_nonzero_flag_save'];check(s.index(0x8e)<s.index(0x92)<s.index(0x9e)<s.index(0xaa),'B1down flagset precedestransform/save/notify')
 return ps


def domains():
 for i in range(256):
  for count in range(256):
   if i<count:check(i<=254 and (i+1)&255==i+1,'B1down bulkindex bounded despite freshcount')
 for i in range(16):check(16+4*i+4<=80 and 16+4*i+2<80,'B1down16record slab allkey/bytefields withinframe')
 check(set(range(16,80)).isdisjoint(range(80,96)),'B1down localtable64 disjointsavedframe')
 for V in range(65536):
  check((V&255)==V%256,'B1down low8write fieldprojection')
  if V>255:check(V!=(V&255),'B1down comparefullV cannever equal anyU8')
 check(256!=0 and 256&255==0,'B1down nonzeroVmaywritezero withoutkeyclear')
 check(512+6*254==2036 and 0x7000+254==0x70fe,'B1down admittedindices numericNVrequest range')
 check(65535==0xffff and 65535>254,'B1down dispatch sentinel exact fullword')
 for size in range(65536):check(size>>2==size//4 and size>>2<=16383,'B1down notifier halfwordunits divideby4')
 return dict(index_freshcount_pairs=65536,B1_value_U16_cases=65536,callback_units_U16_cases=65536,table_entries=16,table_stride=4,
  key='fullwordH comparestoU16keys;newkeywriteslow16H',value='fullwordV comparestoU8slot2;write low8V;clear key only fullV==0',
  record_byte3_excluded_from_direct_record_SH_SB=True,physical_NV_units_or_writeextents_proved=False,target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  pc=STARTS[index][k];raw=init.binding.take(data,pc,SIZES[k]);check(sparse.captured(mem,pc,SIZES[k])==raw,'B1down allbodies strictHEX');bs[part]=body(raw,part,index)
 ns={part:{v['pc']-b['start']:v for v in b['instructions']} for part,b in bs.items()};d,u,n=ns['dispatch'],ns['update'],ns['notify'];G=0x20003000;flag=G-44+80*index
 check(u[0x86]['imm']+u[0x8e]['imm']==flag and u[0x8e]['rs2']==14 and u[0x8a]['imm']==1,'B1down directflagwriter1')
 check(d[0x16]['rs1']==10 and d[0x10]['imm']+d[2]['imm']==65535 and d[0x3c]['op']=='bgeu' and d[0x5c]['imm']==255,'B1down sentinel vsboundedfreshcount')
 check(u[0x8]['op']=='mul' and u[0x1a]['imm']==512 and u[0x44]['imm']==0x7000 and u[0x48]['imm']==16 and u[0xb2]['imm']==80,'B1down NVarguments/localtable bounds')
 check(n[0x28]['width']==2 and n[0x28]['imm']==12 and n[0x2c]['imm']==2 and n[0x30]['rs1']==8 and n[0x30]['imm']==32,'B1down callbackunits andpostcallbackfreshrelease pointer')
 cb=parent['bodies']['handler'];cn={v['pc']-cb['start']:v for v in cb['instructions']}
 check(next(c['target'] for c in cb['calls'] if c['offset']==0x9c)==bs['dispatch']['start'] and next(c['target'] for c in cb['calls'] if c['offset']==0xb2)==bs['notify']['start'] and cn[0x90]['imm']+cn[0x94]['imm']==flag,'B1down actual B1 parent joins')
 # Existing mapped byte predicate and fill proofs reused; hardware instructions remain unexecuted.
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy'];reuse={}
 for name,target,z in [('predicate',0x200004bc,62),('fill',0x2000039c,46)]:
  src=int(f['source'],16)+target-int(f['destination'],16);raw=init.binding.take(data,src,z)
  check(target+z<=int(mapping['first_copy_end_exclusive'],16) and sparse.captured(mem,src,z)==raw,'B1down mappedleaf complete originalHEX')
  b=predicate.body(raw,'predicate',index) if name=='predicate' else fill_source.fill_contract(raw)
  reuse[name]=dict(target=target,source=src,bytes=z,sha256=sha256(raw).hexdigest(),new_code_bytes_counted=0,installed_binding_proved=False)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},reused_leaves=reuse,
  globals=dict(flag=flag,record_count_byte=G-63+80*index,notify_task_byte=G-272+80*index,config=G+492+80*index,context=G+412+80*index),
  dispatch_contract=['fullentryID!=FFFF ->lookup20000a94(ID);null20;nonnullP ->selector6be3c/6c020(freshU8P5,P6,0),index>=freshcount ->21',
   'validindex ->update(index,originalfullH,originalfullV),ignoreupdatestatus,return0; FFFF ->index0,default21,each index<freshU8count callsupdate,anynonzero setssticky0;atmost255callsundercalleereturn/contextpreservation'],
  updater_contract=['read440c2/44156((6*index+512)mod32,16,SP);nonzero0. predicate(SP,255,6)nonzero0. read(index+7000mod32,64,SP16);nonzero1 withoutlocalflag',
   'call6af42/6b126(SP16),ignorestatus. H0 ->predicate(SP16,0,64);nonzero1,elsefillzero64 andchangedpath. AllNVcountunits/outputextents remainunproved',
   'Hnonzero ->scan16slots stride4 forfreshU16slot0==fullH;firstmatch usesfullV vsfreshU8slot2. No match,V0 ->0;otherwise firstzeroU16key getsSHlow16H beforevaluecomparison;noempty0',
   'equalbyte/fullV ->1,noflag/save;different ->SB low8Vtoslot2;onlyfullV0 additionallySH0key. DirectrecordSH/SB excludebyte3;H0fill/opaquecallees mayoverwriteit. NonzeroV256canwrite0valuewhilekeepingkey',
   'changedpath:flag1 BEFOREsecondtransform;call6af42/6b126(SP16),write-request4435c/443f0(index+7000,64,SP16),freshnotifytask->notifier;ignorecallee/statusandreturn1. No atomicity,rollback,actualpersistenceorborrowedstackretentionproof'],
  notifier_contract=['captureconfigword8nonnull,thenF=wordconfig60nonnull,fullentryA0must1;failguards RETwithoutchangingentryA0',
   'captureP=wordcontext32;null returns1withoutcallback/release/clears. Nonnull ->F&~1(freshwordcontext36,freshU16config12>>2,P)',
   'aftercallback freshPprime=wordcontext32;private-release20000110(Pprime) WITHOUTnewnullguard;thenSW0context32,SW0context36;RETwiththenliveprivate-releaseA0. Pprime neednotequalP',
   'callback captured beforelaterreads;noactualsynchronousconsumption/nonretention/validfunction/privatefree/samepointer/physicaleffectproof'],
  composition=['B1 H/V areU16fields;dispatcher validindices <=254 -> numericreadaddresses512..2036,index+7000..70FE,notphysicalNVunitclaims',
   'updater cancallnotifier itself,thenB1parent freshflag maycallnotifieragain; no exactlyonceclaim. Flag1 precedesunknowncallswhich maychangeflag/context/task',
   'dispatcher0 andupdater1 do notproveflagwrite,storagechange,callbackexecutionornotification. Parentnormalcallbackstatus/bit15reply staysaspreviousproof'],
  premises='conditionalcandidateISA/providers;validcode/frame/global/table/callback/buffer extents;NV/transform/predicate/fill/callback/privatefree normalreturns andS/SP/RA/savedframepreservation;noadversealias/wrap/IRQ/DMA/reentry;freshsnapshotidentities separate',
  actual_NV_persistence_provider_binding_flag_preservation_callback_retention_or_pointerlifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-downstream-dispatch-update-notify-static-v1',APP_sha256=sha256(image).hexdigest(),
  profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_new_body_bytes=884,complete_new_body_instructions=336,reused_predicate_fill_bytes=216,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['lookup20000a94/selector6be3c andtransform6af42 contracts','NV440c2/4435c output/write/stackbuffer retention','configcallback60/context32/36 writers andprivatefree lifetime'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1down instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1down typedmutation escaped')
    typed+=1
 check((mutations,typed)==(336,6),'B1down mutation census');domains()
 print('PASS:336 instruction/6 typed-load mutations rejected;freshcount/U16value/frame/16slot certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1down exactledger replay')
 print('PASS:884B/336i complete B1 dispatch/update/notify;strict HEX;flag writer/callback/fresh release joins;exact ledger')
 print('PASS:NO target execution/emulation;NVeffects,installedbindings,retention andpointerlifetime UNPROVED')


if __name__=='__main__':main()
