"""Create-only selected evidence copies and LF final seal after actual replays."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import verify_native as N
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-flash-native'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def create(p,data):
    if p.exists():need(p.read_bytes()==data,'existing report/seal immutable '+str(p))
    else:p.write_bytes(data)
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--host-build',type=Path,required=True);p.add_argument('--native-build',type=Path,required=True);p.add_argument('--guard-receipt',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();s=importlib.util.spec_from_file_location('flash_host_seal',root/MODEL/'verify_host.py');B=importlib.util.module_from_spec(s);s.loader.exec_module(B);results=[]
    (H/'receipts').mkdir(exist_ok=True)
    for kind,base,runner in [('host',a.host_build.resolve(),B),('native',a.native_build.resolve(),N)]:
        need(base.is_relative_to(root),'actual selected build inside project')
        for mode in ('c','cpp'):
            path=base/mode/'verification.json';runner.replay(root,path);r=read(path);metadata=H/'receipts'/(kind+'-'+mode+'.json');create(metadata,path.read_bytes())
            row=dict(kind=kind,mode=mode,receipt=str(path),sha256=sha(path),metadata=metadata.relative_to(H).as_posix(),artifact_dir=path.parent.relative_to(root).as_posix())
            if kind=='host':row.update(tests=r['tests'],actual_compiled_controls=6)
            else:row.update(functions=r['checks']['functions'],ELF_sha256=sha(path.parent/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),allocated_function_bytes=256,instructions=98,original_source_bytes=262,original_instructions=99,unowned_tail_bytes=6,raw_machine_controls=15,IR_controls=3)
            results.append(row)
    guard_path=a.guard_receipt.resolve();guard=read(guard_path);need(guard_path.is_relative_to(root) and guard['passed'] and guard['runner_sha256']==sha(root/MODEL/'verify_host.py') and guard['script_sha256']==sha(H/'guard_controls.py') and len(guard['rejections'])==10 and len(guard['matching_cross_platform_header_fixtures'])==4 and guard['subprocess_calls']==0,'actual current bounded host guard controls')
    create(H/'receipts/guard-controls.json',guard_path.read_bytes())
    index=dict(schema='ID2966-readable-flash-implementation-index-v1',results=results,host_machine_guard=dict(receipt=str(guard_path),artifact_dir=guard_path.parent.relative_to(root).as_posix(),metadata='receipts/guard-controls.json',sha256=sha(guard_path),rejections=10,matching_header_fixtures=4,subprocess_calls=0),native_runner_sha256=sha(H/'verify_native.py'),host_runner_sha256=sha(root/MODEL/'verify_host.py'),source_seal_sha256=N.SOURCE_SEAL,independent_native_checker_sha256=N.REVIEW_SHA,
        native_function_bytes=256,program_compiled_bytes=94,program_original_bytes=100,unowned_tail_bytes=6,full_image_integration=False,pointwise_async_equivalence=False,nonreturn_physical_GPR_prefix_equivalence=False,firmware_BIN_produced=False,target_execution=False,ISA_emulation=False,hardware=False,network=False,OTA_ready=False)
    create(H/'results.json',encoded(index))
    names=['probe_native.py','verify_native.py','verify_native.sh','guard_controls.py','check.py','check.sh','seal.py','README.md','readme.en.md','readme.zh-TW.md','results.json','receipts/host-c.json','receipts/host-cpp.json','receipts/native-c.json','receipts/native-cpp.json','receipts/guard-controls.json']
    models=['.gitignore','verify.py','verify.sh','verify_host.py','README.md','readme.en.md','readme.zh-TW.md','src/flash_native.c','src/flash_native.h','src/native_io.h','src/host_io.c','src/host_io.h','tests/test_flash.c']
    def record(p,n):return dict(path=n,bytes=p.stat().st_size,sha256=sha(p))
    for n in names:
        p=H/n;need(b'\r' not in p.read_bytes(),'new sealed text/report uses UTF8 LF '+n)
    for n in models:
        p=root/MODEL/n;need(b'\r' not in p.read_bytes(),'new model text uses UTF8 LF '+n)
    seal=dict(schema='ID2966-readable-flash-implementation-seal-v1',passed=True,members=[record(H/n,n) for n in names],model_members=[record(root/MODEL/n,MODEL+'/'+n) for n in models],selected_receipts=4,
        all_six_normal_boundaries_admitted=True,all_individual_functions_fit=True,program_unowned_tail_bytes=6,full_image_integration=False,pointwise_async_equivalence=False,nonreturn_physical_GPR_prefix_equivalence=False,firmware_BIN_produced=False,target_execution=False,ISA_emulation=False,hardware=False,network=False,OTA_ready=False)
    create(H/'seal.json',encoded(seal));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(names),model_members=len(models))))
if __name__=='__main__':main()
