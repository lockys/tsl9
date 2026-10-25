"""Verify actual original-VA table cells, CODE destinations and HI/LO arguments."""
import hashlib,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LAYOUT=ROOT/'experiments/tsl9-original-layout/build/central-callbacks-v2'
S=json.loads((HERE/'spec-v1.json').read_text())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_at(e,address,size):
    sections=[s for s in e.sections if s['flags']&2 and s['address']<=address and address+size<=s['address']+s['size']]
    need(len(sections)==1,'One actual allocated original-VA owner')
    s=sections[0];start=address-s['address'];return e.data(s)[start:start+size]
def audit():
    native=runpy.run_path(str(HERE/'build-v1.py'),run_name='offline_table_source_library')
    native['static_audit']()
    need(sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned actual ELF reader')
    ELF=runpy.run_path(str(ROOT/S['reader']))['ELF']
    record=json.loads((LAYOUT/'measurement.json').read_text());results={}
    for mode in ['c','cpp']:
        folder=LAYOUT/mode;path=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf';e=ELF(path)
        result=record['modes'][mode]['result'];need(result['passed'] and sha(path)==result['ELF_sha256'],'Exact retained actual layout proof')
        need(result['curated_integration'] and result['source_C_H_files']==156 and result['source_comparisons']==260 and result['source_objects']==520,'Actual complete curated source layout')
        need(result['original_coordinate_bytes_equal']==70522 and result['applied_relocations_retained']==4972 and result['ABS_FUNC_providers']==0,'Complete measured byte/reference scope')
        need(e.header[0]==2 and e.header[3]==0 and not any(p[0]==1 for p in e.program_headers),'Diagnostic entry zero, no PT_LOAD')
        globals_=[s for s in e.symbols if s['info']>>4]
        gm={s['name']:s for s in globals_};need(len(gm)==len(globals_),'Unique actual linked globals')
        # This ELF deliberately has six hidden reference-only ABS constants.
        # They are not function bodies; native globals_of rejects ABS by design.
        bindings=[]
        for d in S['data_regions']:
            v=gm[d['name']];need(v['info']==17 and v['value']==d['start'] and v['size']==d['bytes'],'Every table has exact original VMA and positive OBJECT extent')
            need(e.sections[v['section']]['flags']==2,'Actual readonly table allocation')
            raw=read_at(e,d['start'],d['bytes'])
            for index,(target,name) in enumerate(zip(d['targets'],d['target_symbols'])):
                cell=d['start']+4*index;word=int.from_bytes(raw[4*index:4*index+4],'little')
                if not target:
                    need(word==0 and not any(r['offset']==cell for r in e.relocations),'Original null callback remains zero without relocation')
                    continue
                fn=gm[name];need(fn['info']==18 and fn['value']==target and fn['size']>0 and e.sections[fn['section']]['flags']==6,'Target is real positive FUNC at original CODE address')
                if d['kind']=='signed-relative-event-table':
                    value=int.from_bytes(raw[4*index:4*index+4],'little',signed=True)
                    need((d['start']+value)&0xffffffff==fn['value'],'Actual relative cell lands on measured CODE entry')
                else:
                    need(word==fn['value'],'Actual relocated callback cell equals real CODE VMA')
                    refs=[r for r in e.relocations if r['offset']==cell]
                    need(len(refs)==1 and refs[0]['type']==1 and refs[0]['addend']==0 and e.symbols[refs[0]['symbol']]['name']==name,'Retained applied R_RISCV_32 points at the exact FUNC')
                bindings.append(dict(cell=cell,original_target=target,actual_CODE_provider=name))
        args=[]
        for hipc,lopc,rd,target,name in [(0x1154e,0x11552,14,0x1a548,'tsl9_central_event_callbacks_static_data_1a548'),
                                       (0x12372,0x12376,12,0x1a674,'tsl9_registered_callbacks_static_data_1a674'),
                                       (0x1237a,0x1237e,11,0x1a668,'tsl9_registered_callbacks_static_data_1a668')]:
            hi=int.from_bytes(read_at(e,hipc,4),'little');lo=int.from_bytes(read_at(e,lopc,4),'little')
            need(hi&127==0x17 and (hi>>7)&31==rd and lo&0x707f==0x13 and (lo>>7)&31==(lo>>15)&31==rd,'Original AUIPC/ADDI opcode and register identity')
            high=hi&0xfffff000;high=high-0x100000000 if high&0x80000000 else high
            low=lo>>20;low=low-4096 if low&2048 else low
            need((hipc+high+low)&0xffffffff==target==gm[name]['value'],'Actual linked pointer argument reaches selected real table')
            h=[r for r in e.relocations if r['offset']==hipc and r['type']==23]
            l=[r for r in e.relocations if r['offset']==lopc and r['type']==24]
            need(len(h)==len(l)==1 and e.symbols[h[0]['symbol']]['name']==name,'Actual HI relocation names the real DATA provider')
            anchor=e.symbols[l[0]['symbol']]
            need(anchor['info']==0 and anchor['value']==hipc,'Actual LO references its exact local HI anchor')
            args.append(dict(HI=hipc,LO=lopc,register=rd,actual_table_VMA=target,DATA_provider=name))
        continuation=json.loads((folder/'continuations.json').read_text())
        expected=[dict(last_PC=0x8034,next_PC=0x8038,owner='tsl9_boot_8004',target=None)]
        need(continuation['uncovered_continuations']==expected and read_at(e,0x8034,4)==bytes.fromhex('73001000'),'Only conservative fallthrough gap is the retained original EBREAK trap')
        need(len(bindings)==22 and len(args)==3,'All table cells and three pointer materializations')
        results[mode]=dict(passed=True,table_CODE_bindings=bindings,actual_HI_LO_table_arguments=args,
                           original_coordinate_bytes_equal=70522,RELA=4972,reference_only_constants=6,
                           guarded_event_table_cells=17,nonnull_callback_cells=5,null_callback_cells=1,
                           ordinary_uncovered_continuations=0,retained_original_EBREAK=1,
                           ELF_sha256=sha(path),curated_integration=True,accepted_coordinate_coverage_percent=91.83,
                           source_C_H_files=156,source_comparisons=260,source_objects=520,original_coordinate_link_performed=True,
                           installed_ROM_ABI_verified=False,original_declaration_extents_proved=False,
                           target_executed=False,new_BIN=False,firmware_ready=False)
    need(results['c']['ELF_sha256']==results['cpp']['ELF_sha256'],'Identical actual diagnostic C/C++ ELFs')
    return dict(passed=True,modes=results)
if __name__=='__main__':
    value=audit();print(json.dumps({k:v for k,v in value['modes']['c'].items() if k not in ['table_CODE_bindings','actual_HI_LO_table_arguments']}))
