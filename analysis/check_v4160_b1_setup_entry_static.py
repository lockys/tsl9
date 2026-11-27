"""Offline bounded setup entry: object fields, register-pointer effects and range call.
Original operands/immutable def-use/CFG and closed host scalar identities only.
No target execution/emulation, mutable target/provider/IRQ model or hardware.
"""
import argparse,json,sys
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_bb_irq_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-setup-entry-static.json')
STARTS=(0x5d006,0x5d14e)
SIZE=238
COUNT=83
HASHES=('725ce1b54cdb0deebffa17a9b0c38979032ea960c099f42321c153cff9af1c8a', 'f604fa4e2a8cc6efe5eac88bef0805c741ebab5fc3616af19b0b8f5f68814c9c')
LITERALS="""
000 addi 2 2 -80
002 store 2 9 68 4
004 lui 9 536883200
008 store 2 18 64 4
00a load 13 9 1340 4
00e lui 18 536883200
012 load 12 18 1288 4
016 store 2 1 76 4
018 store 2 19 60 4
01a store 2 20 56 4
01c store 2 21 52 4
01e store 2 24 40 4
020 store 2 8 72 4
022 store 2 22 48 4
024 store 2 23 44 4
026 store 2 25 36 4
028 store 2 26 32 4
02a store 2 27 28 4
02c addi 14 0 160
030 store 13 14 100 4
032 load 14 12 44 4
034 lui 19 536883200
038 mv 24 10
03a andi 14 14 -4
03c ori 14 14 1
040 store 12 14 44 4
042 load 14 12 0 4
044 lui 10 3342336
048 lui 20 536883200
04c andi 14 14 -385
050 store 12 14 0 4
052 load 14 12 0 4
054 andi 14 14 -385
058 ori 14 14 256
05c store 12 14 0 4
05e load 14 19 1424 4
062 load 11 14 8 4
064 or 11 11 10
066 store 14 11 8 4
068 addi 11 0 90
06c store 13 11 80 4
06e load 11 14 44 4
070 li 10 1
072 andi 11 11 -3
074 store 14 11 44 4
076 load 14 24 126 1
07a andi 11 14 127
07e load 14 12 0 4
080 andi 14 14 -128
084 or 14 14 11
086 store 12 14 0 4
088 load 14 13 4 4
08a lui 11 2181038080
08e addi 11 11 -1
090 andi 14 14 -2
092 store 13 14 4 4
094 load 14 24 104 1
098 andi 14 14 63
09c slli 13 14 25
0a0 load 14 12 44 4
0a2 and 14 14 11
0a4 or 14 14 13
0a6 store 12 14 44 4
0a8 load 14 24 140 4
0ac addi 11 0 35
0b0 store 12 14 8 4
0b2 load 14 24 144 4
0b6 store 12 14 4 4
0b8 addi 14 20 1300
0bc store 14 0 3 1
0c0 jal 1 278122
0c4 load 21 24 76 4
0c8 li 14 7
0ca store 24 14 16 1
0ce store 24 10 126 1
0d2 store 21 14 0 1
0d6 li 14 1
0d8 store 21 0 3 1
0dc store 21 14 2 1
0e0 load 14 24 84 4
0e4 addi 20 20 1300
0e8 andi 14 14 512
0ec beqz 14 290
"""
PATCHES={10: ('load', [13, 9, 1420, 4]), 18: ('load', [12, 18, 1368, 4]), 94: ('load', [14, 19, 1504, 4]), 184: ('addi', [14, 20, 1380]), 192: ('jal', [1, 278262]), 228: ('addi', [20, 20, 1380])}
TYPED=[(10, 2), (18, 2), (94, 2), (118, 4), (148, 4), (168, 2), (178, 2), (196, 2), (224, 2)]
STORES=[(2, 2, 9, 68, 4), (8, 2, 18, 64, 4), (22, 2, 1, 76, 4), (24, 2, 19, 60, 4), (26, 2, 20, 56, 4), (28, 2, 21, 52, 4), (30, 2, 24, 40, 4), (32, 2, 8, 72, 4), (34, 2, 22, 48, 4), (36, 2, 23, 44, 4), (38, 2, 25, 36, 4), (40, 2, 26, 32, 4), (42, 2, 27, 28, 4), (48, 13, 14, 100, 4), (64, 12, 14, 44, 4), (80, 12, 14, 0, 4), (92, 12, 14, 0, 4), (102, 14, 11, 8, 4), (108, 13, 11, 80, 4), (116, 14, 11, 44, 4), (134, 12, 14, 0, 4), (146, 13, 14, 4, 4), (166, 12, 14, 44, 4), (176, 12, 14, 8, 4), (182, 12, 14, 4, 4), (188, 14, 0, 3, 1), (202, 24, 14, 16, 1), (206, 24, 10, 126, 1), (210, 21, 14, 0, 1), (216, 21, 0, 3, 1), (220, 21, 14, 2, 1)]


