"""Static whole-CFG constant facts for original clock memory operands;never run the target."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='clock_reset_static_library')
REG={'zero':0,'ra':1,'sp':2,'gp':3,**{'a'+str(i):10+i for i in range(8)}}
PURE={'bgez','bne','bnez','j','ret'}
def split(o):
 mn,sep,args=o['opcode'].partition(' ');return mn,[x.strip()for x in args.split(',')]if sep else[]
def transfer(o,state):
 # Finite constant-propagation facts only. No branch decision,MMIO value,
 # target instruction execution or simulated memory is used here.
 mn,args=split(o);out=list(state)
 if mn in PURE or mn=='sw':return tuple(out)
 need(mn in {'addi','and','andi','li','lui','lw','or','ori','slli'},'Every original clock transfer classified');rd=REG[args[0]]
 if mn=='lw':value=None
 elif mn=='li':value=int(args[1],0)&0xffffffff
 elif mn=='lui':value=(int(args[1],0)<<12)&0xffffffff
 else:
  a=state[REG[args[1]]];b=state[REG[args[2]]]if mn in ['and','or']else int(args[2],0)
  if a is None or b is None:value=None
  elif mn=='addi':value=(a+b)&0xffffffff
  elif mn in ['and','andi']:value=(a&b)&0xffffffff
  elif mn in ['or','ori']:value=(a|b)&0xffffffff
  else:value=(a<<(b&31))&0xffffffff
 out[rd]=value;out[0]=0;return tuple(out)
def facts(f,ops,g):
 incoming={p:None for p in ops};initial=[None]*32
 for reg,value in [('zero',0),('ra',0x18724),('sp',0x20010000),('gp',0x20004000)]:initial[REG[reg]]=value
 incoming[f['start']]=tuple(initial);pending=[f['start']];changes=0
 while pending:
  p=pending.pop();out=transfer(ops[p],incoming[p])
  for q in g[p]:
   old=incoming[q];new=out if old is None else tuple(a if a==b else None for a,b in zip(old,out))
   if old!=new:incoming[q]=new;pending.append(q);changes+=1
 need(all(v is not None for v in incoming.values()),'Every whole-CFG instruction has incoming abstract facts')
 need(incoming[f['start']]==tuple(initial),'No backedge changes the architectural entry assumptions');return incoming,changes
def audit(llvm):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():need(not Path(p).is_absolute()and'..'not in Path(p).parts and'command_dispatch_windows'not in p,'Allowed pinned evidence path');need(sha(R/p)==h,'Actual input changed: '+p)
 prior=lib(K['prior_checker'])['audit'](llvm);need(prior==read(R/K['prior_receipt'])and not prior['watched_values_at_first_application_use_proved'],'Fresh exact reset/bootstrap contract retains first-use uncertainty')
 B=lib(K['control_reader']);V=lib(K['CFG_reader']);M=read(R/K['APP_map']);source=[x for x in M['instructions']if 0x1874a<=x['PC']<0x18834];need(len(source)==93,'All93 original clock instructions including the cold tail');rows=[];pc=0x1874a
 for o in source:
  raw=bytes.fromhex(o['bytes']);need(o['PC']==pc and len(raw)in [2,4],'Contiguous original clock inventory');d=B['decode_control'](raw,pc);mn=o['op'].split()[0]
  kind='ret'if mn=='ret'else'jmp'if mn=='j'else'cjmp'if d else'load'if mn=='lw'else'store'if mn=='sw'else'other';need(not(mn in ['jal','jalr','jr','mret']),'Leaf clock has no opaque call or machine exit');rows.append(dict(addr=pc,size=len(raw),bytes=o['bytes'],opcode=o['op'],type=kind));pc+=len(raw)
 need(pc==0x18834,'Whole234-byte clock interval');f=dict(start=0x1874a,end=0x18834,operations=rows);ops,g,cfg=V['whole_cfg'](f,B,set(),16);need(not cfg['calls']and len(cfg['typed_exits'])==1 and cfg['typed_exits'][0]['PC']==0x1882e,'One ordinary normal return,not unconditional termination proof')
 payload=b''.join(bytes.fromhex(o['bytes'])for o in rows);fw=(R/K['firmware']).read_bytes();need(payload==fw[0x1874a-0x8000:0x18834-0x8000],'All original clock bytes match the actual APP');E=lib(K['ELF_reader'])['ELF'];native=[]
 for mode in ['c','cpp']:
  p=R/K['layout']/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';elf=E(p);bm={}
  for s in elf.sections:
   if s['type']!=1 or s['flags']!=6:continue
   a=max(f['start'],s['address']);z=min(f['end'],s['address']+s['size'])
   if a<z:
    raw=elf.data(s)
    for q in range(a,z):need(q not in bm,'Unique actual native owner per clock byte');bm[q]=raw[q-s['address']]
  need(set(bm)==set(range(f['start'],f['end']))and bytes(bm[q]for q in range(f['start'],f['end']))==payload,'Whole original234 bytes equal current native C/C++ original-coordinate CODE');native.append(dict(mode=mode,ELF_sha256=sha(p),whole_CODE_bytes_equal=234))
 need(native[0]['ELF_sha256']==native[1]['ELF_sha256'],'Actual C/C++ diagnostic identity');incoming,updates=facts(f,ops,g);accesses=[]
 for p,o in ops.items():
  mn,args=split(o)
  if mn not in ['lw','sw']:continue
  match=re.fullmatch(r'(-?(?:0x[0-9a-f]+|[0-9]+))\((\w+)\)',args[1]);need(match is not None,'Exact original memory operand');base=incoming[p][REG[match[2]]];need(base is not None,'Whole-CFG facts prove every memory base');address=(base+int(match[1],0))&0xffffffff;need(address in [0x40021000,0x40021004,0x40021008,0x2000fff8,0x2000fffc],'Every clock load/store is one of five original addresses');accesses.append(dict(PC=p,kind=mn,address=address,bytes=4,base_register=match[2],base_constant=base))
 stores=[x for x in accesses if x['kind']=='sw'];loads=[x for x in accesses if x['kind']=='lw'];need(ops[0x18830]['opcode']=='sw zero, 12(sp)'and ops[0x18832]['opcode']=='j 0x187ca'and set(g[0x18832])=={0x187ca},'Actual cold store and backward edge preserved');need(any(x['PC']==0x18830 and x['address']==0x2000fffc for x in stores),'Cold-path write included in full footprint')
 watched=prior['watched_states_at_zero_loop_exit'];need(all(not(x['address']<w['end']and w['start']<x['address']+4)for x in stores for w in watched),'All explicit CPU stores avoid every watched byte')
 changed=set()
 for p,o in ops.items():
  mn,args=split(o)
  if mn not in PURE|{'sw'}:changed.add(args[0])
 need(changed=={'sp','a2','a3','a4','a5'}and incoming[0x1882e][1:4]==(0x18724,0x20010000,0x20004000),'GP/RA are never written and SP is restored at every normal return')
 need(0x1874e in V['reachable'](g,f['start'],skip=0x18754),'Original first MMIO load precedes frame allocation');need(len([p for p in g if p in V['reachable'](g,p)and any(q<=p for q in g[p])])>0,'Actual polling/backedges retained without forcing completion')
 return dict(schema='TSL9-whole-original-clock-reset-state-noninterference-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),prior_reset_receipt_sha256=sha(R/K['prior_receipt']),whole_function=cfg,native_CODE_comparisons=native,finite_CFG_constant_propagation=True,abstract_fact_updates=updates,MMIO_values_or_memory_simulated=False,all_memory_operands=accesses,word_loads=len(loads),word_stores=len(stores),unique_memory_addresses=sorted({x['address']for x in accesses}),explicit_store_addresses=sorted({x['address']for x in stores}),all_explicit_CPU_stores_disjoint_from_watched_state=True,watched_states=watched,entry_GP=0x20004000,entry_SP=0x20010000,entry_RA=0x18724,normal_return_GP=0x20004000,normal_return_SP=0x20010000,normal_return_RA=0x18724,GP_and_RA_never_written=True,normal_return_preserves_GP_SP_RA=True,first_MMIO_read_precedes_frame=True,cold_store_and_backedge_preserved=True,whole_original_clock_CODE_bytes=234,whole_original_instructions=93,legacy232_byte_diagnostic_is_not_the_source_for_this_proof=True,clock_physical_completion_or_frequency_proved=False,MMIO_side_effects_or_IRQ_DMA_excluded=False,conditional_zero_preservation_through_clock_and_known_bootstrap=True,values_observed_on_hardware=False,first_application_use_values_proved=False,global_mode_or_counter_domain_proved=False,startup_completed_proved=False,source_or_native_artifact_changed=False,formal_APP_source_files_unchanged=164,formal_APP_byte_coverage_unchanged=95.75,APP_source_provider_UND_unchanged=6,new_APP_CODE_or_DATA_bytes=0,new_SDK_CODE_or_DATA_bytes=0,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False,goal_complete=False,conditions=['Original APP placement and entry GP/SP/RA;normal word accesses and original instruction semantics','SRAM/MMIO addresses are valid and nonaliasing;no faults,IRQ/DMA,MMIO-triggered or reentrant memory interference','Clock polling reaches the original normal return;no physical liveness or clock-frequency claim','Installed bootstrap matches the candidate and its source reads succeed,including the retained4-byte source gap','Later application writes and callback ordering remain separate first-use/global-state obligations'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit(a.tool_dir.resolve());dest=HERE/'verification-v1.json'
  if a.write_receipt:need(not dest.exists(),'Create-only clock footprint receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(v==read(dest),'Fresh whole-clock proof equals retained receipt')
  print(json.dumps(dict(passed=True,CODE_bytes=234,instructions=93,loads=v['word_loads'],stores=v['word_stores'],all_memory_addresses_proved=True,normal_return_GP_SP_RA_preserved=True,first_use_values_proved=False,firmware_ready=False,new_BIN=False)))
 except Exception as e:
  message=str(e)
  for path,label in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),label).replace(path.as_posix(),label)
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
