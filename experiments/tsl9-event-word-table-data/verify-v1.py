"""Static counter/ROM-fill provenance and real readonly C/C++ DATA; no target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='input_counter_static_library')
def portable(v,llvm):
    if isinstance(v,dict):return {portable(k,llvm):portable(x,llvm)for k,x in v.items()}
    if isinstance(v,list):return [portable(x,llvm)for x in v]
    if isinstance(v,str):
        for p,t in [(llvm,'${LLVM_BIN}'),(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:v=v.replace(str(p),t).replace(p.as_posix(),t)
    return v
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def pinned(llvm):
    E=read(HERE/'inputs-v1.json')
    for p,h in E['pins'].items():need(sha(R/p)==h,'Frozen source/native/reference input '+p)
    for n,h in E['tools'].items():need(sha(llvm/n)==h,'Pinned actual local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==E['stdint_sha256'],'Pinned freestanding header');need(sha(HERE/'event_words.v1.c')==E['source_sha256'],'Exactly selected28-byte seven-word DATA source');return E


def contract(E):return lib(E['contract_checker'])['audit'](E)
def audit_data(path,E):
 EL=lib(E['APP_reader'])['ELF'];e=EL(path);alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(e.header[0]==1 and e.header[1]==243 and not e.program_headers and len(alloc)==1,'Nonloadable RV32 DATA-only ET_REL');s=alloc[0];name='tsl9_event_word_read_window_1aae8';need((s['name'],s['type'],s['flags'],s['size'],s['align'],s['address'])==('.rodata.'+name,1,2,28,4,0),'Exactly28 readonly original word bytes,not physical placement');owners=[s for s in e.symbols if s['size']];need(len(owners)==1 and owners[0]['name']==name and owners[0]['info']==17 and owners[0]['size']==28 and owners[0]['value']==0 and owners[0]['section']==s['index'],'One real GLOBAL OBJECT,not a full provider alias');fw=(R/E['firmware']).read_bytes();need(hashlib.sha256(fw).hexdigest()==E['pins'][E['firmware']]and e.data(s)==fw[0x1aae8-0x8000:0x1ab04-0x8000],'All28 native DATA bytes equal exact original window');need(not e.relocations and not any(s['name']and s['info']&15!=4 and s['section']in [0,0xfff1]for s in e.symbols),'No imports,relocations or ABS providers');ind=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent full DATA reader agreement');return dict(passed=True,object_sha256=sha(path),CODE_bytes=0,DATA_bytes=28,positive_OBJECTs=1,relocations=0,named_UND=0,ABS_providers=0,independent_readers=ind)

def compose(path,inputs,E):
    EL=lib(E['APP_reader'])['ELF'];F=lib('experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');a,d,u,r=F['facts'](inputs[0],EL);aa,dd,uu,rr=F['facts'](inputs[1],EL);need(not set(a)&set(aa)and not set(d)&set(dd)and not uu and not rr,'Distinct real DATA-only extension')
    need(F['facts'](path,EL)==({**a,**aa},{**d,**dd},u-set(dd),sorted(r+rr))and len(u)==6 and not set(dd)&u,'Every allocated input byte/global symbol/typed relocation retained;all six imports remain')
    e=EL(path);need(sum(s['size']for s in e.sections if s['flags']&6==6)==69412 and sum(s['size']for s in e.sections if s['flags']&2 and not s['flags']&4)==4126,'Exact69412 CODE and4126 DATA;no padding');ind=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent complete APP-plus-DATA object readers agree');return dict(passed=True,object_sha256=sha(path),CODE_bytes=69412,DATA_bytes=4126,allocated_bytes=73538,relocations=len(e.relocations),APP_source_provider_UND=6,all_input_allocated_bytes_global_symbols_and_typed_relocations_retained=True,independent_readers=ind,original_address_link_performed=False,source_curated=False)
def run(llvm,trial=None,record_replay=False):
    E=pinned(llvm);proof=contract(E);out=HERE/'build'/(trial if trial else'native-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only experimental native folder')
    native={};composition={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        f=out/mode;parent=R/E['APP_component'].replace('/c/','/'+mode+'/');need(sha(parent)==E['APP_component_sha256'],'Current real163-source APP component retained')
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'clang.exe'),'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-fdata-sections','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',str(HERE/'event_words.v1.c'),'-o',str(f/'unit.o')];p=subprocess.run(argv,cwd=R,capture_output=True,timeout=120);(f/'compile.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual DATA compile succeeded;log retained')
        native[mode]=audit_data(f/'unit.o',E)
        if trial:
            p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent),str(f/'unit.o'),'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial composition completed;log retained')
        composition[mode]=compose(f/'candidate.o',[parent,f/'unit.o'],E)
    need(native['c']==native['cpp']and composition['c']==composition['cpp'],'Actual C11/C++17 DATA and complete partial compositions identical');pinned(llvm)
    v=dict(schema='TSL9-conditional-event-word-table-DATA-native-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),state_contract=proof,native=native,composition=composition,new_experimental_DATA_bytes=28,new_CODE_bytes=0,formal_source_C_H_files_unchanged=163,formal_APP_covered_bytes_unchanged=73510,formal_APP_byte_coverage_unchanged=95.72,APP_source_provider_UND_unchanged=6,source_curated=False,original_address_link_performed=False,provider_resolved=False,withheld_payload_or_individual_hash_output=False,installed_ROM_RAM_IRQ_Flash_OTA_proved=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    dest=HERE/'verification-v1.json'
    if trial or record_replay:need(not dest.exists(),'Create-only native/state proof receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    else:need(v==read(dest),'Fresh specific static/native replay equals successful receipt')
    return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');p.add_argument('--record-replay',action='store_true');a=p.parse_args()
    try:
        v=run(a.tool_dir.resolve(),a.trial,a.record_replay);print(json.dumps(dict(passed=True,APP_reference_bytes=388,SDK_reference_bytes=0,new_experimental_DATA_bytes=28,APP_partial_CODE=69412,APP_partial_DATA=4126,APP_source_provider_UND=6,formal_APP_byte_coverage=95.72,provider_resolved=False,new_BIN=False)))
    except Exception as error:print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=portable(str(error),a.tool_dir.resolve()))));raise SystemExit(1)
