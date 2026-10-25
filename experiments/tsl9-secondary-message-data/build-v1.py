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
    need(sha(ROOT/S['source'])==S['source_sha256'],'Exact reviewed DATA C source')
    need(sha(ROOT/S['firmware'])==S['firmware_sha256'],'Actual original image')
    for p,h in S['support_inputs'].items():need(sha(ROOT/p)==h,'Pinned static dependency '+p)
    fw=(ROOT/S['firmware']).read_bytes();code=json.loads((ROOT/S['CODE_spec']).read_text());evidence=json.loads((ROOT/S['CODE_evidence']).read_text())
    pc_names={r['start']:r['name'] for r in code['regions']}
    formal=json.loads((ROOT/S['formal_parent_map']).read_text())['owners']
    need([(d['start'],d['end']) for d in S['data_regions']]==[(0x1a58c,0x1a5a8),(0x19dd4,0x19de0)],'Only seven event cells and the observed12-byte source')
    for d in S['data_regions']:
        raw=fw[d['start']-0x8000:d['end']-0x8000]
        need(len(raw)==d['bytes'] and hashlib.sha256(raw).hexdigest()==d['original_sha256'],'Exact original DATA extent')
        need(not any(r['original_PC']<d['end'] and r['original_PC']+r['bytes']>d['start'] for r in formal),'No formal DATA/CODE overlap')
        if d['kind']=='signed-relative-event-table':
            values=list(struct.unpack('<7i',raw));need(values==d['values'],'Actual seven signed offsets')
            targets=[d['start']+v for v in values]
            need(targets==d['targets'] and [pc_names[t] for t in targets]==d['target_symbols'],'Every cell maps to an actual selected CODE entry')
        else:need(list(raw)==d['values'],'Exact12-byte copy literal')
    event=lib(S['CODE_audit'])['audit']()
    need(event['passed'] and event['event_jump_table']['targets']==S['data_regions'][0]['targets'],'Original unsigned guard and all seven targets agree')
    ops={o['addr']:o for f in evidence['selected_functions'] for o in f['operations']}
    canonical=lambda pc:__import__('re').sub(r'0x([0-9a-f]+)',lambda m:str(int(m[1],16)),ops[pc]['opcode'].replace(' ',''))
    for pc,text in {0x1558e:'addisp,sp,-32',0x15594:'swra,28(sp)',0x155ae:'lia2,12',0x155b0:'auipca1,5',0x155b4:'addia1,a1,-2012',0x155b8:'addia0,sp,4'}.items():need(canonical(pc)==text,'Actual copy-call argument/frame instruction '+hex(pc))
    need(ops[0x155ba]['type']=='call' and ops[0x155ba]['jump']==0x19bf0,'Actual call to the existing forward-copy body')
    need(next(p for p in code['PC_relative_pairs'] if p['PC']==0x155b0)['target_PC']==0x19dd4,'Actual typed source address')
    mem=json.loads((ROOT/'analysis/memory-transfer-2026-10-24/evidence.json').read_text())
    # The accepted182-byte forward-copy body remains an original-context dependency.
    # This proof selects only the observed call window; it does not execute the copier.
    matching=0
    literal=bytes(S['data_regions'][1]['values'])
    for peer in S['peer_literal_evidence']:
        p=ROOT/peer['path'];need(sha(p)==peer['sha256'],'Exact comparison firmware')
        b=p.read_bytes();need(len(b)==peer['bytes'] and b.count(literal)==peer['occurrences'],'Exact fixed-literal occurrence count')
        matching+=bool(peer['occurrences'])
    need(len(S['peer_literal_evidence'])==22 and matching==18,'Shared literal in18of22 local firmware files')
    return dict(passed=True,DATA_bytes=40,positive_OBJECTs=2,event_cells=7,event_unique_targets=6,copy_source_bytes=12,copy_call_PC=0x155ba,copy_entry=0x19bf0,
                copy_frame_bytes=32,copy_destination_offset=4,saved_RA_offset=28,peer_firmware_files=22,matching_peer_files=18,
                no_neighboring_padding_selected=True,original_declaration_extents_proved=False,global_copy_or_stack_bounds_proved=False,installed_ROM_read_contract_proved=False)

def audit_object(path):
    e=elf(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL DATA object')
    gm=globals_of(e);provided={d['name'] for d in S['data_regions']};required={r['target'] for r in S['relocations']}
    need(set(gm)==provided|required,'Exactly two DATA providers and no new function dependencies')
    expected_alloc={d['section']:(1,2,d['bytes'],4) for d in S['data_regions']}
    need({s['name']:(s['type'],s['flags'],s['size'],s['align']) for s in e.sections if s['flags']&2 and s['size']}==expected_alloc,'Exactly40 readonly bytes in two observed-size allocations')
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
    need(sorted(actual)==sorted(expected) and len(actual)==0,'No relocations or hidden function substitutes in the fixed DATA unit')
    need(not any(s['section'] and s['info']&15==2 for s in e.symbols),'No function body or substitute stub')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,DATA_bytes=40,positive_OBJECTs=2,FUNC=0,RELA=0,UND=sorted(required),
                undefined_symbol_types={n:gm[n]['info'] for n in sorted(required)},
                all_original_table_cells_equal_after_PC_resolution=True,independent_readers=comparison,
                object_sha256=sha(path),original_coordinate_link_performed=False,curated_integration=False,
                target_executed=False,new_BIN=False,firmware_ready=False)
def inputs(llvm):
    pins={name:sha(llvm/name) for name in S['tools']}
    need(pins==S['tools'],'Pinned compiler/linker tools')
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned ELF reader')
    for p,h in S['support_inputs'].items():need(sha(ROOT/p)==h,'Pinned static-support input')
    for p in S['peer_literal_evidence']:need(sha(ROOT/p['path'])==p['sha256'],'Pinned peer firmware')
    return dict(build=sha(Path(__file__)),spec=sha(HERE/'spec-v1.json'),source=sha(ROOT/S['source']),
                firmware=sha(ROOT/S['firmware']),reader=sha(ROOT/S['reader']),tools=pins,stdint=S['stdint_sha256'],support=S['support_inputs'],peer_firmware=S['peer_literal_evidence'])
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
    print(json.dumps(dict(passed=True,DATA_bytes=40,OBJECTs=2,languages=['c','cpp'],object_sha256=report['modes']['c']['object_sha256'],target_executed=False)))
if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(passed=False,reason=str(error).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
