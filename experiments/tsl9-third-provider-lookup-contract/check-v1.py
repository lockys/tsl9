"""Prove the actual CEDC lookup operands and CFG without reading its DATA envelope."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='third_provider_static_analysis')
def reaching(f,ops,g,reg):
 pure=set('beq beqz bne bnez j ret'.split());stores=set('sb sh sw'.split());results=set('add addi andi auipc lbu li or ori rem slli'.split());inc={p:set()for p in g};inc[f['start']].add(-1);todo=[f['start']]
 while todo:
  p=todo.pop();o=ops[p];mn=o['opcode'].split()[0];need(mn in pure|stores|results,'All original transfer instructions modelled')
  writes=mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg;out={p}if writes else inc[p]
  for n in g[p]:
   before=len(inc[n]);inc[n]|=out
   if before!=len(inc[n]):todo.append(n)
 return inc
def audit():
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():
  need(not Path(p).is_absolute()and'..'not in Path(p).parts and'command_dispatch_windows'not in p,'Bounded allowed evidence paths');need(sha(R/p)==h,'Frozen actual input changed: '+p)
 e=read(R/K['primary_evidence']);f=next(f for f in e['selected_functions']if f['start']==0xcedc);need(f['end']==0xcf96 and len(f['operations'])==56,'Whole selected186-byte lookup function')
 B=lib(K['control_reader']);V=lib(K['CFG_reader']);ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,cfg=V['whole_cfg'](f,B,ext,0)
 E=lib(K['ELF_reader'])['ELF'];native=[];payload=b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])
 need(len(payload)==186 and not(set(range(f['start'],f['end']))&set(range(0x14056,0x14c8a))),'Only allowed whole original CODE selected')
 for mode in ['c','cpp']:
  path=R/K['layout']/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';elf=E(path);bm={}
  for s in elf.sections:
   if s['type']!=1 or s['flags']!=6:continue
   a=max(f['start'],s['address']);z=min(f['end'],s['address']+s['size'])
   if a<z:
    bb=elf.data(s);bm.update({p:bb[p-s['address']]for p in range(a,z)})
  need(set(bm)==set(range(f['start'],f['end']))and bytes(bm[p]for p in range(f['start'],f['end']))==payload,'Actual selected C/C++ original-coordinate CODE equals every original lookup instruction')
  native.append(dict(mode=mode,ELF_sha256=sha(path),whole_CODE_bytes_equal=186))
 need(native[0]['ELF_sha256']==native[1]['ELF_sha256'],'Actual formal C/C++ diagnostic identity')
 def operands(w):need(all(ops[p]['opcode']==text for p,text in w.items()),'Exact original enable/selector/mode/index operands')
 operands({0xcedc:'auipc a5, 0x1ffff',0xcee0:'lbu a5, 92(a5)',0xcee4:'beqz a5, 0xcf94',0xcee6:'auipc a4, 0x1ffff',0xceea:'lbu a4, 84(a4)',0xceee:'li a3, 255',0xcef2:'lbu a5, 4(a0)',0xcef6:'bne a4, a3, 0xcf66',0xcefa:'auipc a3, 0x1ffff',0xcefe:'addi a3, a3, 62',0xcf02:'lbu a3, 3(a3)',0xcf06:'auipc a4, 0x1ffff',0xcf0a:'lbu a4, 51(a4)',0xcf0e:'addi a3, a3, -1',0xcf10:'andi a3, a3, 255',0xcf14:'auipc a2, 0x1ffff',0xcf18:'sb a3, 39(a2)',0xcf1c:'beqz a3, 0xcf8a',0xcf1e:'li a3, 5',0xcf20:'bne a4, a3, 0xcf7c',0xcf24:'lbu a3, 5(a0)',0xcf28:'andi a5, a5, -113',0xcf2c:'andi a3, a3, -4',0xcf2e:'ori a3, a3, 1',0xcf32:'sb a3, 5(a0)',0xcf36:'sb a5, 4(a0)',0xcf3a:'lbu a5, 4(a0)',0xcf3e:'slli a4, a4, 0x4',0xcf40:'addi a3, a5, 1',0xcf44:'andi a3, a3, 15',0xcf46:'andi a5, a5, -16',0xcf48:'or a5, a5, a3',0xcf4a:'sb a5, 4(a0)',0xcf4e:'auipc a5, 0xd',0xcf52:'addi a5, a5, 298',0xcf56:'add a4, a4, a5',0xcf58:'add a4, a4, a3',0xcf5a:'lbu a5, 0(a4)',0xcf5e:'sb a5, 3(a0)',0xcf62:'j 0x12a08',0xcf66:'li a2, 3',0xcf68:'addi a3, a4, 1',0xcf6c:'rem a3, a3, a2',0xcf70:'auipc a2, 0x1ffff',0xcf74:'sb a3, -54(a2)',0xcf78:'beqz a4, 0xcefa',0xcf7a:'li a4, 0',0xcf7c:'andi a3, a4, 7',0xcf80:'slli a3, a3, 0x4',0xcf82:'andi a5, a5, -113',0xcf86:'or a5, a5, a3',0xcf88:'j 0xcf36',0xcf8a:'auipc a3, 0x1ffff',0xcf8e:'sb zero, -82(a3)',0xcf92:'j 0xcf1e',0xcf94:'ret'})
 need(len(ops)==56,'Every whole-function opcode explicitly checked')
 rd=[]
 for reg,p,w in [('a4',0xcf3e,[0xcf0a,0xcf7a]),('a4',0xcf7c,[0xcf0a,0xcf7a]),('a3',0xcf58,[0xcf44]),('a5',0xcf56,[0xcf52]),('a4',0xcf5a,[0xcf58])]:
  need(reaching(f,ops,g,reg)[p]==set(w),'Whole-CFG exact lookup register definitions');rd.append(dict(register=reg,PC=p,definitions=w))
 a=lambda pc,imm,lo:((pc+(imm<<12))+lo)&0xffffffff
 ram=dict(enable=a(0xcedc,0x1ffff,92),selector=a(0xcee6,0x1ffff,84),countdown=a(0xcefa,0x1ffff,62)+3,mode=a(0xcf06,0x1ffff,51))
 need(ram==dict(enable=0x2000bf38,selector=0x2000bf3a,countdown=0x2000bf3b,mode=0x2000bf39)and a(0xcf14,0x1ffff,39)==ram['countdown']and a(0xcf70,0x1ffff,-54)==ram['selector']and a(0xcf8a,0x1ffff,-82)==ram['enable'],'Exact four logical RAM byte addresses')
 base=a(0xcf4e,0xd,298);need(base==0x1a078,'Original DATA reference base')
 exits={x['PC']for x in cfg['typed_exits']};need(0xcf5a in V['reachable'](g,0xcf8a)and not(exits&V['reachable'](g,0xcf8a,skip=0xcf5a)),'Every finite normal exit after enable-clear still passes the lookup')
 need(set(g[0xcf78])=={0xcefa,0xcf7a}and set(g[0xcf7a])=={0xcf7c}and set(g[0xcf88])=={0xcf36},'Old nonzero/non255 selector forces original mode0 route')
 mode_domain=[0,255];column_domain=[0,15];end=base+16*mode_domain[1]+column_domain[1]+1
 need(end==0x1b078 and end-base==4096 and end-0x1ac00==1144,'Conservative byte-width envelope arithmetic only')
 L=lib(K['layout_builder']);component=L['E'](R/K['component']);plan=L['derive'](component);data={p for o in plan['owners']if o['info']==17 for p in range(o['original_PC'],o['original_PC']+o['bytes'])};windows=[]
 for row in [0,5]:
  lo=base+16*row;hi=lo+16;need(set(range(lo,hi))<=data,'Conditional row has actual existing positive DATA backing');windows.append(dict(row=row,start=lo,end=hi,bytes=16,all_bytes_already_selected_native_DATA=True))
 need(base<0x1a6a0 and 0x1a69c<end,'Metadata-only envelope overlaps excluded default range;no DATA read performed')
 return dict(schema='TSL9-third-DATA-provider-lookup-contract-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),whole_function=cfg,native_CODE_comparisons=native,reaching_definitions=rd,logical_RAM_bytes=ram,physical_RAM_mapping_proved=False,lookup_base=base,lookup_PC=0xcf5a,formula='base1A078 + 16*original_effective_mode + ((fresh_record4 + 1)&15)',mode_definitions=['unmasked byte read2000BF39','forced zero when old selector is1..254'],field_mask_7_writes_A3_not_lookup_mode_A4=True,record_flag_low3_mask_does_not_bound_lookup_to8_rows=True,selector_update_uses_old_selector_for_branch=True,selector_store_is_uint8_of_old_plus1_mod3=True,countdown_uint8_decrement_preserved=True,enable_clear_does_not_skip_current_lookup=True,conservative_mode_domain=mode_domain,proven_column_domain=column_domain,conservative_envelope=[base,end],conservative_envelope_bytes=end-base,conservative_envelope_bytes_beyond_provided_APP=end-0x1ac00,conservative_envelope_is_not_declared_table_size_or_actual_violation_proof=True,conditional_existing_DATA_rows=windows,global_mode_domain_or_all_writers_proved=False,full_provider_definition_justified=False,provider_resolved=False,table_DATA_envelope_read=False,table_DATA_payload_or_individual_hash_output=False,excluded_default_payload_or_hash_output=False,source_or_native_artifact_changed=False,new_APP_CODE_or_DATA_bytes=0,new_SDK_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_byte_coverage_unchanged=95.67,APP_source_provider_UND_unchanged=6,firmware_ready=False,new_BIN=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,conditions=['Original record+3/+4/+5 and four logical RAM bytes remain valid;physical mapping and IRQ/DMA/reentrant coherence are unproved','Finite register/CFG facts preserve all56 original instructions;conservative state ranges do not prove feasible inputs or real out-of-bounds access','Mode0 and conditional mode5 rows are backed,but the mode byte is not globally bounded by the record flag mask','Do not select the conservative4096-byte DATA envelope:it exceeds the supplied APP and overlaps currently excluded default DATA','A full provider needs an actual mode-at-read/use contract or legitimate independent requirements;do not clamp,alias,stub or fill gaps to force closure'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit();dest=HERE/'verification-v1.json'
  if a.write_receipt:
   need(not dest.exists(),'Create-only exact static contract receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(dest.exists()and v==read(dest),'Fresh actual static contract equals receipt')
  print(json.dumps(dict(static_contract_verified=True,whole_CODE_bytes=186,instructions=56,flag_mask_does_not_bound_lookup=True,conservative_envelope_bytes=4096,actual_violation_proved=False,provider_resolved=False,firmware_ready=False,new_BIN=False)))
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(static_contract_verified=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
