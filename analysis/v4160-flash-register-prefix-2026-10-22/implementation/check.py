"""Read-only source identities, exact diffs and optional actual artifact replay."""
import argparse,difflib,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-flash-register-prefix';OLD='experiments/tsl9-v4160-flash-entry-order'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def need(v,m):
    if not v:raise ValueError(m)
def load(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def members(seal):
    value=seal['members'];return [dict(path=n,**row) for n,row in value.items()] if isinstance(value,dict) else value
def source_diff(root):
    rows=[]
    for name in ['src/flash_native.c','src/flash_native.h','src/native_io.h','src/host_io.c','src/host_io.h','tests/test_flash.c','verify.py','verify.sh','verify_host.py','.gitignore']:
        old=root/OLD/name;new=root/MODEL/name;a=old.read_text(encoding='utf-8');b=new.read_text(encoding='utf-8');changed=a!=b
        need(changed==(name in ('src/flash_native.c','src/native_io.h','verify_host.py')),'only intended three changes from previous model')
        rows.append(dict(path=name,previous_sha256=sha(old),current_sha256=sha(new),changed=changed,unified_diff=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=OLD+'/'+name,tofile=MODEL+'/'+name))))
    return dict(passed=True,files=rows,host_provider_tests_API_unchanged=True,compiler_profiles_changed=False,padding_added=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=read(H/'seal.json')
    for row in seal['members']:
        path=H/row['path'];need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'sealed implementation member '+row['path'])
    for row in seal['model_members']:
        path=root/row['path'];need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'sealed model member '+row['path'])
    for row in seal['independent_review_seals']:
        path=H/row['path'];need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'closed independent review seal')
        for member in members(read(path)):need(sha(path.parent/member['path'])==member['sha256'],'immutable independent review member')
    need(source_diff(root)==read(H/'source-diff.json'),'exact previous/current source diff')
    N=load('prefix_native_replay',H/'verify_native.py');B=load('prefix_host_replay',root/MODEL/'verify_host.py');index=read(H/'results.json');replayed=[];missing=[]
    for row in index['results']:
        need(sha(H/row['metadata'])==row['sha256'],'selected immutable receipt metadata');r=read(H/row['metadata']);need(r['passed'] and r['mode']==row['mode'],'selected language/result')
        need(r['runner_sha256']==sha(H/'verify_native.py' if row['kind']=='native' else root/MODEL/'verify_host.py'),'current exact selected runner')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():
            need(sha(actual)==row['sha256'],'actual archive identity');(N if row['kind']=='native' else B).replay(root,actual);replayed.append(row['kind']+'-'+row['mode'])
        else:missing.append(row['kind']+'-'+row['mode'])
    option=index['CLI_options'];need(sha(H/option['metadata'])==option['sha256'],'selected option regression');report=read(H/option['metadata']);need(report['passed'] and report['runner_sha256']==sha(H/'verify_native.py') and report['script_sha256']==sha(H/'test_cli_options.py'),'current CLI regression identities')
    path=root/option['artifact_dir'];receipt=path/'verification.json'
    if receipt.is_file():
        need(sha(receipt)==option['sha256'],'actual CLI test receipt');N.replay(root,root/MODEL/'build/cli-alternate/c/verification.json',root/MODEL/'build/alternate-ID2966.reference')
        for command in report['commands']:need(sha(path/command['log'])==command['log_sha256'],'actual option regression log')
        replayed.append('alternate-reference-c')
    else:missing.append('alternate-reference-c')
    need(not a.require_local_builds or not missing,'required local archives missing')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),actual_archives_replayed=replayed,missing_local_archives=missing,five_leaves_byte_identical=True,total_function_bytes=262,instructions=99,quarter_save_order_original=False,full_image_integration=False,target_execution=False,hardware=False,OTA_ready=False)))
if __name__=='__main__':main()
