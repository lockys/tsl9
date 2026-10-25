"""Full 156-file source proof, retaining prior CODE/DATA evidence unchanged."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'source-proof-v2.json').read_text())
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
def audit_leaves(path):
    spec=json.loads((ROOT/'experiments/tsl9-central-callback-leaves/spec-v1.json').read_text())
    e=E(path);fw=(ROOT/spec['firmware']).read_bytes()
    need(sha(ROOT/spec['firmware'])==spec['firmware_sha256'],'Original leaf image identity')
    rows=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in rows}
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RV32 leaf object')
    need(len(gm)==len(rows) and set(gm)=={r['name'] for r in spec['regions']},'Exactly eleven genuine leaf CODE owners')
    need(not any(s['name'] and not s['section'] for s in e.symbols),'No leaf dependency or substitute')
    owned=set();expected=[];count=0
    for r in spec['regions']:
        f=gm[r['name']];sec=e.sections[f['section']]
        need((f['info'],f['other'],f['value'],f['size'])==(18,0,0,r['bytes']),'Actual complete leaf basic block')
        need((sec['name'],sec['type'],sec['flags'],sec['size'])==('.text.'+r['name'],1,6,r['bytes']),'Exact positive executable allocation')
        owned.add(sec['index']);actual=bytearray(e.data(sec));original=fw[r['start']-0x8000:r['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==r['original_sha256'],'Every original leaf span')
        for edge in [x for x in spec['controls'] if x['owner']==r['name']]:
            off,kind=edge['offset'],edge['type'];width,mask=B['MASKS'][kind]
            a=int.from_bytes(actual[off:off+width],'little');b=int.from_bytes(original[off:off+width],'little')
            need(a&mask==b&mask and a&(~mask&((1<<(8*width))-1))==0,'Exact original branch opcode/registers and zero native displacement')
            need(B['decode_control'](original[off:off+width],edge['PC'])==(kind,edge['target_PC']),'Independent original control target')
            actual[off:off+width]=(a|B['immediate'](kind,edge['target_PC']-edge['PC'])).to_bytes(width,'little')
            expected.append((sec['index'],off,kind,0,edge['target']))
        need(bytes(actual)==original,'Every original leaf instruction after original-PC control resolution')
        at=0
        while at<len(actual):at+=4 if actual[at]&3==3 else 2;count+=1
        need(at==len(actual),'Whole native leaf instructions')
    actual=[(r['section'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name']) for r in e.relocations]
    need(sorted(actual)==sorted(expected) and len(actual)==5 and count==41,'All five typed controls and41 original instructions')
    need({s['index'] for s in e.sections if s['flags']&2 and s['size']}==owned and sum(r['bytes'] for r in spec['regions'])==118,'Every allocated leaf byte owned')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,CODE_bytes=118,instructions=41,FUNC=11,RELA=5,independent_readers=comparison,object_sha256=sha(path))
def inputs(llvm):
    files={Path(__file__),HERE/'source-proof-v2.json',ROOT/'src/source-manifest.json'}
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
    ext=json.loads((HERE/'source-extension-v2.json').read_text());raw=lib('experiments/tsl9-central-callback-tables/parent-manifest-v2.py')['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==ext['previous_manifest_sha256'],'Exact retained153-file parent manifest')
    previous_manifest=json.loads(raw);expected=json.loads(raw)
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:expected[group]+=ext[key]
    need(sha(ROOT/'src/source-manifest.json')==ext['new_manifest_sha256'] and expected==json.loads((ROOT/'src/source-manifest.json').read_text()),'Only three source files,two CODE units and one DATA unit appended')
    C=lib('scripts/verify-curated-source.py');m=C['metadata']()
    need((len(m['files']),len(m['native_units']),len(m['native_data_units']))==(156,123,7),'Complete156-file123-CODE/seven-DATA scope')
    now=json.loads((ROOT/K['curation']).read_text());base=(ROOT/K['curation']).parent
    previous=json.loads((ROOT/K['previous_curation']).read_text())
    need(now['artifacts']==C['inventory'](base),'Complete actual492-object CODE artifact inventory')
    need(C['audit'](base,now,m)==now['results'] and len(now['results'])==246,'Every current origin/curated CODE projection')
    indexed={(r['unit'],r['mode']):r for r in now['results']}
    need(len(previous['results'])==242 and all(indexed[(r['unit'],r['mode'])]==r for r in previous['results']),'All previous242 results unchanged')
    need(len(previous['artifacts'])==1453 and all(now['artifacts'][p]==h for p,h in previous['artifacts'].items()),'All previous1453 artifact records unchanged')
    parent=json.loads((ROOT/K['parent_component']/'measurement.json').read_text());exceptions=[]
    for key,pin in parent['inputs'].items():
        p=expand(key,llvm)
        if p==ROOT/'src/source-manifest.json':
            need(pin==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'Only exact153-to156 manifest input exception');exceptions.append(key)
        else:need(p.is_file() and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'Every other accepted-parent input unchanged')
    need(len(exceptions)==1,'Exactly one explicitly proved parent-manifest extension')
    for mode in ['c','cpp']:need(sha(ROOT/K['parent_component']/mode/K['parent_object'])==K['parent_sha256'],'Exact unchanged source-proven parent component')
    code={}
    for mode in ['c','cpp']:
        code[mode]={}
        for variant in ['origin','curated']:
            leaf=audit_leaves(base/'central-callback-leaves'/mode/variant/'unit.o')
            event=lib('experiments/tsl9-central-event-callbacks/build-v1.py')['audit_object'](base/'central-event-callbacks'/mode/variant/'unit.o')
            need(event['passed'] and event['code_bytes']==1938 and event['original_instructions']==645,'Every original event/helper instruction in current curated CODE build')
            code[mode][variant]=dict(leaves=leaf,event=event)
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
    return dict(passed=True,source_C_H_files=156,CODE_units=123,independent_DATA_units=7,
                CODE_comparisons=246,CODE_objects=492,DATA_comparisons=14,DATA_objects=28,
                total_source_comparisons=260,total_source_objects=520,previous_results_retained=242,
                previous_artifact_records_retained=1453,new_CODE_bytes=2056,new_original_instructions=686,new_DATA_bytes=92,
                code_extension=code,independent_DATA=data,source_curated=True,
                original_coordinate_link_performed=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
                target_executed=False,new_BIN=False,firmware_ready=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',type=Path,required=True);args=parser.parse_args();llvm=args.tool_dir.resolve()
    before=portable(inputs(llvm),llvm);result=proof(llvm);need(before==portable(inputs(llvm),llvm),'All source-proof inputs unchanged during verification')
    out=HERE/'build/source-proof-v2.json';need(not out.exists(),'Create-only aggregate source receipt')
    out.parent.mkdir(exist_ok=True);out.write_bytes(encoded(dict(inputs=before,result=result)))
    print(json.dumps({k:v for k,v in result.items() if k not in ['code_extension','independent_DATA']}))
if __name__=='__main__':main()
