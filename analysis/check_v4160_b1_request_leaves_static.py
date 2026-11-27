"""Offline request shutdown/helper contracts from original operands and immutable CFGs.
No target execution/emulation, mutable target-state model or hardware access.
"""
import argparse,json
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_callback_consume_static as previous
import check_v4160_loaded_hook_sources_static as hooks
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common,FIELDS,BRANCHES=previous.common,previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-request-leaves-static.json')
PARTS=('inner','cleanup','resetwrap')
STARTS=((0x656c6,0x6575a,0x6440a),(0x657b0,0x65844,0x644f4))
SIZES=(148,126,24)
HASHES=(('fcf299be78214671dae256951370b465fb5e4221d584f1acb6cda817aa4993cd', '0a97b7b5296aa4aca6324c43e8419aea77df11822013ddaed92a7f5e4b587523', 'f2322ddc8cba6f293bf2bdea9cf58206566b0dcbba4006deb9eb63b4a2c1a45e'), ('7ef880f5bbe36ac00c6853771abb66c3aa58b4c1815b69fc456efcfe8e02d581', '4c3575874d2ead58cf989cf658c79f84213765c138a2bcdb1a594ec5bb051069', '0008fc118bf37f1b78c1705c65677b8fc96de7d31446ce16a6762e1208920bfa'))
COUNTS=((50, 46, 9), (50, 46, 9))
QK=({'inner': ((60, '1837', 'qk.c.lbu'), (72, '9427', 'qk.c.lbu'), (84, 'f833', 'qk.c.lbu'), (92, 'f833', 'qk.c.lbu'), (100, 'f833', 'qk.c.lbu'), (102, '98a7', 'qk.c.sb'), (106, '98b7', 'qk.c.sb'), (112, '0828', 'qk.c.lbu')), 'cleanup': ((34, '1cb0', 'qk.c.sb'), (108, 'dc24', 'qk.c.lbu')), 'resetwrap': ()}, {'inner': ((60, '1837', 'qk.c.lbu'), (72, '9427', 'qk.c.lbu'), (84, 'f833', 'qk.c.lbu'), (92, 'f833', 'qk.c.lbu'), (100, 'f833', 'qk.c.lbu'), (102, '98a7', 'qk.c.sb'), (106, '98b7', 'qk.c.sb'), (112, '0828', 'qk.c.lbu')), 'cleanup': ((34, '1cb0', 'qk.c.sb'), (108, 'dc24', 'qk.c.lbu')), 'resetwrap': ()})
TYPED=({'inner': ((12, 2),), 'cleanup': ((22, 4), (36, 4), (40, 2), (56, 4), (66, 4)), 'resetwrap': ()}, {'inner': ((12, 2),), 'cleanup': ((22, 4), (36, 4), (40, 2), (56, 4), (66, 4)), 'resetwrap': ()})
LITERALS=(
{
'inner':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 15 1073889280
008 store 2 1 12 4
00a store 2 8 8 4
00c load 9 15 524 4
010 store 15 0 524 4
014 fence.i 
018 lui 8 536883200
01c addi 15 8 1376
020 load 10 15 4 4
022 store 15 0 14 1
026 addi 8 8 1376
02a beqz 10 52
02c auipc 1 536457216
030 jalr 1 1 -1506
034 lui 15 536883200
038 addi 14 15 1300
03c load 14 14 9 1
03e store 8 0 4 4
042 addi 15 15 1300
046 beqz 14 84
048 load 13 15 8 1
04a li 14 8
04c bne 13 14 84
050 store 15 0 9 1
054 load 14 15 7 1
056 li 13 6
058 beq 13 14 100
05c load 14 15 7 1
05e li 13 7
060 bne 13 14 108
064 load 14 15 7 1
066 store 15 14 8 1
068 li 14 1
06a store 15 14 9 1
06c jal 1 409176
070 load 10 8 16 1
072 lui 15 536883200
076 li 11 16
078 store 15 0 -260 1
07c jal 1 276904
080 load 1 2 12 4
082 load 8 2 8 4
084 lui 15 1073889280
088 store 15 9 524 4
08c li 10 0
08e load 9 2 4 4
090 addi 2 2 16
092 jr 1
''',
'cleanup':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 store 2 1 12 4
00a store 2 8 8 4
00c store 2 18 0 4
00e jal 1 415430
012 addi 18 9 1376
016 load 15 18 15 1
01a lui 8 536883200
01e addi 8 8 1344
022 store 8 15 1 1
024 load 10 18 16 1
028 load 15 18 20 4
02c li 11 8
02e addi 9 9 1376
032 store 8 15 8 4
034 jal 1 276904
038 load 10 18 16 1
03c li 11 4
03e jal 1 276904
042 load 15 18 12 1
046 andi 15 15 2
048 beqz 15 108
04a load 15 8 16 4
04c li 12 0
04e li 11 0
050 addi 10 0 34
054 call_indirect 1 15
056 load 8 2 8 4
058 store 9 0 12 1
05c load 1 2 12 4
05e load 9 2 4 4
060 load 18 2 0 4
062 li 11 2
064 li 10 0
066 addi 2 2 16
068 jal 0 277288
06c load 15 9 12 1
06e andi 15 15 4
070 beqz 15 86
072 load 15 8 16 4
074 li 12 0
076 li 11 0
078 addi 10 0 36
07c jump 84
''',
'resetwrap':'''
000 addi 2 2 -16
002 lui 15 536883200
006 store 2 1 12 4
008 store 15 0 1390 1
00c jal 1 409176
010 load 1 2 12 4
012 li 10 0
014 addi 2 2 16
016 jr 1
''',
},
{
'inner':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 15 1073889280
008 store 2 1 12 4
00a store 2 8 8 4
00c load 9 15 524 4
010 store 15 0 524 4
014 fence.i 
018 lui 8 536883200
01c addi 15 8 1456
020 load 10 15 4 4
022 store 15 0 14 1
026 addi 8 8 1456
02a beqz 10 52
02c auipc 1 536457216
030 jalr 1 1 -1740
034 lui 15 536883200
038 addi 14 15 1380
03c load 14 14 9 1
03e store 8 0 4 4
042 addi 15 15 1380
046 beqz 14 84
048 load 13 15 8 1
04a li 14 8
04c bne 13 14 84
050 store 15 0 9 1
054 load 14 15 7 1
056 li 13 6
058 beq 13 14 100
05c load 14 15 7 1
05e li 13 7
060 bne 13 14 108
064 load 14 15 7 1
066 store 15 14 8 1
068 li 14 1
06a store 15 14 9 1
06c jal 1 409410
070 load 10 8 16 1
072 lui 15 536883200
076 li 11 16
078 store 15 0 -180 1
07c jal 1 277044
080 load 1 2 12 4
082 load 8 2 8 4
084 lui 15 1073889280
088 store 15 9 524 4
08c li 10 0
08e load 9 2 4 4
090 addi 2 2 16
092 jr 1
''',
'cleanup':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 store 2 1 12 4
00a store 2 8 8 4
00c store 2 18 0 4
00e jal 1 415664
012 addi 18 9 1456
016 load 15 18 15 1
01a lui 8 536883200
01e addi 8 8 1424
022 store 8 15 1 1
024 load 10 18 16 1
028 load 15 18 20 4
02c li 11 8
02e addi 9 9 1456
032 store 8 15 8 4
034 jal 1 277044
038 load 10 18 16 1
03c li 11 4
03e jal 1 277044
042 load 15 18 12 1
046 andi 15 15 2
048 beqz 15 108
04a load 15 8 16 4
04c li 12 0
04e li 11 0
050 addi 10 0 34
054 call_indirect 1 15
056 load 8 2 8 4
058 store 9 0 12 1
05c load 1 2 12 4
05e load 9 2 4 4
060 load 18 2 0 4
062 li 11 2
064 li 10 0
066 addi 2 2 16
068 jal 0 277428
06c load 15 9 12 1
06e andi 15 15 4
070 beqz 15 86
072 load 15 8 16 4
074 li 12 0
076 li 11 0
078 addi 10 0 36
07c jump 84
''',
'resetwrap':'''
000 addi 2 2 -16
002 lui 15 536883200
006 store 2 1 12 4
008 store 15 0 1470 1
00c jal 1 409410
010 load 1 2 12 4
012 li 10 0
014 addi 2 2 16
016 jr 1
''',
},
)


