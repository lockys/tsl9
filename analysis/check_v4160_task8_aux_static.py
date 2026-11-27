"""Offline extended-payload auxiliary: immutable operands/CFG and scalar proofs.
No target instructions, providers, crypto, RAM/heap or hardware are executed.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_task8_typea0_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-task8-aux-static.json')
STARTS=(0x50160,0x501fa)
SIZE=340
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=('ac8937170ebceb6562671206bf9ac8c8ce019f9113e65abd3438517288dfa350', 'c007eeaa675ab65b00a4f913f8436168c937de498a25925a90464d1266cf8392')
TYPED_LOADS=(((80, 4), (84, 4), (94, 4), (100, 4), (108, 2), (128, 4)), ((80, 4), (84, 4), (94, 4), (100, 4), (108, 2), (128, 4)))
LITERALS=(
'''
000 addi 2 2 -64
002 store 2 8 56 4
004 store 2 1 60 4
006 store 2 9 52 4
008 store 2 18 48 4
00a store 2 19 44 4
00c store 2 20 40 4
00e store 2 21 36 4
010 store 2 22 32 4
012 store 2 23 28 4
014 store 2 24 24 4
016 store 2 25 20 4
018 li 8 2
01a beq 12 0 308
01e beq 14 0 308
022 mv 23 10
024 mv 18 14
026 mv 22 13
028 mv 21 12
02a mv 24 11
02c auipc 1 536547328
030 jalr 1 1 -1784
034 mv 20 10
036 li 8 20
038 beq 10 0 308
03c addi 11 0 83
040 li 10 16
042 auipc 1 536543232
046 jalr 1 1 -354
04a mv 19 10
04c li 8 19
04e beqz 10 308
050 load 9 18 1 1
054 load 15 18 2 1
058 slli 9 9 8
05a slli 15 15 16
05c add 9 9 15
05e load 15 18 0 1
062 add 9 9 15
064 load 15 18 3 1
068 slli 15 15 24
06a add 9 9 15
06c load 15 20 40 4
070 bltu 15 9 124
074 li 14 -1
076 li 8 2
078 bne 15 14 298
07c beq 24 0 138
080 load 15 20 4 1
084 li 8 1
086 andi 15 15 2
088 beqz 15 298
08a addi 25 22 4
08e li 12 8
090 li 11 0
092 mv 10 2
094 slli 25 25 16
096 auipc 1 536543232
09a jalr 1 1 422
09e srli 25 25 16
0a2 addi 11 0 83
0a6 mv 10 25
0a8 auipc 1 536543232
0ac jalr 1 1 -456
0b0 mv 24 10
0b2 li 8 19
0b4 beqz 10 298
0b6 mv 12 22
0b8 mv 11 21
0ba addi 10 10 4
0bc auipc 1 536543232
0c0 jalr 1 1 622
0c4 li 12 4
0c6 mv 11 18
0c8 mv 10 24
0ca auipc 1 536543232
0ce jalr 1 1 608
0d2 li 12 16
0d4 addi 11 20 24
0d8 mv 10 19
0da auipc 1 536543232
0de jalr 1 1 592
0e2 li 14 8
0e4 mv 13 2
0e6 mv 12 25
0e8 mv 11 24
0ea mv 10 19
0ec jal 1 336352
0f0 mv 8 10
0f2 bnez 10 288
0f4 li 12 8
0f6 mv 11 2
0f8 addi 10 2 8
0fa auipc 1 536543232
0fe jalr 1 1 560
102 li 12 8
104 addi 11 18 4
108 addi 10 2 8
10a auipc 1 536543232
10e jalr 1 1 472
112 li 15 1
114 bne 10 15 336
118 mv 11 9
11a mv 10 23
11c jal 1 287496
120 mv 10 24
122 auipc 1 536543232
126 jalr 1 1 -370
12a mv 10 19
12c auipc 1 536543232
130 jalr 1 1 -380
134 mv 10 8
136 load 1 2 60 4
138 load 8 2 56 4
13a load 9 2 52 4
13c load 18 2 48 4
13e load 19 2 44 4
140 load 20 2 40 4
142 load 21 2 36 4
144 load 22 2 32 4
146 load 23 2 28 4
148 load 24 2 24 4
14a load 25 2 20 4
14c addi 2 2 64
14e jr 1
150 li 8 1
152 jump 288
''',
'''
000 addi 2 2 -64
002 store 2 8 56 4
004 store 2 1 60 4
006 store 2 9 52 4
008 store 2 18 48 4
00a store 2 19 44 4
00c store 2 20 40 4
00e store 2 21 36 4
010 store 2 22 32 4
012 store 2 23 28 4
014 store 2 24 24 4
016 store 2 25 20 4
018 li 8 2
01a beq 12 0 308
01e beq 14 0 308
022 mv 23 10
024 mv 18 14
026 mv 22 13
028 mv 21 12
02a mv 24 11
02c auipc 1 536547328
030 jalr 1 1 -1938
034 mv 20 10
036 li 8 20
038 beq 10 0 308
03c addi 11 0 83
040 li 10 16
042 auipc 1 536543232
046 jalr 1 1 -508
04a mv 19 10
04c li 8 19
04e beqz 10 308
050 load 9 18 1 1
054 load 15 18 2 1
058 slli 9 9 8
05a slli 15 15 16
05c add 9 9 15
05e load 15 18 0 1
062 add 9 9 15
064 load 15 18 3 1
068 slli 15 15 24
06a add 9 9 15
06c load 15 20 40 4
070 bltu 15 9 124
074 li 14 -1
076 li 8 2
078 bne 15 14 298
07c beq 24 0 138
080 load 15 20 4 1
084 li 8 1
086 andi 15 15 2
088 beqz 15 298
08a addi 25 22 4
08e li 12 8
090 li 11 0
092 mv 10 2
094 slli 25 25 16
096 auipc 1 536543232
09a jalr 1 1 268
09e srli 25 25 16
0a2 addi 11 0 83
0a6 mv 10 25
0a8 auipc 1 536543232
0ac jalr 1 1 -610
0b0 mv 24 10
0b2 li 8 19
0b4 beqz 10 298
0b6 mv 12 22
0b8 mv 11 21
0ba addi 10 10 4
0bc auipc 1 536543232
0c0 jalr 1 1 468
0c4 li 12 4
0c6 mv 11 18
0c8 mv 10 24
0ca auipc 1 536543232
0ce jalr 1 1 454
0d2 li 12 16
0d4 addi 11 20 24
0d8 mv 10 19
0da auipc 1 536543232
0de jalr 1 1 438
0e2 li 14 8
0e4 mv 13 2
0e6 mv 12 25
0e8 mv 11 24
0ea mv 10 19
0ec jal 1 336520
0f0 mv 8 10
0f2 bnez 10 288
0f4 li 12 8
0f6 mv 11 2
0f8 addi 10 2 8
0fa auipc 1 536543232
0fe jalr 1 1 406
102 li 12 8
104 addi 11 18 4
108 addi 10 2 8
10a auipc 1 536543232
10e jalr 1 1 318
112 li 15 1
114 bne 10 15 336
118 mv 11 9
11a mv 10 23
11c jal 1 287648
120 mv 10 24
122 auipc 1 536543232
126 jalr 1 1 -524
12a mv 10 19
12c auipc 1 536543232
130 jalr 1 1 -534
134 mv 10 8
136 load 1 2 60 4
138 load 8 2 56 4
13a load 9 2 52 4
13c load 18 2 48 4
13e load 19 2 44 4
140 load 20 2 40 4
142 load 21 2 36 4
144 load 22 2 32 4
146 load 23 2 28 4
148 load 24 2 24 4
14a load 25 2 20 4
14c addi 2 2 64
14e jr 1
150 li 8 1
152 jump 288
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'aux literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for off,f3 in TYPED_LOADS[index]:
  check(int.from_bytes(raw[off:off+4],'little')&0x707f==((f3<<12)|3),'aux typed load encoding')
 n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'aux complete instruction boundaries')
 for a,f in s.items():init.g(n,a,'aux operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(340,127,HASHES[index]),'aux complete identity')
 edges={};calls=[];returns=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'aux ordinary RET');returns.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'aux linked direct call');calls.append({'offset':a-pc,'target':d['target']})
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','aux adjacent linked provider pair')
   calls.append({'offset':a-pc,'target':(a-4+u['imm']+d['imm'])&0xfffffffe})
  check(all(b in n for b in q),'aux local CFG closed');edges[a]=q
 todo=[pc];seen=set()
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'aux complete reachable DAG')
 targets=[(0x30,0x20000a94),(0x46,0x20000040),(0x9a,0x2000039c),(0xac,0x20000040),
  (0xc0,0x2000048a),(0xce,0x2000048a),(0xde,0x2000048a),(0xec,(0x521e0,0x52288)[index]),
  (0xfe,0x2000048a),(0x10e,0x20000442),(0x11c,0x46308+152*index),(0x126,0x20000110),(0x130,0x20000110)]
 check(calls==[dict(offset=o,target=t) for o,t in targets],'aux complete call targets')
 stores=[{'offset':a-pc,'base':d['rs1'],'source':d['rs2'],'imm':d['imm'],'bytes':d['width']} for a,d in n.items() if d['op']=='store']
 check(len(stores)==11 and all(d['base']==2 and d['bytes']==4 for d in stores),'aux only direct stores are frame saves')
 check(returns==[pc+0x14e],'aux single normal RET')
 saves={(d['source'],d['imm']) for d in stores}
 restores={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}
 check(saves==restores=={(1,60),(8,56),(9,52),(18,48),(19,44),(20,40),(21,36),(22,32),(23,28),(24,24),(25,20)},'aux save/restore layout')
 return {'start':pc,'bytes':340,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'CFG':edges,
  'calls':calls,'tails':[],'returns':returns,'stores':stores,'complete_local_body':True,'target_execution_or_emulation':False}


def paths(b):
 # Immutable CFG selections only: branch outcomes are assumptions, not execution.
 initial={0x1a:0x1e,0x1e:0x22,0x38:0x3c,0x4e:0x50}
 eligible={**initial,0x70:0x7c,0x7c:0x80,0x88:0x8a,0xb4:0xb6}
 table={
  'null_P':{0x1a:0x134},
  'null_tail':{0x1a:0x1e,0x1e:0x134},
  'lookup_null':{0x1a:0x1e,0x1e:0x22,0x38:0x134},
  'first_alloc_null':{**initial,0x4e:0x134},
  'counter_reject':{**initial,0x70:0x74,0x78:0x12a},
  'mode_flag_reject_sentinel':{**initial,0x70:0x74,0x78:0x7c,0x7c:0x80,0x88:0x12a},
  'mode_flag_reject_strict_increase':{**initial,0x70:0x7c,0x7c:0x80,0x88:0x12a},
  'second_alloc_null':{**eligible,0xb4:0x12a},
  'core_nonzero':{**eligible,0xf2:0x120},
  'compare_not_one':{**eligible,0xf2:0xf4,0x114:0x150},
  'compare_one':{**eligible,0xf2:0xf4,0x114:0x118},
  'counter_sentinel_mode0':{**initial,0x70:0x74,0x78:0x7c,0x7c:0x8a,0xb4:0xb6,0xf2:0xf4,0x114:0x118},
  'counter_sentinel_mode1_flagset':{**initial,0x70:0x74,0x78:0x7c,0x7c:0x80,0x88:0x8a,0xb4:0xb6,0xf2:0xf4,0x114:0x118}}
 chosen={k:common.walk(b,v) for k,v in table.items()}
 frees=(0x126,0x130)
 check(all(all(o not in chosen[k] for o in frees) for k in ('null_P','null_tail','lookup_null','first_alloc_null')),'aux preallocation failures no releases')
 check(all(0x126 not in chosen[k] and 0x130 in chosen[k] for k in ('counter_reject','mode_flag_reject_sentinel','mode_flag_reject_strict_increase','second_alloc_null')),'aux one acquired temporary released on first-only failures')
 for k in ('core_nonzero','compare_not_one','compare_one'):
  seq=chosen[k];check(seq.index(0x126)<seq.index(0x130)<seq.index(0x14e),'aux acquired temporary cleanup order')
 check(0x11c in chosen['compare_one'] and 0x11c not in chosen['compare_not_one'] and 0x11c not in chosen['core_nonzero'],'aux counter update iff compare exactly1 on corezero path')
 allpaths=previous.v34.allocation.previous.dag_paths(b)
 check(all(0x130 in s for s in allpaths if 0x50 in s),'aux all post-first-allocation local exits contain firstrelease')
 check(all(0x126 in s and 0x130 in s for s in allpaths if 0xb6 in s),'aux all post-second-allocation local exits contain bothreleases')
 return {'selected':chosen,'syntactic_DAG_paths':len(allpaths),'allpaths_sha256':sha256(json.dumps(allpaths,separators=(',',':')).encode()).hexdigest(),
  'normal_call_returns_valid_memory_no_alias_and_preserved_S_registers_required':True,'actual_alloc_free_or_pointer_nonretention_proved':False}


def domains():
 # Pure unsigned scalar/extent equations, no target state or memory model.
 cases=0
 for L in range(13,65536):
  N=L-12;B=(N+4)&65535
  check(1<=N<=65523 and B==N+4 and 5<=B<=65527,'aux reachable second request cannot U16 wrap')
  check(4+N==B and N+12==L and (1+(L-13))==N,'aux copy/source/body/trailer intervals')
  for P in (0,1,0x20004000,0xfffffff0,0xffffffff):
   tail=(P+N)&0xffffffff
   check((tail+12)&0xffffffff==(P+L)&0xffffffff,'aux formal RV32 pointer extent equation')
  cases+=1
 check(((65532+4)&65535)==0,'aux generic length wrap outside current caller domain')
 # Counter guard is strict unsigned C>U, with U=FFFFFFFF a separate sentinel.
 probes=(0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff)
 rows=[]
 for U in probes:
  for C in probes:
   for mode in (0,1):
    for flag in (0,2):
     accepted=(U<C or U==0xffffffff) and (mode==0 or flag&2!=0)
     rejected=(U>=C and U!=0xffffffff) or (mode!=0 and flag&2==0)
     check(accepted!=rejected,'aux counter andmodeflag conjunction algebra')
     rows.append([U,C,mode,flag,accepted])
 check(not (0xffffffff<0) and 0x7fffffff<0x80000000,'aux unsigned order boundary')
 check(not ((0<1 or 0==0xffffffff) and (1==0 or 0&2!=0)),'aux strict increase still requires mode1flagbit1 regression')
 # Compare success is integer1, not C memcmp equal0 or arbitrary nonzero.
 check([r for r in (0,1,2,19,0xffffffff) if r==1]==[1],'aux comparison exact1 convention')
 check(not set(range(0,16))&set(range(20,64)),'aux borrowed SP0..15 avoids saved slots20..63')
 return {'reachable_extended_lengths':cases,'length_domain':[13,65535],'copied_N_domain':[1,65523],
  'second_request_domain':[5,65527],'generic_U16_wrap_not_reachable_from_this_decoder':True,
  'counter_boundary_cases':rows,'pointer_samples_per_length':5,'comparison_success_reply':1,
  'actual_buffer_extent_alias_or_provider_semantics_proved':False}


def profile(data,hexraw,index,parent):
 pc=STARTS[index];raw=init.binding.take(data,pc,SIZE);b=body(raw,index);n={v['pc']-pc:v for v in b['instructions']}
 check(parent['bodies']['decoder']['calls']==[{'offset':0x44,'target':pc}],'aux parent decoder call joins this complete body')
 check((n[0x3c]['imm'],n[0x40]['imm'],n[0xa2]['imm'])==(83,16,83),'aux both allocations tag83 firstrequest16')
 check((n[0x8a]['imm'],n[0x94]['imm'],n[0x9e]['imm'])==(4,16,16),'aux second request low16 N+4')
 check((n[0x50]['imm'],n[0x54]['imm'],n[0x5e]['imm'],n[0x64]['imm'])==(1,2,0,3),'aux LE32 counter source bytes')
 check(n[0x6c]['imm']==40 and n[0x80]['imm']==4 and n[0x86]['imm']==2,'aux object counter40/flag4bit1')
 check(n[0x120]['rs2']==24 and n[0x12a]['rs2']==19,'aux frees exact saved allocation results not borrowed P/tail')
 check(n[0xf0]['rs2']==10 and n[0x112]['imm']==1 and n[0x114]['op']=='bne','aux core scalar captured; compare1 success convention')
 check(n[0x118]['rs2']==9 and n[0x11a]['rs2']==23,'aux update passes originalID andcapturedtailcounter')
 check(n[0x134]['rs2']==8 and n[0x150]['rd']==8 and n[0x150]['imm']==1,'aux shared saved reply andlatecomparefailure1')
 _,mem=sparse.inspect(hexraw,sparse.parser());check(sparse.captured(mem,pc,SIZE)==raw,'aux all original bytes in strict HEX')
 return {'label':init.binding.PROFILES[index][0],'body':b,'HEX_capture_receipt':{'source':pc,'bytes':SIZE,'all_bytes_captured':True},
  'CFG_certificate':common.certificates(b),'paths':paths(b),'decoder_entry_contract':{'arguments':['freshU16 M2','1','P','L-12','(P+L-12)mod32'],'L_min':13,'L_max':65535},
  'normal_return_contract':[
   'P==0 or tail==0 ->2;lookup(ID) null ->20;first16B allocation null ->19; these paths do not locally release allocations',
   'captureLE32 tail[0..3]=C;freshU32 object40=U;require(C>U orU==FFFFFFFF),then independently ifmode!=0 requireobject4bit1. Counterreject2 orflagreject1 thenreleasefirst;actualdecoderpassesmode1',
   'fill8 bytes SP0; allocateB request low16(N+4),tag83. Null ->19 afterreleasefirst; otherwise copyN P->B+4,copy4 tail->B,copy16 object24->first',
   'core(first,B,low16(N+4),SP0,8),save full replyR. Rnonzero ->releaseB thenfirst andreturnR',
   'core0 ->copy8 SP0->SP8;compare(SP8,tail+4,8). Exactly1 ->update(originalID,C),return0;otherwise reply1;bothpaths releaseB thenfirst',
   'all direct stores are saved frame slots;payload/tail/object writes through called providers are not ruledout;borrowedP/tail/stack/key retention unresolved'],
  'decoder_status_join':'under normalpreservation: aux0 ->tuple.status1,decoderreply0;auxnonzero ->tuple.status2,decoderreplybit6. Aux19 doesNOTdirectlyproduce handlerR19.',
  'premises':'conditionalcandidateISA/code/providerbindings;validmemory/output extents;normalcalleereturns andS/SP/RA/savedframepreservation;noadversealias/IRQ/DMA/reentry;sourceidentity separatelyretained',
  'actual_installed_binding_core_semantics_or_lifetime_proved':False}


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 result=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return {'schema':'TSL9-task8-extended-aux-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':result,'domains':domains(),
  'complete_body_bytes':680,'complete_body_instructions':254,'C_reconstruction_coverage_changed':False,
  'remaining':['core521e0/52288, objectlookup andcounterupdate effects','copy/fill/compare actualbindings, temporary/key/stack retention','task8 callback body andotherwriters;installedprovider andcompletepayloadlifetime'],
  'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE)
  for a,v in decode(raw,STARTS[i]).items():
   off=a-STARTS[i];z=v['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('aux instruction mutation escaped')
   mutations+=1
  for off,_ in TYPED_LOADS[i]:
   bad=bytearray(raw);bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError as ex:check('typed load encoding' in str(ex),'aux typed mutation guard')
   else:raise RuntimeError('aux typed mutation escaped')
   typed+=1
 check((mutations,typed)==(254,12),'aux mutation census');domains()
 print('PASS:254 instruction/12 typed-load mutations rejected;65523 reachable lengths,327615 pointer equations,counter/compare/frame domains')


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
 else:check(OUT.read_bytes()==encoded,'aux exact ledger replay')
 print('PASS:680B/254i complete extended-payload auxiliary;strict HEX;conditional allocation/cleanup anddecoderstatus joins;exact ledger')
 print('PASS:NO target execution/emulation;actualbindings,core semantics andpointer nonretention UNPROVED')


if __name__=='__main__':main()
