"""Offline complete packet-field parser and distinct B120 publisher.
Original operands, immutable CFGs and host field/interval certificates only.
No target execution/emulation, mutable packet/provider/RAM/MMIO model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_irq_zero_static as previous
import check_v4160_large_consumer_service_static as service
import check_v4160_list_origin_static as origin
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-packet-fields-static.json')
STARTS=((0x5d9ac,0x5da52),(0x5daf4,0x5db9a))
HASHES=(('2e2294580e608741ab2f8935a195f39a21010cc54d2d924e3a1178e7b9b080a3','cae4d98863b4c785559441d29de05d82159522f9e704aabca42adb200dae69dc'),('f9f3503612c526d063b4603fc7908c2f5c4adc4eebd109399c78079e40432769','e0d5f9c9935727e8831f2d4abca2f7e530e5f3a339f7b45d97f34459ce65e238'))
LITERAL='''
000 addi 2 2 -16
002 store 2 9 4 4
004 mv 9 10
006 load 10 10 80 4
008 store 2 8 8 4
00a addi 12 11 1
00e mv 8 11
010 li 13 0
012 li 11 0
014 store 2 1 12 4
016 auipc 1 536498176
01a jalr 1 1 -904
01e bnez 10 162
020 load 15 9 80 4
022 li 12 7
024 li 10 7
026 load 13 15 0 1
028 andi 13 13 15
02a store 9 13 19 1
02c load 14 15 1 1
02e store 9 14 18 1
030 bne 13 12 138
034 load 13 15 2 1
036 li 10 3
038 srli 12 13 6
03c andi 13 13 63
040 bgeu 13 14 138
044 li 10 5
046 bnez 12 138
048 addi 14 14 -1
04a sub 14 14 13
04c store 8 14 5 1
04e load 14 15 3 1
050 li 10 17
052 andi 13 14 2
056 bnez 13 138
058 andi 13 14 4
05c bnez 13 148
05e addi 15 15 4
060 addi 13 0 255
064 store 8 13 2 1
066 andi 13 14 8
06a li 10 20
06c bnez 13 138
06e andi 13 14 16
072 li 10 21
074 bnez 13 138
076 andi 13 14 32
07a li 10 22
07c bnez 13 138
07e andi 14 14 64
082 beqz 14 156
084 load 15 15 0 1
086 store 8 15 0 1
088 li 10 0
08a load 1 2 12 4
08c load 8 2 8 4
08e load 9 2 4 4
090 addi 2 2 16
092 jr 1
094 load 13 15 4 1
096 addi 15 15 5
098 andi 13 13 3
09a jump 100
09c addi 15 0 127
0a0 jump 134
0a2 li 10 1
0a4 jump 138
'''
QK=((0x26,'9423','qk.c.lbu'),(0x2a,'b4b8','qk.c.sb'),(0x2c,'9833','qk.c.lbu'),(0x2e,'b8a8','qk.c.sb'),(0x34,'b423','qk.c.lbu'),(0x4c,'58b0','qk.c.sb'),(0x4e,'b833','qk.c.lbu'),(0x64,'34a0','qk.c.sb'),(0x84,'9c23','qk.c.lbu'),(0x86,'1ca0','qk.c.sb'),(0x94,'d423','qk.c.lbu'))


def specs(part,index):
 pc=STARTS[index][part];out={}
 rows=LITERAL if part==0 else '000 lui 15 380928\n004 lui 14 536883200\n008 addi 15 15 1476\n00c store 14 15 1072 4\n010 jr 1'
 for row in rows.splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);values=list(map(int,values));check(len(values)==len(FIELDS[op]),'packetfields literalfields')
  d=dict(zip(FIELDS[op],values));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  if part==0 and o==0x1a:d['imm']-=252*index
  if part==1 and o==8:d['imm']+=328*index
  if part==1 and o==0xc:d['imm']+=80*index
  out[pc+o]=d
 return out


def body(raw,part,index):
 pc=STARTS[index][part];n=decode(raw,pc);s=specs(part,index)
 check(n.keys()==s.keys(),'packetfields completeboundaries')
 for a,f in s.items():init.g(n,a,'packetfields '+str(part)+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==((166,68,HASHES[index][0]) if part==0 else (18,5,HASHES[index][1])),'packetfields fullidentity')
 if part==0:
  for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'packetfields exactQKbyte')
 edges={};calls=[]
 for a,d in n.items():
  op=d['op'];q=[] if op=='jr' else [a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  if op=='jump':q=[d['target']]
  if op=='jr':check(d['rs1']==1,'packetfields sole ordinaryRET')
  if op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u['rd']==1 and u['op']=='auipc','packetfields linkedPCpair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(op not in ('jal','call_indirect','csr','mret','ecall') and all(z in n for z in q),'packetfields complete closedCFG');edges[a]=q
 check(previous.previous.attempt.common.acyclic(edges),'packetfields completeDAG')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and [a-pc for a,q in edges.items() if not q]==([0x92] if part==0 else [0x10]),'packetfields allreachable/soleRET')
 check(calls==([dict(offset=0x1a,target=0x2000263a+76*index)] if part==0 else []),'packetfields exactsinglehelpercall')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(2,2,9,4,4),(8,2,8,8,4),(0x14,2,1,12,4),(0x2a,9,13,19,1),(0x2e,9,14,18,1),(0x4c,8,14,5,1),(0x64,8,13,2,1),(0x86,8,15,0,1)] if part==0 else [(0xc,14,15,1072+80*index,4)]
 check(stores==expected,'packetfields allstores/frame')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index][part],instructions=list(n.values()),CFG=edges,stores=stores,calls=calls,complete_local_body=True)


def paths(b):
 pc=b['start'];out=[]
 def visit(a,seq):
  seq=seq+[a-pc]
  if not b['CFG'][a]:out.append(seq)
  else:
   for z in b['CFG'][a]:visit(z,seq)
 visit(pc,[])
 if b['bytes']==166:
  check(len(out)==15,'packetfields parser15path census')
  for p in out:
   check(p[-5:]==[0x8a,0x8c,0x8e,0x90,0x92],'packetfields frame restoration onalllocalreturns')
   if 0xa2 in p:check(not ({0x2a,0x2e,0x4c,0x64,0x86}&set(p)),'packetfields servicefail skipsdirectdatastores')
   if 0x4c in p:check(all(o in p for o in (0x2a,0x2e,0x34,0x40,0x46)),'packetfields lengthgates beforeO5')
   if 0x64 in p:check(0x4c in p and 0x56 in p and ((0x5e in p)!=(0x94 in p)),'packetfields twoheaderextensions beforeO2')
   if 0x86 in p:check(0x64 in p and ((0x84 in p)!=(0x9c in p)),'packetfields O0 sourcebranch')
   if 0x84 in p:check((0x5e in p)!=(0x96 in p),'packetfields optionalcursor P4/P5')
 return dict(syntactic_path_count=len(out),paths=out,actual_input_feasibility_or_call_return_proved=False)


def reaching_definitions(b,reg,sites):
 e=b['local_CFG'];pc=b['start'];n={d['pc']:d for d in b['instructions']};pred={a:set() for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].add(a)
 ins={a:set() for a in e};outs={a:set() for a in e};changed=True
 while changed:
  changed=False
  for a in e:
   incoming=({-1} if a==pc else set()).union(*(outs[z] for z in pred[a]));outgoing={a} if n[a].get('rd')==reg else incoming
   if incoming!=ins[a] or outgoing!=outs[a]:ins[a]=incoming;outs[a]=outgoing;changed=True
 return {hex(o):sorted(a-pc for a in ins[pc+o]) for o in sites}


def domains():
 admitted=0;range_values=set()
 for q in range(256):
  d=q&63;high=q>>6
  check(q==d+64*high and 0<=d<=63 and 0<=high<=3,'packetfields subfieldprojection')
  for length in range(256):
   if high==0 and d<length:
    rem=length-1-d;check(0<=rem<=254,'packetfields admittedbytecount interval');admitted+=1;range_values.add(rem)
 check(admitted==14304 and range_values==set(range(255)),'packetfields fielddomaincensus')
 classes={0:0,17:0,20:0,21:0,22:0}
 for flags in range(256):
  code=17 if flags&2 else 20 if flags&8 else 21 if flags&16 else 22 if flags&32 else 0;classes[code]+=1
  check(bool(flags&4)==bool((flags>>2)&1) and bool(flags&64)==bool((flags>>6)&1),'packetfields cursor/optionalbyte bits')
 check(classes=={0:16,17:128,20:64,21:32,22:16},'packetfields rejectionpriority bytepartition')
 return dict(subfield_length_cases=65536,admitted_low6_length_pairs=admitted,remaining_byte_interval=[0,254],flag_priority_byte_cases=256,flag_partition=classes,
  all_local_scalar_results=[0,1,3,5,7,17,20,21,22],required_explicit_N_extent=84,required_explicit_O_extent=6,max_direct_P_extent=6,
  field_length_is_not_a_validated_runtime_buffer_extent=True,no_complete_initialized_output_or_no_write_error_guarantee=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs=[]
 for part,z in ((0,166),(1,18)):
  pc=STARTS[index][part];raw=init.binding.take(data,pc,z);check(sparse.captured(mem,pc,z)==raw,'packetfields fullstrictHEX');bs.append(body(raw,part,index))
 parser,publisher=bs;n={d['pc']-parser['start']:d for d in parser['instructions']};pn={d['pc']-publisher['start']:d for d in publisher['instructions']}
 check(n[4]['rd']==9 and n[4]['rs2']==10 and n[0xe]['rd']==8 and n[0xe]['rs2']==11 and n[0xa]['rd']==12 and n[0xa]['rs1']==11 and n[0xa]['imm']==1 and n[0x10]['imm']==n[0x12]['imm']==0,'packetfields capturedN/O andhelpertuple')
 sp=service.SOURCES[index][4];sr=init.binding.take(data,sp,128);check(sparse.captured(mem,sp,128)==sr,'packetfields reusedservice strictHEX');sb=service.body(sr,'RAMservice',index);sc=service.certificates(sb,'RAMservice')
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(src+sb['start']-dest==sp and sb['start']+128<=end and parser['calls'][0]['target']==sb['start'],'packetfields exacthelper firstcopy join')
 op=origin.STARTS[index][1];orr=init.binding.take(data,op,194);check(sparse.captured(mem,op,194)==orr,'packetfields reusedcreator strictHEX');ob=origin.body(orr,'creator',index);on={d['pc']-op:d for d in ob['instructions']}
 check(on[124]['imm']+on[128]['imm']==0x20003514+80*index and on[134]['imm']==36 and on[134]['rd']==15 and on[138]['rs2']==15 and on[138]['imm']==80,'packetfields conditionalS36->creatorN80 source')
 B=0x200033b8+80*index;target=pn[0]['imm']+pn[8]['imm'];check(target==0x5d5c4+328*index and pn[4]['imm']+pn[0xc]['imm']==B+120 and target!=parser['start'],'packetfields publisher distincttarget/B120')
 dispatch=previous.dispatch;dp=dispatch.STARTS[index];dr=init.binding.take(data,dp,dispatch.SIZES[index]);tr=init.binding.take(data,dispatch.TABLES[index],52)
 check(sparse.captured(mem,dp,len(dr))==dr and sparse.captured(mem,dispatch.TABLES[index],52)==tr,'packetfields reuseddispatch/table strictHEX');db=dispatch.body(dr,tr,index);dn={d['pc']-dp:d for d in db['instructions']};dc=dispatch.certificates(db,index)
 load,call=(0x36e,0x372) if index==0 else (0x370,0x374)
 check(dn[4]['imm']+dn[0x28]['imm']==B and dn[load]['rs1']==9 and dn[load]['imm']==120 and dn[load]['rd']==15 and dn[call]['op']=='call_indirect' and dn[call]['rs1']==15,'packetfields fullB120dispatch reader')
 b125=(0x2d8,0x342) if index==0 else (0x2da,0x344)
 for o in b125:check(dn[o]['imm']==125 and dn[o]['rs1']==9 and dn[o+4]['imm']==1,'packetfields dispatchB125 readsbit0 notIRQOR2/8 bits')
 definitions=reaching_definitions(db,9,[load,*b125]);check(all(ds==[0x28] for ds in definitions.values()),'packetfields fixedB reachingdefinitions atB120/B125readers')
 check(dn[load+2]['op']=='mv' and dn[load+2]['rd']==10 and dn[load+2]['rs2']==8,'packetfields B120callback entryA0 capturedN')
 check(n[0x20]['rs1']==9 and n[0x20]['imm']==80 and n[0x26]['rs1']==15,'packetfields freshP afterservice/nosnapshotidentity')
 return dict(label=init.binding.PROFILES[index][0],bodies=dict(parser=parser,publisher=publisher),CFG_certificates=[paths(b) for b in bs],
  reused_service=dict(start=sb['start'],source=sp,bytes=128,sha256=sb['sha256'],CFG_certificates=sc),reused_creator=dict(start=op,bytes=194,sha256=ob['sha256'],selected_source_operands=[on[o] for o in (124,128,132,134,136,138)]),
  reused_dispatch=dict(start=dp,bytes=len(dr),sha256=db['sha256'],table=db['switch_table'],CFG_certificates=dc,B_base_reaching_definitions=definitions,selected_B120_operands=[dn[o] for o in (load,load+2,call)],selected_B125_operands=[dn[o] for a in b125 for o in (a,a+4,a+6)]),
  published_B120_target=target,B120_target_body_is_still_open=True,
  contract=['parser N=entryA0,O=entryA1;callsservice(freshN80,0,low32(O+1),0). Matching service bypassespacketA0dereference;A2nonnullcanwriteO1 beforelaterparser failure. No complete pointer no-escape/ownership claim',
   'nonzeroservice mapsreply1;zero freshreloadsN80->P;N19=low4(P0),N18=P1 thentype7gate;P2 low6 d/P1 L mustsatisfyd<L,thenP2high2zero;O5=L-1-d',
   'P3bit1 rejects17;bit2setsO2=low2(P4),cursorP5;clearO2=255,cursorP4;bits3/4/5 reject20/21/22 inpriority,afterO5/O2stores;bit6 selectsbytecursor vs127 ->O0,reply0',
   'sourcebytes areindependentfreshloads,notimmutablepacket snapshot;declaredL anddarefields notactualingresslength/extent;directP0..P5 readneedmax6bytes,Nextent84,Oextent6,noownnullguards',
   'creator freshS36 word ->createdN80 onlyunderallocation/fill/source/callee/nonalias/lifetime premises;parserentryN actualidentity/currentN80 preservation unproved',
   'separatepublisher writesB120=5d5c4/5d70c,notparser. DispatchfreshB120 callbackhasnonullguard;actualpublisher-beforeconsumer/order/retention/targetbody1000Bstillopen',
   'dispatchB125two readers testbit0,whereIRQzero OR2/OR8 writesbit1/3;do nottreat asmatchingcompletionbits orclaimallB125consumerscovered'],
  actual_installed_binding_input_contents_length_initialized_outputs_dispatch_order_and_full_lifetimes_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-packet-fields-parser-B120-publisher-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=368,complete_phase_body_instructions=146,reused_service_bytes=256,reused_creator_bytes=388,reused_dispatch_body_bytes=2218,reused_table_bytes=104,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['fullB120target5d5c4/5d70c andB125bit1waits','actualPcontentsproducer/ingresslength andentryobjectidentity','actualproviderbinding/callbackorder/fullpointerownershiplifetimes'])


def tests(carriers):
 count=0
 for i,data in enumerate(carriers):
  for part,z in ((0,166),(1,18)):
   pc=STARTS[i][part];raw=init.binding.take(data,pc,z);b=body(raw,part,i)
   for d in b['instructions']:
    o=d['pc']-pc;size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('packetfields instructionmutation escaped')
    count+=1
 check(count==146,'packetfields mutationcensus')
 print('PASS:146 instruction mutations rejected;completeparser/publisher CFG,frame,outputs andsource/callback joins')


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
 else:check(OUT.read_bytes()==encoded,'packetfields exactledger replay')
 print('PASS:368B/146i completeparser/publisher;strictHEX;65536 fieldpairs/256 flagcases;exactledger')
 print('PASS:NO target execution/emulation;actualbufferlength/content/provider/binding/lifetime UNPROVED')


if __name__=='__main__':main()