def guard(raw,index):
 pc=STARTS[index];n=decode(raw,pc);spec={}
 for row in LITERALS.splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES:op,v=PATCHES[o]
  check(len(v)==len(FIELDS[op]),'setupentry literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'setupentry exactprefixboundaries')
 for a,f in spec.items():init.g(n,a,'setupentry '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNT,HASHES[index]),'setupentry identity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'setupentry typedload')
 return n


def prefix(raw,index):
 pc=STARTS[index];n=guard(raw,index);e={};calls=[];branches=[];frontier=set()
 for a,d in n.items():
  q=[a+d['size']]
  if d['op'] in BRANCHES:q.append(d['target']);branches.append(a-pc)
  elif d['op']=='jal':check(d['rd']==1,'setupentry linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  check(d['op'] not in ('jr','mret','ecall','csr','jump','jalr','call_indirect'),'setupentry noothertransfer');e[a]=q;frontier.update(z for z in q if z not in n)
 check(calls==[dict(offset=0xc0,target=0x43e6a+140*index)] and branches==[0xec] and frontier=={pc+0xee,pc+0x122},'setupentry exactcall/branch/frontiers')
 check(not any(d['op'] in BRANCHES|{'jal'} for a,d in n.items() if a<pc+0xc0),'setupentry beforefirstcall straightline')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES,'setupentry all31stores')
 check([(a-pc,d['imm']) for a,d in n.items() if d.get('rd')==2]==[(0,-80)],'setupentry frame80 remainsactive atfrontiers')
 frame={(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2};check(frame=={(1,76),(8,72),(9,68),(18,64),(19,60),(20,56),(21,52),(22,48),(23,44),(24,40),(25,36),(26,32),(27,28)},'setupentry RA and12Sregister saves')
 pn={a-pc:d for a,d in n.items()};check([o for o,d in pn.items() if d.get('rd')==24]==[0x38] and pn[0x38]['op']=='mv' and pn[0x38]['rs2']==10,'setupentry inputP capturedbeforeA0rewrite')
 reads=[(o,d['imm'],d['width']) for o,d in pn.items() if d['op']=='load' and d['rs1']==24]
 check(reads==[(0x76,126,1),(0x94,104,1),(0xa8,140,4),(0xb2,144,4),(0xc4,76,4),(0xe0,84,4)],'setupentry allinputP reads')
 check(pn[0xce]['rs1']==24 and pn[0xce]['rs2']==10 and pn[0xce]['imm']==126 and not any(d.get('rd')==10 for o,d in pn.items() if 0xc0<o<=0xce),'setupentry low8actualrangereply toP126')
 check(pn[0x70]['imm']==1 and pn[0xac]['imm']==35 and pn[0xc0]['target']==calls[0]['target'],'setupentry range1,35 encodedargs')
 check(pn[0xc4]['rd']==21 and [o for o,d in pn.items() if d.get('rd')==21]==[0xc4] and pn[0xc8]['imm']==7 and pn[0xd6]['imm']==1,'setupentry Qsource/headerliteraldefs')
 check(pn[0xe8]['imm']==512 and pn[0xec]['rs1']==14,'setupentry firstconditionalfreshP84bit9')
 chain=list(n);walks=[chain+[z] for z in sorted(frontier)]
 check(all(all(v in e[u] for u,v in zip(w,w[1:])) for w in walks) and {(u,v) for w in walks for u,v in zip(w,w[1:])}=={(u,v) for u,qs in e.items() for v in qs},'setupentry bothbounded exits coveralledges')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index],instructions=list(n.values()),selected_CFG=e,linked_calls=calls,outside_window_frontier=sorted(frontier),selected_syntactic_walks=[[a-pc for a in w] for w in walks],frame_bytes=80,frame_saves=sorted(frame),input_P_reads=reads,total_stores=31,precall_nonframe_store_count=13,postcall_nonframe_store_count=5,complete_function_claim=False,normal_RET_or_wholeframe_lifetime_proved=False)


