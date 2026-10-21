"""Bounded create/rename capability evidence; no compiler or target execution."""
import hashlib,json,os,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'experiments/tsl9-v4160-tx-register-abi/build'/('temp-inspection-'+uuid.uuid4().hex)
folder.mkdir(parents=True)
observations=[]
for label,base in [('inherited_process_TEMP',Path(tempfile.mkdtemp(prefix='tsl9-entry-rename-'))),('explicit_owned_TEMP',folder/'compiler-temp')]:
 base.mkdir(exist_ok=True);src=base/'owned-probe.s.tmp';dst=base/'owned-probe.s';r=dict(label=label,directory=str(base),create=False,rename=False)
 try:
  src.write_bytes(b'/* ordinary compiler temporary capability probe */\n');r['create']=True;src.rename(dst);r['rename']=True
 except OSError as e:r.update(error_type=type(e).__name__,errno=e.errno,winerror=getattr(e,'winerror',None),error=str(e))
 for p in (src,dst):
  try:
   if p.is_file():p.unlink()
  except OSError as e:r['cleanup_error']=str(e)
 if label=='inherited_process_TEMP':
  try:base.rmdir()
  except OSError as e:r['directory_cleanup_error']=str(e)
 observations.append(r)
entry=ROOT/'experiments/tsl9-v4160-tx-register-abi/adapter/entry.S';text=entry.read_text();report=dict(TEMP=os.environ.get('TEMP'),TMP=os.environ.get('TMP'),python_TEMP=tempfile.gettempdir(),entry_source_sha256=hashlib.sha256(entry.read_bytes()).hexdigest(),entry_has_C_preprocessing_directives=any(l.lstrip().startswith('#') for l in text.splitlines()),entry_has_include_directives=any('.include' in l for l in text.splitlines()),observations=observations,compiler_executed=False,target_executed=False)
(folder/'inspection.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(dict(receipt=str(folder/'inspection.json'),**report)))