def specs(part,index):
 pc=STARTS[index][PARTS.index(part)];out={}
 for row in LITERALS[index][part].splitlines():
  if not row:continue
  off,op,*values=row.split();args=list(map(int,values));check(len(args)==len(FIELDS[op]),'requestleaves literal fields')
  d=dict(zip(FIELDS[op],args));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+int(off,16)]=d
 return out


def body(raw,part,index):
 k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
 check(n.keys()==s.keys(),'requestleaves complete boundaries')
 for a,f in s.items():init.g(n,a,'requestleaves '+part+' '+hex(a-pc),**f)
 for o,f3 in TYPED[index][part]:check(int.from_bytes(raw[o:o+4],'little')&0x707f==((f3<<12)|3),'requestleaves typed load')
 for o,h,m in QK[index][part]:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'requestleaves Xwchc raw/offset')
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[index][k],HASHES[index][k]),'requestleaves full identity')
 e={};calls=[];tails=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op=='jr':check(d['rs1']==1,'requestleaves RET');q=[];rets.append(a)
  elif op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jal':
   check(d['rd'] in (0,1),'requestleaves link')
   if d['rd']==0:tails.append(dict(offset=a-pc,target=d['target'],new_link=False));q=[]
   else:calls.append(dict(offset=a-pc,target=d['target']))
  elif op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','requestleaves pair')
   calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  elif op=='call_indirect':
   check(d['rd']==1 and d['rs1']==15,'requestleaves callback link/register');calls.append(dict(offset=a-pc,target='fresh F+16 callback;no nullguard'))
  check(all(z in n for z in q),'requestleaves closed CFG');e[a]=q
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and common.acyclic(e),'requestleaves all nodes reachable DAG')
 expect={'inner':[(0x30,0x20000110),(0x6c,0x63e58+234*index),(0x7c,0x439a8+140*index)],
  'cleanup':[(0xe,0x656c6+234*index),(0x34,0x439a8+140*index),(0x3e,0x439a8+140*index),(0x54,'fresh F+16 callback;no nullguard')],
  'resetwrap':[(0xc,0x63e58+234*index)]}[part]
 check(calls==[dict(offset=o,target=t) for o,t in expect],'requestleaves complete call census')
 check(tails==([dict(offset=0x68,target=0x43b28+140*index,new_link=False)] if part=='cleanup' else []) and rets==([] if part=='cleanup' else [pc+SIZES[k]-2]),'requestleaves all tails/returns')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store']
 frames={'inner':[(2,2,9,4,4),(8,2,1,12,4),(10,2,8,8,4)],'cleanup':[(2,2,9,4,4),(8,2,1,12,4),(10,2,8,8,4),(12,2,18,0,4)],'resetwrap':[(6,2,1,12,4)]}
 nonframe={'inner':[(0x10,15,0,524,4),(0x22,15,0,14,1),(0x3e,8,0,4,4),(0x50,15,0,9,1),(0x66,15,14,8,1),(0x6a,15,14,9,1),(0x78,15,0,-260+80*index,1),(0x88,15,9,524,4)],
  'cleanup':[(0x22,8,15,1,1),(0x32,8,15,8,4),(0x58,9,0,12,1)],'resetwrap':[(8,15,0,1390+80*index,1)]}
 check([d for d in stores if d[1]==2]==frames[part] and [d for d in stores if d[1]!=2]==nonframe[part],'requestleaves all stores/frame')
 return dict(start=pc,bytes=len(raw),sha256=sha256(raw).hexdigest(),instructions=list(n.values()),CFG=e,calls=calls,tails=tails,returns=rets,stores=stores,complete_local_body=True,target_execution_or_emulation=False)


