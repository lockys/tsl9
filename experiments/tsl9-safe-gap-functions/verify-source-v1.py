"""Full159-file source proof, retaining prior CODE/DATA evidence unchanged."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'source-proof-v1.json').read_text())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='full_curated_source_library')
B=lib('experiments/tsl9-original-startup/build-v1.py')
portable,encoded=B['portable'],B['encoded']
E=lib('experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py')['ELF']
def expand(value,llvm):
    for key,path in [('PROJECT_ROOT',ROOT),('LLVM_BIN',llvm),('CLANG_RESOURCE',llvm.parent/'lib/clang/18')]:
        value=value.replace('$'+'{'+key+'}',str(path))
    return Path(value)
def inputs(llvm):
    files={Path(__file__),HERE/'source-proof-v1.json',ROOT/'src/source-manifest.json'}
    files.update(ROOT/p for p in K['pins'])
    C=lib('scripts/verify-curated-source.py');m=C['metadata']()
    files.update(Path(p) for p in C['inputs'](m))
    code_record=json.loads((ROOT/K['curation']).read_text())
    files.update((ROOT/K['curation']).parent/p for p in code_record['artifacts'])
    for mode in ['c','cpp']:files.add(ROOT/K['parent_component']/mode/K['parent_object'])
    for u in m['native_data_units']:
        V=lib(u['verifier']);r=json.loads((ROOT/u['formal_receipts'][0]).read_text())
        files.update(Path(p) for p in V['inputs'](llvm,r['variants']))
        for mode in ['c','cpp']:
            for variant in r['variants']:
                folder=(ROOT/u['formal_receipts'][0]).parent/mode/variant
                files.update(folder/p for p in r['modes'][mode][variant]['artifacts'])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)}
def proof(llvm):
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Pinned complete source-proof input '+p)
    ext=json.loads((HERE/'source-extension-v1.json').read_text());raw=lib('experiments/tsl9-safe-gap-functions/parent-manifest-v1.py')['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==ext['previous_manifest_sha256'],'Exact retained158-file parent manifest')
    previous_manifest=json.loads(raw);expected=json.loads(raw)
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:expected[group]+=ext[key]
    need(sha(ROOT/'src/source-manifest.json')==ext['new_manifest_sha256'] and expected==json.loads((ROOT/'src/source-manifest.json').read_text()),'Only one source file and one CODE unit appended; DATA unchanged')
    C=lib('scripts/verify-curated-source.py');m=C['metadata']()
    need((len(m['files']),len(m['native_units']),len(m['native_data_units']))==(159,125,8),'Complete159-file125-CODE/eight-DATA scope')
    now=json.loads((ROOT/K['curation']).read_text());base=(ROOT/K['curation']).parent
    previous=json.loads((ROOT/K['previous_curation']).read_text())
    need(now['artifacts']==C['inventory'](base),'Complete actual500-object CODE artifact inventory')
    need(C['audit'](base,now,m)==now['results'] and len(now['results'])==250,'Every current origin/curated CODE projection')
    indexed={(r['unit'],r['mode']):r for r in now['results']}
    need(len(previous['results'])==248 and all(indexed[(r['unit'],r['mode'])]==r for r in previous['results']),'All previous248 results unchanged')
    need(len(previous['artifacts'])==1489 and all(now['artifacts'][p]==h for p,h in previous['artifacts'].items()),'All previous1489 artifact records unchanged')
    parent=json.loads((ROOT/K['parent_component']/'measurement.json').read_text());exceptions=[]
    for key,pin in parent['inputs'].items():
        p=expand(key,llvm)
        if p==ROOT/'src/source-manifest.json':
            need(pin==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'Only exact158-to159 manifest input exception');exceptions.append(key)
        else:need(p.is_file() and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'Every other accepted-parent input unchanged')
    need(len(exceptions)==1,'Exactly one explicitly proved parent-manifest extension')
    for mode in ['c','cpp']:need(sha(ROOT/K['parent_component']/mode/K['parent_object'])==K['parent_sha256'],'Exact unchanged source-proven parent component')
    code={}
    for mode in ['c','cpp']:
        code[mode]={}
        for variant in ['origin','curated']:
            candidate=lib('experiments/tsl9-safe-gap-functions/build-v1.py')['audit_object'](base/'safe-gap-functions'/mode/variant/'unit.o')
            need(candidate['passed'] and candidate['code_bytes']==764 and candidate['original_instructions']==288,'Every original candidate instruction in both origin/curated C/C++ objects')
            code[mode][variant]=dict(safe_gaps=candidate)
    data={}
    for u in m['native_data_units']:
        V=lib(u['verifier']);receipt=ROOT/u['formal_receipts'][0];saved=json.loads(receipt.read_text());folder=receipt.parent
        need(saved['variants']==['origin','curated'] and saved['inputs']==V['portable'](V['inputs'](llvm,saved['variants']),llvm),'Every actual independent DATA input unchanged')
        modes={}
        for mode in ['c','cpp']:
            modes[mode]={}
            for variant in ['origin','curated']:
                f=folder/mode/variant;job=saved['modes'][mode][variant]
                need(V['inventory'](f)==job['artifacts'],'Complete independent DATA output inventory')
                fact=V['audit_object'](f/'unit.o');need(fact==job['result'],'Every actual original/curated DATA object')
                need(V['portable'](V['dependencies'](f,variant,llvm),llvm)==job['dependencies'],'Every actual DATA include dependency')
                comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](f/'unit.o')
                modes[mode][variant]=dict(result=fact,independent_readers=comparison)
            need(V['complete_projection_equal'](folder/mode/'origin/unit.o',folder/mode/'curated/unit.o'),'Complete independent DATA byte/symbol/reference projection')
        data[u['name']]=modes
    return dict(passed=True,source_C_H_files=159,CODE_units=125,independent_DATA_units=8,
                CODE_comparisons=250,CODE_objects=500,DATA_comparisons=16,DATA_objects=32,
                total_source_comparisons=266,total_source_objects=532,previous_results_retained=248,
                previous_artifact_records_retained=1489,new_CODE_bytes=764,new_original_instructions=288,new_DATA_bytes=0,
                code_extension=code,independent_DATA=data,source_curated=True,
                original_coordinate_link_performed=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
                target_executed=False,new_BIN=False,firmware_ready=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',type=Path,required=True);args=parser.parse_args();llvm=args.tool_dir.resolve()
    before=portable(inputs(llvm),llvm);result=proof(llvm);need(before==portable(inputs(llvm),llvm),'All source-proof inputs unchanged during verification')
    out=HERE/'build/source-proof-v1.json';need(not out.exists(),'Create-only aggregate source receipt')
    out.parent.mkdir(exist_ok=True);out.write_bytes(encoded(dict(inputs=before,result=result)))
    print(json.dumps({k:v for k,v in result.items() if k not in ['code_extension','independent_DATA']}))
if __name__=='__main__':main()
