"""Offline complete configuration helper and attempt A1=0 composition.
Original operands/immutable CFGs and host scalar identities only.
No target execution/emulation, hardware or mutable target-state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_sampler_inner_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-frequency-static.json')
STARTS=(0x6434a,0x64434)
SIZE=192
HASHES=('23620ed6e4e6e40bdf34963a5dd72c630772313ca4444f5f56093450ef9874a0', 'dcc33412da10d5f6dc9e8a7481215f47ee0144d665029321285f626494c37c34')
COUNTS=(66, 66)
TYPED=(((8, 2), (20, 2), (136, 4)), ((8, 2), (20, 2), (136, 4)))
QK=(((24, '1c32', 'qk.c.lbu'),), ((24, '1c32', 'qk.c.lbu'),))
LITERALS=(
'''
000 lui 15 536883200
004 lui 10 536883200
008 load 14 15 1424 4
00c addi 12 10 1344
010 lui 15 536883200
014 load 13 15 1288 4
018 load 15 12 1 1
01a andi 16 15 127
01e beqz 11 172
020 load 15 12 4 4
022 load 12 13 0 4
024 andi 12 12 -128
028 or 12 12 16
02c store 13 12 0 4
02e andi 12 11 1
032 beqz 12 66
034 andi 11 11 48
038 li 12 16
03a beq 11 12 166
03e addi 15 15 -1000
042 load 12 14 44 4
044 lui 16 65536
046 addi 16 16 -1536
04a ori 12 12 2
04e store 14 12 44 4
050 divu 12 15 16
054 lui 17 4262461440
058 addi 17 17 -1
05a remu 15 15 16
05e andi 12 12 31
060 slli 11 12 20
064 load 12 14 68 4
066 and 12 12 17
06a or 12 12 11
06c store 14 12 68 4
06e addi 12 0 250
072 lui 11 4294705152
076 slli 15 15 10
078 divu 15 15 12
07c load 12 14 68 4
07e and 12 12 11
080 slli 15 15 14
082 srli 15 15 14
084 or 15 15 12
086 store 14 15 68 4
088 load 15 10 1344 1
08c andi 15 15 2
08e beqz 15 164
090 load 15 13 0 4
092 andi 15 15 127
096 ori 14 15 64
09a load 15 13 0 4
09c andi 15 15 -128
0a0 or 15 15 14
0a2 store 13 15 0 4
0a4 jr 1
0a6 addi 15 15 -2000
0aa jump 66
0ac load 15 14 44 4
0ae andi 15 15 -3
0b0 store 14 15 44 4
0b2 load 15 13 0 4
0b4 andi 15 15 -128
0b8 or 15 15 16
0bc store 13 15 0 4
0be jump 136
''',
'''
000 lui 15 536883200
004 lui 10 536883200
008 load 14 15 1504 4
00c addi 12 10 1424
010 lui 15 536883200
014 load 13 15 1368 4
018 load 15 12 1 1
01a andi 16 15 127
01e beqz 11 172
020 load 15 12 4 4
022 load 12 13 0 4
024 andi 12 12 -128
028 or 12 12 16
02c store 13 12 0 4
02e andi 12 11 1
032 beqz 12 66
034 andi 11 11 48
038 li 12 16
03a beq 11 12 166
03e addi 15 15 -1000
042 load 12 14 44 4
044 lui 16 65536
046 addi 16 16 -1536
04a ori 12 12 2
04e store 14 12 44 4
050 divu 12 15 16
054 lui 17 4262461440
058 addi 17 17 -1
05a remu 15 15 16
05e andi 12 12 31
060 slli 11 12 20
064 load 12 14 68 4
066 and 12 12 17
06a or 12 12 11
06c store 14 12 68 4
06e addi 12 0 250
072 lui 11 4294705152
076 slli 15 15 10
078 divu 15 15 12
07c load 12 14 68 4
07e and 12 12 11
080 slli 15 15 14
082 srli 15 15 14
084 or 15 15 12
086 store 14 15 68 4
088 load 15 10 1424 1
08c andi 15 15 2
08e beqz 15 164
090 load 15 13 0 4
092 andi 15 15 127
096 ori 14 15 64
09a load 15 13 0 4
09c andi 15 15 -128
0a0 or 15 15 14
0a2 store 13 15 0 4
0a4 jr 1
0a6 addi 15 15 -2000
0aa jump 66
0ac load 15 14 44 4
0ae andi 15 15 -3
0b0 store 14 15 44 4
0b2 load 15 13 0 4
0b4 andi 15 15 -128
0b8 or 15 15 16
0bc store 13 15 0 4
0be jump 136
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'controlconfig literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'controlconfig fullboundaries')
 for a,f in s.items():init.g(n,a,'controlconfig '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'controlconfig typedload')
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'controlconfig QKraw/width')
 for o,mask in ((0x50,0x02005033),(0x5a,0x02007033),(0x78,0x02005033)):check(int.from_bytes(raw[o:o+4],'little')&0xfe00707f==mask,'controlconfig DIVU/REMU exactmode')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'controlconfig fullidentity')
 e={};rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'controlconfig RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  check(op not in ('jal','jalr','call_indirect') and all(z in n for z in q),'controlconfig closed/no calls');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and common.acyclic(e) and rets==[pc+0xa4],'controlconfig completeDAG/soleRET')
 writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
 check(writes==list(range(10,18)) and [a-pc for a,d in n.items() if d.get('rd')==10]==[4],'controlconfig fixedA0/GPR envelope')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 check(stores==[(0x2c,13,12,0,4),(0x4e,14,12,44,4),(0x6c,14,12,68,4),(0x86,14,15,68,4),(0xa2,13,15,0,4),(0xb0,14,15,44,4),(0xbc,13,15,0,4)],'controlconfig all7wordstores/no frame')
 return dict(start=pc,bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=[],returns=rets,tails=[],stores=stores,encoded_GPR_writes=writes,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 out={}
 for mode in ('zero','even_nonzero','odd_minus1000','odd_minus2000'):
  for flag in (0,1):
   c={0x1e:0xac if mode=='zero' else 0x20,0x32:0x42 if mode=='even_nonzero' else 0x34,0x3a:0xa6 if mode=='odd_minus2000' else 0x3e,0x8e:0x90 if flag else 0xa4}
   seq=common.walk(b,c);out[mode+'_terminalflag'+str(flag)]=seq
   check((0xa2 in seq)==bool(flag) and seq[-1]==0xa4,'controlconfig terminaloption/RET')
   check(all((o in seq)==(mode!='zero') for o in (0x20,0x2c,0x4e,0x50,0x5a,0x6c,0x78,0x86)),'controlconfig zero bypassesF4/arithmetic/word68')
   if mode=='zero':check(0xb0 in seq and 0xbc in seq and seq.index(0xb0)<seq.index(0xbc)<seq.index(0x88),'controlconfig clearbit1 thenlow7 thenfreshflag')
   else:check(seq.index(0x6c)<seq.index(0x7c)<seq.index(0x86),'controlconfig twoindependentfreshword68 observations')
   if flag:check(seq.index(0x90)<seq.index(0x9a)<seq.index(0xa2),'controlconfig terminaltwofreshR0 ordering')
 return out


def domains():
 classes=[0]*4
 for a1 in range(65536):
  k=0 if a1==0 else 1 if not a1&1 else 3 if a1&48==16 else 2;classes[k]+=1
 check(classes==[1,32767,24576,8192] and 0x100!=0 and not(0x100&1),'controlconfig fullA1 classification/lowbytezero notzeromode')
 for remainder in range(64000):
  scaled=remainder<<10;fraction=scaled//250
  check(scaled<2**32 and 0<=fraction<=262139 and fraction&0x3ffff==fraction,'controlconfig remainder scale fitsU32/18bits')
 check(63999*1024//250==262139 and 0xffffffff//64000==67108,'controlconfig maximalfraction/quotient')
 for quotient in range(67109):check((quotient&31)<<20 & ~0x01f00000==0,'controlconfig quotientfield truncation')
 for x in (0,1,999,1000,1999,2000,64000,0x7fffffff,0xffffffff):
  for adjustment in (0,1000,2000):
   v=(x-adjustment)&0xffffffff;q,r=divmod(v,64000)
   check(v==q*64000+r and 0<=r<64000 and v==(x-adjustment)%2**32,'controlconfig unsignedunderflow/not saturation')
 for low in range(128):
  for highbyte in range(256):
   second=highbyte<<24;word=(second&0xffffff80)|(low|64)
   check(word&127==low|64 and word>>24==highbyte,'controlconfig independentterminal low/high observations')
 return dict(fullA1_low16_cases=65536,A1_partition=classes,remainder_cases=64000,quotient_cases=67109,terminal_low7_highbyte_cases=32768,
  arithmetic='X=freshF4 fornonzeroevenA1;oddA1 low32(X-2000) if(A1&48)==16 else low32(X-1000);q=X//64000,r=X%64000;fieldQ=(q&31)<<20,fieldF=(r<<10)//250',
  normal_reply=0x20003000,entry_A0_A2_ignored=True,attempt_A1_zero_skips_all_DIVU_REMU_and_word68=True,target_execution_or_emulation=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE)
 check(sparse.captured(mem,STARTS[index],SIZE)==raw,'controlconfig strictoriginalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;F=G+1344+80*index;Dslot=G+1424+80*index;Rslot=G+1288+80*index
 check(n[0]['imm']+n[8]['imm']==Dslot and n[0x10]['imm']+n[0x14]['imm']==Rslot and n[4]['imm']+n[0xc]['imm']==F and n[4]['imm']+n[0x88]['imm']==F and n[4]['imm']==G,'controlconfig fixedglobals/reply')
 check(n[0x44]['imm']+n[0x46]['imm']==64000 and n[0x6e]['imm']==250 and (n[0x54]['imm']+n[0x58]['imm'])&0xffffffff==0xfe0fffff and n[0x72]['imm']==0xfffc0000,'controlconfig positive divisors/masks')
 check(n[0x3e]['imm']==-1000 and n[0xa6]['imm']==-2000 and n[0x18]['imm']==1 and n[0x1a]['imm']==127 and n[0x8c]['imm']==2 and n[0x96]['imm']==64,'controlconfig branch/low7 constants')
 attempt=previous.previous.previous
 callerraw=init.binding.take(data,attempt.STARTS[index],502);caller=attempt.body(callerraw,index)
 check(sparse.captured(mem,attempt.STARTS[index],502)==callerraw and next(c['target'] for c in caller['calls'] if c['offset']==0x76)==b['start'],'controlconfig exactattemptcall join')
 cn={d['pc']-caller['start']:d for d in caller['instructions']}
 check(cn[0x62]['op']=='li' and cn[0x62]['rd']==11 and cn[0x62]['imm']==0 and not any(d.get('rd')==11 for o,d in cn.items() if 0x62<o<0x76) and cn[0x70]['rd']==10,'controlconfig attempt explicitA1zero nointermediateclobber')
 check([o for o,d in n.items() if d.get('rd')==12][0]==0xc and n[0xc]['rs1']==10 and [o for o,d in n.items() if d.get('rd')==10]==[4],'controlconfig entryA0/A2 overwrittenbeforeuse')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),reused_attempt=dict(start=caller['start'],bytes=502,new_code_bytes_counted=0),
  nominal_globals=dict(config=F,D_pointer_slot=Dslot,R_pointer_slot=Rslot),
  contract=['capturefreshD fromDslot,freshR fromRslot,freshU8F1low7;no nullguards,noD/Rreload,noentryA0/A2use;onlyA1entryargumentused;allordinarypaths returnfixedG20003000',
   'fullA1zero:SW(freshD44&FFFFFFFD)D44;SW((freshR0&FFFFFF80)|sampledF1low7)R0;noF4read,divisionorword68write',
   'nonzeroA1:capturesfreshF4 X;writesR0low7. EvenA1 keepsX;oddA1subtracts2000if(A1&30hex)==10hex,else1000,low32. FreshD44OR2 ->D44',
   'q=Xunsigned//64000,r=Xunsigned%64000;firstfreshD68 AND FE0FFFFF OR((q&31)<<20),thenindependentlyfreshD68 AND FFFC0000 OR(((r<<10)//250)&3FFFF);notcoherent/atomicpair',
   'commonfreshF0bit1clear ->RET;set ->firstfreshR0low7 OR40,secondfreshR0upper25bits,combineSW R0;not assumedtoequalsampledF1/noatomicity',
   'attempt+76 explicitlyA1=0 (A0freshF1ignored):zero pathapplies regardlessentryA0,thenfixedreplyG;caller lateroverwritesA0beforeitsclock/channeluses. No physicalfrequency/registersuccessmeaning'],
  premises='candidateISA/API/installedcode;validcode/global/Dextent72/Rextent4;ordinaryaccesscompletion;no adversealias/wrap/IRQ/DMA/reentry/externalwriters;freshread equalities separate',
  actual_provider_binding_hardware_effects_atomicity_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-control-config-attemptzero-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=384,complete_phase_body_instructions=132,reused_attempt_bytes=1004,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['63b0e/63bf8 finalchannel helper andcallback65de6/65ed0','config/mask/divisor/K writers andactualconstraints','actualinstalledproviders/hardwareeffects/pollprogress/fullpointerlifetimes'])


def tests(carriers):
 mutations=typed=arithmetic=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('controlconfig instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('controlconfig typedmutation escaped')
   typed+=1
  for o in (0x50,0x5a,0x78):
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<12)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('controlconfig arithmeticmode mutation escaped')
   arithmetic+=1
 check((mutations,typed,arithmetic)==(132,6,6),'controlconfig mutationcensus')
 print('PASS:132 instruction/6 typed-load/6 arithmetic-mode mutations rejected;complete CFG/store/GPR/attemptzero certificates')


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
 else:check(OUT.read_bytes()==encoded,'controlconfig exactledger replay')
 print('PASS:384B/132i complete controlconfig;strictHEX;65536 A1/64000 remainder/67109 quotient cases;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/hardware/atomicity/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
