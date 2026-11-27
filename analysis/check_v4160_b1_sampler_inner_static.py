"""Offline sampler inner bit-selector: original operands/CFG and scalar proofs.
No target execution/emulation, mutable target state or hardware access.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_sampler_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,BRANCHES=previous.common,previous.BRANCHES
FIELDS={**previous.FIELDS,'remu':('rd','rs1','rs2')}
OUT=Path(__file__).with_name('v4160-b1-sampler-inner-static.json')
STARTS=(0x20002c50,0x20002c9c)
SOURCES=(0x42ec0,0x42f4c)
SIZE=88
HASHES=('14ce0fb3ca71083c6b052c82dd4469a6f263764d43bdd8f188d1f91b8b6fd12d', '739db76bad830b2f6020202860976cb28fcc6652b66f7978d887a3820de8b818')
COUNTS=(31, 31)
TYPED=((), ())
QK=(((16, '5c37', 'qk.c.lbu'), (18, '2c3e', 'qk.c.lbu'), (30, '1cb2', 'qk.c.sb'), (32, '5cb7', 'qk.c.sb'), (38, '183b', 'qk.c.lbu')), ((16, '5c37', 'qk.c.lbu'), (18, '2c3e', 'qk.c.lbu'), (30, '1cb2', 'qk.c.sb'), (32, '5cb7', 'qk.c.sb'), (38, '183b', 'qk.c.lbu')))
LITERALS=(
'''
000 lui 14 536883200
004 lui 13 536883200
008 addi 12 13 1344
00c addi 14 14 1376
010 load 15 14 13 1
012 load 11 12 27 1
014 load 10 12 20 4
016 add 15 15 11
018 andi 15 15 31
01a srl 11 10 15
01e store 12 15 1 1
020 store 14 15 13 1
022 andi 11 11 1
024 bnez 11 86
026 load 14 14 17 1
028 li 13 0
02a addi 16 0 32
02e remu 15 15 14
032 li 14 0
034 srl 11 10 14
038 andi 11 11 1
03a andi 17 14 255
03e beqz 11 80
040 bne 15 13 74
044 store 12 17 1 1
048 jr 1
04a addi 13 13 1
04c andi 13 13 255
050 addi 14 14 1
052 bne 14 16 52
056 jr 1
''',
'''
000 lui 14 536883200
004 lui 13 536883200
008 addi 12 13 1424
00c addi 14 14 1456
010 load 15 14 13 1
012 load 11 12 27 1
014 load 10 12 20 4
016 add 15 15 11
018 andi 15 15 31
01a srl 11 10 15
01e store 12 15 1 1
020 store 14 15 13 1
022 andi 11 11 1
024 bnez 11 86
026 load 14 14 17 1
028 li 13 0
02a addi 16 0 32
02e remu 15 15 14
032 li 14 0
034 srl 11 10 14
038 andi 11 11 1
03a andi 17 14 255
03e beqz 11 80
040 bne 15 13 74
044 store 12 17 1 1
048 jr 1
04a addi 13 13 1
04c andi 13 13 255
050 addi 14 14 1
052 bne 14 16 52
056 jr 1
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'innerselector literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'innerselector fullboundaries')
 for a,f in s.items():init.g(n,a,'innerselector '+hex(a-pc),**f)
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'innerselector QK raw/width')
 check(int.from_bytes(raw[0x2e:0x32],'little')&0xfe00707f==0x02007033,'innerselector unsignedREMU encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'innerselector fullidentity')
 e={};rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'innerselector RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  check(op not in ('jal','jalr','call_indirect') and all(z in n for z in q),'innerselector closed/no calls');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 cut={a:[z for z in qs if (a-pc,z-pc)!=(0x52,0x34)] for a,qs in e.items()}
 check(seen==set(n) and not common.acyclic(e) and common.acyclic(cut) and rets==[pc+0x48,pc+0x56],'innerselector completeCFG/onecyclecut/twoRET')
 writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
 check(writes==list(range(10,18)) and [a-pc for a,d in n.items() if d.get('rd')==10]==[0x14],'innerselector onlyAregisters/capturedmask reply')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==[(0x1e,12,15,1,1),(0x20,14,15,13,1),(0x44,12,17,1,1)],'innerselector all3bytestores/no frame')
 check([a-pc for a,d in n.items() if d.get('rd')==14]==[0,0xc,0x26,0x32,0x50] and [a-pc for a,d in n.items() if d.get('rd')==13]==[4,0x28,0x4a,0x4c],'innerselector index/ordinal soledefinitions')
 return dict(start=pc,source=SOURCES[index],bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=[],returns=rets,tails=[],stores=stores,encoded_GPR_writes=writes,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 choices={'candidate_bit_set':{0x24:0x56},'first_bit_ordinal_match':{0x24:0x26,0x3e:0x40,0x40:0x44},
  'one_zero_bit_template':{0x24:0x26,0x3e:0x50,0x52:0x56},'one_setbit_mismatch_template':{0x24:0x26,0x3e:0x40,0x40:0x4a,0x52:0x56}}
 out={name:common.walk(b,c) for name,c in choices.items()}
 # Expand only the immutable CFG sequence; no target registers or memory model.
 for name in ('one_zero_bit_template','one_setbit_mismatch_template'):
  seq=out[name];a=seq.index(0x34);z=seq.index(0x52);expanded=seq[:a]+seq[a:z+1]*32+seq[z+1:]
  e=b['CFG'];pc=b['start'];check(all(pc+q in e[pc+p] for p,q in zip(expanded,expanded[1:])) and expanded.count(0x34)==32,'innerselector 32iteration syntacticwitness')
  out[name.replace('one_','32_')]=expanded
 for name,seq in out.items():
  check(seq.index(0x1e)<seq.index(0x20)<seq.index(0x24) and seq[-1] in (0x48,0x56),'innerselector initialstores before test/RET')
  check((0x44 in seq)==(name=='first_bit_ordinal_match'),'innerselector optionalF1only replacement')
 return out


def domains():
 # Declarative bitstring ranks and arithmetic certificates; no target scan runner.
 pairs=0
 for low in range(65536):
  mask=low|(low<<16);bits=tuple(i for i in range(32) if mask&(1<<i));count=len(bits)
  for j in range(32):
   pairs+=1
   if count:
    rank=j%count;selected=j if mask&(1<<j) else bits[rank]
    check(0<=selected<32 and bool(mask&(1<<selected)) and len(bits[:rank])==rank,'innerselector nonzero popcount-divisor closedform')
   else:check(mask==0 and not bits,'innerselector emptymask no candidate/rankmatch')
 check(pairs==2097152,'innerselector bitstring paircensus')
 for j in range(32):
  for divisor in range(256):
   rank=j if divisor==0 else j%divisor
   check(0<=rank<=j<32 and (divisor or rank==j),'innerselector REMUzero edge/rankbounds')
 for old in range(256):
  for step in range(256):check((old+step)&31==((old&31)+(step&31))%32,'innerselector freshbyte proposal modulo32')
 for count in range(33):
  for index in range(33):check(index<=32 and count<=32 and (index&255)==index and (count&255)==count,'innerselector boundedindex/ordinal no8bitwrap')
 check((2%2)==0 and (1,7)[2%2]==1 and not(0x82&(1<<2)),'innerselector replacement !=storedproposal witness')
 check(2>=len((1,7)) and 0x82==((1<<1)|(1<<7)),'innerselector REMUzero unavailable-rank witness')
 return dict(bitstring_families=65536,candidate_bit_pairs=pairs,freshbyte_proposal_pairs=65536,j_divisor_pairs=8192,
  closedform='capturedmask setbit list L;J=(freshC13+freshF27)&31. IfbitJset,outputJ;elseR=J%d fornonzero freshC17,orJford0;R<lenL ->L[R],elseJ. A0=capturedmask',
  stable_positive_popcount_divisor='ifC17==popcount(capturedmask)>0,selectedF1 isasetbit;notassumedbycode',
  scan_bound=32,scan_shift_indices=[0,31],C13_always_proposedJ=True,F1_maydiffer_from_C13=True,unavailable_rank_leaves_unset_candidate_possible=True,
  target_execution_or_emulation=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,SOURCES[index],SIZE)
 check(sparse.captured(mem,SOURCES[index],SIZE)==raw,'innerselector strictoriginalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 F=0x20003540+80*index;C=F+32
 check(n[4]['imm']+n[8]['imm']==F and n[0]['imm']+n[0xc]['imm']==C and n[0x10]['imm']==13 and n[0x12]['imm']==27 and n[0x14]['imm']==20 and n[0x26]['imm']==17,'innerselector allfixedread origins')
 check(n[0x18]['imm']==31 and n[0x2a]['imm']==32 and n[0x50]['imm']==1 and n[0x4a]['imm']==1 and n[0x4c]['imm']==255 and n[0x32]['imm']==n[0x28]['imm']==0,'innerselector finite32scan anchors')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];pc=STARTS[index]
 check(int(first['source'],16)+pc-int(first['destination'],16)==SOURCES[index] and int(first['destination'],16)<=pc and pc+SIZE<=int(mapping['first_copy_end_exclusive'],16),'innerselector completefirstcopy mapping')
 samplerraw=init.binding.take(data,previous.SOURCES[index],166);sampler=previous.body(samplerraw,index)
 check(sparse.captured(mem,previous.SOURCES[index],166)==samplerraw and sampler['calls'][1]['target']==pc,'innerselector samplerlinkedcall exactjoin')
 sn={d['pc']-sampler['start']:d for d in sampler['instructions']}
 writes={F+1,C+13};protected=set(range(C+8,C+12))|{F+26,F+27,C+17}|set(range(F+20,F+24))
 check(writes.isdisjoint(protected),'innerselector fixedbytestores excludeK/baseline/mask/step/divisor')
 check(sn[0x54]['target']==pc and sn[0x56]['rs1']==18 and sn[0x56]['imm']==26 and sn[0x5a]['imm']==8 and sn[0x68]['rd']==8 and sn[0x40]['rd']==20 and 8 not in b['encoded_GPR_writes'] and 20 not in b['encoded_GPR_writes'],'innerselector postcallreload andq/r preservation')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),
  RAM_mapping=dict(source=SOURCES[index],entry=pc,bytes=SIZE,candidate_first_copy=first,actual_copy_proved=False),
  reused_sampler=dict(start=sampler['start'],bytes=166,new_code_bytes_counted=0),fixed_write_bytes=sorted(writes),protected_sampler_bytes=sorted(protected),
  contract=['freshC13 thenfreshF27 thencapturedU32F20 mask;J=low5(C13+F27);storebyteJtoF1 thenC13 BEFOREtestingcapturedmaskbitJ;setbit ->RETwithoutC17read',
   'unsetbit ->freshU8C17 divisor;RV32unsignedREMU:rankJ%divisor,divisor0 ->J. Scanheldmaskbit0..31 withordinalofsetbits;match ->SBindexF1,RET;exhaustionRETleavesproposedJ',
   'only3byte store sites F1,C13,F1;fallbackreplacement neverrewritesC13;no calls/frame/S/SP/RA writes;allordinarypaths <=32 probes,A0=capturedmask,not selectedindex/status',
   'entryA0/A1/A2notinputs:alloperand originsfixed globals orlocalarithmetic. Capturedmask notrereadinside scan. No claimC17==popcountmask',
   'underconditionalmapping/noalias/load-storecompletion,fullknownleaf locally finiteandpreservesS0q/S4r/SP/RA;encodedwritesexcludeF26K andC8baselineword. Thusknowncallee removesopaqueSclobber/Kwriter frontier',
   'samplerreloadsK/baseline AFTERleaf;externalwriters/IRQ/DMA/hardwarealias canstillchange them. LeafdoesnotestablishKpositive orwhole samplertermination. K0 nonprogress caveat remains'],
  premises='candidateISAinclRV32REMUzeroandfirstcopy/installedleaf;validfixedcode/globalaccesses andordinarymemorycompletion;no adversephysicalalias/IRQ/DMA/reentry/externalwriters;freshsnapshot equalityseparate',
  actual_installation_maskcount_invariant_hardwareeffects_samplerprogress_or_fullpointerlifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-sampler-inner-bitselector-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=176,complete_phase_body_instructions=62,reused_sampler_bytes=332,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['C17 divisor/C13/F27/maskF20 writers andactualKsource/invariants','6434a/64434,63b0e/63bf8 andcallback65de6/65ed0','actualinstalledproviders/externalwriters/wholepollprogress andfullpointerlifetimes'])


def tests(carriers):
 mutations=remu=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('innerselector instructionmutation escaped')
   mutations+=1
  bad=bytearray(raw);bad[0x2e:0x32]=(int.from_bytes(bad[0x2e:0x32],'little')^(1<<12)).to_bytes(4,'little')
  try:body(bad,i)
  except RuntimeError:pass
  else:raise RuntimeError('innerselector REMUmode mutation escaped')
  remu+=1
 check((mutations,remu)==(62,2),'innerselector mutationcensus')
 print('PASS:62 instruction/2 REMU-mode mutations rejected;complete CFG/store/GPR andsampler preservation certificates')


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
 else:check(OUT.read_bytes()==encoded,'innerselector exactledger replay')
 print('PASS:176B/62i mappedselector;strictHEX;2097152 bitpairs/65536 bytepairs/8192 ranks;sampler joins;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/divisorinvariant/wholepollprogress/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
