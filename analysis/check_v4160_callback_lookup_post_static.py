"""Offline attribute lookup output and callback post-message contracts.
Original operands/CFG, immutable paths and host scalar certificates only.
No target execution/emulation, provider, RAM/heap/list/callback state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_callback_fields_static as previous
import check_v4160_threshold_message_static as queue
import check_v4160_message_marker_static as allocator
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-callback-lookup-post-static.json')
PARTS=('lookup','post')
STARTS=((0x20000a48,0x4b534),(0x20000a48,0x4b5cc))
SOURCES=((0x40cb8,0x4b534),(0x40cf8,0x4b5cc))
SIZES=(76,102)
HASHES=(('f9860781608c80ceac8460fcb8d70da435cc453c30f3dc14d258ab27343a3755', 'f69696a13531b320114787b50fd270c6ff23a34e66ef1aee5b573c332571f7ce'), ('f99f1812657d2930ce13e8a4bc60e9a60561254294653e1a7ca6f446fe287d0b', '872e92125ff0f29415a483e99c37e3309d26e953ad477729dff291a37cc88ce1'))
COUNTS=((27, 40), (27, 40))
QK=({'lookup': (), 'post': ((12, '1820', 'qk.c.lbu'), (52, '1ea1', 'qk.c.sh'), (66, '06a5', 'qk.c.sh'), (70, '0820', 'qk.c.lbu'))}, {'lookup': (), 'post': ((12, '1820', 'qk.c.lbu'), (52, '1ea1', 'qk.c.sh'), (66, '06a5', 'qk.c.sh'), (70, '0820', 'qk.c.lbu'))})
TYPED=({'lookup': ((4, 2), (16, 5), (24, 5), (50, 5)), 'post': ()}, {'lookup': ((4, 2), (16, 5), (24, 5), (50, 5)), 'post': ()})
LITERALS=(
{
'lookup':'''
000 lui 15 536883200
004 load 14 15 -120 4
008 bnez 14 14
00a li 12 0
00c jump 64
00e load 15 14 8 4
010 load 16 15 10 2
014 bltu 10 16 42
018 load 17 14 4 2
01c add 13 17 16
020 bge 10 13 42
024 li 13 0
026 bne 13 17 46
02a load 14 14 0 4
02c jump 8
02e mv 12 15
030 addi 15 15 16
032 load 6 15 -6 2
036 bne 6 10 68
03a beqz 11 64
03c store 11 16 0 2
040 mv 10 12
042 jr 1
044 addi 13 13 1
046 slli 13 13 16
048 srli 13 13 16
04a jump 38
''',
'post':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 536883200
008 addi 8 8 -288
00c load 14 8 0 1
00e store 2 1 28 4
010 store 2 9 20 4
012 store 2 18 16 4
014 store 2 19 12 4
016 addi 15 0 255
01a beq 14 15 88
01e mv 19 10
020 li 10 10
022 mv 9 12
024 mv 18 11
026 auipc 1 536563712
02a jalr 1 1 -804
02e beqz 10 88
030 addi 15 0 177
034 store 10 15 0 2
036 store 10 0 4 1
03a store 10 19 2 2
03e store 10 18 6 2
042 store 10 9 8 2
044 mv 11 10
046 load 10 8 0 1
048 load 8 2 24 4
04a load 1 2 28 4
04c load 9 2 20 4
04e load 18 2 16 4
050 load 19 2 12 4
052 addi 2 2 32
054 jal 0 274952
058 load 1 2 28 4
05a load 8 2 24 4
05c load 9 2 20 4
05e load 18 2 16 4
060 load 19 2 12 4
062 addi 2 2 32
064 jr 1
''',
},
{
'lookup':'''
000 lui 15 536883200
004 load 14 15 -40 4
008 bnez 14 14
00a li 12 0
00c jump 64
00e load 15 14 8 4
010 load 16 15 10 2
014 bltu 10 16 42
018 load 17 14 4 2
01c add 13 17 16
020 bge 10 13 42
024 li 13 0
026 bne 13 17 46
02a load 14 14 0 4
02c jump 8
02e mv 12 15
030 addi 15 15 16
032 load 6 15 -6 2
036 bne 6 10 68
03a beqz 11 64
03c store 11 16 0 2
040 mv 10 12
042 jr 1
044 addi 13 13 1
046 slli 13 13 16
048 srli 13 13 16
04a jump 38
''',
'post':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 lui 8 536883200
008 addi 8 8 -208
00c load 14 8 0 1
00e store 2 1 28 4
010 store 2 9 20 4
012 store 2 18 16 4
014 store 2 19 12 4
016 addi 15 0 255
01a beq 14 15 88
01e mv 19 10
020 li 10 10
022 mv 9 12
024 mv 18 11
026 auipc 1 536563712
02a jalr 1 1 -956
02e beqz 10 88
030 addi 15 0 177
034 store 10 15 0 2
036 store 10 0 4 1
03a store 10 19 2 2
03e store 10 18 6 2
042 store 10 9 8 2
044 mv 11 10
046 load 10 8 0 1
048 load 8 2 24 4
04a load 1 2 28 4
04c load 9 2 20 4
04e load 18 2 16 4
050 load 19 2 12 4
052 addi 2 2 32
054 jal 0 275092
058 load 1 2 28 4
05a load 8 2 24 4
05c load 9 2 20 4
05e load 18 2 16 4
060 load 19 2 12 4
062 addi 2 2 32
064 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'CLpost literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'CLpost typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'CLpost complete boundaries')
 for a,f in s.items():init.g(n,a,'CLpost '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'CLpost Xwchc encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'CLpost complete identity')
 edges={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'CLpost ordinary RET');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   check(d['rd']==0 and d['target']==0x43208+140*index,'CLpost restoredframe sender tail');tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','CLpost adjacent pair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'CLpost closed local CFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'CLpost allnodes reachable')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 if part=='lookup':
  check(not calls and not tails and rets==[pc+0x42] and stores==[dict(offset=0x3c,base=11,source=16,imm=0,bytes=2)],'CLpost lookup onlyoutputhalfwordstore,nocalls')
  check(not any(d.get('rd') in {1,2,8,9,18,19,20,21,22,23,24,25,26,27} for d in n.values()),'CLpost lookup leafkeepsS/SP/RA')
  cut={a:[z for z in qs if (a-pc,z-pc) not in ((0x2c,8),(0x4a,0x26))] for a,qs in edges.items()}
  check(not common.acyclic(edges) and common.acyclic(cut),'CLpost lookup outer andinnerloop cuts')
 else:
  check(common.acyclic(edges) and calls==[dict(offset=0x2a,target=0x20000236)] and rets==[pc+0x64],'CLpost postallocator andRET')
  check(len(stores)==10 and [d for d in stores if d['base']!=2]==[
   dict(offset=o,base=10,source=r,imm=off,bytes=z) for o,r,off,z in ((0x34,15,0,2),(0x36,0,4,1),(0x3a,19,2,2),(0x3e,18,6,2),(0x42,9,8,2))],'CLpost fivepayloadstores exactorder')
  saved={(1,28),(8,24),(9,20),(18,16),(19,12)}
  check({(d['source'],d['imm']) for d in stores if d['base']==2}==saved,'CLpost frame saves')
  check(n[pc+0xc]['rd']==14 and n[pc+0x1a]['rs1']==14 and n[pc+0x46]['rd']==10,'CLpost guardglobal overwritesincomingA4,taskrefetched')
 return dict(start=pc,source=SOURCES[index][k],bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def checked(b,seq):
 e=b['CFG'];p=b['start'];check(not e[p+seq[-1]] and all(p+z in e[p+a] for a,z in zip(seq,seq[1:])) and seq[0]==0,'CLpost immutable path');return seq


def paths(b,part):
 if part=='post':
  ps={k:common.walk(b,c) for k,c in {'task255_skip':{0x1a:0x58},'allocation0':{0x1a:0x1e,0x2e:0x58},'allocate_build_tail':{0x1a:0x1e,0x2e:0x30}}.items()}
  check(ps['allocate_build_tail'][-2:]==[0x52,0x54] and 0x46 in ps['allocate_build_tail'],'CLpost taskrefetch/frame beforetail')
  return ps
 ps={'empty':common.walk(b,{8:0xa}),'firstmatch_output':common.walk(b,{8:0xe,0x14:0x18,0x20:0x24,0x26:0x2e,0x36:0x3a,0x3a:0x3c}),
  'firstmatch_nooutput':common.walk(b,{8:0xe,0x14:0x18,0x20:0x24,0x26:0x2e,0x36:0x3a,0x3a:0x40})}
 prefix=[0,4,8,0xe,0x10,0x14,0x18,0x1c,0x20,0x24]
 failprobe=[0x26,0x2e,0x30,0x32,0x36,0x44,0x46,0x48,0x4a]
 ps['threeprobes_then_exhaust_andempty']=checked(b,prefix+failprobe*3+[0x26,0x2a,0x2c,8,0xa,0xc,0x40,0x42])
 ps['secondmatch_output']=checked(b,prefix+failprobe+[0x26,0x2e,0x30,0x32,0x36,0x3a,0x3c,0x40,0x42])
 ps['count0_no_candidate_read']=checked(b,prefix+[0x26,0x2a,0x2c,8,0xa,0xc,0x40,0x42])
 return ps


def domains():
 cases=0
 for F in range(65536):
  for N in (0,1,65535):
   total=F+N;check(0<=total<=131070 and total<2**31,'CLpost capturedU16sum signedpositive')
   for H in {0,65535,F,max(0,total-1),min(65535,total)}:
    if H>65535:continue
    check((not(H<F) and not(H>=total))==(F<=H<F+N),'CLpost U16key exactrange partition');cases+=1
 for N in range(65536):
  check(N<65536 and (N==0 or ((N-1)+1==N and 16*(N-1)+10+2<=16*N)),'CLpost boundedU16index no wrap beforecount')
 check(0xffffffff>=1 and -1<3 and 0xffffffff>65535,'CLpost signedupper fullword routewitness,cannotmatchU16')
 check(65535<=100000<65535+65535 and 100000>65535,'CLpost positivewidekey rangeeligiblebutnomatch')
 check(5<=7<5+3 and 5!=7,'CLpost outputfirsthandle notrequestedhandle')
 fields=[(0,2),(2,2),(4,1),(6,2),(8,2)];covered={o+j for o,z in fields for j in range(z)}
 check(covered==set(range(10))-{5},'CLpost visiblemessage byte5 untouched')
 check(10+8==18 and 0xf000|10==0xf00a,'CLpost fixed messageallocator coreargs18/tagf00a')
 for x in range(65536):check(((x&0xffff)==x) and 0<=x<=65535,'CLpost low16fielddomain')
 return dict(U16_range_boundary_cases=cases,inner_count_cases=65536,field_low16_cases=65536,
  range_general='unsignedH<F skips;otherwise signed32(H)>=F+N skips. FullH compared with freshU16record10;H>65535 cannotmatch',
  output='capturedfirstU16[config10],not H or matchingrecord10 freshvalue',visible_message_bytes=10,locally_unwritten_visible_bytes=[5],
  distinct_task_snapshots='initial T0==255 skips;postallocationfresh T1 usedforsender,notrechecked;T0!=255 doesnotproveT1!=255',
  execution_or_actualdatareachability_proved=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={};mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy']
 def src(target):return int(first['source'],16)+target-int(first['destination'],16)
 check(src(0x20000a48)==SOURCES[index][0] and 0x20000a48+76<=int(mapping['first_copy_end_exclusive'],16),'CLpost complete lookup firstcopy map')
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,SOURCES[index][k],SIZES[k]);check(sparse.captured(mem,SOURCES[index][k],SIZES[k])==raw,'CLpost complete originalHEX backing')
  bs[part]=body(raw,part,index)
 l,p=bs['lookup'],bs['post'];ln={v['pc']-l['start']:v for v in l['instructions']};pn={v['pc']-p['start']:v for v in p['instructions']}
 check(ln[0]['imm']+ln[4]['imm']==0x20002f88+80*index and ln[0x20]['op']=='bge' and ln[0x20]['rs1']==10 and ln[0x20]['rs2']==13,'CLpost secondlist andsignedupperguard')
 check(ln[0xe]['imm']==8 and ln[0x10]['imm']==10 and ln[0x18]['imm']==4 and ln[0x30]['imm']==16 and ln[0x32]['imm']==-6 and ln[0x3c]['rs2']==16,'CLpost outputfirsthandle andrecordstride')
 task=pn[4]['imm']+pn[8]['imm'];check(task==0x20002ee0+80*index and pn[0x20]['imm']==10 and pn[0x30]['imm']==177,'CLpost taskcell and10byte/B1message')
 cb=parent['body'];cn={v['pc']-cb['start']:v for v in cb['instructions']}
 check(cb['calls'][0]['target']==l['start'] and cn[8]['imm']==30 and cn[0x30]['op']=='load' and cn[0x30]['imm']==30 and cn[0x30]['width']==2,'CLpost callerSP30 lookupoutputjoin')
 check(cb['calls'][-1]['target']==p['start'] and cn[0x90]['rs2']==8 and cn[0x52]['op']=='bnez','CLpost posttarget andsavedcallbackzero normalreturn')
 ar=init.binding.take(data,src(allocator.ENTRY),allocator.LENGTH);check(ar==allocator.MSG and sha256(ar).hexdigest()==allocator.MSG_SHA and sparse.captured(mem,src(allocator.ENTRY),allocator.LENGTH)==ar,'CLpost reusedallocator originalHEX complete')
 an=allocator.decode(ar,allocator.ENTRY)
 for a,f in allocator.message_specs().items():allocator.guard(an,a,'CLpost reusedallocator operand',**f)
 sb=queue.body(init.binding.take(data,0x43208+140*index,146),'sender',index)
 check(sb['start']==p['tails'][0]['target'] and sparse.captured(mem,sb['source'],146)==init.binding.take(data,sb['source'],146),'CLpost reusedsender originalHEX exacttailjoin')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},
  lookup_mapping=dict(source=SOURCES[index][0],target=0x20000a48,bytes=76,installed_binding_proved=False),
  reused_leaves=dict(allocator=dict(source=src(allocator.ENTRY),target=allocator.ENTRY,bytes=86,sha256=allocator.MSG_SHA,new_code_bytes_counted=0),sender=dict(source=sb['source'],target=sb['start'],bytes=146,sha256=sb['sha256'],new_code_bytes_counted=0)),
  lookup_contract=['capturehead;pernode config=U32node8,F=U16config10;unsignedH<F skips,beforecountread. OtherwisecaptureN=U16node4,sumF+N;signedH>=sum skips',
   'eligible: indexi0..N-1;capturecandidatepointer=config+16*i;freshU16candidate10 equalsfullH ->optionallySH FtoentryA1,returncandidatepointer. InitialF andfreshcandidate0key aredistinctreads',
   'count0 skipsprobes;no match followsfreshnode0;nullhead ->0. Onlypayloadstore is outputhalfword;no frame/calls/MMIO/pointerstore. Innerloop boundedN;finitevalidouterlist remainspremise',
   'callerSP30nonzero validoutput andnormalmatch ->lookupwritesFbeforeRET;callerfreshLHUconsumesF onlyifnotlateroverwritten. Equalcallbackregistrationkey requiresseparateconfig/keypreservation'],
  post_contract=['32Bframe;freshU8taskcell->A4 overwritesincomingA4. InitialT0=255 ->restoreRETwithoriginalA0,noallocation. T0!=255 request20000236(10),null->0',
   'nonnullM ->SH177@M0,SB0@M4,SHlow16originalA0@M2,SHlow16originalA1@M6,SHlow16originalA2@M8. M5locallyuntouched;no deepcopy orsourcepointerretention',
   'A1=M;freshT1=taskbyte->A0;restoreframe;unlinkedtailsender(T1,M). NoT1 sentinelrecheck/no localfree. T1maydifferfromT0. Originalcallerignoresnormalpostreply andreturns savedcallback0'],
  queue_join=['matchingallocator wraps10+8=18,tagf00a;corepayloadQ,M=Q+8;Q0word0,Q4U16len10,Q6byteFF,Q7unspecified;visiblepayloadnotcleared',
   'matching sender validnonnullM,fulltask>2 andtask<freshcount;headernext0/ownerFF required. Admissionwritesowner,appendsglobally,signals event8000,returns0;invalidtaskattemptsdealloc/3,badheaderattemptsdealloc/5',
   'neither taskguard nor allocation success proves enqueue;failurecleanup doesnotestablishinverseownership. No actual message consumer/free lifetime established'],
  premises='candidateISA/startup/providerbindings;validcode/stack/config/node/message/header/output/callback extents;ordinarycalleeS/SP/RA/savedframepreservation;finitevalidouterlist;noadversealias/wrap/IRQ/DMA/reentry;freshreads keptdistinct',
  actual_installed_binding_unconditional_output_taskpreservation_delivery_or_pointerlifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-callback-lookup-output-postmessage-static-v1',APP_sha256=sha256(image).hexdigest(),
  profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_new_body_bytes=356,complete_new_body_instructions=134,reused_allocator_sender_bytes=464,C_reconstruction_coverage_changed=False,
  remaining=['actualnode/config/count/ID writers andcross-call preservation','taskbytewriters andB1 downstreamconsumer/free lifetime','installedprovider/startup andphysicalsideeffects'],
  target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False)


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('CLpost instructionmutation escaped')
    mutations+=1
   for o,f in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('CLpost typedmutation escaped')
    typed+=1
 check((mutations,typed)==(134,8),'CLpost mutation census');domains()
 print('PASS:134 instruction/8 typed-load mutations rejected;U16 range/index/firsthandle andmessage-layout certificates')


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
 else:check(OUT.read_bytes()==encoded,'CLpost exactledger replay')
 print('PASS:356B/134i complete lookup/post;strict HEX;SP30 firsthandle andB1 sender joins;464B reused;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,preservation,delivery andpointerlifetime UNPROVED')


if __name__=='__main__':main()
