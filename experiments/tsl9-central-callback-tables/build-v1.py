"""Compile exact table windows; inspect native DATA and function references only."""
import argparse,hashlib,json,runpy,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_text())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='offline_table_library')
def elf(p):return lib(S['reader'])['ELF'](p)
def globals_of(e):
    rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows}
    need(len(m)==len(rows) and all(s['section']!=0xfff1 for s in rows),'Unique globals without ABS providers')
    return m
def static_audit():
    need(sha(ROOT/S['source'])==S['source_sha256'],'Exact reviewed C source')
    need(sha(ROOT/S['firmware'])==S['firmware_sha256'],'Original image identity')
    fw=(ROOT/S['firmware']).read_bytes()
    specs=[json.loads((ROOT/p).read_text()) for p in ['experiments/tsl9-central-callback-leaves/spec-v1.json','experiments/tsl9-central-event-callbacks/spec-v1.json']]
    pc_names={r['start']:r['name'] for s in specs for r in s['regions']}
    formal=json.loads((ROOT/'experiments/tsl9-original-layout/build/callback-prefix-data-v2/c/layout-map.json').read_text())['owners']
    pc_names.update({r['original_PC']:r['name'] for r in formal if r['info']==18})
    need([(d['start'],d['end']) for d in S['data_regions']]==[(0x1a548,0x1a58c),(0x1a668,0x1a674),(0x1a674,0x1a680)],'Only observed safe table cells; no neighboring data selected')
    for d in S['data_regions']:
        raw=fw[d['start']-0x8000:d['end']-0x8000]
        need(len(raw)==d['bytes'] and hashlib.sha256(raw).hexdigest()==d['original_sha256'],'Every original table window')
        need(not any(r['original_PC']<d['end'] and r['original_PC']+r['bytes']>d['start'] for r in formal),'No overlap with accepted original-coordinate owner')
        if d['kind']=='signed-relative-event-table':
            values=list(struct.unpack('<17i',raw));need(values==d['values'],'Actual signed event offsets')
            targets=[(d['start']+v)&0xffffffff for v in values]
        else:targets=list(struct.unpack('<3I',raw))
        need(targets==d['targets'],'Every actual original target cell')
        need([pc_names[t] if t else None for t in targets]==d['target_symbols'],'Every non-null target is a measured positive CODE entry')
    event=lib('experiments/tsl9-central-event-callbacks/audit-v1.py')['audit']()
    need(event['passed'] and event['event_jump_table_entries']==17 and event['event_jump_table_targets']==sorted(set(S['data_regions'][0]['targets'])),'Original guarded dispatch agrees with all selected table targets')
    return dict(passed=True,DATA_bytes=92,positive_OBJECTs=3,event_cells=17,event_unique_targets=7,
                callback_cells=6,non_null_callback_cells=5,null_callback_cells=1,
                original_declaration_extents_proved=False,installed_ROM_read_contract_proved=False)
def audit_object(path):
    e=elf(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL DATA object')
    gm=globals_of(e);provided={d['name'] for d in S['data_regions']};required={r['target'] for r in S['relocations']}
    need(set(gm)==provided|required,'Exactly three providers and five genuine function-address dependencies')
    expected_alloc={d['section']:(1,2,d['bytes'],4) for d in S['data_regions']}
    need({s['name']:(s['type'],s['flags'],s['size'],s['align']) for s in e.sections if s['flags']&2 and s['size']}==expected_alloc,'Exactly 92 readonly bytes in three original-size allocations')
    for name in required:
        v=gm[name];need(v['section']==v['value']==v['size']==v['other']==0 and v['info'] in (16,18),'Genuine undefined function address without storage or ABS substitution')
    fw=(ROOT/S['firmware']).read_bytes();expected=[]
    for d in S['data_regions']:
        v=gm[d['name']];sec=e.sections[v['section']]
        need((v['info'],v['other'],v['value'],v['size'],sec['name'])==(17,0,0,d['bytes'],d['section']),'Positive actual OBJECT of exact selected extent')
        raw=bytearray(e.data(sec));original=fw[d['start']-0x8000:d['end']-0x8000]
        for ref in [r for r in S['relocations'] if r['owner']==d['name']]:
            at=ref['offset'];need(raw[at:at+4]==bytes(4),'Original function cell represented by genuine zero-addend RELA')
            need(int.from_bytes(original[at:at+4],'little')==ref['target_PC'],'Relocation targets actual original callback address')
            raw[at:at+4]=ref['target_PC'].to_bytes(4,'little')
            expected.append((sec['index'],at,1,0,ref['target']))
        need(bytes(raw)==original,'Every original table byte after original-PC resolution')
    actual=[(r['section'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name']) for r in e.relocations]
    need(sorted(actual)==sorted(expected) and len(actual)==5,'All five typed R_RISCV_32 callback references, and no extra relocations')
    need(not any(s['section'] and s['info']&15==2 for s in e.symbols),'No function body or substitute stub')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,DATA_bytes=92,positive_OBJECTs=3,FUNC=0,RELA=5,UND=sorted(required),
                undefined_symbol_types={n:gm[n]['info'] for n in sorted(required)},
                all_original_table_cells_equal_after_PC_resolution=True,independent_readers=comparison,
                object_sha256=sha(path),original_coordinate_link_performed=False,curated_integration=False,
                target_executed=False,new_BIN=False,firmware_ready=False)
def inputs(llvm):
    pins={name:sha(llvm/name) for name in S['tools']}
    need(pins==S['tools'],'Pinned compiler/linker tools')
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned ELF reader')
    return dict(build=sha(Path(__file__)),spec=sha(HERE/'spec-v1.json'),source=sha(ROOT/S['source']),
                firmware=sha(ROOT/S['firmware']),reader=sha(ROOT/S['reader']),tools=pins,stdint=S['stdint_sha256'])
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-dir',type=Path,required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--trial');group.add_argument('--replay',type=Path)
    args=parser.parse_args();llvm=args.tool_dir.resolve();before=inputs(llvm);static=static_audit()
    if args.replay:
        out=args.replay.resolve();need(out.parent==HERE/'build','Owned retained table trial')
        saved=json.loads((out/'measurement.json').read_text());need(saved['inputs']==before and saved['static_audit']==static,'Every current input and static contract unchanged')
        for mode in ['c','cpp']:need(audit_object(out/mode/'unit.o')==saved['modes'][mode],'Fresh actual retained object proof')
        print(json.dumps(dict(passed=True,mode='read-only-table-replay',target_executed=False)));return
    need(args.trial and Path(args.trial).name==args.trial,'Single owned trial name')
    out=HERE/'build'/args.trial;need(not out.exists(),'Create-only trial')
    report=dict(inputs=before,static_audit=static,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'clang.exe'),*S['flags'][mode],'-c',str(ROOT/S['source']),'-o',str(folder/'unit.o')]
        result=subprocess.run(argv,capture_output=True,timeout=60)
        log=result.stderr.decode('utf-8',errors='replace').replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE')
        (folder/'compile.log').write_text(log,encoding='utf-8');need(result.returncode==0,'Compiler failed; local diagnostic retained')
        report['modes'][mode]=audit_object(folder/'unit.o')
    need(report['modes']['c']['object_sha256']==report['modes']['cpp']['object_sha256'],'Identical C/C++ DATA objects')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':main()
