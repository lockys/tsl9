"""Compile only primary task-handler ABI assertions; emit no allocated target bytes."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];E=json.loads((HERE/'evidence-v1.json').read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='task_handler_ABI_library')
N=lib(E['prior_study']+'/build-v1.py')
def inputs(llvm):
    N['inputs'](llvm);need(sha(ROOT/E['primary_header'])==E['primary_header_sha256'],'Exact saved primary header')
    paths=[Path(__file__),HERE/'evidence-v1.json',HERE/'task_handler_abi.c',ROOT/E['primary_header'],llvm/'clang.exe',llvm.parent/'lib/clang/18/include/stdint.h']
    return N['portable']({str(p):sha(p)for p in paths},llvm)
def inventory(p):return{f.name:sha(f)for f in sorted(p.iterdir())if f.is_file()}
def deps(folder,llvm):
    text=(folder/'unit.d').read_text('utf-8').replace('\\\n',' ');target,sep,tail=text.partition(':');need(sep and target=='unit.o','Actual ABI compiler dependency target')
    paths={Path(re.sub(r'\\(.)',r'\1',s)).resolve()for s in re.findall(r'(?:\\.|[^\s])+',tail)}
    allowed={(HERE/'task_handler_abi.c').resolve(),(ROOT/E['primary_header']).resolve()};resource=(llvm.parent/'lib/clang/18').resolve()
    need(allowed<=paths and all(p in allowed or p.is_relative_to(resource)for p in paths),'Only actual ABI source, primary header and compiler resources')
    return N['portable']({str(p):sha(p)for p in sorted(paths)},llvm)
def inspect(path):
    rd='experiments/tsl9-resident-root-chain-callees/';EL=lib(rd+'elf_reader-v7.py')['ELF'];e=EL(path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable RV32 ABI object')
    need(not any(s['flags']&2 and s['size']for s in e.sections)and not e.relocations,'No allocated CODE/DATA and no relocations')
    need(not any(s['info']>>4 for s in e.symbols),'No global function,object,absolute or undefined provider')
    independent=lib(rd+'compare-readers-v3.py')['audit'](path);need(independent['passed'],'Independent ABI object readers')
    return dict(passed=True,object_sha256=sha(path),allocated_bytes=0,functions=0,relocations=0,
        primary_handler_type='uint16_t (*)(uint8_t, uint16_t)',RV32_pointer_bytes=4,task_ID_bytes=1,event_and_result_bytes=2,
        source_and_header_compiler_checked=True,independent_readers=independent,
        installed_private_ABI_or_hardware_proved=False,target_executed=False,network=False)
def replay(llvm):
    f=HERE/'build/abi-v1';v=json.loads((f/'measurement.json').read_bytes());need(v['inputs']==inputs(llvm),'Actual ABI compile inputs retained');out={}
    for mode in ['c','cpp']:
        p=f/mode;row=v['modes'][mode];need(row['artifacts']==inventory(p)and row['dependencies']==deps(p,llvm),'Actual ABI artifacts and include closure retained')
        out[mode]=inspect(p/'unit.o');need(out[mode]==row['result'],'Fresh actual ABI result')
    need(out['c']==out['cpp'],'Both real C/C++ primary ABI assertion objects equal');return out
def build(llvm):
    f=HERE/'build/abi-v1';need(not f.exists(),'Create-only ABI build');before=inputs(llvm);v=dict(inputs=before,modes={})
    for mode in ['c','cpp']:
        p=f/mode;p.mkdir(parents=True);argv=[str(llvm/'clang.exe'),*N['flags'](mode),'-MD','-MF',str(p/'unit.d'),'-MT','unit.o','-c',str(HERE/'task_handler_abi.c'),'-o',str(p/'unit.o')]
        proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(p/'compile.log').write_text(N['portable']((proc.stdout+proc.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(proc.returncode==0,'Actual primary ABI compile; log retained')
        v['modes'][mode]=dict(command=N['portable'](argv,llvm),exit=0,result=inspect(p/'unit.o'),dependencies=deps(p,llvm),artifacts=inventory(p))
    need(inputs(llvm)==before and v['modes']['c']['result']==v['modes']['cpp']['result'],'Stable inputs and equal actual ABI objects')
    (f/'measurement.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');return replay(llvm)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--build',action='store_true');a=p.parse_args()
    try:
        v=build(a.tool_dir.resolve())if a.build else replay(a.tool_dir.resolve());print(json.dumps(dict(passed=True,primary_type=v['c']['primary_handler_type'],allocated_bytes=0,object_sha256=v['c']['object_sha256'],new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
