"""Offline complete request config leaf and reused RAM mode1 composition.
Original-byte operands/immutable CFG and host scalar certificates only.
No target execution/emulation, mutable state model or hardware access.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_request_leaves_static as previous
import check_v4160_constructor_consumer_tail_static as tails
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-request-config-static.json')
STARTS=(0x63c54,0x63d3e)
SIZE=278
HASHES=('82f07fced82ac94eae52ed7927014447b4d2e293589bdb031a252e6c4ee14cfe', 'ebc664f0b8770453ee56ef29260cfb3aeb67305be84d4eeb2f4fe35c0b17f3f5')
COUNTS=(95, 95)
TYPED=(((4, 2), (12, 2), (38, 4), (54, 2)), ((4, 2), (12, 2), (38, 4), (54, 2)))
LITERALS=(
'''
000 lui 15 536883200
004 load 15 15 1292 4
008 beqz 15 34
00a load 13 15 4 4
00c load 16 15 8 4
010 load 14 13 0 4
012 or 14 14 16
016 store 13 14 0 4
018 load 13 15 12 4
01a load 15 15 20 4
01c load 14 13 0 4
01e or 15 15 14
020 store 13 15 0 4
022 lui 14 536883200
026 load 16 14 1296 1
02a lui 15 536883200
02e lui 14 536883200
032 andi 13 10 2
036 load 15 15 1288 4
03a andi 16 16 1
03e addi 14 14 1300
042 beqz 13 166
044 load 13 15 0 4
046 lui 10 4294955008
048 addi 10 10 -1
04a and 13 13 10
04c lui 10 8192
04e or 13 13 10
050 store 15 13 0 4
052 lui 13 589824
056 addi 13 13 134
05a store 15 13 32 4
05c lui 13 137371648
060 addi 13 13 -15
062 store 15 13 20 4
064 lui 13 200704
068 addi 13 13 1561
06c store 15 13 24 4
06e lui 13 12288
070 addi 13 13 -1826
074 store 15 13 40 4
076 lui 13 16801792
07a addi 13 13 784
07e store 15 13 36 4
080 lui 13 4169728
084 bne 16 0 140
088 lui 13 3448832
08c addi 13 13 1247
090 slli 11 11 7
092 store 15 13 16 4
094 addi 11 11 868
098 store 14 11 16 4
09a beqz 12 160
09c slli 12 12 1
09e store 14 12 16 4
0a0 store 14 0 4 1
0a4 jr 1
0a6 lui 13 589824
0aa addi 13 13 131
0ae store 15 13 32 4
0b0 lui 13 135274496
0b4 addi 13 13 -1791
0b8 store 15 13 20 4
0ba lui 13 200704
0be addi 13 13 1572
0c2 store 15 13 24 4
0c4 lui 13 12288
0c6 addi 13 13 -1858
0ca store 15 13 40 4
0cc lui 13 16801792
0d0 addi 13 13 784
0d4 store 15 13 36 4
0d6 beq 16 0 258
0da lui 13 4169728
0de addi 13 13 718
0e2 store 15 13 16 4
0e4 lui 13 4294955008
0e6 addi 16 13 -1
0ea load 13 15 0 4
0ec li 17 1
0ee addi 11 11 5
0f0 and 13 13 16
0f4 bne 10 17 268
0f8 store 15 13 0 4
0fa slli 11 11 3
0fc addi 11 11 60
100 jump 152
102 lui 13 3284992
106 addi 13 13 720
10a jump 226
10c lui 10 4096
10e or 13 13 10
110 store 15 13 0 4
112 slli 11 11 4
114 jump 252
''',
'''
000 lui 15 536883200
004 load 15 15 1372 4
008 beqz 15 34
00a load 13 15 4 4
00c load 16 15 8 4
010 load 14 13 0 4
012 or 14 14 16
016 store 13 14 0 4
018 load 13 15 12 4
01a load 15 15 20 4
01c load 14 13 0 4
01e or 15 15 14
020 store 13 15 0 4
022 lui 14 536883200
026 load 16 14 1376 1
02a lui 15 536883200
02e lui 14 536883200
032 andi 13 10 2
036 load 15 15 1368 4
03a andi 16 16 1
03e addi 14 14 1380
042 beqz 13 166
044 load 13 15 0 4
046 lui 10 4294955008
048 addi 10 10 -1
04a and 13 13 10
04c lui 10 8192
04e or 13 13 10
050 store 15 13 0 4
052 lui 13 589824
056 addi 13 13 134
05a store 15 13 32 4
05c lui 13 137371648
060 addi 13 13 -15
062 store 15 13 20 4
064 lui 13 200704
068 addi 13 13 1561
06c store 15 13 24 4
06e lui 13 12288
070 addi 13 13 -1826
074 store 15 13 40 4
076 lui 13 16801792
07a addi 13 13 784
07e store 15 13 36 4
080 lui 13 4169728
084 bne 16 0 140
088 lui 13 3448832
08c addi 13 13 1247
090 slli 11 11 7
092 store 15 13 16 4
094 addi 11 11 868
098 store 14 11 16 4
09a beqz 12 160
09c slli 12 12 1
09e store 14 12 16 4
0a0 store 14 0 4 1
0a4 jr 1
0a6 lui 13 589824
0aa addi 13 13 131
0ae store 15 13 32 4
0b0 lui 13 135274496
0b4 addi 13 13 -1791
0b8 store 15 13 20 4
0ba lui 13 200704
0be addi 13 13 1572
0c2 store 15 13 24 4
0c4 lui 13 12288
0c6 addi 13 13 -1858
0ca store 15 13 40 4
0cc lui 13 16801792
0d0 addi 13 13 784
0d4 store 15 13 36 4
0d6 beq 16 0 258
0da lui 13 4169728
0de addi 13 13 718
0e2 store 15 13 16 4
0e4 lui 13 4294955008
0e6 addi 16 13 -1
0ea load 13 15 0 4
0ec li 17 1
0ee addi 11 11 5
0f0 and 13 13 16
0f4 bne 10 17 268
0f8 store 15 13 0 4
0fa slli 11 11 3
0fc addi 11 11 60
100 jump 152
102 lui 13 3284992
106 addi 13 13 720
10a jump 226
10c lui 10 4096
10e or 13 13 10
110 store 15 13 0 4
112 slli 11 11 4
114 jump 252
''',
)


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERALS[index].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'requestconfig fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index)
 check(n.keys()==s.keys(),'requestconfig complete boundaries')
 for a,f in s.items():init.g(n,a,'requestconfig '+hex(a-pc),**f)
 for o,f3 in TYPED[index]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'requestconfig typed load')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNTS[index],HASHES[index]),'requestconfig fullidentity')
 e={};rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'requestconfig RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  check(op not in ('jal','jalr','call_indirect') and all(z in n for z in q),'requestconfig no calls/closed CFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and common.acyclic(e) and rets==[pc+0xa4],'requestconfig reachable DAG/soleRET')
 check(not any(d.get('rd') in (1,2,8,9,*range(18,28)) for d in n.values()),'requestconfig no SP/link/S definitions')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 expected=[(0x16,13,14,0,4),(0x20,13,15,0,4),(0x50,15,13,0,4),(0x5a,15,13,32,4),(0x62,15,13,20,4),(0x6c,15,13,24,4),(0x74,15,13,40,4),(0x7e,15,13,36,4),(0x92,15,13,16,4),(0x98,14,11,16,4),(0x9e,14,12,16,4),(0xa0,14,0,4,1),(0xae,15,13,32,4),(0xb8,15,13,20,4),(0xc2,15,13,24,4),(0xca,15,13,40,4),(0xd4,15,13,36,4),(0xe2,15,13,16,4),(0xf8,15,13,0,4),(0x110,15,13,0,4)]
 check(stores==expected,'requestconfig all20 store sites')
 return dict(start=pc,bytes=SIZE,sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,returns=rets,tails=[],calls=[],stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def config_paths(b):
 out={}
 for mode in range(4):
  for descriptor in (0,1):
   for flag in (0,1):
    for override in (0,1):
     c={8:0xa if descriptor else 0x22,0x42:0x44 if mode&2 else 0xa6,
      0x84:0x8c if flag else 0x88,0xd6:0xda if flag else 0x102,
      0xf4:0xf8 if mode==1 else 0x10c,0x9a:0x9c if override else 0xa0}
     seq=common.walk(b,c);out[f'mode{mode}_descriptor{descriptor}_flag{flag}_override{override}']=seq
     check((0x16 in seq)==bool(descriptor) and (0x20 in seq)==bool(descriptor),'requestconfig descriptor bothstores gate')
     check((0x9e in seq)==bool(override) and seq[-2:]==[0xa0,0xa4],'requestconfig optional durationoverride/common clearRET')
     check((0xfc in seq)==(mode<2) and (0x8c in seq)==(mode>=2),'requestconfig mandatoryadd60/add1247 paths')
     check((0x50 in seq)==bool(mode&2) and (0xf8 in seq)==(mode==1) and (0x110 in seq)==(mode==0),'requestconfig modecontrol writes')
 return out


def scalar_certificates(b):
 n={d['pc']-b['start']:d for d in b['instructions']}
 def pair(a,z):return (n[a]['imm']+n[z]['imm'])&0xffffffff
 check(pair(0x46,0x48)==pair(0xe4,0xe6)==0xffffcfff,'requestconfig bits12/13 clear mask')
 high={32:pair(0x52,0x56),20:pair(0x5c,0x60),24:pair(0x64,0x68),40:pair(0x6e,0x70),36:pair(0x76,0x7a)}
 low={32:pair(0xa6,0xaa),20:pair(0xb0,0xb4),24:pair(0xba,0xbe),40:pair(0xc4,0xc6),36:pair(0xcc,0xd0)}
 check(high=={32:589958,20:137371633,24:202265,40:10462,36:16802576} and low=={32:589955,20:135272705,24:202276,40:10430,36:16802576},'requestconfig fixedwords')
 flagwords={'mode2_3_flag0':pair(0x88,0x8c),'mode2_3_flag1':pair(0x80,0x8c),'mode0_1_flag0':pair(0x102,0x106),'mode0_1_flag1':pair(0xda,0xde)}
 check(flagwords=={'mode2_3_flag0':3450079,'mode2_3_flag1':4170975,'mode0_1_flag0':3285712,'mode0_1_flag1':4170446},'requestconfig flagword additions')
 check(n[0x90]['imm']==7 and n[0x94]['imm']==868 and n[0xee]['imm']==5 and n[0xfa]['imm']==3 and n[0x112]['imm']==4 and n[0xfc]['imm']==60 and n[0x9c]['imm']==1,'requestconfig duration operands')
 return dict(high_mode_words=high,low_mode_words=low,flag_words=flagwords,mask=0xffffcfff,
  duration='mode&2:(entryA1<<7)+868;else fullmode==1:((entryA1+5)<<3)+60;else:((entryA1+5)<<4)+60;all low32;entryA2nonzero overwrites with low32(entryA2<<1)',
  reply='full entrymode==1:1;entrymode&2:8192;otherbit1clear:4096;not generic success')


def domains():
 classes=[0,0,0]
 for mode in range(65536):
  k=2 if mode&2 else 1 if mode==1 else 0;classes[k]+=1
  check((k==2)==bool(mode&2) and (k==1)==(mode==1),'requestconfig full16mode partition')
 check(classes==[32767,1,32768],'requestconfig modeclass count')
 requests=[]
 for mode in range(4):
  amount=33508 if mode&2 else 2140 if mode==1 else 4220;reply=8192 if mode&2 else 1 if mode==1 else 4096
  check(amount==((255<<7)+868 if mode&2 else ((255+5)<<(3 if mode==1 else 4))+60),'requestconfig request255 arithmetic')
  requests.append(dict(mode=mode,status_word16=amount,reply=reply,control_bits12_13=2 if mode&2 else 0 if mode==1 else 1))
 for x in (0,1,255,65535,0x7fffffff,0xffffffff):
  for shift in (1,3,4,7):check(((x<<shift)&0xffffffff)==((x*(1<<shift))%2**32),'requestconfig fixedwidth shifts')
 picks=[0,0,0]
 for first in range(4):
  for second in range(4):picks[0 if first==0 else 1 if second==2 else 2]+=1
 check(picks==[4,3,9],'requestconfig RAM independentlyfresh durationpick partition')
 return dict(mode_low16_cases=65536,mode_partition=classes,request_modes=requests,RAM_mode1_ignores_entry_A1_A2=True,
  RAM_fresh_control_pairs=16,RAM_duration_partition=picks,normal_RAM_mode1_reply=1,target_execution_or_emulation=False)


def ram_paths(b):
 base={0x10:0x7e,0x80:0x9e,0xa0:0xa4,0x68:0x6a,0x6e:0x70,0x72:0x74};out={}
 for name,choose in {'duration406':{0xd6:0xd8},'duration1086':{0xd6:0xe2,0xea:0xee},'duration446':{0xd6:0xe2,0xea:0xf4}}.items():
  for exitname,exits in {'wordzero':{},'status2bit':{0x68:0x74},'status3bit':{0x6e:0x74}}.items():
   seq=common.walk(b,{**base,**choose,**exits});out[name+'_'+exitname]=seq
   n={d['pc']-b['start']:d for d in b['instructions']}
   check(not any(n[o].get('rd')==10 for o in seq) and not any(n[o]['op'] in ('jal','jalr','call_indirect') for o in seq),'requestconfig RAMmode1 no A0definitions/calls')
   check(0x14 not in seq and 0x2c not in seq and seq.index(0xac)<seq.index(0xae)<seq.index(0xbc)<seq.index(0xc6)<seq.index(0xde)<seq.index(0x58),'requestconfig RAMmask/fence/restore/poll order')
 return out


def profile(data,hexraw,index,parent):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE)
 check(sparse.captured(mem,STARTS[index],SIZE)==raw,'requestconfig strict originalHEX');b=body(raw,index);n={d['pc']-b['start']:d for d in b['instructions']}
 G=0x20003000;S=G+1300+80*index;F=G+1344+80*index
 check(n[0]['imm']+n[4]['imm']==G+1292+80*index and n[0x22]['imm']+n[0x26]['imm']==G+1296+80*index and n[0x2a]['imm']+n[0x36]['imm']==G+1288+80*index and n[0x2e]['imm']+n[0x3e]['imm']==S,'requestconfig globaladdress sources')
 # Parent contains preceding cleanup evidence; the call-site source comes from its callback-consume ancestor.
 callparent=previous.previous;requestpc=callparent.STARTS[index][1];request=callparent.body(init.binding.take(data,requestpc,328),'request',index)
 check(sparse.captured(mem,requestpc,328)==init.binding.take(data,requestpc,328),'requestconfig original caller HEX')
 rn={d['pc']-requestpc:d for d in request['instructions']}
 check(next(c['target'] for c in request['calls'] if c['offset']==0xc8)==STARTS[index] and next(c['target'] for c in request['calls'] if c['offset']==0xde)==tails.STARTS[index][3],'requestconfig caller pair targets')
 check(rn[0xc0]['imm']==4 and rn[0xc2]['imm']==3 and rn[0xbc]['imm']==255 and rn[0xba]['imm']==0,'requestconfig caller tuple constant operands')
 check(rn[0xcc]['op']=='load' and rn[0xcc]['rd']==11 and rn[0xd0]['imm']==255 and rn[0xd4]['imm']==1 and rn[0xd6]['imm']==4 and rn[0xd8]['imm']==3,'requestconfig independentlyfresh RAMtuple')
 src=tails.SOURCES[index][3];pc=tails.STARTS[index][3];ramraw=init.binding.take(data,src,250)
 check(sparse.captured(mem,src,250)==ramraw,'requestconfig RAM source strictHEX');old=tails.body(ramraw,'ramtail',index)
 ram=dict(old,CFG=old['local_CFG'],returns=[pc+124],tails=[])
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy']
 check(int(first['destination'],16)<=pc and pc+250<=int(mapping['first_copy_end_exclusive'],16) and int(first['source'],16)+pc-int(first['destination'],16)==src,'requestconfig full RAM affine source')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=common.certificates(b),paths=config_paths(b),scalar_certificates=scalar_certificates(b),
  reused_request=dict(start=requestpc,bytes=328,new_code_bytes_counted=0),reused_RAM_body=old,RAM_mode1_paths=ram_paths(ram),
  RAM_mapping=dict(source=src,entry=pc,bytes=250,candidate_first_copy=first,actual_RAM_or_boot_proved=False),
  nominal_globals=dict(status=S,config=F,dynamic_pointer_slot=G+1288+80*index,descriptor_slot=G+1292+80*index,flag_byte=G+1296+80*index),
  config_contract=['optional freshdescriptor nonzero ->twoordered ORstores throughdescriptor+4/mask8 anddescriptor+12/mask20;no innerpointer guards;mayaliaslater sources',
   'freshflag bit0 andfreshdynamicP captured once;no further Pslot reload;no nullguard;mode usesfullA0&2 thenfullA0==1,notlowbyte normalization',
   '20 encodedstore sites,no calls/frame/loops/S/SP/RA definitions;allordinarypaths eventuallySB0S4 andRET;A0branchdependent1/4096/8192;A1/A2canbeclobbered',
   'request (freshF0bits4..5,255,0) givesS16=4220/2140/33508/33508 for0/1/2/3;replies4096/1/8192/8192 ignored;noA2override;doesnotprovememoryreadback underalias'],
  RAM_mode1_contract=['request independentlyfresh(1,F0bits4..5,255) selectsno-callmode1;entryA1/A2notreadbeforeA2overwrite;ordinaryreply remainsA0=1',
   'initialH0+12captured,SWsaved&FFFFDFFF toH0+12,FENCE.I;freshH1 ->SW8192H1+8,SB128S4;twoindependentfreshR0bits12..13 reads choose406/1086/446;SWdurationH1+100,SWsavedoriginalH0wordH1+12',
   'freshH2capturedonce beforepoll;eachiterationfreshS2bit0,thenfreshS3bit0,thenH2word100;anybitsetorword0exits. NoHslotreloadinsidepoll,no timeout/progress proof',
   'H0/H1/H2 andconfigP maydiffer;configupdatesR0 notastableproofRAMreadseesearliermode;aliasedobjects/writers/mapping/providerbinding remainpremises'],
  premises='candidateISA/API/firstcopymapping;validcode/global/dynamicobject/frameextents;ordinarycalleepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshread equalities requireseparateproof',
  actual_hardware_effects_provider_binding_poll_termination_or_complete_pointer_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-request-config-and-RAMmode1-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i,parent['profiles'][i]) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=556,complete_phase_body_instructions=190,reused_RAM_bytes=500,reused_request_bytes=656,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['64794/6487e fullattempthelper andnestedservices','actualglobalwriters/installedproviders andsnapshot stability','borrowedpointerextent/lifetime,hardwareeffects andpollprogress'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);body(raw,i)
  for a,d in decode(raw,STARTS[i]).items():
   o=a-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('requestconfig instruction mutation escaped')
   mutations+=1
  for o,f3 in TYPED[i]:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('requestconfig typed mutation escaped')
   typed+=1
 check((mutations,typed)==(190,8),'requestconfig mutation census');domains()
 print('PASS:190 instruction/8 typed-load mutations rejected;65536 modes/4 request modes/16 freshcontrol pairs;immutable paths andscalar certificates')


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
 else:check(OUT.read_bytes()==encoded,'requestconfig exactledger replay')
 print('PASS:556B/190i complete config leaf;strict HEX;request255 andmappedRAMmode1 joins;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/hardware/pollprogress/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
