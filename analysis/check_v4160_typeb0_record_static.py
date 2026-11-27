"""Offline B0 record lookup/prefix cleanup and callback-list lookup.
Pinned original operands/CFG and immutable loop/scalar certificates only.
No target execution/emulation, provider, register/RAM/heap/list model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_typeb0_cases_static as previous
import check_v4160_special_event_callback_static as special
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-typeb0-record-static.json')
PARTS=('clear','arraylookup','callbackrecord','callbackpointer')
STARTS=((0x4b5d2,0x4b61e,0x4b650,0x4b66c),(0x4b66a,0x4b6b6,0x4b6e8,0x4b704))
SIZES=(76,50,28,22)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('ed0eeb3a32f54f627a4e30f6ed7e77474d01cc0199cd22497290c2b05110e50c', 'dce57037efc72b73c27660ba276f865397dbbf33a13859e0cc29069a0bca4214', '8255a57304aac5a0982aa0a21452f79dae4991b70a08d8d3ffb7deb6b69c141e', '71734a302dea8acf974338ce42987593a113b33842470e33b82f9445c62b5aa4'), ('c44f3a843980637510c60b52cacaef8d5210d79f4930d493d17295a4df6ae9d9', 'cf9da91512a9224f622c8c7529d955831cb9d9887e5c35567eaf8be847c67109', 'e484dfc91209a39384ac199a377788a671c6c3f44bbab0b176594ff110653700', '71734a302dea8acf974338ce42987593a113b33842470e33b82f9445c62b5aa4'))
COUNTS=((30, 16, 11, 10), (30, 16, 11, 10))
TYPED_LOADS=({'clear': (), 'arraylookup': ((4, 4), (12, 2), (34, 5)), 'callbackrecord': ((4, 2),), 'callbackpointer': ()}, {'clear': (), 'arraylookup': ((4, 4), (12, 2), (34, 5)), 'callbackrecord': ((4, 2),), 'callbackpointer': ()})
LITERALS=(
{
'clear':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 9 4 4
006 store 2 18 0 4
008 store 2 1 12 4
00a mv 9 10
00c addi 8 10 4
010 addi 18 10 184
014 load 15 8 0 2
016 beqz 15 60
018 load 10 8 8 4
01a beqz 10 36
01c auipc 1 536563712
020 jalr 1 1 -1246
024 mv 10 8
026 li 12 12
028 li 11 0
02a auipc 1 536563712
02e jalr 1 1 -608
032 addi 8 8 12
034 store 8 0 -12 2
038 bne 8 18 20
03c load 1 2 12 4
03e load 8 2 8 4
040 li 15 -1
042 store 9 15 0 2
044 load 18 2 0 4
046 load 9 2 4 4
048 addi 2 2 16
04a jr 1
''',
'arraylookup':'''
000 lui 15 536883200
004 load 12 15 949 1
008 lui 15 536883200
00c load 14 15 -116 4
010 li 15 0
012 bne 12 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c mv 13 14
01e addi 14 14 184
022 load 11 14 -184 2
026 beq 11 10 24
02a addi 15 15 1
02c andi 15 15 255
030 jump 18
''',
'callbackrecord':'''
000 lui 15 536883200
004 load 15 15 -108 4
008 beqz 15 24
00a load 14 15 4 2
00c bne 14 10 20
010 load 10 15 8 4
012 jr 1
014 load 15 15 0 4
016 jump 8
018 li 10 0
01a jr 1
''',
'callbackpointer':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 jal 1 308816
008 beqz 10 18
00a load 10 10 8 4
00c load 1 2 12 4
00e addi 2 2 16
010 jr 1
012 li 10 0
014 jump 12
''',
},
{
'clear':'''
000 addi 2 2 -16
002 store 2 8 8 4
004 store 2 9 4 4
006 store 2 18 0 4
008 store 2 1 12 4
00a mv 9 10
00c addi 8 10 4
010 addi 18 10 184
014 load 15 8 0 2
016 beqz 15 60
018 load 10 8 8 4
01a beqz 10 36
01c auipc 1 536563712
020 jalr 1 1 -1398
024 mv 10 8
026 li 12 12
028 li 11 0
02a auipc 1 536563712
02e jalr 1 1 -760
032 addi 8 8 12
034 store 8 0 -12 2
038 bne 8 18 20
03c load 1 2 12 4
03e load 8 2 8 4
040 li 15 -1
042 store 9 15 0 2
044 load 18 2 0 4
046 load 9 2 4 4
048 addi 2 2 16
04a jr 1
''',
'arraylookup':'''
000 lui 15 536883200
004 load 12 15 1029 1
008 lui 15 536883200
00c load 14 15 -36 4
010 li 15 0
012 bne 12 15 28
016 li 13 0
018 mv 10 13
01a jr 1
01c mv 13 14
01e addi 14 14 184
022 load 11 14 -184 2
026 beq 11 10 24
02a addi 15 15 1
02c andi 15 15 255
030 jump 18
''',
'callbackrecord':'''
000 lui 15 536883200
004 load 15 15 -28 4
008 beqz 15 24
00a load 14 15 4 2
00c bne 14 10 20
010 load 10 15 8 4
012 jr 1
014 load 15 15 0 4
016 jump 8
018 li 10 0
01a jr 1
''',
'callbackpointer':'''
000 addi 2 2 -16
002 store 2 1 12 4
004 jal 1 308968
008 beqz 10 18
00a load 10 10 8 4
00c load 1 2 12 4
00e addi 2 2 16
010 jr 1
012 li 10 0
014 jump 12
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'B0record literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for off,f3 in TYPED_LOADS[index][part]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'B0record typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B0record completeboundaries '+part)
 for a,f in s.items():init.g(n,a,'B0record operand '+part+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B0record completeidentity '+part)
 edges={};calls=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B0record ordinaryRET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'B0record linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B0record adjacentlinkedpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B0record closedlocalCFG');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B0record allnodes reachable')
 loop=((0x38,0x14),(0x30,0x12),(0x16,0x8),None)[k]
 cut={a:[z for z in qs if loop is None or (a,z)!=(pc+loop[0],pc+loop[1])] for a,qs in edges.items()}
 check(common.acyclic(cut) and (common.acyclic(edges)==(loop is None)),'B0record exactcycle edge cut')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 check((len(calls),len(returns),len(stores))==((2,1,6),(0,1,0),(0,2,0),(1,1,1))[k],'B0record call/return/storecensus')
 if part=='clear':
  check(calls==[dict(offset=0x20,target=0x20000110),dict(offset=0x2e,target=0x2000039c)],'B0record privatefree thenfill targetcensus')
  check(stores[-2:]==[dict(offset=0x34,base=8,source=0,imm=-12,bytes=2),dict(offset=0x42,base=9,source=15,imm=0,bytes=2)],'B0record directheads0 andrecordkeyFFFF')
  saves={(v['source'],v['imm']) for v in stores if v['base']==2}
  restores={(v['rd'],v['imm']) for v in n.values() if v['op']=='load' and v['rs1']==2}
  check(saves==restores=={(1,12),(8,8),(9,4),(18,0)},'B0record16Bframe exactrestore')
 elif part=='callbackpointer':check(calls==[dict(offset=4,target=STARTS[index][2])] and stores==[dict(offset=2,base=2,source=1,imm=12,bytes=4)],'B0record wrapper exactlinkedgetter')
 else:check(2 not in {v.get('rd') for v in n.values()},'B0record readonlylookup noSPwrite')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=returns,stores=stores,cycle_edge=loop,complete_local_body=True,target_execution_or_emulation=False)


def checked(b,seq):
 pc=b['start'];e=b['CFG'];absolute=[pc+o for o in seq]
 check(absolute[0]==pc and not e[absolute[-1]] and all(z in e[a] for a,z in zip(absolute,absolute[1:])),'B0record immutablefullpath certificate')
 return seq


def clear_paths(b):
 head=[0,2,4,6,8,0xa,0xc,0x10];ep=[0x3c,0x3e,0x40,0x42,0x44,0x46,0x48,0x4a]
 nullslot=[0x14,0x16,0x18,0x1a,0x24,0x26,0x28,0x2a,0x2e,0x32,0x34,0x38]
 ptrslot=[0x14,0x16,0x18,0x1a,0x1c,0x20,0x24,0x26,0x28,0x2a,0x2e,0x32,0x34,0x38]
 rows={
  'firstheadzero_skipsallsuffix':head+[0x14,0x16]+ep,
  'oneoccupied_nullword_thenempty':head+nullslot+[0x14,0x16]+ep,
  'oneoccupied_nonzeroword_thenempty':head+ptrslot+[0x14,0x16]+ep,
  'all15occupied_nonzerowords':head+ptrslot*15+ep}
 paths={k:checked(b,v) for k,v in rows.items()}
 check(0x20 not in paths['firstheadzero_skipsallsuffix'] and 0x2e not in paths['firstheadzero_skipsallsuffix'],'B0record earlyempty nocalls')
 check(paths['all15occupied_nonzerowords'].count(0x20)==paths['all15occupied_nonzerowords'].count(0x2e)==15,'B0record maximum15release/fillattempts')
 n={v['pc']-b['start']:v for v in b['instructions']}
 check(not any(n[o].get('rd')==10 for o in (0x1a,0x1c)),'B0record slotword A0 forwarded unchangedtoprivatefree')
 check(all(0x42 in s for s in paths.values()),'B0record recordkeyFFFF evenearlyexit')
 return {'selected':paths,'allnormalpaths_keyFFFF_requirescallee_savedframe_andobjectpreservation':True,
  'processed_slot_bound':[0,15],'contiguous_prefix_occupancy_proved':False,'actual_release_fill_or_suffixcleanup_proved':False}


def array_paths(b):
 start=[0,4,8,0xc,0x10];mismatch=[0x12,0x1c,0x1e,0x22,0x26,0x2a,0x2c,0x30]
 rows={'count0_no_keydereference':start+[0x12,0x16,0x18,0x1a],
  'firstkeymatch':start+[0x12,0x1c,0x1e,0x22,0x26,0x18,0x1a],
  'one_mismatch_secondmatch':start+mismatch+[0x12,0x1c,0x1e,0x22,0x26,0x18,0x1a],
  'count255_no_match':start+mismatch*255+[0x12,0x16,0x18,0x1a]}
 paths={k:checked(b,v) for k,v in rows.items()}
 check(paths['count255_no_match'].count(0x22)==255 and 0x22 not in paths['count0_no_keydereference'],'B0record exactcapturedbytecount probe bound')
 return {'selected':paths,'count_and_pointer_are_distinct_singlecaptures':True,'zero_count_reads_global_pointercell_butdoesnotdereferenceP':True,'actual_allocation_bound_or_unique_key_proved':False}


def callback_paths(r,w):
 rows={'headnull':[0,4,8,0x18,0x1a],
  'firstmatch_value_atnode8':[0,4,8,0xa,0xc,0x10,0x12],
  'secondmatch':[0,4,8,0xa,0xc,0x14,0x16,8,0xa,0xc,0x10,0x12],
  'finite_one_miss_null':[0,4,8,0xa,0xc,0x14,0x16,8,0x18,0x1a]}
 paths={k:checked(r,v) for k,v in rows.items()}
 wp={'getterzero':common.walk(w,{8:0x12}),'getternonzero_second_dereference':common.walk(w,{8:0xa})}
 return {'list_selected':paths,'wrapper_selected':wp,'list_value_at_node8_is_not_nodeaddress':True,'wrapper_loads_word_atreturnedvalue_plus8':True,
  'finite_acyclic_list_actual_functionABI_or_pointer_nonretention_proved':False}


def domains():
 validprefix=0
 for mask in range(1<<15):
  # Pure bitstring domain, no simulated records or memory access.
  firstzero=next((i for i in range(15) if not(mask>>i&1)),15)
  prefix=(1<<firstzero)-1
  check(mask&prefix==prefix and (firstzero==15 or not(mask>>firstzero&1)),'B0record firstzero-prefix scalarproperty')
  validprefix+=int(mask==prefix)
 check(validprefix==16,'B0record exactly16prefix-only occupancybitstrings')
 check(next(i for i in range(15) if not(5>>i&1))==1 and bool(5>>2&1),'B0record holecounterexample leaveslateroccupiedsuffix unvisited')
 for N in range(256):
  check(all(((i+1)&255)==i+1 for i in range(N)),'B0record capturedU8N terminationbeforeindexwrap')
  check(184*N<=46920,'B0record fullgenericarray extent')
 for i in range(15):check(4+12*i+12<=184 and 4+12*i+8+4<=184,'B0record slotfill/word geometry')
 check(4+12*15==184 and 194*3+6>=184*3,'B0record source-selected stride geometry isconditional')
 check(65536>65535 and 0xffffffff>65535,'B0record raw32keys aboveU16 cannotmatch')
 return {'occupancy_bitstring_cases':32768,'prefix_only_masks':validprefix,'hole_example_mask':5,'hole_firstzero_index':1,
  'captured_count_cases':256,'generic_max_record_bytes':46920,'slot_count':15,'slot_stride':12,'record_stride':184,
  'slot_word8_projects_from_M16_in_case22_copy12':True,'actual_record_extent_contiguous_occupancy_or_heap_proved':False}


def profile(data,hexraw,index,parent):
 bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
 c,a,r,w=(bs[x] for x in PARTS);ns={part:{v['pc']-bs[part]['start']:v for v in bs[part]['instructions']} for part in PARTS}
 cn,an,rn,wn=(ns[x] for x in PARTS);G=0x20003000;delta=80*index
 count=G+949+delta;array=G-116+delta;listhead=G-108+delta
 check(an[4]['imm']+G==count and an[0xc]['imm']+G==array and rn[4]['imm']+G==listhead,'B0record distinctcount/array/listhead roles')
 check(an[0x1e]['imm']==184 and an[0x22]['width']==2 and an[0x26]['rs2']==10 and an[0x2c]['imm']==255,'B0record firstkeymatch fullA0 andcapturedU8count grammar')
 check(cn[0x16]['target']==c['start']+0x3c and cn[0x18]['imm']==8 and cn[0x26]['imm']==12 and cn[0x34]['imm']==-12,'B0record firstzeroexit selectedword8 thenfill12/headclear')
 check(cn[0x40]['imm']==-1 and cn[0x42]['width']==2 and cn[0x10]['imm']==184,'B0record finalkeyFFFF andrecordendpoint')
 check(rn[0xa]['imm']==4 and rn[0x10]['imm']==8 and rn[0x14]['imm']==0 and wn[0xa]['imm']==8,'B0record twolevelcallback dereferences notflattened')
 # Original caller joins: B0 case22, case18 and published special-event callback.
 b=parent['bodies']['case22'];bn={v['pc']-b['start']:v for v in b['instructions']};bc={x['offset']:x['target'] for x in b['calls']}
 ac={x['offset']:x['target'] for x in parent['bodies']['case18']['calls']}
 check(bc[0x5a]==bc[0x64]==a['start'] and bc[0x2a]==ac[0x66]==w['start'],'B0record currentcase source/callbacklookup joins')
 check(bn[0x98]['op']=='jalr' and bn[0x8c]['imm']==12 and bn[0x88]['imm']==8,'B0record slot12 copyprojectsoriginalM16 toslot8')
 sb=special.body(init.binding.take(data,special.STARTS[index][2],114),'callback',index);sp=special.STARTS[index][2];sn={v['pc']-sp:v for v in sb['instructions']}
 check(sn[20]['target']==a['start'] and sn[108]['target']==c['start'] and sn[24]['target']==sp+108,'B0record mode1matchinglookupnonnull clear thenenumeration')
 # Existing ID8 publication proof, reused with no new coverage claim.
 route=task8.route8;rp=route.STARTS[index][2];res=route.body(init.binding.take(data,rp,266),'resources',index);resn={v['pc']-rp:v for v in res['instructions']}
 check(resn[16]['imm']==G and resn[20]['imm']+G==array and resn[100]['rs1']==8 and resn[100]['rs2']==10,'B0record ID8arraypublication fromallocatorreply')
 check(resn[8]['imm']+G+resn[14]['imm']==count,'B0record resourcecount sourcecell equalslookupcount')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for part,z in bs.items():
  check(sparse.captured(mem,z['start'],z['bytes'])==init.binding.take(data,z['start'],z['bytes']),'B0record strictoriginalHEX backing')
  receipts.append({'part':part,'source':z['start'],'bytes':z['bytes'],'all_bytes_captured':True})
 return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{part:common.certificates(z) for part,z in bs.items()},
  'clear_paths':clear_paths(c),'array_paths':array_paths(a),'callback_paths':callback_paths(r,w),'globals':dict(count_byte=count,array_pointer_word=array,callback_list_head_word=listhead),
  'source_reuse':{'ID8_resources':rp,'ID8_resources_sha256':res['sha256'],'special_callback':sp,'special_callback_sha256':sb['sha256'],'new_code_bytes_counted':0},
  'array_contract':['capturecountU8N andarraywordP separatelyonce;index0;whileindex!=N,readU16atP+184*i andcompareFULLentryA0;firstmatch returnsrecordaddress,elseincrementindexAND255. Count0 ->0withoutPdereference;genericN<=255 boundsprobes,noPnullguard',
   'fullentrykey>65535 cannotmatch. No stores/calls/SPwrite;firstmatchnotuniqueness. Capturedcount/array/keys extent andactualallocation unproved'],
  'clear_contract':['originalO,slotO4,endO184;firstzeroU16slothead immediatelyexits. Otherwise freshwordslot8nonnull ->privatefree(unchangedword),thenfill(slot,0,12),advanceslot12,SH0previoushead;max15slots',
   'allordinaryexits SHFFFFtoO0 evenifearlyempty;notclearO2..3 directly. Emptyfirst ->A0originalO;processedprefix ->thenlive lastfillreply,noforcedstatus. S/SP/RA/frame/O separation andnestednormalreturns required',
   'onlycontiguousoccupiedprefix visited;lateroccupiedslotsbeyondfirsthole arenotprobedorlocallycleared. Prefix-only occupancyinvariant andactualfree/filleffects notproved'],
  'callback_contract':['separatelisthead;walknode0next,compareU16node4 withfullentrykey;match RETURNSU32node8 VALUE,notnodeaddress;nullchain0. No count/cycleguard orfiniteprogressproof',
   'wrapper callslistgetter;returnedvalue0 ->0;nonnull ->loadU32[value8] andreturn. Two distinct+8dereferencelevels,notdirectfunctionfieldatlistnode8;doesnotexecute function. Actualwriters/extent/functionABI unproved'],
  'ownership_join':'case22copy12(M8->slot) projectsM16pointerVALUEtoslot8 underbytecopy/preservationpremises. Specialmode1recordlookupnonnull thenprefixclear canlaterattemptprivatefree(slot8);noexactsameallocation,exclusiveownership,finiteenumorcompletepointerlifetimeproof.',
  'premises':'conditionalcandidateISA/provider/source/queuebindings;validrecord/object/slot/list/frame/pointeeaccesses;ordinarynestedreturns,S/SP/RA/savedframepreservation;noadversealias/IRQ/DMA/reentry;fresh/capturedvalues identityseparatelyretained',
  'actual_installed_binding_fullcleanup_delivery_or_pointer_lifetime_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-B0-record-prefixclear-callbacklookup-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':352,'complete_body_instructions':134,'C_reconstruction_coverage_changed':False,
  'remaining':['callbacklist writers andreturnedobject/functionABI','slot consumers/otherwriters andcontiguousprefix invariant','ordinary4bb22,request/report effects,actualcopy/providerbindings andfullpointerlifetime'],
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
    else:raise RuntimeError('B0record instructionmutation escaped')
    mutations+=1
   for off,_ in TYPED_LOADS[i][part]:
    bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError as ex:check('typedload encoding' in str(ex),'B0record typedguard')
    else:raise RuntimeError('B0record typedmutation escaped')
    typed+=1
 check((mutations,typed)==(134,8),'B0record mutationcensus');domains()
 print('PASS:134 instruction/8 typed-load mutations rejected;32768 occupancy bitstrings;count/slot/frame domains')


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
 else:check(OUT.read_bytes()==encoded,'B0record exactledgerreplay')
 print('PASS:352B/134i complete recordlookup/prefixclear/callbacklookups;strict HEX;source/slot/specialmode joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,contiguousoccupancy,fullcleanup andpointerlifetime UNPROVED')


if __name__=='__main__':main()
