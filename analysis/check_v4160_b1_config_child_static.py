"""Offline configuration byte derivation and four-field recomputation.
Original operands/immutable CFGs and closed host integer identities only.
No target execution/emulation, mutable object/list/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_worker_leaves_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-config-child-static.json')
ROLES=('byte78','recompute')
SIZES={'byte78':90,'recompute':336}
STARTS=({'byte78': 351722, 'recompute': 351812}, {'byte78': 352042, 'recompute': 352132})
COUNTS={'byte78': 29, 'recompute': 103}
HASHES=({'byte78': 'd093a26951bcc9bf952bfeaf2c348842b1907c08fe84e0b9ce91dedf0b789f16', 'recompute': 'f682f7340c20231cabaa59572654087b4b8170334373a53431e65e0cb1880267'}, {'byte78': 'd093a26951bcc9bf952bfeaf2c348842b1907c08fe84e0b9ce91dedf0b789f16', 'recompute': 'f682f7340c20231cabaa59572654087b4b8170334373a53431e65e0cb1880267'})
LITERALS={
'byte78':"""
000 load 14 10 326 1
004 li 13 2
006 load 15 10 486 2
00a bne 14 13 70
00e load 13 10 328 2
012 addi 15 15 -376
016 beqz 13 36
018 div 15 15 14
01c addi 15 15 -43
020 li 14 8
022 jump 46
024 li 14 8
026 div 15 15 14
02a addi 15 15 -43
02e div 15 15 14
032 load 14 10 484 2
036 slli 15 15 16
038 srli 15 15 16
03a bgeu 15 14 64
03e mv 14 15
040 store 10 14 78 1
044 jr 1
046 li 13 1
048 bne 14 13 84
04c addi 15 15 -68
050 li 14 4
052 jump 46
054 addi 15 15 -80
058 jump 32
""",
'recompute':"""
000 load 15 10 464 2
004 load 14 10 476 2
008 addi 2 2 -16
00a store 2 1 12 4
00c bgeu 15 14 18
010 mv 14 15
012 slli 17 14 16
016 load 15 10 478 2
01a load 14 10 466 2
01e srli 17 17 16
022 bgeu 14 15 40
026 mv 15 14
028 slli 16 15 16
02c load 13 10 472 2
030 load 15 10 468 2
034 srli 16 16 16
038 bgeu 15 13 62
03c mv 13 15
03e load 14 10 470 2
042 load 15 10 474 2
046 slli 6 13 16
04a srli 6 6 16
04e bgeu 14 15 84
052 mv 15 14
054 load 13 10 327 1
058 slli 15 15 16
05a li 14 2
05c srli 15 15 16
05e bne 13 14 114
062 lui 12 4096
064 addi 12 12 -1392
068 mv 14 16
06a bgeu 16 12 138
06e mv 14 12
070 jump 138
072 load 14 10 256 4
076 slli 13 14 20
07a blt 13 0 146
07e lui 12 4096
080 addi 12 12 -1976
084 mv 14 16
086 bltu 12 16 110
08a slli 16 14 16
08e srli 16 16 16
092 load 13 10 326 1
096 li 14 2
098 bne 13 14 274
09c load 14 10 58 2
09e addi 13 0 1250
0a2 mul 14 14 13
0a6 andi 13 17 255
0aa slli 13 13 6
0ac addi 12 13 975
0b0 addi 13 13 1276
0b4 blt 12 16 188
0b8 addi 13 16 300
0bc sub 14 14 13
0be bge 15 14 196
0c2 mv 14 15
0c4 slli 14 14 16
0c6 lui 12 4096
0c8 srli 14 14 16
0ca addi 12 12 -1392
0ce mv 15 14
0d0 bgeu 14 12 214
0d4 mv 15 12
0d6 slli 15 15 16
0d8 srli 15 15 16
0da load 12 10 480 2
0de andi 14 17 255
0e2 andi 13 6 255
0e6 bne 12 14 306
0ea load 12 10 482 2
0ee bne 12 16 306
0f2 load 12 10 484 2
0f6 bne 12 13 306
0fa load 12 10 486 2
0fe bne 12 15 306
102 store 10 0 124 1
106 jal 1 351722
10a li 10 2
10c load 1 2 12 4
10e addi 2 2 16
110 jr 1
112 load 14 10 256 4
116 slli 13 14 20
11a blt 13 0 218
11e lui 12 4096
120 addi 12 12 -1976
124 mv 11 15
126 bgeu 12 15 300
12a mv 11 12
12c slli 15 11 16
130 jump 216
132 li 12 1
134 store 10 12 124 1
138 store 10 14 480 2
13c store 10 16 482 2
140 store 10 13 484 2
144 store 10 15 486 2
148 jal 1 351722
14c li 10 0
14e jump 268
""",
}
PATCHES={'byte78': {}, 'recompute': {262: ('jal', [1, 352042]), 328: ('jal', [1, 352042])}}
TYPED={'byte78': [(0, 4), (6, 5), (14, 5), (50, 5)], 'recompute': [(0, 5), (4, 5), (22, 5), (26, 5), (44, 5), (48, 5), (62, 5), (66, 5), (84, 4), (114, 2), (146, 4), (218, 5), (234, 5), (242, 5), (250, 5), (274, 2)]}
QK={'byte78': [], 'recompute': [(156, '3a3d', 'qk.c.lhu')]}
STORES={'byte78': [(64, 10, 14, 78, 1)], 'recompute': [(10, 2, 1, 12, 4), (258, 10, 0, 124, 1), (308, 10, 12, 124, 1), (312, 10, 14, 480, 2), (316, 10, 16, 482, 2), (320, 10, 13, 484, 2), (324, 10, 15, 486, 2)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'configchild literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'configchild completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'configchild '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'configchild completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'configchild typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'configchild exactQK')
 e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'configchild RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':check(d['rd']==1,'configchild allcallslinked');calls.append(dict(offset=a-pc,target=d['target']))
  check(op not in ('ecall','mret','csr','jalr','call_indirect') and all(z in n for z in q),'configchild closedCFG');e[a]=q
 expected=[] if role=='byte78' else [dict(offset=o,target=STARTS[index]['byte78']) for o in (0x106,0x148)]
 check(calls==expected and rets==[0x44 if role=='byte78' else 0x110],'configchild exactcalls/RET')
 seen=set();active=set()
 def visit(a):
  check(a not in active,'configchild localCFG acyclic')
  if a in seen:return
  active.add(a)
  for z in e[a]:visit(z)
  active.remove(a);seen.add(a)
 visit(pc);check(seen==set(n),'configchild allreachable includingpostRET')
 check(sum(map(len,e.values()))=={'byte78':32,'recompute':120}[role],'configchild exactedgecensus')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'configchild allstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,returns=rets,stores=stores,complete_local_body=True,local_CFG_acyclic=True,target_execution_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ret=pc+b['returns'][0]
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  raise RuntimeError('configchild no syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,ret)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'configchild all-edge witness');walks.append([a-pc for a in p])
 def countpaths(a,z=None):
  cache={}
  def f(a):
   if a==z:return 1
   if a in cache:return cache[a]
   cache[a]=(int(z is None) if not e[a] else sum(f(v) for v in e[a]));return cache[a]
  return f(a)
 preds={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:preds[z].append(a)
 defs={pc+o for o,d in n.items() if d.get('rd')==10 or d['op']=='jal'}
 def last_before(a):
  hits=set();entry=False;todo=preds[a][:];seen=set()
  while todo:
   a=todo.pop()
   if a in defs:hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(preds[a])
  return hits,entry
 last,entry=last_before(ret);args={}
 for c in b['calls']:
  hits,ent=last_before(pc+c['offset']);check(not hits and ent,'configchild eachchild receivesentryP');args[hex(c['offset'])]='entryP'
 selected=[c['offset'] for c in b['calls']]+[d['pc']-pc for d in b['instructions'] if d['op']=='store' and d['rs1']!=2]
 if role=='byte78':
  check(not last and entry and not b['calls'],'configchild leafA0 unchanged')
  check([(o,d['imm'],d['width']) for o,d in n.items() if d['op']=='load']==[(0,326,1),(6,486,2),(0xe,328,2),(0x32,484,2)],'configchild fourfreshloads exactorder')
  check({d['rd'] for d in n.values() if 'rd'in d}=={13,14,15},'configchild noSP/RA/S/P registerdefs')
  check(n[4]['imm']==2 and n[0x46]['imm']==1 and n[0xa]['target']==pc+0x46 and n[0x48]['target']==pc+0x54,'configchild exactmode2/mode1/other branches')
  check(n[0x12]['imm']==-376 and n[0x1c]['imm']==n[0x2a]['imm']==-43 and n[0x4c]['imm']==-68 and n[0x54]['imm']==-80,'configchild signedoffsets')
  check(n[0x20]['imm']==n[0x24]['imm']==8 and n[0x50]['imm']==4 and n[0x16]['target']==pc+0x24,'configchild H0 select8 not2')
  check([o for o,d in n.items() if d['op']=='div']==[0x18,0x26,0x2e] and n[0x36]['imm']==n[0x38]['imm']==16,'configchild signedDIV thenlow16')
  check(n[0x3a]['op']=='bgeu' and n[0x3a]['rs1']==15 and n[0x3a]['rs2']==14 and n[0x40]['imm']==78,'configchild unsignedmin thenlow8store')
  statuses={'entryP':countpaths(pc)}
  facts=dict(frame_bytes=0,object_explicit_extent=488,source_load_order=[326,486,328,484],H328_read_only_mode2=True,normal_reply='entryP unchanged',only_direct_store='low8(min(freshU16P484,low16(signed_formula))) ->P78',no_direct_pointer_publication_or_nested_calls=True,actual_source_validity_or_stability_proved=False)
 else:
  check(last=={0x10a,0x14c} and not entry and n[0x10a]['imm']==2 and n[0x14c]['imm']==0,'configchild normalstatuses exactlastA0defs')
  statuses={str(n[o]['imm']):countpaths(pc,pc+o)*countpaths(pc+o) for o in sorted(last)}
  check(sum(statuses.values())==countpaths(pc),'configchild statuspaths coverallsyntaxpaths')
  check(n[0]['imm']==464 and n[4]['imm']==476 and n[0x16]['imm']==478 and n[0x1a]['imm']==466 and n[0x2c]['imm']==472 and n[0x30]['imm']==468 and n[0x3e]['imm']==470 and n[0x42]['imm']==474,'configchild fourindependent unsignedmin pairs')
  check(n[0x54]['imm']==327 and n[0x92]['imm']==326 and n[0x5a]['imm']==n[0x96]['imm']==2,'configchild twofresh modebytes')
  check(n[0x62]['imm']+n[0x64]['imm']==n[0xc6]['imm']+n[0xca]['imm']==2704 and n[0x7e]['imm']+n[0x80]['imm']==n[0x11e]['imm']+n[0x120]['imm']==2120,'configchild exactfloor/cap constants')
  check(n[0x72]['imm']==n[0x112]['imm']==256 and n[0x76]['imm']==n[0x116]['imm']==20 and n[0x7a]['op']==n[0x11a]['op']=='blt','configchild freshbit11 throughsignedshift')
  check(n[0x9c]['imm']==58 and n[0x9e]['imm']==1250 and n[0xa2]['op']=='mul' and n[0xa6]['imm']==255 and n[0xaa]['imm']==6,'configchild QKfactor1250 andlow8A*64')
  check(n[0xac]['imm']==975 and n[0xb0]['imm']==1276 and n[0xb8]['imm']==300 and n[0xb4]['op']=='blt' and n[0xbc]['op']=='sub' and n[0xbe]['op']=='bge','configchild signedthreshold/signedmin beforelow16')
  check(n[0xc4]['imm']==n[0xc8]['imm']==16 and n[0xd0]['op']=='bgeu' and n[0xd4]['rs2']==12,'configchild trunc16 precedesunsignedfloor')
  check(n[0xde]['imm']==n[0xe2]['imm']==255 and [n[o]['imm'] for o in (0xda,0xea,0xf2,0xfa)]==[480,482,484,486],'configchild low8A/C andfourcurrenthalfwordcompares')
  check(n[0x102]['rs2']==0 and n[0x102]['imm']==124 and n[0x132]['imm']==1 and n[0x134]['rs2']==12 and n[0x134]['imm']==124,'configchild equalclear/mismatchset flag')
  check([n[o]['imm'] for o in (0x138,0x13c,0x140,0x144)]==[480,482,484,486] and n[8]['imm']==-16 and n[0x10e]['imm']==16,'configchild allfourpublished andbalanced16Bframe')
  facts=dict(frame_bytes=16,object_explicit_extent=488,source_min_pairs=[[464,476],[466,478],[468,472],[470,474]],output_halfwords=[480,482,484,486],outputs_480_484_low8=True,equal_arm_flag124=0,mismatch_arm_flag124=1,mismatch_rewrites_allfour=True,normal_statuses=[0,2],calls_receive_entryP=True,mode2_signedmin_low16_then_floor_order_required=True,local_pointer_publication_excludes_frame_and_child_argument=True)
 check((countpaths(pc),statuses)==((8,{'entryP':8}) if role=='byte78' else (4400,{'2':880,'0':3520})),'configchild exactDAG/statuspathcensus')
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),all_local_DAG_path_count=countpaths(pc),syntactic_status_path_counts=statuses,child_A0_arguments=args,last_A0_definitions=sorted(last),entryA0_may_reach_RET=entry,selected_entry_exit_walks={hex(o):[v-pc for v in path(pc,pc+o)+path(pc+o,ret)[1:]] for o in selected},facts=facts,syntactic_walks_are_not_execution_or_feasiblepath_proofs=True)


def trunc0(n,d):
 check(d>0,'configchild closed positive divisor')
 return (1 if n>=0 else -1)*(abs(n)//d)


def domains():
 ranges={};cases=0
 for label in ('mode2_Hnonnull','mode2_Hzero','mode1','othermode'):
  vals=[]
  for x in range(65536):
   if label=='mode2_Hnonnull':q=trunc0(trunc0(x-376,2)-43,8)
   elif label=='mode2_Hzero':q=trunc0(trunc0(x-376,8)-43,8)
   elif label=='mode1':q=trunc0(x-68,4)
   else:q=trunc0(x-80,8)
   check(-32768<=q<=32767 and 0<=q&65535<=65535,'configchild signedformula andtrunc16 domain');vals.append(q);cases+=1
  bounds=[min(vals),max(vals)];check(bounds=={'mode2_Hnonnull':[-28,4067],'mode2_Hzero':[-11,1012],'mode1':[-17,16366],'othermode':[-10,8181]}[label],'configchild exactgenericformula extrema');ranges[label]=bounds
  if label.startswith('mode2'):
   narrowed=vals[2704:];check(min(narrowed)==(140 if label.endswith('Hnonnull') else 31) and min(narrowed)>=0,'configchild preservedmode2floor removesnegativeDIVdomain')
 for m in range(256):check((m==2 or m==1 or m not in (1,2)),'configchild exhaustivebyte modepartition')
 check(-376<=65535-376<=65159 and -68<=65535-68<=65467 and -80<=65535-80<=65455,'configchild no32bitsigned subtractoverflow')
 for a in range(256):
  t=a*64
  check(975<=t+975<=17295 and 1276<=t+1276<=17596,'configchild low8A threshold bounds')
  for b in (0,1,2120,2704,t+975,t+976,65535):
   h=t+1276 if b>t+975 else b+300
   check(300<=h<=17596,'configchild piecewiseH interval')
 check(65535*1250==81918750 and -17596>=-(1<<31) and 81918750-300<(1<<31),'configchild mode2signedproduct/subtraction nooverflow')
 # A closed scalar counterexample to moving unsigned truncation after the floor.
 raw_min=min(0,0*1250-300);folded=max(raw_min&65535,2704)
 check(raw_min==-300 and folded==65236 and folded!=max(raw_min,2704),'configchild min/low16/floor order cannotcommute')
 for v in range(65536):check(0<=v&255<=255 and max(v,2704)>=2704 and min(v,2120)<=2120,'configchild halfword clamp/low8 domains')
 check(488==486+2 and len(TYPED['byte78'])+len(TYPED['recompute'])==20,'configchild extent/loadcensus')
 return dict(generic_leaf_formula_cases=cases,generic_leaf_signed_formula_intervals=ranges,mode2_preserved_X_floor=2704,mode2_preserved_formula_minima={'Hnonnull':140,'Hzero':31},recompute_H_interval=[300,17596],factor1250_product_interval=[0,81918750],closed_truncation_order_witness={'signed_min':-300,'low16_then_floor2704':65236,'reordered_incorrect_result':2704},witness_is_not_reachable_object_or_runtime_observation=True,no_mutable_target_state_model=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'configchild fullstrictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()}
 cp=previous.STARTS[index]['config'];cr=init.binding.take(data,cp,200);check(sparse.captured(mem,cp,200)==cr,'configchild fullconfigcaller HEX');cb=previous.body(cr,'config',index);cc=previous.certificates(cb,'config')
 check(cb['calls']==[dict(offset=0x88,target=bs['byte78']['start'])],'configchild configwrapper target join')
 leafdefs={d['rd'] for d in bs['byte78']['instructions'] if 'rd'in d};check(not leafdefs&{1,2,8,9,10,18,19,20,21,22,23,24,25,26,27},'configchild no callee-saved/SP/RA/P definitions')
 check(bs['byte78']['stores']==[(0x40,10,14,78,1)],'configchild childonlyP78 not124/482/486')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_config_wrapper=dict(start=cp,bytes=200,sha256=cb['sha256'],normal_reply=cc['facts']['normal_reply']),
  contracts=['byte78 leaf noframe/calls/A0/SP/RA/Sdefs,ordinaryreply entryP;onlydirectstore P78 byte,min(freshU16P484,low16(signedDIVformula)),no pointerpublish exceptentryP return. ExplicitPextent488,noguard',
   'mode2 captU16X=P486: iffreshU16P328 nonzero,trunc0((trunc0((X-376)/2)-43)/8);ifzero,trunc0((trunc0((X-376)/8)-43)/8). mode1 trunc0((X-68)/4);othermode trunc0((X-80)/8). Truncationbeforeunsignedmin matters fornegative q',
   'matchingconfigwrapper childonlywritesP78,doesnotlocallyrewriteP124/P482/P486 orretainP;configforce0/fieldstores survive thischild absent otherwriters,aliasing/frame disruption. Source/mode persistence/fullchain ownership notproved',
   'recompute independentfreshmin A=P464/P476,B=P466/P478,C=P468/P472,D=P470/P474;U16outputs P480=low8A,P484=low8C. B clamp usescaptP327:mode2 floor2704,elsefreshP256bit11?unchanged:cap2120',
   'recompute D mode2 capturedP326: t=64low8A,H=(B>t+975?t+1276:B+300),R=1250freshU16P58;D=max(low16(signedmin(D,R-H)),2704). Othermodes freshP256bit11?D:cap2120. Do notcommute low16 andfloor,ormerge P256 reads',
   'recompute freshhalfword equalitychain480/482/484/486 shortcircuits. Equal arm P124=0,child(P),force2. Mismatch arm P124=1,storesallfour outputs480/482/484/486 inthatorder,child(P),force0. Childtakesfreshmode/X/H/Z;matchingbodyonlyP78write',
   'conditionalX>=2704/mode2 retaineduntilleaf givesnonnegativeq min140 or31,notpositiveP78 becausefreshZ may0 andlow8canwrap. Genericnegativeq wraps throughlow16. Noactualinstalledbinding/sourcevalidity/asyncfieldstability orcompleteconsumption/releaseorder proof'],
  actual_binding_field_stability_frame_object_nonaliasing_complete_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-configuration-byte-and-four-field-recompute-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=852,complete_phase_body_instructions=264,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['recomputeactualcallers andsourcewriters/sourcevalidlengths','5d006/5d14e andothernestedservices;clock/arena/recordactualbindings','group post-clear node lifetime,asyncfield/modepreservation,fullconsumption and releaseorder'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('configchild instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('configchild typedmutation escaped')
    typed+=1
 check((mutated,typed)==(264,40),'configchild mutationcensus')
 print('PASS:264 instruction/40 typed-load mutations rejected;complete configuration child contracts')


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
 else:check(OUT.read_bytes()==encoded,'configchild exactledger replay')
 print('PASS:852B/264i complete configchild;strictHEX;DAG statuses/P78-only child/config preservation joins;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/asyncfieldstability/full lifetimes UNPROVED')


if __name__=='__main__':main()