def paths(b,part):
 if part=='inner':
  choices={f'pointer{p}_oldlatch{l}_state{state}':{0x2a:0x2c if p else 0x34,0x46:0x48 if l else 0x54,0x4c:0x50,
   0x58:0x64 if state==6 else 0x5c,0x60:0x64 if state==7 else 0x6c} for p in (0,1) for l in (0,1) for state in (6,7,0)}
  choices['oldlatch_nonzero_status8not8']={0x2a:0x34,0x46:0x48,0x4c:0x54,0x58:0x5c,0x60:0x6c}
 elif part=='cleanup':choices={'callback34':{0x48:0x4a},'callback36':{0x48:0x6c,0x70:0x72},'no_callback':{0x48:0x6c,0x70:0x56}}
 else:choices={'normal':{}}
 out={name:common.walk(b,c) for name,c in choices.items()}
 if part=='cleanup':
  for name,seq in out.items():
   check((0x54 in seq)==(name!='no_callback') and seq[-1]==0x68,'requestleaves atmostone callback then tail')
   check(seq.index(0xe)<seq.index(0x22)<seq.index(0x32)<seq.index(0x34)<seq.index(0x3e)<seq.index(0x42)<seq.index(0x58)<seq.index(0x66)<seq.index(0x68),'requestleaves publish/stop/callback/clear/tail order')
   if name!='no_callback':check(seq.index(0x54)<seq.index(0x58),'requestleaves flags clear after callback normal return')
 if part=='inner':
  for name,seq in out.items():check(seq.index(0x22)<seq.index(0x2a) and seq.index(0x3e)<seq.index(0x6c)<seq.index(0x70)<seq.index(0x78)<seq.index(0x7c)<seq.index(0x88)<seq.index(0x8c),'requestleaves clear/release/reset/stop/control order')
 return out


