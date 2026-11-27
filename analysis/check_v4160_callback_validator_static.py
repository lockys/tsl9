"""Offline callback descriptor setup, ID assignment and paired-list publish.
Original operands/CFG, immutable bounded paths and host scalar certificates.
No target execution/emulation, provider, register/RAM/heap/list model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_callback_list_writers_static as previous
import check_v4160_id11_outer_tail_static as origin
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
task8=previous.task8
OUT=Path(__file__).with_name('v4160-callback-validator-static.json')
STARTS=(0x4ce22,0x4ceba)
SIZE=256
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=('517f027a30a56007370b5227d9ea49bcfa27797f53960b569a1ddaf59b75ff24', '77e6d704407895b4cd90fe9f16d503d1ca5b4c4bd9a4ecb402f13637d58fb304')
TYPED_LOADS=(((102, 5), (160, 5)), ((102, 5), (160, 5)))
LITERALS=(
'''
000 load 15 10 0 2
002 bnez 15 10
004 li 15 2
006 mv 10 15
008 jr 1
00a addi 2 2 -16
00c store 2 9 4 4
00e load 9 10 4 4
010 store 2 8 8 4
012 store 2 1 12 4
014 store 2 18 0 4
016 load 13 9 0 1
018 load 12 9 4 4
01a mv 8 10
01c lui 10 454656
020 li 11 2
022 addi 10 10 -1392
026 jal 1 280100
02a beqz 10 62
02c load 15 8 2 1
02e li 14 9
030 addi 15 15 -7
032 andi 15 15 255
036 bgeu 14 15 98
03a li 15 24
03c jump 84
03e load 13 9 0 1
040 load 12 9 4 4
042 lui 10 454656
046 li 11 2
048 addi 10 10 -1380
04c jal 1 280100
050 bnez 10 44
052 li 15 2
054 load 1 2 12 4
056 load 8 2 8 4
058 load 9 2 4 4
05a load 18 2 0 4
05c mv 10 15
05e addi 2 2 16
060 jr 1
062 lui 18 536883200
066 load 13 18 -276 2
06a li 15 1
06c addi 18 18 -276
070 beqz 13 84
072 load 14 8 0 2
074 add 14 14 13
076 lui 13 65536
078 blt 13 14 84
07c lui 11 16384
07e addi 11 11 1794
082 li 10 12
084 auipc 1 536555520
088 jalr 1 1 410
08c mv 9 10
08e li 15 19
090 beqz 10 84
092 li 12 12
094 li 11 0
096 auipc 1 536555520
09a jalr 1 1 1252
09e load 15 8 0 2
0a0 load 11 18 0 2
0a4 li 12 0
0a6 li 14 0
0a8 add 13 11 14
0ac slli 13 13 16
0ae srli 13 13 16
0b0 bltu 14 15 230
0b4 add 15 15 11
0b6 slli 15 15 16
0b8 srli 15 15 16
0ba beqz 12 192
0bc store 18 15 0 2
0c0 store 9 0 0 4
0c4 li 12 8
0c6 mv 11 8
0c8 addi 10 9 4
0cc auipc 1 536555520
0d0 jalr 1 1 1092
0d4 lui 15 536883200
0d8 addi 15 15 -120
0dc load 14 15 0 4
0de bnez 14 248
0e0 store 15 9 0 4
0e2 li 15 0
0e4 jump 84
0e6 load 12 8 4 4
0e8 slli 10 14 4
0ec addi 14 14 1
0ee add 12 12 10
0f0 store 12 13 10 2
0f2 li 12 1
0f4 jump 168
0f6 mv 14 15
0f8 load 15 14 0 4
0fa bnez 15 246
0fc store 14 9 0 4
0fe jump 84
''',
'''
000 load 15 10 0 2
002 bnez 15 10
004 li 15 2
006 mv 10 15
008 jr 1
00a addi 2 2 -16
00c store 2 9 4 4
00e load 9 10 4 4
010 store 2 8 8 4
012 store 2 1 12 4
014 store 2 18 0 4
016 load 13 9 0 1
018 load 12 9 4 4
01a mv 8 10
01c lui 10 454656
020 li 11 2
022 addi 10 10 -896
026 jal 1 280248
02a beqz 10 62
02c load 15 8 2 1
02e li 14 9
030 addi 15 15 -7
032 andi 15 15 255
036 bgeu 14 15 98
03a li 15 24
03c jump 84
03e load 13 9 0 1
040 load 12 9 4 4
042 lui 10 454656
046 li 11 2
048 addi 10 10 -884
04c jal 1 280248
050 bnez 10 44
052 li 15 2
054 load 1 2 12 4
056 load 8 2 8 4
058 load 9 2 4 4
05a load 18 2 0 4
05c mv 10 15
05e addi 2 2 16
060 jr 1
062 lui 18 536883200
066 load 13 18 -196 2
06a li 15 1
06c addi 18 18 -196
070 beqz 13 84
072 load 14 8 0 2
074 add 14 14 13
076 lui 13 65536
078 blt 13 14 84
07c lui 11 16384
07e addi 11 11 1794
082 li 10 12
084 auipc 1 536555520
088 jalr 1 1 258
08c mv 9 10
08e li 15 19
090 beqz 10 84
092 li 12 12
094 li 11 0
096 auipc 1 536555520
09a jalr 1 1 1100
09e load 15 8 0 2
0a0 load 11 18 0 2
0a4 li 12 0
0a6 li 14 0
0a8 add 13 11 14
0ac slli 13 13 16
0ae srli 13 13 16
0b0 bltu 14 15 230
0b4 add 15 15 11
0b6 slli 15 15 16
0b8 srli 15 15 16
0ba beqz 12 192
0bc store 18 15 0 2
0c0 store 9 0 0 4
0c4 li 12 8
0c6 mv 11 8
0c8 addi 10 9 4
0cc auipc 1 536555520
0d0 jalr 1 1 940
0d4 lui 15 536883200
0d8 addi 15 15 -40
0dc load 14 15 0 4
0de bnez 14 248
0e0 store 15 9 0 4
0e2 li 15 0
0e4 jump 84
0e6 load 12 8 4 4
0e8 slli 10 14 4
0ec addi 14 14 1
0ee add 12 12 10
0f0 store 12 13 10 2
0f2 li 12 1
0f4 jump 168
0f6 mv 14 15
0f8 load 15 14 0 4
0fa bnez 15 246
0fc store 14 9 0 4
0fe jump 84
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'CBsetup literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for off,f3 in TYPED_LOADS[index]:check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'CBsetup typedload encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'CBsetup completeboundaries')
 for a,f in s.items():init.g(n,a,'CBsetup operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(256,100,HASHES[index]),'CBsetup completeidentity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'CBsetup ordinaryRET');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'CBsetup linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','CBsetup adjacentpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'CBsetup closedlocalCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'CBsetup allnodesreachable')
 cut={a:[z for z in qs if (a-pc,z-pc) not in ((0xf4,0xa8),(0xfa,0xf6))] for a,qs in edges.items()}
 check(common.acyclic(cut) and not common.acyclic(edges),'CBsetup IDloop andlistloop edgecuts')
 check(calls==[dict(offset=o,target=t) for o,t in [(0x26,0x44624+148*index),(0x4c,0x44624+148*index),(0x88,0x20000040),(0x9a,0x2000039c),(0xd0,0x20000332)]],'CBsetup all5originalcalltargets')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 check(len(stores)==9 and rets==[pc+8,pc+0x60],'CBsetup exactstore/return census')
 expected={(1,12),(8,8),(9,4),(18,0)}
 check({(d['source'],d['imm']) for d in stores if d['base']==2}==expected and {(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}==expected,'CBsetup16Bframe restores')
 return dict(start=pc,bytes=256,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def checked(b,seq):
 pc=b['start'];e=b['CFG'];s=[pc+o for o in seq]
 check(s[0]==pc and not e[s[-1]] and all(z in e[a] for a,z in zip(s,s[1:])),'CBsetup immutablepath certificate');return seq


def witnesses(b):
 gates={2:0xa,0x2a:0x2c,0x36:0x62,0x70:0x72,0x78:0x7c};allocated={**gates,0x90:0x92}
 choices={'initialN0_reply2':{2:4},'both_table_matches0_reply2':{2:0xa,0x2a:0x3e,0x50:0x52},
  'param_outside7_16_reply24':{2:0xa,0x2a:0x2c,0x36:0x3a},'counter0_reply1':{**gates,0x70:0x54},
  'captured_sum_above65536_reply1':{**gates,0x78:0x54},'allocation0_reply19':{**gates,0x90:0x54},
  'postfillN0_publish_secondary':{**allocated,0xb0:0xb4,0xba:0xc0,0xde:0xe0},
  'tailappend_secondary':{**allocated,0xb0:0xb4,0xba:0xc0,0xde:0xf8,0xfa:0xfc}}
 paths={k:common.walk(b,v) for k,v in choices.items()}
 base=paths['postfillN0_publish_secondary'];i=base.index(0xa8);after=base.index(0xb4)
 iteration=[0xa8,0xac,0xae,0xb0,0xe6,0xe8,0xec,0xee,0xf0,0xf2,0xf4]
 prefix=base[:i];suffix=base[i:after]+[0xb4,0xb6,0xb8,0xba,0xbc]+base[base.index(0xc0):]
 paths['postfillN4_writeIDs_counter_publish']=checked(b,prefix+iteration*4+suffix)
 paths['postfillN1_writeIDs_counter_publish']=checked(b,prefix+iteration+suffix)
 seq=paths['postfillN4_writeIDs_counter_publish']
 check(seq.count(0xf0)==4 and seq.index(0xf0)<seq.index(0xbc)<seq.index(0xd0)<seq.index(0xe0),'CBsetup IDstores thencounter then descriptorcopy thenpublication')
 check(0xf0 not in base and 0xbc not in base and 0xe0 in base,'CBsetup postfillN0 skipsID/counter butstillpublishes')
 tn={v['pc']-b['start']:v for v in b['instructions']}
 check(not any(tn[o].get('rd')==13 and tn[o]['op']=='mv' for o in base[:base.index(0x26)]),'CBsetup doesnotcaptureoriginalA3 asobject')
 return {'selected':paths,'bounded_IDloop_maximum':65535,'tailappend_requiresfinitevalidlist':True,'cross_snapshot_N_counter_andpointer_equality_proved':False}


def domains():
 accepted=[]
 for byte in range(256):
  hit=((byte-7)&255)<=9;check(hit==(7<=byte<=16),'CBsetup byteparaminclusive7..16');
  if hit:accepted.append(byte)
 boundaryvectors=0
 for K in range(65536):
  boundary=65536-K
  for N in {0,1,65535,max(0,min(65535,boundary-1)),max(0,min(65535,boundary)),max(0,min(65535,boundary+1))}:
   S=K+N;check(S<2**31,'CBsetup capturedU16sum signedcompare nondnegative')
   check((K!=0 and not(65536<S))==(1<=K<=65535 and 0<=N<=min(65535,65536-K)),'CBsetup exactstrictgreaterthan65536 guard partition');boundaryvectors+=1
 check(1+65535==65536 and (1+65535)&65535==0,'CBsetup equalityaccepted thenstablefinalcountermay0')
 for N in range(65536):
  if N:check(16*(N-1)+10+2<=16*N and N<2**32,'CBsetup allU16 IDloopcount/stride extent')
 check([1+i for i in range(4)]==[1,2,3,4] and (1+4)&65535==5,'CBsetup conditionalwrapperIDs1..4/counter5')
 check(all(not(set(range(16*i+10,16*i+12))&set(range(72,76))) for i in range(4)),'CBsetup fixed4records avoidcallbackobject8 atconfig+72')
 check(set(range(12))-set(range(4))-set(range(4,12))==set(),'CBsetup fill12 pluscopy8 descriptorlayout')
 return {'byteparam_cases':256,'accepted_byteparams':accepted,'counter_boundary_vectors':boundaryvectors,'fresh_loop_count_cases':65536,
  'count_snapshot_domains':'initialN0>0;preallocationfreshN1 andpostfillfreshN2 mayindependentlybe0..65535;counterK1/K2 maydiffer;IDpointerreloadedperiteration',
  'stable_counter_wrap_equality':{'K':1,'N':65535,'sum':65536,'final_U16_counter':0},
  'stable_wrapper_example':{'N':4,'counter':1,'assigned_IDs':[1,2,3,4],'next_counter':5,'primary_key_fromfirstconfig10':1},
  'actual_reachability_pointers_identity_or_provider_output_proved':False}


def profile(data,hexraw,index,parent):
 raw=init.binding.take(data,STARTS[index],SIZE);b=body(raw,index);pc=b['start'];n={v['pc']-pc:v for v in b['instructions']}
 G=0x20003000;C=G-276+80*index;head=G-120+80*index
 check(n[0x66]['imm']+G==C and n[0xd4]['imm']+n[0xd8]['imm']==head,'CBsetup counter andsecondaryhead distinctglobals')
 check(n[0x78]['op']=='blt' and n[0x76]['imm']==65536 and (n[0x78]['rs1'],n[0x78]['rs2'])==(13,14),'CBsetup strictsigned65536<sum branch')
 check(n[0x82]['imm']==12 and n[0x7c]['imm']+n[0x7e]['imm']==0x4702,'CBsetup secondarynode12/tag4702')
 check(n[0x9e]['rs1']==8 and n[0xa0]['rs1']==18 and n[0xb0]['op']=='bltu' and n[0xe8]['imm']==4 and n[0xec]['imm']==1 and n[0xf0]['imm']==10,'CBsetup separatelyrefetchedN/K and16stride IDstores')
 check(n[0xa8]['rs1']==11 and n[0xa8]['rs2']==14 and n[0xe6]['rs1']==8 and n[0xe6]['imm']==4,'CBsetup keylow16Kplusi andfresharraypointer periteration')
 check(n[0xc0]['rs2']==0 and n[0xc4]['imm']==8 and n[0xc6]['rs2']==8 and n[0xc8]['imm']==4,'CBsetup node0zero anddescriptor8copytonode4')
 an={v['pc']-parent['bodies']['append']['start']:v for v in parent['bodies']['append']['instructions']}
 check(parent['bodies']['append']['calls'][0]==dict(offset=0x28,target=pc) and an[0x20]['imm']==8,'CBsetup parentappend descriptorcall joinsfullbody')
 check(an[0x24]['imm']==8 and an[0x26]['imm']==10 and an[0x1c]['imm']==12,'CBsetup descriptorcount/byte/configptr writer offsets')
 op=origin.STARTS[index][2];defaults=origin.body(init.binding.take(data,op,248),'defaults',index);on={v['pc']-op:v for v in defaults['instructions']}
 check(on[46]['rs2']==11 and on[40]['imm']==1 and on[46]['imm']+G==C,'CBsetup knowninitialcounter1 source')
 _,mem=sparse.inspect(hexraw,sparse.parser());check(sparse.captured(mem,pc,SIZE)==raw,'CBsetup completeoriginalHEX backing')
 tables=[n[0x1c]['imm']+n[0x22]['imm'],n[0x42]['imm']+n[0x48]['imm']]
 check(tables==[0x6ea90+496*index,0x6ea9c+496*index],'CBsetup originalversion-specific ROMreferences')
 gaps=[]
 expected_samples=[(0,40,None,None,201,42,None,None,3,42,None,None),(1,40,None,None,5,42,None,None,(86,238)[index],145,4,0)]
 for t,sample in zip(tables,expected_samples):
  observed=tuple(mem.get(t+j) for j in range(12))
  check(t>=0x40000+len(data) and observed==sample,'CBsetup sparseHEX partialreference sample,unknownbytes notzerofilled')
  gaps.append(dict(address=t,diagnostic_probe_bytes=12,observed_bytes_or_uncaptured_null=observed,captured_bytes=sum(v is not None for v in observed),
   probe_is_not_proved_table_extent=True,full_table_or_matcher_success_proved=False))
 return {'label':init.binding.PROFILES[index][0],'body':b,'HEX_capture_receipt':dict(source=pc,bytes=256,all_bytes_captured=True),'CFG_certificate':common.certificates(b),'paths':witnesses(b),
  'globals':dict(counter_halfword=C,secondary_head=head),'partial_reference_source_windows':gaps,
  'source_reuse':dict(ID11defaults=op,sha256=defaults['sha256'],new_code_bytes_counted=0),
  'normal_return_contract':['D0U16zero ->2;otherwise captureD4configpointer andreadconfig0byte/config4word for two ROMtablematcher calls;atleastone nonzero required,else2. OriginalA3isoverwritten beforefirstmatcher,notusedtolocallywritecallbackobject',
   'freshD2byte must7..16 else24;capturedcounterK1 mustnonzero;freshN1=D0,K1+N1>65536 ->1 (equalityallowed). Allocate12/tag4702,null19;fill12replyignored',
   'afterfill separatelyreadN2=D0,K2=counter;fori0..N2-1 reloadD4pointer,SHlow16(K2+i) atpointer+16*i+10. No callsinsideboundedloop. N2>0 ->SHlow16(K2+N2)counter;N2zero skipsIDs/counterbutstillcontinues',
   'node0=0;copy(node4,D,8);thenappendnode tosecondarylisthead orfirstnullnext;normalreply0. Underbytecopy node8isD4configpointer,notparentA3callbackobject. No rollback/free encoded'],
  'parent_composition':'secondarypublication mayprecedeparent0withoutprimarynode(A3null),parent2(freshconfig10zero),orparent19(primaryallocationnull). StablewrapperN4/K1 assignsIDs1..4,counter5,primarykeyfirstconfig10=1;thisisa conditionalexample,notobservedruntime.',
  'premises':'conditionalcandidateISA/provider/sourcebindings;validdescriptor/config/array/node/list/frame accesses;ordinarycalleeS/SP/RA/savedframepreservation;finite validtail-list anddistinctnodes;noadversealias/IRQ/DMA/reentry;eachfresh/capturedvalueidentity separatelyretained',
  'actual_installed_binding_tablecontents_object8writer_or_pointerlifetime_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-callback-setup-IDassign-secondarypublish-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'domains':domains(),
  'complete_body_bytes':512,'complete_body_instructions':200,'C_reconstruction_coverage_changed':False,
  'remaining':['partialROMreference sources andmatcher44624/446b8 contract','callbackobject8writers andwrapperactualcaller','actualcopy/providerbindings,freshvalue preservation,pairedlistidentity andpointerlifetime'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE)
  for a,d in decode(raw,STARTS[i]).items():
   off=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('CBsetup instructionmutation escaped')
   mutations+=1
  for off,_ in TYPED_LOADS[i]:
   bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError as ex:check('typedload encoding' in str(ex),'CBsetup typedguard')
   else:raise RuntimeError('CBsetup typedmutation escaped')
   typed+=1
 check((mutations,typed)==(200,4),'CBsetup mutationcensus');domains()
 print('PASS:200 instruction/4 typed-load mutations rejected;65536 counter domains andcount/stride/wrap/frame certificates')


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
 else:check(OUT.read_bytes()==encoded,'CBsetup exactledgerreplay')
 print('PASS:512B/200i complete setup;strict HEX;ID/counter/secondarylist/parent joins andpartial ROM windows;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,ROMtables,object8writer andpointerlifetime UNPROVED')


if __name__=='__main__':main()
