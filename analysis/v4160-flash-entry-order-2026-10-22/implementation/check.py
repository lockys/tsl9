"""Read-only exact source-diff and selected artifact replay."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent;OLD='experiments/tsl9-v4160-flash-native';MODEL='experiments/tsl9-v4160-flash-entry-order'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_diff(root):
    names=['src/flash_native.c','src/flash_native.h','src/native_io.h','src/host_io.c','src/host_io.h','tests/test_flash.c','verify.py','verify.sh','verify_host.py','.gitignore'];rows=[]
    for name in names:
        old=root/OLD/name;new=root/MODEL/name;expected=old.read_bytes()
        if name=='src/flash_native.c':
            text=expected.decode();start=text.index('fn_word tsl9_flash_program_18ef2');a=text[:start];b=text[start:];b=b.replace('destination=FN_AND(destination,FN_K(0xffffff00u));','destination=FN_ALIGN0(destination);',1)
            for pc,mask in [('18f02','1'),('18f0c','2')]:
                before='FN_READ(0x'+pc+'u,FN_ADD(base,FN_K(12u)),status);status=FN_AND(status,FN_K('+mask+'u));';after='FN_READ(0x'+pc+'u,FN_ADD(base,FN_K(12u)),status);status=FN_POLL5_AND(status,'+mask+'u);';need(b.count(before)==1,'one initial poll source site');b=b.replace(before,after)
            for pc,mask in [('18f06','1'),('18f10','2')]:
                anchor='while(FN_POLL_TRUE(0x'+pc+'u,status,'+mask+'u));FN_CHECK_FLOW(); }';need(b.count(anchor)==1,'one original fresh base site');b=b.replace(anchor,anchor+'\n    base=FN_BASE4();')
            expected=(a+b).encode()
        elif name=='src/native_io.h':
            text=expected.decode().replace('#define FN_COUNT() FN_K(256u)','#define FN_ALIGN0(v) FN_AND((v),FN_K(0xffffff00u))\n#define FN_POLL5_AND(v,mask) FN_AND((v),FN_K(mask))\n#define FN_COUNT() FN_K(256u)')
            text=text.replace('#define FN_COUNT() FN_FIXED_VALUE("a2",256u)','#define FN_ALIGN0(v) FN_FIXED_VALUE("a0",FN_AND(FN_FIXED_VALUE("a0",(v)),FN_K(0xffffff00u)))\n#define FN_POLL5_AND(v,mask) FN_FIXED_VALUE("a5",FN_AND((v),FN_K(mask)))\n#define FN_COUNT() FN_FIXED_VALUE("a2",256u)');expected=text.encode()
        elif name=='verify_host.py':expected=expected.replace(OLD.encode(),MODEL.encode())
        need(new.read_bytes()==expected,'only authorized source/model-path changes '+name);rows.append(dict(path=name,old_sha256=sha(old),new_sha256=sha(new),changed=old.read_bytes()!=new.read_bytes()))
    return dict(passed=True,files=rows,changed_paths=['src/flash_native.c','src/native_io.h','verify_host.py'],host_semantics_unchanged=True,compiler_profiles_changed=False,padding_added=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=read(H/'seal.json')
    for row in seal['members']:
        path=H/row['path'];need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'sealed implementation member '+row['path'])
    for row in seal['model_members']:
        path=root/row['path'];need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'sealed readable model '+row['path'])
    need(source_diff(root)==read(H/'source-diff.json'),'exact bounded source changes')
    N=load('entry_order_native_replay',H/'verify_native.py');B=load('entry_order_host_replay',root/MODEL/'verify_host.py');index=read(H/'results.json');replayed=[];missing=[]
    for row in index['results']:
        metadata=H/row['metadata'];need(sha(metadata)==row['sha256'],'selected exact receipt metadata');r=read(metadata);need(r['passed'] and r['mode']==row['mode'],'actual language/result')
        expected=sha(H/'verify_native.py' if row['kind']=='native' else root/MODEL/'verify_host.py');need(r['runner_sha256']==expected,'current exact runner')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():need(sha(actual)==row['sha256'],'actual archive identity');(N if row['kind']=='native' else B).replay(root,actual);replayed.append(row['kind']+'-'+row['mode'])
        else:missing.append(row['kind']+'-'+row['mode'])
    option_row=index['CLI_options'];option=read(H/option_row['metadata']);need(sha(H/option_row['metadata'])==option_row['sha256'] and option['passed'] and option['runner_sha256']==sha(H/'verify_native.py') and option['script_sha256']==sha(H/'test_cli_options.py'),'exact CLI option regression metadata')
    need(option['alternate_reference_compile_passed'] and option['same_explicit_reference_replay_passed'] and option['wrong_default_context_rejected'] and not option['target_execution'],'alternate-reference API regression')
    option_base=root/option_row['artifact_dir']
    if (option_base/'verification.json').is_file():
        need(sha(option_base/'verification.json')==option_row['sha256'],'actual option archive identity');N.replay(root,option_base/'native/c/verification.json',option_base/'same-ID2966-alternate-location.bin')
        for c in option['commands']:need(sha(option_base/c['log'])==c['log_sha256'],'actual option regression log')
        replayed.append('alternate-reference-c')
    else:missing.append('alternate-reference-c')
    need(not a.require_local_builds or not missing,'required local archives missing')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),source_diff_checked=True,actual_archives_replayed=replayed,missing_local_archives=missing,program_bytes=100,total_function_bytes=262,instructions=99,full_image_integration=False,target_execution=False,OTA_ready=False)))
if __name__=='__main__':main()
