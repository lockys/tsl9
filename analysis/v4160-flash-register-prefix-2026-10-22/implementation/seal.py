"""Create-only metadata/seal. Build archives are not publication members."""
import argparse,hashlib,json
from pathlib import Path
import check as C
H=Path(__file__).resolve().parent;MODEL=C.MODEL
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def create(p,data):
    if p.exists():C.need(p.read_bytes()==data,'immutable existing evidence '+str(p))
    else:p.write_bytes(data)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();N=C.load('prefix_native_seal',H/'verify_native.py');B=C.load('prefix_host_seal',root/MODEL/'verify_host.py');(H/'receipts').mkdir(exist_ok=True);results=[]
    for kind,base,runner in [('host','host-final',B),('native','native-final',N)]:
        for mode in ('c','cpp'):
            actual=root/MODEL/'build'/base/mode/'verification.json';runner.replay(root,actual);metadata='receipts/'+kind+'-'+mode+'.json';create(H/metadata,actual.read_bytes());r=C.read(actual)
            row=dict(kind=kind,mode=mode,receipt=str(actual),sha256=sha(actual),metadata=metadata,artifact_dir=actual.parent.relative_to(root).as_posix())
            if kind=='host':row.update(tests=r['tests'],actual_compiled_controls=6)
            else:row.update(functions=r['checks']['functions'],ELF_sha256=sha(actual.parent/'COMPONENT-ONLY-NOT-FIRMWARE.elf'),allocated_function_bytes=262,instructions=99,raw_machine_controls=99,actual_compiled_controls=3)
            results.append(row)
    create(H/'source-diff.json',encoded(C.source_diff(root)))
    option_base=root/MODEL/'build/cli-options';option=option_base/'verification.json';report=C.read(option);C.need(report['passed'] and report['runner_sha256']==sha(H/'verify_native.py') and report['script_sha256']==sha(H/'test_cli_options.py'),'final option regression identities');N.replay(root,root/MODEL/'build/cli-alternate/c/verification.json',root/MODEL/'build/alternate-ID2966.reference');create(H/'receipts/cli-options.json',option.read_bytes())
    option_row=dict(receipt=str(option),sha256=sha(option),metadata='receipts/cli-options.json',artifact_dir=option_base.relative_to(root).as_posix())
    create(H/'results.json',encoded(dict(schema='ID2966-flash-register-prefix-index-v1',results=results,CLI_options=option_row,total_native_bytes=262,instructions=99,five_leaf_bytes=198,five_leaves_byte_identical=True,quarter_save_order_original=False,full_scratch_GPR_prefix_equivalence=False,pointwise_async_equivalence=False,full_image_integration=False,firmware_BIN_produced=False,target_execution=False,hardware=False,OTA_ready=False)))
    names=['verify_native.py','verify_native.sh','prefix_gate.py','test_cli_options.py','check.py','seal.py','README.md','readme.en.md','readme.zh-TW.md','source-diff.json','results.json',*[p.relative_to(H).as_posix() for p in sorted((H/'receipts').glob('*.json'))]]
    files=[H/n for n in names];model=[p for p in(root/MODEL).rglob('*') if p.is_file() and 'build' not in p.relative_to(root/MODEL).parts]
    for p in files+model:C.need(b'\r' not in p.read_bytes(),'new text uses LF '+str(p))
    def record(p,n):return dict(path=n,bytes=p.stat().st_size,sha256=sha(p))
    reviews=[]
    for name in ('ABI-review','source-review'):
        path=H.parent/name/'seal.json';C.need(path.is_file(),'independent review must close before implementation seal '+name)
        for row in C.members(C.read(path)):C.need(sha(path.parent/row['path'])==row['sha256'],'independent immutable member '+name+'/'+row['path'])
        reviews.append(record(path,'../'+name+'/seal.json'))
    data=dict(schema='ID2966-flash-register-prefix-implementation-seal-v1',passed=True,members=[record(p,p.relative_to(H).as_posix()) for p in files],model_members=[record(p,p.relative_to(root).as_posix()) for p in sorted(model)],independent_review_seals=reviews,selected_receipts=4,five_leaf_original_bytes=True,total_native_bytes=262,full_image_integration=False,firmware_BIN_produced=False,target_execution=False,hardware=False,OTA_ready=False)
    create(H/'seal.json',encoded(data));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(files),model_members=len(model))))
if __name__=='__main__':main()