def domains():
 partition=[0,0,0];latches=0
 for first in range(256):
  for second in range(256):
   code=34 if first&2 else 36 if second&4 else 0;partition[{34:0,36:1,0:2}[code]]+=1
   check((code==34)==bool(first&2) and (code==36)==(not(first&2) and bool(second&4)),'requestleaves two independent flags')
   matched=first==6 or second==7;latches+=matched
   check(matched==(first==6 or (first!=6 and second==7)),'requestleaves first6 second7 predicates')
 check(partition==[32768,16384,16384] and latches==511,'requestleaves freshbyte partitions')
 for later in range(256):check((later&255)==later,'requestleaves thirdfresh byte maydiffer from6/7')
 for code,reply in ((34,17),(36,19)):
  check(code>2 and (code-17)&255==reply and reply>1,'requestleaves APP status no retry/deref forcallback34/36')
 for i in range(2):
  base=0x200031c8+80*i;check(base+4*2==0x200031d0+80*i and base+4*4+4<=0x100000000,'requestleaves registrar accepted address range')
 return dict(fresh_flags_pairs=65536,callback_partition=partition,fresh_state_pairs=65536,latch_gate_pairs=511,
  independently_reloaded_latch_byte_cases=256,APP34_reply=17,APP36_reply=19,APP34_36_retry_or_A2_dereference=False,
  target_execution_or_emulation=False)


def profile(image,data,hexraw,index,parent,app):
 _,mem=sparse.inspect(hexraw,sparse.parser());bs={}
 for k,part in enumerate(PARTS):
  raw=init.binding.take(data,STARTS[index][k],SIZES[k]);check(sparse.captured(mem,STARTS[index][k],SIZES[k])==raw,'requestleaves strict original HEX');bs[part]=body(raw,part,index)
 C=0x20003560+80*index;S=0x20003514+80*index;F=C-32
 n={part:{d['pc']-b['start']:d for d in b['instructions']} for part,b in bs.items()};a,c,w=(n[p] for p in PARTS)
 check(a[0x18]['imm']+a[0x1c]['imm']==a[0x18]['imm']+a[0x26]['imm']==C and a[0x34]['imm']+a[0x38]['imm']==a[0x34]['imm']+a[0x42]['imm']==S,'requestleaves inner C/S sources')
 check(c[4]['imm']+c[0x12]['imm']==c[4]['imm']+c[0x2e]['imm']==C and c[0x1a]['imm']+c[0x1e]['imm']==F and w[2]['imm']+w[8]['imm']==C+14,'requestleaves config/clear sources')
 check(c[0x50]['imm']==34 and c[0x78]['imm']==36 and c[0x4c]['imm']==c[0x4e]['imm']==c[0x74]['imm']==c[0x76]['imm']==0,'requestleaves callback tuples')
 check(c[0x2c]['imm']==8 and c[0x3c]['imm']==4 and a[0x76]['imm']==16 and c[0x62]['imm']==2 and c[0x64]['imm']==0,'requestleaves stop masks and registrar tuple')
 # Existing parent already checks original-byte RF caller and timer contracts; verify exact new joins.
 check(next(t['target'] for t in parent['bodies']['request']['tails'] if t['offset']==0xb2)==bs['cleanup']['start'],'requestleaves eight-exit tail joins cleanup')
 check(next(c['target'] for c in parent['bodies']['task']['calls'] if c['offset']==0xba)==bs['cleanup']['start'],'requestleaves event8 joins cleanup')
 check([q['target'] for q in parent['bodies']['request']['calls'] if q['offset'] in (0xec,0xfe)]==[bs['resetwrap']['start']]*2,'requestleaves request resetwrapper joins')
 inner=previous.previous.previous;reset=inner.old_body(data,mem,'reset',index)
 check(bs['inner']['calls'][1]['target']==bs['resetwrap']['calls'][0]['target']==reset['start'],'requestleaves reset joins')
 hd=hooks.DETAILS[index];pc=hd[6];raw=init.binding.take(data,pc,22)
 check(sparse.captured(mem,pc,22)==raw,'requestleaves registrar strictHEX')
 registrar=hooks.body(raw,'registrar',pc,hd[7],hd[-1][3]);check(bs['cleanup']['tails'][0]['target']==pc and registrar['complete_function'],'requestleaves full registrar join')
 callbackpaths={str(code):common.walk(app,{2:6,6:0xa,0x12:0x4a}) for code in (34,36)}
 sn={d['pc']-app['start']:d for d in app['instructions']}
 for seq in callbackpaths.values():check(seq[-1]==0x4a and not any(sn[o]['op']=='load' and sn[o]['rs1']==12 for o in seq),'requestleaves APP noA2read normalRET')
 return dict(label=init.binding.PROFILES[index][0],bodies=bs,CFG_certificates={p:common.certificates(b) for p,b in bs.items()},paths={p:paths(b,p) for p,b in bs.items()},
  reused_reset=reset,reused_registrar=registrar,reused_APP_status=app,APP34_36_paths=callbackpaths,
  context=C,status=S,config=F,registrar_clear_word=0x200031d0+80*index,
  inner_contract=['saveU32control4002420c inS1;SW0control,FENCE.I;capturefreshC4;clearC14 BEFORE capturedpointer test;nonnull requests20000110(capturedC4)',
   'afterrelease normalreturn,readfreshS9 thenclearC4 regardlessrelease reply;freshS9nonzero andfreshS8==8 clearsS9;firstfreshS7==6 oranotherfreshS7==7 ->thirdfreshS7 toS8,S9=1;thirdbyte notassumed6/7',
   'alwaysreset63e58/63f42,thenfreshC16 andclear20002efc/20002f4c beforestop(freshC16,16);restorecapturedcontrol,forceA0=0;no release/cancel/hardwareacknowledgement'],
  cleanup_contract=['innernormalreturn thenfreshC15 ->F1;freshC20 ->F8;stop(freshC16,8);stop(independentlyfreshC16,4);childrepliesignored',
   'firstfreshC12bit1 ->freshF16(34,0,0);else secondfreshC12bit2 ->freshF16(36,0,0);else nocallback. No pointer nullguard;atmostone localcallbacksitevisit',
   'callbacknormalreturn thenSB0C12,restoreS/RA/SP,unlinkedtailregistrar(0,2);registrar fullentryA1<=4 ->SWentryA0(table+4*A1),elseRET;hereclears200031d0/20003220;replyA0=0underpreservation',
   'matchingAPP174ee:34 ->A0=(34-17)&255=17 thennormalRET;36 ->19 thennormalRET;neither retries orreadsnullA2. Return17isnot reentryasstatus17'],
  resetwrap_contract=['clearbyteC14,callreset withthenlivearguments;ignore reply;forceA0=0,restoreSP/RA,RET;no physical reset guarantee'],
  premises='candidateISA/API/mapping/actualprovider-callbackbinding;validcode/frame/config/objectextents;ordinarycalleeS/SP/RA/savedframepreservation;no adversealias/wrap/IRQ/DMA/reentry;freshread equalities separate',
  full_pointer_lifetime_release_success_timer_cancellation_hardware_restore_or_actual_binding_proved=False)


