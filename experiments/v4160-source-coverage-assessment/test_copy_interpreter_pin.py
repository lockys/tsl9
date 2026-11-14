"""Negative checks of the optional interpreter gate without touching user files."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=ROOT/'experiments/tsl9-copy-instruction-interpreter/interpreter.py'
if not source.is_file(): raise SystemExit('SKIP: optional local interpreter unavailable')
with tempfile.TemporaryDirectory(prefix='filter-pin-') as td:
    root=Path(td); app=root/'experiments/v4160-source-coverage-assessment'; lib=root/'experiments/tsl9-copy-instruction-interpreter'
    app.mkdir(parents=True); lib.mkdir(parents=True)
    for name in ('filter_reference_copy_execution.py','filter_reference_providers.py'): shutil.copyfile(HERE/name,app/name)
    cmd=[sys.executable,'-I','-B',str(app/'filter_reference_copy_execution.py')]
    missing=subprocess.run(cmd,capture_output=True,text=True)
    if missing.returncode==0 or 'SKIP: optional local copy instruction interpreter unavailable' not in missing.stderr: raise ValueError('missing interpreter must not pass')
    data=source.read_bytes()+b'\n# mutation\n'
    (lib/'interpreter.py').write_bytes(data)
    changed=subprocess.run(cmd,capture_output=True,text=True)
    if changed.returncode==0 or 'FAIL: optional local interpreter hash mismatch' not in changed.stderr: raise ValueError('changed interpreter must fail')
    print('PASS: missing and mutated optional interpreter both rejected before import')
