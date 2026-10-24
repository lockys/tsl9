"""Compile selected saved-SDK RF declarations into layout data; never execute them."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes())
HEADER_SHA='fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e'
FIELDS=['LLEMode','Channel','Frequency','accessAddress','CRCInit','rfStatusCB','ChannelMap','Resv','HeartPeriod','HopPeriod','HopIndex','RxMaxlen','TxMaxlen']
EXPECTED=[32,4,4,0,1,4,8,12,16,20,24,25,26,27,28,29]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(header):
    lines=header.read_bytes().decode('utf8','replace').splitlines()
    text='#include <stdint.h>\n#ifdef __cplusplus\n#define DATA extern "C" const\n#define ALIGN_OF(T) alignof(T)\n#else\n#define DATA const\n#define ALIGN_OF(T) _Alignof(T)\n#endif\n'
    text+=lines[2680]+'\n'+'\n'.join(lines[2685:2708])+'\n'
    expr=['sizeof(rfConfig_t)','ALIGN_OF(rfConfig_t)','sizeof(pfnRFStatusCB_t)']+['__builtin_offsetof(rfConfig_t,'+f+')'for f in FIELDS]
    return (text+'DATA uint32_t tsl9_rf_profile_layout[] __attribute__((used)) = {\n'+',\n'.join('    '+x for x in expr)+'\n};\n').encode()
def audit(path):
    e=runpy.run_path(str(ROOT/S['reader']))['ELF'](path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Data-only RV32 ET_REL')
    symbols=[x for x in e.symbols if x['info']>>4]
    need(len(symbols)==1,'One actual layout data owner')
    f=symbols[0];sec=e.sections[f['section']]
    need(f['name']=='tsl9_rf_profile_layout'and f['info']==17 and f['value']==0 and f['size']==64,'Real64B object')
    need(sec['flags']==2 and sec['type']==1 and sec['size']==64,'Read-only layout data')
    need(not e.relocations and not any(x['info']&15==2 for x in e.symbols),'No code orreferences')
    need({x['index']for x in e.sections if x['flags']&2 and x['size']}=={sec['index']},'Every allocated byte islayout data')
    raw=e.data(sec);values=[int.from_bytes(raw[n:n+4],'little')for n in range(0,64,4)]
    need(values==EXPECTED,'Actual compiled default ILP32 RF layout')
    return dict(passed=True,values=dict(zip(['size','alignment','callback_pointer_bytes']+FIELDS,values)),object_sha256=sha(path),allocated_data_bytes=64,FUNC=0,RELA=0,UND=0,target_executed=False,installed_ABI_proved=False)
def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--header',type=Path,required=True);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();header=a.header.resolve();llvm=a.tool_dir.resolve();src=HERE/'src/sdk_rf_layout.v1.c'
    need(sha(header)==HEADER_SHA,'Saved SDK header identity')
    need(not re.search(rb'#\s*pragma\s+pack',header.read_bytes()),'No unmodelled header packing pragma')
    need(src.read_bytes()==source(header),'Exact selected SDK declaration extraction withLF normalization')
    for path,pin in [(ROOT/S['reader'],S['reader_sha256']),(llvm/'clang.exe',S['tools']['clang.exe']),(llvm.parent/'lib/clang/18/include/stdint.h',S['stdint_sha256'])]:need(sha(path)==pin,'Pinned parser/compiler/header')
    def key(path):
        if path==header:return '$'+'{SAVED_SDK_HEADER}'
        for base,token in [(ROOT,'PROJECT_ROOT'),(llvm,'LLVM_BIN'),(llvm.parent/'lib/clang/18','CLANG_RESOURCE')]:
            if path.is_relative_to(base):return '$'+'{'+token+'}/'+path.relative_to(base).as_posix()
        raise ValueError('Unexpected layout input location')
    paths=[Path(__file__),HERE/'spec-v1.json',src,header,ROOT/S['reader'],llvm/'clang.exe',llvm.parent/'lib/clang/18/include/stdint.h']
    inputs={key(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in paths}
    out=(a.replay or a.output).resolve()
    need(out.parent==HERE/'build','Owned layout output')
    if a.replay:
        report=json.loads((out/'measurement.json').read_bytes())
        need(report['inputs']==inputs,'Every recorded SDK layout input unchanged')
        for mode in ['c','cpp']:
            need(report['modes'][mode]['result']==audit(out/mode/'layout.o')and
                 report['modes'][mode]['artifacts']==inventory(out/mode),'Actual retained layout data andinventory')
        print(json.dumps(dict(passed=True,languages=['c','cpp'],compiled_profile_only=True,installed_ABI_proved=False,target_executed=False)));return
    need(not out.exists(),'Create-only layout output')
    report=dict(schema='TSL9-saved-SDK-RF-layout-data-only-v1',inputs=inputs,modes={},compiled_profile_only=True,installed_ABI_proved=False,target_executed=False,network=False)
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'clang.exe')]+S['flags'][mode]+['-c',str(src),'-o',str(folder/'layout.o')]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120)
        (folder/'compile.log').write_bytes(result.stdout+result.stderr)
        need(result.returncode==0,'Actual SDK layout compilation failed;local log retained')
        facts=audit(folder/'layout.o');report['modes'][mode]=dict(result=facts,artifacts=inventory(folder))
    need(src.read_bytes()==source(header)and sha(header)==HEADER_SHA,'SDK layout sources unchanged')
    (out/'measurement.json').write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,values=report['modes']['c']['result']['values'],languages=['c','cpp'],allocated_data_bytes_per_object=64,FUNC=0,target_executed=False,installed_ABI_proved=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,subprocess.SubprocessError)as error:
        print(json.dumps(dict(passed=False,error_label=str(error)if isinstance(error,ValueError)else'Local SDK layout failure;values withheld')));raise SystemExit(1)
