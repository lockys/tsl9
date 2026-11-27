"""Offline worker, reverse bytecopy and fixed-return core wrapper contracts.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation, provider/crypto/NV/RAM/hardware model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_nv_write_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-worker-static.json')
PARTS=('worker','reverse','core')
STARTS=((0x51f78,0x2000048a,0x63890),(0x52020,0x2000048a,0x6397a))
SOURCES=((0x51f78,0x406fa,0x63890),(0x52020,0x4073a,0x6397a))
SIZES=(144,50,56)
HASHES=(('465c94f709ae43ed4cb6fc8d549b8b304666d0b8920ed727feb30f3c13bbb9a5', 'b9962986b1a35537acf5a390ac6d41e38e25d843ce9dab2335f9d955a1ebdcd2', 'e176dcf1c79c6a2b3fd05cf73734355df498193f76ad373b970b70b5b1f2d83c'), ('fb099f443d029edd2554929df613756b0218340481753070613c8f479f125bc8', 'b9962986b1a35537acf5a390ac6d41e38e25d843ce9dab2335f9d955a1ebdcd2', '85854f4ce98898483e9bad1a37052b7c2015c4a733da9fa292904344dcfcbbae'))
COUNTS=((52, 16, 23), (52, 16, 23))
QK=({'worker': (), 'reverse': ((40, '9c31', 'qk.c.lbu'),), 'core': ()}, {'worker': (), 'reverse': ((40, '9c31', 'qk.c.lbu'),), 'core': ()})
TYPED=({'worker': (), 'reverse': ((4, 2),), 'core': ((4, 2),)}, {'worker': (), 'reverse': ((4, 2),), 'core': ((4, 2),)})
LITERALS=(
{
'worker':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 19 12 4
006 mv 9 11
008 mv 19 10
00a addi 11 0 83
00e addi 10 0 48
012 store 2 18 16 4
014 store 2 1 28 4
016 store 2 8 24 4
018 mv 18 12
01a auipc 1 536535040
01e jalr 1 1 174
022 beqz 10 140
024 addi 12 0 48
028 li 11 0
02a mv 8 10
02c auipc 1 536535040
030 jalr 1 1 1016
034 li 12 16
036 mv 11 19
038 mv 10 8
03a auipc 1 536535040
03e jalr 1 1 1240
042 mv 11 9
044 li 12 3
046 addi 10 8 29
04a auipc 1 536535040
04e jalr 1 1 1224
052 addi 12 8 32
056 addi 11 8 16
05a mv 10 8
05c jal 1 407696
060 mv 9 10
062 li 12 3
064 addi 11 8 45
068 mv 10 18
06a auipc 1 536535040
06e jalr 1 1 1192
072 mv 10 8
074 auipc 1 536535040
078 jalr 1 1 292
07c load 1 2 28 4
07e load 8 2 24 4
080 mv 10 9
082 load 18 2 16 4
084 load 9 2 20 4
086 load 19 2 12 4
088 addi 2 2 32
08a jr 1
08c li 9 19
08e jump 124
''',
'reverse':'''
000 lui 15 1073889280
004 load 14 15 524 4
008 store 15 0 524 4
00c fence.i 
010 addi 15 12 -1
014 add 11 11 15
016 add 12 12 10
018 bne 10 12 38
01c lui 15 1073889280
020 store 15 14 524 4
024 jr 1
026 addi 11 11 -1
028 load 15 11 1 1
02a addi 10 10 1
02c store 10 15 -1 1
030 jump 24
''',
'core':'''
000 lui 15 536883200
004 load 14 15 1340 4
008 addi 2 2 -32
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 11 12 4
010 store 2 12 8 4
012 load 15 14 80 4
014 mv 8 10
016 li 10 13
018 ori 15 15 128
01c store 14 15 80 4
01e jal 1 409306
020 load 12 2 8 4
022 load 11 2 12 4
024 mv 10 8
026 auipc 1 536473600
02a jalr 1 1 -1528
02e load 1 2 28 4
030 load 8 2 24 4
032 li 10 0
034 addi 2 2 32
036 jr 1
''',
},
{
'worker':'''
000 addi 2 2 -32
002 store 2 9 20 4
004 store 2 19 12 4
006 mv 9 11
008 mv 19 10
00a addi 11 0 83
00e addi 10 0 48
012 store 2 18 16 4
014 store 2 1 28 4
016 store 2 8 24 4
018 mv 18 12
01a auipc 1 536535040
01e jalr 1 1 6
022 beqz 10 140
024 addi 12 0 48
028 li 11 0
02a mv 8 10
02c auipc 1 536535040
030 jalr 1 1 848
034 li 12 16
036 mv 11 19
038 mv 10 8
03a auipc 1 536535040
03e jalr 1 1 1072
042 mv 11 9
044 li 12 3
046 addi 10 8 29
04a auipc 1 536535040
04e jalr 1 1 1056
052 addi 12 8 32
056 addi 11 8 16
05a mv 10 8
05c jal 1 407930
060 mv 9 10
062 li 12 3
064 addi 11 8 45
068 mv 10 18
06a auipc 1 536535040
06e jalr 1 1 1024
072 mv 10 8
074 auipc 1 536535040
078 jalr 1 1 124
07c load 1 2 28 4
07e load 8 2 24 4
080 mv 10 9
082 load 18 2 16 4
084 load 9 2 20 4
086 load 19 2 12 4
088 addi 2 2 32
08a jr 1
08c li 9 19
08e jump 124
''',
'reverse':'''
000 lui 15 1073889280
004 load 14 15 524 4
008 store 15 0 524 4
00c fence.i 
010 addi 15 12 -1
014 add 11 11 15
016 add 12 12 10
018 bne 10 12 38
01c lui 15 1073889280
020 store 15 14 524 4
024 jr 1
026 addi 11 11 -1
028 load 15 11 1 1
02a addi 10 10 1
02c store 10 15 -1 1
030 jump 24
''',
'core':'''
000 lui 15 536883200
004 load 14 15 1420 4
008 addi 2 2 -32
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 11 12 4
010 store 2 12 8 4
012 load 15 14 80 4
014 mv 8 10
016 li 10 13
018 ori 15 15 128
01c store 14 15 80 4
01e jal 1 409540
020 load 12 2 8 4
022 load 11 2 12 4
024 mv 10 8
026 auipc 1 536473600
02a jalr 1 1 -1686
02e load 1 2 28 4
030 load 8 2 24 4
032 li 10 0
034 addi 2 2 32
036 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'B1worker literalfields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k]
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'B1worker typedload encoding')
 n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'B1worker full boundaries')
 for a,f in s.items():init.g(n,a,'B1worker '+part+' operand '+hex(a-pc),**f)
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'B1worker Xwchc raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'B1worker completeidentity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'B1worker RET RA');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'B1worker linked JAL');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','B1worker callpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'B1worker closedCFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n),'B1worker all localnodes reachable')
 if part=='reverse':
  cut={a:[z for z in qs if (a-pc,z-pc)!=(0x30,0x18)] for a,qs in edges.items()}
  check(not common.acyclic(edges) and common.acyclic(cut),'B1worker reverse exactloopcut')
 else:check(common.acyclic(edges),'B1worker worker/core acyclic')
 expected={'worker':[(0x1e,0x20000040),(0x30,0x2000039c),(0x3e,0x2000048a),(0x4e,0x2000048a),(0x5c,0x63890+234*index),(0x6e,0x2000048a),(0x78,0x20000110)],
  'reverse':[],'core':[(0x1e,0x63eda+234*index),(0x2a,0x200022be+76*index)]}[part]
 check(calls==[dict(offset=o,target=t) for o,t in expected] and rets==[pc+{'worker':0x8a,'reverse':0x24,'core':0x36}[part]],'B1worker allcall/return sites')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 saved=[d for d in stores if d['base']==2]
 frames={'worker':{(9,20),(19,12),(18,16),(1,28),(8,24)},'reverse':set(),'core':{(1,28),(8,24),(11,12),(12,8)}}
 check(len(saved)==len(frames[part]) and {(d['source'],d['imm']) for d in saved}==frames[part] and all(d['bytes']==4 for d in saved),'B1worker exactframe saves')
 nonframe=[d for d in stores if d['base']!=2]
 desired={'worker':[],'reverse':[(8,15,0,524,4),(0x20,15,14,524,4),(0x2c,10,15,-1,1)],'core':[(0x1c,14,15,80,4)]}[part]
 check(nonframe==[dict(offset=o,base=r,source=v,imm=x,bytes=z) for o,r,v,x,z in desired],'B1worker nonframe stores')
 if part=='reverse':
  check(raw[0xc:0x10]==bytes.fromhex('0f100000') and n[pc]['imm']+n[pc+4]['imm']==0x4002420c,'B1worker reverse fixedcontrol/FENCE')
  check({d['rd'] for d in n.values() if 'rd' in d}=={10,11,12,14,15} and not calls,'B1worker reverse keepsS/SP/RA;no frame/calls')
 return dict(start=pc,source=SOURCES[index][k],bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,
  complete_local_body=True,target_execution_or_emulation=False)


def valid_path(b,seq):
 pc=b['start'];e=b['CFG'];check(seq[0]==0 and not e[pc+seq[-1]] and all(pc+z in e[pc+a] for a,z in zip(seq,seq[1:])),'B1worker immutablepath');return seq


def paths(b,part):
 if part=='worker':
  ps={name:common.walk(b,{0x22:z}) for name,z in [('alloc_null_19',0x8c),('alloc_nonnull_fill_reverse_core_output_release',0x24)]}
  check([x for x in ps['alloc_null_19'] if x in {c['offset'] for c in b['calls']}]==[0x1e],'B1worker null path onlyallocator')
  normal=ps['alloc_nonnull_fill_reverse_core_output_release']
  check(normal.index(0x5c)<normal.index(0x60)<normal.index(0x6e)<normal.index(0x78)<normal.index(0x80),'B1worker unconditional output-before-release-before savedreply')
  return ps
 if part=='core':return dict(normal_fixed0=common.walk(b,{}))
 ps={}
 for n in (0,3,16):
  unit=[0x18,0x26,0x28,0x2a,0x2c,0x30];seq=[0,4,8,0xc,0x10,0x14,0x16]+unit*n+[0x18,0x1c,0x20,0x24]
  ps[str(n)+'byte']=valid_path(b,seq)
  check(seq.count(0x2c)==n and seq.index(0xc)<seq.index(0x18),'B1worker control/FENCE precedes evenzero payload guard')
 return ps


def domains():
 pairs=0
 for n in range(257):
  for j in range(n):
   check(n-1-j>=0 and n-1-j<n and ((n-1-j)-1)+1==n-1-j,'B1worker decrement/read+1 relative sourceindex')
   check((j+1)-1==j and j<n,'B1worker increment/store-1 relative destindex');pairs+=1
 check(pairs==32896,'B1worker reverse scalarindex census')
 for n in (3,16):
  check({n-1-j for j in range(n)}==set(range(n)) and all(n-1-(n-1-j)==j for j in range(n)),'B1worker reverseindex bijection/involution algebra')
 # Relative intervals only, no target bytes/heap/register state.
 first=set(range(16));second=set(range(29,32));output=set(range(45,48));whole=set(range(48))
 core_inputs=(set(range(16)),set(range(16,32)));core_output=set(range(32,48))
 check(first.isdisjoint(second) and first|second<=whole and second<=core_inputs[1] and output<=core_output,'B1worker input/output slices within48B')
 check(core_inputs[0].isdisjoint(core_inputs[1]) and (core_inputs[0]|core_inputs[1]).isdisjoint(core_output) and core_inputs[0]|core_inputs[1]|core_output==whole,'B1worker three16B coreblocks')
 check(len(whole-(first|second))==29 and set(range(16,29))<=whole-(first|second),'B1worker fill-reverse pre-core unaffected relativebytes')
 for j in range(3):check(45+(2-j)==47-j and 29+j<=31 and 2-j in range(3),'B1worker output/input last3 byteindices')
 check(10==8+2 and set(range(8,11)).isdisjoint(set(range(12,15))) and set(range(12,15)).isdisjoint(set(range(20,32))),'B1worker caller scratch/savedframe interval joins')
 for x in range(256):check(64<=((x&63)|64)<=127,'B1worker wrapper normalized finalscratchbyte')
 for x in (0,1,127,128,255,0x7fffffff,0x80000000,0xffffffff):check((x|128)&128==128 and ((x|128)&~128)==(x&~128),'B1worker core ORbit7 samples')
 return dict(reverse_length_domain='0..256',reverse_source_dest_index_pairs=pairs,actual_worker_lengths=[16,3,3],
  reverse_contract='under valid nonalias stable extents:D[j] receives fresh S[n-1-j],0<=j<n;normalA0=D+nmod32;not a memorysnapshot ormemmove proof',
  workspace_bytes=48,reverse_first_destination=[0,16],reverse_second_destination=[29,32],reverse_output_source=[45,48],core_block_intervals=[[0,16],[16,32],[32,48]],
  pre_core_fill_only_bytes=29,pre_core_block2_zero_prefix=[16,29],caller_input_scratch=[8,11],caller_output_scratch=[12,15],
  conditional_status='allocatornull19;nonnull+matchingcore+ordinarynormalcalls ->worker0;core0ignoresinnercallee replies',
  result_bytes_and_actual_provider_binding_retention_or_physical_effects_proved=False,target_execution_or_emulation=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={};mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);f=mapping['first_copy']
 def source(target):return int(f['source'],16)+target-int(f['destination'],16)
 check(source(0x2000048a)==SOURCES[index][1] and 0x2000048a+50<=int(mapping['first_copy_end_exclusive'],16),'B1worker complete reverse linkedmapping')
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,SOURCES[index][k],SIZES[k]);check(sparse.captured(mem,SOURCES[index][k],SIZES[k])==raw,'B1worker completeoriginal sparseHEX');bs[part]=body(raw,part,index)
 n={part:{d['pc']-b['start']:d for d in b['instructions']} for part,b in bs.items()};w,r,c=n['worker'],n['reverse'],n['core']
 check(w[0xa]['imm']==83 and w[0xe]['imm']==w[0x24]['imm']==48 and w[0x28]['imm']==0 and w[0x8c]['imm']==19,'B1worker allocation/fill/nullstatus')
 check([w[a]['rs2'] for a in (6,8,0x18)]==[11,10,12] and w[0x34]['imm']==16 and w[0x44]['imm']==w[0x62]['imm']==3 and w[0x46]['imm']==29 and w[0x64]['imm']==45,'B1worker exactinput/output arguments')
 check(w[0x52]['imm']==32 and w[0x56]['imm']==16 and w[0x5a]['rs2']==8 and w[0x60]['rd']==9 and w[0x60]['rs2']==10 and w[0x80]['rs2']==9,'B1worker coreblocks andsavedR')
 check(r[0x10]['imm']==-1 and r[0x14]['rd']==11 and r[0x16]['rd']==12 and r[0x26]['imm']==-1 and r[0x28]['imm']==1 and r[0x2a]['imm']==1 and r[0x2c]['imm']==-1,'B1worker reverse pre/postincrement addresses')
 check(c[0]['imm']+c[4]['imm']==0x2000353c+80*index and c[0x12]['imm']==c[0x1c]['imm']==80 and c[0x18]['imm']==128 and c[0x16]['imm']==13 and c[0x32]['imm']==0,'B1worker dynamiccontext OR80/cmd13/fixed0')
 check(c[0x20]['imm']==8 and c[0x22]['imm']==12 and c[0x24]['rs2']==8,'B1worker core reloads originalA0/A1/A2 beforeRAMprovider')
 cmod=previous.previous.previous
 caller=cmod.body(init.binding.take(data,cmod.STARTS[index][3],cmod.SIZES[3]),'check3',index)
 cn={d['pc']-caller['start']:d for d in caller['instructions']}
 check(next(d['target'] for d in caller['calls'] if d['offset']==0x32)==bs['worker']['start'] and cn[0x22]['imm']==12 and cn[0x24]['imm']==8 and cn[0x36]['op']=='bnez','B1worker actual check3 (P,SP8,SP12)/nonzero gate')
 down=cmod.previous.previous;filltarget=0x2000039c;fillsrc=source(filltarget);fillraw=init.binding.take(data,fillsrc,46)
 check(filltarget+46<=int(mapping['first_copy_end_exclusive'],16) and sparse.captured(mem,fillsrc,46)==fillraw,'B1worker reusedcompletefill originalHEX/mapping');down.fill_source.fill_contract(fillraw)
 target=bs['core']['calls'][1]['target'];src=source(target)
 check(target+2<=int(mapping['first_copy_end_exclusive'],16) and sparse.captured(mem,src,2)==init.binding.take(data,src,2),'B1worker innerprovider candidateentry mapping only')
 check(bs['worker']['calls'][4]['target']==bs['core']['start'],'B1worker exactcore calljoin')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={part:common.certificates(b) for part,b in bs.items()},paths={part:paths(b,part) for part,b in bs.items()},
  reused_fill=dict(source=fillsrc,target=filltarget,bytes=46,sha256=sha256(fillraw).hexdigest(),new_code_bytes_counted=0,installed_binding_proved=False),
  inner_provider_entry_mapping=dict(source=src,target=target,entry_prefix=init.binding.take(data,src,2).hex(),complete_callee_semantics_proved=False,new_code_bytes_counted=0,installed_binding_proved=False),
  worker_contract=['saveoriginalP/Q/O inS3/S1/S2;allocate(48,83);null ->19 without fill/reverse/core/output/release',
   'nonnullW ->fill(W,0,48),reverse(W,P,16),reverse(W29,Q,3),core(W,W16,W32);savefullR inS1',
   'unconditional reverse(O,W45,3) AFTERcore evenifRnonzero;thenprivate-release20000110(W);return savedR;childcopy/free repliesignored',
   'onlydirectstores5framewords;workspaceownership/extent/initialization/output/noescape/release notprovedbyarguments alone'],
  reverse_contract=['firstcaptureword4002420c,SW0thenFENCE.I beforelength guard;no frame,calls,nullpointerguard;normalexit restorescapturedword',
   'sourcecursor=S+n-1,end=D+nmod32;eachstep predecrementS,readU8cursor1,incrementD,SBcursor-1;normalA0=D+n,A1=S-1,A2=D+n;freshreads notsnapshot',
   'n0 skips payloadreads/stores butstillcontrolword/FENCE;nonnullvalidextents/nonalias/stability remainpremises;notcopy20000332 ormemmove'],
  core_contract=['firstloadB=U32[2000353c/2000358c],no nullguard;freshwordB80 OR80,SWB80 beforecalls. Physicalobject/MMIO/disjointness unknown',
   'call63eda/63fc4 withA0=13;A1/A2 stillthenlive workspacepointers,notconfinementproof;afterreturn restoreoriginalA0 viaS0 andA1/A2 viaframe',
   'call200022be/2000230a(originalA0,A1,A2);ignorebothcallee scalarreplies;normalRETforces0. No local outputblockstore provesinnerprovider wrotebytes'],
  composition=['check3 supplies(P,ownSP8,ownSP12);sourceSP8..10 includesnormalizedSP10 (byte&63)|64. Matchingreverse placeslast3inputbytes reversedatW29..31 andW45..47 reversedatcallerSP12..14',
   'withmatchingfill/reverse/validnonaliasstableworkspace,beforecore W0..15 carries reversedP16,W16..28 stillzero,W29..31 reversedQ3. Unknowncore/provider effectsafterward separate',
   'matchingcoreordinarynormalreturns implynonnullworkerpathR0;allocatornullworker19 propagatescheck3 nonzero andselector skip. Normalnonnullworkerpath enterscheck3 finalcomparator,zeroiff fullreply1',
   'core0 alone doesnotestablishinitialized/meaningfuloutput,providercompletion,physicaleffects orpointerlifetime;privatefreeattempt occurs afteroutputcopy,actualno-retention/release remainsunproved'],
  premises='conditionalcandidateISA/providers/firstcopymapping;validcode/frame/controlword/context/workspace/source/outputextents;ordinarycalleeS/SP/RA/savedframepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshsnapshot equalities separate',
  actual_inner_provider_hardware_output_installed_binding_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-worker-reverse-core-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=500,complete_phase_body_instructions=182,reused_fill_bytes=92,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['63eda/63fc4 commandhelper and200022be/2000230a outputprovider','dynamiccontext pointerwriters/providerbinding andsideeffects','actualsourcevalues/reachability andcompleteborrowedpointerlifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1worker instructionmutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('B1worker typedmutation escaped')
    typed+=1
 check((mutations,typed)==(182,4),'B1worker mutationcensus');domains()
 print('PASS:182 instruction/4 typed-load mutations rejected;32896 reverseindex pairs;48B/caller interval andsavedreply certificates')


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
 else:check(OUT.read_bytes()==encoded,'B1worker exactledger replay')
 print('PASS:500B/182i complete worker/reverse/core;strict HEX/mapping;check3 andcore0 join;exact ledger')
 print('PASS:NO target execution/emulation;innerprovider output/binding,physicaleffects andpointerlifetime UNPROVED')


if __name__=='__main__':main()
