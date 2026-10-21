"""Read-only sealed metadata and available actual host/native artifact closure."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=read(H/'seal.json')
    for r in seal['members']:
        path=(H/r['path']).resolve();need(path.is_relative_to(H.resolve()) and path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed implementation member '+r['path'])
    for r in seal['model_members']:
        path=root/r['path'];need(path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed readable model/CLI '+r['path'])
    index=read(H/'results.json');need(len(index['results'])==4,'four selected actual native/host receipts');native=module('flash_native_readback',H/'verify_native.py');host=module('flash_host_readback',root/'experiments/tsl9-v4160-flash-native/verify_host.py');native.context(root);host.source_evidence(root)
    guard_row=index['host_machine_guard'];guard_metadata=H/guard_row['metadata'];guard=read(guard_metadata)
    need(sha(guard_metadata)==guard_row['sha256'] and guard['passed'] and guard['runner_sha256']==sha(root/'experiments/tsl9-v4160-flash-native/verify_host.py') and guard['script_sha256']==sha(H/'guard_controls.py'),'selected current guard identities')
    need(len(guard['rejections'])==10 and len(guard['matching_cross_platform_header_fixtures'])==4 and guard['subprocess_calls']==0 and all(r['rejected_before_subprocess'] and r['subprocess_calls']==0 for r in guard['rejections']),'bounded reject-before-launch evidence')
    actual_guard=root/guard_row['artifact_dir']/'verification.json'
    if actual_guard.is_file():need(sha(actual_guard)==guard_row['sha256'],'actual selected guard archive identity')
    replayed=[];missing=[]
    for row in index['results']:
        metadata=H/row['metadata'];need(sha(metadata)==row['sha256'],'byte-identical selected receipt metadata');r=read(metadata)
        need(r['passed'] is True and r['mode']==row['mode'],'selected actual language/result')
        if row['kind']=='native':need(r['runner_sha256']==sha(H/'verify_native.py') and r['checks']['allocated_function_bytes']==256 and r['checks']['unowned_original_program_tail_bytes']==6,'native current identity/actual fit and remaining gap')
        else:need(r['runner_sha256']==sha(root/'experiments/tsl9-v4160-flash-native/verify_host.py') and r['tests']==dict(passed=True,groups=5,cases=481,checks=247191,synthetic_provider=True,RV32_execution=False),'host exact current identity/coverage')
        for key in ('hardware','network','OTA_ready'):need(r[key] is False,'readiness boundary remains false')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():
            need(sha(actual)==row['sha256'],'actual selected archive matches metadata');(native if row['kind']=='native' else host).replay(root,actual);replayed.append(row['kind']+'-'+row['mode'])
        else:missing.append(row['kind']+'-'+row['mode'])
    need(not a.require_local_builds or not missing,'required historical local archives missing; run the fresh portable CLIs separately')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),selected_metadata=4,actual_archives_replayed=replayed,missing_local_archives=missing,fresh_compilation=False,native_function_bytes=256,native_instructions=98,program_original_bytes=100,program_compiled_bytes=94,full_image_integration=False,firmware_BIN_produced=False,target_execution=False,hardware=False,OTA_ready=False)))
if __name__=='__main__':main()
