"""Offline selector pool search, optional output and check wrapper contracts.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation, NV/provider/worker/RAM/callback model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_selector_transform_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-selector-callees-static.json')
PARTS=('poolfind','output','veneer','check3')
STARTS=((0x6b50c,0x6b730,0x46018,0x50040),(0x6b6f0,0x6b914,0x460b0,0x500da))
SIZES=(82,74,4,90)
HASHES=(('c31b0eb8847ed855b5501179e87abfb1ac307f39ffb3105f2f67d2fbaf084e2c', '8f23e3d332bade6c4525ef9d1ac5b9d444538c3d61dc956be0b24a77e050de2a', 'e9d93dfea09f5921941c86b2e083077b4613745355cb8624639c9c85dc92dc04', 'b98188c66f15f4771e7f7df3edcdf5769a90c90d749e6d56adaa77dbc4f1d44d'), ('f4b6b7c99021a45fac19cabf13803c70b5794c6b8bdff62a76f57edbfa1be082', '1476569bda6643c223859fc9111f39c97be4a1e595c6a0131057254229612da5', '937d927cd9aede0763004a5c60477f5920290e63f519cdb51ec7ac1b3aef9ad8', 'fa43ca07501bbcd647083283d330b012cc2dd547d9aa1514141acb86ae0c84f2'))
COUNTS=((32, 29, 1, 37), (32, 29, 1, 37))
QK=({'poolfind': (), 'output': (), 'veneer': (), 'check3': ((32, '1c85', 'qk.c.lbusp'), (48, '5c85', 'qk.c.sbsp'))}, {'poolfind': (), 'output': (), 'veneer': (), 'check3': ((32, '1c85', 'qk.c.lbusp'), (48, '5c85', 'qk.c.sbsp'))})
TYPED=({'poolfind': ((24, 4), (50, 2)), 'output': ((4, 4),), 'veneer': (), 'check3': ()}, {'poolfind': ((24, 4), (50, 2)), 'output': ((4, 4),), 'veneer': (), 'check3': ()})
LITERALS=(
{
'poolfind':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 19 12 4
00a store 2 1 28 4
00c mv 18 10
00e li 8 0
010 lui 9 536883200
014 lui 19 536883200
018 load 15 9 -63 1
01c bltu 8 15 50
020 mv 8 15
022 mv 10 8
024 load 1 2 28 4
026 load 8 2 24 4
028 load 9 2 20 4
02a load 18 2 16 4
02c load 19 2 12 4
02e addi 2 2 32
030 jr 1
032 load 15 19 -68 4
036 slli 10 8 4
03a li 12 6
03c mv 11 18
03e add 10 10 15
040 auipc 1 536432640
044 jalr 1 1 -266
048 bnez 10 34
04a addi 8 8 1
04c andi 8 8 255
050 jump 24
''',
'output':'''
000 lui 15 536883200
004 load 15 15 -63 1
008 addi 2 2 -32
00a store 2 8 24 4
00c store 2 1 28 4
00e store 2 9 20 4
010 li 8 2
012 bgeu 10 15 62
016 beqz 11 62
018 li 15 6
01a mul 10 10 15
01e mv 9 11
020 mv 12 2
022 li 11 16
024 addi 10 10 512
028 jal 1 278722
02c mv 8 10
02e bnez 10 62
030 li 12 6
032 mv 11 2
034 mv 10 9
036 auipc 1 536432640
03a jalr 1 1 -1076
03e mv 10 8
040 load 1 2 28 4
042 load 8 2 24 4
044 load 9 2 20 4
046 addi 2 2 32
048 jr 1
''',
'veneer':'''
000 jal 0 327744
''',
'check3':'''
000 beqz 10 86
002 addi 2 2 -32
004 store 2 9 20 4
006 store 2 1 28 4
008 store 2 8 24 4
00a mv 9 10
00c li 10 2
00e beqz 11 76
010 li 12 3
012 addi 10 2 8
014 mv 8 11
016 addi 11 11 3
018 auipc 1 536543232
01c jalr 1 1 730
020 load 15 2 10 1
022 addi 12 2 12
024 addi 11 2 8
026 andi 15 15 63
02a ori 15 15 64
02e mv 10 9
030 store 2 15 10 1
032 jal 1 335736
036 bnez 10 76
038 li 12 3
03a mv 11 8
03c addi 10 2 12
03e auipc 1 536543232
042 jalr 1 1 964
046 addi 10 10 -1
048 sltu 10 0 10
04c load 1 2 28 4
04e load 8 2 24 4
050 load 9 2 20 4
052 addi 2 2 32
054 jr 1
056 li 10 2
058 jr 1
''',
},
{
'poolfind':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 19 12 4
00a store 2 1 28 4
00c mv 18 10
00e li 8 0
010 lui 9 536883200
014 lui 19 536883200
018 load 15 9 17 1
01c bltu 8 15 50
020 mv 8 15
022 mv 10 8
024 load 1 2 28 4
026 load 8 2 24 4
028 load 9 2 20 4
02a load 18 2 16 4
02c load 19 2 12 4
02e addi 2 2 32
030 jr 1
032 load 15 19 12 4
036 slli 10 8 4
03a li 12 6
03c mv 11 18
03e add 10 10 15
040 auipc 1 536432640
044 jalr 1 1 -750
048 bnez 10 34
04a addi 8 8 1
04c andi 8 8 255
050 jump 24
''',
'output':'''
000 lui 15 536883200
004 load 15 15 17 1
008 addi 2 2 -32
00a store 2 8 24 4
00c store 2 1 28 4
00e store 2 9 20 4
010 li 8 2
012 bgeu 10 15 62
016 beqz 11 62
018 li 15 6
01a mul 10 10 15
01e mv 9 11
020 mv 12 2
022 li 11 16
024 addi 10 10 512
028 jal 1 278870
02c mv 8 10
02e bnez 10 62
030 li 12 6
032 mv 11 2
034 mv 10 9
036 auipc 1 536432640
03a jalr 1 1 -1560
03e mv 10 8
040 load 1 2 28 4
042 load 8 2 24 4
044 load 9 2 20 4
046 addi 2 2 32
048 jr 1
''',
'veneer':'''
000 jal 0 327898
''',
'check3':'''
000 beqz 10 86
002 addi 2 2 -32
004 store 2 9 20 4
006 store 2 1 28 4
008 store 2 8 24 4
00a mv 9 10
00c li 10 2
00e beqz 11 76
010 li 12 3
012 addi 10 2 8
014 mv 8 11
016 addi 11 11 3
018 auipc 1 536543232
01c jalr 1 1 576
020 load 15 2 10 1
022 addi 12 2 12
024 addi 11 2 8
026 andi 15 15 63
02a ori 15 15 64
02e mv 10 9
030 store 2 15 10 1
032 jal 1 335904
036 bnez 10 76
038 li 12 3
03a mv 11 8
03c addi 10 2 12
03e auipc 1 536543232
042 jalr 1 1 810
046 addi 10 10 -1
048 sltu 10 0 10
04c load 1 2 28 4
04e load 8 2 24 4
050 load 9 2 20 4
052 addi 2 2 32
054 jr 1
056 li 10 2
058 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values))
  check(len(args)==len(FIELDS[op]),'B1child literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1child typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1child complete boundaries')
 for a,f in s.items():init.g(n,a,'B1child '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1child Xwchc raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1child completeidentity')
 edges={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1child RET RA');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   check(d['rd'] in (0,1),'B1child call/tail link')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1child adjacent callpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1child closedCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1child all localnodes reachable')
 if part=='poolfind':
  cut={a:[z for z in qs if (a-pc,z-pc)!=(0x50,0x18)] for a,qs in edges.items()}
  check(not common.acyclic(edges) and common.acyclic(cut),'B1child pool exactloopcut')
 else:check(common.acyclic(edges),'B1child nonpool acyclic')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 frames={'poolfind':{(8,24),(9,20),(18,16),(19,12),(1,28)},'output':{(8,24),(1,28),(9,20)},'veneer':set(),'check3':{(9,20),(1,28),(8,24)}}
 saved=[d for d in stores if d['bytes']==4]
 check(len(saved)==len(frames[part]) and all(d['base']==2 for d in saved) and {(d['source'],d['imm']) for d in saved}==frames[part],'B1child exactsavedframe')
 expected={'poolfind':[(0x44,0x20000442)],'output':[(0x28,0x440c2+148*index),(0x3a,0x20000332)],'veneer':[],
  'check3':[(0x1c,0x20000332),(0x32,0x51f78+168*index),(0x42,0x20000442)]}[part]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'B1child allcalltargets')
 check(rets==[pc+o for o in {'poolfind':[0x30],'output':[0x48],'veneer':[],'check3':[0x54,0x58]}[part]],'B1child allreturn sites')
 check(tails==([dict(offset=0,target=STARTS[index][3],new_link=False)] if part=='veneer' else []),'B1child exacttail/check3 boundary')
 if part=='check3':
  check([d for d in stores if d['bytes']!=4]==[dict(offset=0x30,base=2,source=15,imm=10,bytes=1)],'B1child onlyscratchbyte modified locally')
 else:check(len(stores)==len(saved),'B1child frameonly localstores')
 return dict(start=pc,source=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part=='poolfind':
  seq=[0,2,4,6,8,0xa,0xc,0xe,0x10,0x14,0x18,0x1c,0x32,0x36,0x3a,0x3c,0x3e,0x40,0x44,0x48,0x4a,0x4c,0x50,0x18,0x1c,0x20,0x22,0x24,0x26,0x28,0x2a,0x2c,0x2e,0x30]
  e=b['CFG'];pc=b['start']
  check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1child immutable mismatch/reload/exit path')
  return dict(count0_or_exhausted=common.walk(b,{0x1c:0x20}),first_nonzero_compare=common.walk(b,{0x1c:0x32,0x48:0x22}),one_mismatch_then_exhausted=seq)
 choices={'output':{'index_rejected':{0x12:0x3e},'output_null':{0x12:0x16,0x16:0x3e},'NV_nonzero_status':{0x12:0x16,0x16:0x18,0x2e:0x3e},'NV_zero_copy6':{0x12:0x16,0x16:0x18,0x2e:0x30}},
  'veneer':{'unlinked_tail':{}},'check3':{'P_null_no_frame':{0:0x56},'Q_null_after_frame':{0:2,0xe:0x4c},'worker_nonzero':{0:2,0xe:0x10,0x36:0x4c},'worker_zero_compare_normalize':{0:2,0xe:0x10,0x36:0x38}}}[part]
 ps={name:common.walk(b,c) for name,c in choices.items()}
 if part=='check3':check(ps['P_null_no_frame']==[0,0x56,0x58] and 0x42 not in ps['worker_nonzero'] and 0x42 in ps['worker_zero_compare_normalize'],'B1child nullguard/worker gate')
 return ps


def domains():
 admitted=0
 for i in range(256):
  for N in range(256):
   if i<N:
    check(i<=254 and (i+1)&255==i+1,'B1child no admitted indexwrap');admitted+=1
 for N in range(256):
  check(N<=255 and (N==0 or 16*(N-1)+6<=16*N),'B1child stablecount strided extent')
 for x in range(256):
  y=(x&63)|64
  check(64<=y<=127 and y&63==x&63 and y&192==64,'B1child scratchbyte bits7:6 fixed01')
 # Algebraic full-domain certificate: modulo32 subtraction is zero iff R=1.
 # Two disjoint intervals partition every U32; this does not invoke the worker.
 intervals=((0,0,0xffffffff,0xffffffff),(1,1,0,0),(2,0xffffffff,1,0xfffffffe))
 check(sum(hi-lo+1 for lo,hi,_,_ in intervals)==2**32,'B1child U32 normalize intervalcoverage')
 for lo,hi,alo,ahi in intervals:
  check((lo-1)&0xffffffff==alo and (hi-1)&0xffffffff==ahi and ahi-alo==hi-lo,'B1child subtract interval endpoints/monotonicity')
  check((ahi==0)==(lo==hi==1) and (alo==0)==(lo==hi==1),'B1child normalizedzero iff reply1')
 copied=set(range(8,11));workerout=set(range(12,15));saved=set(range(20,32));scratch=set(range(0,16))
 check(copied.isdisjoint(workerout) and (copied|workerout).isdisjoint(saved) and scratch.isdisjoint(saved),'B1child local interval disjointness')
 check(512+6*254==2036 and 16*254+6==4070,'B1child admitted addressarithmetic')
 check(admitted==32640,'B1child exactadmitted pairs')
 return dict(index_freshcount_pairs=65536,admitted_pairs=admitted,count_limit=255,max_admitted_index=254,
  scratch_byte_inputs=256,scratch_bits7_6='01',normalize_U32_intervals=intervals,normalize='0 iff full comparator reply=1;otherwise1',
  local_copy_input=[8,11],worker_output_argument_only=[12,15],saved_frame=[20,32],optional_output_scratch_argument_only=[0,16],
  frame_interval_limit='intervals describe local arguments/operations;opaque NV/worker output extent,initialization andretention NOT inferred',
  target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,STARTS[index][k],SIZES[k]);check(sparse.captured(mem,STARTS[index][k],SIZES[k])==raw,'B1child completebody original sparseHEX');bs[part]=body(raw,part,index)
 n={part:{d['pc']-b['start']:d for d in b['instructions']} for part,b in bs.items()}
 p,o,c=n['poolfind'],n['output'],n['check3'];G=0x20003000
 check(p[0x10]['imm']+p[0x18]['imm']==G-63+80*index and p[0x14]['imm']+p[0x32]['imm']==G-68+80*index,'B1child freshcount/pool globaladdresses')
 check(p[0x36]['imm']==4 and p[0x3a]['imm']==6 and p[0x3c]['rs2']==18 and p[0x3e]['rd']==10,'B1child pool comparator(pool+16*i,Q,6)')
 check(o[0]['imm']+o[4]['imm']==G-63+80*index and o[0x18]['imm']==6 and o[0x24]['imm']==512 and o[0x22]['imm']==16 and o[0x20]['rs2']==2,'B1child output numericNV request/borrowedSP')
 check(o[0x2c]['rd']==8 and o[0x2c]['rs2']==10 and o[0x30]['imm']==6 and o[0x32]['rs2']==2 and o[0x34]['rs2']==9 and o[0x3e]['rs2']==8,'B1child copy6 andsavedstatus reply')
 check(c[0x10]['imm']==3 and c[0x12]['imm']==8 and c[0x16]['imm']==3 and c[0x20]['imm']==10 and c[0x30]['imm']==10,'B1child Q3..5 ->SP8..10 scratchlastbyte')
 check(c[0x26]['imm']==63 and c[0x2a]['imm']==64 and c[0x22]['imm']==12 and c[0x24]['imm']==8 and c[0x2e]['rs2']==9,'B1child worker(P,SP8,SP12)/bitpattern')
 check(c[0x38]['imm']==3 and c[0x3a]['rs2']==8 and c[0x3c]['imm']==12 and c[0x46]['imm']==-1 and c[0x48]['rs1']==0,'B1child compare(SP12,Q,3) ->fullreply!=1')
 selector=parent['bodies']['selector'];calls={d['offset']:d['target'] for d in selector['calls']};s={d['pc']-selector['start']:d for d in selector['instructions']}
 check([calls[a] for a in (0x40,0xde,0xca)]==[bs[x]['start'] for x in ('poolfind','output','veneer')],'B1child exact3selector joins')
 check(s[0x3e]['rd']==10 and s[0x3e]['rs2']==11 and s[0xc6]['rs2']==19 and s[0xc8]['rs2']==2 and s[0xce]['op']=='bnez','B1child selector type01Q/type3(SP,Q)/zeroaccept')
 check(bs['veneer']['tails'][0]['target']==bs['check3']['start'],'B1child tail into exactcompletewrapper')
 reused=parent['reused_leaves'];check(reused['comparator']['target']==0x20000442 and reused['copy']['target']==0x20000332,'B1child priorcompleteleaf joins')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},
  reused_leaves={name:dict(reused[name],new_code_bytes_counted=0) for name in ('comparator','copy')},
  poolfind_contract=['captureQ inS2,index0;freshU8count eachguard;rejectreturns thatsampledcount.Eachadmittedindex freshpoolword,comparator(pool+16*i,Q,6),nonzero returnsindex;zero incrementslow8',
   'pool row offset0 differsfromselector type2 offset6.Matchingcomparator returns1 onall6equal OR nullpointer;no unconditional key-validity proof',
   'index<=254 beforeprobe,atmost255 probes under normalcallee/contextpreservation;count changesbetweenprobes andparentchecks remainpossible'],
  optional_output_contract=['freshU8count thenframe32;fullunsignedindex>=count OR outputnull ->2;else NV440c2/44156(512+6*index,16,SP)',
   'capturefullNVresponse inS0;nonzero propagated;zero ->copy(output,SP,6),ignorecopyreply,return saved0',
   'actualB1 O0 gatesoff thiscallee inselector;generalcontract stillconditional.NV numeric16 doesnotproveunits,initializedSP0..5 oractualwriteextent'],
  check3_contract=['veneer singleunlinkedJAL ->50040/500da;500d8 isexcluded previousbody finaljump',
   'Pnull ->2 beforeframe;Qnull ->2 afterframe32;elsecopy(SP8,Q3,3),freshSP10 ->(byte&63)|64,writeonlySP10 locally',
   'opaque51f78/52020(P,SP8,SP12);nonzerofullresponse propagated;zero ->comparator(SP12,Q,3) andnormalize0 iff fullreply1 else1',
   'matchingbooleancomparator makeszero wrapperreply conditionalon workerzero andthreebyteequality;workeroutput content/initialization/extent remainunknown',
   'localSP11 untouched;SP12..14 have no localinitializer;no stackoutputvalidity inferredfromworkerzero orpointerarguments'],
  composition=['B1 query P_record+6 enters type01poolfind or type3wrapper.Type3middleworker inputP isselectorSP,notoriginalrecord pointer',
   'query/originaloutputsavedinSregisters,notdirectlystoredasglobalpointerbythesebodies;childcalls receiveborrowedpointers andmayretain them. No transitive no-retention orwholelifetimeproof',
   'candidateRAMcopy/comparator completeness/mapping reused frompriorphase;installedbinding andHWcontrolword/FENCE effects notexecuted orvalidated'],
  premises='conditionalcandidateISA/firstcopymapping/providers;validcode/frame/query/pool/read/writeextents;ordinarycalleeS/SP/RA/savedframepreservation;no adversealias/wrap/IRQ/DMA/reentry;allfreshsnapshot equalities separate',
  actual_provider_binding_worker_output_NV_extent_retention_or_full_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-selector-directcallees-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_new_body_bytes=500,complete_new_body_instructions=198,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['NV440c2/4435c completebuffercontracts/units/retention','opaque worker51f78/52020 outputcontract','actualprovider binding,query/payload sources andcompletepointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1child instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1child typedmutation escaped')
    typed+=1
 check((mutations,typed)==(198,6),'B1child mutationcensus');domains()
 print('PASS:198 instruction/6 typed-load mutations rejected;65536 index/count pairs;256 scratchbyte cases;fullU32 normalization intervals')


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
 else:check(OUT.read_bytes()==encoded,'B1child exactledger replay')
 print('PASS:500B/198i complete selectorcallees;strict HEX;exact50040/500da tails;pool/output/check3 joins;exact ledger')
 print('PASS:NO target execution/emulation;NV/worker output,installedbinding,retention andpointerlifetime UNPROVED')


if __name__=='__main__':main()
