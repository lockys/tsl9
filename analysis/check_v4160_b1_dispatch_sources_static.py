"""Offline nominal timer-IRQ table ABI, gate source and pending-clear joins.
Original bytes and immutable CFG/def-use/interval/closed scalar proofs only.
No target execution/emulation or mutable object/task/provider model.
"""
import argparse,json,re,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_retry_services_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-dispatch-sources-static.json')
ROLES=('gate','initialize_prefix','cleanup_tail')
SIZES={'gate':30,'initialize_prefix':62,'cleanup_tail':80}
STARTS=({'gate': 351198, 'initialize_prefix': 341550, 'cleanup_tail': 358330}, {'gate': 351518, 'initialize_prefix': 341724, 'cleanup_tail': 358650})
COUNTS={'gate': 9, 'initialize_prefix': 20, 'cleanup_tail': 24}
HASHES=({'gate': 'fa1f4754fae15748af84432baa88396461e15ba14ac2567079c8f4654c37ddf8', 'initialize_prefix': 'd9161c509371f2ef33c33a70810b8ad946caf4fb8109187753bbeb610ba8425c', 'cleanup_tail': 'cd63242307aae91384674eadd2955172d658f6cb4b31fe819d43537a25350589'}, {'gate': 'ae43c8c6392fef73941d15eba2a6997ea1ddeed5951d3eee7f8d73895ae4dd87', 'initialize_prefix': 'b30defc16c708406db5627076a1d096a583e1d579d87c5a8390fb3fc0c7fc33c', 'cleanup_tail': 'b9213e9e7c485f59110edeb727222debffe20b2c09086ad1b88df67d5c3b3dfd'})
LITERALS={
'gate':"""
000 lui 15 536883200
004 load 15 15 415 1
008 addi 2 2 -16
00a store 2 1 12 4
00c bnez 15 30
00e lui 10 339968
012 addi 10 10 1324
016 jal 1 277582
01a jal 1 341550
""",
'initialize_prefix':"""
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 lui 15 536883200
00c addi 12 0 296
010 li 11 0
012 store 2 8 8 4
014 mv 8 10
016 addi 10 9 952
01a store 2 1 12 4
01c store 15 0 1252 4
020 store 2 18 0 4
022 auipc 1 536530944
026 jalr 1 1 -692
02a li 10 0
02c jal 1 351188
030 li 10 0
032 jal 1 351304
036 lui 15 536883200
03a store 15 8 415 1
""",
'cleanup_tail':"""
000 lui 15 536883200
004 addi 15 15 952
008 load 14 15 180 2
00c bnez 14 72
00e lui 14 536883200
012 store 14 0 1260 4
016 lui 14 536883200
01a load 14 14 568 4
01e store 15 14 176 4
022 lui 15 536883200
026 load 15 15 500 4
02a beqz 15 72
02c lui 8 536883200
030 addi 8 8 412
034 load 10 8 32 4
036 beqz 10 72
038 auipc 1 536514560
03c jalr 1 1 -1762
040 store 8 0 32 4
044 store 8 0 36 4
048 load 1 2 12 4
04a load 8 2 8 4
04c addi 2 2 16
04e jr 1
""",
}
PATCHES={'gate': {4: ('load', [15, 15, 495, 1]), 18: ('addi', [10, 10, 1498]), 22: ('jal', [1, 277722]), 26: ('jal', [1, 341724])}, 'initialize_prefix': {22: ('addi', [10, 9, 1032]), 28: ('store', [15, 0, 1332, 4]), 38: ('jalr', [1, 1, -866]), 44: ('jal', [1, 351508]), 50: ('jal', [1, 351624]), 58: ('store', [15, 8, 495, 1])}, 'cleanup_tail': {4: ('addi', [15, 15, 1032]), 18: ('store', [14, 0, 1340, 4]), 26: ('load', [14, 14, 648, 4]), 38: ('load', [15, 15, 580, 4]), 48: ('addi', [8, 8, 492]), 56: ('auipc', [1, 536510464]), 60: ('jalr', [1, 1, 2014])}}
TYPED={'gate': [(4, 4)], 'initialize_prefix': [], 'cleanup_tail': [(8, 5), (26, 2), (38, 2)]}


