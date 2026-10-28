"""Audit original APP coverage and a partially backed data reference; no payload extraction."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='APP_residual_static_library')
def canonical(v):return json.loads(json.dumps(v))
def spans(values):
    out=[]
    for p in sorted(values):
        if out and out[-1][1]==p:out[-1][1]=p+1
        else:out.append([p,p+1])
    return out
def verify(llvm):
    E=read(HERE/'inputs-v1.json');need(all(sha(R/p)==h for p,h in E['reference_inputs'].items()),'Every frozen source/native/layout input retained')
    L=lib('experiments/tsl9-original-layout/build-v65.py');L['pins'](llvm);proof=L['source_proof'](llvm);saved=read(R/'experiments/tsl9-original-layout/build/safe-gap-v2/measurement.json')
    need(canonical(proof)==saved['source_proof'],'Fresh complete159-file/532-object source proof retained')
    native={}
    for mode in ['c','cpp']:
        path=R/E['APP_ELF'].replace('/c/','/'+mode+'/');need(sha(path)==E['APP_ELF_sha256'],'Actual identical nonloadable C/C++ APP diagnostic')
        src=L['E'](L['source'](mode));plan=L['derive'](src);L['validate_original'](src,plan);v=L['audit_link'](path,src,plan)
        need(canonical(v)==saved['modes'][mode]['result'],'Fresh actual original-address link audit matches retained receipt');native[mode]=v
    need(native['c']==native['cpp'],'Actual C/C++ APP diagnostic results identical')
    elf=L['E'](R/E['APP_ELF']);owned={p for s in elf.sections if s['flags']&2 and s['size']for p in range(s['address'],s['address']+s['size'])};whole=set(range(E['APP_start'],E['APP_end']));withheld={p for a,z in E['withheld_ranges']for p in range(a,z)}
    need(owned<=whole and len(owned)==73374 and not owned&withheld,'All actual73374 selected bytes, no withheld coverage')
    missing=whole-owned;need(len(missing)==3426 and len(missing&withheld)==3128 and len(missing-withheld)==298,'Exact missing-byte partition; no padding added')
    layout=read(R/'experiments/tsl9-original-layout/build/safe-gap-v2/c/layout-map.json');imports=layout['imports'];need(len(imports)==6,'Six actual compiler import references remain')
    target=0x1a078;owners=[o for o in layout['owners']if o['original_PC']<=target<o['original_PC']+o['bytes']]
    need(len(owners)==1,'One positive real owner covers reference base');owner=owners[0]
    need(owner['info']==17 and owner['name']=='tsl9_grid_read_data_pool_19ed8'and owner['original_PC']==0x19ed8 and owner['bytes']==432 and owner['original_PC']+owner['bytes']==0x1a088,'Readonly432-byte pool backs only16 bytes from1A078 onward')
    unit=read(R/'experiments/tsl9-record-field-transitions/spec-v1.json');pair=next(v for v in unit['PC_relative_pairs']if v['PC']==0xcf4e)
    need(pair['target_PC']==target and pair['reference_kind']=='unbounded-static-data-address'and not pair['referent_provided'],'Original source explicitly leaves this provider unresolved')
    A=read(R/'analysis/record-field-transitions-2026-10-25/evidence.json');f=next(f for f in A['selected_functions']if f['start']<=0xcf4e<f['end']);need((f['start'],f['end'])==(0xcedc,0xcf96),'Complete original consumer scope')
    need(not any(a<f['end']and f['start']<z for a,z in E['withheld_ranges']),'Selected consumer does not intersect withheld CODE')
    raw=(R/unit['firmware']).read_bytes()[f['start']-0x8000:f['end']-0x8000]
    need(raw==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'Actual original consumer bytes only; no residual DATA payload read')
    code=[s for s in elf.sections if s['flags']&6==6 and s['address']<=f['start']and f['end']<=s['address']+s['size']];need(len(code)==1,'One actual native CODE owner span')
    section=code[0];need(elf.data(section)[f['start']-section['address']:f['end']-section['address']]==raw,'Compiled original-coordinate consumer bytes identical')
    B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,cfg=V['whole_cfg'](f,B,ext,0)
    expected={0xcf3a:'lbu a5, 4(a0)',0xcf3e:'slli a4, a4, 0x4',0xcf40:'addi a3, a5, 1',0xcf44:'andi a3, a3, 15',0xcf4e:'auipc a5, 0xd',0xcf52:'addi a5, a5, 298',0xcf56:'add a4, a4, a5',0xcf58:'add a4, a4, a3',0xcf5a:'lbu a5, 0(a4)',0xcf5e:'sb a5, 3(a0)',0xcf7a:'li a4, 0',0xcf0a:'lbu a4, 51(a4)'}
    need(all(ops[p]['opcode']==s for p,s in expected.items()),'Exact mode/nibble arithmetic and byte read operands')
    pure={'beqz','bne','beq','bnez','j','ret'};stores={'sb'};results={'auipc','lbu','li','add','addi','andi','ori','slli','or','rem'};cache={}
    def reaching(site,reg):
        if reg not in cache:
            incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
            while todo:
                pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0];need(mn in pure|stores|results,f'No unmodelled register writer at {pc:#x}: {mn}')
                writes=mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg;out={pc}if writes else incoming[pc]
                for n in g[pc]:
                    before=len(incoming[n]);incoming[n]|=out
                    if len(incoming[n])!=before:todo.append(n)
            cache[reg]=incoming
        return cache[reg][site]
    mode_defs=reaching(0xcf3e,'a4');need(mode_defs=={0xcf0a,0xcf7a}and reaching(0xcf58,'a3')=={0xcf44},'Ordinary-entry mode comes only from byte load or zero; final nibble is masked')
    for use,definition,reg in [(0xcf40,0xcf3a,'a5'),(0xcf44,0xcf40,'a3'),(0xcf56,0xcf52,'a5'),(0xcf5a,0xcf58,'a4')]:need(reaching(use,reg)=={definition},'All address-expression definitions preserved')
    h=int.from_bytes(bytes.fromhex(ops[0xcf4e]['bytes']),'little');l=int.from_bytes(bytes.fromhex(ops[0xcf52]['bytes']),'little');imm=l>>20;imm=imm-4096 if imm&2048 else imm
    need(h&127==0x17 and l&0x707f==0x13 and(h>>7)&31==(l>>7)&31==(l>>15)&31==15 and(0xcf4e+(h&0xfffff000)+imm)&0xffffffff==target,'Raw PC-relative base is exactly1A078')
    start,end=target,target+16*255+15+1;window=set(range(start,end));need((start,end)==(0x1a078,0x1b078)and len(window)==4096,'Conservative byte-mode/nibble envelope, not original declaration or reachable-value set')
    outside=window-whole;overlap=window&withheld;need(len(outside)==1144 and spans(overlap)==[[0x1a69c,0x1a6a0]],'Conservative envelope exceeds provided image and intersects withheld default word')
    facts=dict(original_APP_covered_bytes=73374,original_APP_missing_bytes=3426,withheld_missing_bytes=3128,other_uncovered_bytes=298,uncovered_intervals=spans(missing),withheld_ranges=E['withheld_ranges'],compiler_imports=[dict(name=v['source_symbol'],address=v['original_reference_PC'],body_implementation_proved=v['body_implementation_proved'])for v in imports])
    access=dict(passed=True,consumer_entry=0xcedc,consumer_end=0xcf96,consumer_CFG=cfg,address_pair=0xcf4e,read_PC=0xcf5a,base=target,expression='base + 16*mode + nibble',mode_reaching_definitions=sorted(mode_defs),ordinary_entry_mode_conservative_domain=[0,255],nibble_domain=[0,15],conservative_window=[start,end],conservative_bytes=4096,all_values_reachable_or_original_declaration_extent_proved=False,existing_owner=owner['name'],owner_range=[owner['original_PC'],owner['original_PC']+owner['bytes']],base_owner_offset=416,base_backed_suffix_bytes=16,bytes_outside_provided_APP=len(outside),withheld_intersection=spans(overlap),provided_native_bytes_in_envelope=len(window&owned),missing_in_image_bytes=len(window&whole-owned),global_mode_invariant_or_indirect_entry_bounds_proved=False,full_provider_binding_justified=False,address_only_coverage_is_not_sufficient=True,actual_invalid_read_or_firmware_defect_proved=False)
    return dict(schema='TSL9-APP-residual-access-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),native_source_proof=dict(C_H_files=159,source_comparisons=266,source_objects=532,positive_allocated_bytes=73374),gap_map=facts,access_contract=access,original_C_Cpp_ELF_sha256=E['APP_ELF_sha256'],APP_byte_coverage_unchanged=95.54,compiler_UND_unchanged=6,new_CODE_bytes=0,new_DATA_bytes=0,new_target_compilation=False,provider_resolved=False,source_or_link_layout_modified=False,payload_or_individual_withheld_hash_output=False,installed_ROM_RAM_IRQ_Flash_OTA_proved=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipt:
            for name,value in [('verification-v1.json',v),('gaps-v1.json',v['gap_map'])]:
                dest=HERE/name;need(not dest.exists(),'Create-only receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,covered_bytes=73374,missing_bytes=3426,other_uncovered_bytes=298,conservative_access_bytes=4096,base_backed_suffix_bytes=16,bytes_outside_provided_APP=1144,provider_resolved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
