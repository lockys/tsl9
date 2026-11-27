"""Offline B1 object lookup, selector and fieldwise inversion contracts.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation or RAM/NV/provider/callback state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_downstream_static as previous
import check_v4160_comparator_tail_static as comparator
import check_v4160_app_nv_callbacks_static as copier
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-selector-transform-static.json')
PARTS=('lookup','selector','transform')
STARTS=((0x20000a94,0x6be3c,0x6af42),(0x20000a94,0x6c020,0x6b126))
SOURCES=((0x40d04,0x6be3c,0x6af42),(0x40d44,0x6c020,0x6b126))
SIZES=(50,234,34)
HASHES=(('d2ac1a7a2d7244dd9e73525e0542ea493aff4e711702418d537567f7d29bbaf1', 'ccbfaab933799b17913bc9f1ac03c85a4f1378071c7580fe2ed05d31f1d0466f', '43e3cbe233ebb3efd4863b2b0ffe182c5e65a1bc77876752e4f781a9ec4b623f'), ('7ede47a7527760c3f8fac5c675d99301e3af40c0d1b3b3d8898edb5bca2fd42d', '8f7b4c0ba5666b73a7aef45c5ec0c846c4d55e0d7b26ac71945060c8d8ffc42b', '43e3cbe233ebb3efd4863b2b0ffe182c5e65a1bc77876752e4f781a9ec4b623f'))
COUNTS=((16, 88, 10), (16, 88, 10))
QK=({'lookup': (), 'selector': ((42, '8020', 'qk.c.lbu'), (68, '9c20', 'qk.c.lbu'), (128, '9c20', 'qk.c.lbu'), (152, '9c20', 'qk.c.lbu'), (208, '9c20', 'qk.c.lbu')), 'transform': ((4, '1e21', 'qk.c.lhu'),)}, {'lookup': (), 'selector': ((42, '8020', 'qk.c.lbu'), (68, '9c20', 'qk.c.lbu'), (128, '9c20', 'qk.c.lbu'), (152, '9c20', 'qk.c.lbu'), (208, '9c20', 'qk.c.lbu')), 'transform': ((4, '1e21', 'qk.c.lhu'),)})
TYPED=({'lookup': ((4, 4), (12, 2), (34, 5)), 'selector': ((96, 2),), 'transform': ((16, 4),)}, {'lookup': ((4, 4), (12, 2), (34, 5)), 'selector': ((96, 2),), 'transform': ((16, 4),)})
LITERALS=(
{
'lookup':'''
000 lui 15 536883200
004 load 12 15 948 1
008 lui 15 536883200
00c load 14 15 852 4
010 li 15 0
012 bne 12 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c mv 13 14
01e addi 14 14 60
022 load 11 14 -58 2
026 beq 11 10 24
02a addi 15 15 1
02c andi 15 15 255
030 jump 18
''',
'selector':'''
000 addi 2 2 -48
002 store 2 9 36 4
004 store 2 18 32 4
006 store 2 19 28 4
008 lui 9 536883200
00c store 2 1 44 4
00e store 2 8 40 4
010 store 2 20 24 4
012 li 15 2
014 mv 19 11
016 mv 18 12
018 addi 9 9 -63
01c beq 10 15 138
020 bltu 10 15 62
024 li 15 3
026 beq 10 15 228
02a load 8 9 0 1
02c mv 10 8
02e load 1 2 44 4
030 load 8 2 40 4
032 load 9 2 36 4
034 load 18 2 32 4
036 load 19 2 28 4
038 load 20 2 24 4
03a addi 2 2 48
03c jr 1
03e mv 10 11
040 jal 1 439564
044 load 15 9 0 1
046 mv 8 10
048 bgeu 10 15 44
04c beq 18 0 44
050 li 12 6
052 mv 11 19
054 mv 10 18
056 auipc 1 536428544
05a jalr 1 1 1184
05e jump 44
060 load 15 20 -68 4
064 slli 10 8 4
068 li 12 6
06a add 10 10 15
06c mv 11 19
06e addi 10 10 6
070 auipc 1 536428544
074 jalr 1 1 1430
078 bnez 10 208
07a addi 8 8 1
07c andi 8 8 255
080 load 15 9 0 1
082 bltu 8 15 96
086 mv 8 15
088 jump 44
08a li 8 0
08c lui 20 536883200
090 jump 128
092 addi 8 8 1
094 andi 8 8 255
098 load 15 9 0 1
09a bgeu 8 15 134
09e mul 10 8 20
0a2 mv 12 2
0a4 li 11 16
0a6 addi 10 10 515
0aa slli 10 10 16
0ac srli 10 10 16
0ae jal 1 278722
0b2 bnez 10 146
0b4 li 12 16
0b6 addi 11 0 255
0ba mv 10 2
0bc auipc 1 536428544
0c0 jalr 1 1 1476
0c4 bnez 10 146
0c6 mv 11 19
0c8 mv 10 2
0ca jal 1 286744
0ce bnez 10 146
0d0 load 15 9 0 1
0d2 bgeu 8 15 44
0d6 beq 18 0 44
0da mv 11 18
0dc mv 10 8
0de jal 1 440112
0e2 jump 44
0e4 li 8 0
0e6 li 20 6
0e8 jump 152
''',
'transform':'''
000 addi 14 10 64
004 load 15 10 0 2
006 addi 10 10 4
008 xori 15 15 -1
00c store 10 15 -4 2
010 load 15 10 -2 1
014 xori 15 15 -1
018 store 10 15 -2 1
01c bne 10 14 4
020 jr 1
''',
},
{
'lookup':'''
000 lui 15 536883200
004 load 12 15 1028 1
008 lui 15 536883200
00c load 14 15 932 4
010 li 15 0
012 bne 12 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c mv 13 14
01e addi 14 14 60
022 load 11 14 -58 2
026 beq 11 10 24
02a addi 15 15 1
02c andi 15 15 255
030 jump 18
''',
'selector':'''
000 addi 2 2 -48
002 store 2 9 36 4
004 store 2 18 32 4
006 store 2 19 28 4
008 lui 9 536883200
00c store 2 1 44 4
00e store 2 8 40 4
010 store 2 20 24 4
012 li 15 2
014 mv 19 11
016 mv 18 12
018 addi 9 9 17
01c beq 10 15 138
020 bltu 10 15 62
024 li 15 3
026 beq 10 15 228
02a load 8 9 0 1
02c mv 10 8
02e load 1 2 44 4
030 load 8 2 40 4
032 load 9 2 36 4
034 load 18 2 32 4
036 load 19 2 28 4
038 load 20 2 24 4
03a addi 2 2 48
03c jr 1
03e mv 10 11
040 jal 1 440048
044 load 15 9 0 1
046 mv 8 10
048 bgeu 10 15 44
04c beq 18 0 44
050 li 12 6
052 mv 11 19
054 mv 10 18
056 auipc 1 536428544
05a jalr 1 1 700
05e jump 44
060 load 15 20 12 4
064 slli 10 8 4
068 li 12 6
06a add 10 10 15
06c mv 11 19
06e addi 10 10 6
070 auipc 1 536428544
074 jalr 1 1 946
078 bnez 10 208
07a addi 8 8 1
07c andi 8 8 255
080 load 15 9 0 1
082 bltu 8 15 96
086 mv 8 15
088 jump 44
08a li 8 0
08c lui 20 536883200
090 jump 128
092 addi 8 8 1
094 andi 8 8 255
098 load 15 9 0 1
09a bgeu 8 15 134
09e mul 10 8 20
0a2 mv 12 2
0a4 li 11 16
0a6 addi 10 10 515
0aa slli 10 10 16
0ac srli 10 10 16
0ae jal 1 278870
0b2 bnez 10 146
0b4 li 12 16
0b6 addi 11 0 255
0ba mv 10 2
0bc auipc 1 536428544
0c0 jalr 1 1 992
0c4 bnez 10 146
0c6 mv 11 19
0c8 mv 10 2
0ca jal 1 286896
0ce bnez 10 146
0d0 load 15 9 0 1
0d2 bgeu 8 15 44
0d6 beq 18 0 44
0da mv 11 18
0dc mv 10 8
0de jal 1 440596
0e2 jump 44
0e4 li 8 0
0e6 li 20 6
0e8 jump 152
''',
'transform':'''
000 addi 14 10 64
004 load 15 10 0 2
006 addi 10 10 4
008 xori 15 15 -1
00c store 10 15 -4 2
010 load 15 10 -2 1
014 xori 15 15 -1
018 store 10 15 -2 1
01c bne 10 14 4
020 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B1select literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1select typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1select fullboundaries')
 for a,f in s.items():init.g(n,a,'B1select '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1select Xwchc encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1select completeidentity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1select RET RA');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'B1select linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1select adjacentpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1select closedCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1select allreachable')
 cuts={'lookup':((0x30,0x12),),'selector':((0x82,0x60),(0x94,0x98)),'transform':((0x1c,4),)}[part]
 cut={a:[z for z in qs if (a-pc,z-pc) not in cuts] for a,qs in edges.items()}
 check(not common.acyclic(edges) and common.acyclic(cut),'B1select exactloopcut DAG')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 if part=='selector':
  expected=[(0x40,0x6b50c+484*index),(0x5a,0x20000332),(0x74,0x20000442),(0xae,0x440c2+148*index),(0xc0,0x200004bc),(0xca,0x46018+152*index),(0xde,0x6b730+484*index)]
  check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[pc+0x3c],'B1select all7calltargets/RET')
  saved={(1,44),(8,40),(9,36),(18,32),(19,28),(20,24)}
  check(len(stores)==6 and all(d['base']==2 for d in stores) and {(d['source'],d['imm']) for d in stores}==saved,'B1select frameonly stores')
  check([a-pc for a,d in n.items() if d.get('rd')==18]==[0x16,0x34],'B1select optionaloutput heldS2 untilrestore')
 elif part=='lookup':
  check(not calls and not stores and rets==[pc+0x1a] and not any(d.get('rd') in {1,2,8,9,18,19,20,21,22,23,24,25,26,27} for d in n.values()),'B1select lookup nostores/frame/calls')
 else:
  check(not calls and rets==[pc+0x20] and stores==[dict(offset=0xc,base=10,source=15,imm=-4,bytes=2),dict(offset=0x18,base=10,source=15,imm=-2,bytes=1)],'B1select transform exactfields')
  check({d['rd'] for d in n.values() if 'rd' in d}=={10,14,15} and n[pc]['imm']==64 and n[pc+6]['imm']==4 and n[pc+8]['imm']==n[pc+0x14]['imm']==-1,'B1select transform inversion/stride/end contract')
 return dict(start=pc,source=SOURCES[index][k],bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def checked(b,seq):
 e=b['CFG'];pc=b['start'];check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1select immutablepath');return seq


def paths(b,part):
 if part=='lookup':return {'empty':common.walk(b,{0x12:0x16}),'firstmatch':common.walk(b,{0x12:0x1c,0x26:0x18}),
  'one_mismatch_then_exhaust':checked(b,[0,4,8,0xc,0x10,0x12,0x1c,0x1e,0x22,0x26,0x2a,0x2c,0x30,0x12,0x16,0x18,0x1a])}
 if part=='transform':
  unit=[4,6,8,0xc,0x10,0x14,0x18,0x1c];seq=checked(b,[0]+unit*16+[0x20])
  check(seq.count(0xc)==seq.count(0x18)==16,'B1select transform16fieldstore witnesses');return {'16steps':seq}
 base={0x1c:0x20,0x20:0x24,0x26:0x2a}
 choices={'other_type_returns_freshcount':base,
  'type01_return_helper_outofrange':{0x1c:0x20,0x20:0x3e,0x48:0x2c},
  'type01_B1_outputnull':{0x1c:0x20,0x20:0x3e,0x48:0x4c,0x4c:0x2c},
  'type01_copy6':{0x1c:0x20,0x20:0x3e,0x48:0x4c,0x4c:0x50},
  'type2_count0':{0x1c:0x8a,0x82:0x86},
  'type2_match_B1_nooutput':{0x1c:0x8a,0x82:0x60,0x78:0xd0,0xd2:0xd6,0xd6:0x2c},
  'type3_count0':{0x1c:0x20,0x20:0x24,0x26:0xe4,0x9a:0x86},
  'type3_match_B1_nooutput':{0x1c:0x20,0x20:0x24,0x26:0xe4,0x9a:0x9e,0xb2:0xb4,0xc4:0xc6,0xce:0xd0,0xd2:0xd6,0xd6:0x2c},
  'type3_match_optionaloutput':{0x1c:0x20,0x20:0x24,0x26:0xe4,0x9a:0x9e,0xb2:0xb4,0xc4:0xc6,0xce:0xd0,0xd2:0xd6,0xd6:0xda}}
 ps={label:common.walk(b,c) for label,c in choices.items()}
 check(all(0x5a not in ps[k] and 0xde not in ps[k] for k in ('type01_B1_outputnull','type2_match_B1_nooutput','type3_match_B1_nooutput')),'B1select B1 O0 excludes localoutputcalls')
 return ps


def domains():
 for x in range(65536):check(((~((~x)&65535))&65535)==x,'B1select U16 inversion scalar involution')
 for x in range(256):check(((~((~x)&255))&255)==x,'B1select U8 inversion scalar involution')
 keys={4*i+j for i in range(16) for j in (0,1)};vals={4*i+2 for i in range(16)};pads={4*i+3 for i in range(16)}
 check(len(keys)==32 and len(vals)==len(pads)==16 and keys|vals|pads==set(range(64)) and not(keys|vals)&pads,'B1select 48modified/16untouched footprint')
 for k in range(1,17):check((4*k)%2**32==64 if k==16 else (4*k)%2**32!=64,'B1select stridefirstend equality at16')
 for i in range(256):
  for N in range(256):
   if i<N:check(i<=254 and (i+1)&255==i+1,'B1select freshcount bound no admittedwrap')
 check(515+6*254==2039 and 16*254+6+6==4076 and 60*254+2+2==15244,'B1select admitted source arithmetic bounds')
 for n in range(256):check(n==0 or 60*(n-1)+4<=60*n,'B1select lookup count/stride extent')
 return dict(U16_involution_cases=65536,U8_involution_cases=256,index_freshcount_pairs=65536,transform_iterations=16,
  transform_selected_field_bytes=48,transform_untouched_padding_bytes=16,transform_reply='entryB+64 mod32;notforcedstatus',
  double_application_identity='scalar field algebra only,requirescompletevalidstores/stabledata/nointerveningwrites;updaterchangesfieldvaluesbetweenitscalls',
  optional_output='actualB1 O=0 heldS2;localcopy6/helperoutcalls skipped,not a transitive no-side-effect claim',
  fresh_counts='selector candidate validation/exhaustion andparent admission eachsamplecount separately;equalvalues notproved',
  target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={};mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy']
 def source(target):return int(f['source'],16)+target-int(f['destination'],16)
 check(source(0x20000a94)==SOURCES[index][0] and 0x20000a94+50<=int(mapping['first_copy_end_exclusive'],16),'B1select complete lookup linkedmapping')
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,SOURCES[index][k],SIZES[k]);check(sparse.captured(mem,SOURCES[index][k],SIZES[k])==raw,'B1select allbodies originalHEX');bs[part]=body(raw,part,index)
 n={part:{v['pc']-b['start']:v for v in b['instructions']} for part,b in bs.items()};G=0x20003000
 l,s,t=n['lookup'],n['selector'],n['transform']
 check(l[0]['imm']+l[4]['imm']==G+948+80*index and l[8]['imm']+l[0xc]['imm']==G+852+80*index and l[0x1e]['imm']==60 and l[0x22]['imm']==-58,'B1select distinct lookupcount/array/keystride')
 check(s[8]['imm']+s[0x18]['imm']==G-63+80*index and s[0x60]['imm']+G==G-68+80*index and s[0x64]['imm']==4,'B1select selector count/pool sources')
 check(s[0x68]['imm']==6 and s[0xb4]['imm']==16 and s[0xb6]['imm']==255 and s[0xa6]['imm']==515 and s[0xaa]['imm']==s[0xac]['imm']==16,'B1select comparedomain andNVnumericaddress')
 pd=parent['bodies']['dispatch'];dn={v['pc']-pd['start']:v for v in pd['instructions']}
 check(pd['calls'][0]['target']==bs['lookup']['start'] and pd['calls'][1]['target']==bs['selector']['start'] and dn[0x2a]['imm']==5 and dn[0x26]['imm']==6 and dn[0x2c]['imm']==0,'B1select actualB1 lookupP/type/Q/output0 join')
 up=parent['bodies']['update'];un={v['pc']-up['start']:v for v in up['instructions']}
 check([c['target'] for c in up['calls'] if c['offset'] in (0x5c,0x92)]==[bs['transform']['start']]*2 and un[0x5a]['imm']==16 and un[0x8c]['imm']==16,'B1select updater bothtransforms useSP16')
 reuse={}
 for name,target,z in [('comparator',0x20000442,72),('predicate',0x200004bc,62),('copy',0x20000332,58)]:
  src=source(target);raw=init.binding.take(data,src,z);check(target+z<=int(mapping['first_copy_end_exclusive'],16) and sparse.captured(mem,src,z)==raw,'B1select reusedleaf originalHEX/mapping')
  if name=='comparator':b=comparator.body(raw,'comparator',index)
  elif name=='predicate':b=previous.predicate.body(raw,'predicate',index)
  else:b=copier.body(raw,'copy',target,18,init.binding.COPY_HASH)
  reuse[name]=dict(source=src,target=target,bytes=z,sha256=sha256(raw).hexdigest(),new_code_bytes_counted=0,installed_binding_proved=False)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},reused_leaves=reuse,
  lookup_contract=['captureU8count thenU32array once,evencount0loadsarrayword. index0..N-1,stride60,freshU16record2 comparedtofullentryID;firstmatchreturnsrecordbase,exhausted0',
   'no frame/stores/calls/nullguard;capturedN<=255 boundsprobes beforeindexwrap;recordarray/extent/identity/crossreads remainconditional'],
  selector_contract=['fulltype0/1 ->6b50c/6b6f0(Q),capturefullindexR;freshcount testonlygates optionaloutputcopy6(O,Q,6);returnR evenifoutofrange',
   'type2 ->index0;perstepfreshcount/poolword,compare20000442(pool+16*i+6,Q,6);nonzero selects,zero incrementlow8. Matchingcomparator null-success stillretained',
   'type3 ->index0;read440c2/44156(low16(515+6*i),16,SP);nonzero skip;predicate(SP,255,16)nonzero skip;46018/460b0(SP,Q)zero selects,nonzero skip. Transferunits/comparecallee semanticsnotinferred',
   'type2/3 candidate rechecks freshcount;optionalO nonzero andcandidatevalid ->6b730/6b914(index,O);returncapturedindex eitherway. Exhaustionreturnsmostrecentcount,notearlierindex. Otherfulltype ->freshcount',
   'B1passesO0:underS2/framepreservation bothlocaloptionaloutputcalls skipped. Allothercallee/borrowedquery/NV sideeffects remainpossible'],
  transform_contract=['no nullguard/frame/calls;end=B+64mod32.16 stride4steps: freshU16slot0,SHlow16NOTtosamekey;freshU8slot2,SBlow8NOTtosamevalue',
   'slot3neverread/writtenbythisleaf;A0normalreply=endpointer. OnlyGPRsA0/A4/A5written;no originalpointerregister directstore. Validaccess/noalias/physicaleffects/preservation remainpremises',
   'updaterlocalbufferSP16..79 ->exact32keybytes+16valuebytes,16paddingbytesuntouchedbytransform. Firstandsecondapplicationareseparatedbyupdates;no cancellationclaim'],
  composition=['lookuprecord P ->B1 selector(freshU8P5,P6,0);subsequentselector/parentcount samples canchange. Parentindexadmission0doesnotproveearliermatch orvalidextent',
   'transformsclarify encodedfieldrepresentation only:NVread/writeextents,stackbuffer retention andactualstoredbytes remainunproved. H0wholefill maychange padding even though transformsandrecordSH/SB do not'],
  premises='conditionalcandidateISA/provider/firstcopymapping;validcode/frame/query/row/pool/buffer extents;ordinarycalleeS/SP/RA/savedframepreservation;noadversealias/wrap/IRQ/DMA/reentry;allfreshsnapshot equalities separate',
  installedbinding_NV_output_queryretention_realreachability_or_completepointerlifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-lookup-selector-fieldinvert-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_new_body_bytes=636,complete_new_body_instructions=228,reused_leaf_bytes=384,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['selectorhelper6b50c/46018/6b730 completecontracts','NV440c2/4435c bufferextent/units/retention','actualconfigcallback/contextwriter andprovider lifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1select instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1select typedmutation escaped')
    typed+=1
 check((mutations,typed)==(228,10),'B1select mutationcensus');domains()
 print('PASS:228 instruction/10 typed-load mutations rejected;U16/U8 inversion,fieldfootprint,16steps/freshcount certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1select exactledger replay')
 print('PASS:636B/228i complete lookup/selector/fieldinvert;strict HEX;B1 output0 andpadding preservation joins;exact ledger')
 print('PASS:NO target execution/emulation;NV/provider bindings,retention andpointerlifetime UNPROVED')


if __name__=='__main__':main()
