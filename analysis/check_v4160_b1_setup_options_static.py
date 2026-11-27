"""Offline setup optional fields, signed length gate and complete packed-word helper.
Original operands/immutable CFG/def-use and closed host scalar identities only.
No target execution/emulation, mutable packet/IRQ/provider model or hardware.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_setup_entry_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-setup-options-static.json')
ROLES=('options','helper')
SIZES={'options':154,'helper':102}
STARTS=({'options': 381172, 'helper': 408938}, {'options': 381500, 'helper': 409172})
COUNTS={'options': 47, 'helper': 37}
HASHES=({'options': '69f73f1b31817ef5c2207b9993e8f3f1904d642621039bca5620261d9e0a11ba', 'helper': 'bde4a781e19112b0c24ed9fa147936ec3659d9d4be2783ad45c8f9aa4d1f938a'}, {'options': '9ef9e9ead714d1fd3e1302a0f650fadc373c9280357c1ab379c70a14b9dfed3d', 'helper': 'f408abcef430c0d867d6c221a0b535936b07c80317e34a87d7cd0cd948069e43'})
LITERALS={
'options':"""
000 li 14 4
002 store 21 14 3 1
006 load 14 24 182 1
00a load 12 24 181 1
00e load 13 24 76 4
012 slli 14 14 6
014 or 14 14 12
016 store 13 14 4 1
018 load 14 21 2 1
01c li 13 0
01e addi 14 14 1
020 store 21 14 2 1
024 load 12 24 184 1
028 load 11 24 181 1
02c load 10 24 182 1
030 jal 1 408938
034 load 14 24 84 4
038 andi 14 14 1024
03c beqz 14 128
03e load 13 21 3 1
042 load 14 24 76 4
046 load 12 21 2 1
04a ori 13 13 8
04e store 21 13 3 1
052 load 13 24 138 2
056 add 14 14 12
058 store 14 13 3 1
05a load 14 21 2 1
05e load 13 24 76 4
062 load 12 24 127 1
066 add 13 13 14
068 load 14 24 138 2
06c slli 12 12 4
06e srli 14 14 8
070 andi 14 14 15
072 or 14 14 12
074 store 13 14 4 1
076 load 14 21 2 1
07a addi 14 14 2
07c store 21 14 2 1
080 load 11 21 2 1
084 load 13 24 132 2
088 addi 14 0 253
08c lui 8 536883200
090 sub 14 14 11
092 addi 8 8 952
096 bge 14 13 680
""",
'helper':"""
000 beqz 10 18
002 lui 14 1073881088
006 load 15 14 72 1
00a ori 15 15 2
00e store 14 15 72 1
012 slli 11 11 3
014 lui 15 536883200
018 store 15 11 1310 1
01c lui 15 536883200
020 load 15 15 1288 4
024 slli 12 12 8
026 or 11 11 12
028 or 11 11 10
02a store 15 11 100 4
02c load 14 15 100 4
02e lui 12 4287102976
032 addi 12 12 -1
034 and 14 14 12
036 lui 12 2621440
03a or 14 14 12
03c store 15 14 100 4
03e load 14 15 100 4
040 ori 14 14 4
044 store 15 14 100 4
046 load 14 15 0 4
048 beqz 13 84
04a lui 13 536870912
04e or 14 14 13
050 store 15 14 0 4
052 jr 1
054 lui 13 536870912
058 and 13 13 14
05a load 14 15 0 4
05c lui 12 3758096384
060 addi 12 12 -1
062 and 14 14 12
064 jump 78
""",
}
PATCHES={'options': {48: ('jal', [1, 409172]), 146: ('addi', [8, 8, 1032])}, 'helper': {24: ('store', [15, 11, 1390, 1]), 32: ('load', [15, 15, 1368, 4])}}
TYPED={'options': [(6, 4), (10, 4), (14, 2), (24, 4), (36, 4), (40, 4), (44, 4), (52, 2), (62, 4), (66, 2), (70, 4), (82, 5), (90, 4), (94, 2), (98, 4), (104, 5), (118, 4), (128, 4), (132, 5)], 'helper': [(6, 4), (32, 2)]}
QK={'options': [(22, 'd8a2', 'qk.c.sb'), (88, '34b3', 'qk.c.sb'), (116, 'd8a2', 'qk.c.sb')], 'helper': []}
STORES={'options': [(2, 21, 14, 3, 1), (22, 13, 14, 4, 1), (32, 21, 14, 2, 1), (78, 21, 13, 3, 1), (88, 14, 13, 3, 1), (116, 13, 14, 4, 1), (124, 21, 14, 2, 1)], 'helper': [(14, 14, 15, 72, 1), (24, 15, 11, 1310, 1), (42, 15, 11, 100, 4), (60, 15, 14, 100, 4), (68, 15, 14, 100, 4), (80, 15, 14, 0, 4)]}


def guard(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);spec={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'setupoptions literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'setupoptions boundaries '+role)
 for a,f in spec.items():init.g(n,a,'setupoptions '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'setupoptions exactidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'setupoptions typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'setupoptions QKexactwidth')
 return n


def body(raw,role,index):
 pc=STARTS[index][role];n=guard(raw,role,index);e={};calls=[];rets=[];frontier=set()
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jr':check(d['rs1']==1,'setupoptions RETthroughRA');q=[];rets.append(a-pc)
  elif op=='jal':check(d['rd']==1,'setupoptions linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  check(op not in ('ecall','mret','csr','jalr','call_indirect'),'setupoptions onlyknowntransfers');e[a]=q;frontier.update(z for z in q if z not in n)
 check(calls==([dict(offset=0x30,target=STARTS[index]['helper'])] if role=='options' else []) and rets==([] if role=='options' else [0x52]),'setupoptions exactcall/RETs')
 check(frontier==({pc+154,pc+0x2a8} if role=='options' else set()),'setupoptions exactfrontiers')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];expected=[(o,b,r,v+80*index if role=='helper' and o==0x18 else v,w) for o,b,r,v,w in STORES[role]]
 check(stores==expected,'setupoptions complete storecensus')
 if role=='helper':check({d['rd'] for d in n.values() if 'rd'in d}=={11,12,13,14,15},'setupoptions helper noframe/call/A0/RA/GP/Sdefs')
 else:check(not any(d.get('rd') in (2,21,24) for d in n.values()),'setupoptions keepsactiveSP/heldQ/heldP')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,linked_calls=calls,returns=rets,outside_window_frontier=sorted(frontier),stores=stores,complete_function_claim=(role=='helper'),actual_callee_or_wholechain_progress_proved=False)


def path_certificate(e,root,expected):
 walks=[];active=set()
 def visit(a,p):
  check(a not in active,'setupoptions acyclicgraph')
  p=p+[a]
  if a not in e or not e[a]:walks.append(p);return
  active.add(a)
  for z in e[a]:visit(z,p)
  active.remove(a)
 visit(root,[])
 edges={(a,z) for a,qs in e.items() for z in qs};covered={(a,z) for p in walks for a,z in zip(p,p[1:])}
 check(edges==covered and len(walks)==expected,'setupoptions allnode/edge/pathcensus')
 return dict(paths=walks,path_count=len(walks),edge_count=len(edges),all_edges_witnessed=True,syntactic_paths_not_target_traces_or_feasibility_proof=True)


def helper_certificate(b,index):
 pc=b['start'];n={d['pc']-pc:d for d in b['instructions']};cert=path_certificate(b['CFG'],pc,4)
 check(cert['edge_count']==38 and n[0]['rs1']==10 and n[0]['target']==pc+0x12,'setupoptions helper optionalxguard')
 check(n[2]['imm']+n[6]['imm']==0x40022048 and n[0xa]['imm']==2 and n[0xe]['width']==1,'setupoptions helper fixedbyteOR2')
 check(n[0x12]['imm']==3 and n[0x18]['imm']==1310+80*index and n[0x20]['imm']==1288+80*index and n[0x24]['imm']==8,'setupoptions helper shifts/H10/Rslot')
 check((n[0x2e]['imm']+n[0x32]['imm'])&0xffffffff==0xff87ffff and n[0x36]['imm']==0x280000 and n[0x40]['imm']==4,'setupoptions helper R100masks/threewrites')
 check(n[0x46]['rs1']==n[0x5a]['rs1']==15 and n[0x46]['imm']==n[0x5a]['imm']==0 and n[0x48]['rs1']==13 and n[0x48]['target']==pc+0x54,'setupoptions helper twoR0samples')
 check(n[0x4a]['imm']==n[0x54]['imm']==0x20000000 and n[0x58]['op']=='and' and n[0x58]['rs2']==14 and ((n[0x5c]['imm']+n[0x60]['imm'])&0xffffffff)==0xdfffffff and n[0x64]['target']==pc+0x4e,'setupoptions helper zeroarm restoresfirstbit29 into secondread')
 check([o for o,d in n.items() if d.get('rd')==15]==[6,0xa,0x14,0x1c,0x20],'setupoptions helperR stableheldpointer afterload')
 return dict(CFG=cert,frame_bytes=0,normal_A0='unchanged entry x',linked_calls=0,local_S0_S11_SP_GP_RA_definitions=False,zero_A3_R0_formula='(second_fresh_R0 & dfffffff) | (first_fresh_R0 & 20000000)',nonzero_A3_R0_formula='first_fresh_R0 | 20000000',A3_zero_is_not_force_bit29_clear=True,physical_register_semantics_or_nonaliasing_proved=False)


def compose(data,mem,index,options):
 pc=previous.STARTS[index];raw=init.binding.take(data,pc,238);check(sparse.captured(mem,pc,238)==raw,'setupoptions priorprefix strictHEX');old=previous.prefix(raw,index);e={**old['selected_CFG'],**options['CFG']}
 check(not set(old['selected_CFG'])&set(options['CFG']) and options['start']==pc+0xee and old['outside_window_frontier']==[pc+0xee,pc+0x122],'setupoptions prior/new exactjoin')
 cert=path_certificate(e,pc,8);check(cert['edge_count']==133 and {p[-1] for p in cert['paths']}=={pc+0x188,pc+0x396},'setupoptions combined2frontiers')
 n={d['pc']-options['start']:d for d in options['instructions']}
 check(n[0]['imm']==4 and n[2]['rs1']==21 and n[2]['imm']==3 and n[0x12]['imm']==6 and n[0x16]['width']==1,'setupoptions firstarm header4/low8packedbyte')
 check([n[o]['imm'] for o in (6,0xa,0xe,0x24,0x28,0x2c)]==[182,181,76,184,181,182] and n[0x1c]['rd']==13 and n[0x1c]['imm']==0,'setupoptions separateheader andhelper argument samples')
 check(n[0x18]['imm']==n[0x20]['imm']==2 and n[0x1e]['imm']==1 and n[0x38]['imm']==1024,'setupoptions countincrement andfreshbit10')
 check(n[0x4a]['imm']==8 and n[0x52]['imm']==n[0x68]['imm']==138 and n[0x42]['imm']==n[0x5e]['imm']==76 and n[0x46]['imm']==n[0x5a]['imm']==n[0x76]['imm']==2,'setupoptions threeindex/twobase/twoword snapshots')
 check(n[0x58]['imm']==3 and n[0x74]['imm']==4 and n[0x6c]['imm']==4 and n[0x6e]['imm']==8 and n[0x70]['imm']==15 and n[0x7a]['imm']==2,'setupoptions splitlowbyte/nibble andcountplus2')
 check(n[0x80]['width']==1 and n[0x84]['width']==2 and n[0x84]['imm']==132 and n[0x88]['imm']==253 and n[0x90]['op']=='sub' and n[0x96]['op']=='bge','setupoptions signed253-c vsU16length afterstores')
 for d in options['instructions']:
  if d['pc']>options['start']+0x30:check(d.get('rs1')!=10 and d.get('rs2')!=10,'setupoptions helperA0 notused inselectedcontinuation')
 return dict(reused_prefix=dict(start=pc,bytes=238,sha256=old['sha256']),combined_prefix_bytes=392,combined_CFG_certificate=cert,combined_exit_offsets=[0x188,0x396],active_frame_bytes=80,no_complete_setup_or_frame_restore_claim=True,helper_A3=0,helper_A0_A1_A2_sources=['freshU8P182','freshU8P181','freshU8P184'],helper_result_not_used_before_selected_frontiers=True,object_or_frame_nonaliasing_or_runtime_path_proved=False)


def record_join(data,mem,index,helper):
 import check_v4160_b1_record_callback_static as record
 pc=record.STARTS[index];raw=init.binding.take(data,pc,1618);check(sparse.captured(mem,pc,1618)==raw,'setupoptions recordcaller fullstrictHEX');b=record.body(raw,index);n={d['pc']-pc:d for d in b['instructions']}
 check(n[0x3d8]['op']=='li' and n[0x3d8]['rd']==13 and n[0x3d8]['imm']==0 and [n[o]['imm'] for o in (0x3de,0x3e2,0x3e6)]==[184,181,182] and n[0x3ea]['target']==helper['start'],'setupoptions secondbytecaller exactargs/join')
 return dict(start=pc,bytes=1618,sha256=b['sha256'],helper_call_offset=0x3ea,A3=0,args_are_separate_fresh_U8_samples=True,earlier_header_samples_not_merged=True,actualobject_identity_or_callorder_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for r in ROLES:
  pc=STARTS[index][r];raw=init.binding.take(data,pc,SIZES[r]);check(sparse.captured(mem,pc,len(raw))==raw,'setupoptions newbytes strictHEX');bs[r]=body(raw,r,index)
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,helper_certificate=helper_certificate(bs['helper'],index),combined_setup=compose(data,mem,index,bs['options']),reused_record_caller=record_join(data,mem,index,bs['helper']),
  contracts=['heldP=S8/heldQ=S5 frompriorprefix;bit9armwritesQ3=4,low8((freshP182<<6)|freshP181) tofreshP76+4,thenfreshQ2+1 mod8;noP181mask meansfields mayoverlap',
   'resampleP184/P181/P182 thenhelper(x,y,z,0);matchinghelper hasno calls/frame/S-registerdefs andreturnsx. xnonzero ->fixedbyte40022048 OR2;H10=low8(y<<3);freshRpointer;R100=low32((y<<3)|(z<<8)|x);twofreshR100 RMWs masksff87ffff/280000 thenOR4',
   'A3zerohelper preservesfirstR0samplebit29 intoanotherfreshR0sample masked dfffffff;notforceclear,not single-readRMW. R/global/fixedaddress overlap andphysicalMMIO effects remainunknown',
   'independentfreshP84bit10:Q3=freshQ3|8;freshbase0=P76/freshidx0=Q2/freshu0=P138 ->SB low8u0 atbase0+idx0+3;newbase1/idx1/u1 andfreshP127 ->SB low8((P127<<4)|((u1>>8)&15)) atbase1+idx1+4;freshidx2 Q2+2 mod8',
   'onlystablecanonical/noninterferingP/Q/helperfields composeinitialcount2 to2/3/4/5 andflags0/4/8/12;not actualinput/contiguity/extent/capacity proof',
   'afteralloptionalwrites freshc=U8Q2,freshlen=U16P132;signed(253-c)>=len ->setup+396 else+188. threshold-2..253,c254/255 nevertake. Itdoesnotprotectpreviouswrites. Frame80 stillactive;completepayload/return/lifetimes unproved'],
  actual_provider_aliases_physicaleffects_capacity_and_complete_lifetimes_proved=False)


def domains():
 M=0xffffffff;B=1<<29;packed_cases=0;nibble_cases=0;merge_cases=0;guard_cases=0
 for x in range(256):
  for y in range(256):
   check((((x<<6)|y)&255)==(((x&3)<<6)|y),'setupoptions unmaskedORbyte formula');packed_cases+=1
  for d in (1,2):check(((x+d)&255)==((x+d)%256),'setupoptions bytecount wrap')
 for word in range(65536):
  for p in (0,15,255):
   check(((p<<4)|((word>>8)&15))&255==((p&15)<<4)|((word>>8)&15),'setupoptions secondbyte nibbleformula');nibble_cases+=1
  for h in (0,0xe0000000):
   second=word|h
   for firstbit in (0,B):
    merged=(second&0xdfffffff)|firstbit;check(merged&B==firstbit and merged&~B==second&~B,'setupoptions separateR0reads mergeidentity');merge_cases+=1
  for c in (2,3,4,5,254,255):
   signed=253-c;encoded=signed&M;decoded=encoded if encoded<1<<31 else encoded-(1<<32)
   check((decoded>=word)==(c<=253 and word<=253-c),'setupoptions signedlengthgate');guard_cases+=1
 family=[]
 for a in (0,1):
  for b in (0,1):
   c=2+a+2*b;f=4*a+8*b;check(2<=c<=5 and f in (0,4,8,12),'setupoptions stablecanonical counts/flags');family.append(dict(bit9=a,bit10=b,count=c,flags=f))
 return dict(unmasked_packed_byte_cases=packed_cases,separate_U16_nibble_family_cases=nibble_cases,separate_R0_merge_family_cases=merge_cases,signed_length_guard_family_cases=guard_cases,length_counts_sampled=[2,3,4,5,254,255],threshold_interval=[-2,253],stable_canonical_family=family,canonical_family_requires_same_valid_P_Q_fields_noaliases_noexternalwriters=True,helper_byteargs_packed_word_formula='low32((y<<3)|(z<<8)|x),OR not disjoint concatenation',closed_host_scalar_identities_only=True,no_target_buffer_or_packet_state_constructed=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-setup-option-fields-and-complete-packed-word-helper-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),new_complete_body_bytes=204,new_complete_body_instructions=74,new_bounded_window_bytes=308,new_bounded_window_instructions=94,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['setup+188/+396 lengthadjust/nextcases/fullreturn','actualP/Q/otherpointerextent/aliases/fieldstability','R/global/fixedregister effects andrealIRQorder/providerbindings','wholeobject/payloadconsumption-release andpointerlifetimes'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for r in ROLES:
   pc=STARTS[i][r];raw=init.binding.take(data,pc,SIZES[r]);n=guard(raw,r,i)
   for d in n.values():
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:guard(bad,r,i)
    except RuntimeError:pass
    else:raise RuntimeError('setupoptions instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[r]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:guard(bad,r,i)
    except RuntimeError:pass
    else:raise RuntimeError('setupoptions typedmutation escaped')
    typed+=1
 check((mutated,typed)==(168,42),'setupoptions mutationcensus')
 print('PASS:168 instruction/42 typed-load mutations rejected;options+completehelper')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'setupoptions exactledger replay')
 print('PASS:204B/74i completehelper+308B/94i options;strictHEX;8combinedpaths/signedgate/freshsample joins;exactledger')
 print('PASS:NO target execution/emulation;actualcapacity/aliases/IRQorder/fullreturn/lifetimes UNPROVED')


if __name__=='__main__':main()
