"""Offline bounded configuration ingress, tail join and two actual caller gates.
Original operands/immutable CFGs and closed host integer identities only.
No target execution/emulation, mutable object/list/provider model.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_config_child_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS=previous.FIELDS
BRANCHES=previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-recompute-callers-static.json')
ROLES=('ingress','gate80','gateflag')
SIZES={'ingress':130,'gate80':94,'gateflag':80}
STARTS=({'ingress': 372666, 'gate80': 378702, 'gateflag': 378796}, {'ingress': 372994, 'gate80': 379030, 'gateflag': 379124})
COUNTS={'ingress': 43, 'gate80': 35, 'gateflag': 30}
HASHES=({'ingress': 'd38640f1f0988ea8e21fe61b824f382d951913363c374cb9a8fa3cca3ee46a45', 'gate80': '79b56a402af4f624f28d403fd5b4b23bd1876267a609349db58af131a0be2434', 'gateflag': 'c2b72002b80ba7617d1744cec70678a72b7a4bd0638c8271518d52d2ff9dad50'}, {'ingress': 'd50f34f5e5a251bd102b04c8d9c8bb2bd8746b56f2214e87c6f97226c03a7a5f', 'gate80': '79b56a402af4f624f28d403fd5b4b23bd1876267a609349db58af131a0be2434', 'gateflag': 'c2b72002b80ba7617d1744cec70678a72b7a4bd0638c8271518d52d2ff9dad50'})
LITERALS={
'ingress':"""
000 load 15 10 276 4
004 addi 6 0 224
008 load 12 15 4 1
00a load 14 15 3 1
00c slli 12 12 8
00e or 12 12 14
010 addi 14 12 -27
014 slli 14 14 16
016 srli 14 14 16
018 bltu 6 14 126
01c load 13 15 6 1
01e load 14 15 5 1
020 lui 16 16384
022 slli 13 13 8
024 or 13 13 14
026 addi 14 13 -328
02a slli 14 14 16
02c srli 14 14 16
02e addi 16 16 328
032 bltu 16 14 126
036 load 14 15 8 1
038 load 17 15 7 1
03c slli 14 14 8
03e or 14 14 17
042 addi 17 14 -27
046 slli 17 17 16
048 srli 17 17 16
04c bltu 6 17 126
050 load 17 15 9 1
054 load 15 15 10 1
056 slli 15 15 8
058 or 15 15 17
05c addi 17 15 -328
060 slli 17 17 16
062 srli 17 17 16
066 bltu 16 17 126
06a store 10 12 472 2
06e store 10 13 474 2
072 store 10 14 476 2
076 store 10 15 478 2
07a jal 0 351812
07e li 10 1
080 jr 1
""",
'gate80':"""
000 load 14 10 22 1
002 li 15 9
004 bne 14 15 88
008 addi 2 2 -16
00a store 2 8 8 4
00c store 2 1 12 4
00e load 13 10 16 1
010 addi 14 0 80
014 mv 8 10
016 li 15 1
018 bne 13 14 64
01c jal 1 372666
020 bnez 10 74
022 load 15 8 160 4
026 store 8 0 43 1
02a ori 15 15 256
02e store 8 15 160 4
032 load 15 8 17 1
034 ori 15 15 -128
038 store 8 15 17 1
03a li 15 1
03c store 8 15 16 1
03e li 15 0
040 load 1 2 12 4
042 load 8 2 8 4
044 mv 10 15
046 addi 2 2 16
048 jr 1
04a load 15 8 42 1
04e ori 15 15 1
052 store 8 15 42 1
056 jump 50
058 li 15 1
05a mv 10 15
05c jr 1
""",
'gateflag':"""
000 load 14 10 22 1
002 li 15 9
004 beq 14 15 22
008 li 10 1
00a jr 1
00c li 10 1
00e load 1 2 12 4
010 load 8 2 8 4
012 addi 2 2 16
014 jr 1
016 load 15 10 264 4
01a addi 2 2 -16
01c store 2 8 8 4
01e store 2 1 12 4
020 andi 15 15 32
024 mv 8 10
026 beqz 15 12
028 jal 1 372666
02c li 15 1
02e beq 10 15 12
032 load 14 8 16 1
034 bne 14 15 66
038 addi 15 0 81
03c store 8 15 16 1
03e li 10 0
040 jump 14
042 load 15 8 168 4
046 ori 15 15 128
04a store 8 15 168 4
04e jump 62
""",
}
PATCHES={'ingress': {122: ('jal', [0, 352132])}, 'gate80': {28: ('jal', [1, 372994])}, 'gateflag': {40: ('jal', [1, 372994])}}
TYPED={'ingress': [(0, 2), (56, 4), (80, 4)], 'gate80': [(34, 2), (74, 4)], 'gateflag': [(22, 2), (66, 2)]}
QK={'ingress': [(8, 'd023', 'qk.c.lbu'), (10, 'b833', 'qk.c.lbu'), (28, 'f423', 'qk.c.lbu'), (30, 'd833', 'qk.c.lbu'), (54, '9827', 'qk.c.lbu'), (84, 'bc27', 'qk.c.lbu')], 'gate80': [(0, '7829', 'qk.c.lbu'), (14, '1429', 'qk.c.lbu'), (50, '1c38', 'qk.c.lbu'), (56, '1cb8', 'qk.c.sb'), (60, '1ca8', 'qk.c.sb')], 'gateflag': [(0, '7829', 'qk.c.lbu'), (50, '1828', 'qk.c.lbu'), (60, '1ca8', 'qk.c.sb')]}
STORES={'ingress': [(106, 10, 12, 472, 2), (110, 10, 13, 474, 2), (114, 10, 14, 476, 2), (118, 10, 15, 478, 2)], 'gate80': [(10, 2, 8, 8, 4), (12, 2, 1, 12, 4), (38, 8, 0, 43, 1), (46, 8, 15, 160, 4), (56, 8, 15, 17, 1), (60, 8, 15, 16, 1), (82, 8, 15, 42, 1)], 'gateflag': [(28, 2, 8, 8, 4), (30, 2, 1, 12, 4), (60, 8, 15, 16, 1), (74, 8, 15, 168, 4)]}


def specs(role,index):
 pc=STARTS[index][role];out={}
 for row in LITERALS[role].splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES[role]:op,v=PATCHES[role][o]
  check(len(v)==len(FIELDS[op]),'recomputecallers literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  out[pc+o]=f
 return out


def body(raw,role,index):
 pc=STARTS[index][role];n=decode(raw,pc);s=specs(role,index);check(n.keys()==s.keys(),'recomputecallers completeboundaries '+role)
 for a,f in s.items():init.g(n,a,'recomputecallers '+role+' '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[role],COUNTS[role],HASHES[index][role]),'recomputecallers completeidentity '+role)
 for o,f3 in TYPED[role]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'recomputecallers typedload')
 for o,h,m in QK[role]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'recomputecallers exactQK')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'recomputecallers RET RA');q=[];rets.append(a-pc)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   if d['rd']==0:q=[];tails.append(dict(offset=a-pc,target=d['target']))
   else:check(d['rd']==1,'recomputecallers linkedcall');calls.append(dict(offset=a-pc,target=d['target']))
  check(op not in ('ecall','mret','csr','jalr','call_indirect') and all(z in n for z in q),'recomputecallers closedlocalCFG');e[a]=q
 expected=[] if role=='ingress' else [dict(offset=0x1c if role=='gate80' else 0x28,target=STARTS[index]['ingress'])]
 check(calls==expected and tails==([dict(offset=0x7a,target=previous.STARTS[index]['recompute'])] if role=='ingress' else []),'recomputecallers exactcalls/tail')
 check(rets=={'ingress':[0x80],'gate80':[0x48,0x5c],'gateflag':[0xa,0x14]}[role],'recomputecallers exactRETs')
 seen=set();active=set()
 def visit(a):
  check(a not in active,'recomputecallers localCFG acyclic')
  if a in seen:return
  active.add(a)
  for z in e[a]:visit(z)
  active.remove(a);seen.add(a)
 visit(pc);check(seen==set(n),'recomputecallers allreachable includingpostRET')
 check(sum(map(len,e.values()))=={'ingress':45,'gate80':36,'gateflag':32}[role],'recomputecallers exactedgecensus')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES[role],'recomputecallers allstores')
 return dict(start=pc,bytes=SIZES[role],sha256=HASHES[index][role],instructions=list(n.values()),CFG=e,local_CFG=e,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,local_CFG_acyclic=True,actual_chain_execution_proved=False)


def certificates(b,role):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']};ends=[a for a,q in e.items() if not q]
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 def finish(a):
  ps=[p for z in ends if (p:=path(a,z)) is not None];check(bool(ps),'recomputecallers suffix');return min(ps,key=len)
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+finish(z)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'recomputecallers all-edge witness');walks.append([a-pc for a in p])
 def countpaths(a,z=None,blocked=()):
  cache={};blocked=set(blocked)
  def f(a):
   if a in blocked:return 0
   if a==z:return 1
   if a in cache:return cache[a]
   cache[a]=(int(z is None) if not e[a] else sum(f(v) for v in e[a]));return cache[a]
  return f(a)
 preds={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:preds[z].append(a)
 def last_before(a,reg):
  defs={pc+o for o,d in n.items() if d.get('rd')==reg or (d['op']=='jal' and d['rd']==1)}
  hits=set();entry=False;todo=preds[a][:];seen=set()
  while todo:
   a=todo.pop()
   if a in defs:hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(preds[a])
  return hits,entry
 args={}
 for c in b['calls']+b['tails']:
  hits,ent=last_before(pc+c['offset'],10);check(not hits and ent,'recomputecallers everyedge passesentryP');args[hex(c['offset'])]='entryP'
 returns={}
 for o in b['returns']:
  hits,ent=last_before(pc+o,10);check(not ent,'recomputecallers normalRET notentryA0');sub={};values=set()
  for d in hits:
   w=n[d]
   if w['op']=='li':values.add(w['imm'])
   else:
    check(w['op']=='mv' and w['rs2']==15,'recomputecallers A0 fromfinalA5');ds,en=last_before(pc+d,15);check(not en and all(n[v]['op']=='li' for v in ds),'recomputecallers finalA5 constants notopaque child');sub[hex(d)]=sorted(ds);values.update(n[v]['imm'] for v in ds)
  check(values<={0,1},'recomputecallers onlynormal0/1');returns[hex(o)]=dict(last_A0_defs=sorted(hits),A5_source_defs=sub,normal_values=sorted(values),syntactic_paths=countpaths(pc,pc+o))
 frame={}
 if role=='ingress':
  check([n[o]['target'] for o in (0x18,0x32,0x4c,0x66)]==[pc+0x7e]*4 and n[4]['imm']==224 and n[0x20]['imm']+n[0x2e]['imm']==16712,'recomputecallers fourguards/constants')
  check([n[o]['imm'] for o in (0x10,0x42)]==[-27,-27] and [n[o]['imm'] for o in (0x26,0x5c)]==[-328,-328] and all(n[o]['imm']==16 for o in (0x14,0x16,0x2a,0x2c,0x46,0x48,0x60,0x62)),'recomputecallers low16guard notsigned')
  check([(o,d['rs1'],d['imm'],d['width']) for o,d in n.items() if d['op']=='load']==[(0,10,276,4),(8,15,4,1),(0xa,15,3,1),(0x1c,15,6,1),(0x1e,15,5,1),(0x36,15,8,1),(0x38,15,7,1),(0x50,15,9,1),(0x54,15,10,1)],'recomputecallers capturedQ/freshbyteorder')
  check([n[o]['rs2'] for o in (0xe,0x24,0x3e,0x58)]==[14,14,17,17] and [n[o]['imm'] for o in (0xc,0x22,0x3c,0x56)]==[8]*4,'recomputecallers LE16pack order')
  check(not {d['rd'] for d in n.values() if 'rd'in d}&{1,2,8,9,18,19,20,21,22,23,24,25,26,27},'recomputecallers frameless noRA/SP/Sdefs')
  tail=pc+0x7a;hits,ent=last_before(tail,10);check(not hits and ent and n[0x7e]['imm']==1,'recomputecallers tailretainsP/reject1')
  for o in (0x6a,0x6e,0x72,0x76):check(countpaths(pc,tail,blocked=[pc+o])==0,'recomputecallers allfourstores dominate tail')
  check(countpaths(pc,pc+0x80,blocked=[pc+0x7e])==0 and not any(path(pc+o,pc+0x80) for o in (0x6a,0x6e,0x72,0x76)),'recomputecallers rejects no localstore')
  facts=dict(frame_bytes=0,object_direct_extent=480,captured_Q_from_P276=True,Q_direct_minimum_extent=11,Q_load_offsets=[4,3,6,5,8,7,9,10],four_LE16_spans=[[3,4],[5,6],[7,8],[9,10]],admitted_intervals=[[27,251],[328,17040],[27,251],[328,17040]],ordered_output_halfwords=[472,474,476,478],reject_reply=1,tail_chain_normal_values_if_matching=[0,2],incoming_RA_and_A0_unchanged_at_tail=True,no_direct_pointer_publication=True)
 else:
  alloc=0x8 if role=='gate80' else 0x1a;dealloc=0x46 if role=='gate80' else 0x12
  check(n[alloc]['imm']==-16 and n[dealloc]['imm']==16 and [o for o,d in n.items() if d.get('rd')==2]==sorted([alloc,dealloc]),'recomputecallers onlybalancedSPdefs')
  for o,d in n.items():
   if d['op'] in ('load','store') and d['rs1']==2:check(countpaths(pc,pc+o,blocked=[pc+alloc])==0,'recomputecallers allocation dominates frameaccess')
  for o in b['returns']:check(countpaths(pc+alloc,pc+o,blocked=[pc+dealloc])==0,'recomputecallers framepaths deallocatebefore RET')
  frame=dict(bytes=16,allocation=alloc,deallocation=dealloc,RA_SP12_S0_SP8_saves_and_restores=True,allocation_dominates_frameaccess=True,all_allocated_RET_paths_deallocate=True)
  check(n[0]['imm']==22 and n[2]['imm']==9,'recomputecallers typebyte9 gate')
  if role=='gate80':
   check(n[0xe]['imm']==16 and n[0x10]['imm']==80 and n[0x20]['op']=='bnez' and n[0x20]['rs1']==10,'recomputecallers gate80 exactstate80/fullRnonnull')
   check(n[0x26]['imm']==43 and n[0x26]['rs2']==0 and n[0x22]['imm']==160 and n[0x2a]['imm']==256 and n[0x2e]['imm']==160,'recomputecallers R0 effects43/160')
   check(n[0x4a]['imm']==n[0x52]['imm']==42 and n[0x4e]['imm']==1 and n[0x56]['target']==pc+0x32,'recomputecallers Rnonzero bit0 thencommon')
   check(n[0x32]['imm']==n[0x38]['imm']==17 and n[0x34]['imm']==-128 and n[0x3a]['imm']==1 and n[0x3c]['imm']==16 and n[0x3e]['imm']==0,'recomputecallers commonP17bit7/P16one/return0')
   facts=dict(type22_required=9,state16_required=80,tests_full_reply_nonzero=True,matched_reply2_uses_same_branch_as1=True,reply0_writes=['P43=0','P160=freshP160|256'],reply_nonzero_writes=['P42=freshP42|1'],both_called_arms_write=['P17=freshP17|128','P16=1'],called_arms_normal_reply=0,skipped_gate_normal_reply=1,no_direct_P124_write=True)
  else:
   check(n[0x16]['imm']==264 and n[0x20]['imm']==32 and n[0x26]['op']=='beqz' and n[0x2c]['imm']==1 and n[0x2e]['op']=='beq' and n[0x2e]['rs1']==10 and n[0x2e]['rs2']==15,'recomputecallers gateflag bit5 andexactR1')
   check(n[0x32]['imm']==16 and n[0x34]['op']=='bne' and n[0x38]['imm']==81 and n[0x3c]['imm']==16 and n[0x3e]['imm']==0,'recomputecallers Rnot1/state1->81')
   check(n[0x42]['imm']==n[0x4a]['imm']==168 and n[0x46]['imm']==128 and n[0x4e]['target']==pc+0x3e,'recomputecallers stateother P168bit7 andforced0')
   facts=dict(type22_required=9,word264_bit5_required=True,tests_full_reply_equal1=True,matched_reply2_uses_same_branch_as0=True,reply1_stops_before_own_object_stores=True,reply_not1_then_fresh_state16_1_writes='P16=81',reply_not1_then_otherstate_writes='P168=freshP168|128',handled_arms_normal_reply=0,skipped_or_reply1_normal_reply=1,no_direct_P124_write=True)
 check(countpaths(pc)=={'ingress':5,'gate80':4,'gateflag':5}[role],'recomputecallers exactDAGpathcensus')
 selected=[c['offset'] for c in b['calls']+b['tails']]+[d['pc']-pc for d in b['instructions'] if d['op']=='store' and d['rs1']!=2]
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),all_local_DAG_path_count=countpaths(pc),normal_return_certificates=returns,child_A0_arguments=args,exit_syntactic_path_counts={hex(a-pc):countpaths(pc,a) for a in ends},selected_entry_exit_walks={hex(o):[v-pc for v in path(pc,pc+o)+finish(pc+o)[1:]] for o in selected},frame_certificate=frame,facts=facts,syntactic_paths_not_feasibleinputs_or_targetexecution=True)


def domains():
 for v in range(65536):
  check((((v-27)&65535)<=224)==(27<=v<=251),'recomputecallers narrowinterval allU16')
  check((((v-328)&65535)<=16712)==(328<=v<=17040),'recomputecallers wideinterval allU16')
  lo=v&255;hi=v>>8;check((hi<<8|lo)==v,'recomputecallers allbytepairs LE16')
  check(min(v,251)<=251 and min(v,17040)<=17040,'recomputecallers minupperbounds allotherU16')
 for b in range(17041):check(max(b,2704)<=17040 and min(b,2120)<=17040,'recomputecallers Bclamps retain17040upperbound')
 for z in range(252):
  for t in (0,1,251,252,65535):check(min(z,t)<=251 and min(z,t)&255==min(z,t),'recomputecallers boundedZ removesfinalbytewrap')
 for v in range(256):
  check((v|0xffffff80)&255==v|128 and (v|1)&254==v&254,'recomputecallers byteOR masks')
 for r in (0,1,2,40,0xffffffff):
  check((r!=0)==(r in (1,2,40,0xffffffff)) and (r==1)==(r not in (0,2,40,0xffffffff)),'recomputecallers fullwordreply truth table')
 check((2!=0) and (2!=1) and min(0,27)==0 and min(0,251)==0,'recomputecallers reply2classification/countpositivity notinferred')
 return dict(full_U16_guard_cases=65536,LE16_bytepairs=65536,accepted_field_intervals={'P472':[27,251],'P474':[328,17040],'P476':[27,251],'P478':[328,17040]},conditional_recompute_bounds={'P480':[0,251],'P482':[0,17040],'P484':[0,251],'P486_nonmode2':[0,17040],'P486_mode2':[2704,65535]},conditional_leaf_P78_interval=[0,251],all_require_sameP_source_field_mode_preservation=True,reply2_gate80_nonzero_branch=True,reply2_gateflag_not1_branch=True,no_runtime_model_or_reachable_payload_proof=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for role in ROLES:
  pc=STARTS[index][role];raw=init.binding.take(data,pc,SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'recomputecallers complete strictHEX '+role);bs[role]=body(raw,role,index)
 cert={r:certificates(b,r) for r,b in bs.items()}
 reused={};reused_bodies={}
 for role in previous.ROLES:
  pc=previous.STARTS[index][role];raw=init.binding.take(data,pc,previous.SIZES[role]);check(sparse.captured(mem,pc,len(raw))==raw,'recomputecallers reusedfullHEX '+role);b=previous.body(raw,role,index);c=previous.certificates(b,role);reused_bodies[role]=b;reused[role]=dict(start=pc,bytes=b['bytes'],sha256=b['sha256'],normal_reply=c['facts'].get('normal_reply'),statuses=c['facts'].get('normal_statuses'))
 check(bs['ingress']['tails'][0]['target']==reused['recompute']['start'] and all(bs[r]['calls'][0]['target']==bs['ingress']['start'] for r in ('gate80','gateflag')),'recomputecallers gate->ingress->recompute joins')
 check(reused['recompute']['statuses']==[0,2] and reused['byte78']['normal_reply']=='entryP unchanged','recomputecallers exactmappedchild reply closure')
 rb=reused_bodies['recompute'];rn={d['pc']-rb['start']:d for d in rb['instructions']};lb=reused_bodies['byte78'];ln={d['pc']-lb['start']:d for d in lb['instructions']}
 check([rn[o]['imm'] for o in (4,0x2c,0x16,0x42)]==[476,472,478,474] and all(rn[o]['rs1']==10 and rn[o]['width']==2 for o in (4,0x2c,0x16,0x42)),'recomputecallers acceptedstores feedA/C/B/D sourcefields')
 check(ln[0x32]['rs1']==10 and ln[0x32]['imm']==484 and ln[0x32]['width']==2,'recomputecallers stable boundedZ joinsleaf')
 check(all(d.get('rd')!=8 for r in ('ingress',) for d in bs[r]['instructions']) and all(d.get('rd')!=8 for b in reused_bodies.values() for d in b['instructions']),'recomputecallers fullmatchedchain noS0definitions')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates=cert,reused_full_original_bodies=reused,
  contracts=['capturedQ=U32P276;loadsLE16 Q3..4,Q5..6,Q7..8,Q9..10 withfreshbyteorder4/3/6/5/8/7/9/10. Guardlow16(v-27)<=224 forfirst/third,low16(v-328)<=16712 forsecond/fourth. Reject1 beforelocalstores,no null/length guard;Qextent11 direct',
   'allfourheldvalues passguards beforeorderedSH P472/P474/P476/P478;frameless unlinkedJAL x0 to recompute withoriginalP/RA,doesnotlocallyreadsourceagain orretainQ. Matchingnormalchain status0/2 reachesoriginalcaller;invalid1 no tail',
   'conditionalC=min(P468,acceptedP472)<=251 andA=min(P464,acceptedP476)<=251,so low8output P484/P480 losesnobits;B=min(P466,acceptedP478)<=17040,clamp2704floor/2120cap retainsupper17040. Nonmode2D<=17040;mode2signedmin/low16/floor mayexceed17040',
   'matchingrecompute->leaf andfreshZ=P484 stability givesP78<=251 nofinalbytewrap,notpositive becauseCcan0. Mode/fieldstability,validframe/object/Q extents,aliasing andinstalledbinding remainpremises',
   'gate80 requiresfreshP22=9 andcapturedP16=80,thenoriginalP->ingress. FullR=0 clearsP43 andwritesfreshP160|256;fullRnonzero writesfreshP42|1. Bothcalledarms setfreshP17bit7,P16=1,andforce0. skippedgateforce1. R2 followsthesamebranchasR1,notproofvalidationfailure',
   'gateflag requiresfreshP22=9 andfreshP264bit5;originalP->ingress;onlyfullR==1 forces1 before ownobjectstores. R!=1 freshP16==1 writes81 elsefreshP168|128,thenforce0. MatchingR2 acceptedhere alongsideR0. No subsequentcallee/P124write in eithergate',
   'callers preservefullchildreturndistinctions inbranchesbutforceown0/1 statuses. Fullsource data/ingress calleridentity,actualprovider/taskcallbackrouting,otherwriters,asyncstatevisibility,nodeownership/consumption/freeorder unproved'],
  actual_binding_sourcevalidity_fieldstability_nodeownership_full_lifetime_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-bounded-config-ingress-and-caller-gates-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_phase_body_bytes=608,complete_phase_body_instructions=216,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['P276sourcewriter/extent andactualgate dispatch/ingresspath','5d006/5d14e andothernestedservices;clock/arena/recordactualbindings','asynchronousfield/modepreservation,group post-clear node lifetime,fullconsumption/releaseorder'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  for role in ROLES:
   pc=STARTS[i][role];raw=init.binding.take(data,pc,SIZES[role]);b=body(raw,role,i)
   for d in b['instructions']:
    o=d['pc']-pc;z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('recomputecallers instructionmutation escaped')
    mutated+=1
   for o,_ in TYPED[role]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,role,i)
    except RuntimeError:pass
    else:raise RuntimeError('recomputecallers typedmutation escaped')
    typed+=1
 check((mutated,typed)==(216,14),'recomputecallers mutationcensus')
 print('PASS:216 instruction/14 typed-load mutations rejected;bounded ingress and exact caller branches')


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
 else:check(OUT.read_bytes()==encoded,'recomputecallers exactledger replay')
 print('PASS:608B/216i complete ingress/callers;strictHEX;tail-return/conditional251bound joins;exactledger')
 print('PASS:NO target execution/emulation;actualbindings/asyncfieldstability/full lifetimes UNPROVED')


if __name__=='__main__':main()
