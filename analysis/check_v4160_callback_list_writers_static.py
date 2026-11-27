"""Offline callback-list append/remove, paired detach and once-gated wrapper.
Original operands/CFG, immutable path and host scalar/interval certificates.
No target execution/emulation, provider, register/RAM/heap/list model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_typeb0_record_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-callback-list-writers-static.json')
PARTS=('append','remove','detach','wrapper')
STARTS=((0x4cf22,0x4b830,0x4b7d8,0x4cf96),(0x4cfba,0x4b8c8,0x4b870,0x4d02e))
SIZES=(116,92,88,48)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('7023ea87d03b31c404410530970f27b7607358ae35817c716feadb6f46c04e9a', '6ac92c62d4e78f9e6b93856c9ae43cddc09ad73c4b1a62b8c09877a75f74380e', '01495715c89898603820e93905d5804b4b769d63f75f2a8520ffa4269fe3f2bf', '411520bf2973aea970831710e86c6be108f759be1e0078739d2fb0aafda142c7'), ('00e252250cca547d088e56dc5df2375891edbefb54df4b63b67cdc050bb20cd1', '3185efe4cff6dc2625f73ab55a9a070c259f38f5947d763197a2bc645de30100', '74098d949fec685f9ff0f659007326efa20840177d8de72b87436585f6c7066e', 'c32c05de77be74177f6bb3ed51d79facb4bcdd75c87865cb9273e5a61cf07135'))
COUNTS=((49, 38, 35, 17), (49, 38, 35, 17))
TYPED_LOADS=({'append': (), 'remove': ((4, 2), (16, 5)), 'detach': ((10, 2),), 'wrapper': ()}, {'append': (), 'remove': ((4, 2), (16, 5)), 'detach': ((10, 2),), 'wrapper': ()})
LITERALS=(
{
'append':'''
000 addi 2 2 -32
002 store 2 1 28 4
004 store 2 8 24 4
006 store 2 9 20 4
008 store 2 18 16 4
00a bnez 10 28
00c li 9 2
00e load 1 2 28 4
010 load 8 2 24 4
012 mv 10 9
014 load 18 2 16 4
016 load 9 2 20 4
018 addi 2 2 32
01a jr 1
01c store 2 10 12 4
01e mv 8 10
020 addi 10 2 8
022 mv 18 13
024 store 2 11 8 2
026 store 2 12 10 1
028 jal 1 314914
02c mv 9 10
02e bnez 10 14
030 beq 18 0 14
034 load 15 8 10 2
036 beqz 15 12
038 lui 11 16384
03a addi 11 11 1797
03e li 10 12
040 auipc 1 536555520
044 jalr 1 1 222
048 beqz 10 112
04a load 15 8 10 2
04c store 10 0 0 4
050 store 10 18 8 4
054 store 10 15 4 2
056 lui 15 536883200
05a addi 15 15 -108
05e load 14 15 0 4
060 bnez 14 104
062 store 15 10 0 4
064 jump 14
066 mv 14 15
068 load 15 14 0 4
06a bnez 15 102
06c store 14 10 0 4
06e jump 14
070 li 9 19
072 jump 14
''',
'remove':'''
000 lui 14 536883200
004 load 15 14 -108 4
008 li 12 0
00a addi 14 14 -108
00e beqz 15 88
010 load 16 15 4 2
014 load 13 15 0 4
016 bne 16 10 78
01a addi 2 2 -32
01c store 2 1 28 4
01e store 2 8 24 4
020 store 2 9 20 4
022 beqz 12 84
024 store 12 13 0 4
026 mv 9 10
028 mv 10 15
02a mv 8 11
02c auipc 1 536563712
030 jalr 1 1 -1868
034 addi 11 2 8
036 mv 10 9
038 jal 1 309208
03c bnez 10 68
03e beqz 8 68
040 load 15 2 12 4
042 store 8 15 0 4
044 load 1 2 28 4
046 load 8 2 24 4
048 load 9 2 20 4
04a addi 2 2 32
04c jr 1
04e mv 12 15
050 mv 15 13
052 jump 14
054 store 14 13 0 4
056 jump 38
058 li 10 1
05a jr 1
''',
'detach':'''
000 addi 2 2 -16
002 lui 15 536883200
006 store 2 8 8 4
008 store 2 1 12 4
00a load 8 15 -120 4
00e li 13 0
010 addi 15 15 -120
014 beqz 8 84
016 load 14 8 8 4
018 load 12 14 10 2
01a load 14 8 0 4
01c bne 12 10 74
020 beqz 13 80
022 store 13 14 0 4
024 mv 10 11
026 beqz 11 54
028 li 12 8
02a addi 11 8 4
02e auipc 1 536563712
032 jalr 1 1 -1236
036 mv 10 8
038 auipc 1 536563712
03c jalr 1 1 -1792
040 li 10 0
042 load 1 2 12 4
044 load 8 2 8 4
046 addi 2 2 16
048 jr 1
04a mv 13 8
04c mv 8 14
04e jump 20
050 store 15 14 0 4
052 jump 36
054 li 10 1
056 jump 66
''',
'wrapper':'''
000 lui 15 536883200
004 addi 15 15 -132
008 load 14 15 0 1
00a bnez 14 44
00c li 14 1
00e store 15 14 0 1
010 andi 10 10 1
012 beqz 10 44
014 lui 13 536883200
018 lui 10 536883200
01c addi 13 13 -324
020 li 12 16
022 li 11 4
024 addi 10 10 -388
028 jal 0 315170
02c li 10 0
02e jr 1
''',
},
{
'append':'''
000 addi 2 2 -32
002 store 2 1 28 4
004 store 2 8 24 4
006 store 2 9 20 4
008 store 2 18 16 4
00a bnez 10 28
00c li 9 2
00e load 1 2 28 4
010 load 8 2 24 4
012 mv 10 9
014 load 18 2 16 4
016 load 9 2 20 4
018 addi 2 2 32
01a jr 1
01c store 2 10 12 4
01e mv 8 10
020 addi 10 2 8
022 mv 18 13
024 store 2 11 8 2
026 store 2 12 10 1
028 jal 1 315066
02c mv 9 10
02e bnez 10 14
030 beq 18 0 14
034 load 15 8 10 2
036 beqz 15 12
038 lui 11 16384
03a addi 11 11 1797
03e li 10 12
040 auipc 1 536555520
044 jalr 1 1 70
048 beqz 10 112
04a load 15 8 10 2
04c store 10 0 0 4
050 store 10 18 8 4
054 store 10 15 4 2
056 lui 15 536883200
05a addi 15 15 -28
05e load 14 15 0 4
060 bnez 14 104
062 store 15 10 0 4
064 jump 14
066 mv 14 15
068 load 15 14 0 4
06a bnez 15 102
06c store 14 10 0 4
06e jump 14
070 li 9 19
072 jump 14
''',
'remove':'''
000 lui 14 536883200
004 load 15 14 -28 4
008 li 12 0
00a addi 14 14 -28
00e beqz 15 88
010 load 16 15 4 2
014 load 13 15 0 4
016 bne 16 10 78
01a addi 2 2 -32
01c store 2 1 28 4
01e store 2 8 24 4
020 store 2 9 20 4
022 beqz 12 84
024 store 12 13 0 4
026 mv 9 10
028 mv 10 15
02a mv 8 11
02c auipc 1 536563712
030 jalr 1 1 -2020
034 addi 11 2 8
036 mv 10 9
038 jal 1 309360
03c bnez 10 68
03e beqz 8 68
040 load 15 2 12 4
042 store 8 15 0 4
044 load 1 2 28 4
046 load 8 2 24 4
048 load 9 2 20 4
04a addi 2 2 32
04c jr 1
04e mv 12 15
050 mv 15 13
052 jump 14
054 store 14 13 0 4
056 jump 38
058 li 10 1
05a jr 1
''',
'detach':'''
000 addi 2 2 -16
002 lui 15 536883200
006 store 2 8 8 4
008 store 2 1 12 4
00a load 8 15 -40 4
00e li 13 0
010 addi 15 15 -40
014 beqz 8 84
016 load 14 8 8 4
018 load 12 14 10 2
01a load 14 8 0 4
01c bne 12 10 74
020 beqz 13 80
022 store 13 14 0 4
024 mv 10 11
026 beqz 11 54
028 li 12 8
02a addi 11 8 4
02e auipc 1 536563712
032 jalr 1 1 -1388
036 mv 10 8
038 auipc 1 536563712
03c jalr 1 1 -1944
040 li 10 0
042 load 1 2 12 4
044 load 8 2 8 4
046 addi 2 2 16
048 jr 1
04a mv 13 8
04c mv 8 14
04e jump 20
050 store 15 14 0 4
052 jump 36
054 li 10 1
056 jump 66
''',
'wrapper':'''
000 lui 15 536883200
004 addi 15 15 -52
008 load 14 15 0 1
00a bnez 14 44
00c li 14 1
00e store 15 14 0 1
010 andi 10 10 1
012 beqz 10 44
014 lui 13 536883200
018 lui 10 536883200
01c addi 13 13 -248
020 li 12 16
022 li 11 4
024 addi 10 10 -312
028 jal 0 315322
02c li 10 0
02e jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'CBwriter literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'CBwriter typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'CBwriter completeboundaries '+part)
 for a,f in s.items():init.g(n,a,'CBwriter operand '+part+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'CBwriter completeidentity '+part)
 edges={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'CBwriter ordinaryRET');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op in ('jal','jalr'):
   if op=='jal':t=d['target']
   else:
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1'],'CBwriter adjacentpair');t=(a-4+u['imm']+d['imm'])&0xfffffffe
   check(d['rd'] in (0,1),'CBwriter linkclass')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=t,new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=t))
  check(all(z in n for z in q),'CBwriter closedlocalCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'CBwriter allnodesreachable')
 loop=((0x6a,0x66),(0x52,0xe),(0x4e,0x14),None)[k]
 cut={a:[z for z in qs if loop is None or (a,z)!=(pc+loop[0],pc+loop[1])] for a,qs in edges.items()}
 check(common.acyclic(cut) and common.acyclic(edges)==(loop is None),'CBwriter cycleedgecut')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 check((len(calls),len(tails),len(rets),len(stores))==((2,0,1,12),(2,0,2,6),(2,0,1,4),(0,1,1,1))[k],'CBwriter call/tail/return/storecensus')
 if part!='wrapper':
  # Match only actual callee-saved/RA slots, excluding append descriptor SP12.
  expected=({'append':{(1,28),(8,24),(9,20),(18,16)},'remove':{(1,28),(8,24),(9,20)},'detach':{(1,12),(8,8)}})[part]
  actual={(d['source'],d['imm']) for d in stores if (d['source'],d['imm']) in expected and d['base']==2}
  restores={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and (d['rd'],d['imm']) in expected}
  check(actual==restores==expected,'CBwriter savedframe restores')
 else:check(tails==[dict(offset=0x28,target=STARTS[index][0],new_link=False)],'CBwriter wrapperunlinkedappendtail')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=rets,stores=stores,cycle_edge=loop,complete_local_body=True,target_execution_or_emulation=False)


def checked(b,seq):
 pc=b['start'];e=b['CFG'];s=[pc+o for o in seq]
 check(s[0]==pc and not e[s[-1]] and all(z in e[a] for a,z in zip(s,s[1:])),'CBwriter immutablefullpath certificate');return seq


def append_paths(b):
 before={0xa:0x1c,0x2e:0x30,0x30:0x34,0x36:0x38}
 choices={'nullconfig_reply2':{0xa:0xc},'validator_nonzero':{0xa:0x1c,0x2e:0xe},
  'validator0_nullcallback_reply0':{0xa:0x1c,0x2e:0x30,0x30:0xe},
  'configkey0_reply2':{**before,0x36:0xc},'allocationnull_reply19':{**before,0x48:0x70},
  'emptylist_publish':{**before,0x48:0x4a,0x60:0x62},'one_existing_append':{**before,0x48:0x4a,0x60:0x68,0x6a:0x6c}}
 paths={k:common.walk(b,v) for k,v in choices.items()}
 seq=paths['one_existing_append'];pos=seq.index(0x68);paths['two_existing_append']=checked(b,seq[:pos]+[0x68,0x6a,0x66]+seq[pos:])
 for name in ('emptylist_publish','one_existing_append','two_existing_append'):
  seq=paths[name];check(seq.index(0x4c)<seq.index(0x50)<seq.index(0x54)<seq.index(0x62 if 0x62 in seq else 0x6c),'CBwriter nodeinitializedbeforepublishingpointer')
 check(0x44 not in paths['validator0_nullcallback_reply0'] and 0x28 in paths['validator0_nullcallback_reply0'],'CBwriter nullcallback0 stillrunsvalidator butnoallocation')
 check(all(0x62 not in paths[k] and 0x6c not in paths[k] for k in ('nullconfig_reply2','validator_nonzero','validator0_nullcallback_reply0','configkey0_reply2','allocationnull_reply19')),'CBwriter failurepaths nonodepublication')
 return {'selected':paths,'finite_valid_distinct_list_required_for_tailappend':True,'duplicatekey_absence_deepcopy_or_actualobjectlifetime_proved':False}


def removal_paths(r,d):
 found={0xe:0x10,0x16:0x1a,0x22:0x54}
 choices={'notfound':{0xe:0x58},'primaryremoved_secondarymissing':{**found,0x3c:0x44},
  'bothremoved_nooutput':{**found,0x3c:0x3e,0x3e:0x44},'bothremoved_outputword':{**found,0x3c:0x3e,0x3e:0x40},
  'primary_interior_output':{**found,0x22:0x24,0x3c:0x3e,0x3e:0x40}}
 paths={k:common.walk(r,v) for k,v in choices.items()};seq=paths['primaryremoved_secondarymissing']
 check(seq.index(0x54)<seq.index(0x30)<seq.index(0x38) and 0x42 not in seq,'CBwriter primaryunlink/freeattempt precedessecondaryfailure;nooutputwrite')
 ds={k:common.walk(d,v) for k,v in {
  'notfound':{0x14:0x54},'headmatch_copy':{0x14:0x16,0x1c:0x20,0x20:0x50,0x26:0x28},
  'headmatch_nocopy':{0x14:0x16,0x1c:0x20,0x20:0x50,0x26:0x36},
  'interiormatch_copy':{0x14:0x16,0x1c:0x20,0x20:0x22,0x26:0x28}}.items()}
 for name in ('headmatch_copy','interiormatch_copy'):
  seq=ds[name];check(seq.index(0x32)<seq.index(0x3c)<seq.index(0x40),'CBwriter snapshotcopy beforesecondarynodefree thenforced0')
 return {'primary_selected':paths,'secondary_selected':ds,'primaryfailure_after_mutation_possible':True,
  'outputword_source':'secondarynode+8 copied toparentSP12 under8-bytecopycontract,notprimarynode8',
  'matched_nodes_same_object_or_actualfree_completion_proved':False}


def wrapper_paths(b):
 ps={k:common.walk(b,v) for k,v in {'flagalreadyset':{0xa:0x2c},'first_selector_even':{0xa:0xc,0x12:0x2c},'first_selector_odd_tail':{0xa:0xc,0x12:0x14}}.items()}
 check(0xe not in ps['flagalreadyset'] and 0xe in ps['first_selector_even'] and 0xe in ps['first_selector_odd_tail'],'CBwriter latchstore beforebitgate andtail')
 check(ps['first_selector_odd_tail'].index(0xe)<ps['first_selector_odd_tail'].index(0x28),'CBwriter latchsetbeforeappendoutcome')
 return {'selected':ps,'latched_even_when_selector_even_or_appendfails_under_no_other_writer_premise':True,'threadsafe_once_or_actualretry_policy_proved':False}


def domains():
 nodewrites=set(range(0,6))|set(range(8,12));check(set(range(12))-nodewrites=={6,7},'CBwriter node6/7notdirectlyinitialized')
 for latch in range(256):
  for selector in range(256):
   tail=latch==0 and bool(selector&1)
   check(tail==(not latch and selector%2==1),'CBwriter latch/bit0gate scalar')
 check(not set(range(8,16))&set(range(20,32)),'CBwriter secondarysnapshot avoidsprimarysavedslots')
 check(8+(8-4)==12 and 12+4<=16,'CBwriter copiedsecondarynode8 ->parentSP12 projection')
 check(4+2<=12 and 8+4==12,'CBwriter callbacknodeword extents')
 return {'latch_selector_byte_cases':65536,'node_bytes_directly_written':sorted(nodewrites),'node_gap':[6,7],
  'descriptor_partial_layout':{'halfword8':'low16entryA1','byte10':'low8entryA2','byte11':'notdirectlywritten','word12':'originalconfigpointer'},
  'actualcallbackrecord_extent_identity_or_nonretention_proved':False}


def profile(data,hexraw,index,parent):
 bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
 a,r,d,w=(bs[x] for x in PARTS);ns={part:{v['pc']-bs[part]['start']:v for v in bs[part]['instructions']} for part in PARTS};an,rn,dn,wn=(ns[x] for x in PARTS)
 G=0x20003000;H=G-108+80*index;H2=G-120+80*index;flag=G-132+80*index;cfg=G-388+76*index;obj=G-324+76*index
 check(an[0x56]['imm']+an[0x5a]['imm']==H and rn[0]['imm']+rn[4]['imm']==H and dn[2]['imm']+dn[0xa]['imm']==H2,'CBwriter primary/secondaryhead roles')
 check(a['calls']==[dict(offset=0x28,target=0x4ce22+152*index),dict(offset=0x44,target=0x20000040)],'CBwriter appendvalidator andalloc12 calls')
 check(r['calls']==[dict(offset=0x30,target=0x20000110),dict(offset=0x38,target=d['start'])] and d['calls']==[dict(offset=0x32,target=0x20000332),dict(offset=0x3c,target=0x20000110)],'CBwriter pairedunlink/free/copy calltargets')
 check(an[0x1e]['rd']==8 and an[0x1e]['rs2']==10 and an[0x22]['rd']==18 and an[0x22]['rs2']==13,'CBwriter distinctoriginalconfigA0 andcallbackobjectA3')
 check(an[0x34]['rs1']==an[0x4a]['rs1']==8 and an[0x34]['imm']==an[0x4a]['imm']==10,'CBwriter keyfreshconfig10 notdescriptorSP10')
 check(an[0x3e]['imm']==12 and an[0x38]['imm']+an[0x3a]['imm']==0x4705 and an[0x50]['rs2']==18,'CBwriter request12/tag4705 andborrowedobjectnode8')
 check(dn[0x16]['imm']==8 and dn[0x18]['rs1']==14 and dn[0x18]['imm']==10,'CBwriter secondarykey nested node8pointee10 notnode10')
 check(rn[0x28]['rs2']==15 and dn[0x36]['rs2']==8 and rn[0x40]['imm']==12 and rn[0x42]['rs1']==8,'CBwriter freesNODE thenoutputssecondarysnapshotword')
 check(wn[0]['imm']+wn[4]['imm']==flag and wn[0x14]['imm']+wn[0x1c]['imm']==obj and wn[0x18]['imm']+wn[0x24]['imm']==cfg,'CBwriter wrapperflagshift80 vsobjectshift76')
 check(wn[0xe]['rs2']==14 and wn[0xc]['imm']==1 and wn[0x20]['imm']==16 and wn[0x22]['imm']==4,'CBwriter latchbeforeappend andfixedarguments')
 # Known reader returns node8 value, wrapper then reads that object's +8.
 getter=parent['bodies']['callbackrecord'];gn={v['pc']-getter['start']:v for v in getter['instructions']}
 check(gn[4]['imm']+G==H and gn[0x10]['imm']==8,'CBwriter exactknownreaderhead/valuejoin')
 origin=previous.previous.previous.origin
 op=origin.STARTS[index][2];defaults=origin.body(init.binding.take(data,op,248),'defaults',index);on={v['pc']-op:v for v in defaults['instructions']}
 check(on[70]['imm']+G==H and on[78]['imm']+G==H2 and on[104]['imm']+G==flag,'CBwriter knowninitialhead/flagclear source')
 check(on[228]['imm']+G==obj and on[236]['rs2']==0 and on[242]['rs2']==0 and on[242]['imm']==8,'CBwriter callbackobjectinitialword8zero,notinferredinstalledfunction')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for part,z in bs.items():
  check(sparse.captured(mem,z['start'],z['bytes'])==init.binding.take(data,z['start'],z['bytes']),'CBwriter originalstrictHEX backing')
  receipts.append({'part':part,'source':z['start'],'bytes':z['bytes'],'all_bytes_captured':True})
 return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{part:common.certificates(z) for part,z in bs.items()},
  'append_paths':append_paths(a),'removal_paths':removal_paths(r,d),'wrapper_paths':wrapper_paths(w),
  'globals':dict(primary_head=H,secondary_head=H2,latch_byte=flag,wrapper_config=cfg,wrapper_callback_object=obj),
  'source_reuse':dict(ID11defaults=op,sha256=defaults['sha256'],new_code_bytes_counted=0),
  'append_contract':['configA0null ->2;elseborrowSP8descriptor(low16A1,low8A2,originalconfigword),captureoriginalA3object;validatorfullreplynonzero propagated',
   'validator0+objectnull ->0 withoutnodeallocation/publication. Objectnonnull ->freshU16config10 nonzero else2;allocate12/tag4705,null19',
   'node0=0,node8=originalA3pointer,node4=freshU16config10 AFTERallocator;bytes6..7notdirectlywritten. Emptyhead publishelseappendatfirstnullnext;return0 underpreservation. No deepcopy,uniqueness,count/cycleguard orrollbackproof'],
  'remove_contract':['fullentrykey compareU16node4 inprimarylist;firstmatch unlinkcachednext,privatefree(matchedNODE),then secondarydetach(originalkey,parentSP8). Primarymissing1 beforeframe',
   'secondaryreply propagated;only0 andoriginalA1nonnull writesU32[originalA1]=U32parentSP12 fromsecondarysnapshot. Secondarymissing1 canfollowprimarymutation/releaseattempt. Primarynode8objectnotdirectlyfreed orusedasreturnoutput'],
  'detach_contract':['independenthead;matchfullkey againstU16[U32node8 +10],notnode10. Unlinkfirstmatch,ifoutputnonnull copy8(node4->output),privatefree(node),force0;missing1',
   'copy/free repliesignored;originalobjectatnode8 notdirectlyfreed. Returnedsnapshotobject can differfromprimarynode8 withoutcross-listidentity/uniquenessproof'],
  'wrapper_contract':'freshlatchnonzero ->0;zero ->store1 BEFORE testingentrybit0;even ->0,odd ->unlinkedappend(cfg,4,16,obj). No localreset evenappendfailure;fixedobjectaddresses shift76 whileflag/head shift80',
  'ownership_boundary':'writerretainsoriginalA3 objectpointer byvalue inheapnode;readerlaterdereferences object8. Object/embeddedcallbacklifetime,validator/provider behavior andallwriters notclosed;partialtwo-listremoval isnotatomic ownership handoff.',
  'premises':'conditionalcandidateISA/provider/sourcebindings;validconfig/object/node/list/frame/copy/output extents;finite validlists,distinctnodes/nonadversealias;ordinarycalleeS/SP/RA/savedframepreservation;noIRQ/DMA/reentry/unaccountedwriters;freshkey/objectidentityseparatelyretained',
  'actual_installed_binding_allwriters_objectownership_or_nonretention_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-callbacklist-writers-pairedremove-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':688,'complete_body_instructions':278,'C_reconstruction_coverage_changed':False,
  'remaining':['validator4ce22/4ceba andcallbackobject8writers','pairedlistinsertion/objectsource andactualwrappercallers','actualproviderbindings,allwriters,object/embeddedfunctionlifetime andconsumercontracts'],
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
    else:raise RuntimeError('CBwriter instructionmutation escaped')
    mutations+=1
   for off,_ in TYPED_LOADS[i][part]:
    bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError as ex:check('typedload encoding' in str(ex),'CBwriter typedguard')
    else:raise RuntimeError('CBwriter typedmutation escaped')
    typed+=1
 check((mutations,typed)==(278,6),'CBwriter mutationcensus');domains()
 print('PASS:278 instruction/6 typed-load mutations rejected;65536 latch/selector cases;node/descriptor/snapshot/frame domains')


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
 else:check(OUT.read_bytes()==encoded,'CBwriter exactledgerreplay')
 print('PASS:688B/278i complete callbacklist append/remove/detach/wrapper;strict HEX;source/reader/partialremoval joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,allwriters,object/embeddedcallback lifetime UNPROVED')


if __name__=='__main__':main()
