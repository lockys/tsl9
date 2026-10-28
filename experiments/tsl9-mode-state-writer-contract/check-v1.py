"""Audit scoped original mode writers and direct caller arguments, without execution."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='mode_writer_static_analysis')
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def table_cfg(f,e,B,V):
 ops={o['addr']:o for o in f['operations']};g={p:[]for p in ops};tables={};data={};exits=[];calls=[]
 need([(d['start'],d['bytes'])for d in e['data_regions']]==[(0x1a13c,20),(0x1a150,120),(0x1a1c8,332),(0x1a314,40),(0x1a33c,244)],'Only five existing positive relative-offset tables')
 for t,index,limit in zip(e['data_regions'],['a2','a5','s0','s1','a5'],['a5','a4','a5','a5','a4']):
  raw=bytes.fromhex(t['raw_hex']);need(len(raw)==t['bytes']==t['entries']*4 and hashlib.sha256(raw).hexdigest()==t['original_sha256'],'Exact complete existing signed-offset table')
  targets=[(t['start']+int.from_bytes(raw[i:i+4],'little',signed=True))&0xffffffff for i in range(0,len(raw),4)];need(targets==t['target_PCs']and set(targets)<=set(ops),'Every actual table target belongs to whole function')
  pc=t['base_PC'];high=ops[pc];low=ops[pc+4];need(high['opcode']=='auipc a4, 0xc'and low['opcode'].startswith('addi a4, a4, '),'Original table base pair');need((pc+(0xc<<12)+int(low['opcode'].rsplit(', ',1)[1]))==t['start'],'Actual relative table address')
  need(ops[t['limit_PC']]['opcode']=='li '+limit+', '+str(t['entries']-1)and ops[t['guard_PC']]['opcode'].startswith('bltu '+limit+', '+index+', '),'Original unsigned table index guard')
  shift=ops[pc+8];add=ops[pc+8+shift['size']];need(shift['opcode']=='slli '+index+', '+index+', 0x2'and add['opcode']=='add '+index+', '+index+', a4'and add['addr']+add['size']==t['load_PC']and ops[t['load_PC']]['opcode']=='lw a5, 0('+index+')'and ops[t['jump_PC']]['opcode']=='jr a5','Actual guarded index/load/relative-dispatch chain')
  interval=[o for o in f['operations']if pc<=o['addr']<=t['jump_PC']];need(all(o['type']not in ['call','ucall','cjmp','jmp']for o in interval),'No opaque call or branch within table dispatch sequence');need(any(o['opcode']=='add a5, a5, a4'for o in interval),'Table value added to original base before dispatch')
  tables[t['jump_PC']]=sorted(set(targets));data.update({t['start']+i:b for i,b in enumerate(raw)})
 for pc,o in ops.items():
  following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
  if pc in tables:g[pc]=tables[pc];continue
  if o['type']in ['ret','rjmp']:exits.append(dict(PC=pc,type=o['type'],instruction=o['opcode']));continue
  if d:
   kind,target=d
   if o['type']=='call':need(following in ops,'Whole call continuation');calls.append(dict(PC=pc,target=target));g[pc]=[following]
   elif target in ops:g[pc]=[target]+([following]if o['type']=='cjmp'else[])
   else:need(o['type']=='jmp','Original external tail');exits.append(dict(PC=pc,type='direct-tail',target=target,instruction=o['opcode']))
  else:
   need(following in ops,'No fallthrough beyond selected function');g[pc]=[following]
   if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
 need(V['reachable'](g,f['start'])==set(ops)and exits,'Whole CFG includes all actual relative-table arms')
 depths={};pending=[(f['start'],0)]
 while pending:
  pc,depth=pending.pop()
  if pc in depths:need(depths[pc]==depth,'Whole table CFG SP joins agree');continue
  depths[pc]=depth;o=ops[pc];delta=int(o['opcode'].rsplit(', ',1)[1])if o['opcode'].startswith('addi sp, sp, ')else 0;need(delta in [-16,0,16],'Actual frame adjustments only');after=depth+delta;need(after in [-16,0],'Actual own frame states')
  if not g[pc]:need(after==0,'Frame released at every exit')
  pending.extend((n,after)for n in g[pc])
 return ops,g,dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=16,own_frame_balanced=True,all_CFG_instructions_reachable=True,typed_exits=exits,calls=calls,relative_jump_tables=5,existing_positive_table_DATA_bytes=len(data),table_mapping_validity_required=True),data
def audit():
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():
  need(not Path(p).is_absolute()and'..'not in Path(p).parts and'command_dispatch_windows'not in p,'Allowed pinned local input');need(sha(R/p)==h,'Input changed: '+p)
 B=lib(K['control_reader']);V=lib(K['CFG_reader']);E=lib(K['ELF_reader'])['ELF'];rows=[];ops={};graphs={};functions={};selected={};table_data={}
 for item in K['functions']:
  evidence=read(R/item['evidence']);f=next(f for f in evidence['selected_functions']if f['start']==item['start']);need(f['end']==item['end'],'Whole selected original function')
  addresses={o['addr']for o in f['operations']};external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))and d[1]not in addresses}
  if f['start']==0xe220:oo,g,cfg,table_data=table_cfg(f,evidence,B,V)
  else:oo,g,cfg=V['whole_cfg'](f,B,external,item['frame'])
  need(not set(oo)&set(ops),'Unique selected CODE instructions');ops.update(oo);graphs[f['start']]=g;functions[f['start']]=f;rows.append(cfg)
  pc=f['start'];raw=bytearray()
  for o in f['operations']:
   need(o['addr']==pc and o['size']==len(bytes.fromhex(o['bytes'])),'Contiguous whole CODE evidence');raw.extend(bytes.fromhex(o['bytes']));pc+=o['size']
  need(pc==f['end']and not(f['start']<0x14c8a and 0x14056<f['end']),'Only allowed CODE ranges');selected.update({f['start']+i:v for i,v in enumerate(raw)})
 native=[];allops=None
 for mode in ['c','cpp']:
  path=R/K['layout']/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';elf=E(path);bm={};instruction_map={};code_bytes=0
  for s in elf.sections:
   if s['type']!=1 or s['flags']!=6:continue
   need(not(s['address']<0x14c8a and 0x14056<s['address']+s['size']),'Excluded CODE absent from selected artifact');raw=elf.data(s);code_bytes+=len(raw);at=0
   while at<len(raw):
    size=4 if raw[at]&3==3 else 2;need(at+size<=len(raw),'Complete instruction boundary');pc=s['address']+at;instruction_map[pc]=(size,int.from_bytes(raw[at:at+size],'little'));at+=size
   for p in selected:
    if s['address']<=p<s['address']+s['size']:need(p not in bm,'Unique native CODE owner');bm[p]=raw[p-s['address']]
  table_witness={}
  for s in elf.sections:
   if s['type']==1 and s['flags']==2 and any(s['address']<=p<s['address']+s['size']for p in table_data):
    need(not(s['address']<0x1a6a0 and 0x1a69c<s['address']+s['size']),'No excluded default DATA section read');raw=elf.data(s)
    for p in table_data:
     if s['address']<=p<s['address']+s['size']:need(p not in table_witness,'Unique native table owner');table_witness[p]=raw[p-s['address']]
  need(table_witness==table_data and len(table_data)==756,'All five original tables equal existing native positive DATA')
  need(bm==selected and code_bytes==69412 and len(instruction_map)==23602,'Whole selected bodies equal actual native CODE;full selected CODE inventory unchanged')
  native.append(dict(mode=mode,ELF_sha256=sha(path),selected_CODE_bytes_equal=len(bm)))
  if allops is None:allops=instruction_map
  else:need(allops==instruction_map,'C/C++ selected native instruction maps identical')
 def operands(w):need(all(ops[p]['opcode']==v for p,v in w.items()),'Exact original writer/caller operands')
 operands({0xd05c:'auipc a5, 0x1ffff',0xd060:'addi a5, a5, -292',0xd064:'li a4, 1',0xd066:'neg a2, a2',0xd06a:'sb a4, 0(a5)',0xd06e:'sb a0, 1(a5)',0xd072:'sb a2, 2(a5)',0xd076:'sb a1, 3(a5)',0xd07a:'ret'})
 base=(0xd05c+(0x1ffff<<12)-292)&0xffffffff;need(base==0x2000bf38,'Exact nominal original state base')
 g=graphs[0xd05c];need(all(set(g[a])=={b}for a,b in zip(sorted(g),sorted(g)[1:])),'Straight-line four-byte setter,without a mode clamp')
 direct=[]
 for p,(size,h)in sorted(allops.items()):
  d=B['decode_control'](h.to_bytes(size,'little'),p)
  if d and d[1]==0xd05c:direct.append(p)
 need(direct==[0xa224,0xac6c,0xd528,0xe1ea,0xe6e8],'Exact direct encoded branches/calls to setter within selected CODE only')
 callers=[]
 for root,pc,definitions in [(0xa204,0xa224,{0xa220:3}),(0xac0a,0xac6c,{0xac12:1,0xac64:3}),(0xd50a,0xd528,{0xd524:5}),(0xe1a6,0xe1ea,{0xe1e8:3}),(0xe220,0xe6e8,{0xe6e6:3})]:
  f=functions[root];g=graphs[root];operands({p:'li a0, '+str(value)for p,value in definitions.items()});blocked={p:[]if p in definitions else list(v)for p,v in g.items()};need(pc in V['reachable'](g,root)and pc not in V['reachable'](blocked,root),'Actual constant-mode definitions collectively dominate direct setter transfer')
  # Restrict inspection to instructions on paths from the definition to the transfer.
  reverse={p:[]for p in g}
  for a,targets in g.items():
   for b in targets:reverse[b].append(a)
  forward=set().union(*(V['reachable'](g,p)for p in definitions));region=(forward&V['reachable'](reverse,pc))-set(definitions)-{pc}
  for p in region:
   o=ops[p];mn=o['opcode'].split()[0];need(o['type']not in ['call','ucall'],'No intervening ABI-clobbering call')
   need(mn in ['sb','sh','sw','beq','bne','beqz','bnez','bltu','bleu','j']or o['opcode'].partition(' ')[2].split(',')[0]!='a0','No intervening A0 overwrite')
  need(B['decode_control'](bytes.fromhex(ops[pc]['bytes']),pc)[1]==0xd05c,'Actual direct setter transfer')
  callers.append(dict(function=root,PC=pc,mode_definitions=[dict(PC=p,value=v)for p,v in definitions.items()],modes=sorted(set(definitions.values())),whole_CFG_constant_arguments_proved=True))
 operands({0xd0b2:'lui a5, 0x1000',0xd0b6:'addi a5, a5, 1281',0xd0ba:'j 0xd0c4',0xd0bc:'lui a5, 0x1000',0xd0c0:'addi a5, a5, 1025',0xd0c4:'auipc a4, 0x1ffff',0xd0c8:'sw a5, -396(a4)',0xd0d4:'lui a5, 0x1000',0xd0d8:'addi a5, a5, 513',0xd0dc:'j 0xd0c4'})
 g=graphs[0xd07c];need({p for p in g if 0xd0c4 in g[p]}=={0xd0ba,0xd0c0,0xd0dc}and set(g[0xd0c4])=={0xd0c8},'All local predecessors of the original word writer')
 need(((0xd0c4+(0x1ffff<<12)-396)&0xffffffff)==base,'Word writer overlaps exactly four logical state bytes');word_writes=[]
 for hi,lo,tail,imm in [(0xd0b2,0xd0b6,0xd0ba,1281),(0xd0bc,0xd0c0,0xd0c4,1025),(0xd0d4,0xd0d8,0xd0dc,513)]:
  need(set(g[hi])=={lo}and set(g[lo])=={tail}and{p for p in g if lo in g[p]}=={hi},'No bypass of each constant word constructor');word=(0x1000<<12)+imm;fields=list(word.to_bytes(4,'little'));need(fields[0]==1 and fields[2:]==[0,1],'Exact original little-endian four-byte state assignment');word_writes.append(dict(high_PC=hi,low_PC=lo,store_PC=0xd0c8,word=word,state_bytes=fields,mode=fields[1]))
 need(sorted(x['mode']for x in word_writes)==[2,4,5],'Conditional original word-writer modes2,4,5')
 operands({0xd0ee:'lui a5, 0x40',0xd0f2:'lw t1, 72(a5)',0xd0f6:'li a2, 16',0xd0f8:'li a1, 0',0xd0fa:'auipc a0, 0x1ffff',0xd0fe:'addi a0, a0, -450',0xd102:'jr t1'})
 need(((0xd0fa+(0x1ffff<<12)-450)&0xffffffff)==base,'Opaque initializer destination matches state base')
 L=lib(K['layout_builder']);plan=L['derive'](L['E'](R/K['component']));data={p for o in plan['owners']if o['info']==17 for p in range(o['original_PC'],o['original_PC']+o['bytes'])};gaps=[]
 for mode in [1,3]:
  lo=0x1a078+mode*16;hi=lo+16;need(not set(range(lo,hi))&data,'Conditional16-byte mode row is an actual positive-DATA coverage gap');gaps.append(dict(mode=mode,start=lo,end=hi,bytes=16,lookup_PC=0xcf5a,all_columns_bound_by_mask=True,all_columns_or_mode_reachability_observed=False,all_bytes_missing_from_formal_DATA=True,payload_read=False))
 prior=lib(K['prior_checker'])['audit']();need(prior==read(R/K['prior_receipt'])and not prior['global_mode_domain_or_all_writers_proved'],'Retain full original lookup contract and unknown global domain')
 return dict(schema='TSL9-mode-state-writer-contract-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),whole_functions=rows,reference_CODE_bytes=len(selected),reference_instructions=len(ops),native_CODE_comparisons=native,selected_native_CODE_bytes=69412,selected_native_instructions=23602,state_base=base,mode_address=base+1,physical_RAM_mapping_proved=False,setter=dict(start=0xd05c,end=0xd07c,mode_store_PC=0xd06e,mode_expression='low8(incoming A0)',enable=1,selector_expression='low8(-incoming A2)',countdown_expression='low8(incoming A1)',local_mode_guard=False),direct_encoded_setter_calls=callers,conditional_word_writes=word_writes,scoped_explicit_modes=[1,2,3,4,5],opaque_initializer=dict(function=0xd0ee,table_slot=0x40048,destination=base,A1=0,A2=16,callee_identity_effects_or_zeroing_proved=False),conditional_mode_DATA_gaps=gaps,all_aliases_indirect_callers_IRQ_DMA_or_excluded_writers_covered=False,global_mode_domain_proved=False,full_provider_definition_justified=False,provider_resolved=False,formal_APP_source_files_unchanged=162,formal_APP_byte_coverage_unchanged=95.67,APP_source_provider_UND_unchanged=6,new_APP_CODE_or_DATA_bytes=0,source_or_native_artifact_changed=False,table_DATA_envelope_read=False,excluded_CODE_or_default_payload_read=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False,goal_complete=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit();dest=HERE/'verification-v1.json'
  if a.write_receipt:need(not dest.exists(),'Create-only receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(dest.exists()and v==read(dest),'Fresh actual contract equals retained receipt')
  print(json.dumps(dict(passed=True,reference_CODE_bytes=v['reference_CODE_bytes'],reference_instructions=v['reference_instructions'],direct_calls=5,scoped_explicit_modes=[1,2,3,4,5],conditional_mode_DATA_gap_bytes=32,global_mode_domain_proved=False,provider_resolved=False,new_BIN=False)))
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
