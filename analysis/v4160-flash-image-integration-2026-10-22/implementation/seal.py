"""Create-only LF selected metadata/seal after independent review closes."""
import argparse,hashlib,json
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,indent=2)+'\n').encode()
def create(path,data):
    if path.exists():V.need(path.read_bytes()==data,'existing selected evidence immutable')
    else:path.write_bytes(data)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();(H/'receipts').mkdir(exist_ok=True);rows=[]
    for mode in ('c','cpp'):
        actual=root/V.MODEL/'build/formal-final'/mode/'verification.json';V.replay(root,actual);r=V.read(actual);name='receipts/'+mode+'.json';create(H/name,actual.read_bytes());rows.append(dict(mode=mode,receipt=str(actual),sha256=sha(actual),metadata=name,artifact_dir=actual.parent.relative_to(root).as_posix(),image=str(actual.parent/V.IMAGE),image_sha256=r['checks']['image']['sha256'],compile_TUs=42,RELA=r['checks']['merged']['RELA'],ELF_RELA_image_controls=23,dependency_controls=3))
    V.need(rows[0]['image_sha256']==rows[1]['image_sha256'],'two actual source images identical')
    index=dict(schema='TSL9-eleven-readable-source-image-index-v1',results=rows,image_sha256=rows[0]['image_sha256'],image_basename=V.IMAGE,manifest_sha256=V.MANIFEST_SHA,source_bytes=76800,readable_functions=11,readable_function_bytes=526,allocations=691,retained_storage_sections=680,outside_RELA=8259,owned_RELA=11,RELA=8270,incoming_entry_references=20,canonical_relative_bindings=53,differences_vs_original=70,differences_vs_previous_IRQ_image=62,strict_ROM_provider=False,numeric_ROM_witness_only=True,pointwise_equivalence=False,asynchronous_equivalence=False,full_GPR_prefix_equivalence=False,hardware=False,network=False,target_execution=False,emulation=False,flashable=False,OTA_ready=False)
    create(H/'results.json',encoded(index));files=[p for p in H.rglob('*') if p.is_file() and p.name!='seal.json' and p.suffix in ('.py','.sh','.md','.json')];models=[p for p in (root/V.MODEL).iterdir() if p.is_file()]
    def record(p,n):return dict(path=n,bytes=p.stat().st_size,sha256=sha(p))
    for path in files:V.need(b'\r' not in path.read_bytes(),'new authored reports/scripts use LF')
    for path in models:
        if path.name!='original-image-layout.ld':V.need(b'\r' not in path.read_bytes(),'new authored model text uses LF')
    seal=dict(schema='TSL9-eleven-readable-source-image-seal-v1',passed=True,members=[record(p,p.relative_to(H).as_posix()) for p in sorted(files)],model_members=[record(p,p.relative_to(root).as_posix()) for p in sorted(models)],selected_receipts=2,image_sha256=rows[0]['image_sha256'],storage_image_admitted=True,readable_functions=11,partial_readable_reconstruction=True,strict_ROM_provider=False,full_GPR_prefix_equivalence=False,pointwise_equivalence=False,asynchronous_equivalence=False,physical_compatibility=False,hardware=False,target_execution=False,flashable=False,OTA_ready=False)
    create(H/'seal.json',encoded(seal));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(files),model_members=len(models))))
if __name__=='__main__':main()
