"""Read-only closure of the selected source-image report, with optional archives."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--require-local-builds',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    seal=read(H/'final-audit.json')
    for n,pin in seal['members'].items():
        path=(H/n).resolve();need(path.is_relative_to(H.resolve()) and sha(path)==pin,'sealed report member '+n)
    for n,pin in seal['model_members'].items():need(sha(root/n)==pin,'sealed portable model input '+n)
    spec=importlib.util.spec_from_file_location('source_image_readonly',H/'verify_image.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V);ctx=V.context(root)
    index=read(H/'results.json');need(len(index['results'])==2 and {r['mode'] for r in index['results']}=={'c','cpp'},'selected actual C/CPP receipt metadata')
    replayed=[];missing=[]
    for row in index['results']:
        metadata=H/row['metadata'];need(sha(metadata)==row['sha256'],'byte-identical selected actual receipt copy');r=read(metadata)
        need(r['passed'] is True and r['mode']==row['mode'] and r['runner_sha256']==sha(H/'verify_image.py') and r['manifest_sha256']==V.MANIFEST_SHA,'actual receipt identities')
        need(r['source_files']==ctx['manifest']['source_files'],'current exact source/header pins')
        need(r['checks']['image']['sha256']==index['image_sha256'] and r['checks']['image']['bytes']==76800 and len(r['checks']['image']['differences'])==8,'actual selected image result')
        need(len(r['actual_negative_controls'])==15 and all(x['rejected'] is True for x in r['actual_negative_controls']),'all15 actual negative artifacts rejected')
        need(all(r[k] is False for k in ['strict_ROM_provider','pointwise_equivalence','asynchronous_equivalence','flashable','OTA_ready','hardware','network','target_execution','emulation']),'false unresolved readiness gates remain false')
        actual=root/row['artifact_dir']/'verification.json'
        if actual.is_file():
            need(sha(actual)==row['sha256'],'selected local actual receipt matches metadata');V.replay(root,actual,ctx);replayed.append(row['mode'])
        else:missing.append(row['mode'])
    need(not a.require_local_builds or not missing,'required selected historical archives unavailable; run a fresh build separately')
    print(json.dumps(dict(passed=True,seal_sha256=sha(H/'final-audit.json'),selected_metadata=2,local_archives_replayed=replayed,missing_local_archives=missing,
        fresh_compilation=False,source_bytes=76800,differences=8,image_sha256=index['image_sha256'],flashable=False,OTA_ready=False,target_execution=False)))
if __name__=='__main__':main()
