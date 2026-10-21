#!/usr/bin/env python3
"""Create this new implementation seal once; never modify prior scopes."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,r):
 with p.open('xb') as f:f.write((json.dumps(r,indent=2)+'\n').encode())
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare(root,here,model):
 host=load(model/'verify_host.py','seal_reply_host');native=load(here/'verify_native.py','seal_reply_native');out=here/'receipts';out.mkdir(exist_ok=True);results=[]
 for kind,base,runner in [('host','formal-host-v1',host),('native','formal-native-final',native)]:
  for mode in ('c','cpp'):
   actual=model/'build'/base/mode/'verification.json';runner.replay(root,actual);metadata=out/(kind+'-'+mode+'.json')
   with metadata.open('xb') as f:f.write(actual.read_bytes())
   results.append(dict(kind=kind,mode=mode,receipt=str(actual),archive_relative=actual.relative_to(root).as_posix(),metadata=metadata.relative_to(here).as_posix(),sha256=sha(actual)))
 g=host.guard(root);obj=model/'build/formal-native-final/c/page_reply.o';calls=[];old=g.subprocess.run
 def forbidden(*args,**kwargs):calls.append(1);raise RuntimeError('guard attempted process launch')
 try:
  g.subprocess.run=forbidden
  try:g.execute([obj],here,'must-not-launch-native',{},host_test=True)
  except ValueError as e:message=str(e)
  else:raise ValueError('RISC-V target unexpectedly admitted')
 finally:g.subprocess.run=old
 assert not calls and 'RISC-V ELF is prohibited' in message
 write(out/'host-target-refusal.json',dict(schema='TSL9-page-reply-actual-RV32-prelaunch-refusal-v1',guard_sha256=host.GUARD_PIN,object_relative=obj.relative_to(root).as_posix(),object_sha256=sha(obj),refused=True,subprocess_calls=0,reason=message,current_python=g.host_executable(Path(sys.executable)),RV32_execution=False))
 write(here/'results.json',dict(schema='TSL9-page-reply-selected-implementation-results-v1',passed=True,results=results,native=dict(bytes=124,instructions=50,compiler_only_identity=False,explicit_ABI_order_changed_bytes=28,ordered_linked_original_identity=True,provider_witness_only=True,TX_provider_bytes=0,raw_IR_controls=11,actual_compiled_controls=3),host=dict(groups=3,cases=87,checks=3634,actual_compiled_controls=6,guard_every_launch=True),independent_review_seals={scope:sha(here.parent/scope/'seal.json') for scope in ('source-review','code-review','ABI-review','scheduling-review')},metadata_published_only=True,original_BIN_codegen_input=False,full_image=False,universal_opaque_native_SP_S_ABI=False,RV32_execution=False,hardware=False,network=False,OTA_ready=False))
 print(json.dumps(dict(passed=True,results=results,index_sha256=sha(here/'results.json'))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--prepare-metadata',action='store_true');a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent;case=here.parent;model=root/'experiments/tsl9-v4160-ota-page-reply'
 if a.prepare_metadata:prepare(root,here,model);sys.exit(0)
 members=['verify_native.py','check.py','check.sh','seal.py','README.md','readme.zh-TW.md','readme.en.md','results.json','receipts/host-c.json','receipts/host-cpp.json','receipts/native-c.json','receipts/native-cpp.json','receipts/host-target-refusal.json']
 model_members=['.gitignore','src/page_reply.c','src/page_reply.h','src/reply_io.h','src/host_io.c','src/host_io.h','tests/test_page_reply.c','verify_host.py','verify_native.py','verify.sh','verify_native.sh','README.md','readme.zh-TW.md','readme.en.md']
 external={}
 for scope in ('source-review','code-review','ABI-review','scheduling-review'):
  path=case/scope/'seal.json';s=json.loads(path.read_bytes());external[path.relative_to(root).as_posix()]=sha(path)
  if isinstance(s.get('members'),dict):rows=[(path.parent/n,pin) for n,pin in s['members'].items()]
  else:rows=[((root/s['model'] if r.get('scope')=='model' else path.parent)/r['path'],r['sha256']) for r in s.get('files',s.get('members',[]))]
  for q,pin in rows:assert sha(q)==pin;external[q.relative_to(root).as_posix()]=pin
 for name in model_members:
  b=(model/name).read_bytes();assert b'\r' not in b and b.endswith(b'\n')
 for name in members:
  b=(here/name).read_bytes();assert b'\r' not in b and b.endswith(b'\n')
 write(here/'seal.json',dict(schema='TSL9-page-reply-implementation-seal-v1',members={n:sha(here/n) for n in members},model_members={n:sha(model/n) for n in model_members},external_members=external,archive_replay_required_for_artifact_claims=True,partial_readable_reconstruction=True,full_image=False,OTA_ready=False))
 print(json.dumps(dict(passed=True,seal_sha256=sha(here/'seal.json'),implementation_members=len(members),model_members=len(model_members))))
