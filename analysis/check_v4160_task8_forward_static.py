"""Offline task8 B0-forwarder and pointer-selection leaf contracts.
Immutable original operands/CFG, host scalar and interval algebra only.
No target instructions, callbacks, provider, RAM/heap or hardware are run.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_task8_callback_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-task8-forward-static.json')
PARTS=('forwarder','pointerleaf')
STARTS=((0x49e4a,0x49dcc),(0x49ee2,0x49e64))
SIZES=(134,126)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('d883a484f5ab54a9f5d66b802166d8ec417f14cdc13f39c69dbd4b01ad320788', 'a9d45ed5a0ccb2a85e7d769f0cfeea5824d1cf46b1d8c0d1165667ff0a12b420'), ('9492021de165bb832ff3ef9560d1561603489beacf0d94049b118706924b073e', 'a9d45ed5a0ccb2a85e7d769f0cfeea5824d1cf46b1d8c0d1165667ff0a12b420'))
COUNTS=((51, 45), (51, 45))
TYPED_LOADS=({'forwarder': (), 'pointerleaf': ()}, {'forwarder': (), 'pointerleaf': ()})
LITERALS=(
{
'forwarder':'''
000 addi 15 0 255
004 beq 10 15 130
008 addi 2 2 -32
00a store 2 9 20 4
00c mv 9 10
00e addi 10 0 32
012 store 2 8 24 4
014 store 2 18 16 4
016 store 2 19 12 4
018 store 2 20 8 4
01a store 2 21 4 4
01c store 2 1 28 4
01e mv 18 14
020 mv 19 13
022 mv 21 12
024 mv 20 11
026 auipc 1 536567808
02a jalr 1 1 966
02e mv 8 10
030 li 10 19
032 beqz 8 100
034 addi 15 0 -80
038 store 8 15 0 1
03a store 8 21 1 1
03e store 8 20 2 2
042 store 8 19 4 1
046 addi 10 8 8
04a li 12 24
04c beq 18 0 118
050 mv 11 18
052 auipc 1 536567808
056 jalr 1 1 1174
05a mv 11 8
05c mv 10 9
05e jal 1 274952
062 li 10 0
064 load 1 2 28 4
066 load 8 2 24 4
068 load 9 2 20 4
06a load 18 2 16 4
06c load 19 2 12 4
06e load 20 2 8 4
070 load 21 2 4 4
072 addi 2 2 32
074 jr 1
076 li 11 0
078 auipc 1 536567808
07c jalr 1 1 1242
080 jump 90
082 li 10 2
084 jr 1
''',
'pointerleaf':'''
000 li 15 15
002 beq 11 15 122
006 bltu 15 11 56
00a li 15 9
00c beq 11 15 122
010 bltu 15 11 42
014 li 15 6
016 beq 11 15 110
01a li 15 7
01c beq 11 15 122
020 li 15 5
022 beq 11 15 122
026 li 10 0
028 jr 1
02a li 15 13
02c beq 11 15 122
030 bltu 15 11 114
034 li 15 11
036 jump 34
038 li 15 23
03a beq 11 15 118
03e bltu 15 11 82
042 li 15 18
044 beq 11 15 122
048 li 15 22
04a beq 11 15 118
04e li 15 17
050 jump 34
052 li 15 29
054 beq 11 15 122
058 bltu 15 11 96
05c li 15 27
05e jump 34
060 addi 15 0 82
064 beq 11 15 122
068 addi 15 0 210
06c jump 34
06e load 10 10 12 4
070 jr 1
072 load 10 10 0 4
074 jr 1
076 load 10 10 8 4
078 jr 1
07a load 10 10 4 4
07c jr 1
''',
},
{
'forwarder':'''
000 addi 15 0 255
004 beq 10 15 130
008 addi 2 2 -32
00a store 2 9 20 4
00c mv 9 10
00e addi 10 0 32
012 store 2 8 24 4
014 store 2 18 16 4
016 store 2 19 12 4
018 store 2 20 8 4
01a store 2 21 4 4
01c store 2 1 28 4
01e mv 18 14
020 mv 19 13
022 mv 21 12
024 mv 20 11
026 auipc 1 536567808
02a jalr 1 1 814
02e mv 8 10
030 li 10 19
032 beqz 8 100
034 addi 15 0 -80
038 store 8 15 0 1
03a store 8 21 1 1
03e store 8 20 2 2
042 store 8 19 4 1
046 addi 10 8 8
04a li 12 24
04c beq 18 0 118
050 mv 11 18
052 auipc 1 536567808
056 jalr 1 1 1022
05a mv 11 8
05c mv 10 9
05e jal 1 275092
062 li 10 0
064 load 1 2 28 4
066 load 8 2 24 4
068 load 9 2 20 4
06a load 18 2 16 4
06c load 19 2 12 4
06e load 20 2 8 4
070 load 21 2 4 4
072 addi 2 2 32
074 jr 1
076 li 11 0
078 auipc 1 536567808
07c jalr 1 1 1090
080 jump 90
082 li 10 2
084 jr 1
''',
'pointerleaf':'''
000 li 15 15
002 beq 11 15 122
006 bltu 15 11 56
00a li 15 9
00c beq 11 15 122
010 bltu 15 11 42
014 li 15 6
016 beq 11 15 110
01a li 15 7
01c beq 11 15 122
020 li 15 5
022 beq 11 15 122
026 li 10 0
028 jr 1
02a li 15 13
02c beq 11 15 122
030 bltu 15 11 114
034 li 15 11
036 jump 34
038 li 15 23
03a beq 11 15 118
03e bltu 15 11 82
042 li 15 18
044 beq 11 15 122
048 li 15 22
04a beq 11 15 118
04e li 15 17
050 jump 34
052 li 15 29
054 beq 11 15 122
058 bltu 15 11 96
05c li 15 27
05e jump 34
060 addi 15 0 82
064 beq 11 15 122
068 addi 15 0 210
06c jump 34
06e load 10 10 12 4
070 jr 1
072 load 10 10 0 4
074 jr 1
076 load 10 10 8 4
078 jr 1
07a load 10 10 4 4
07c jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'forward literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
 check(n.keys()==s.keys(),'forward complete instruction boundaries '+part)
 for a,f in s.items():init.g(n,a,'forward operand '+part+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'forward complete identity '+part)
 edges={};calls=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'forward ordinary RET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'forward linked directcall');calls.append({'offset':a-pc,'target':d['target']})
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','forward adjacentlinked pair')
   calls.append({'offset':a-pc,'target':(a-4+u['imm']+d['imm'])&0xfffffffe})
  check(all(z in n for z in q),'forward closed local CFG');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'forward complete reachable DAG')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 if part=='pointerleaf':
  check(not calls and not stores and len(returns)==5,'pointerleaf no calls/stores andfiveRETs')
  check({d['rd'] for d in n.values() if d.get('rd',0)}=={10,15},'pointerleaf onlyA0/A5 encodeddefinitions;noSPwrite')
  check([(a-pc,d['imm'],d['rs1'],d['width']) for a,d in n.items() if d['op']=='load']==[(0x6e,12,10,4),(0x72,0,10,4),(0x76,8,10,4),(0x7a,4,10,4)],'pointerleaf exact unguardedwordloads')
 else:
  check(calls==[dict(offset=o,target=t) for o,t in [(0x2a,0x20000236),(0x56,0x20000332),(0x5e,0x43208+140*index),(0x7c,0x2000039c)]],'forward completecallcensus')
  check(len(stores)==11 and returns==[pc+0x74,pc+0x84],'forward store/returncensus')
  check([d for d in stores if d['base']!=2]==[dict(offset=0x38,base=8,source=15,imm=0,bytes=1),dict(offset=0x3a,base=8,source=21,imm=1,bytes=1),dict(offset=0x3e,base=8,source=20,imm=2,bytes=2),dict(offset=0x42,base=8,source=19,imm=4,bytes=1)],'forward exactvisiblemessagefields')
  saves={(d['source'],d['imm']) for d in stores if d['base']==2}
  restores={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}
  check(saves==restores=={(1,28),(8,24),(9,20),(18,16),(19,12),(20,8),(21,4)},'forward exactsave/restorelayout')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=returns,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def forward_paths(b):
 selections={'task_exact255':{4:0x82},'allocation_null':{4:8,0x32:0x64},
  'allocation_nonnull_source_nonnull':{4:8,0x32:0x34,0x4c:0x50},'allocation_nonnull_source_null':{4:8,0x32:0x34,0x4c:0x76}}
 selected={k:common.walk(b,v) for k,v in selections.items()};n={v['pc']-b['start']:v for v in b['instructions']}
 allpaths=task8.v34.allocation.previous.dag_paths(b);check(len(allpaths)==4,'forward four immutable paths')
 for name,seq in selected.items():
  last=[o for o in seq if n[o].get('rd')==10][-1]
  check(n[last]['op']=='li' and n[last]['imm']==(2 if name=='task_exact255' else 19 if name=='allocation_null' else 0),'forward path fixedreply2/19/0')
  check((0x5e in seq)==name.startswith('allocation_nonnull'),'forward sender iffallocationnonnull')
  if 0x5e in seq:check(seq[seq.index(0x5e)+1]==0x62 and n[0x62]['imm']==0,'forward senderreplyunconditionally overwritten')
 # Explicit A0=32 is the only argument preparation before allocation; A4 stillsource.
 for seq in selected.values():
  if 0x2a in seq:check(not any(n[o].get('rd')==14 for o in seq[:seq.index(0x2a)]),'forward ambientA4source stilllive atallocator')
 return {'selected':selected,'syntactic_paths':len(allpaths),'allpaths_sha256':sha256(json.dumps(allpaths,separators=(',',':')).encode()).hexdigest(),
  'normalreturn_andcallee_frame_preservation_required':True,'sender0_queueing_or_pointer_nonretention_proved':False}


def leaf_intervals(b):
 # Immutable path predicates and host intervals only. No registers or memory are
 # stepped: each branch's threshold is the last literal A5 definition in its
 # recorded prefix. All other leaf A5 definitions are rejected below.
 n={v['pc']-b['start']:v for v in b['instructions']};pc=b['start'];rows=[]
 allpaths=task8.v34.allocation.previous.dag_paths(b)
 check(all(d['op']=='li' or d['op']=='addi' and d['rs1']==0 for d in n.values() if d.get('rd')==15),'pointerleaf thresholddefinitions are literals')
 for seq in allpaths:
  intervals=[(0,0xffffffff)];predicates=[]
  for j,o in enumerate(seq[:-1]):
   d=n[o]
   if d['op'] not in BRANCHES:continue
   defs=[n[z]['imm'] for z in seq[:j] if n[z].get('rd')==15];check(bool(defs),'pointerleaf literalthreshold dominatesbranch');c=defs[-1]
   taken=seq[j+1]==d['target']-pc
   check(d['op'] in ('beq','bltu'),'pointerleaf unsignedliteral predicategrammar')
   if d['op']=='beq':
    check((d['rs1'],d['rs2'])==(11,15),'pointerleaf equalityoperandgrammar')
    ranges=[(c,c)] if taken else [(0,c-1),(c+1,0xffffffff)]
   else:
    check((d['rs1'],d['rs2'])==(15,11),'pointerleaf unsignedcompareoperandgrammar')
    ranges=[(c+1,0xffffffff)] if taken else [(0,c)]
   intervals=[(max(a,x),min(z,y)) for a,z in intervals for x,y in ranges if max(a,x)<=min(z,y)]
   predicates.append([o,d['op'],c,taken])
  if not intervals:continue
  loads=[n[o]['imm'] for o in seq if n[o]['op']=='load'];offset=loads[-1] if loads else None
  check(len(loads)<=1,'pointerleaf oneorzero sourcewordload')
  if not loads:check(any(n[o]['op']=='li' and n[o].get('rd')==10 and n[o]['imm']==0 for o in seq),'pointerleaf defaultfixedzero')
  rows.append({'intervals':intervals,'load_offset_or_fixedzero':offset,'path':seq,'predicates':predicates})
 flat=sorted((a,z,r['load_offset_or_fixedzero']) for r in rows for a,z in r['intervals'])
 check(flat[0][0]==0 and flat[-1][1]==0xffffffff and all(a[1]+1==z[0] for a,z in zip(flat,flat[1:])),'pointerleaf disjointcompleteU32partition')
 expected={0:[14],4:[5,7,9,11,13,15,17,18,27,29,82,210],8:[22,23],12:[6]}
 for off,ops in expected.items():
  actual=[op for a,z,o in flat if o==off for op in range(a,z+1)]
  check(sorted(actual)==ops,'pointerleaf complete exact U32 wordoffset group '+str(off))
 check(sum(z-a+1 for a,z,o in flat if o is not None)==16,'pointerleaf exactly16U32opcode values load')
 check(sum(z-a+1 for a,z,o in flat if o is None)==2**32-16,'pointerleaf remainingU32values returnzero')
 return {'syntactic_paths':len(allpaths),'nonempty_predicate_paths':len(rows),'U32_partition':flat,'certificates':rows,
  'exact_word_offset_groups':expected,'fixedzero_U32_cases':2**32-16,'target_memory_read_or_execution':False}


def domains():
 groups={0:{14},4:{5,7,9,11,13,15,17,18,27,29,82,210},8:{22,23},12:{6}}
 admitted=previous.domains()['other_callback_opcodes'];leafops=sorted(set(admitted)-{4,30})
 check(leafops==[2,6,8,10,12,14,16,18,22,24],'forward callerleafdomain requires unchangedtuple')
 selected={op:off for off,ops in groups.items() for op in leafops if op in ops}
 check(selected=={14:0,18:4,22:8,6:12},'forward onlyfour initialcalleropcodes canselectword')
 direct={0,1,2,3,4};copied=set(range(8,32));check(set(range(32))-direct-copied=={5,6,7},'forward exactunwrittenlocalmessagegap')
 check(8+24==32 and all(off+4<=24 for off in groups),'forward selectedwordfits24B copiedrecord underextentpremise')
 cases=0
 for task in range(256):
  for count in range(256):
   sender_accept=2<task<count
   check(sender_accept==(3<=task<=count-1),'forward independent sender task/count algebra')
   cases+=int(sender_accept)
 check(cases==31878 and 0!=255 and 256!=255,'forward fullregister255 guard notU8rangevalidation')
 return {'byte_task_count_cases':65536,'sender_task_admitted_cases':cases,'conditional_unchangedtuple_leaf_opcodes':leafops,
  'conditional_nonzero_word_selection':selected,'local_message_written_bytes':sorted(direct),'provider_copy_or_fill_extent':[8,31],
  'local_message_gap':[5,6,7],'record_copy_bytes':24,'visible_request':32,'sourceextent_initialized_or_deepcopy_proved':False}


def profile(data,hexraw,index,parent):
 bs={part:body(init.binding.take(data,STARTS[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
 f,l=bs['forwarder'],bs['pointerleaf'];fn={d['pc']-f['start']:d for d in f['instructions']}
 check(fn[0]['imm']==255 and fn[4]['rs1']==10 and fn[4]['op']=='beq','forward exactfulltask255 rejection')
 check(fn[0xe]['imm']==32 and fn[0x34]['imm']&255==0xb0 and fn[0x4a]['imm']==24,'forward request,typeB0,record24')
 check([fn[o]['rs2'] for o in (0x1e,0x20,0x22,0x24)]==[14,13,12,11],'forward captureentrysource/opcode/flag/ID')
 check(fn[0x46]['rs1']==8 and fn[0x46]['imm']==8 and fn[0x50]['rs2']==18,'forward recordcopyusesoriginalA4toM8')
 check(fn[0x5a]['rs2']==8 and fn[0x5c]['rs2']==9,'forward sendergetsoriginalfulltask andsavedM')
 cb=parent['body'];cn={d['pc']-cb['start']:d for d in cb['instructions']}
 check([c['target'] for c in cb['calls'] if c['offset'] in (0x5e,0x17a)]==[f['start']]*2 and [c['target'] for c in cb['calls'] if c['offset']==0x188]==[l['start']],'forward callbackbothcallers andleafjoin')
 check(cn[0x56]['imm']==0 and cn[0x5a]['imm']==0 and cn[0x174]['imm']==24 and cn[0x176]['imm']==0,'forward opcode30nullsource vsrowsuccessSP24 source,callbackA2zero')
 check(cn[0x180]['target']==cb['start']+0x2e and cn[0x18e]['rs2']==0,'forward nonzeroreturn bypassesflagclear')
 sender=common.body(init.binding.take(data,common.STARTS[index][2],146),'sender',index)
 check(sender['start']==0x43208+140*index,'forward exactexisting senderreuse')
 sn={d['pc']-sender['start']:d for d in sender['instructions']}
 check(sn[0x30]['op']=='bgeu' and sn[0x36]['op']=='bltu' and sn[0x56]['op']=='bnez','forward sender task/headergates unchanged')
 allocator=common.message;araw=init.binding.take(data,0x404a6+64*index,allocator.LENGTH)
 check(sha256(araw).hexdigest()==allocator.MSG_SHA and allocator.ENTRY==0x20000236,'forward mappedmessageallocatoridentityreuse')
 _,mem=sparse.inspect(hexraw,sparse.parser());receipts=[]
 for part,b in bs.items():
  check(sparse.captured(mem,b['start'],b['bytes'])==init.binding.take(data,b['start'],b['bytes']),'forward strictoriginalHEX backing')
  receipts.append({'part':part,'source':b['start'],'bytes':b['bytes'],'all_bytes_captured':True})
 return {'label':init.binding.PROFILES[index][0],'bodies':bs,'HEX_capture_receipts':receipts,'CFG_certificates':{part:common.certificates(b) for part,b in bs.items()},
  'forward_paths':forward_paths(f),'leaf_interval_certificates':leaf_intervals(l),'reused_sender':{'start':sender['start'],'bytes':146,'sha256':sender['sha256'],'new_code_bytes_counted':0},
  'reused_allocator':{'entry':allocator.ENTRY,'source':0x404a6+64*index,'bytes':allocator.LENGTH,'sha256':allocator.MSG_SHA,'new_code_bytes_counted':0},
  'forward_contract':['fulltask255 ->2 beforeframe/alloc;otherwisealloc32 via20000236,ambientA4source remainslive;alloc0 ->19',
   'nonnullM:storeB0at0,low8inputA2at1,low16inputA1at2,low8inputA3at4. No localaccessbytes5..7; sourceA4nonnull ->copy24toM8,elsefill24zero',
   'sender(originalfulltask,M),ignoreitsfullreply andreturn0. No localrelease. Sourceandembeddedpointerownership/nonretention andsenderdisposition notproved'],
  'callback_join':'opcode30 passesnullsource andignores2/19/0. Row-success passesfresh taskbyte/SP24source;2or19propagatebeforeflagclear. Helper0permitsleaf;nonzeroselectedwordclearsflag,evenwhenunderlyingsenderrejected3/5,sincehelperforces0.',
  'sender_boundary':'existingconditional sender requiresfulltask>2 and<freshcount,U32M-8zero andU8M-2FF;rejecttask ->deallocattemptthen3;badheader ->deallocattemptthen5. Helper0doesnotprovequeuepublication. DeallocatorpassesMunchanged,notcorepayloadM-8;actualreleaseunproved.',
  'leaf_contract':'no calls,stores orSPchanges;fullU32opcode,nottruncated. Exactly16opcodevaluesselectoneU32word atoffset0/4/8/12;allotherU32valuesreturn0. No pointeridentity,extent,ownership ornonnullsourceguard.',
  'premises':'conditionalcandidateISA/code/provider/queuebindings;validmessage/frame/source/header/selectedwordextents;normalnestedreturns andS/SP/RA/savedframepreservation;noadversealias/IRQ/DMA/reentry;freshopcodestability isextra for narrowedcallerleafset',
  'actual_installed_binding_delivery_payload_ownership_or_nonretention_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-task8-B0forward-pointerleaf-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':520,'complete_body_instructions':192,'C_reconstruction_coverage_changed':False,
  'remaining':['B0message consumer andnestedpayloadrelease/retention','rowdecoder/handlers andothercallbacksource','actualcopy/fill/allocator/providerbindings andotherwriters'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=unsigned=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
   for a,d in n.items():
    off=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('forward instructionmutation escaped')
    mutations+=1
    if d['op']=='bltu':
     bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^0x2000).to_bytes(4,'little')
     check(decode(bad,STARTS[i][k])[a]['op']=='blt','forward signedbranchmutation fixture')
     try:body(bad,part,i)
     except RuntimeError as ex:check('operand' in str(ex),'forward exactunsignedbranchguard')
     else:raise RuntimeError('forward signedbranchmutation escaped')
     unsigned+=1
 check((mutations,unsigned)==(192,10),'forward mutationcensus');domains()
 print('PASS:192 instruction/10 unsigned-to-signed branch mutations rejected;complete U32 leaf intervalpartition;task/count/message/frame domains')


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
 else:check(OUT.read_bytes()==encoded,'forward exactledgerreplay')
 print('PASS:520B/192i complete B0forwarder/pointerleaf;strict HEX;callback/status19/ignored-senderreply joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,delivery,deepcopy andpointer lifetime/ownership UNPROVED')


if __name__=='__main__':main()
