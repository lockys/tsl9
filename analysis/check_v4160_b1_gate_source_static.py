"""Offline source-slot/actual dispatch joins; selected windows, not full parent semantics.
Original operands/immutable CFGs and closed host integer identities only.
No target execution/emulation, mutable object/list/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_recompute_callers_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-gate-source-static.json')
ROLES=('prefixA','prefixB','dispatchA','dispatchB')
SIZES={'prefixA':68,'prefixB':80,'dispatchA':58,'dispatchB':64}
STARTS=({'prefixA': 366008, 'prefixB': 397876, 'dispatchA': 367042, 'dispatchB': 399278}, {'prefixA': 366336, 'prefixB': 398110, 'dispatchA': 367370, 'dispatchB': 399512})
COUNTS={'prefixA': 22, 'prefixB': 28, 'dispatchA': 21, 'dispatchB': 23}
HASHES=({'prefixA': '6ce3308f2b9621d75a6a227dc1b3d49d575dbef78cebd942eef42394cb0e9b1e', 'prefixB': 'ca89339f2bf71703feaef01b81b39420c7a5c67ae3e20ceb769358501f93eedf', 'dispatchA': 'fb4f3b11159405a7a9e6e3d89cd64bb38010615677f0264f91aa5b28563f595c', 'dispatchB': '1e1e22d50957fd8785de86c81e70bfe8c374c98597845db4b6c019f5480d19b5'}, {'prefixA': 'fa20b2546dcf53f68ae8c891fafbddc3504a723a32e6b50f35aecec56978da20', 'prefixB': '5d4804ffe2057f3751a2c9fa82e07fe422df3b89609b21beb3be9909a58f3a42', 'dispatchA': 'fb4f3b11159405a7a9e6e3d89cd64bb38010615677f0264f91aa5b28563f595c', 'dispatchB': '0af4189e76a1e1c0babd25db680deefc3d55f4e69ccd4eb83b26e4e92ab70f4b'})
LITERALS={
'prefixA':"""
000 addi 2 2 -48
002 store 2 18 32 4
004 lui 18 536883200
008 addi 15 18 952
00c store 2 8 40 4
00e load 8 15 164 4
012 store 2 9 36 4
014 store 2 21 20 4
016 store 2 22 16 4
018 lui 9 536883200
01c lui 21 536883200
020 lui 22 450560
024 store 2 19 28 4
026 store 2 20 24 4
028 store 2 1 44 4
02a store 2 23 12 4
02c addi 18 18 952
030 addi 9 9 1300
034 lui 19 536883200
038 lui 20 536883200
03c addi 21 21 564
040 addi 22 22 1344
""",
'prefixB':"""
000 addi 2 2 -80
002 store 2 9 68 4
004 lui 9 536883200
008 addi 15 9 952
00c store 2 22 48 4
00e lui 22 450560
012 store 2 8 72 4
014 store 2 19 60 4
016 store 2 20 56 4
018 store 2 21 52 4
01a load 8 15 164 4
01e lui 19 536883200
022 lui 20 536883200
026 lui 21 536883200
02a addi 15 22 1344
02e store 2 18 64 4
030 store 2 23 44 4
032 store 2 1 76 4
034 store 2 24 40 4
036 store 2 25 36 4
038 store 2 26 32 4
03a store 2 27 28 4
03c li 23 0
03e addi 9 9 952
042 addi 18 19 1300
046 addi 20 20 564
04a addi 21 21 492
04e store 2 15 12 4
""",
'dispatchA':"""
000 load 13 8 13 1
002 li 14 3
004 bne 13 14 58
008 load 15 8 23 1
00a addi 14 0 42
00e bgeu 14 15 44
012 load 15 8 23 1
014 li 14 7
016 beq 15 14 -24
01a store 8 15 45 1
01e load 15 8 168 4
022 ori 15 15 1
026 store 8 15 168 4
02a jump -24
02c slli 15 15 2
02e add 15 15 22
030 load 15 15 0 4
032 mv 10 8
034 call_indirect 1 15
036 bnez 10 18
038 jump -24
""",
'dispatchB':"""
000 load 15 8 13 1
002 li 14 3
004 bne 15 14 70
008 load 15 8 23 1
00a addi 14 0 42
00e bgeu 14 15 50
012 load 15 8 23 1
014 li 14 7
016 beq 15 14 64
01a store 8 15 45 1
01e load 15 8 168 4
022 mv 10 8
024 ori 15 15 1
028 store 8 15 168 4
02c jal 1 369214
030 jump 64
032 load 14 2 12 4
034 slli 15 15 2
036 mv 10 8
038 add 15 15 14
03a load 15 15 0 4
03c call_indirect 1 15
03e bnez 10 18
""",
}
PATCHES={'prefixA': {8: ('addi', [15, 18, 1032]), 44: ('addi', [18, 18, 1032]), 48: ('addi', [9, 9, 1380]), 60: ('addi', [21, 21, 644]), 64: ('addi', [22, 22, 1840])}, 'prefixB': {8: ('addi', [15, 9, 1032]), 42: ('addi', [15, 22, 1840]), 62: ('addi', [9, 9, 1032]), 66: ('addi', [18, 19, 1380]), 70: ('addi', [20, 20, 644]), 74: ('addi', [21, 21, 572])}, 'dispatchA': {}, 'dispatchB': {44: ('jal', [1, 369542])}}
TYPED={'prefixA': [(14, 2)], 'prefixB': [(26, 2)], 'dispatchA': [(30, 2)], 'dispatchB': [(30, 2)]}
QK={'prefixA': [], 'prefixB': [], 'dispatchA': [(0, '5434', 'qk.c.lbu'), (8, '7c38', 'qk.c.lbu'), (18, '7c38', 'qk.c.lbu')], 'dispatchB': [(0, '5c34', 'qk.c.lbu'), (8, '7c38', 'qk.c.lbu'), (18, '7c38', 'qk.c.lbu')]}
STORES={'prefixA': [(2, 2, 18, 32, 4), (12, 2, 8, 40, 4), (18, 2, 9, 36, 4), (20, 2, 21, 20, 4), (22, 2, 22, 16, 4), (36, 2, 19, 28, 4), (38, 2, 20, 24, 4), (40, 2, 1, 44, 4), (42, 2, 23, 12, 4)], 'prefixB': [(2, 2, 9, 68, 4), (12, 2, 22, 48, 4), (18, 2, 8, 72, 4), (20, 2, 19, 60, 4), (22, 2, 20, 56, 4), (24, 2, 21, 52, 4), (46, 2, 18, 64, 4), (48, 2, 23, 44, 4), (50, 2, 1, 76, 4), (52, 2, 24, 40, 4), (54, 2, 25, 36, 4), (56, 2, 26, 32, 4), (58, 2, 27, 28, 4), (78, 2, 15, 12, 4)], 'dispatchA': [(26, 8, 15, 45, 1), (38, 8, 15, 168, 4)], 'dispatchB': [(26, 8, 15, 45, 1), (40, 8, 15, 168, 4)]}

TABLES=(0x6e540,0x6e730)
TABLE_WORDS=((372796, 377972, 372968, 378058, 372998, 373122, 373160, 373220, 377836, 377702, 373488, 373524, 373630, 373776, 377566, 377346, 377130, 368678, 373936, 374012, 378796, 378702, 374056, 374464, 374790, 374912, 374948, 378880, 376680, 375090, 375148, 378884, 378888, 378892, 378896, 378388, 375210, 375414, 378900, 378876, 375578, 376624, 376114), (373124, 378300, 373296, 378386, 373326, 373450, 373488, 373548, 378164, 378030, 373816, 373852, 373958, 374104, 377894, 377674, 377458, 369006, 374264, 374340, 379124, 379030, 374384, 374792, 375118, 375240, 375276, 379208, 377008, 375418, 375476, 379212, 379216, 379220, 379224, 378716, 375538, 375742, 379228, 379204, 375906, 376952, 376442))
TABLE_HASHES=('5c1e552fd4abbce901e4da56d15ca9cd18e718a0d137c57ec4023a2831afdde7', '14943a07f7cada542d928fdc479c8f7013c2b4b379b6ef4ae0bac99b412f20d4')
PARENT_STARTS=((0x595b8,0x61234),(0x59700,0x6131e))
PARENT_SIZES=(1926,2280)
PARENT_COUNTS=(653,764)
PARENT_HASHES=(('7e8c819b03c98908d110d44db164fff4937ff5b9f549e657b0e0f14a233b64b0','3f22ada892a9d0fbe4f449c1417690b5a4ab1954f467111097a9ee7a52d90485'),('918ac453db34e0605d787c992230f35eb2f5600e587c2fb4db5c2988596578f3','a279fac49fb47210f25c108ed782989c38b917ede578cba4941434b46fe15b83'))


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'gatesource literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def window(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'gatesource selectedwindow boundaries')
 for a,f in s.items():init.g(n,a,'gatesource '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'gatesource selectedwindow identity')
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'gatesource typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'gatesource exactQK')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'gatesource selectedstores')
 edges={};calls=[];frontier=set()
 for a,d in n.items():
  q=[a+d['size']]
  if d['op'] in BRANCHES:q.append(d['target'])
  elif d['op']=='jump':q=[d['target']]
  elif d['op']=='jal':check(d['rd']==1,'gatesource windowlinkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif d['op']=='call_indirect':check(d['rd']==1 and d['rs1']==15,'gatesource dispatchA5 linkedcall');calls.append(dict(offset=a-pc,target='loadedA5'))
  check(d['op'] not in ('jr','jalr','ecall','mret','csr'),'gatesource boundedwindow supported op')
  edges[a]=q;frontier.update(z for z in q if z not in n)
 expected={'prefixA':[],'prefixB':[],'dispatchA':[(0x34,'loadedA5')],'dispatchB':[(0x2c,0x5a23e+328*index),(0x3c,'loadedA5')]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'gatesource exactwindowcalls')
 if role.startswith('dispatch'):
  k=0 if role=='dispatchA' else 1
  check(n[pc]['imm']==13 and n[pc+2]['imm']==3 and n[pc+8]['imm']==23 and n[pc+0xa]['imm']==42,'gatesource type3/key42 gate')
  check(n[pc+0x12]['imm']==23 and n[pc+0x14]['imm']==7 and n[pc+0x1a]['imm']==45 and n[pc+0x1e]['imm']==168,'gatesource fallbackfreshkey/7/45/168')
  check(n[pc+(0x22 if k==0 else 0x24)]['imm']==1,'gatesource fallbackbit0')
  check(n[pc+(0x2c if k==0 else 0x34)]['imm']==2,'gatesource 4byte tablescale')
  check(n[pc+(0x36 if k==0 else 0x3e)]['op']=='bnez' and n[pc+(0x36 if k==0 else 0x3e)]['rs1']==10,'gatesource nonzeroreply fallback')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index][role],instructions=list(n.values()),selected_window_CFG=edges,outside_window_frontier=sorted(frontier),calls=calls,stores=stores,complete_parent_function_claim=False,target_execution_proved=False)


def table(raw,index):
 check(len(raw)==172 and sha256(raw).hexdigest()==TABLE_HASHES[index],'gatesource complete43wordtable identity')
 words=tuple(int.from_bytes(raw[o:o+4],'little') for o in range(0,172,4));check(words==TABLE_WORDS[index],'gatesource complete43word operands')
 check(words[20]==previous.STARTS[index]['gateflag'] and words[21]==previous.STARTS[index]['gate80'],'gatesource actualgate entries20/21')
 return dict(start=TABLES[index],bytes=172,sha256=TABLE_HASHES[index],words=words,zero_based_gate_keys={'20':words[20],'21':words[21]},other_entry_bodies_not_expanded_here=True,actual_installedtable_or_invocation_proved=False)


def parent_census(raw,index,k):
 pc=PARENT_STARTS[index][k];n=decode(raw,pc)
 check((len(raw),len(n),sha256(raw).hexdigest())==(PARENT_SIZES[k],PARENT_COUNTS[k],PARENT_HASHES[index][k]),'gatesource fullparent identity/census')
 e={};calls=[];tails=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal' and d['rd']==0:q=[];tails.append((a-pc,d['target']))
  elif op in ('jal','jalr','call_indirect'):check(d['rd']==1,'gatesource fullparentcalls linked');calls.append(a)
  check(op not in ('jr','ecall','mret','csr') and all(z in n for z in q),'gatesource fullparent graph hasonlyknownlocaledges');e[a]=q
 check(tails==[(0x65c if k==0 else 0x77c,0x567be+320*index)],'gatesource fullparent soleunlinkedtail')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n),'gatesource fullparent reachablecensus')
 preds={a:[] for a in n}
 for a,qs in e.items():
  for z in qs:preds[z].append(a)
 def last_before(a,reg):
  hits=set();entry=False;seen=set();todo=preds[a][:]
  while todo:
   a=todo.pop()
   if n[a].get('rd')==reg:hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(preds[a])
  return hits,entry
 def reaches(a,z,blocked=()):
  seen=set();todo=[a];blocked=set(blocked)
  while todo:
   a=todo.pop()
   if a in blocked:continue
   if a==z:return True
   if a not in seen:seen.add(a);todo.extend(e[a])
  return False
 source=0xe if k==0 else 0x1a;call=0x43e if k==0 else 0x5b6;arg=call-2 if k==0 else call-6
 init.g(n,pc+source,'gatesource sourcecapture',op='load',rd=8,rs1=15,imm=164,width=4)
 check(last_before(pc+arg,8)==({source},False),'gatesource S0 reachingdef exactcapture notepilogue')
 check(last_before(pc+call,10)==({arg},False),'gatesource linkeddispatch A0 exactlyS0')
 init.g(n,pc+arg,'gatesource dispatcharg',op='mv',rd=10,rs2=8)
 init.g(n,pc+8,'gatesource exactB formation',op='addi',rd=15,rs1=18 if k==0 else 9,imm=952+80*index)
 init.g(n,pc+4,'gatesource B base',op='lui',rd=18 if k==0 else 9,imm=0x20003000)
 check(last_before(pc+source,15)==({8},False),'gatesource capturebase reachingdef')
 tableproof={}
 if k==0:
  add=0x438;check(last_before(pc+add,22)==({0x40},False) and last_before(pc+0x40,22)==({0x20},False),'gatesource A heldS6 tablebase reachingdefs')
  init.g(n,pc+0x20,'gatesource tableA LUI',op='lui',rd=22,imm=0x6e000);init.g(n,pc+0x40,'gatesource tableA ADDI',op='addi',rd=22,rs1=22,imm=1344+496*index)
  tableproof=dict(register=22,table_definition=0x40,LUI_definition=0x20)
 else:
  stores=[a-pc for a,d in n.items() if d['op']=='store' and d['rs1']==2 and d['imm']==12]
  check(stores==[0x4e] and not reaches(pc,pc+0x5ac,[pc+0x4e]),'gatesource savedSP12 unique/dominatingstore')
  check(last_before(pc+0x4e,15)==({0x2a},False) and last_before(pc+0x2a,22)==({0xe},False),'gatesource storedtable value reachingdefs')
  init.g(n,pc+0xe,'gatesource tableB LUI',op='lui',rd=22,imm=0x6e000);init.g(n,pc+0x2a,'gatesource tableB ADDI',op='addi',rd=15,rs1=22,imm=1344+496*index)
  init.g(n,pc+0x4e,'gatesource SP12 savetable',op='store',rs1=2,rs2=15,imm=12,width=4);init.g(n,pc+0x5ac,'gatesource SP12 reloadtable',op='load',rd=14,rs1=2,imm=12,width=4)
  spdefs=[(a-pc,d['imm']) for a,d in n.items() if d.get('rd')==2];check(len(spdefs)==2 and spdefs[0]==(0,-80) and spdefs[1][1]==80,'gatesource parentB ownSPdefinitions')
  check(not reaches(pc+spdefs[1][0],pc+0x5ac),'gatesource SPdeallocation cannotprecede selectedreload')
  tableproof=dict(saved_frame_offset=12,unique_local_store=0x4e,store_value_definition=0x2a,LUI_definition=0xe,reload=0x5ac,live_S6_not_assumed_table=True)
 defs={str(r):[a-pc for a,d in n.items() if d.get('rd')==r] for r in (8,22)}
 check(sum(map(len,e.values()))==(732 if k==0 else 837),'gatesource exactparentedgecensus')
 return dict(start=pc,bytes=len(raw),instructions_count=len(n),sha256=PARENT_HASHES[index][k],node_count=len(n),edge_count=sum(map(len,e.values())),CFG_sha256=sha256(json.dumps(e,separators=(',',':')).encode()).hexdigest(),linked_call_offsets=[a-pc for a in calls],S0_S6_definition_offsets=defs,selected_dispatch_call=call,selected_A0_definition=arg,selected_S0_source_definition=source,table_source_certificate=tableproof,all_static_nodes_reachable=True,full_parent_semantics_reconstructed=False,all_calls_callee_saved_register_frame_table_preservation_required=True,loop_progress_or_pointer_validity_proved=False)


def source_joins(image,data,hexraw,index,mem):
 import check_v4160_b1_key_submit_static as key
 import check_v4160_b1_ram_query_static as query
 import check_v4160_b1_buffer_origin_static as origin
 refs={};ns={}
 for role in key.ROLES:
  pc=key.STARTS[index][role];raw=init.binding.take(data,pc,key.SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'gatesource reusedkey/submit fullHEX');b=key.body(raw,role,index);refs[role]=dict(start=pc,bytes=b['bytes'],sha256=b['sha256']);ns[role]={d['pc']-pc:d for d in b['instructions']}
 kn=ns['key'];sn=ns['submit'];G=0x20003000;B=0x200033b8+80*index;S=0x20003514+80*index
 check(kn[0x8c]['imm']==G and kn[0x90]['rs1']==kn[0x90]['rd']==15 and kn[0x90]['imm']==1336+80*index and kn[0xa0]['rs1']==8 and kn[0xa0]['rs2']==15 and kn[0xa0]['imm']==276,'gatesource heldS36 ->keyW276')
 check(kn[0x70]['imm']==272 and kn[0x70]['rs2']==10 and kn[0x74]['op']=='bnez' and kn[0x74]['target']==refs['key']['start']+0x8c,'gatesource separateallocator272 nonnullgate')
 check(sn[0xa]['imm']==952+80*index and sn[0xba]['rs1']==19 and sn[0xba]['rs2']==8 and sn[0xba]['imm']==168,'gatesource submitpublishesB168 notB164')
 qr=init.binding.take(data,query.SOURCES[index],620);check(sparse.captured(mem,query.SOURCES[index],620)==qr,'gatesource queryfullfirstcopyHEX');qb=query.body(qr,index);qn={d['pc']-query.ENTRY:d for d in qb['instructions']}
 check(qn[0x16]['op']=='mv' and qn[0x16]['rd']==8 and qn[0x16]['rs2']==10 and qn[0x1c0]['imm']==G and qn[0x1c4]['rs1']==15 and qn[0x1c4]['rs2']==8 and qn[0x1c4]['imm']==1116+80*index and qn[0x1c8]['imm']==0,'gatesource queryP publication B164/forced0')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+query.ENTRY-int(fc['destination'],16)==query.SOURCES[index] and query.ENTRY+620<=int(mapping['first_copy_end_exclusive'],16),'gatesource query firstcopymapping')
 op=origin.profile(image,data,hexraw,index);ab,_,_=origin.app_body(image)
 check(op['packet_pointer_slot']==S+36==G+kn[0x90]['imm'] and G+qn[0x1c4]['imm']==B+164 and B+164+4==B+168,'gatesource exactcell joins, distinctadjacent objectslots')
 refs['query']=dict(start=query.ENTRY,source=query.SOURCES[index],bytes=620,sha256=qb['sha256'])
 for role in ('config_initializer','RF_pointer_publisher'):
  b=op['reused_bodies'][role];refs[role]={k:b[k] for k in ('start','bytes','sha256')}
 refs['APP_builder']={k:ab[k] for k in ('start','bytes','sha256')}
 return dict(reused_full_original_bodies=refs,packet_source_slot=S+36,key_object_field=276,key_allocated_other_buffer_field=272,dispatch_object_slot=B+164,query_published_object_slot=B+164,submit_published_other_slot=B+168,conditional_nominal_Q=origin.H,required_ingress_extent=11,nominal_reserved_prefix_bytes=272,
  contracts=['matchingAPPconfig/copy/fieldpreservation ->freshconfigword0 X ->S36; keysuccessfulotherallocationpath freshS36 heldword ->lookupW276. Allocatorreply storedW272 separately;64..260 request isnotQextent',
   'queryselectedsuccesssuffix publishesentryP toB164 thenforce0; bothselectedparents independentlycaptureB164. Publication-before-capture/nooverwrite/liveP/samebinding required; querydoesnotdirectlyinvokeparents here',
   'submit publishesW toB168,distinctadjacentword; cannot useitasB164 bridge. keylookupW andqueryP identity remainsunproved',
   'nominalAPPH=2000418c/272prefix cancontainQ3..10 numerically only;not11byte ingresslength/initialization/ownership orunchangedsourceproof'],actual_source_extent_object_identity_ordering_and_complete_lifetime_proved=False)


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());ws={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'gatesource complete selectedwindow strictHEX');ws[role]=window(raw,role,index)
 tr=init.binding.take(data,TABLES[index],172);check(sparse.captured(mem,TABLES[index],172)==tr,'gatesource tablefullstrictHEX');tab=table(tr,index)
 parents=[]
 for k,pc in enumerate(PARENT_STARTS[index]):
  raw=init.binding.take(data,pc,PARENT_SIZES[k]);check(sparse.captured(mem,pc,len(raw))==raw,'gatesource parentidentity fullstrictHEX');parents.append(parent_census(raw,index,k))
 gates={}
 for role in ('gate80','gateflag'):
  pc=previous.STARTS[index][role];raw=init.binding.take(data,pc,previous.SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'gatesource gatefullstrictHEX');b=previous.body(raw,role,index);gates[role]={k:b[k] for k in ('start','bytes','sha256')}
 return dict(label=init.binding.PROFILES[index][0],selected_windows=ws,full_dispatch_table=tab,parent_identity_CFG_definition_census=parents,reused_gates=gates,source_joins=source_joins(image,data,hexraw,index,mem),
  contracts=['bothselecteddispatchwindows requirefreshP13=3 thenfreshU8P23<=42;key20->gateflag,key21->gate80,A0=S0 capturedfromB164,notincomingparentA0. Targetnonnull/executable andactualtablebinding notguarded/proved',
   'firstparent usesheldS6 tablebase;second usesuniquelocalSP12 savedtablebase,notlaterreassignedS6. Fulloriginalparentidentity/CFG anddefcensus supportselectedreachingdefs undercallee/frame/alias/tablepreservation premises;notfullparentsemantic reconstruction',
   'bothzero childreplies skipfallback;nonzero entersfallback,reloadfreshP23,if7 skip fallbackstores. OtherwiseSB P45=low8freshkey andSW P168=freshP168|1. Secondparentadditionallycalls5a23e/5a386(P) afterstores,firstdoesnot inthiswindow',
   'matchinggate80 calledarmreturns0 foringress0/1/2,soevenitsnonzerochildbranch doesnotcauseouterfallback. Gateflagsource-reject1 propagates1 ->outerfallback;gateflag0/2 actionreturns0 ->skip. Bothgates skippedconditionsreturn1. Freshkeys/states maydiffer atfallback;noactor/packet/event progression proof'],full_parent_behaviour_or_actual_hardware_provider_or_complete_lifetime_proved=False)


def domains():
 for key in range(256):check((key<=42)==(0<=4*key and 4*key+4<=172),'gatesource exact43entry addressbound')
 for i in range(2):
  check(TABLES[i]+20*4==0x6e590+496*i and TABLES[i]+21*4==0x6e594+496*i,'gatesource gateentrycells')
  check(0x20003514+80*i+36==0x20003000+1336+80*i and 0x200033b8+80*i+164==0x20003000+1116+80*i,'gatesource fixedslot identities')
  check(0x200033b8+80*i+164+4==0x200033b8+80*i+168,'gatesource distinctadjacent words notsamepublication')
 import check_v4160_b1_buffer_origin_static as origin
 check(origin.H+11<=origin.H+272<2**32,'gatesource numericprefix accommodatesrequired11,notactualextent')
 return dict(byte_key_cases=256,admitted_keys=43,gateflag_key=20,gate80_key=21,tablebytes_each=172,required_Q_extent=11,nominal_prefix_extent=272,nominal_fit_is_not_source_length_or_ownership_proof=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-gate-dispatch-and-source-slot-composition-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_selected_window_bytes=540,new_selected_window_instructions=188,new_dispatch_table_bytes=344,new_original_complete_function_count=0,parent_identity_census_bytes=8412,parent_identity_census_is_not_full_semantic_reconstruction=True,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['actualkeyW/queryP/parentP identity and publication/capture/clearordering','actualQbyteproducer/ingresslength/fieldstability andproviderbinding','fullparentloops/othercases/5a23e/5a386 fallbackcallee andconsumption/release/fullnodeownership'])


def tests(carriers):
 mutated=typed=tablebytes=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=window(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:window(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('gatesource instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:window(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('gatesource typedmutation escaped')
    typed+=1
  tr=init.binding.take(data,TABLES[i],172)
  for o in range(172):
   bad=bytearray(tr);bad[o]^=1
   try:table(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('gatesource tablemutation escaped')
   tablebytes+=1
 check((mutated,typed,tablebytes)==(188,8,344),'gatesource mutationcensus')
 print('PASS:188 instruction/8 typed-load/344 table-byte mutations rejected;selected dispatch/source contracts')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'gatesource exactledger replay')
 print('PASS:540B/188i selected windows+344B tables;strictHEX;parent def-census;S36/W276/B164 joins;exactledger')
 print('PASS:NO target execution/emulation;fullparentsemantics/actualbindings/ingresslength/full lifetimes UNPROVED')


if __name__=='__main__':main()
