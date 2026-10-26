"""Compile numeric trap requirements only;never execute a target,HOST model or ISA."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(p),run_name='offline_trap_library')
def portable(v,llvm,refs):
    if isinstance(v,dict):return {portable(k,llvm,refs):portable(w,llvm,refs)for k,w in v.items()}
    if isinstance(v,list):return [portable(w,llvm,refs)for w in v]
    if isinstance(v,str):
        for p,token in [(llvm,'${LLVM_BIN}'),(refs,'${REFERENCE_ROOT}'),(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:v=v.replace(str(p),token).replace(p.as_posix(),token)
    return v
def object_facts(path):
    E=lib(ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py')['ELF'](path)
    need(E.header[0]==1 and E.header[1]==243 and not E.program_headers,'Actual nonloadable RV32 ET_REL')
    allocated=[s for s in E.sections if s['flags']&2 and s['size']];external=[s for s in E.symbols if s['info']>>4]
    need(not allocated and not E.relocations and not external,'Compile-only constraints emit zero nonempty allocated sections,relocations,providers and imports')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,object_sha256=sha(path),allocated_bytes=0,CODE_bytes=0,DATA_bytes=0,relocations=0,external_symbols=0,independent_readers=independent)
def pins(llvm,refs):
    s=load(HERE/'spec-v1.json')
    for name in ['source','derive','evidence','source_provenance']:
        p=s['source']if name=='source'else {'derive':'derive-v1.py','evidence':'evidence-v1.json','source_provenance':'source-provenance.json'}[name]
        need(sha(HERE/p)==s[name+'_sha256'],'Pinned authored '+name)
    for name,h in s['tools'].items():need(sha(llvm/name)==h,'Pinned LLVM '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==s['stdint_sha256'],'Pinned stdint resource')
    d=lib(HERE/'derive-v1.py');e=d['inspect'](refs);need(e==load(HERE/'evidence-v1.json')and d['source'](e)==(HERE/s['source']).read_text(),'Fresh original/primary derivation matches evidence and C source')
    return s,e
def inputs(llvm,refs):
    s=load(HERE/'spec-v1.json');paths={HERE/'spec-v1.json',HERE/'derive-v1.py',HERE/'source-provenance.json',HERE/'evidence-v1.json',HERE/s['source'],HERE/'build-v1.py',llvm.parent/'lib/clang/18/include/stdint.h'}
    paths.update(ROOT/p for p in s['inputs']);paths.update(llvm/n for n in s['tools'])
    for row in load(HERE/'source-provenance.json')['references']:paths.update([refs/row['relative_path'],refs/row['manifest_relative_path']])
    return portable({str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)},llvm,refs)
def inventory(folder):return {p.name:sha(p)for p in sorted(folder.iterdir())if p.is_file()}
def dependencies(folder,llvm,refs):
    parser=ROOT/'scripts/verify-curated-source.py';need(sha(parser)=='1b07fcc89584794389b87c1721e9669285cd5948f9cfbe8be979cf071e7b3832','Frozen actual compiler dependency parser')
    return portable(lib(parser)['dependencies'](folder,'origin',llvm.parent/'lib/clang/18'),llvm,refs)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--reference-root',required=True,type=Path);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args();llvm=a.tool_dir.resolve();refs=a.reference_root.resolve();s,e=pins(llvm,refs);before=inputs(llvm,refs)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained compile trial');record=load(out/'measurement.json');need(record['inputs']==before,'Every actual input identity retained')
        for mode in ['c','cpp']:
            f=out/mode;need(record['modes'][mode]['artifacts']==inventory(f)and record['modes'][mode]['dependencies']==dependencies(f,llvm,refs)and record['modes'][mode]['result']==object_facts(f/'unit.o'),'Fresh complete actual native receipt matches')
        print(json.dumps(dict(passed=True,replayed=True,allocated_bytes=0,new_CODE_bytes=0)));return
    need(Path(a.trial).name==a.trial,'One fresh trial name');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only native trial');out.mkdir(parents=True);record=dict(schema='TSL9-trap-profile-native-v1',inputs=before,modes={},target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False)
    for mode in ['c','cpp']:
        f=out/mode;f.mkdir();argv=[str(llvm/'clang.exe')]+s['flags'][mode]+['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(HERE/s['source']),'-o',str(f/'unit.o')];v=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/'compile.log').write_text(portable((v.stdout+v.stderr).decode('utf-8','replace'),llvm,refs),encoding='utf-8');need(v.returncode==0,'Native compile failed;trial retained')
        record['modes'][mode]=dict(argv=portable(argv,llvm,refs),exit=v.returncode,result=object_facts(f/'unit.o'),dependencies=dependencies(f,llvm,refs),artifacts=inventory(f))
    need(record['modes']['c']['result']==record['modes']['cpp']['result'],'Actual C11/C++17 constraint objects identical');need(inputs(llvm,refs)==before,'Actual inputs unchanged through compile');(out/'measurement.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,allocated_bytes=0,CODE_bytes=0,DATA_bytes=0,object_sha256=record['modes']['c']['result']['object_sha256'],new_BIN=False)))
if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
