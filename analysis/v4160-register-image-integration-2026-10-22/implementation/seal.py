"""Create-only selected metadata and seal after both independent reviews close."""
import argparse,hashlib,json
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def create(p,data):
    if p.exists():V.need(p.read_bytes()==data,'immutable existing selected evidence')
    else:p.write_bytes(data)
def member_rows(value):
    rows=value['members'];return [dict(path=n,**r) for n,r in rows.items()] if isinstance(rows,dict) else rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();(H/'receipts').mkdir(exist_ok=True);rows=[]
    for mode in ('c','cpp'):
        actual=root/V.MODEL/'build/formal-final'/mode/'verification.json';V.replay(root,actual);r=V.read(actual);metadata='receipts/'+mode+'.json';create(H/metadata,actual.read_bytes());rows.append(dict(mode=mode,receipt=str(actual),sha256=sha(actual),metadata=metadata,artifact_dir=actual.parent.relative_to(root).as_posix(),image=str(actual.parent/V.IMAGE),image_sha256=r['checks']['image']['sha256'],compile_TUs=42,commands=57,RELA=8270,ELF_RELA_image_controls=23,dependency_controls=3,scheduling_controls=4,actual_artifacts=201))
    V.need(rows[0]['image_sha256']==rows[1]['image_sha256']==V.context(root)['manifest']['original_image_sha256'],'both actual images equal original reference')
    option=root/V.MODEL/'build/cli-readonly/verification.json';r=V.read(option);V.need(r['passed'] and r['runner_sha256']==sha(H/'verify_image.py') and r['script_sha256']==sha(H/'test_cli.py'),'final readonly CLI check identities');create(H/'receipts/cli-options.json',option.read_bytes());option_meta=dict(receipt=str(option),sha256=sha(option),metadata='receipts/cli-options.json',artifact_dir=option.parent.relative_to(root).as_posix())
    index=dict(schema='TSL9-register-scheduled-source-image-index-v1',results=rows,CLI_options=option_meta,image_sha256=rows[0]['image_sha256'],image_basename=V.IMAGE,manifest_sha256=V.MANIFEST_SHA,source_bytes=76800,readable_functions=11,readable_function_bytes=526,allocations=691,retained_storage_sections=680,outside_RELA=8259,owned_RELA=11,RELA=8270,incoming_entry_references=20,canonical_relative_bindings=53,differences_vs_original=0,differences_vs_previous_full_image=70,differences_vs_previous_IRQ_image=8,explicit_ABI_frame_scheduling=True,compiler_alone_emitted_final_order=False,strict_ROM_provider=False,numeric_ROM_witness_only=True,pointwise_equivalence=False,asynchronous_equivalence=False,full_GPR_prefix_equivalence=False,hardware=False,network=False,target_execution=False,emulation=False,flashable=False,OTA_ready=False)
    create(H/'results.json',encoded(index));files=[p for p in H.rglob('*') if p.is_file() and p.name!='seal.json' and p.suffix in ('.py','.sh','.md','.json')];models=[p for p in(root/V.MODEL).iterdir() if p.is_file()]
    for p in files+models:
        if p.name=='original-image-layout.ld':V.need(sha(p)=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b' and p.read_bytes()==(root/'experiments/tsl9-v4160-flash-image-integration/original-image-layout.ld').read_bytes(),'only exact historical CRLF layout exception')
        else:V.need(b'\r' not in p.read_bytes(),'all newly authored text uses LF')
    def record(p,n):return dict(path=n,bytes=p.stat().st_size,sha256=sha(p))
    reviews=[]
    for name in ('ABI-review','source-review'):
        path=H.parent/name/'seal.json';V.need(path.is_file(),'independent review must close first '+name)
        for item in member_rows(V.read(path)):V.need(sha(path.parent/item['path'])==item['sha256'],'closed independent member')
        reviews.append(record(path,'../'+name+'/seal.json'))
    value=dict(schema='TSL9-register-scheduled-source-image-seal-v1',passed=True,members=[record(p,p.relative_to(H).as_posix()) for p in sorted(files)],model_members=[record(p,p.relative_to(root).as_posix()) for p in sorted(models)],independent_review_seals=reviews,selected_receipts=2,image_sha256=rows[0]['image_sha256'],storage_image_identical_to_original=True,readable_functions=11,partial_readable_reconstruction=True,compiler_plus_explicit_ABI_scheduling=True,compiler_alone_emitted_final_order=False,strict_ROM_provider=False,full_GPR_prefix_equivalence=False,pointwise_equivalence=False,asynchronous_equivalence=False,physical_compatibility=False,hardware=False,target_execution=False,flashable=False,OTA_ready=False)
    create(H/'seal.json',encoded(value));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(files),model_members=len(models))))
if __name__=='__main__':main()
