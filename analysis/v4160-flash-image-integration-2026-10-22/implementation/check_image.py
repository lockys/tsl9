"""Read-only selected seal/metadata and available actual artifact replay."""
import argparse,hashlib,json
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve();seal=V.read(H/'seal.json')
    for r in seal['members']:
        path=(H/r['path']).resolve();V.need(path.is_relative_to(H) and path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed implementation member')
    for r in seal['model_members']:
        path=(root/r['path']).resolve();V.need(path.is_relative_to(root) and path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'sealed source-image model input')
    ctx=V.context(root);index=V.read(H/'results.json');V.need(len(index['results'])==2,'selected actual C/C++ image receipts');replayed=[];missing=[]
    for row in index['results']:
        meta=H/row['metadata'];V.need(sha(meta)==row['sha256'],'byte-identical selected receipt metadata');r=V.read(meta);V.need(r['passed'] and r['runner_sha256']==sha(H/'verify_image.py') and r['manifest_sha256']==V.MANIFEST_SHA,'current successful image runner/source ledger')
        V.need(r['checks']['merged']['RELA']==8270 and r['checks']['actual_commands']['compile_TUs']==42 and r['checks']['image']['sha256']==index['image_sha256'] and len(r['actual_negative_controls'])==23 and len(r['actual_dependency_controls'])==3,'actual expected scoped admission counts')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():V.need(sha(actual)==row['sha256'],'actual local archive identity');V.replay(root,actual);replayed.append(row['mode'])
        else:missing.append(row['mode'])
    V.need(not a.require_local_builds or not missing,'required actual local build archives missing')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),selected_metadata=2,actual_archives_replayed=replayed,missing_local_archives=missing,image_sha256=index['image_sha256'],source_bytes=76800,differences=70,flashable=False,OTA_ready=False,target_execution=False)))
if __name__=='__main__':main()