def caller_join(data,mem,index):
 import check_v4160_b1_b120_target_static as caller
 pc=caller.STARTS[index];raw=init.binding.take(data,pc,1000);check(sparse.captured(mem,pc,1000)==raw,'setupentry callerfullstrictHEX');b=caller.body(raw,index);n={d['pc']:d for d in b['instructions']};e=b['CFG'];pred={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].append(a)
 hits=set();entry=False;seen=set();todo=pred[pc+0x306][:]
 while todo:
  a=todo.pop();d=n[a]
  if d.get('rd')==8:hits.add(a-pc);continue
  if a==pc:entry=True
  if a not in seen:seen.add(a);todo.extend(pred[a])
 check(hits=={0x18} and not entry,'setupentry callerS0 uniqueentryP reachingdef')
 init.g(n,pc+0x18,'setupentry caller capture',op='mv',rd=8,rs2=10)
 init.g(n,pc+0x306,'setupentry caller explicitarg',op='mv',rd=10,rs2=8)
 init.g(n,pc+0x308,'setupentry caller directtarget',op='jal',rd=1,target=STARTS[index])
 check(e[pc+0x306]==[pc+0x308],'setupentry caller nointermediateA0rewrite')
 return dict(start=pc,bytes=1000,sha256=b['sha256'],entry_P_capture=0x18,selected_A0_definition=0x306,selected_setup_call=0x308,S0_reaching_definitions=sorted(hits),callee_S0_SP_savedframe_preservation_and_normalreturn_required=True,actualsame_object_or_releasehistory_proved=False)


def reused_range(data,mem,index):
 import check_v4160_comparator_tail_static as comparator
 import check_v4160_range_retry_static as ranges
 pc=comparator.STARTS[index][1];raw=init.binding.take(data,pc,36);check(sparse.captured(mem,pc,36)==raw,'setupentry completebytehelper strictHEX');b=comparator.body(raw,'byte_range',index);cert=comparator.certificates(b,'byte_range');n={d['pc']-pc:d for d in b['instructions']}
 check(n[10]['target']==0x433a8+140*index and n[20]['op']=='mulhsu' and n[20]['rs1']==11 and n[28]['imm']==255,'setupentry exactsignedhigh/low8helper')
 sp=ranges.DETAILS[index][0][2];sr=init.binding.take(data,sp,108);check(sparse.captured(mem,sp,108)==sr,'setupentry sourcefullstrictHEX');source=ranges.body(sr,'source',index)
 return dict(byte_range=dict(start=pc,bytes=36,sha256=b['sha256'],certificate=cert),source=dict(start=sp,bytes=108,sha256=source['sha256'],nested_callback_target_still_fresh=True),new_argument_domain=[1,35],normal_reply_interval=[1,34],closed_formula='low8(1+floor(34*U32[source_reply]/2^32))',full_nestedcall_termination_or_actualrandom_distribution_proved=False,callee_saved_S8_and_source_frame_preservation_required=True)


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,SIZE);check(sparse.captured(mem,pc,SIZE)==raw,'setupentry strictHEX');b=prefix(raw,index);n={d['pc']-pc:d for d in b['instructions']};G=0x20003000;delta=80*index
 check(n[4]['imm']+n[0xa]['imm']==G+1340+delta and n[0xe]['imm']+n[0x12]['imm']==G+1288+delta and n[0x34]['imm']+n[0x5e]['imm']==G+1424+delta and n[0x48]['imm']+n[0xb8]['imm']==G+1300+delta,'setupentry fixedT/R/U/Hcells')
 check(n[0x3a]['imm']==-4 and n[0x3c]['imm']==1 and n[0x4c]['imm']==n[0x54]['imm']==-385 and n[0x58]['imm']==256,'setupentry R44lowbits andseparateR0snapshots')
 check(n[0x44]['imm']==0x330000 and n[0x64]['op']=='or' and n[0x72]['imm']==-3 and n[0x90]['imm']==-2,'setupentry U8/U44/T4 masks')
 check(n[0x7a]['imm']==127 and n[0x80]['imm']==-128 and n[0x98]['imm']==63 and n[0x9c]['imm']==25 and ((n[0x8a]['imm']+n[0x8e]['imm'])&0xffffffff)==0x81ffffff,'setupentry P126low7/P104sixbit fieldmask')
 bbraw=init.binding.take(data,previous.SOURCES[index],244);check(sparse.captured(mem,previous.SOURCES[index],244)==bbraw,'setupentry BBfullstrictHEX');bb=previous.body(bbraw,index);bn={d['pc']-bb['start']:d for d in bb['instructions']}
 check(bn[4]['imm']==n[0x12]['imm'] and bn[0x5e]['imm']==n[0xa]['imm'] and bn[0x2a]['imm']==n[0xb8]['imm'],'setupentry sameBB R/Tslots andHbase notsame freshpointee')
 # Only compare fixed cells. Loaded T/R/U pointees and object/frame addresses
 # are not assumed distinct, equal, live or stable across these operations.
 return dict(label=init.binding.PROFILES[index][0],bounded_prefix=b,caller=caller_join(data,mem,index),range_call=reused_range(data,mem,index),reused_BB=dict(start=bb['start'],source=bb['source'],bytes=244,sha256=bb['sha256']),cells=dict(T=G+1340+delta,R=G+1288+delta,U=G+1424+delta,H=G+1300+delta),
  contracts=['entryP heldS8 before A0rewrite;first192B straightline/no calls;capturefreshT/R/U fromfixedcells withoutnonnullguards;no directentryP pointerstore beforefirstcall,not an alias/wholechainnonretentionproof',
   'precall ordered stores:T100=160;R44=(fresh&~3)|1;R0=fresh&~180hex;R0=(anotherfresh&~180hex)|100hex;U8word=fresh|330000hex;T80=90;U44=fresh&~2;R0=(fresh&~127)|(freshP126&127);T4=fresh&~1;R44=(fresh&81ffffffhex)|((freshP104&63)<<25);R8=freshP140;R4=freshP144;H3=0',
   'firstcall43e6a/43ef6 getsA0=1,A1=35;matchingnormalbytehelper returns1..34 regardlessU32sourcereply;no distribution/reachability/termination proof;S8/sourceframesmustsurvive nestedcallback',
   'aftercall freshQ=U32P76;P16=7;P126=low8actualreply;Q0=7;Q3=0;Q2=1;noQnullguard/release/copy/lengthcheck. ValidP148B/Q4B andaliasstability remainpremises',
   'R low7 hasalreadycaptured previousfreshP126 beforelaterP126replacement;no automaticpostcall R0/P126 equality. R/T slotsharing andHbase match BB,notstablepointees norphysicalsetup-vsIRQorder',
   'endsatfirstconditional freshP84bit9;frontiers+ee/+122 with80Bframestillactive. No wholefunctionreturn/framebalance/nextcases/payloadlifetime claim'],
  actual_binding_physical_effects_pointer_identity_retention_and_complete_return_flow_proved=False)


