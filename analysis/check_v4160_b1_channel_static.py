"""Offline complete channel leaf and attempt128 parameter/reply composition.
Original operands/immutable CFGs and host scalar/interval certificates only.
No target execution/emulation, hardware or mutable target-state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_frequency_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-channel-static.json')
STARTS=(0x63b0e,0x63bf8)
SIZE=326
HASHES=('9eb540eac7550b6a7e1c4e5ba63af04285e869cc1ae810b05571ec1422f4a61c', 'c5ba7949b7bb9d3631a2e5a9913d1d87d45a0934127de3e13c31bcf4ba3f6ac9')
COUNTS=(124, 124)
TYPED=(((4, 2), (48, 2), (54, 2), (88, 2), (136, 2), (200, 2), (252, 2), (302, 2)), ((4, 2), (48, 2), (54, 2), (88, 2), (136, 2), (200, 2), (252, 2), (302, 2)))
QK=(((52, '3826', 'qk.c.lbu'), (102, '5ca2', 'qk.c.sb'), (216, '54a2', 'qk.c.sb'), (268, '54a2', 'qk.c.sb'), (316, '54a2', 'qk.c.sb')), ((52, '3826', 'qk.c.lbu'), (102, '5ca2', 'qk.c.sb'), (216, '54a2', 'qk.c.sb'), (268, '54a2', 'qk.c.sb'), (316, '54a2', 'qk.c.sb')))
LITERALS=(
'''
000 lui 15 536883200
004 load 15 15 1292 4
008 beqz 15 30
00a load 13 15 16 4
00c load 12 15 20 4
00e load 14 13 0 4
010 or 14 14 12
012 store 13 14 0 4
014 load 13 15 0 4
016 load 15 15 8 4
018 load 14 13 0 4
01a or 15 15 14
01c store 13 15 0 4
01e lui 12 536883200
022 lui 15 536883200
026 addi 12 12 1300
02a lui 16 536883200
02e li 17 1
030 load 15 15 1288 4
034 load 14 12 10 1
036 load 13 16 1340 4
03a bne 10 17 122
03e load 10 15 0 4
040 lui 17 4294955008
042 addi 17 17 -1
044 and 10 10 17
048 store 15 10 0 4
04a load 10 13 12 4
04c lui 15 4294959104
04e addi 15 15 -1
050 and 15 15 10
052 store 13 15 12 4
054 nop 
056 nop 
058 load 13 16 1340 4
05c lui 15 8192
05e addi 11 11 11
060 store 13 15 8 4
062 addi 15 0 -128
066 store 12 15 4 1
068 slli 15 11 2
06c addi 11 14 158
070 add 11 11 15
072 slli 11 11 1
074 store 13 11 100 4
076 store 13 10 12 4
078 jr 1
07a lui 17 4294955008
07c andi 28 10 2
080 addi 6 17 -1
084 beq 28 0 274
088 load 17 15 0 4
08c addi 11 11 2
08e li 28 3
090 and 17 17 6
094 lui 6 8192
096 or 17 17 6
09a store 15 17 0 4
09e lui 17 4294918144
0a0 addi 14 14 190
0a4 slli 11 11 3
0a6 addi 17 17 -1
0a8 bne 10 28 230
0ac load 10 15 0 4
0ae and 10 10 17
0b2 lui 17 16384
0b4 or 10 10 17
0b8 store 15 10 0 4
0ba load 10 13 12 4
0bc lui 15 4294959104
0be addi 15 15 -1
0c0 and 15 15 10
0c2 store 13 15 12 4
0c4 nop 
0c6 nop 
0c8 load 15 16 1340 4
0cc addi 13 0 -128
0d0 addi 11 11 215
0d4 store 15 6 8 4
0d8 store 12 13 4 1
0da slli 11 11 1
0dc add 11 11 14
0de slli 11 11 1
0e0 store 15 11 100 4
0e2 store 15 10 12 4
0e4 jr 1
0e6 load 10 15 0 4
0e8 and 10 10 17
0ec store 15 10 0 4
0ee load 10 13 12 4
0f0 lui 15 4294959104
0f2 addi 15 15 -1
0f4 and 15 15 10
0f6 store 13 15 12 4
0f8 nop 
0fa nop 
0fc load 15 16 1340 4
100 addi 13 0 -128
104 addi 11 11 74
108 store 15 6 8 4
10c store 12 13 4 1
10e slli 11 11 3
110 jump 220
112 load 10 15 0 4
114 lui 17 4096
116 and 10 10 6
11a or 10 10 17
11e store 15 10 0 4
120 load 10 13 12 4
122 lui 15 4294959104
124 addi 15 15 -1
126 and 15 15 10
128 store 13 15 12 4
12a nop 
12c nop 
12e load 15 16 1340 4
132 lui 13 8192
134 addi 11 11 10
136 store 15 13 8 4
138 addi 13 0 -128
13c store 12 13 4 1
13e slli 11 11 3
140 addi 14 14 158
144 jump 220
''',
'''
000 lui 15 536883200
004 load 15 15 1372 4
008 beqz 15 30
00a load 13 15 16 4
00c load 12 15 20 4
00e load 14 13 0 4
010 or 14 14 12
012 store 13 14 0 4
014 load 13 15 0 4
016 load 15 15 8 4
018 load 14 13 0 4
01a or 15 15 14
01c store 13 15 0 4
01e lui 12 536883200
022 lui 15 536883200
026 addi 12 12 1380
02a lui 16 536883200
02e li 17 1
030 load 15 15 1368 4
034 load 14 12 10 1
036 load 13 16 1420 4
03a bne 10 17 122
03e load 10 15 0 4
040 lui 17 4294955008
042 addi 17 17 -1
044 and 10 10 17
048 store 15 10 0 4
04a load 10 13 12 4
04c lui 15 4294959104
04e addi 15 15 -1
050 and 15 15 10
052 store 13 15 12 4
054 nop 
056 nop 
058 load 13 16 1420 4
05c lui 15 8192
05e addi 11 11 11
060 store 13 15 8 4
062 addi 15 0 -128
066 store 12 15 4 1
068 slli 15 11 2
06c addi 11 14 158
070 add 11 11 15
072 slli 11 11 1
074 store 13 11 100 4
076 store 13 10 12 4
078 jr 1
07a lui 17 4294955008
07c andi 28 10 2
080 addi 6 17 -1
084 beq 28 0 274
088 load 17 15 0 4
08c addi 11 11 2
08e li 28 3
090 and 17 17 6
094 lui 6 8192
096 or 17 17 6
09a store 15 17 0 4
09e lui 17 4294918144
0a0 addi 14 14 190
0a4 slli 11 11 3
0a6 addi 17 17 -1
0a8 bne 10 28 230
0ac load 10 15 0 4
0ae and 10 10 17
0b2 lui 17 16384
0b4 or 10 10 17
0b8 store 15 10 0 4
0ba load 10 13 12 4
0bc lui 15 4294959104
0be addi 15 15 -1
0c0 and 15 15 10
0c2 store 13 15 12 4
0c4 nop 
0c6 nop 
0c8 load 15 16 1420 4
0cc addi 13 0 -128
0d0 addi 11 11 215
0d4 store 15 6 8 4
0d8 store 12 13 4 1
0da slli 11 11 1
0dc add 11 11 14
0de slli 11 11 1
0e0 store 15 11 100 4
0e2 store 15 10 12 4
0e4 jr 1
0e6 load 10 15 0 4
0e8 and 10 10 17
0ec store 15 10 0 4
0ee load 10 13 12 4
0f0 lui 15 4294959104
0f2 addi 15 15 -1
0f4 and 15 15 10
0f6 store 13 15 12 4
0f8 nop 
0fa nop 
0fc load 15 16 1420 4
100 addi 13 0 -128
104 addi 11 11 74
108 store 15 6 8 4
10c store 12 13 4 1
10e slli 11 11 3
110 jump 220
112 load 10 15 0 4
114 lui 17 4096
116 and 10 10 6
11a or 10 10 17
11e store 15 10 0 4
120 load 10 13 12 4
122 lui 15 4294959104
124 addi 15 15 -1
126 and 15 15 10
128 store 13 15 12 4
12a nop 
12c nop 
12e load 15 16 1420 4
132 lui 13 8192
134 addi 11 11 10
136 store 15 13 8 4
138 addi 13 0 -128
13c store 12 13 4 1
13e slli 11 11 3
140 addi 14 14 158
144 jump 220
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'channel literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'channel fullboundaries')
 for a,f in s.items():init.g(n,a,'channel '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'channel typedload')
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'channel QK raw/width')
 for o in (0x54,0x56,0xc4,0xc6,0xf8,0xfa,0x12a,0x12c):check(raw[o:o+2]==bytes.fromhex('0100') and n[pc+o]['op']=='nop','channel retainedhints')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'channel fullidentity')
 e={};rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'channel RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  check(op not in ('jal','jalr','call_indirect') and all(z in n for z in q),'channel no calls/closedCFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and common.acyclic(e) and rets==[pc+0x78,pc+0xe4],'channel completeDAG/twoRET')
 writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
 check(writes==[6,*range(10,18),28],'channel onlycaller-saved GPR/noSP/RA/S')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(0x12,13,14,0,4),(0x1c,13,15,0,4),(0x48,15,10,0,4),(0x52,13,15,12,4),(0x60,13,15,8,4),(0x66,12,15,4,1),(0x74,13,11,100,4),(0x76,13,10,12,4),(0x9a,15,17,0,4),(0xb8,15,10,0,4),(0xc2,13,15,12,4),(0xd4,15,6,8,4),(0xd8,12,13,4,1),(0xe0,15,11,100,4),(0xe2,15,10,12,4),(0xec,15,10,0,4),(0xf6,13,15,12,4),(0x108,15,6,8,4),(0x10c,12,13,4,1),(0x11e,15,10,0,4),(0x128,13,15,12,4),(0x136,15,13,8,4),(0x13c,12,13,4,1)]
 check(stores==expected,'channel all23store sites/no frame')
 return dict(start=pc,bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=[],returns=rets,tails=[],stores=stores,encoded_GPR_writes=writes,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 out={};n={d['pc']-b['start']:d for d in b['instructions']}
 details={0:(0x120,0x128,0x12e,0x136,0x13c,0xe0,0xe2),1:(0x4a,0x52,0x58,0x60,0x66,0x74,0x76),2:(0xee,0xf6,0xfc,0x108,0x10c,0xe0,0xe2),3:(0xba,0xc2,0xc8,0xd4,0xd8,0xe0,0xe2)}
 for mode in range(4):
  for descriptor in (0,1):
   c={8:0xa if descriptor else 0x1e,0x3a:0x3e if mode==1 else 0x7a,0x84:0x112 if mode==0 else 0x88,0xa8:0xac if mode==3 else 0xe6}
   seq=common.walk(b,c);out[f'mode{mode}_descriptor{descriptor}']=seq
   check((0x12 in seq)==bool(descriptor) and (0x1c in seq)==bool(descriptor),'channel descriptorgates bothORstores')
   load,masked,reload,write8,writeS4,write100,restore=details[mode]
   check(all(o in seq for o in details[mode]) and seq.index(load)<seq.index(masked)<seq.index(reload)<seq.index(write8)<seq.index(writeS4)<seq.index(write100)<seq.index(restore),'channel capturedH0word/clear/freshH1/orderedwrites')
   check(n[load]['op']=='load' and n[load]['rd']==10 and n[load]['imm']==12 and not any(n[o].get('rd')==10 for o in seq[seq.index(load)+1:]),'channel fullcapturedH0word reply preservedthroughRET')
   check((0x9a in seq)==(mode in (2,3)) and (0xb8 in seq)==(mode==3) and (0xec in seq)==(mode==2) and (0x11e in seq)==(mode==0),'channel modeRMW sitepartition')
 return out


def scalar_certificates(b):
 n={d['pc']-b['start']:d for d in b['instructions']}
 check((n[0x40]['imm']+n[0x42]['imm'])&0xffffffff==(n[0x7a]['imm']+n[0x80]['imm'])&0xffffffff==0xffffcfff,'channel control12/13clear mask')
 check((n[0x9e]['imm']+n[0xa6]['imm'])&0xffffffff==0xffff3fff,'channel control14/15clear mask')
 for a,z in ((0x4c,0x4e),(0xbc,0xbe),(0xf0,0xf2),(0x122,0x124)):check((n[a]['imm']+n[z]['imm'])&0xffffffff==0xffffdfff,'channel H12bit13clear mask')
 check(n[0x5c]['imm']==n[0x94]['imm']==n[0x132]['imm']==8192 and n[0xb2]['imm']==16384 and n[0x114]['imm']==4096,'channel control/set8 constants')
 check(n[0x5e]['imm']==11 and n[0x68]['imm']==2 and n[0x6c]['imm']==158 and n[0x72]['imm']==1,'channel mode1 durationanchors')
 check(n[0x8c]['imm']==2 and n[0xa4]['imm']==3 and n[0xa0]['imm']==190 and n[0xd0]['imm']==215 and n[0xda]['imm']==n[0xde]['imm']==1,'channel mode3 durationanchors')
 check(n[0x104]['imm']==74 and n[0x10e]['imm']==3 and n[0x134]['imm']==10 and n[0x13e]['imm']==3 and n[0x140]['imm']==158,'channel mode2/fallback durationanchors')
 return dict(control12_13_mask=0xffffcfff,control14_15_mask=0xffff3fff,H12_mask=0xffffdfff,
  duration_coefficients={0:[16,2,476],1:[8,2,404],2:[128,2,1820],3:[32,2,1304]},
  duration='low32(A*entryA1+2*capturedU8S10+B);mode0=fallbackbit1clear/non1,mode2=otherbit1set/non3;notjustlowbytemodes',
  reply='full mode-specific U32[initialcapturedH0+12] sampled AFTER R0 writes,then keptA0;not entrysnapshot/zero/duration/status')


def domains():
 classes=[0]*4
 for mode in range(65536):
  k=1 if mode==1 else 3 if mode==3 else 2 if mode&2 else 0;classes[k]+=1
 check(classes==[32767,1,32767,1] and 5&2==0 and 7!=3,'channel fullmodeclassification')
 for a in range(65536):
  for s in (0,1,127,255):
   forms=[2*(s+158+8*(a+10)),2*(s+158+4*(a+11)),2*(s+190+8*(8*(a+2)+74)),2*(s+190+2*(8*(a+2)+215))]
   for mode,(A,B) in enumerate(((16,476),(8,404),(128,1820),(32,1304))):check(forms[mode]&0xffffffff==(A*a+2*s+B)&0xffffffff,'channel modular durationidentity')
 request=[]
 for mode,(A,B) in enumerate(((16,476),(8,404),(128,1820),(32,1304))):
  vals=[A*2+2*s+B for s in range(256)];request.append(dict(mode=mode,A1=2,min=min(vals),max=max(vals),base=A*2+B))
 check([r['base'] for r in request]==[508,420,2076,1368] and [r['max'] for r in request]==[1018,930,2586,1878],'channel request128 A1two fullbytebounds')
 for a in (0x7fffffff,0xffffffff):
  for A,B in ((16,476),(8,404),(128,1820),(32,1304)):check((A*a+510+B)&0xffffffff==(A*a+510+B)%2**32,'channel fullwordwrap notsaturation')
 return dict(fullmode_low16_cases=65536,mode_partition=classes,duration_identity_cases=1048576,request_A1two=request,
  fullwidth_unsigned_reply=True,H0_equals_H1_assumed=False,scalar_value_and_store_destination_separate=True,target_execution_or_emulation=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE)
 check(sparse.captured(mem,STARTS[index],SIZE)==raw,'channel strictoriginalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;S=G+1300+80*index;Rslot=G+1288+80*index;Hslot=G+1340+80*index
 check(n[0]['imm']+n[4]['imm']==G+1292+80*index and n[0x1e]['imm']+n[0x26]['imm']==S and n[0x22]['imm']+n[0x30]['imm']==Rslot and n[0x2a]['imm']+n[0x36]['imm']==Hslot and n[0x34]['imm']==10,'channel fixedsources')
 for o in (0x58,0xc8,0xfc,0x12e):check(n[0x2a]['imm']+n[o]['imm']==Hslot,'channel allfreshH1 sources')
 attempt=previous.previous.previous.previous
 callerraw=init.binding.take(data,attempt.STARTS[index],502);caller=attempt.body(callerraw,index)
 check(sparse.captured(mem,attempt.STARTS[index],502)==callerraw and [c['target'] for c in caller['calls'] if c['offset'] in (0x152,0x1ae)]==[b['start']]*2,'channel bothattempt sites exactjoin')
 cn={d['pc']-caller['start']:d for d in caller['instructions']};seq=attempt.paths(caller)['request128_direct_delta']
 check(cn[0x194]['rd']==9 and cn[0x194]['imm']==2 and cn[0x100]['rs1']==9 and cn[0x104]['imm']==16 and cn[0x128]['rs2']==11 and cn[0x130]['rd']==11 and not any(cn[o].get('rd')==11 for o in seq[seq.index(0x130)+1:seq.index(0x152)]),'channel attempt savedA1two spill/reload preserved tocall')
 check(cn[0x14a]['rd']==10 and cn[0x14e]['imm']==4 and cn[0x150]['imm']==3 and not any(cn[o].get('rd')==10 for o in seq[seq.index(0x152)+1:]),'channel freshfourmode argument andfinalreply unmodified')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=paths(b),scalar_certificates=scalar_certificates(b),
  reused_attempt=dict(start=caller['start'],bytes=502,new_code_bytes_counted=0),nominal_globals=dict(status=S,R_pointer_slot=Rslot,H_pointer_slot=Hslot,descriptor_pointer_slot=G+1292+80*index),
  contract=['optionaldescriptor nonnull ->ORstorethroughdesc16/mask20 then throughdesc0/mask8;innerpointernullsnotguarded;thenfreshR,byteS10,freshH0;no mandatorypointerguards',
   'fullmode1 R0clear12/13;fallbackbit1clear/non1 R0clear12/13set12;bit1set firstR0clear12/13set13,thenfreshR0clear14/15 additionallyset14 ONLYif fullmode3. Dontmerge independentRMWsnapshots',
   'everymode loadsfullH0word12 intoA0 AFTER R0 writes;SWH0word12maskedFFFFDFFF;two0100hints;freshH1slot reload;SWH1+8=8192,SB128S4,SWH1+100duration,SWH1+12=capturedA0;H0/H1neednotequal',
   'no calls/frame/loops/S/SP/RA writes;clobbersA0-A7,T1,T3;A2entryignored. FullnormalreplycapturedH0word12,notfixedstatus/physicalacknowledgement',
   'request128 passesfreshconfigbits4..5 andfullA1=2;duration2*S10+508/420/2076/1368 for0/1/2/3. AttemptnormallyRETthesameA0capturedword afteritsown localwrites,underframe/accesspremises'],
  premises='candidateISA/API/installedcode;validcode/global/descriptor/R/Hextents;ordinaryaccesscompletion;no adversealias/wrap/IRQ/DMA/reentry/externalwriters;freshsnapshot equalityseparate',
  actual_provider_binding_hardware_restoration_pointer_equality_pollprogress_or_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-channel-leaf-attempt128-return-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=652,complete_phase_body_instructions=248,reused_attempt_bytes=1004,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['callback65de6/65ed0 andC12 completionwriters','config/mask/divisor/K writers andactualreachableconstraints','actualinstalledproviders/physicaleffects/pollprogress/fullpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('channel instructionmutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('channel typedmutation escaped')
   typed+=1
 check((mutations,typed)==(248,16),'channel mutationcensus')
 print('PASS:248 instruction/16 typed-load mutations rejected;complete CFG/store/GPR/attemptA1two andcapturedreply certificates')


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
 else:check(OUT.read_bytes()==encoded,'channel exactledger replay')
 print('PASS:652B/248i complete channel;strictHEX;1048576 duration/65536 mode cases;fullwordreturn;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/physicalrestore/pollprogress/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