def guard(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'dispatchsources literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  s[pc+o]=f
 check(n.keys()==s.keys(),'dispatchsources exactwindowboundaries '+role)
 for a,f in s.items():init.g(n,a,'dispatchsources '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'dispatchsources selectedidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'dispatchsources unsigned typedload')
 return n


def window(raw,role,index):
 pc=STARTS[index][role];n=guard(raw,role,index);e={};calls=[];frontier=set();rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'dispatchsources ordinaryRET');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op in ('jal','jalr'):
   check(d['rd']==1,'dispatchsources selectedlinkedcall');t=d.get('target')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'dispatchsources PCrelativepair');t=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append(dict(offset=a-pc,target=t))
  check(op not in ('ecall','mret','csr','jump','call_indirect'),'dispatchsources selectedops');e[a]=q;frontier.update(z for z in q if z not in n)
 expected={'gate':[(22,0x43c4e+140*index),(26,0x5362e+174*index)],'initialize_prefix':[(38,0x2000039c),(44,0x55bd4+320*index),(50,0x55c48+320*index)],'cleanup_tail':[(0x3c,0x20000110)]}[role]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==([0x4e] if role=='cleanup_tail' else []),'dispatchsources exactcalls/RETs')
 check(frontier==(set() if role=='cleanup_tail' else {pc+SIZES[role]}),'dispatchsources exactfrontiers')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index][role],instructions=list(n.values()),selected_CFG=e,outside_window_frontier=sorted(frontier),linked_calls=calls,returns=rets,complete_function_claim=False,full_body_reused_for_context=True)


def header_contract(raw):
 patterns={
  'status_type':rb'(?m)^typedef\s+uint8_t\s+bStatus_t\s*;',
  'default_FLASH_base':rb'(?m)^#define\s+LIB_FLASH_BASE_ADDRESSS\s+0x00040000\s*$',
  'function_table_base':rb'(?m)^#define\s+FUNCITON_BASE_ADDRESSS\s+\(LIB_FLASH_BASE_ADDRESSS\+0x34\)\s*$',
  'table_word_load':rb'(?m)^#define\s+BLE_LIB_JT\(n\)\s+\(\*\(uint32_t\*\)\(\s*FUNCITON_BASE_ADDRESSS\+n\*4\s*\)\)\s*$',
  'IRQ_alias':rb'(?m)^#define\s+TMOS_TimerIRQHandler\s+\(\(\s*bStatus_t\s*\(\*\)\s*\(\s*uint32_t\s*\*time\s*\)\s*\)\s*BLE_LIB_JT\(120\)\s*\)\s*$'}
 matches={k:re.findall(p,raw) for k,p in patterns.items()}
 check(all(len(v)==1 for v in matches.values()),'dispatchsources originalSDK exactmacro/type declarations')
 check(0x40000+0x34+120*4==0x40214,'dispatchsources exactJT120 address')
 return dict(header_sha256=sha256(raw).hexdigest(),declarations={k:v[0].decode().strip() for k,v in matches.items()},nominal_alias='TMOS_TimerIRQHandler',nominal_return_type='bStatus_t = uint8_t',nominal_argument='uint32_t *time',default_library_base=0x40000,table_offset=0x34,index=120,word_address=0x40214,
  comment_param_None_does_not_override_explicit_macro_signature=True,ABI_name_is_not_actual_callsite_or_installed_provider_proof=True)


def vector(raw):
 check(raw==bytes.fromhex('ba090020'),'dispatchsources exactJT120word')
 return dict(address=0x40214,bytes=4,sha256=sha256(raw).hexdigest(),value=0x200009ba)


def byte_hits(raw,base,value):
 needle=value.to_bytes(4,'little');hits=[];start=0
 while (o:=raw.find(needle,start))>=0:hits.append(base+o);start=o+1
 return hits


