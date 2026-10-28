"""Compile origin/curated readonly conditional event-word DATA in C11/C++17; no target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];S=json.loads((HERE/'spec-v1.json').read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='lookup_curated_DATA_library')
B=lib('experiments/tsl9-original-startup/build-v1.py');portable,encoded=B['portable'],B['encoded']
def source_path(v):return ROOT/S['source'if v=='origin'else'curated_source']
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def dependencies(folder,variant,llvm):return lib('scripts/verify-curated-source.py')['dependencies'](folder,variant,llvm.parent/'lib/clang/18')
def audit_object(path):return lib(S['state_checker'])['audit_data'](path,json.loads((ROOT/S['state_inputs']).read_bytes()))
def complete_projection_equal(left,right):
    E=lib(S['reader'])['ELF'];a,b=E(left),E(right)
    need([s['name']for s in a.sections]==[s['name']for s in b.sections],'Same complete section inventory')
    need(all(a.data(s)==b.data(b.section(s['name']))for s in a.sections if s['name']not in ['.symtab','.strtab']),'All nonsymbol carrier bytes equal')
    need([s for s in a.symbols if s['info']&15!=4]==[s for s in b.symbols if s['info']&15!=4],'Every non-FILE symbol record identical')
    need([s['name']for s in a.symbols if s['info']&15==4]==['event_words.v1.c']and[s['name']for s in b.symbols if s['info']&15==4]==['event_word_table_data.c'],'Only the explicit local FILE basename differs')
    need(a.relocations==b.relocations==[],'No added relocations or imports');return True
def inputs(llvm,variants):
    files={Path(__file__),HERE/'spec-v1.json',llvm.parent/'lib/clang/18/include/stdint.h'}
    files.update(ROOT/p for p in S['pins']);files.update(llvm/n for n in S['tools']);files.update(source_path(v)for v in variants)
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(files)}
def run(llvm,trial=None,replay=None):
    for p,h in S['pins'].items():need(sha(ROOT/p)==h,'Pinned DATA/source/state input '+p)
    for n,h in S['tools'].items():need(sha(llvm/n)==h,'Pinned actual local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned freestanding header')
    for variant in ['origin','curated']:need(sha(source_path(variant))==S['source_sha256'],'Exact origin/curated DATA source')
    contract=json.loads((ROOT/S['state_contract_receipt']).read_bytes())['state_contract']
    need(contract['passed']and S['state_contract_replayed_before_extension'],'Scoped use proof actually replayed before curation')
    manifest=ROOT/'src/source-manifest.json'
    if sha(manifest)!=S['state_parent_manifest_sha256']:
        parent=lib(S['parent_manifest_helper'])['raw_parent']();need(hashlib.sha256(parent).hexdigest()==S['state_parent_manifest_sha256'],'Exact historical manifest exception,not changed CODE/DATA')
    need(not contract['global_index_at_read_invariant_proved']and not contract['full_table_extent_proved'],'Retain unknown global index and full original table extent')
    variants=['origin','curated'];before=portable(inputs(llvm,variants),llvm);out=HERE/'build'/(trial if trial else 'data-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only DATA trial folder')
    else:need(replay is not None and replay.resolve()==out,'Replay only known DATA folder')
    report=dict(schema='TSL9-origin-curated-event-word-DATA-v1',inputs=before,variants=variants,state_contract=contract,modes={})
    for mode in ['c','cpp']:
        report['modes'][mode]={}
        for variant in variants:
            folder=out/mode/variant
            if trial:
                folder.mkdir(parents=True);argv=[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(source_path(variant)),'-o',str(folder/'unit.o')]
                p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(folder/'compile.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual DATA compile succeeded; diagnostic retained')
            result=audit_object(folder/'unit.o');deps=dependencies(folder,variant,llvm)
            report['modes'][mode][variant]=dict(result=result,dependencies=portable(deps,llvm),artifacts=inventory(folder))
        complete_projection_equal(out/mode/'origin/unit.o',out/mode/'curated/unit.o')
    need(report['modes']['c']==report['modes']['cpp'],'C11/C++17 full DATA measurements and dependencies identical by variant')
    need(before==portable(inputs(llvm,variants),llvm),'Every actual DATA input unchanged during compilation/replay')
    if trial:(out/'measurement.json').write_bytes(encoded(report))
    else:need(report==json.loads((out/'measurement.json').read_bytes()),'Fresh DATA/projection/dependency replay equals exact receipt')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args()
    try:
        v=run(a.tool_dir.resolve(),a.trial,a.replay);print(json.dumps(dict(passed=True,variants=v['variants'],DATA_bytes=28,comparisons=2,objects=4,original_address_link_performed=False,target_executed=False)))
    except Exception as error:
        message=str(error)
        for p,t in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
