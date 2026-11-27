"""Offline complete JT2 nonzero status leaf and callback ordering composition.
Original operands, immutable CFG paths and host bit-field arithmetic only.
No target execution/emulation, mutable RAM/packet/MMIO/trap/provider model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_buffer_origin_static as previous
import check_v4160_b1_attempt_static as attempt
import check_v4160_hook_lifetime_static as hook
import check_v4160_context_callback_frame_static as context
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=attempt.FIELDS,attempt.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-irq-status-static.json')
STARTS=(0x20002b4c,0x20002b98)
SOURCES=(0x42dbc,0x42e48)
HASHES=('cfdca0786ab01e2c8b6dc2bdd341d922944bc9da5fd62bb4536c9c62bcc98dcb','4c25a996cad6862b92b139a6ae7f1e89a43ad0e72ca09d96ba82eb427b2595a2')
LITERAL='''
000 lui 15 536883200
004 load 15 15 1340 4
008 lui 13 536883200
00c addi 14 13 1300
010 load 12 15 8 4
012 store 14 12 24 4
014 load 12 15 8 4
016 srli 12 12 3
018 andi 12 12 1
01a beqz 12 46
01c load 12 14 2 1
01e ori 12 12 1
022 store 14 12 2 1
024 addi 12 0 -128
028 store 14 12 4 1
02a li 12 8
02c store 15 12 8 4
02e load 12 15 8 4
030 andi 12 12 1
032 beqz 12 64
034 load 12 14 1 1
036 ori 12 12 1
03a store 14 12 1 1
03c li 12 1
03e store 15 12 8 4
040 load 12 15 8 4
042 srli 12 12 2
044 andi 12 12 1
046 bnez 12 80
048 load 12 15 8 4
04a srli 12 12 1
04c andi 12 12 1
04e beqz 12 154
050 store 14 0 5 1
054 load 12 15 8 4
056 lui 11 536883200
05a load 11 11 1288 4
05e srli 12 12 2
060 andi 12 12 1
062 beqz 12 248
064 load 12 11 0 4
066 srli 12 12 12
068 andi 12 12 3
06a bnez 12 242
06c load 10 15 80 4
06e load 12 14 36 4
070 andi 10 10 32
074 load 12 12 1 1
076 beqz 10 198
078 bnez 12 236
07a addi 12 0 93
07e store 15 12 28 4
080 load 12 13 1300 1
084 ori 12 12 1
088 store 13 12 1300 1
08c li 13 4
08e store 15 13 8 4
090 load 13 11 44 4
092 andi 13 13 -4
094 ori 13 13 1
098 store 11 13 44 4
09a load 13 15 8 4
09c slli 12 13 18
0a0 bge 12 0 182
0a4 load 13 14 4 1
0a6 slli 13 13 24
0a8 srai 13 13 24
0aa bge 13 0 178
0ae li 13 1
0b0 store 14 13 4 1
0b2 lui 14 8192
0b4 store 15 14 8 4
0b6 load 14 15 8 4
0b8 slli 13 14 16
0bc bge 13 0 196
0c0 lui 14 32768
0c2 store 15 14 8 4
0c4 jr 1
0c6 beqz 12 122
0c8 li 10 1
0ca bne 12 10 212
0ce addi 12 0 97
0d2 jump 126
0d4 li 10 2
0d6 bne 12 10 224
0da addi 12 0 101
0de jump 126
0e0 li 10 3
0e2 bne 12 10 236
0e6 addi 12 0 105
0ea jump 126
0ec addi 12 0 107
0f0 jump 126
0f2 addi 12 0 108
0f6 jump 126
0f8 load 13 14 3 1
0fa ori 13 13 1
0fe store 14 13 3 1
100 li 13 2
102 jump 142
'''
TYPED=((4,2),(0x5a,2),(0x80,4))
QK=((0x1c,'3023','qk.c.lbu'),(0x22,'30a3','qk.c.sb'),(0x28,'50a3','qk.c.sb'),(0x34,'1033','qk.c.lbu'),(0x3a,'10b3','qk.c.sb'),(0x74,'1032','qk.c.lbu'),(0xa4,'5423','qk.c.lbu'),(0xb0,'54a3','qk.c.sb'),(0xf8,'3433','qk.c.lbu'),(0xfe,'34b3','qk.c.sb'))


def specs(pc,index):
 out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);args=list(map(int,values))
  check(len(args)==len(FIELDS[op]),'IRQstatus literal fields');d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  if o in (4,0xc,0x5a,0x80,0x88):d['imm']+=80*index
  out[pc+o]=d
 return out


def body(raw,index,pc=None):
 pc=STARTS[index] if pc is None else pc;n=decode(raw,pc);s=specs(pc,index)
 check(n.keys()==s.keys(),'IRQstatus full boundaries')
 for a,f in s.items():init.g(n,a,'IRQstatus '+hex(a-pc),**f)
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'IRQstatus typed load')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'IRQstatus exact QK byte access')
 check((len(raw),len(n),sha256(raw).hexdigest())==(260,100,HASHES[index]),'IRQstatus complete identity')
 edges={}
 for a,d in n.items():
  op=d['op'];q=[] if op=='jr' else [a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  if op=='jump':q=[d['target']]
  check(op not in ('jal','jalr','call_indirect','csr','mret','ecall') and all(z in n for z in q),'IRQstatus leaf closedCFG/no calls/traps')
  if op=='jr':check(d['rs1']==1,'IRQstatus ordinary RET')
  edges[a]=q
 check(attempt.common.acyclic(edges),'IRQstatus complete DAG')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and [a-pc for a,qs in edges.items() if not qs]==[0xc4],'IRQstatus complete reachability/soleRET')
 writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
 check(writes==list(range(10,16)),'IRQstatus onlyA0..A5 writes/noSP/RA/GP/S/CSR')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(0x12,14,12,24,4),(0x22,14,12,2,1),(0x28,14,12,4,1),(0x2c,15,12,8,4),(0x3a,14,12,1,1),(0x3e,15,12,8,4),(0x50,14,0,5,1),(0x7e,15,12,28,4),(0x88,13,12,1300+80*index,1),(0x8e,15,13,8,4),(0x98,11,13,44,4),(0xb0,14,13,4,1),(0xb4,15,14,8,4),(0xc2,15,14,8,4),(0xfe,14,13,3,1)]
 check(stores==expected,'IRQstatus all15 stores')
 check([a-pc for a,d in n.items() if d.get('rd')==15]==[0,4] and [a-pc for a,d in n.items() if d.get('rd')==14]==[0xc,0xb2,0xb6,0xc0],'IRQstatus heldH and lateA4 reuse')
 return dict(start=pc,bytes=260,sha256=HASHES[index],instructions=list(n.values()),CFG=edges,stores=stores,calls=[],returns=[pc+0xc4],GPR_writes=writes,complete_local_body=True)


def witnesses(b):
 # All paths are syntactic CFG witnesses, not feasible device/state traces.
 pc=b['start'];paths=[]
 def visit(a,seq):
  seq=seq+[a-pc]
  if not b['CFG'][a]:paths.append(seq)
  else:
   for z in b['CFG'][a]:visit(z,seq)
 visit(pc,[])
 check(all(p[-1]==0xc4 for p in paths),'IRQstatus all paths normalRET')
 for p in paths:
  if 0x74 in p:check(all(o in p for o in (0x50,0x54,0x64,0x6c,0x6e)) and p.index(0x6e)<p.index(0x74),'IRQstatus packetbyte source precedes use')
  check((0x7e in p)==(0x88 in p) and (0x22 in p)==(0x28 in p)==(0x2c in p),'IRQstatus code/setS0 and bit3 write groups')
  check((0xfe in p)==(0x100 in p) and not (0x74 in p and 0xfe in p),'IRQstatus distinct freshbit2 branches')
  if 0x7e in p:check(p.index(0x7e)<p.index(0x88)<p.index(0x8e)<p.index(0x98),'IRQstatus selectedcode/S0/H8/R44 order')
  if 0xb0 in p:check(p.index(0xa4)<p.index(0xb0)<p.index(0xb2),'IRQstatus S4 dereference beforeA4reused')
  check(0xb6 in p and p.index(0xb6)<p.index(0xbc),'IRQstatus final freshH8 bit15')
 chosen={}
 for p in paths:
  key=next((hex(o) for o in (0x7a,0xce,0xda,0xe6,0xec,0xf2,0xfe) if o in p),'no_code_or_S3')
  chosen.setdefault(key,p)
 check(len(paths)==456 and len(chosen)==8,'IRQstatus exactpath census/eight branch witnesses')
 return dict(syntactic_path_count=len(paths),all_paths_sha256=sha256(json.dumps(paths,separators=(',',':')).encode()).hexdigest(),selected_witnesses=chosen,actual_feasibility_or_dispatch_proved=False)


def domains():
 for x in range(65536):
  check(bool(((x<<18)&0xffffffff)&0x80000000)==bool(x&(1<<13)),'IRQstatus shifted sign isbit13')
  check(bool(((x<<16)&0xffffffff)&0x80000000)==bool(x&(1<<15)),'IRQstatus shifted sign isbit15')
 for x in range(256):
  shifted=(x<<24)&0xffffffff;signed=(shifted^0x80000000)-0x80000000
  check((signed>>24)==(x if x<128 else x-256),'IRQstatus S4 signbyte')
 counts={}
 for bit5 in (0,1):
  values=[(93 if x==0 else 107) if bit5 else (93+4*x if x<=3 else 107) for x in range(256)]
  check(set(values)==({93,107} if bit5 else {93,97,101,105,107}),'IRQstatus byteclass codepartition')
  counts[str(bit5)]={str(v):values.count(v) for v in sorted(set(values))}
 return dict(independent_low16_bit_projection_cases=65536,S4_signed_byte_cases=256,byteclass_cases=512,code_partitions=counts,
  byte_is_class_operand_not_a_length_check=True,fresh_H8_reads_are_separate_observations=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];src=SOURCES[index];raw=init.binding.take(data,src,260)
 check(sparse.captured(mem,src,260)==raw,'IRQstatus complete strictHEX');b=body(raw,index);body(raw,index,src)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];base=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(base+pc-dest==src and dest<=pc and pc+260<=end,'IRQstatus full firstcopy affine mapping')
 cs,cp,flag,nz,z,ch,gh=context.REF_DETAILS[index]
 cr=init.binding.take(data,cs,56);gr=init.binding.take(data,cs-12,8)
 check(sparse.captured(mem,cs,56)==cr and sparse.captured(mem,cs-12,8)==gr and nz==pc,'IRQstatus caller strictHEX/exacttarget')
 caller=context.body(cr,'callback',cp,56,16,3,ch,(flag,nz,z));gateway=context.body(gr,'gateway',cp-12,8,2,0,gh,0x200007a0)
 hs,delta,sh,hh=hook.DETAILS[index];hr=init.binding.take(data,hs,22);hc=init.binding.take(data,hs+22,48)
 check(sparse.captured(mem,hs,70)==hr+hc,'IRQstatus complete setter/consumer strictHEX')
 setter=hook.body(hr,'setter',0x2000078a,delta,sh);consumer=hook.body(hc,'consumer',0x200007a0,delta,hh)
 for source,runtime,size in ((cs,cp,56),(cs-12,cp-12,8),(hs,0x2000078a,22),(hs+22,0x200007a0,48)):
  check(base+runtime-dest==source and dest<=runtime and runtime+size<=end,'IRQstatus reused full firstcopy mapping')
 ar=init.binding.take(data,attempt.STARTS[index],502);cbpc=previous.previous.STARTS[index];cbr=init.binding.take(data,cbpc,430)
 check(sparse.captured(mem,attempt.STARTS[index],502)==ar and sparse.captured(mem,cbpc,430)==cbr,'IRQstatus attempt/completion strictHEX')
 ab=attempt.body(ar,index);completion=previous.previous.body(cbr,index)
 an={d['pc']-ab['start']:d for d in ab['instructions']};cn={d['pc']-cbpc:d for d in completion['instructions']}
 check(an[0x1ba]['imm']+an[0x1c0]['imm']==cbpc and an[0x1da]['imm']==cn[0x16c]['imm']==cn[0x19e]['imm']==12,'IRQstatus completionliteral/clear/store joins')
 check(an[0x1da]['rs2']==0 and cn[0x166]['imm']==2 and cn[0x19c]['imm']==-1,'IRQstatus outerzero vscompletion2/FF')
 check(caller['calls'][0]['target']==hex(pc) and gateway['calls'][0]['target']==consumer['start'],'IRQstatus JT2leaf/gatewayhook joins')
 S=0x20003514+80*index;C=S+76;slot=0x20003000+delta
 check(S+36==0x20003538+80*index and len({slot,slot+4,C+12,S+2,S+3})==5,'IRQstatus distinct literalcells')
 check(S+28<=C+12 and slot+5<=S and S+40<C+12,'IRQstatus fixed status/slot extents excludeC12')
 bn={d['pc']-pc:d for d in b['instructions']}
 check([o for o,d in bn.items() if d['op']=='load' and d['rs1']==15 and d['imm']==8]==[0x10,0x14,0x2e,0x40,0x48,0x54,0x9a,0xb6],'IRQstatus eight distinctH8load sites')
 return dict(label=init.binding.PROFILES[index][0],flash_source=src,first_copy=mapping['first_copy'],body=b,CFG_certificates=witnesses(b),
  reused_bodies=dict(JT2_callback=caller,gateway=gateway,setter=setter,consumer=consumer,attempt=ab,completion=completion),
  nominal_globals=dict(S=S,C=C,Hslot=S+40,Rslot=S-12,hookslot=slot,hookflag=slot+4,completionbyte=C+12),eight_H8_load_sites=[0x10,0x14,0x2e,0x40,0x48,0x54,0x9a,0xb6],
  contract=['hold H=freshU32[Hslot] once;freshU32[H+8] savedS24. Independent freshH8bit3 ->OR1S2,SB128S4,SW8H8;freshH8bit0 ->OR1S1,SW1H8',
   'freshH8bit2 OR separatelyfreshH8bit1 gatesS5clear;another freshH8bit2 clear ->OR1S3,SW2H8,R44low2set1;set ->freshR0bits12..13 nonzero selects108',
   'R0classzero ->freshH80bit5 andfreshP=U32[S36],thenU8[P+1];bit5set:0->93,other->107;bit5clear:0/1/2/3->93/97/101/105,other->107. No null/bounds/length validation orPstores',
   'code ->SWH28;OR1freshS0;SW4H8;R44maskedlow2set1. LaterfreshH8bit13 ->signedS4 test;negative ->S4=1;SWH8=8192. LastfreshH8bit15 ->SWH8=32768',
   'no local calls/frame/CSR/SP/RA/GP/S register writes;onlyA0..A5 GPRdefs;ordinaryRET. Dynamic H/R stores mayalias frame/globals/packet unless excluded separately',
   'JT2 nonzero caller writesframe0 priorCSR341,setsCSR341gateway,linkedcallsleaf thenMRET;leaf preserves CSR/stack GPR directly but memoryalias/physicaleffects and actualtraproute notproven',
   'attempt setter(callbackliteral) ->outerC12clear ->poll;gatewayconsumer captureshookslot thenoptionalindirectcall;normalcompletion2/FF arebothnonzero. No ordering proof versusouterclear, actualdelivery orprogress'],
  actual_installed_binding_buffer_initialization_length_dispatch_order_pollprogress_and_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-JT2-nonzero-status-leaf-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=520,complete_phase_body_instructions=200,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['actualP bytecontentproducer andingresslength','JT2zero-pathcallee andactualtrap/callbackdelivery/order','actualinstalledprovider/physicaleffects/freshpointerequality/fullownershiplifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,SOURCES[i],260);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-STARTS[i];size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('IRQstatus instructionmutation escaped')
   mutations+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('IRQstatus typedmutation escaped')
   typed+=1
 check((mutations,typed)==(200,6),'IRQstatus mutation census')
 print('PASS:200 instruction/6 typed-load mutations rejected;fullDAG/store/GPR/QK andcallback-order joins')


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
 else:check(OUT.read_bytes()==encoded,'IRQstatus exactledger replay')
 print('PASS:520B/200i complete JT2nonzero leaf;strictHEX;65536 bit/512 byteclass cases;exactledger')
 print('PASS:NO target execution/emulation;bufferlength/content/delivery/clearorder/provider/lifetime UNPROVED')


if __name__=='__main__':main()