def source_census(image,data,mem):
 hits={name:{hex(v):byte_hits(raw,base,v) for v in (0x200009ba,0x200009bb,0x40214)} for name,raw,base in (('APP',image,0x8000),('candidate_file',data,0x40000))}
 check(hits['APP']=={'0x200009ba':[],'0x200009bb':[],'0x40214':[]} and hits['candidate_file']=={'0x200009ba':[0x40214],'0x200009bb':[],'0x40214':[]},'dispatchsources exactbounded bytepatterncensus')
 check(sparse.captured(mem,0x40214,4)==bytes.fromhex('ba090020'),'dispatchsources uniquehit strictHEX')
 return dict(all_byte_start_literal_matches=hits,APP_bytes=len(image),candidate_file_bytes=len(data),source_capture_required_for_positive_hit=True,indirect_indexed_nonadjacent_or_missing_ROM_callers_excluded=False,not_a_complete_callgraph_or_instruction_boundary_census=True)


def paths(b):
 pc=b['start'];e=b['selected_CFG'];walks=[]
 def visit(a,p):
  check(a not in p,'dispatchsources selectedDAG')
  p=p+[a]
  if a not in e or not e[a]:walks.append([v-pc for v in p]);return
  for z in e[a]:visit(z,p)
 visit(pc,[])
 covered={(pc+a,pc+z) for p in walks for a,z in zip(p,p[1:])}
 check(covered=={(a,z) for a,qs in e.items() for z in qs},'dispatchsources allselected edgeswitnessed')
 return dict(selected_syntactic_entry_exit_walks=walks,all_selected_edges_witnessed=True,not_target_traces_or_feasible_input_witnesses=True)


