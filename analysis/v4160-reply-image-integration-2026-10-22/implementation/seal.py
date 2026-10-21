#!/usr/bin/env python3
"""Create selected metadata and seal only after independent review closure."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('twelve_image_sealed_verifier',H/'verify_image.py');V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def create(p,b):
 if p.exists():V.need(p.read_bytes()==b,'immutable existing selected metadata')
 else:
  with p.open('xb') as f:f.write(b)
def encoded(r):return (json.dumps(r,indent=2)+'\n').encode()
def members(value):
 rows=value.get('members',value.get('files'));return [dict(path=n,sha256=r if isinstance(r,str) else r['sha256']) for n,r in rows.items()] if isinstance(rows,dict) else rows
def record(p,name):return dict(path=name,bytes=p.stat().st_size,sha256=sha(p))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve();(H/'receipts').mkdir(exist_ok=True);results=[]
 for mode in ('c','cpp'):
  actual=root/V.MODEL/'build/formal-v1'/mode/'verification.json';V.replay(root,actual);r=V.read(actual);metadata='receipts/'+mode+'.json';create(H/metadata,actual.read_bytes());results.append(dict(mode=mode,receipt=str(actual),sha256=sha(actual),metadata=metadata,artifact_dir=actual.parent.relative_to(root).as_posix(),image=str(actual.parent/V.IMAGE),image_sha256=r['checks']['image']['sha256'],compile_TUs=43,commands=61,RELA=8269,ELF_RELA_image_controls=30,dependency_controls=4,scheduling_controls=6,recipe_controls=1,actual_artifacts=len(r['artifacts'])))
 V.need(results[0]['image_sha256']==results[1]['image_sha256']==V.context(root)['manifest']['original_image_sha256'],'both source-derived actual images equal original')
 option=root/V.MODEL/'build/cli-readonly/verification.json';r=V.read(option);V.need(r['passed'] and r['runner_sha256']==sha(H/'verify_image.py') and r['script_sha256']==sha(H/'test_cli.py'),'current readonly CLI identities');create(H/'receipts/cli-options.json',option.read_bytes())
 index=dict(schema='TSL9-twelve-function-source-image-index-v1',results=results,CLI_options=dict(receipt=str(option),sha256=sha(option),metadata='receipts/cli-options.json',artifact_dir=option.parent.relative_to(root).as_posix()),image_sha256=results[0]['image_sha256'],image_basename=V.IMAGE,manifest_sha256=V.MANIFEST_SHA,source_bytes=76800,readable_functions=12,readable_function_bytes=650,allocations=691,retained_storage_sections=679,outside_RELA=8257,owned_RELA=12,RELA=8269,incoming_entry_references=21,canonical_relative_bindings=53,discharged_private_branches=11,differences_vs_original=0,differences_vs_previous_eleven_function_image=0,explicit_ABI_stages=2,compiler_alone_emitted_final_order=False,strict_ROM_provider=False,numeric_ROM_witness_only=True,pointwise_equivalence=False,asynchronous_equivalence=False,universal_resident_ABI=False,hardware=False,network=False,target_execution=False,emulation=False,flashable=False,OTA_ready=False);create(H/'results.json',encoded(index))
 files=[p for p in H.rglob('*') if p.is_file() and p.name!='seal.json' and p.suffix in ('.py','.sh','.md','.json')];model_files=[p for p in(root/V.MODEL).iterdir() if p.is_file()]
 for path in files+model_files:
  if path.name=='original-image-layout.ld':V.need(sha(path)=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b','only exact historical CRLF layout exception')
  else:V.need(b'\r' not in path.read_bytes() and path.read_bytes().endswith(b'\n'),'new UTF8 LF text')
 reviews=[]
 for name in ('ABI-review','source-review'):
  path=H.parent/name/'seal.json';V.need(path.is_file(),'independent review closes first')
  for row in members(V.read(path)):V.need(sha(path.parent/row['path'])==row['sha256'],'immutable independent member')
  reviews.append(record(path,'../'+name+'/seal.json'))
 seal=dict(schema='TSL9-twelve-function-source-image-seal-v1',passed=True,members=[record(p,p.relative_to(H).as_posix()) for p in sorted(files)],model_members=[record(p,p.relative_to(root).as_posix()) for p in sorted(model_files)],independent_review_seals=reviews,selected_receipts=2,image_sha256=results[0]['image_sha256'],storage_image_identical_to_original=True,readable_functions=12,partial_readable_reconstruction=True,compiler_plus_two_explicit_ABI_stages=True,compiler_alone_emitted_final_order=False,ROM_provider=False,universal_resident_ABI=False,physical_compatibility=False,hardware=False,target_execution=False,flashable=False,OTA_ready=False);create(H/'seal.json',encoded(seal));print(json.dumps(dict(passed=True,seal_sha256=sha(H/'seal.json'),index_sha256=sha(H/'results.json'),members=len(files),model_members=len(model_files))))