def derive(image,carriers,header,coverage,hexes):
 parent=previous.derive(image,carriers,header,coverage,hexes);app=previous.app_body(image,'status')
 return dict(schema='TSL9-B1-request-shutdown-helpers-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(image,d,h,i,parent['profiles'][i],app) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=596,complete_phase_body_instructions=210,reused_registrar_bytes=44,reused_reset_bytes=260,reused_APP_unique_bytes=76,
  C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['64794/6487e,63c54/63d3e andRAM200026ba/20002706 effects','actualflags/state/callbackwriters andinstalledproviderbinding','private release semantics underactualbinding,allalias/reentrant pointerlifetimes andtimerdelivery'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  for k,part in enumerate(PARTS):
   raw=init.binding.take(data,STARTS[i][k],SIZES[k]);body(raw,part,i)
   for a,d in decode(raw,STARTS[i][k]).items():
    o=a-STARTS[i][k];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('requestleaves mutation escaped')
    mutations+=1
   for o,f3 in TYPED[i][part]:
    bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
    try:body(bad,part,i)
    except RuntimeError:pass
    else:raise RuntimeError('requestleaves typed mutation escaped')
    typed+=1
 check((mutations,typed)==(210,12),'requestleaves mutation census');domains()
 print('PASS:210 instruction/12 typed-load mutations rejected;65536 freshflags/65536 state pairs;callback34/36 andframe/order certificates')


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
 else:check(OUT.read_bytes()==encoded,'requestleaves exactledger replay')
 print('PASS:596B/210i complete request cleanup/inner/resetwrapper;strict HEX;APP callback34/36 andregistrar joins;exactledger')
 print('PASS:NO target execution/emulation;actualbinding/release/cancel/hardware/fullpointerlifetime UNPROVED')


if __name__=='__main__':main()