def profile(image,data,hexraw,index,abi):
 import check_v4160_first_role_gate_static as role
 import check_v4160_role_initializer_fields_static as fields
 import check_v4160_task5_object_static as obj
 import check_v4160_task_registration_static as registration
 import check_v4160_config_buffer_source_static as buffer
 _,mem=sparse.inspect(hexraw,sparse.parser())
 def take(pc,z):
  raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'dispatchsources strictHEX selected/reused');return raw
 ws={r:window(take(STARTS[index][r],SIZES[r]),r,index) for r in ROLES};wn={r:{d['pc']-w['start']:d for d in w['instructions']} for r,w in ws.items()}
 gb=role.body(take(STARTS[index]['gate'],84),'gate',index)
 ib=fields.body(take(STARTS[index]['initialize_prefix'],426),'initializer',index)
 cp=obj.STARTS[index][1];cb=obj.body(take(cp,252),'cleanup',index);walks=obj.cleanup_paths(cb)
 reg=registration.body(take(registration.DETAILS[index][0],48),index)
 fill=buffer.fill_contract(take(0x4060c+64*index,46))
 setters=[role.body(take(s,10),'setter'+str(k),index) for k,s in enumerate(role.DETAILS[index]['setters'])]
 check(fill['encoded_GPR_writes']==[10,14,15] and all(not any(d.get('rd')==8 for d in s['instructions']) for s in setters),'dispatchsources matchedfill/setters preserveheldS0')
 check(reg['encoded_GPR_definitions']==[10,12,13,14,15] and reg['no_local_frame_or_nested_calls'],'dispatchsources registrationleaf')
 gn,inn,cn=(wn[r] for r in ROLES);G=0x20003000;C=G+412+80*index;B=G+952+80*index;D=G+564+80*index;pending=B+308
 check(gn[0]['imm']+gn[4]['imm']==C+3 and gn[12]['target']==ws['gate']['start']+30 and gn[22]['target']==registration.DETAILS[index][0] and gn[26]['target']==ws['initialize_prefix']['start'],'dispatchsources gatezero ->registration theninitializer')
 check(not any(d.get('rd')==10 for o,d in gn.items() if 22<o<26),'dispatchsources rawregistrationA0 passedtosetup')
 check(inn[20]['op']=='mv' and inn[20]['rd']==8 and inn[20]['rs2']==10 and [o for o,d in inn.items() if d.get('rd')==8]==[20] and inn[58]['rs2']==8 and inn[54]['imm']+inn[58]['imm']==C+3,'dispatchsources capturedrawreply low8 toC3')
 check(inn[22]['rs1']==9 and inn[22]['imm']==952+80*index and inn[12]['imm']==296 and inn[16]['imm']==0,'dispatchsources prefixfill(B,0,296)')
 # These numeric intervals cover the matched prefix/leaf effects only. Later
 # initializer callees, aliases and frame/global overlaps stay explicit premises.
 writes=[(B,296),(B+296,4),(B+300,4),(B+304,4)]
 for a,z in writes:
  for x,n in ((C+3,1),(pending,4),(D+16,4)):check(a+z<=x or x+n<=a,'dispatchsources prefixclear excludes gate/pending/D16')
 check(cn[0]['imm']+cn[4]['imm']==B and cn[8]['imm']==180 and cn[8]['width']==2 and cn[12]['target']==cp+0xb4,'dispatchsources freshB180 controlscleanupclear')
 check(cn[14]['imm']+cn[18]['imm']==pending and cn[18]['rs2']==0 and cn[18]['width']==4,'dispatchsources pendingzero fixedbase')
 check(cn[22]['imm']+cn[26]['imm']==D+4 and cn[30]['imm']==176 and cn[30]['rs2']==14 and cn[34]['imm']+cn[38]['imm']==C+88,'dispatchsources freshperiod/B176 then independentC88gate')
 check(cn[44]['imm']+cn[48]['imm']==C and cn[52]['imm']==cn[64]['imm']==32 and cn[68]['imm']==36,'dispatchsources C32release thenlocal32/36 clear')
 check(len({pending,D+16,C+88,C+3})==4,'dispatchsources sameprofile distinctcells')
 pb=previous.body(take(previous.SOURCES[index]['publish'],10),'publish',index)
 db=previous.body(take(previous.SOURCES[index]['dispatch'],48),'dispatch',index);df=previous.certificates(db,'dispatch')['facts']
 check(df['first_gate']==C+3 and df['callback_word']==D+16 and previous.certificates(pb,'publish')['facts']['destination']==D+16,'dispatchsources actualconsumer celljoins')
 vb=vector(take(abi['word_address'],4));check(vb['value']==db['start'],'dispatchsources nominalJT120 ->mappeddispatcher')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];check(int(fc['source'],16)+vb['value']-int(fc['destination'],16)==db['source'] and vb['value']+48<=int(mapping['first_copy_end_exclusive'],16),'dispatchsources completecopieddispatcher mapping')
 # Confirm that each selected window is a subrange of the checked full context.
 for r,full,start in (('gate',gb,STARTS[index]['gate']),('initialize_prefix',ib,STARTS[index]['initialize_prefix']),('cleanup_tail',cb,cp)):
  fulln={d['pc']:d for d in full['instructions']};check(all(fulln[d['pc']]==d for d in ws[r]['instructions']),'dispatchsources selectedops equal fullbody')
 return dict(label=init.binding.PROFILES[index][0],selected_windows=ws,selected_path_certificates={r:paths(b) for r,b in ws.items()},nominal_JT120=vb,
  reused_full_contexts=dict(gate=dict(start=STARTS[index]['gate'],bytes=84,sha256=gb['sha256']),initializer=dict(start=STARTS[index]['initialize_prefix'],bytes=426,sha256=ib['sha256']),cleanup=dict(start=cp,bytes=252,sha256=cb['sha256'],all_edge_witnesses=walks),registration=dict(start=registration.DETAILS[index][0],bytes=48,sha256=reg['sha256']),fill=dict(source=0x4060c+64*index,bytes=46,sha256=sha256(take(0x4060c+64*index,46)).hexdigest()),setters=[dict(start=s['start'],bytes=s['bytes'],sha256=s['sha256']) for s in setters]),
  consumer=dict(start=db['start'],source=db['source'],bytes=48,sha256=db['sha256'],first_copy=fc),bounded_literal_census=source_census(image,data,mem),
  cells=dict(C=C,B=B,D=D,dispatch_gate=C+3,pending=pending,callback=D+16,cleanup_independent_gate=C+88),
  source_contracts=['fresh C3 zero selects register(handler) then setup(rawreply);setup captures rawreply in S0 and low8 stores C3 after matched fill/setters;no255 rejection',
   'registration success n<c returns n;failure n>=c returns255;therefore C3!=0 does not prove registration success and valid n0 registration givesgate0',
   'prefix fill(B,0,296) and three trailingwordclears end at B308 exclusive;pending B308 is outside;doesnot prove preservation across laterinitializercalls',
   'cleanup freshU16 B180 zero ->pending=0 ->fresh D4 copied B176 ->independent C88 gate;C32nonnull asks private release then clears C32/C36. No direct D16 clear inselectedtail;opaque release effects notexcluded',
   'matching SDK defaultJT120 word ->completecopied RAM200009ba. Nominal uint32_t*time fits previous selector Out4B requirement,not actual call argument/init/nonretention proof'],
  actual_callsite_ordering_otherwriters_providerbinding_aliases_inflight_callbacks_and_complete_consumption_release_lifetimes_proved=False)


