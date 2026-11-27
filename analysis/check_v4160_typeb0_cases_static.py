"""Offline B0 case18/case22 and common post-helper contracts.
Original operands/CFG, immutable path certificates and host scalar intervals.
No target execution/emulation, provider or register/RAM/heap/list model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_typeb0_consumer_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-typeb0-cases-static.json')
PARTS=('case18','case22','post')
STARTS=((0x4bdc6,0x4bcd8,0x49f54),(0x4be5e,0x4bd70,0x49fec))
SIZES=(152,238,40)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('d12b09d3eb091d0fa4a1ce2ba6eff5853ec228c389f0aeca1a539d0a4ad765fc', '18f584a0c6d43d8314c296030c173d843304be89d29e77e3e96e7da21bc5893d', '8e1622812a495fc9424cccacc618cb7d75c1dfccec67f6aeae826b9ff5e9ba09'), ('299f4fb2fa4a62cf1644ae60bcd057fb2fd813614aa67888be47260cc4318556', '5f15ede23ee2b234f7550f4d02731e99991a252044a648d5870c0d5bf745145a', '8e1622812a495fc9424cccacc618cb7d75c1dfccec67f6aeae826b9ff5e9ba09'))
COUNTS=((66, 98, 15), (66, 98, 15))
TYPED_LOADS=({'case18': (), 'case22': ((84, 5),), 'post': ()}, {'case18': (), 'case22': ((84, 5),), 'post': ()})
LITERALS=(
{
'case18':'''
000 addi 2 2 -48
002 store 2 8 40 4
004 mv 8 10
006 load 10 10 8 2
008 store 2 9 36 4
00a mv 9 11
00c addi 11 2 30
010 store 2 18 32 4
012 store 2 1 44 4
014 mv 18 12
016 auipc 1 536563712
01a jalr 1 1 -916
01e beqz 10 144
020 load 15 10 8 1
022 andi 15 15 32
026 bnez 15 98
028 load 14 8 17 1
02a addi 15 0 82
02e bnez 14 50
030 load 15 8 4 1
032 load 13 8 10 2
034 load 12 8 12 4
036 load 11 8 8 2
038 load 10 8 2 2
03a li 14 0
03c jal 1 310050
040 mv 15 10
042 bnez 10 132
044 load 15 8 17 1
046 bnez 15 82
048 load 10 8 2 2
04a jal 1 282884
04e li 15 22
050 bnez 10 84
052 li 15 0
054 load 1 2 44 4
056 load 8 2 40 4
058 load 9 2 36 4
05a load 18 2 32 4
05c mv 10 15
05e addi 2 2 48
060 jr 1
062 store 2 10 12 4
064 load 10 2 30 2
066 jal 1 308844
06a mv 15 10
06c beqz 10 148
06e load 11 2 12 4
070 load 10 8 2 2
072 li 12 18
074 call_indirect 1 15
076 mv 15 10
078 beqz 10 40
07a load 14 8 8 2
07c store 9 14 0 2
07e load 14 8 17 1
080 bnez 14 82
082 jump 84
084 li 14 22
086 bne 10 14 122
08a store 18 0 0 1
08e jump 82
090 li 15 1
092 jump 122
094 li 15 14
096 jump 122
''',
'case22':'''
000 addi 2 2 -48
002 store 2 8 40 4
004 mv 8 10
006 load 10 10 8 2
008 store 2 9 36 4
00a mv 9 11
00c addi 11 2 18
010 store 2 1 44 4
012 store 2 18 32 4
014 auipc 1 536563712
018 jalr 1 1 -676
01c beqz 10 234
01e load 15 10 8 1
020 store 2 10 12 4
022 andi 15 15 32
026 beqz 15 84
028 load 10 2 18 2
02a jal 1 308844
02e mv 15 10
030 load 11 2 12 4
032 bnez 10 70
034 load 15 8 8 2
036 li 10 14
038 store 9 15 0 2
03a load 1 2 44 4
03c load 8 2 40 4
03e load 9 2 36 4
040 load 18 2 32 4
042 addi 2 2 48
044 jr 1
046 load 10 8 2 2
048 li 12 18
04a call_indirect 1 15
04c beqz 10 84
04e load 15 8 8 2
050 store 9 15 0 2
052 jump 58
054 load 18 8 2 2
058 mv 10 18
05a jal 1 308766
05e bnez 10 118
060 lui 10 65536
062 addi 10 10 -1
064 jal 1 308766
068 bnez 10 114
06a load 15 8 8 2
06c li 10 9
06e store 9 15 0 2
070 jump 58
072 store 10 18 0 2
076 addi 14 10 4
07a li 15 0
07c li 13 15
07e load 12 14 0 2
080 bnez 12 222
082 li 14 12
084 mul 15 15 14
088 addi 18 8 8
08c li 12 12
08e mv 11 18
090 addi 15 15 4
092 add 10 10 15
094 auipc 1 536559616
098 jalr 1 1 1478
09c li 12 12
09e mv 11 18
0a0 addi 10 2 20
0a2 auipc 1 536559616
0a6 jalr 1 1 1464
0aa load 12 8 12 2
0ac load 10 8 2 2
0ae li 14 16
0b0 li 13 0
0b2 li 11 23
0b4 jal 1 303706
0b8 store 2 10 28 4
0ba bnez 10 196
0bc load 15 8 8 2
0be li 10 17
0c0 store 9 15 0 2
0c2 jump 58
0c4 load 11 8 16 4
0c6 load 12 8 12 2
0c8 auipc 1 536559616
0cc jalr 1 1 1426
0d0 load 10 8 2 2
0d2 addi 11 2 20
0d4 jal 1 282948
0d8 beqz 10 58
0da li 10 22
0dc jump 58
0de addi 15 15 1
0e0 addi 14 14 12
0e2 bne 15 13 126
0e6 li 10 9
0e8 jump 78
0ea li 10 1
0ec jump 78
''',
'post':'''
000 load 14 10 0 2
002 addi 15 0 176
006 bne 14 15 38
00a load 15 10 4 1
00c li 14 18
00e bne 15 14 34
012 load 14 10 17 1
014 li 15 1
016 bne 15 14 38
01a load 10 10 2 2
01c li 11 1
01e jal 0 317794
022 li 14 27
024 jump 22
026 jr 1
''',
},
{
'case18':'''
000 addi 2 2 -48
002 store 2 8 40 4
004 mv 8 10
006 load 10 10 8 2
008 store 2 9 36 4
00a mv 9 11
00c addi 11 2 30
010 store 2 18 32 4
012 store 2 1 44 4
014 mv 18 12
016 auipc 1 536563712
01a jalr 1 1 -1068
01e beqz 10 144
020 load 15 10 8 1
022 andi 15 15 32
026 bnez 15 98
028 load 14 8 17 1
02a addi 15 0 82
02e bnez 14 50
030 load 15 8 4 1
032 load 13 8 10 2
034 load 12 8 12 4
036 load 11 8 8 2
038 load 10 8 2 2
03a li 14 0
03c jal 1 310202
040 mv 15 10
042 bnez 10 132
044 load 15 8 17 1
046 bnez 15 82
048 load 10 8 2 2
04a jal 1 283032
04e li 15 22
050 bnez 10 84
052 li 15 0
054 load 1 2 44 4
056 load 8 2 40 4
058 load 9 2 36 4
05a load 18 2 32 4
05c mv 10 15
05e addi 2 2 48
060 jr 1
062 store 2 10 12 4
064 load 10 2 30 2
066 jal 1 308996
06a mv 15 10
06c beqz 10 148
06e load 11 2 12 4
070 load 10 8 2 2
072 li 12 18
074 call_indirect 1 15
076 mv 15 10
078 beqz 10 40
07a load 14 8 8 2
07c store 9 14 0 2
07e load 14 8 17 1
080 bnez 14 82
082 jump 84
084 li 14 22
086 bne 10 14 122
08a store 18 0 0 1
08e jump 82
090 li 15 1
092 jump 122
094 li 15 14
096 jump 122
''',
'case22':'''
000 addi 2 2 -48
002 store 2 8 40 4
004 mv 8 10
006 load 10 10 8 2
008 store 2 9 36 4
00a mv 9 11
00c addi 11 2 18
010 store 2 1 44 4
012 store 2 18 32 4
014 auipc 1 536563712
018 jalr 1 1 -828
01c beqz 10 234
01e load 15 10 8 1
020 store 2 10 12 4
022 andi 15 15 32
026 beqz 15 84
028 load 10 2 18 2
02a jal 1 308996
02e mv 15 10
030 load 11 2 12 4
032 bnez 10 70
034 load 15 8 8 2
036 li 10 14
038 store 9 15 0 2
03a load 1 2 44 4
03c load 8 2 40 4
03e load 9 2 36 4
040 load 18 2 32 4
042 addi 2 2 48
044 jr 1
046 load 10 8 2 2
048 li 12 18
04a call_indirect 1 15
04c beqz 10 84
04e load 15 8 8 2
050 store 9 15 0 2
052 jump 58
054 load 18 8 2 2
058 mv 10 18
05a jal 1 308918
05e bnez 10 118
060 lui 10 65536
062 addi 10 10 -1
064 jal 1 308918
068 bnez 10 114
06a load 15 8 8 2
06c li 10 9
06e store 9 15 0 2
070 jump 58
072 store 10 18 0 2
076 addi 14 10 4
07a li 15 0
07c li 13 15
07e load 12 14 0 2
080 bnez 12 222
082 li 14 12
084 mul 15 15 14
088 addi 18 8 8
08c li 12 12
08e mv 11 18
090 addi 15 15 4
092 add 10 10 15
094 auipc 1 536559616
098 jalr 1 1 1326
09c li 12 12
09e mv 11 18
0a0 addi 10 2 20
0a2 auipc 1 536559616
0a6 jalr 1 1 1312
0aa load 12 8 12 2
0ac load 10 8 2 2
0ae li 14 16
0b0 li 13 0
0b2 li 11 23
0b4 jal 1 303858
0b8 store 2 10 28 4
0ba bnez 10 196
0bc load 15 8 8 2
0be li 10 17
0c0 store 9 15 0 2
0c2 jump 58
0c4 load 11 8 16 4
0c6 load 12 8 12 2
0c8 auipc 1 536559616
0cc jalr 1 1 1274
0d0 load 10 8 2 2
0d2 addi 11 2 20
0d4 jal 1 283096
0d8 beqz 10 58
0da li 10 22
0dc jump 58
0de addi 15 15 1
0e0 addi 14 14 12
0e2 bne 15 13 126
0e6 li 10 9
0e8 jump 78
0ea li 10 1
0ec jump 78
''',
'post':'''
000 load 14 10 0 2
002 addi 15 0 176
006 bne 14 15 38
00a load 15 10 4 1
00c li 14 18
00e bne 15 14 34
012 load 14 10 17 1
014 li 15 1
016 bne 15 14 38
01a load 10 10 2 2
01c li 11 1
01e jal 0 317946
022 li 14 27
024 jump 22
026 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B0cases literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'B0cases typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B0cases completeboundaries '+part)
 for a,f in s.items():init.g(n,a,'B0cases operand '+part+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B0cases completeidentity '+part)
 edges={};calls=[];tails=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B0cases ordinaryRET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   if op=='jal':t=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1'],'B0cases adjacentpair');t=(a-4+u['imm']+d['imm'])&0xfffffffe
   check(d['rd'] in (0,1),'B0cases linkclass')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=t,new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=t))
  elif op=='call_indirect':
   check(d['rd']==1 and d['rs1']==15,'B0cases linkedcallback');calls.append(dict(offset=a-pc,target='captured X15 & ~1',indirect=True))
  check(all(z in n for z in q),'B0cases closedlocalCFG');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B0cases fullreachability')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 check((len(calls),len(tails),len(returns),len(stores))==((5,0,1,7),(10,0,1,11),(0,1,1,0))[k],'B0cases exactcall/tail/return/storecensus')
 back=[(a-pc,z-pc) for a,qs in edges.items() for z in qs if z<a]
 if part=='case22':
  cut={a:[z for z in qs if (a,z)!=(pc+0xe2,pc+0x7e)] for a,qs in edges.items()}
  check(common.acyclic(cut) and not common.acyclic(edges),'B0cases onlyone cycle edge')
  check(n[pc+0xe2]['target']==pc+0x7e and n[pc+0xde]['imm']==1 and n[pc+0xe0]['imm']==12 and n[pc+0x7c]['imm']==15,'B0cases 15probe loop operands')
 else:check(common.acyclic(edges),'B0cases completeDAG')
 if part!='post':
  saves={(d['source'],d['imm']) for d in stores if d['base']==2 and d['offset']<0x16}
  restores={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and d['imm']>=32}
  check(saves==restores=={(1,44),(8,40),(9,36),(18,32)},'B0cases 48Bframe saves/restores')
 else:check({d['rd'] for d in n.values() if d.get('rd',0)}=={10,11,14,15},'B0cases postnoframe/noSdefinitions')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=returns,stores=stores,backward_address_edges=back,complete_local_body=True,target_execution_or_emulation=False)


def case18_paths(b):
 entry={0x1e:0x20,0x26:0x28};ordinary={**entry,0x2e:0x30}
 foreign={0x1e:0x20,0x26:0x62,0x6c:0x6e}
 choices={
  'lookupnull_M17zero_reply1':{0x1e:0x90,0x80:0x82},
  'lookupnull_M17nonzero_reply0':{0x1e:0x90,0x80:0x52},
  'callbackpointer_null_M17zero_reply14':{0x1e:0x20,0x26:0x62,0x6c:0x94,0x80:0x82},
  'indirect22_M17zero_no_localclear':{**foreign,0x78:0x7a,0x80:0x82},
  'indirect_nonzero_M17nonzero_reply0':{**foreign,0x78:0x7a,0x80:0x52},
  'ordinary22_clearsflag_reply0':{**ordinary,0x42:0x84,0x86:0x8a},
  'ordinary_other_nonzero_writesout':{**ordinary,0x42:0x84,0x86:0x7a,0x80:0x82},
  'ordinary0_followup_nonzero_local22_no_clear':{**ordinary,0x42:0x44,0x46:0x48,0x50:0x54},
  'ordinary0_M17nonzero_reply0':{**ordinary,0x42:0x44,0x46:0x52}}
 paths={k:common.walk(b,v) for k,v in choices.items()};n={d['pc']-b['start']:d for d in b['instructions']}
 allpaths=task8.v34.allocation.previous.dag_paths(b)
 for seq in allpaths:
  if 0x8a in seq:check(0x3c in seq and 0x84 in seq and seq[seq.index(0x86)+1]==0x8a and 0x52 in seq and 0x7c not in seq,'B0cases onlyordinaryhelper22 clearsflag thenreply0')
 check(0x8a not in paths['indirect22_M17zero_no_localclear'] and 0x7c in paths['indirect22_M17zero_no_localclear'],'B0cases indirect22 isnot ordinary22 clear')
 check(0x8a not in paths['ordinary0_followup_nonzero_local22_no_clear'],'B0cases synthesized22 doesnotclearflag')
 for name,seq in paths.items():
  if 'reply0' in name:check(n[[o for o in seq if n[o].get('rd')==15][-1]]['imm']==0,'B0cases selectedforced0 paths')
 return {'selected':paths,'syntactic_paths':len(allpaths),'allpaths_sha256':sha256(json.dumps(allpaths,separators=(',',':')).encode()).hexdigest(),
  'actual_callbackeffects_output_or_pointer_nonretention_proved':False}


def case22_paths(b):
 entry={0x1c:0x1e,0x26:0x54};first={**entry,0x5e:0x76};free={**first,0x80:0x82}
 choices={
  'rootlookupnull_reply1_writesM8':{0x1c:0xea},
  'callbackpointer_null_reply14_writesM8':{0x1c:0x1e,0x26:0x28,0x32:0x34},
  'firstkey_found_doesnotpublishkey':{**free,0xba:0xbc},
  'fallbackkey_found_publisheskey':{**entry,0x5e:0x60,0x68:0x72,0x80:0x82,0xba:0xbc},
  'bothkeysnull_reply9_writesM8':{**entry,0x5e:0x60,0x68:0x6a},
  'published_copy_then_requestnull_reply17':{**free,0xba:0xbc},
  'published_copy_then_reportzero_reply0':{**free,0xba:0xc4,0xd8:0x3a},
  'published_copy_then_reportnonzero_reply22':{**free,0xba:0xc4,0xd8:0xda}}
 paths={k:common.walk(b,v) for k,v in choices.items()};pc=b['start'];edges=b['CFG']
 def checked(seq):
  absolute=[pc+o for o in seq];check(all(z in edges[a] for a,z in zip(absolute,absolute[1:])) and not edges[absolute[-1]],'B0cases immutableboundedloop witness');return seq
 prefix=paths['published_copy_then_requestnull_reply17'];head=prefix[:prefix.index(0x7e)];after=prefix[prefix.index(0x82):]
 late=checked(head+[o for _ in range(14) for o in (0x7e,0x80,0xde,0xe0,0xe2)]+[0x7e,0x80]+after)
 full=checked(head+[o for _ in range(14) for o in (0x7e,0x80,0xde,0xe0,0xe2)]+[0x7e,0x80,0xde,0xe0,0xe2,0xe6,0xe8,0x4e,0x50,0x52,0x3a,0x3c,0x3e,0x40,0x42,0x44])
 check(full.count(0x7e)==15 and late.count(0x7e)==15,'B0cases exactmaximum15probes')
 check(0x72 not in paths['firstkey_found_doesnotpublishkey'] and 0x72 in paths['fallbackkey_found_publisheskey'],'B0cases keypublication onfallback only')
 seq=paths['published_copy_then_requestnull_reply17'];check(seq.index(0x98)<seq.index(0xa6)<seq.index(0xb4)<seq.index(0xc0),'B0cases selectedrecord copy precedeslaterrequestfailureoutput')
 check(0x4e in full and 0x50 in full and 0x6e not in full,'B0cases fullrow error reloadsfreshM8 foroutput notindex15')
 return {'selected':paths,'late_firstzero_index14':late,'all15occupied_reply9_outputfreshM8':full,
  'loop_bound':'index0..14 probe U16 atO+4+12*i;occupied incrementsindex/base;index15 terminates,withoutcalls inside loop. Validmemory/no interference assumptions remain.',
  'allfull_output_halfword':'freshU16M8','allfull_reply':9,'selected_slot_copy_rolled_back_or_actual_persistent_pointer_ownership_proved':False}


def post_paths(b):
 paths={
  'word_not00B0_RET':common.walk(b,{6:0x26}),
  'opcode18_M17not1_RET':common.walk(b,{6:0xa,0xe:0x12,0x16:0x26}),
  'opcode18_M17eq1_tail':common.walk(b,{6:0xa,0xe:0x12,0x16:0x1a}),
  'opcode27_tail_without_M17read':common.walk(b,{6:0xa,0xe:0x22,0x16:0x1a}),
  'otheropcode_RET':common.walk(b,{6:0xa,0xe:0x22,0x16:0x26})}
 check(0x12 not in paths['opcode27_tail_without_M17read'] and 0x12 in paths['opcode18_M17eq1_tail'],'B0cases opcode27 doesnotrequireM17one')
 return paths


def domains():
 for word in range(65536):check((word==0xb0)==((word&255)==0xb0 and word>>8==0),'B0cases postword type-and-byte1zero gate')
 for op in range(256):
  for m17 in range(256):
   hit=(op==18 and m17==1) or op==27
   check(hit==((m17==1 if op==18 else op==27)),'B0cases exactpost18/27 predicates')
 for i in range(15):
  check(4+12*i+2<=174 and 4+12*i+12<=184,'B0cases probe/selectedrecord intervals')
  check(i+1<=15,'B0cases occupiedindex boundedincrement')
 check(set(range(18,32)).isdisjoint(range(32,48)) and set(range(30,32)).isdisjoint(range(32,48)),'B0cases lookup/snapshot scratch avoids savedframe')
 check(20+8==28 and 8+8==16,'B0cases messageM16 pointerprojects tolocalsnapshotSP28 beforeoverwrite')
 return {'post_word_cases':65536,'post_opcode_M17_cases':65536,'slot_probes_max':15,'last_probe_offset':172,'probe_extent_end':174,'last_full_record_extent_end':184,
  'original_M16_is_selected_slot_record_word8_then_local_snapshot_word8_replaced':True,'actualmemoryextent_copysemantics_alias_or_pointerlifetime_proved':False}


def profile(data,hexraw,index,parent):
 bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
 a,b,p=(bs[x] for x in PARTS);an={d['pc']-a['start']:d for d in a['instructions']};bn={d['pc']-b['start']:d for d in b['instructions']};pn={d['pc']-p['start']:d for d in p['instructions']}
 delta=152*index
 expectedA=[(0x1a,0x20000a48),(0x3c,0x4bb22+delta),(0x4a,0x45104+148*index),(0x66,0x4b66c+delta),(0x74,'captured X15 & ~1')]
 expectedB=[(0x18,0x20000a48),(0x2a,0x4b66c+delta),(0x4a,'captured X15 & ~1'),(0x5a,0x4b61e+delta),(0x64,0x4b61e+delta),
  (0x98,0x20000332),(0xa6,0x20000332),(0xb4,0x4a25a+delta),(0xcc,0x20000332),(0xd4,0x45144+148*index)]
 for z,expected in ((a,expectedA),(b,expectedB)):
  check(z['calls']==[dict(offset=o,target=t,**({'indirect':True} if isinstance(t,str) else {})) for o,t in expected],'B0cases exactnestedcall targets')
 check(p['tails']==[dict(offset=0x1e,target=0x4d962+delta,new_link=False)],'B0cases post unlinkedIDhelper tail')
 check(an[0x14]['rd']==18 and an[0x14]['rs2']==12 and an[0x8a]['rs1']==18 and an[0x8a]['rs2']==0,'B0cases onlydirectborrowedflagclear writesoriginalA2')
 check(an[0x86]['target']==a['start']+0x7a and an[0x78]['target']==a['start']+0x28 and an[0x80]['target']==a['start']+0x52,'B0cases ordinary22vsindirect22 andM17override exactedges')
 check(bn[0x5e]['target']==b['start']+0x76 and bn[0x68]['target']==b['start']+0x72 and bn[0xe8]['target']==bn[0xec]['target']==b['start']+0x4e,'B0cases fallbackkeypublication anderroroutputfreshM8 edges')
 check(bn[0x8c]['imm']==bn[0x9c]['imm']==12 and bn[0x88]['imm']==8 and bn[0xb8]['imm']==28 and bn[0xc4]['imm']==16,'B0cases slot/snapshot12 andrequestreply overwrite ofM16 copy')
 check(pn[0]['width']==2 and pn[0xe]['target']==p['start']+0x22 and pn[0x24]['target']==p['start']+0x16,'B0cases posthalfwordgate andopcode27sharedcompare')
 h=parent['bodies']['handler'];hn={d['pc']-h['start']:d for d in h['instructions']};hc={c['offset']:c['target'] for c in h['calls']}
 check((hc[0x2d4],hc[0x2e6],hc[0xe2])==(a['start'],b['start'],p['start']),'B0cases exactparentcall joins')
 check(hn[0x2ca]['imm']==9 and hn[0x2ce]['imm']==10 and hn[0x2f0]['rs2']==0,'B0cases parentA2flag/A1halfword andcase22zero directclear')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for part,z in bs.items():
  check(sparse.captured(mem,z['start'],z['bytes'])==init.binding.take(data,z['start'],z['bytes']),'B0cases originalstrictHEX backing')
  receipts.append({'part':part,'source':z['start'],'bytes':z['bytes'],'all_bytes_captured':True})
 return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{part:common.certificates(z) for part,z in bs.items()},
  'case18_paths':case18_paths(a),'case22_paths':case22_paths(b),'post_paths':post_paths(p),
  'case18_contract':['saveM,A1halfwordout,A2flag;lookup(U16M8,SP30). Null->reply1 viafreshM8out+M17override;functionptrnull->14 sameoutput/override',
   'object8bit5 ->indirect(ID,object,18);zero continuesordinary;nonzero writesoutM8 thenfreshM17nonzero returns0,otherwise propagatesfullreply;indirect22 doesnotdirectclearflag',
   'ordinaryhelper(ID,U16M8,U32M12,U16M10,0,(82 iffreshM17nonzero elsefreshM4));exactreply22 clearsoriginalA2 byteandreturns0 WITHOUT directhalfwordoutstore;othernonzeroviaout/M17override',
   'ordinary0 ->freshM17nonzero returns0;otherwisefollowup(ID),nonzero maps22,zero0. Locallysynthesized22 doesnotclearflag'],
  'case22_contract':['lookup(U16M8,SP18);null1,outfreshM8. Optionalcallbackptrnull14writesoutM8;callbacknonzero writesoutM8 andpropagates;zeroordinary',
   'ordinarylookup(ID) firstnonnull skipskeypublication;fallbacklookup(FFFF) nonnull SHoriginalcapturedID toobject0. Bothnull ->9,outfreshM8',
   'probe15 U16heads object4+12*i;firstzero ->copy12M8 toselectedrow andSP20 BEFORElaterrequest. All15occupied ->9,outfreshM8 via4e/50,notindex15',
   'request(ID,23,U16M12,0,16);save returnedpointerSP28,overwriting snapshotword8 formerlyM16. Null ->17,outfreshM8 AFTERslotcopyattempt. Nonnull copy(returnedpointer,freshM16,freshU16M12),thenreport(ID,SP20);report0 ->0,nonzero->22',
   'no explicitflag parameter/store;parentclearsonnormal0. Earlierselectedrow12Bcopy preservesoriginalM16 pointerVALUE underbytecopycontract,notdeepcopy orrollbackproof'],
  'post_contract':'U16M0 must00B0 (typeB0andM1zero);opcode18 additionallyfreshM17==1,opcode27 skipsM17read;matchingtail(ID,1)->4d962/4d9fa,otherwiseRETwithMunchanged. Nostores/frame;parentignoresreply.',
  'premises':'conditionalcandidateISA/provider/queuebindings;validM/outputs/objectslots/callback/stack/source/destination extents;ordinarycalleeS/SP/RA/savedframepreservation;noadversealias/IRQ/DMA/reentry;freshidentity/values separatelyretained',
  'actual_installed_binding_copy_persistence_or_pointer_ownership_lifetime_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-B0-case18-case22-post-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':860,'complete_body_instructions':358,'C_reconstruction_coverage_changed':False,
  'remaining':['recordlookup/table ownership consumers andwrites','ordinary4bb22,callbackpointerlookup,request/report/IDhelper nestedcontracts','actualcopy/providerbindings,slotlifetime andotherwriters'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k])
   for a,d in decode(raw,STARTS[i][k]).items():
    off=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B0cases instructionmutation escaped')
    mutations+=1
   for off,_ in TYPED_LOADS[i][part]:
    bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError as ex:check('typedload encoding' in str(ex),'B0cases typedguard')
    else:raise RuntimeError('B0cases typedmutation escaped')
    typed+=1
 check((mutations,typed)==(358,2),'B0cases mutationcensus');domains()
 print('PASS:358 instruction/2 typed-load mutations rejected;15probe certificates;post/U16/frame/pointerprojection domains')


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
 else:check(OUT.read_bytes()==encoded,'B0cases exactledgerreplay')
 print('PASS:860B/358i complete case18/case22/post;strict HEX;flag/output/publication/parentjoins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,copy/slotpersistence andpayloadlifetime UNPROVED')


if __name__=='__main__':main()