def domains():
 M=1<<32;samples=0
 for high in range(65536):
  for low in (0,65535):
   r=(high<<16)|low;q=(34*r)>>32;check(0<=q<=33 and 1<=1+q<=34 and ((1+q)&255)==1+q,'setupentry closedrange1..34');samples+=1
 check(34*(M-1)<34*M and (34*(M-1))//M==33 and 34*0//M==0,'setupentry monotoneclosedbound endpoints')
 for byte in range(256):
  check(0<=byte&127<=127 and 0<=byte&63<=63 and ((byte&63)<<25)&0x81ffffff==0,'setupentry disjointR44field bits')
 return dict(new_range_argument_domain=[1,35],coefficient=34,source_U32_family_cases=samples,source_samples='all65536 high16 words with low16=0/65535;notallU32',normal_reply_closed_bound=[1,34],all_U8_field_cases=256,range_distribution_reachability_or_physical_state_proved=False,closed_host_scalar_identities_only=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-bounded-setup-entry-register-field-and-range-call-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_bounded_prefix_bytes=476,new_bounded_prefix_instructions=166,new_complete_body_bytes=0,new_complete_body_instructions=0,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['setup+ee/+122 optionalbranches andfullreturn/sideeffects','P76/Qallocation/extent/aliasing andsourcefieldstability','actualrange/clock binding andnestedcallbackpreservation','realR/T/U pointers/IRQorder andfullobjectconsumption-release lifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);n=guard(raw,i)
  for d in n.values():
   o=d['pc']-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('setupentry instructionmutation escaped')
   mutated+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('setupentry typedmutation escaped')
   typed+=1
 check((mutated,typed)==(166,18),'setupentry mutationcensus')
 print('PASS:166 instruction/18 typed-load mutations rejected;bounded setup entry')


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
 else:check(OUT.read_bytes()==encoded,'setupentry exactledger replay')
 print('PASS:476B/166i bounded setup prefix;strictHEX;callerP/range1..34/BB sharedslot joins;exactledger')
 print('PASS:NO target execution/emulation;fullsetupreturn/binding/IRQorder/aliasing/lifetimes UNPROVED')


if __name__=='__main__':main()
