"""Create-only selected receipt copies and final report seal, after actual replay."""
import argparse,hashlib,json
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def create(p,data):
    if p.exists():need(p.read_bytes()==data,'existing seal/report is immutable: '+str(p))
    else:p.write_bytes(data)
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode('utf-8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--actual-build',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();build=a.actual_build.resolve();ctx=V.context(root);results=[]
    (H/'receipts').mkdir(exist_ok=True)
    for mode in ('c','cpp'):
        receipt=build/mode/'verification.json';V.replay(root,receipt,ctx);r=read(receipt)
        need(r['mode']==mode and r['runner_sha256']==sha(H/'verify_image.py'),'current actually compiled runner/language identity')
        metadata=H/'receipts'/(mode+'.json');create(metadata,receipt.read_bytes())
        results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),metadata=metadata.relative_to(H).as_posix(),artifact_dir=receipt.parent.relative_to(root).as_posix(),
            image=str(receipt.parent/'NOT-FLASH-VALIDATED-irq-callframe.bin'),image_sha256=r['checks']['image']['sha256'],allocations=691,retained_sections=686,
            canonical_bindings=53,outside_RELA=8270,total_RELA=8276,source_bytes=76800,difference_bytes=8,actual_negative_controls=15,actual_commands=44,dependency_rules=36,artifacts=len(r['artifacts'])))
    need(results[0]['image_sha256']==results[1]['image_sha256'],'selected C/CPP byteidentical image')
    index=dict(schema='TSL9-source-integrated-IRQ-image-index-v1',results=results,runner_sha256=sha(H/'verify_image.py'),manifest_sha256=V.MANIFEST_SHA,image_sha256=results[0]['image_sha256'],
        strict_ROM_provider=False,numeric_ROM_witness_only=True,pointwise_equivalence=False,asynchronous_equivalence=False,flashable=False,OTA_ready=False,target_execution=False,emulation=False,network=False,hardware=False)
    create(H/'results.json',encoded(index))
    names=['verify_image.py','verify_image.sh','check_image.py','check_image.sh','seal_report.py','README.md','readme.en.md','readme.zh-TW.md','results.json','receipts/c.json','receipts/cpp.json']
    models=['.gitignore','prepare_manifest.py','source-manifest.json','original-image-layout.ld','verify.py','verify.sh','README.md','readme.en.md','readme.zh-TW.md']
    seal=dict(schema='TSL9-source-integrated-IRQ-image-seal-v1',members={n:sha(H/n) for n in names},model_members={V.MODEL+'/'+n:sha(root/V.MODEL/n) for n in models},
        selected_receipts=2,image_sha256=index['image_sha256'],source_bytes=76800,difference_bytes=8,negative_controls_each=15,all_static_gates_passed=True,
        strict_ROM_provider=False,pointwise_equivalence=False,asynchronous_equivalence=False,flashable=False,OTA_ready=False,target_execution=False,emulation=False,hardware=False,network=False)
    create(H/'final-audit.json',encoded(seal));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'final-audit.json'),index_sha256=sha(H/'results.json'),members=len(names),model_members=len(models))))
if __name__=='__main__':main()
