"""Compile exact captured candidate data as C11/C++17; never execute target code."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];E=json.loads((HERE/'evidence-v1.json').read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='initial_data_native_library')
def portable(v,llvm):
    if isinstance(v,str):
        for p,t in [(llvm,'${LLVM_BIN}'),(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:v=v.replace(str(p),t).replace(p.as_posix(),t)
    elif isinstance(v,list):v=[portable(x,llvm)for x in v]
    elif isinstance(v,dict):v={portable(k,llvm):portable(x,llvm)for k,x in v.items()}
    return v
def inventory(p):return{f.name:sha(f)for f in sorted(p.iterdir())if f.is_file()}
def dependencies(folder,llvm):
    text=(folder/'unit.d').read_text('utf-8').replace('\\\n',' ');target,sep,tail=text.partition(':');need(sep and target=='unit.o','Actual compiler dependency target')
    paths={Path(re.sub(r'\\(.)',r'\1',s)).resolve()for s in re.findall(r'(?:\\.|[^\s])+',tail)}
    source=(HERE/'resident_initial_data.c').resolve();resource=(llvm.parent/'lib/clang/18').resolve()
    need(source in paths and all(p==source or p.is_relative_to(resource)for p in paths),'Only current C source and compiler resource headers')
    return portable({str(p):sha(p)for p in sorted(paths)},llvm)
def flags(mode):
    return['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-ffreestanding','-fno-builtin','-fno-stack-protector',
        '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-fdata-sections','-ffunction-sections','-Wall','-Wextra','-Werror',
        '-x','c'if mode=='c'else'c++','-std=c11'if mode=='c'else'-std=c++17']
def inputs(llvm):
    lib(E['parent_study']+'/build-v1.py')['pins'](llvm)
    need(all(sha(ROOT/p)==h for p,h in E['whole_reader_inputs'].items()),'Frozen native readers')
    paths=[Path(__file__),HERE/'evidence-v1.json',HERE/'resident_initial_data.c',ROOT/E['segment'],llvm/'clang.exe',llvm.parent/'lib/clang/18/include/stdint.h']
    return portable({str(p):sha(p)for p in paths},llvm)
def unit(path):
    EL=lib('experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py')['ELF'];e=EL(path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable RV32 ET_REL data only')
    sec=next(s for s in e.sections if s['name']==E['section']);raw=(ROOT/E['segment']).read_bytes()
    need(sec['flags']==2 and sec['type']==1 and sec['size']==136 and sec['align']==4 and e.data(sec)==raw,'Every actual initialized byte equals captured segment')
    need([s['index']for s in e.sections if s['flags']&2 and s['size']]==[sec['index']],'Exactly one readonly allocation')
    syms=[s for s in e.symbols if s['info']>>4];need(len(syms)==1,'One actual exported data object')
    s=syms[0];need((s['name'],s['info'],s['section'],s['value'],s['size'])==(E['symbol'],17,sec['index'],0,136),'Positive OBJECT with real bytes,not an absolute provider')
    need(not e.relocations and not any(s['info']&15==2 for s in e.symbols),'Zero relocations and zero functions')
    independent=lib('experiments/tsl9-resident-root-chain-callees/compare-readers-v3.py')['audit'](path);need(independent['passed'],'Two independent readers agree')
    return dict(passed=True,object_sha256=sha(path),DATA_bytes=136,CODE_bytes=0,positive_OBJECT_regions=1,functions=0,relocations=0,
        section=E['section'],symbol=E['symbol'],source_sha256=E['segment_sha256'],independent_readers=independent,
        numeric_pointer_words_are_data_not_function_providers=True,target_executed=False,hardware_accessed=False,network=False)
def replay(llvm):
    folder=HERE/'build/native-v1';saved=json.loads((folder/'measurement.json').read_bytes());need(saved['inputs']==inputs(llvm),'All actual compile inputs unchanged')
    result={}
    for mode in ['c','cpp']:
        p=folder/mode;row=saved['modes'][mode]
        need(row['artifacts']==inventory(p)and row['dependencies']==dependencies(p,llvm),'All native artifacts and include dependencies retained')
        result[mode]=unit(p/'unit.o');need(row['result']==result[mode],'Fresh actual data object result')
    need(result['c']==result['cpp'],'Actual C/C++ data objects identical');return result
def build(llvm):
    folder=HERE/'build/native-v1';need(not folder.exists(),'Create-only native data build');before=inputs(llvm);saved=dict(inputs=before,modes={})
    for mode in ['c','cpp']:
        p=folder/mode;p.mkdir(parents=True)
        argv=[str(llvm/'clang.exe'),*flags(mode),'-MD','-MF',str(p/'unit.d'),'-MT','unit.o','-c',str(HERE/'resident_initial_data.c'),'-o',str(p/'unit.o')]
        proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(p/'compile.log').write_text(portable((proc.stdout+proc.stderr).decode('utf-8','replace'),llvm),encoding='utf-8')
        need(proc.returncode==0,'Actual native data compile failed; log retained')
        saved['modes'][mode]=dict(command=portable(argv,llvm),exit=0,result=unit(p/'unit.o'),dependencies=dependencies(p,llvm),artifacts=inventory(p))
    need(inputs(llvm)==before and saved['modes']['c']['result']==saved['modes']['cpp']['result'],'Stable inputs and identical C/C++ objects')
    (folder/'measurement.json').write_text(json.dumps(saved,indent=2)+'\n',encoding='utf-8')
    return replay(llvm)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--build',action='store_true');a=p.parse_args()
    try:
        v=build(a.tool_dir.resolve())if a.build else replay(a.tool_dir.resolve());print(json.dumps(dict(passed=True,DATA_bytes=136,CODE_bytes=0,functions=0,identical_C_CPP=True,object_sha256=v['c']['object_sha256'],new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
