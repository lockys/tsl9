"""Read-only selected seal, metadata and optional actual whole-image replay."""
import argparse,hashlib,json
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def members(value):
    rows=value['members'];return [dict(path=n,**r) for n,r in rows.items()] if isinstance(rows,dict) else rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=V.read(H/'seal.json')
    for r in seal['members']:
        path=(H/r['path']).resolve();V.need(path.is_relative_to(H) and path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed implementation member')
    for r in seal['model_members']:
        path=(root/r['path']).resolve();V.need(path.is_relative_to(root) and path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed model member')
    for r in seal['independent_review_seals']:
        path=H/r['path'];V.need(sha(path)==r['sha256'],'closed independent review')
        for item in members(V.read(path)):V.need(sha(path.parent/item['path'])==item['sha256'],'immutable independent review member')
    ctx=V.context(root);index=V.read(H/'results.json');V.need(len(index['results'])==2,'selected C/C++ image receipts');replayed=[];missing=[]
    for row in index['results']:
        meta=H/row['metadata'];V.need(sha(meta)==row['sha256'],'exact selected receipt metadata');r=V.read(meta);V.need(r['passed'] and r['runner_sha256']==sha(H/'verify_image.py') and r['manifest_sha256']==V.MANIFEST_SHA,'current runner/ledger/language identity')
        V.need(r['mode']==row['mode'] and r['checks']['merged']['RELA']==8270 and r['checks']['actual_commands']['commands']==57 and r['checks']['actual_commands']['compile_TUs']==42 and r['checks']['image']['sha256']==index['image_sha256'] and not r['checks']['image']['differences'],'actual original-identical source image counts')
        V.need(len(r['artifacts'])==201 and len(r['actual_negative_controls'])==23 and len(r['actual_dependency_controls'])==3 and len(r['actual_scheduling_controls'])==4,'actual artifact/control inventory')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():V.need(sha(actual)==row['sha256'],'actual archive identity');V.replay(root,actual);replayed.append(row['mode'])
        else:missing.append(row['mode'])
    option=index['CLI_options'];V.need(sha(H/option['metadata'])==option['sha256'],'selected CLI checks');report=V.read(H/option['metadata']);V.need(report['passed'] and report['runner_sha256']==sha(H/'verify_image.py') and report['script_sha256']==sha(H/'test_cli.py'),'current readonly CLI regression identities')
    base=root/option['artifact_dir']
    if(base/'verification.json').is_file():
        V.need(sha(base/'verification.json')==option['sha256'],'actual CLI receipt')
        for record in report['records']:V.need(sha(base/record['log'])==record['log_sha256'],'actual CLI replay/rejection logs')
        V.need(V.context(root,base/'same-ID2966.reference')['flash']['firmware'].resolve()==(base/'same-ID2966.reference').resolve(),'actual alternate reference context forwarded')
        replayed.append('CLI-options')
    else:missing.append('CLI-options')
    V.need(not a.require_local_builds or not missing,'required actual build archives missing')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),actual_archives_replayed=replayed,missing_local_archives=missing,image_sha256=index['image_sha256'],source_bytes=76800,differences=0,compiler_plus_explicit_ABI_scheduling=True,flashable=False,OTA_ready=False,target_execution=False)))
if __name__=='__main__':main()