def domains():
 cases=0
 for n in range(256):
  for capacity in range(256):
   reply=n if n<capacity else 255
   check(0<=reply<=255 and (reply!=0)==(n>=capacity or n!=0),'dispatchsources registrationreply/nonzero identity');cases+=1
 check((0 if 0<1 else 255)==0 and (255 if 255<255 else 255)==255,'dispatchsources validzero/rejected255 counterexamples')
 return dict(registration_count_capacity_pairs=cases,scope='closed host U8 scalar identity;not executed registration/task state',successful_zero_index_has_dispatch_gate_zero=True,rejection255_has_dispatch_gate_nonzero=True,actual_count_capacity_or_task_liveness_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes);abi=header_contract(header)
 return dict(schema='TSL9-B1-timerIRQ-nominal-table-and-dispatch-source-joins-static-v1',APP_sha256=sha256(image).hexdigest(),SDK=abi,profiles=[profile(image,d,h,i,abi) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_complete_body_bytes=0,new_complete_body_instructions=0,selected_previously_guarded_bytes=344,selected_instruction_guards=106,new_word_vector_bytes=8,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['actual JT120/dispatcher caller PC and argument initialization/reply use','other C3/pending/D16 writers and ordering','actual loaded provider and valid nonalias globals/frames','opaque query/release sideeffects and full callback/node consumption-release lifetimes'])


def tests(carriers,header):
 mutations=typed=wordbytes=0
 for i,data in enumerate(carriers):
  for r in ROLES:
   pc=STARTS[i][r];raw=init.binding.take(data,pc,SIZES[r]);n=guard(raw,r,i)
   for d in n.values():
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:guard(bad,r,i)
    except RuntimeError:pass
    else:raise RuntimeError('dispatchsources instructionmutation escaped')
    mutations+=1
   for o,_ in TYPED[r]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:guard(bad,r,i)
    except RuntimeError:pass
    else:raise RuntimeError('dispatchsources typedmutation escaped')
    typed+=1
  raw=init.binding.take(data,0x40214,4)
  for o in range(4):
   bad=bytearray(raw);bad[o]^=1
   try:vector(bad)
   except RuntimeError:pass
   else:raise RuntimeError('dispatchsources wordmutation escaped')
   wordbytes+=1
 for old,new in ((b'BLE_LIB_JT(120)',b'BLE_LIB_JT(121)'),(b'uint32_t *time',b'uint16_t *time'),(b'typedef uint8_t                 bStatus_t;',b'typedef uint16_t                bStatus_t;'),(b'(LIB_FLASH_BASE_ADDRESSS+0x34)',b'(LIB_FLASH_BASE_ADDRESSS+0x38)')):
  bad=header.replace(old,new);check(bad!=header,'dispatchsources header mutation occurred')
  try:header_contract(bad)
  except RuntimeError:pass
  else:raise RuntimeError('dispatchsources ABI mutation escaped')
 check((mutations,typed,wordbytes)==(106,8,8),'dispatchsources mutationcensus')
 print('PASS:106 instruction/8 typed-load/8 vector-byte/4 SDK ABI mutations rejected')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers,header);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'dispatchsources exactledger replay')
 print('PASS:JT120 nominal TimerIRQ ABI;344B/106i selected source joins+8B vector;strictHEX;exactledger')
 print('PASS:NO target execution/emulation;actualcallers/installedbinding/full consumption-release lifetimes UNPROVED')


if __name__=='__main__':main()
