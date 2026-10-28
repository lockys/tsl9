"""Audit the real source-proven original-coordinate DATA extension without executing it."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='lookup_original_coordinate_audit')
def canonical(v):return json.loads(json.dumps(v))
def audit(llvm):
    E=read(HERE/'audit-inputs-v1.json')
    for p,h in E['pins'].items():need(sha(R/p)==h,'Pinned completed native/source/layout input '+p)
    L=lib('experiments/tsl9-original-layout/build-v69.py');L['pins'](llvm);proof=L['source_proof'](llvm);saved=read(R/E['layout_receipt']);need(canonical(proof)==saved['source_proof'],'Fresh163-source proof equals completed actual layout receipt')
    component=L['E'](L['source']('c'));plan=L['derive'](component);folder=(R/E['layout_receipt']).parent/'c';need(plan==read(folder/'layout-map.json'),'Actual source component derives exact linked owner map')
    old=read(R/E['parent_layout_map']);code=lambda p:[{k:o[k]for k in ['name','original_PC','bytes','source_sha256']}for o in p['owners']if o['info']==18];need(code(old)==code(plan)and len(code(plan))==6182,'Every original69412 CODE byte carrier,owner and coordinate retained')
    prior={o['name']:o for o in old['owners']};now={o['name']:o for o in plan['owners']};need(set(prior)<=set(now),'All previous6243 positive owners retained')
    for name,p in prior.items():need(all(now[name][k]==p[k]for k in ['name','info','original_PC','bytes','source_sha256']),'Every prior CODE/DATA owner byte identity and coordinate retained')
    added=[o for o in plan['owners']if o['name']not in prior];need([(o['original_PC'],o['bytes'],o['info'])for o in added]==[(0x1a088,16,17),(0x1a0a8,16,17)],'Only the two conditional16-byte readonly windows added')
    import_roles=lambda p:[{k:v for k,v in i.items()if k!='source_symbol_index'}for i in p['imports']]
    need(import_roles(plan)==import_roles(old)and len(plan['imports'])==6 and plan['real_DATA_label_bindings']==old['real_DATA_label_bindings'],'All six semantic import roles and real DATA labels retained; symbol-table indices may shift when a FILE/three objects are appended')
    independent=lib('experiments/tsl9-original-layout/compare-diagnostic-v1.py');native={};hashes=[]
    for mode in ['c','cpp']:
        f=(R/E['layout_receipt']).parent/mode;path=f/'NONLOADABLE-ORIGINAL-LAYOUT.elf';need(L['inventory'](f)==saved['modes'][mode]['artifacts'],'Every retained native layout output unchanged')
        e=L['E'](path);need(sha(L['source'](mode))==L['K']['source_sha256'],'Actual C/C++ source component identity');hashes.append(sha(path));native[mode]=independent['audit'](path,e);need(native[mode]['passed'],'Independent actual diagnostic reader agreement')
    need(len(set(hashes))==1 and native['c']==native['cpp'],'Actual complete C/C++ diagnostics identical')
    linked=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf';result=L['audit_link'](linked,component,plan);need(result==saved['modes']['c']['result']==saved['modes']['cpp']['result'],'Fresh complete original-byte/address/relocation-role audit matches actual link')
    continuation=L['fallthrough'](plan,L['E'](linked));need(continuation==saved['modes']['c']['fallthrough']==saved['modes']['cpp']['fallthrough']==read(R/E['parent_continuations']),'Every CODE continuation-position result retained, including inherited conservative startup-to-vector observation')
    elf=L['E'](linked);owned={p for s in elf.sections if s['flags']&2 and s['size']for p in range(s['address'],s['address']+s['size'])};whole=set(range(0x8000,0x1ac00));withheld=set(range(0x14056,0x14c8a))|set(range(0x1a69c,0x1a6a0));need(len(owned)==73510 and owned<=whole and not owned&withheld,'Exactly73510 actual allocated original bytes, without withheld content or padding')
    need(len(whole-owned)==3290 and len(whole-owned-withheld)==162,'Residual3290 bytes are3128 withheld plus162 other unselected bytes')
    rows=[]
    for mode,start in [(1,0x1a088),(3,0x1a0a8)]:
        end=start+16;need(set(range(start,end))<=owned,'Every conditional row byte has positive native DATA')
        owners=[o for o in plan['owners']if o['info']==17 and o['original_PC']==start and o['bytes']==16 and o['name']=='tsl9_record_mode_read_window_'+format(start,'x')];need(len(owners)==1,'One real row owner,not a full provider alias');rows.append(dict(conditional_mode=mode,start=start,end=end,bytes=16,owner=owners[0]['name']))
    state=read(R/'experiments/tsl9-record-mode-row-data/verification-v1.json')['state_contract'];need(state['scoped_explicit_modes']==[1,2,3,4,5]and not state['global_mode_domain_proved']and not state['provider_resolved'],'Retain scoped original writer proof and unknown global mode-at-read')
    conditions=['Original mode-at-read1or3 and column0..15;all columns are bounded but their actual reachability is unobserved','Valid original RAM/register mapping and buffer;physical mapping remains unproved','Aliases,indirect callers,excluded writers,IRQ/DMA and write-to-read coherence remain open','Two positive row owners do not establish full original table extent or resolve1A078 provider']
    return dict(schema='TSL9-source-curated-original-coordinate-mode-row-DATA-audit-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'audit-inputs-v1.json'),source_proof=proof,native_layout_result=result,independent_diagnostic_readers=native,new_DATA_rows=rows,new_source_DATA_bytes=32,conditional_read_bytes_backed=32,conditions=conditions,all_prior_CODE_and_DATA_owner_bytes_and_coordinates_retained=True,CODE_owner_records=6182,CODE_bytes=69412,DATA_bytes=4098,original_coordinate_bytes_equal=73510,coverage_percent=95.72,source_C_H_files=163,source_comparisons=274,source_objects=548,compiler_UND=6,real_DATA_labels=6,new_DATA_labels=0,uncovered_bytes=3290,withheld_missing_bytes=3128,other_unselected_bytes=162,CODE_continuation_result_unchanged=True,conservative_continuation_observations=continuation['uncovered_continuations'],full_provider_binding_justified=False,global_state_invariant_proved=False,withheld_payload_or_individual_hash_output=False,original_coordinate_link_performed=True,source_curated=True,installed_ROM_RAM_IRQ_Flash_OTA_proved=False,full_firmware_rebuilt=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve())
        if a.write_receipt:
            out=HERE/'audit-result-v1.json';need(not out.exists(),'Create-only actual original-coordinate audit receipt');out.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v[k]for k in ['passed','source_C_H_files','source_comparisons','source_objects','CODE_bytes','DATA_bytes','original_coordinate_bytes_equal','coverage_percent','compiler_UND','new_source_DATA_bytes','conditional_read_bytes_backed','other_unselected_bytes','new_BIN']}))
    except Exception as error:
        message=str(error)
        for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
