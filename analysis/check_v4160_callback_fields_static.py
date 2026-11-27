"""Offline callback field sources and complete write-consumer contract.
Original bytes/CFG, immutable paths and source/interval certificates only.
No target execution/emulation, provider, RAM/heap/callback state model.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_callback_matcher_static as previous
import check_v4160_id11_outer_tail_static as origin
import check_v4160_fallback_initialization_static as startup
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-callback-fields-static.json')
STARTS=(0x4bb22,0x4bbba)
SIZE=164
HASHES=('d5b4b852af03d5c689fa26c0fe92df56ba8eac6698ebb48d39be5d852187b033', '5eb6be3ad020e192796399c867c2db0e15b4018319c78005aa6be4c79ad111e9')
COUNTS=(68, 68)
QK=(((48, 'a887', 'qk.c.lhusp'), (92, '9820', 'qk.c.lbu'), (102, '1c33', 'qk.c.lbu'), (104, '1823', 'qk.c.lbu')), ((48, 'a887', 'qk.c.lhusp'), (92, '9820', 'qk.c.lbu'), (102, '1c33', 'qk.c.lbu'), (104, '1823', 'qk.c.lbu')))
TYPED=(((58, 2), (124, 4), (128, 4)), ((58, 2), (124, 4), (128, 4)))
APPHASH='aabbbc538799c7b18d6e82ba0bcf3384a083ba75f648bb86bdd3b16b41cd3b75'
APPLITERAL="""
000 load 15 8 304 4
004 auipc 13 69632
008 addi 13 13 -448
00c li 12 16
00e li 11 4
010 addi 10 3 0
014 call_indirect 1 15
"""
LITERALS=(
'''
000 addi 2 2 -64
002 store 2 20 40 4
004 mv 20 11
006 store 2 19 44 4
008 addi 11 2 30
00c mv 19 10
00e mv 10 20
010 store 2 8 56 4
012 store 2 18 48 4
014 store 2 21 36 4
016 store 2 1 60 4
018 store 2 9 52 4
01a mv 18 12
01c store 2 13 12 4
01e store 2 14 8 4
020 mv 21 15
022 auipc 1 536563712
026 jalr 1 1 -252
02a li 8 1
02c beqz 10 144
02e mv 9 10
030 load 10 2 30 2
032 li 8 14
034 jal 1 308816
038 beqz 10 144
03a load 16 10 4 4
03e beq 16 0 144
042 load 14 2 8 4
044 load 13 2 12 4
046 mv 15 21
048 mv 12 18
04a mv 11 9
04c mv 10 19
04e call_indirect 1 16
050 mv 8 10
052 bnez 10 144
054 addi 15 0 254
058 beq 21 15 144
05c load 14 9 0 1
05e li 15 2
060 bne 14 15 144
064 load 14 9 4 4
066 load 15 14 1 1
068 load 14 14 0 1
06a slli 15 15 8
06c or 15 15 14
06e slli 15 15 16
070 lui 14 12288
072 srai 15 15 16
074 addi 14 14 -1790
078 bne 15 14 144
07c load 15 18 1 1
080 load 12 18 0 1
084 mv 11 20
086 slli 15 15 8
088 or 12 12 15
08a mv 10 19
08c jal 1 308532
090 mv 10 8
092 load 1 2 60 4
094 load 8 2 56 4
096 load 9 2 52 4
098 load 18 2 48 4
09a load 19 2 44 4
09c load 20 2 40 4
09e load 21 2 36 4
0a0 addi 2 2 64
0a2 jr 1
''',
'''
000 addi 2 2 -64
002 store 2 20 40 4
004 mv 20 11
006 store 2 19 44 4
008 addi 11 2 30
00c mv 19 10
00e mv 10 20
010 store 2 8 56 4
012 store 2 18 48 4
014 store 2 21 36 4
016 store 2 1 60 4
018 store 2 9 52 4
01a mv 18 12
01c store 2 13 12 4
01e store 2 14 8 4
020 mv 21 15
022 auipc 1 536563712
026 jalr 1 1 -404
02a li 8 1
02c beqz 10 144
02e mv 9 10
030 load 10 2 30 2
032 li 8 14
034 jal 1 308968
038 beqz 10 144
03a load 16 10 4 4
03e beq 16 0 144
042 load 14 2 8 4
044 load 13 2 12 4
046 mv 15 21
048 mv 12 18
04a mv 11 9
04c mv 10 19
04e call_indirect 1 16
050 mv 8 10
052 bnez 10 144
054 addi 15 0 254
058 beq 21 15 144
05c load 14 9 0 1
05e li 15 2
060 bne 14 15 144
064 load 14 9 4 4
066 load 15 14 1 1
068 load 14 14 0 1
06a slli 15 15 8
06c or 15 15 14
06e slli 15 15 16
070 lui 14 12288
072 srai 15 15 16
074 addi 14 14 -1790
078 bne 15 14 144
07c load 15 18 1 1
080 load 12 18 0 1
084 mv 11 20
086 slli 15 15 8
088 or 12 12 15
08a mv 10 19
08c jal 1 308684
090 mv 10 8
092 load 1 2 60 4
094 load 8 2 56 4
096 load 9 2 52 4
098 load 18 2 48 4
09a load 19 2 44 4
09c load 20 2 40 4
09e load 21 2 36 4
0a0 addi 2 2 64
0a2 jr 1
''',
)


def literal(rows,pc):
 out={}
 for row in rows.splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'CBfields literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index]
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'CBfields typed load encoding')
 n=decode(raw,pc);s=literal(LITERALS[index],pc);check(n.keys()==s.keys(),'CBfields all boundaries')
 for a,f in s.items():init.g(n,a,'CBfields operand '+hex(a-pc),**f)
 for o,h,m in QK[index]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'CBfields Xwchc encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(164,68,HASHES[index]),'CBfields complete identity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'CBfields ordinary return');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'CBfields linked call');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','CBfields adjacent pair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':check(d['rd']==1 and d['rs1']==16,'CBfields object4 callback');calls.append(dict(offset=a-pc,target='captured U32[object+4] & ~1'))
  check(all(z in n for z in q),'CBfields closed local CFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'CBfields all reachable localDAG')
 check(calls==[dict(offset=o,target=t) for o,t in [(0x26,0x20000a48),(0x34,0x4b650+152*index),(0x4e,'captured U32[object+4] & ~1'),(0x8c,0x4b534+152*index)]],'CBfields four originalcalls')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 check(len(stores)==9 and all(d['base']==2 and d['bytes']==4 for d in stores) and rets==[pc+0xa2],'CBfields all stores stackonly')
 saved={(1,60),(8,56),(9,52),(18,48),(19,44),(20,40),(21,36)}
 check(saved<={(d['source'],d['imm']) for d in stores} and {(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and d['imm']>=36}==saved,'CBfields64Bframe savedrestore')
 check(n[pc+0x90]['op']=='mv' and n[pc+0x90]['rs2']==8 and n[pc+0x50]['rd']==8,'CBfields captured callbackstatus returned afterposthelper')
 return dict(start=pc,bytes=164,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b):
 base={0x2c:0x2e,0x38:0x3a,0x3e:0x42}
 choices={'lookup_null_reply1':{0x2c:0x90},'object_null_reply14':{**base,0x38:0x90},'object4_null_reply14':{**base,0x3e:0x90},
  'callback_nonzero_propagated':{**base,0x52:0x90},'callback0_method254_skip_post':{**base,0x52:0x54,0x58:0x90},
  'callback0_not2_skip_post':{**base,0x52:0x54,0x58:0x5c,0x60:0x90},
  'callback0_type2_otherID_skip_post':{**base,0x52:0x54,0x58:0x5c,0x60:0x64,0x78:0x90},
  'callback0_type2_ID2902_post_replyignored':{**base,0x52:0x54,0x58:0x5c,0x60:0x64,0x78:0x7c}}
 ps={k:common.walk(b,v) for k,v in choices.items()}
 check(0x4e not in ps['object4_null_reply14'] and 0x8c in ps['callback0_type2_ID2902_post_replyignored'],'CBfields callgate paths')
 return ps


def appwindow(image):
 pc=0x8fb8;raw=image[pc-0x8000:pc-0x8000+22];n=decode(raw,pc);s=literal(APPLITERAL,pc)
 check(n.keys()==s.keys(),'CBfields APP window boundaries')
 for a,f in s.items():init.g(n,a,'CBfields APP operand '+hex(a-pc),**f)
 check(sha256(raw).hexdigest()==APPHASH and pc+4+n[pc+4]['imm']+n[pc+8]['imm']==0x19dfc,'CBfields APP callback address formation')
 record=image[0x19dfc-0x8000:0x19e08-0x8000];check(record==bytes.fromhex('000000008c88000000000000'),'CBfields originalAPP threeword source')
 check(image[0x8fce-0x8000:0x8fd0-0x8000].hex()=='3c48','CBfields nextinstruction overwritesA5,noimmediate statusgate')
 return dict(start=pc,bytes=22,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),complete_function=False,
  args=dict(A0='live GP',A1=4,A2=16,A3=0x19dfc),loaded_target='freshU32[liveS0+304] & ~1',nominal_slot_if_S0_40000=0x40130,
  S0_value_and_allpreceding_callee_preservation_proved=False,immediate_return_status_checked=False,
  original_record=dict(address=0x19dfc,bytes=12,hex=record.hex(),sha256=sha256(record).hexdigest(),words=[0,0x888c,0],whole_ABI_or_runtime_preservation_proved=False))


def domains():
 for k in range(65536):
  signed=k if k<32768 else k-65536
  check((signed==0x2902)==(k==0x2902),'CBfields signedpackedU16 ID gate')
 check(set(range(30,32)).isdisjoint(range(36,64)) and set(range(8,16)).isdisjoint(range(30,64)),'CBfields scratchhalfword andborrowedwords vs savedframe')
 check(0x19dfc+4==0x19e00 and 0x19dfc+8==0x19e04,'CBfields three distinct APP fields')
 return dict(packed_U16_ID_cases=65536,posthelper_ID=0x2902,method_comparison='fullword A5==254;not low8 truncation',
  write_callback_field=4,optional_callback_field=8,APP_write_callback=0x888c,APP_optional_callback_initial=0,
  frame_scratch_halfword=[30,32],frame_borrowed_words=[8,16],frame_saved=[36,64],
  actualpointerextents_state_or_call_execution_proved=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,164)
 check(sparse.captured(mem,pc,164)==raw,'CBfields entirewritebody originalHEX')
 b=body(raw,index)
 # Anchor getter and wrapper by their own byte-backed proof, independent of traversal order.
 from check_v4160_typeb0_record_static import body as reader_body
 getter=reader_body(init.binding.take(data,0x4b650+152*index,28),'callbackrecord',index)
 pointer=reader_body(init.binding.take(data,0x4b66c+152*index,22),'callbackpointer',index)
 check(b['calls'][1]['target']==getter['start'],'CBfields writeconsumer->objectgetter join')
 g={v['pc']-getter['start']:v for v in getter['instructions']};pp={v['pc']-pointer['start']:v for v in pointer['instructions']}
 check(g[0x10]['op']=='load' and g[0x10]['imm']==8 and pp[0xa]['op']=='load' and pp[0xa]['imm']==8,'CBfields node8value thenobject8 distinctloads')
 detail=startup.DETAILS[index];initpc=detail[0];ir=init.binding.take(data,initpc,114)
 check(sha256(ir).hexdigest()==detail[11] and sparse.captured(mem,initpc,114)==ir,'CBfields reusedinitializer identity')
 request=startup.binding.constants(data,initpc+70,initpc+102,stop_call=True)
 src,dst,last=detail[6:9];check((request['source'],request['destination'],request['inclusive_last'],request['target'])==(src,dst,last,0x20000010),'CBfields actual secondcopyoperand join')
 object_rows=[]
 for label,offset,words in [('dynamic',0,([0x49156,0x49270,0],[0x491ee,0x49308,0])[index]),('fixed',76,[0,0x4b500+152*index,0])]:
  a=src+offset;o=dst+offset;block=sparse.captured(mem,a,12)
  check(block==b''.join(w.to_bytes(4,'little') for w in words) and dst<=o and o+12<=last+4,'CBfields capturedcallbackobject source insidecopyrange')
  check(o+12<=detail[3],'CBfields objects precede finalzerorange')
  object_rows.append(dict(role=label,source=a,destination_if_copy=o,bytes=12,hex=block.hex(),words=words,all_bytes_captured=True,
   callback8_source_word=0,copy_completion_or_later_preservation_proved=False))
 defaults_pc=origin.STARTS[index][2];db=origin.body(init.binding.take(data,defaults_pc,248),'defaults',index);dn={v['pc']-defaults_pc:v for v in db['instructions']}
 check(dn[228]['imm']+dn[220]['imm']==object_rows[1]['destination_if_copy'] and dn[242]['op']=='store' and dn[242]['imm']==8 and dn[242]['rs2']==0,'CBfields fixeddefaults direct+8zero source')
 slot=init.binding.word(data,0x40130)
 check(slot==(0x4cf22+152*index),'CBfields APP nominalslot append join')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificate=common.certificates(b),paths=paths(b),
  source_callback_records=object_rows,reused_secondcopy=dict(initializer=initpc,sha256=sha256(ir).hexdigest(),request=request,new_code_bytes_counted=0),
  fixed_defaults_reused=dict(start=defaults_pc,sha256=db['sha256'],zero_object8=True,new_code_bytes_counted=0),
  reader_reuse=dict(getter= getter['start'],getter_sha256=getter['sha256'],pointer=pointer['start'],pointer_sha256=pointer['sha256'],new_code_bytes_counted=0),
  APP_nominal_slot=dict(address=0x40130,value=slot,requires_liveS0_40000=True,installed_binding_proved=False),
  contract=['lookup20000a48(originalA1,SP30);captureobjectA0;null->1. SuccessdoesnotlocallyinitializeSP30;freshU16SP30 passedtogetter',
   'getter returnsobjectpointer;null->14. freshU32object4=F,null->14;otherwisecall F&~1(originalA0,lookupobject,originalA2,originalA3,originalA4,originalA5)',
   'savefullcallbackA0 inS0. Nonzero->returnit;zero plusfulloriginalA5!=254 plusfreshU8lookupobject0==2 pluspackedfreshU8[U32lookupobject4+0/1]==2902 ->posthelper',
   'posthelper4b534/4b5cc(originalA0,originalA1,packedfreshsourceA2[0/1]);A3thenliveaftercallback,notreset;A4=2902,A5=sourcebyte1<<8;A6/A7thenlive. posthelperreplyignored,normalfinalA0=S0=0',
   'allstoresinbodyareframeonly;no directcallbackfieldwriter,no payload copy/free. Externalcallee/pointer/retentionbehavior remainsconditional'],
  premises='candidateISA/provider bindings,normalreturn andsavedframe/S/SP/RA preservation;validscratch/object/callback/source extents,finitegetterlist;noadversealias/wrap/IRQ/DMA/reentry;freshread identities keptdistinct',
  allwriters_runtime_records_installedprovider_or_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return dict(schema='TSL9-callback-field-sources-writeconsumer-static-v1',APP_sha256=sha256(image).hexdigest(),APP_window=appwindow(image),profiles=profiles,domains=domains(),
  new_complete_consumer_bytes=328,new_complete_consumer_instructions=136,APP_bounded_window_bytes=22,APP_bounded_window_instructions=7,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['otherwriters andrealrecord preservation;noexhaustivealiasnegativeclaim','20000a48 lookup scratchoutput and4b534 posthelper completeeffects','actualregister/provider/startup/APPpath andobject lifetime'])


def tests(image,carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],164)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('CBfields instructionmutation escaped')
   mutations+=1
  for o,f in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('CBfields typedmutation escaped')
   typed+=1
 for a,d in decode(image[0xfb8:0xfce],0x8fb8).items():
  o=a-0x8000;z=d['size'];bad=bytearray(image);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
  try:appwindow(bad)
  except RuntimeError:pass
  else:raise RuntimeError('CBfields APPmutation escaped')
  mutations+=1
 for o in range(12):
  bad=bytearray(image);bad[0x19dfc-0x8000+o]^=1
  try:appwindow(bad)
  except RuntimeError:pass
  else:raise RuntimeError('CBfields APPfieldmutation escaped')
 check((mutations,typed)==(143,6),'CBfields mutation census');domains()
 print('PASS:143 instruction/6 typed-load/12 APP-record mutations rejected;65536 packed-ID andframe/field certificates')


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
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers)
 encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'CBfields exactledger replay')
 print('PASS:328B/136i fullwriteconsumers +22B/7i boundedAPP;strict HEX/secondcopy/defaults/threefield joins;exact ledger')
 print('PASS:NO target execution/emulation;allwriters,installedbindings,callee effects andpointerlifetime UNPROVED')


if __name__=='__main__':main()
