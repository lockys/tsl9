"""Offline mapped admission sampler: original operands/CFG and host scalar algebra.
No target execution/emulation, clock/timer/provider or mutable state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_attempt_static as previous
import check_v4160_constructor_publication_chain_static as publication
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-sampler-static.json')
STARTS=(0x20002d4c,0x20002d98)
SOURCES=(0x42fbc,0x43048)
SIZE=166
HASHES=('5ab9e314b76791668901accd23c3269f41fe71704630ec53410a908e400d1bb5', '10dad8c41c2f835c22e5737d6d9a0c59c5d76da5e895bd8843230180fbdd6d39')
COUNTS=(56, 56)
TYPED=(((4, 2), (86, 4), (90, 2), (94, 2), (154, 2)), ((4, 2), (86, 4), (90, 2), (94, 2), (154, 2)))
QK=(((58, 'bc2f', 'qk.c.lbu'),), ((58, 'bc2f', 'qk.c.lbu'),))
LITERALS=(
'''
000 lui 15 536883200
004 load 15 15 480 4
008 addi 2 2 -32
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 20 8 4
010 store 2 1 28 4
012 store 2 18 16 4
014 store 2 19 12 4
016 call_indirect 1 15
018 lui 9 536883200
01c addi 15 9 1376
020 load 8 15 8 4
022 li 20 0
024 beq 8 10 132
028 addi 9 9 1376
02c bltu 10 8 150
030 sub 10 10 8
032 lui 14 536883200
036 addi 15 14 1344
03a load 15 15 26 1
03c srli 8 10 5
040 andi 20 10 31
044 addi 18 14 1344
048 bltu 8 15 126
04c lui 19 536883200
050 addi 19 19 564
054 jal 1 536882256
056 load 13 18 26 1
05a load 16 9 8 4
05e load 11 19 4 4
062 slli 14 13 5
066 add 14 14 16
068 sub 8 8 13
06a mv 12 14
06c bltu 14 16 116
070 bltu 14 11 120
074 sub 12 14 11
078 store 9 12 8 4
07a bgeu 8 13 84
07e slli 8 8 5
080 or 20 8 20
084 load 1 2 28 4
086 load 8 2 24 4
088 mv 10 20
08a load 9 2 20 4
08c load 18 2 16 4
08e load 19 2 12 4
090 load 20 2 8 4
092 addi 2 2 32
094 jr 1
096 lui 15 536883200
09a load 15 15 568 4
09e sub 8 15 8
0a2 add 10 10 8
0a4 jump 50
''',
'''
000 lui 15 536883200
004 load 15 15 560 4
008 addi 2 2 -32
00a store 2 8 24 4
00c store 2 9 20 4
00e store 2 20 8 4
010 store 2 1 28 4
012 store 2 18 16 4
014 store 2 19 12 4
016 call_indirect 1 15
018 lui 9 536883200
01c addi 15 9 1456
020 load 8 15 8 4
022 li 20 0
024 beq 8 10 132
028 addi 9 9 1456
02c bltu 10 8 150
030 sub 10 10 8
032 lui 14 536883200
036 addi 15 14 1424
03a load 15 15 26 1
03c srli 8 10 5
040 andi 20 10 31
044 addi 18 14 1424
048 bltu 8 15 126
04c lui 19 536883200
050 addi 19 19 644
054 jal 1 536882332
056 load 13 18 26 1
05a load 16 9 8 4
05e load 11 19 4 4
062 slli 14 13 5
066 add 14 14 16
068 sub 8 8 13
06a mv 12 14
06c bltu 14 16 116
070 bltu 14 11 120
074 sub 12 14 11
078 store 9 12 8 4
07a bgeu 8 13 84
07e slli 8 8 5
080 or 20 8 20
084 load 1 2 28 4
086 load 8 2 24 4
088 mv 10 20
08a load 9 2 20 4
08c load 18 2 16 4
08e load 19 2 12 4
090 load 20 2 8 4
092 addi 2 2 32
094 jr 1
096 lui 15 536883200
09a load 15 15 648 4
09e sub 8 15 8
0a2 add 10 10 8
0a4 jump 50
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'sampler literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'sampler fullboundaries')
 for a,f in s.items():init.g(n,a,'sampler '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'sampler typedload')
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'sampler QK raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'sampler fullidentity')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'sampler RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'sampler linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'sampler indirectlink');calls.append(dict(offset=a-pc,target='freshclockslot;no nullguard'))
  check(all(z in n for z in q),'sampler closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 cut={a:[z for z in qs if (a-pc,z-pc)!=(0x7a,0x54)] for a,qs in e.items()}
 check(seen==set(n) and not common.acyclic(e) and common.acyclic(cut) and rets==[pc+0x94],'sampler completeCFG/onecyclecut/soleRET')
 check(calls==[dict(offset=0x16,target='freshclockslot;no nullguard'),dict(offset=0x54,target=0x20002c50+76*index)],'sampler bothcalltargets')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==[(0xa,2,8,24,4),(0xc,2,9,20,4),(0xe,2,20,8,4),(0x10,2,1,28,4),(0x12,2,18,16,4),(0x14,2,19,12,4),(0x78,9,12,8,4)],'sampler sixframesaves/one nonframestore')
 check([a-pc for a,d in n.items() if d.get('rd')==8]==[0x20,0x3c,0x68,0x7e,0x86,0x9e] and [a-pc for a,d in n.items() if d.get('rd')==20]==[0x22,0x40,0x80,0x90],'sampler q/r encodeddefinitions')
 return dict(start=pc,source=SOURCES[index],bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,returns=rets,tails=[],stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 base={0x24:0x28,0x2c:0x30,0x48:0x4c,0x6c:0x70,0x70:0x78,0x7a:0x7e}
 choices={'clock_equals_baseline':{0x24:0x84},'direct_delta_skiploop':{**base,0x48:0x7e},'wrapped_delta_skiploop':{**base,0x2c:0x96,0x48:0x7e},
  'one_iteration_no_modulus_sub':base,'one_iteration_add_wrapped':{**base,0x6c:0x74},'one_iteration_v_ge_modulus':{**base,0x70:0x74}}
 out={name:common.walk(b,c) for name,c in choices.items()}
 for name,seq in out.items():
  check(seq[-1]==0x94 and seq.index(0x16)<seq.index(0x20),'sampler clockbeforebaseline')
  check((0x78 in seq)==name.startswith('one_iteration'),'sampler branchstore witnesses')
  if 'skiploop' in name:check(0x54 not in seq and 0x7e in seq and 0x80 in seq,'sampler no loopcall onskip')
 check(0x3a not in out['clock_equals_baseline'] and 0x9a not in out['clock_equals_baseline'],'sampler equalityskip threshold/modulus')
 return out


def domains():
 mask=0xffffffff;cases=0
 for k in range(1,256):
  for d in range(65536):
   q,r=d>>5,d&31;count=q//k;rem=q%k
   check(q==count*k+rem and 0<=rem<k and ((rem<<5)|r)==d%(32*k),'sampler stablepositiveK quotient/remainder certificate')
   cases+=1
  check((0xffffffff>>5)//k<=134217727 and 32*k-16>=16,'sampler stableK loopbound/admissionnonempty')
 check(cases==16711680 and (0xffffffff>>5)==134217727,'sampler finitehostdomain census')
 # Zero K cannot decrease q; this is algebra, not iteration of target state.
 for q in (0,1,255,134217727):check(q-0==q and q>=0,'sampler constantzero subtraction/backedge')
 for old in (0,1,0xffffe020,0xfffffff0,0xffffffff):
  for k in (0,1,127,255):
   v=(old+32*k)&mask
   for m in (0,1,32,8160,0xffffffff):
    subtract=v<old or v>=m;value=(v-m)&mask if subtract else v
    check(value==((v-m)%2**32 if subtract else v),'sampler singleconditional subtraction')
 check(((0+32*255)&mask)-1>1,'sampler single subtraction notgeneral modulo witness')
 return dict(stable_positive_K_cases=cases,stable_positive_K_domain='K1..255,D0..65535;algebra extends to allU32 D',
  conditional_formula='if initial andallperiterationKstablepositive,allcallees return/preserveq/r:reply=D%(32*K),loopcalls=floor((D>>5)/K)<=134217727',
  constant_K0_non_equal_clock='qneverdecreases andunsignedbackedgealways true undernormalcallee/preservation;no ordinaryreturn proved;equalclock stillreturns0',
  changing_K='initial vsfreshloopK maydiffer;largerfreshK canunderflowq;no unconditional range/progress/bound claim',
  loop_baseline_write='v=low32(freshold+32*freshK);ifv<old orv>=freshM ->low32(v-M),elsev;one subtraction,notgenericmodM',target_execution_or_emulation=False)


def clock_provenance(image,data,mem,index):
 gates=publication.gates;pc,size,*_=gates.DETAILS[index];raw=init.binding.take(data,pc,size)
 check(sparse.captured(mem,pc,size)==raw,'sampler fullconfig writer strictHEX');writer=gates.body(raw,index);_,a=gates.specs(pc,index)
 n={d['pc']:d for d in writer['instructions']};clockslot=0x200031e0+80*index;copied=0x20003234+80*index
 check(int(writer['service_word'],16)==clockslot and int(writer['copied_config'],16)==copied and n[a(92)]['imm']+0x20003000==copied and n[a(100)]['imm']+0x20003000==clockslot,'sampler clockwriter exactcells')
 constructor=publication.app.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct');cn={d['pc']:d for d in constructor['instructions']}
 check((0x19bba+cn[0x19bba]['imm']+cn[0x19bbe]['imm'])&0xffffffff==0x191c6 and cn[0x19bc2]['op']=='store' and cn[0x19bc2]['imm']==0 and cn[0x19bca]['rs2']==2,'sampler constructor codeword/framearg source')
 check(init.binding.word(data,0x40074)==pc and sparse.captured(mem,0x40074,4)==init.binding.take(data,0x40074,4),'sampler rawconfigAPIcandidate')
 service=publication.mode.service;reader=service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,service.APP_HASHES[1]);rn={d['pc']:d for d in reader['instructions']}
 check(not reader['calls'] and not any(d['op']=='store' for d in rn.values()),'sampler APPreader no calls/stores')
 check([(p,d['target']) for p,d in rn.items() if d['op']=='bne']==[(0x191d6,0x191ca),(0x191ea,0x191de),(0x191fe,0x191f2),(0x19216,0x1920a)],'sampler APPreader fourretryedges')
 return dict(reused_writer=writer,reused_constructor=constructor,reused_reader=reader,writer_paths=[publication.path(writer,index,h,z) for h in (False,True) for z in (False,True)],
  conditional_codeword=0x191c6,clockslot=clockslot,copied_config=copied,
  contract=['APPconstructor emitscode191c6 inframeword0,A0=frame to fresh40074;candidateAPI->fullwriter;acceptednonnullconfig gates ->copy16 ->freshcopiedword0 ->SWclockslot',
   'no directentryA0storetoslot;optionalhooks/source/copy/return/preservation premises required;othernonzerohooks remainunclosed;nullconfig/default path hasdifferentcodeword',
   'underpreservedsource/copiedword,slot mayequal191c6. Actualexecution/order/laterwriters/installedidentity notproved;sampler andattempt eachreadfreshsamecell,notnecessarilysamepointer',
   'matchedAPPreader pairsfreshhighhalfwords40002818,low4000281c untilpairwiseequal;H1==H2 ->(H2<<16)|L1,else(H2<<16)|L2 afteranotherlowpair;no finalhighrecheck/coherentatomicclock/progressproof'],
  actual_installed_clock_binding_or_counter_semantics_proved=False)


def profile(image,data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,SOURCES[index],SIZE)
 check(sparse.captured(mem,SOURCES[index],SIZE)==raw,'sampler strictoriginalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;C=G+1376+80*index;F=G+1344+80*index;slot=G+480+80*index;M=G+568+80*index
 check(n[0]['imm']+n[4]['imm']==slot and n[0x18]['imm']+n[0x1c]['imm']==C and n[0x18]['imm']+n[0x28]['imm']==C and n[0x32]['imm']+n[0x36]['imm']==F and n[0x96]['imm']+n[0x9a]['imm']==M and n[0x4c]['imm']+n[0x50]['imm']+4==M,'sampler global sourcejoins')
 check(n[0x3c]['imm']==n[0x62]['imm']==n[0x7e]['imm']==5 and n[0x40]['imm']==31 and n[0x3a]['imm']==n[0x56]['imm']==26,'sampler quotient/remainder/threshold operands')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];pc=STARTS[index]
 check(int(first['source'],16)+pc-int(first['destination'],16)==SOURCES[index] and int(first['destination'],16)<=pc and pc+SIZE<=int(mapping['first_copy_end_exclusive'],16),'sampler full affinecopysource')
 attempt=previous.body(init.binding.take(data,previous.STARTS[index],502),index)
 check(sparse.captured(mem,previous.STARTS[index],502)==init.binding.take(data,previous.STARTS[index],502) and attempt['calls'][0]['target']==pc,'sampler fullattempt originaljoin')
 an={d['pc']-attempt['start']:d for d in attempt['instructions']};check(an[0x120]['imm']+an[0x124]['imm']==slot,'sampler andattempt sameclockslotcell')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),RAM_mapping=dict(source=SOURCES[index],entry=pc,bytes=SIZE,candidate_first_copy=first,actual_copy_proved=False),
  reused_attempt=dict(start=attempt['start'],bytes=502,new_code_bytes_counted=0),clock_provenance=clock_provenance(image,data,mem,index),
  contract=['freshclockfunctionword beforeframe;32Bframe sixsavedwords;indirectclockcall no localnullguard/explicitA0-A2setup;freshC8 baseline AFTER call',
   'T==B ->return0 withoutthreshold/modulusread;elseT>B ->D=T-B;T<B ->D=low32(T+freshM-B),no+1. q=D>>5,r=D&31;initialfreshF26 k0,ifq<k0 returnsD',
   'otherwiseeachiteration linkedRAM20002c50/20002c9c(),thenfreshK=U8F26,freshold=U32C8,freshM;v=low32(old+32*K);ifv<old orv>=M subtractMonce;SWtoC8;qlow32(q-K);unsignedq>=justsampledK repeats',
   'ordinaryexit returnslow32((q<<5)|originalr). Initialk0 andlaterK snapshots distinct;freshK>qmayunderflow;K0doesnotdecreaseq. Not RNG/timeunits/terminationguarantee',
   'underseparateconstantpositiveK andnormalcallee/preservation premises:reply=D%(32*K);outerattempt readslaterF26 again andaccepts16..32*K-16 onlyifalsosameK. Neverassumethatstability'],
  premises='candidateISA/API/firstcopy/installedcode;validcode/frame/globalextents;normalcalleeS/SP/RA/framepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalityseparate',
  actual_clock_provider_binding_progress_physical_effects_or_full_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-mapped-sampler-clock-provenance-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=332,complete_phase_body_instructions=112,reused_attempt_bytes=1004,reused_writer_bytes=448,reused_APP_constructor_reader_bytes=216,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['RAM20002c50/20002c9c loopcallee effects andbaselinewriters','6434a/64434,63b0e/63bf8 andcallback65de6/65ed0','actualinstalledclock/provideridentity,writerorder,allpollprogress andfullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('sampler instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('sampler typedmutation escaped')
   typed+=1
 check((mutations,typed)==(112,10),'sampler mutationcensus')
 print('PASS:112 instruction/10 typed-load mutations rejected;complete CFG/frame/call/store andclock-writer certificates')


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
 else:check(OUT.read_bytes()==encoded,'sampler exactledger replay')
 print('PASS:332B/112i mappedsampler;strictHEX;16711680 hostremainder cases;APPconstructor/configwriter/reader joins;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/clocksemantics/pollprogress/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
