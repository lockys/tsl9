"""Offline complete JT2 zero-path leaf: flag, metadata and packet-class reads.
Original operands, immutable CFG witnesses and host field arithmetic only.
No target execution/emulation, mutable target RAM/MMIO/packet/provider model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_irq_status_static as previous
import check_v4160_callback_dispatch_static as dispatch
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-irq-zero-static.json')
STARTS=(0x2000298e,0x200029da)
SOURCES=(0x42bfe,0x42c8a)
HASHES=('6eb951abd869b41da959cf1050a7e8469d54bf9522f5c5f1d9e93ea85b7ed6c0','7f19ded3e90afa2616b1c61f8f06213adfb90369934c62fd89417563ec36507a')
LITERAL='''
000 lui 15 536883200
004 load 15 15 1340 4
008 load 14 15 12 4
00a slli 13 14 17
00e bge 13 0 50
012 load 14 15 8 4
014 slli 13 14 17
018 bge 13 0 50
01c li 14 -1
01e store 15 14 104 4
020 lui 14 536883200
024 addi 14 14 412
028 load 13 14 28 4
02a addi 13 13 1
02c store 14 13 28 4
02e lui 14 16384
030 store 15 14 8 4
032 load 14 15 8 4
034 srli 14 14 3
036 andi 14 14 1
038 beqz 14 84
03a lui 14 536883200
03e addi 14 14 1300
042 load 13 14 2 1
044 ori 13 13 1
048 store 14 13 2 1
04a addi 13 0 -128
04e store 14 13 4 1
050 li 14 8
052 store 15 14 8 4
054 load 14 15 8 4
056 andi 14 14 1
058 beqz 14 110
05a lui 14 536883200
05e addi 14 14 1300
062 load 13 14 1 1
064 ori 13 13 1
068 store 14 13 1 1
06a li 14 1
06c store 15 14 8 4
06e load 14 15 8 4
070 srli 14 14 2
072 andi 14 14 1
074 bnez 14 126
076 load 14 15 8 4
078 srli 14 14 1
07a andi 14 14 1
07c beqz 14 208
07e lui 14 536883200
082 addi 12 14 1300
086 store 12 0 5 1
08a load 13 15 8 4
08c lui 11 536883200
090 load 11 11 1288 4
094 srli 13 13 2
096 andi 13 13 1
098 beqz 13 384
09a load 13 11 0 4
09c srli 13 13 12
09e andi 13 13 3
0a0 bnez 13 378
0a2 load 10 15 80 4
0a4 load 13 12 36 4
0a6 andi 12 10 32
0aa load 13 13 1 1
0ac beqz 12 334
0ae bnez 13 372
0b0 addi 13 0 93
0b4 store 15 13 28 4
0b6 load 13 14 1300 1
0ba ori 13 13 1
0be store 14 13 1300 1
0c2 li 14 4
0c4 store 15 14 8 4
0c6 load 14 11 44 4
0c8 andi 14 14 -4
0ca ori 14 14 1
0ce store 11 14 44 4
0d0 load 14 15 8 4
0d2 slli 13 14 19
0d6 bge 13 0 254
0da lui 14 536883200
0de addi 13 14 952
0e2 load 12 13 124 1
0e6 addi 14 14 952
0ea andi 12 12 16
0ec beqz 12 396
0ee load 14 13 124 1
0f2 ori 14 14 32
0f6 store 13 14 124 1
0fa lui 14 4096
0fc store 15 14 8 4
0fe load 14 15 8 4
100 slli 13 14 18
104 bge 13 0 290
108 lui 14 536883200
10c addi 14 14 1300
110 load 13 14 4 1
112 slli 13 13 24
114 srai 13 13 24
116 bge 13 0 286
11a li 13 1
11c store 14 13 4 1
11e lui 14 8192
120 store 15 14 8 4
122 load 14 15 8 4
124 slli 13 14 16
128 bge 13 0 332
12c lui 14 536883200
130 addi 14 14 952
134 load 13 14 125 1
138 andi 13 13 1
13a beqz 13 428
13c load 13 14 125 1
140 ori 13 13 2
144 store 14 13 125 1
148 lui 14 32768
14a store 15 14 8 4
14c jr 1
14e beqz 13 176
150 li 12 1
152 bne 13 12 348
156 addi 13 0 97
15a jump 180
15c li 12 2
15e bne 13 12 360
162 addi 13 0 101
166 jump 180
168 li 12 3
16a bne 13 12 372
16e addi 13 0 105
172 jump 180
174 addi 13 0 107
178 jump 180
17a addi 13 0 108
17e jump 180
180 load 14 12 3 1
182 ori 14 14 1
186 store 12 14 3 1
188 li 14 2
18a jump 196
18c load 13 14 124 1
190 li 12 2
192 andi 13 13 15
194 beq 13 12 420
198 load 13 14 124 1
19c li 12 3
19e andi 13 13 15
1a0 bne 13 12 250
1a4 li 13 4
1a6 store 14 13 124 1
1aa jump 250
1ac load 13 14 125 1
1b0 andi 13 13 4
1b2 beqz 13 328
1b4 load 13 14 125 1
1b8 ori 13 13 8
1bc jump 324
'''
DELTA_SITES=(4,0x24,0x3e,0x5e,0x82,0x90,0xb6,0xbe,0xde,0xe6,0x10c,0x130)
TYPED=((4,2),(0x90,2),(0xb6,4),(0xe2,4),(0xee,4),(0x134,4),(0x13c,4),(0x18c,4),(0x198,4),(0x1ac,4),(0x1b4,4))
QK=((0x42,'3423','qk.c.lbu'),(0x48,'34a3','qk.c.sb'),(0x4e,'54a3','qk.c.sb'),(0x62,'1433','qk.c.lbu'),(0x68,'14b3','qk.c.sb'),(0xaa,'9432','qk.c.lbu'),(0x110,'5423','qk.c.lbu'),(0x11c,'54a3','qk.c.sb'),(0x180,'3832','qk.c.lbu'),(0x186,'38b2','qk.c.sb'))


def specs(pc,index):
 out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);values=list(map(int,values))
  check(len(values)==len(FIELDS[op]),'IRQzero literalfields');d=dict(zip(FIELDS[op],values));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  if o in DELTA_SITES:d['imm']+=80*index
  out[pc+o]=d
 return out


def body(raw,index,pc=None):
 pc=STARTS[index] if pc is None else pc;n=decode(raw,pc);s=specs(pc,index)
 check(n.keys()==s.keys(),'IRQzero full boundaries')
 for a,f in s.items():init.g(n,a,'IRQzero '+hex(a-pc),**f)
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'IRQzero typed load')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'IRQzero exactQKbyte')
 check((len(raw),len(n),sha256(raw).hexdigest())==(446,158,HASHES[index]),'IRQzero fullidentity')
 edges={}
 for a,d in n.items():
  op=d['op'];q=[] if op=='jr' else [a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  if op=='jump':q=[d['target']]
  if op=='jr':check(d['rs1']==1,'IRQzero ordinaryRET')
  check(op not in ('jal','jalr','call_indirect','csr','mret','ecall') and all(z in n for z in q),'IRQzero closed leaf/no calls/traps');edges[a]=q
 check(previous.attempt.common.acyclic(edges),'IRQzero completeDAG')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and [a-pc for a,qs in edges.items() if not qs]==[0x14c],'IRQzero reachability/soleRET')
 writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
 check(writes==list(range(10,16)) and [a-pc for a,d in n.items() if d.get('rd')==15]==[0,4],'IRQzero onlyA0..A5/noSP/RA/GP/S;heldH')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(0x1e,15,14,104,4),(0x2c,14,13,28,4),(0x30,15,14,8,4),(0x48,14,13,2,1),(0x4e,14,13,4,1),(0x52,15,14,8,4),(0x68,14,13,1,1),(0x6c,15,14,8,4),(0x86,12,0,5,1),(0xb4,15,13,28,4),(0xbe,14,13,1300+80*index,1),(0xc4,15,14,8,4),(0xce,11,14,44,4),(0xf6,13,14,124,1),(0xfc,15,14,8,4),(0x11c,14,13,4,1),(0x120,15,14,8,4),(0x144,14,13,125,1),(0x14a,15,14,8,4),(0x186,12,14,3,1),(0x1a6,14,13,124,1)]
 check(stores==expected,'IRQzero all21 stores')
 h8=[a-pc for a,d in n.items() if d['op']=='load' and d['rs1']==15 and d['imm']==8]
 check(h8==[0x12,0x32,0x54,0x6e,0x76,0x8a,0xd0,0xfe,0x122],'IRQzero nineH8read sites')
 return dict(start=pc,bytes=446,sha256=HASHES[index],instructions=list(n.values()),CFG=edges,stores=stores,GPR_writes=writes,H8_load_sites=h8,calls=[],returns=[pc+0x14c],complete_local_body=True)


def witnesses(b):
 pc=b['start'];paths=[]
 def visit(a,seq):
  seq=seq+[a-pc]
  if not b['CFG'][a]:paths.append(seq)
  else:
   for z in b['CFG'][a]:visit(z,seq)
 visit(pc,[]);chosen={}
 for p in paths:
  check(p[-1]==0x14c and (0x1e in p)==(0x2c in p)==(0x30 in p),'IRQzero pairbit14 stores')
  if 0xaa in p:check(all(o in p for o in (0x86,0x8a,0x9a,0xa2,0xa4)) and p.index(0xa4)<p.index(0xaa),'IRQzero packetclass sources')
  check((0xb4 in p)==(0xbe in p) and not (0xaa in p and 0x186 in p),'IRQzero code/S0 andS3 paths')
  check(not (0xf6 in p and 0x1a6 in p),'IRQzero distinctB124write paths')
  if 0xf6 in p:check(0xe2 in p and 0xee in p and p.index(0xe2)<p.index(0xee)<p.index(0xf6),'IRQzero B124freshOR32')
  if 0x1a6 in p:check(0x18c in p and 0x1a4 in p,'IRQzero B124literal4 source')
  if 0x144 in p:check((0x13c in p) != (0x1b4 in p),'IRQzero B125OR2 vsOR8 sources')
  if 0x11c in p:check(p.index(0x110)<p.index(0x11c)<p.index(0x11e),'IRQzero signedS4beforeA4reuse')
  key='/'.join(next((hex(o) for o in family if o in p),'skip') for family in ((0xb0,0x156,0x162,0x16e,0x174,0x17a,0x186),(0xf6,0x1a6),(0x13c,0x1b4)))
  chosen.setdefault(key,p)
 check(len(paths)==13680 and len(chosen)==72,'IRQzero path/witness census')
 return dict(syntactic_path_count=len(paths),all_paths_sha256=sha256(json.dumps(paths,separators=(',',':')).encode()).hexdigest(),selected_witnesses=chosen,actual_feasibility_or_delivery_proved=False)


def domains():
 for x in range(65536):
  for shift,bit in ((17,14),(19,12),(18,13),(16,15)):
   check(bool(((x<<shift)&0xffffffff)&0x80000000)==bool(x&(1<<bit)),'IRQzero shifted sign bitprojection')
 # Separate observations are separate scalar inputs, not a target-state trace.
 lowcases=0
 for first in range(256):
  for second in range(256):
   check(((first&15)==2 or ((first&15)!=2 and (second&15)==3))==((first&15)==2 or (second&15)==3),'IRQzero B124low-nibble predicate');lowcases+=1
 for x in range(256):
  check((x|32)&32 and (x|2)&2 and (x|8)&8,'IRQzero independentOR bit identities')
  check((x|32)!=4 and (4&32)==0,'IRQzero OR32 bit5 vs literal4 distinctwait predicates')
 for x in (0,1,0x7fffffff,0xfffffffe,0xffffffff):check((x+1)&0xffffffff==(x+1)%2**32,'IRQzero counterincrement mod32')
 return dict(independent_low16_bit_projection_cases=65536,B124_two_fresh_nibble_cases=lowcases,independent_OR_byte_cases=256,
  reused_packetclass_certificate=previous.domains(),snapshot_equality_or_atomicity_proved=False)


def dispatch_join(data,mem,index,B):
 pc=dispatch.STARTS[index];raw=init.binding.take(data,pc,dispatch.SIZES[index]);table=init.binding.take(data,dispatch.TABLES[index],52)
 check(sparse.captured(mem,pc,len(raw))==raw and sparse.captured(mem,dispatch.TABLES[index],52)==table,'IRQzero reuseddispatch/table strictHEX')
 b=dispatch.body(raw,table,index);cert=dispatch.certificates(b,index);n={d['pc']-pc:d for d in b['instructions']}
 check(n[4]['imm']+n[0x28]['imm']==B and b['switch_table']['words'][3]==pc+0x58,'IRQzero samefixedB/case95 tabletarget')
 check(n[0x58]['imm']==4 and n[0x5a]['rs1']==9 and n[0x5a]['imm']==124 and n[0x5e]['target']==pc+0x5a,'IRQzero B124eq4 wait')
 wait=(0x2ba,0x2bc)[index];sites=[0x5a,0x5e]
 for o in (wait,0x3d2):
  check(n[o]['op']=='load' and n[o]['rs1']==9 and n[o]['imm']==124 and n[o+4]['imm']==32 and n[o+8]['target']==pc+o,'IRQzero B124bit5 wait');sites.extend((o,o+4,o+8))
 return dict(start=pc,bytes=len(raw),sha256=b['sha256'],switch_table=b['switch_table'],selected_wait_operands=[n[o] for o in sites],CFG_certificates=cert,
  full_original_body_revalidated=True,writer_reader_same_fixed_B124=True,
  relation='leaf literal4 satisfies exact4 wait but clearsbit5;leaf OR32 setsbit5 but cannot equal4. Actualobservation requires runtimeordering/retention/access/realbinding;noasyncprogress proof')


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());src=SOURCES[index];pc=STARTS[index];raw=init.binding.take(data,src,446)
 check(sparse.captured(mem,src,446)==raw,'IRQzero complete strictHEX');b=body(raw,index);body(raw,index,src)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];base=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(base+pc-dest==src and dest<=pc and pc+446==previous.STARTS[index] and pc+446<=end,'IRQzero full firstcopy andadjacentstatusboundary')
 cs,cp,flag,nz,z,ch,gh=previous.context.REF_DETAILS[index];cr=init.binding.take(data,cs,56)
 check(sparse.captured(mem,cs,56)==cr and z==pc,'IRQzero exactJT2zero-callee join')
 cb=previous.context.body(cr,'callback',cp,56,16,3,ch,(flag,nz,z));cn={d['pc']-cp:d for d in cb['instructions']}
 check(cn[46]['op']=='store' and cn[46]['rs2']==1 and cn[46]['rs1']==2 and cn[46]['imm']==120 and cn[48]['target']==pc and cn[52]['rd']==1 and cn[52]['imm']==120,'IRQzero callerRAframe120 store/call/reload')
 nr=init.binding.take(data,previous.SOURCES[index],260);check(sparse.captured(mem,previous.SOURCES[index],260)==nr,'IRQzero reusednonzeroleaf strictHEX');nonzero=previous.body(nr,index)
 S=0x20003514+80*index;B=0x200033b8+80*index;meta=0x2000319c+80*index
 check(B+126<=S and meta+32<B and S+40<S+88,'IRQzero fixedmetadata/B/S/C12 ranges separated')
 n={d['pc']-pc:d for d in b['instructions']}
 check(n[0x24]['imm']+0x20003000==meta and n[0xde]['imm']+0x20003000==n[0xe6]['imm']+0x20003000==n[0x130]['imm']+0x20003000==B,'IRQzero fixedglobal bases')
 return dict(label=init.binding.PROFILES[index][0],flash_source=src,first_copy=first,body=b,CFG_certificates=witnesses(b),reused_JT2_callback=cb,reused_nonzero_leaf=nonzero,reused_dispatch_B124_join=dispatch_join(data,mem,index,B),
  globals=dict(S=S,B=B,metadata=meta,incremented_word=meta+28,Hslot=S+40,Rslot=S-12,B124=B+124,B125=B+125),
  contract=['H capturedonce;freshH12bit14 AND separatelyfreshH8bit14 ->H104=FFFFFFFF;freshmetadata28 word incrementmod32;H8=16384;then nineindependentH8loadsites overall',
   'freshH8bit3 ->OR1S2,SB128S4,SW8H8;freshH8bit0 ->OR1S1,SW1H8;bit2 ORseparatebit1 gatesS5clear;newfreshbit2 clear ->OR1S3/SW2H8/R44low2=1',
   'bit2set ->freshR0bits12..13 nonzero108;otherwisefreshH80bit5 andfreshS36/P+1 selects93/97/101/105/107 asnonzeroleaf;no buffer/null/extent/length validation orPstores',
   'freshH8bit12 ->freshB124bit4:set ->anotherfreshB124 OR32 store;clear ->separatefreshlow-nibble==2,elseanotherfreshlow-nibble==3 writesliteral4;allbit12setroutesH8=4096',
   'freshH8bit13 ->freshsignedS4,negativewrites1;H8=8192. FreshH8bit15 ->freshB125bit0:set ->anotherfreshB125 OR2;elseanotherfreshB125bit2:set ->anotherfreshB125 OR8;allbit15setroutesH8=32768',
   'fixedB124 joins complete callback case95 exact4 andtwo bit5waits,notdynamicN124. LocalOR32/literal4 aredistinct enabling writes,notactualeventdelivery orfinitepollproof',
   'no local calls/frame/CSR/SP/RA/GP/S registerwrites;soleRET;onlyA0..A5 GPRdefs. FixedB124/125 globals arenot same-offsetdynamicN fields. ActualH/R alias/physicaleffects remainopen',
   'JT2flagcapturedzero path clearsflag,SWcallerRAframe120,linkedcallsleaf,LWRAframe120,RET;needsvalidframe/global/dynamicextents,nondestructivealias andaccessconditions;notgateway/MRET path'],
  actual_binding_buffer_contents_length_trap_delivery_atomicity_pollprogress_or_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-JT2-zero-path-status-leaf-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=892,complete_phase_body_instructions=316,reused_nonzero_leaf_bytes=520,reused_dispatch_body_bytes=2218,reused_dispatch_table_bytes=104,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['B124/B125 actualdispatchconsumers/writers andcallbackordering','actualP contentsproducer/ingresslength/initialization','actualinstalledproviders/physicaleffects/freshpointerequality/pollprogress/fullownershiplifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],446);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-STARTS[i];size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('IRQzero instructionmutation escaped')
   mutations+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('IRQzero typedmutation escaped')
   typed+=1
 check((mutations,typed)==(316,22),'IRQzero mutationcensus')
 print('PASS:316 instruction/22 typed-load mutations rejected;fullDAG/all21stores/field-snapshot/caller-frame certificates')


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
 else:check(OUT.read_bytes()==encoded,'IRQzero exactledger replay')
 print('PASS:892B/316i complete JT2zero leaf;strictHEX;65536 bit/65536 fresh-nibble cases;exactledger')
 print('PASS:NO target execution/emulation;bufferlength/content/provider/delivery/order/lifetime UNPROVED')


if __name__=='__main__':main()
