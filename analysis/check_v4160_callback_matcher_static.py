"""Offline width-dispatch matcher and 2-to-16-byte expansion contracts.
Original operands/CFG, immutable paths and host scalar/interval certificates.
No target execution/emulation or provider/register/RAM/heap state machine.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_callback_validator_static as previous
import check_v4160_comparator_tail_static as comparator
import check_v4160_app_nv_callbacks_static as copier
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
OUT=Path(__file__).with_name('v4160-callback-matcher-static.json')
PARTS=('matcher','expand')
STARTS=((0x44624,0x445e6),(0x446b8,0x4467a))
SIZES=(102,62)
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
HASHES=(('b5595b11c4a9369796902cd50b0bf47641f9c0180d0975f88cc53fda6e09ac50', '959d4bb28b34668fb6e4d7829a1f3832d23045c66f6d5ab767ad8480b2a267bb'), ('e5798381c106490e650174243bac5dc5b574a45fc05e787e4b3024f5a20a16df', 'b5b186b23bf8c9717abd03d156974e179efc82d839c7a26a497de935b687d887'))
COUNTS=((43, 27), (43, 27))
LITERALS=(
{
'matcher':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 1 28 4
008 li 14 2
00a mv 9 10
00c mv 8 12
00e beq 11 14 80
012 li 12 16
014 li 15 0
016 bne 11 12 44
01a beq 13 14 56
01e bne 13 11 44
022 jump 84
024 li 14 16
026 li 15 0
028 beq 13 14 68
02c load 1 2 28 4
02e load 8 2 24 4
030 load 9 2 20 4
032 mv 10 15
034 addi 2 2 32
036 jr 1
038 mv 11 2
03a mv 10 8
03c jal 1 280038
03e li 12 16
040 mv 11 2
042 jump 88
044 mv 11 2
046 jal 1 280038
048 li 12 16
04a mv 11 2
04c mv 10 8
04e jump 90
050 bne 13 11 36
054 mv 12 11
056 mv 11 8
058 mv 10 9
05a auipc 1 536592384
05e jalr 1 1 -572
062 mv 15 10
064 jump 44
''',
'expand':'''
000 beqz 10 58
002 addi 2 2 -16
004 store 2 9 4 4
006 store 2 1 12 4
008 store 2 8 8 4
00a mv 9 10
00c li 10 0
00e beqz 11 48
010 mv 8 11
012 lui 11 450560
016 mv 10 8
018 li 12 16
01a addi 11 11 880
01e auipc 1 536592384
022 jalr 1 1 -722
026 load 15 9 0 1
028 li 10 1
02a store 8 15 12 1
02c load 15 9 1 1
02e store 8 15 13 1
030 load 1 2 12 4
032 load 8 2 8 4
034 load 9 2 4 4
036 addi 2 2 16
038 jr 1
03a li 10 0
03c jr 1
''',
},
{
'matcher':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 1 28 4
008 li 14 2
00a mv 9 10
00c mv 8 12
00e beq 11 14 80
012 li 12 16
014 li 15 0
016 bne 11 12 44
01a beq 13 14 56
01e bne 13 11 44
022 jump 84
024 li 14 16
026 li 15 0
028 beq 13 14 68
02c load 1 2 28 4
02e load 8 2 24 4
030 load 9 2 20 4
032 mv 10 15
034 addi 2 2 32
036 jr 1
038 mv 11 2
03a mv 10 8
03c jal 1 280186
03e li 12 16
040 mv 11 2
042 jump 88
044 mv 11 2
046 jal 1 280186
048 li 12 16
04a mv 11 2
04c mv 10 8
04e jump 90
050 bne 13 11 36
054 mv 12 11
056 mv 11 8
058 mv 10 9
05a auipc 1 536592384
05e jalr 1 1 -720
062 mv 15 10
064 jump 44
''',
'expand':'''
000 beqz 10 58
002 addi 2 2 -16
004 store 2 9 4 4
006 store 2 1 12 4
008 store 2 8 8 4
00a mv 9 10
00c li 10 0
00e beqz 11 48
010 mv 8 11
012 lui 11 450560
016 mv 10 8
018 li 12 16
01a addi 11 11 1376
01e auipc 1 536592384
022 jalr 1 1 -870
026 load 15 9 0 1
028 li 10 1
02a store 8 15 12 1
02c load 15 9 1 1
02e store 8 15 13 1
030 load 1 2 12 4
032 load 8 2 8 4
034 load 9 2 4 4
036 addi 2 2 16
038 jr 1
03a li 10 0
03c jr 1
''',
},
)

TEMPLATE=bytes.fromhex('fb349b5f800000800010000000000000')
QK=((0x26,'9c20','load',0,9),(0x2a,'5ca4','store',12,8),
    (0x2c,'9c30','load',1,9),(0x2e,'5cb4','store',13,8))


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*vals=row.split();args=list(map(int,vals));check(len(args)==len(FIELDS[op]),'matcher literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
 check(n.keys()==s.keys(),'matcher complete boundaries')
 for a,f in s.items():init.g(n,a,'matcher '+part+' operand '+hex(a-pc),**f)
 if part=='expand':
  for o,h,op,imm,base in QK:
   d=n[pc+o]
   check(raw[o:o+2].hex()==h and d['op']==op and d['width']==1 and d['imm']==imm and d['rs1']==base and d.get('mnemonic')==('qk.c.lbu' if op=='load' else 'qk.c.sb'),'matcher Xwchc byte encoding')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'matcher complete identity')
 edges={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'matcher ordinary return');rets.append(a);q=[]
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'matcher linked call');calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','matcher adjacent pair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  check(all(z in n for z in q),'matcher closed local CFG');edges[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(edges[a])
 check(seen==set(n) and common.acyclic(edges),'matcher all instructions reachable,local DAG')
 stores=[dict(offset=a-pc,base=d['rs1'],source=d['rs2'],imm=d['imm'],bytes=d['width']) for a,d in n.items() if d['op']=='store']
 expected=({(1,28),(8,24),(9,20)} if part=='matcher' else {(1,12),(8,8),(9,4)})
 check({(d['source'],d['imm']) for d in stores if d['base']==2}==expected and {(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2}==expected,'matcher exact frame save/restore')
 if part=='matcher':
  check(calls==[dict(offset=0x3c,target=STARTS[index][1]),dict(offset=0x46,target=STARTS[index][1]),dict(offset=0x5e,target=0x20000442)],'matcher two expansion calls and comparison target')
  check(len(stores)==3 and rets==[pc+0x36],'matcher only frame stores and one return')
 else:
  check(calls==[dict(offset=0x22,target=0x20000332)] and len(stores)==5 and rets==[pc+0x38,pc+0x3c],'matcher expansion copy/frame/byte stores and returns')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=edges,calls=calls,tails=[],returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part=='matcher':
  choices={
   'unsupported_left':{0xe:0x12,0x16:0x2c},
   'left16_unsupported_right':{0xe:0x12,0x16:0x1a,0x1a:0x1e,0x1e:0x2c},
   'left2_unsupported_right':{0xe:0x50,0x50:0x24,0x28:0x2c},
   'same2':{0xe:0x50,0x50:0x54},
   'same16':{0xe:0x12,0x16:0x1a,0x1a:0x1e,0x1e:0x22},
   'left16_right2':{0xe:0x12,0x16:0x1a,0x1a:0x38},
   'left2_right16':{0xe:0x50,0x50:0x24,0x28:0x44}}
 else:choices={'source_null':{0:0x3a},'destination_null':{0:2,0xe:0x30},'copy_template_patch_two_bytes':{0:2,0xe:0x10}}
 p={label:common.walk(b,v) for label,v in choices.items()}
 if part=='matcher':
  for label in ('same2','same16'):check(0x5e in p[label] and not set((0x3c,0x46))&set(p[label]),'matcher samewidth no expansion')
  check(0x3c in p['left16_right2'] and 0x46 in p['left2_right16'],'matcher expansion side selection')
  for label in ('unsupported_left','left16_unsupported_right','left2_unsupported_right'):check(not set((0x3c,0x46,0x5e))&set(p[label]),'matcher unsupported no childcalls')
  # No branch tests expansion A0 before comparison: its null/failure status is ignored.
  check(p['left16_right2'][p['left16_right2'].index(0x3c)+1:p['left16_right2'].index(0x5e)]==[0x3e,0x40,0x42,0x58,0x5a] and p['left2_right16'][p['left2_right16'].index(0x46)+1:p['left2_right16'].index(0x5e)]==[0x48,0x4a,0x4c,0x4e,0x5a],'matcher expansion reply unchecked')
 else:
  check(0x22 not in p['source_null'] and 0x22 not in p['destination_null'],'matcher null expansion no copy/payload read')
  seq=p['copy_template_patch_two_bytes'];check(seq.index(0x22)<seq.index(0x26)<seq.index(0x2a)<seq.index(0x2c)<seq.index(0x2e),'matcher ordered copy and fresh byte patch')
 return p


def domains():
 # Branch partitions and field packing only: no target comparator, copy, RAM or registers.
 classes=[]
 for L in range(256):
  for R in range(256):
   route=('same' if L==R and L in (2,16) else 'expand_right' if (L,R)==(16,2) else 'expand_left' if (L,R)==(2,16) else 'zero')
   accepted=L in (2,16) and R in (2,16)
   check((route!='zero')==accepted,'matcher fullbyte width partition')
   if accepted:classes.append([L,R,route])
 for k in range(65536):check(((k&255)|(((k>>8)&255)<<8))==k,'matcher allU16 littleendian field packing')
 check(all(L not in (2,16) and R not in (2,16) for L,R in ((256,256),(0xffffffff,0xffffffff))),'matcher fullword equality is not byte-truncated')
 check(set(range(16)).isdisjoint(range(20,32)) and set(range(-16,0)).isdisjoint(range(32)),'matcher scratch and both savedframes separate')
 check(set((12,13))<=set(range(16)) and set((0,1))==set(range(2)),'matcher two-byte patch extents')
 return dict(byte_width_pairs=65536,accepted_byte_width_pairs=classes,U16_field_packing_cases=65536,
  general_widths='A1/A3 compared as fullwords; exactly2or16 accepted,not low8 masks',
  validator_rightwidth_byte_cases=256,validator_necessary_rightwidths=[2,16],
  expanded_template_formula='template[0:12] + source byte0,source byte1 + template[14:16], conditional completed ordinarycopy/freshreads/nonalias',
  frame_intervals=dict(matcher_scratch=[0,16],matcher_saved=[20,32],expansion_frame_relative_to_matcherSP=[-16,0]),
  target_payload_comparison_or_copy_executed=False)


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());bodies={};certs={}
 for k,part in enumerate(PARTS):
  pc=STARTS[index][k];raw=init.binding.take(data,pc,SIZES[k]);check(sparse.captured(mem,pc,SIZES[k])==raw,'matcher full original HEX body')
  b=body(raw,part,index);bodies[part]=b;certs[part]=dict(edges=common.certificates(b),selected=paths(b,part))
 n={v['pc']-STARTS[index][1]:v for v in bodies['expand']['instructions']}
 template_pc=n[0x12]['imm']+n[0x1a]['imm'];check(template_pc==0x6e370+496*index,'matcher exact template pointer')
 check(sparse.captured(mem,template_pc,16)==init.binding.take(data,template_pc,16)==TEMPLATE,'matcher all16templatebytes original HEX anddense')
 # Reuse original startup mapping and existing complete leaf contracts, not an installed RAM claim.
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);m=mapping['first_copy'];reuse={}
 for part,ram,z in [('comparator',0x20000442,72),('copy',0x20000332,58)]:
  source=int(m['source'],16)+ram-int(m['destination'],16)
  check(ram+z<=int(mapping['first_copy_end_exclusive'],16) and source==((0x406b2,0x406f2) if part=='comparator' else (0x405a2,0x405e2))[index],'matcher complete reused leaf mapping')
  raw=init.binding.take(data,source,z);check(sparse.captured(mem,source,z)==raw,'matcher reused leaf original HEX')
  b=comparator.body(raw,'comparator',index) if part=='comparator' else copier.body(raw,'copy',ram,18,init.binding.COPY_HASH)
  reuse[part]=dict(target=ram,source=source,bytes=z,sha256=b['sha256'],new_code_bytes_counted=0,installed_binding_proved=False)
  if part=='copy':check(b['encoded_GPR_writes']==[13,14,15,16],'matcher copy preservesA0/1/2,S/SP/RA locally')
 check(reuse['comparator']['target']==bodies['matcher']['calls'][2]['target'] and reuse['copy']['target']==bodies['expand']['calls'][0]['target'],'matcher reused leaves exact calls')
 pn={v['pc']-parent['body']['start']:v for v in parent['body']['instructions']}
 check(parent['body']['calls'][:2]==[dict(offset=o,target=STARTS[index][0]) for o in (0x26,0x4c)] and pn[0x20]['imm']==2 and pn[0x46]['imm']==2 and pn[0x16]['rd']==13 and pn[0x18]['rd']==12,'matcher validatorcall argument widths andsources')
 references=[]
 for key,base in enumerate((0x6ea90,0x6ea9c)):
  a=base+496*index;raw=sparse.captured(mem,a,2);check(raw==bytes((key,0x28)),'matcher two required reference bytes fully captured')
  receipt=parent['partial_reference_source_windows'][key]
  check(receipt['address']==a and receipt['observed_bytes_or_uncaptured_null'][:2]==tuple(raw),'matcher previous partialwindow joins full required2B prefix')
  expanded=TEMPLATE[:12]+raw+TEMPLATE[14:];check(len(expanded)==16 and expanded[12:14]==raw,'matcher immutable source certificate')
  references.append(dict(address=a,required_direct_bytes=2,captured_hex=raw.hex(),littleendian_U16=int.from_bytes(raw,'little'),expanded16_hex_if_completed_nonalias=expanded.hex(),
   full_12byte_diagnostic_or_following_table_extent_required_by_this_matcher=False))
 return dict(label=init.binding.PROFILES[index][0],bodies=bodies,CFG_certificates=certs,
  original_HEX_complete_body_bytes=164,template=dict(address=template_pc,bytes=16,hex=TEMPLATE.hex(),all_bytes_captured=True),references=references,reused_leaves=reuse,
  matcher_contract=dict(args=['P=A0','left_width=A1','Q=A2','right_width=A3'],
   unsupported='unless both fullword widths in{2,16}:return0,nochildcalls',same_width='compare(P,Q,left_width),returncompletecompareA0',
   left16_right2='expand(Q,SP);ignoreexpansionreply;compare(P,SP,16);returncomparereply',left2_right16='expand(P,SP);ignoreexpansionreply;compare(Q,SP,16);returncomparereply',
   local_payload_accesses=False,nonframe_stores=False,pointer_null_guard=False,helper_status_guard=False),
  expansion_contract=dict(source_null='return0beforeframe/nochild',destination_null='return0afterframe/nochild',
   nonnull='copy(D,template,16);freshU8[source0]->D12;freshU8[source1]->D13;forceA0=1',copy_reply_checked=False,
   no_nonframe_store_of_original_source_pointer=True,scope_of_retention='local instruction stores only; input bytes may themselves be pointer encodings; external provider/MMIO/aliases not excluded'),
  conditional_provider_contract=dict(comparator='controlword4002420c capture/zero,FENCE.I before guards; eitherpointerNULL orlen0 ->1;otherwisefirstfreshbyte mismatch0,allnmatch1;restorecapturedcontrolword onnormalexit',
   copy='samecontrolword/FENCE beforeguards;nullpointer skipscopy;nonnullforwardfreshbyte transfers,n0skips;no capture of entire source snapshot',
   execution_or_physical_sideeffects_observed=False),
  validator_composition=dict(necessary_config0=[2,16],config4_null='with matchingcompare:config0=2 directcompare returns1;config0=16 expandsnonnullROMthencompare withnullQ returns1;otherconfig0 returns0',
   config0_2_nonnull='compare2 fresh config4 bytes against0028 thenifneeded0128;first reference requiring2 bytes is completely captured despite surroundingHEXholes',
   config0_16_nonnull='expand2-byte reference into16-byte template atSP,compare16freshconfig4 bytes;all required ROMbytes captured',
   second_matcher='onlyfirstreply0;config0/config4arefreshlyread again,so no single-source snapshot proof',
   nonzero_reply_does_not_prove_valid_nonnull_pointer=True,remaining_parameter7_16_counter_allocation_publication_gates='reuse previous validator contract'),
  premises='conditionalcandidateISA/startupmapping;codeandnormalcallee/frame/S-register preservation;valid accesses/nonnull scratchSP;noadverseMMIO/payload/frame/code aliases,wrap,IRQ/DMA/reentry;eachfreshread keptdistinct',
  installed_bindings_object8writer_actual_setup_success_or_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))]
 return dict(schema='TSL9-callback-width-matcher-expansion-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=profiles,domains=domains(),
  complete_new_body_bytes=328,complete_new_body_instructions=140,reused_leaf_bytes=260,reused_leaf_instructions=82,C_reconstruction_coverage_changed=False,
  remaining=['callbackobject+8writers andwrapper actualcaller','actual installed providers/MMIO effects andfreshfieldpreservation','pairedlist/config/object allocation andpointer lifetime'],
  target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False)


def tests(carriers):
 mutations=qk=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    off=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('matcher instructionmutation escaped')
    mutations+=1
   if part=='expand':
    for o,h,op,imm,base in QK:
     bad=bytearray(raw);bad[o:o+2]=(int(h[2:]+h[:2],16)^(1<<12)).to_bytes(2,'little')
     try:body(bad,part,i)
     except RuntimeError:pass
     else:raise RuntimeError('matcher Xwchc-offset mutation escaped')
     qk+=1
 check((mutations,qk)==(140,8),'matcher mutation census');domains()
 print('PASS:140 instruction +8 Xwchc offset mutations rejected;65536 width pairs/65536 U16 packing certificates')


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
 else:check(OUT.read_bytes()==encoded,'matcher exact ledger replay')
 print('PASS:328B/140i full matcher/expansion;strict HEX;2-byte references and16-byte templates fully captured;260B reused leaves;exact ledger')
 print('PASS:NO target execution/emulation;installedbindings,physicaleffects,object8writers andpointerlifetime UNPROVED')


if __name__=='__main__':main()
