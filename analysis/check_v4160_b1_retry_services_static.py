"""Offline retry counter and callback publication/dispatch contracts.
Original bytes, immutable CFG/def-use and closed host scalar identities only.
No target execution/emulation or mutable object/list/heap/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_fallback_tail_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-retry-services-static.json')
ROLES=('retry','publish','dispatch')
SIZES={'retry':62,'publish':10,'dispatch':48}
STARTS=({'retry': 352582, 'publish': 278226, 'dispatch': 536873402}, {'retry': 352902, 'publish': 278366, 'dispatch': 536873402})
SOURCES=({'retry': 352582, 'publish': 278226, 'dispatch': 265258}, {'retry': 352902, 'publish': 278366, 'dispatch': 265322})
COUNTS={'retry': 19, 'publish': 3, 'dispatch': 16}
HASHES=({'retry': '915d36a2c28a585a43a59a2a7aeb3e06c81c976817ac639d12b9cdb3414483a7', 'publish': 'e0cb016bd834c66f3eee4e65cdfa8b88190468b945c417dcc03093b804297a37', 'dispatch': '4788cb2d8da1107724fa9c26fdc3c5e559762786debec6aef529a3023735d185'}, {'retry': '915d36a2c28a585a43a59a2a7aeb3e06c81c976817ac639d12b9cdb3414483a7', 'publish': '2cd938b76377503dcae7c3b15890983ab1b8de75f83ae0414bd14ed9d14a711e', 'dispatch': 'e26fccbae34b2fb0cbe763dafed34a9fc6c0fe21a006696a4c260627ef9ff6e4'})
LITERALS={
'retry':"""
000 load 15 10 236 4
004 addi 15 15 1
006 store 10 15 236 4
00a bnez 15 22
00c load 15 10 240 4
010 addi 15 15 1
012 store 10 15 240 4
016 load 15 10 240 4
01a andi 15 15 128
01e beqz 15 42
020 li 15 1
022 store 10 15 236 4
026 store 10 0 240 4
02a load 15 10 42 1
02e andi 14 15 64
032 beqz 14 60
034 ori 15 15 32
038 store 10 15 42 1
03c jr 1
""",
'publish':"""
000 lui 15 536883200
004 store 15 10 580 4
008 jr 1
""",
'dispatch':"""
000 lui 15 536883200
004 load 15 15 415 1
008 beqz 15 34
00a lui 15 536883200
00e load 15 15 576 1
012 beqz 15 38
014 lui 15 536883200
018 load 6 15 580 4
01c beq 6 0 42
020 jr 6
022 li 10 1
024 jr 1
026 li 10 2
028 jr 1
02a addi 10 0 255
02e jr 1
""",
}
PATCHES={'retry': {}, 'publish': {4: ('store', [15, 10, 660, 4])}, 'dispatch': {4: ('load', [15, 15, 495, 1]), 14: ('load', [15, 15, 656, 1]), 24: ('load', [6, 15, 660, 4])}}
TYPED={'retry': [(0, 2), (12, 2), (22, 2), (42, 4)], 'publish': [], 'dispatch': [(4, 4), (14, 4), (24, 2)]}
STORES={'retry': [(6, 10, 15, 236, 4), (18, 10, 15, 240, 4), (34, 10, 15, 236, 4), (38, 10, 0, 240, 4), (56, 10, 15, 42, 1)], 'publish': [(4, 15, 10, 580, 4)], 'dispatch': []}


def guard(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);spec={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'retryservices literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'retryservices completeboundaries '+role)
 for a,f in spec.items():init.g(n,a,'retryservices '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'retryservices completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'retryservices typedload')
 return n


def body(raw,role,index):
 pc=STARTS[index][role];n=guard(raw,role,index);e={};rets=[];tails=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':
   q=[]
   if d['rs1']==1:rets.append(a-pc)
   else:check(role=='dispatch' and d['rs1']==6,'retryservices onlyexternalJR');tails.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  check(op not in ('ecall','mret','csr','jal','jalr','call_indirect','jump') and all(z in n for z in q),'retryservices closedlocalCFG/no calls');e[a]=q
 check(rets=={'retry':[0x3c],'publish':[8],'dispatch':[0x24,0x28,0x2e]}[role] and tails==([0x20] if role=='dispatch' else []),'retryservices exactexits')
 seen=set();active=set()
 def visit(a):
  check(a not in active,'retryservices acyclic')
  if a in seen:return
  active.add(a)
  for z in e[a]:visit(z)
  active.remove(a);seen.add(a)
 visit(pc);check(seen==set(n),'retryservices allreachable includingposttail')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(o,b,r,v+80*index if role=='publish' else v,w) for o,b,r,v,w in STORES[role]]
 check(stores==expected,'retryservices allstores')
 defs={d['rd'] for d in n.values() if 'rd'in d}
 check(defs=={'retry':{14,15},'publish':{15},'dispatch':{6,10,15}}[role],'retryservices exactregisterdefs/no frame orcallee saved writes')
 return dict(start=pc,source=SOURCES[index][role],bytes=len(raw),sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,returns=rets,external_unlinked_JR_offsets=tails,stores=stores,register_definitions=sorted(defs),complete_local_body=True,local_CFG_acyclic=True,no_frame_or_linked_calls=True,actual_invocation_or_wholechain_completion_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=[a for a,q in e.items() if not q];pred={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].append(a)
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 def finish(a):return min((p for z in ends if (p:=path(a,z)) is not None),key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'retryservices all edgewitness');walks.append([v-pc for v in p])
 def count(a,z=None,blocked=()):
  cache={}
  def f(a):
   if a in blocked:return 0
   if a==z:return 1
   if a not in cache:cache[a]=int(z is None) if not e[a] else sum(f(v) for v in e[a])
   return cache[a]
  return f(a)
 def last_before(a):
  todo=pred[a][:];hits=set();entry=(a==pc);seen=set()
  while todo:
   a=todo.pop()
   if n[a-pc].get('rd')==10:hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(pred[a])
  return hits,entry
 if role=='retry':
  check(n[0]['imm']==n[6]['imm']==236 and n[0xc]['imm']==n[0x12]['imm']==n[0x16]['imm']==240 and n[0x1a]['imm']==128,'retryservices low/highfreshsamples/bit39')
  check(n[0xa]['rs1']==15 and n[0xa]['target']==pc+0x16 and n[0x1e]['target']==pc+0x2a,'retryservices carrybranch andresetguard')
  check(n[0x20]['imm']==1 and n[0x22]['imm']==236 and n[0x26]['rs2']==0 and n[0x26]['imm']==240,'retryservices resetone thenzerohigh')
  check(n[0x2a]['imm']==n[0x38]['imm']==42 and n[0x2e]['imm']==64 and n[0x34]['imm']==32 and n[0x32]['target']==pc+0x3c,'retryservices bit6gate/heldbyteORbit5')
  check(last_before(pc+0x3c)==(set(),True) and count(pc,pc+0x3c,blocked=[pc+6])==0,'retryservices entryA0preserved/lowstoredominates')
  check(path(pc+0x12,pc+0x16) is not None and path(pc+0x26,pc+0x38) is not None,'retryservices freshhighaftercarry/flagafterreset')
  facts=dict(direct_P_prefix_bytes=244,normal_A0='unchanged entry P',low_carry_test='held increment == 0',high_reset_test='fresh U32[P240] & 128',reset_order=['P236=1','P240=0'],flag='fresh P42 bit6 set -> held P42 OR 32;else no store',no_local_allocation_free_or_pointer_publication=True,atomic_counter_or_flag_RMW=False,global_canonical_counter_invariant_proved=False)
 elif role=='publish':
  check(n[0]['imm']==0x20003000 and n[4]['rs2']==10 and n[4]['width']==4 and last_before(pc+8)==(set(),True),'retryservices rawword publication/unchangedA0')
  facts=dict(destination=n[0]['imm']+n[4]['imm'],word_width=4,normal_A0='unchanged entry value',callback_invoked_here=False,no_local_load_guard_separate_clear_allocation_or_release=True,zero_entry_value_clears_destination=True,valid_pointer_or_extent_or_lifetime_proved=False)
 else:
  check(n[0]['imm']==n[0xa]['imm']==n[0x14]['imm']==0x20003000 and n[0xe]['width']==1 and n[0x18]['width']==4,'retryservices dispatch freshgates andword')
  check(n[8]['target']==pc+0x22 and n[0x12]['target']==pc+0x26 and n[0x1c]['target']==pc+0x2a,'retryservices orderedgates')
  check(n[0x22]['imm']==1 and n[0x26]['imm']==2 and n[0x2a]['imm']==255 and n[0x2a]['rs1']==0,'retryservices exactearlyvalues')
  for end,definition in ((0x24,0x22),(0x28,0x26),(0x2e,0x2a)):check(last_before(pc+end)==({definition},False),'retryservices earlyA0defuse')
  check(last_before(pc+0x20)==(set(),True) and count(pc,pc+0x20,blocked=[pc+0x18])==0,'retryservices tailoriginalA0/slotloaddominates')
  facts=dict(first_gate=0x20003000+n[4]['imm'],second_gate=0x20003000+n[0xe]['imm'],callback_word=0x20003000+n[0x18]['imm'],early_statuses=[1,2,255],success='JR T1 unlinked after all three nonzero samples; A0/A1/RA/SP unchanged',no_local_stores_clear_free_or_frame=True,success_scalar_return_or_callback_retention_proved=False)
 check((len(walks),count(pc))=={'retry':(21,8),'publish':(2,1),'dispatch':(15,4)}[role],'retryservices edge/pathcensus')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),syntactic_DAG_paths=count(pc),exit_path_counts={hex(a-pc):count(pc,a) for a in ends},facts=facts,walks_are_not_feasible_inputs_or_runtime_progress=True)


def joins(data,mem,index,bs):
 import check_v4160_b1_key_source_tail_static as key
 import check_v4160_b1_ram_record_callback_static as record
 import check_v4160_config_gates_static as config
 def take(pc,z):
  raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'retryservices reusedfullbody strictHEX');return raw
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];src=int(fc['source'],16);dst=int(fc['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 for runtime,source,z in ((bs['dispatch']['start'],bs['dispatch']['source'],48),(record.STARTS['select'],record.SOURCES[index]['select'],222)):
  check(dst<=runtime and runtime+z<=end and src+runtime-dst==source,'retryservices fullfirstcopy runtime/sourceidentity')
 sp=previous.STARTS[index]['sharedtail'];sb=previous.body(take(sp,278),'sharedtail',index);previous.certificates(sb,'sharedtail');sn={d['pc']-sp:d for d in sb['instructions']}
 check(next(c['target'] for c in sb['calls'] if c['offset']==0xc2)==bs['publish']['start'] and sn[0xbe]['rd']==10 and sn[0xbe]['imm']==1260+80*index,'retryservices sharedtail heldpending ->matchingpublish')
 check(not any(d.get('rd')==10 for o,d in sn.items() if 0xc2<o<=0xde),'retryservices unchangedpublishreply reachesnormalRET')
 rp=previous.SLICE_STARTS[index]['retry'];rb=previous.slice_guard(take(rp,18),'retry',index)
 check(rb['calls']==[bs['retry']['start']],'retryservices selectedparentcall')
 kp=key.STARTS[index]['tail'];kb=key.body(take(kp,168),'tail',index);key.certificates(kb,'tail');kn={d['pc']-kp:d for d in kb['instructions']}
 check(kn[0x18]['imm']==kn[0x30]['imm']==kn[0x34]['imm']==kn[0x5e]['imm']==1260+80*index and kn[0x28]['imm']+kn[0x2c]['imm']==record.STARTS['select'] and kn[0x3c]['target']==bs['publish']['start'],'retryservices fixedselectorliteral/pending/sourceclear/publishjoin')
 check(kn[0x20]['target']==kp+0x34 and kn[0x34]['rd']==10 and kn[0x30]['rs2']==14 and kn[0x5e]['rs2']==0,'retryservices conditional literal butfreshreload can differ')
 select=record.body(take(record.SOURCES[index]['select'],222),'select',index);selectcert=record.certificates(select,'select')
 cp,cz,*_=config.DETAILS[index];cb=config.body(take(cp,cz),index);cn={d['pc']-cp:d for d in cb['instructions']}
 pub=certificates(bs['publish'],'publish')['facts']['destination'];df=certificates(bs['dispatch'],'dispatch')['facts'];D=0x20003234+80*index;pending=0x200034ec+80*index
 check(pub==df['callback_word']==D+16 and df['second_gate']==D+12 and int(cb['copied_config'],16)==D and cb['copy_call_arguments']['A2']==16,'retryservices matchingpublication/consumer/copyboundary')
 if index:check(cn[12]['op']=='store' and cn[12]['rs1']==15 and cn[12]['rs2']==0 and cn[12]['imm']==660 and cb['V140_unconditional_pre_hook_clear']==hex(pub),'retryservices V140 prehookslotclear')
 else:check(cb['V140_unconditional_pre_hook_clear'] is None,'retryservices V131 no corresponding preclear claim')
 check(pending!=pub and D+16==pub and int(cb['optional_hook_word'],16)!=pub,'retryservices pending/copiedrecord/optionalhook distinct cells')
 return dict(reused_sharedtail=dict(start=sp,bytes=278,sha256=sb['sha256'],fresh_pending_load_offset=0xbe,publication_call_offset=0xc2,normal_RET_A0='same held pending value if matching publish returns normally'),selected_parent_retry=rb,
  reused_key_source_tail=dict(start=kp,bytes=168,sha256=kb['sha256'],pending_word=pending,literal=record.STARTS['select'],literal_store_offset=0x30,fresh_reload_offset=0x34,publication_call_offset=0x3c,pending_clear_other_arm=0x5e),
  first_copy=mapping['first_copy'],first_copy_end_exclusive=mapping['first_copy_end_exclusive'],
  reused_selector=dict(start=record.STARTS['select'],source=record.SOURCES[index]['select'],bytes=222,sha256=select['sha256'],certificate=selectcert,dispatch_entry_A0='caller-original Out if actual callback word still equals selector',required_writable_output_bytes=4,no_local_output_nullguard=True,query_SP12_uninitialized_locally=True,registry_termination_or_transitive_nonretention_proved=False),
  reused_config=dict(start=cp,bytes=cz,sha256=cb['sha256'],copied_config=D,copy_bytes=16,copy_excludes_D16=True,pre_hook_callback_clear=cb['V140_unconditional_pre_hook_clear'],unknown_hook_or_copy_sideeffects_excluded=False),
  destination=pub,pending_word_distinct_from_callback_word=True,matching_loaded_code_required=True,actual_callers_ordering_binding_aliases_inflight_callbacks_and_complete_lifetimes_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  raw=init.binding.take(data,SOURCES[index][role],SIZES[role]);check(sparse.captured(mem,SOURCES[index][role],len(raw))==raw,'retryservices newbody strictHEX');bs[role]=body(raw,role,index)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={r:certificates(b,r) for r,b in bs.items()},conditional_joins=joins(data,mem,index,bs),actual_provider_binding_or_full_consumption_release_lifetime_proved=False)


def domains():
 # Closed host integer identities; these expressions do not run an ISA or mutate
 # a target counter. Stable samples are an explicit hypothesis for concatenation.
 m=0xffffffff;cases=0
 for high in range(65536):
  for low in (0,1,m-1,m):
   u=(low+1)&m;h=(high+int(u==0))&m;v=(high<<32)|low
   check(((h<<32)|u)==((v+1)&((1<<64)-1)),'retryservices stable-sample carryidentity');cases+=1
   if high<128:
    check((bool(h&128))==(v==(1<<39)-1),'retryservices sampledcanonicalboundary')
 for low in range(65536):
  check((127<<32)+low+1<(1<<39),'retryservices all16bitlows canonical interior');cases+=1
 for byte in range(256):
  check(((byte|32)&64)==(byte&64) and (byte|32)&32,'retryservices heldflag ORidentity')
 check(((256+0)<<32)|1 > (1<<39) and not (256&128),'retryservices noncanonicalupperbits survivebit7test')
 check((1<<39)-1+1==128<<32 and ((128&128)!=0),'retryservices closedcanonicalwrapto1')
 return dict(stable_sample_u64_carry_identity_family_cases=262144,high_family='all U16 high words,low32 in 0/1/fffffffe/ffffffff;not all U32 high/low pairs',additional_canonical_low16_cases=65536,total_counter_identity_family_cases=cases,flag_byte_cases=256,
  conditional_canonical_domain='For stable uninterrupted samples and 0<=V<2^39: increment unless V=2^39-1, then reset to1;zero also advances to1',reset_predicate='fresh high bit7,concatenated bit39;not bit63 or generic modulo2^39',noncanonical_witness=dict(high=256,low=0,after_high=256,after_low=1),witness_is_not_reachable_input_or_runtime_observation=True,atomicity_termination_or_global_invariant_proved=False,closed_host_scalar_identities_only=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-retry-publication-dispatch-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_complete_body_bytes=240,new_complete_body_instructions=76,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['actual dispatcher callers and matching copied/installed code','other pending/D16/gate writers and actual ordering/aliasing','canonical counter source and concurrent updates','opaque selector queries/callback retention/object identity and complete consumption-release lifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,SOURCES[i][role],SIZES[role]);n=guard(raw,role,i)
   for d in n.values():
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:guard(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('retryservices instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:guard(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('retryservices typedmutation escaped')
    typed+=1
 check((mutated,typed)==(76,14),'retryservices mutationcensus')
 print('PASS:76 instruction/14 typed-load mutations rejected;complete retry/publish/dispatch')


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
 else:check(OUT.read_bytes()==encoded,'retryservices exactledger replay')
 print('PASS:240B/76i complete bodies;strictHEX/runtimePC;retry/publication/dispatch/selector/config joins;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/aliasing/concurrency/full consumption-release lifetimes UNPROVED')


if __name__=='__main__':main()
