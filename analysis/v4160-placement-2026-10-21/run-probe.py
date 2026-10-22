#!/usr/bin/env python3
"""Resolve published/workspace paths without modifying sealed probe sources."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import uuid

HERE=Path(__file__).resolve().parent
SEAL='5a3250bad6e00422fc63df21a521eb4427358d19cb86179f5a2b937d16b1fe1f'
IMAGE='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)


def dependency(root,scope):
    candidates=[Path('analysis')/scope/'compiler-review',Path('apk-analysis')/('tsl9-'+scope)/'compiler-review']
    for relative in candidates:
        p=(root/relative).resolve()
        if p.is_dir():
            need(p.is_relative_to(root),'Contained immutable dependency')
            return relative
    raise ValueError('Missing immutable compiler dependency: '+scope)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('kind',choices=['reset','clock','thunk'])
    p.add_argument('--project-root',type=Path,default=HERE.parents[1])
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--language',choices=['c','cpp','both'],default='both')
    p.add_argument('--fragment',action='store_true')
    a=p.parse_args();root=a.project_root.resolve()
    need(not a.fragment or a.kind=='reset','Fragment applies only to reset')
    scope=HERE/'compiler-probe';seal=scope/'final-audit.json'
    need(sha(seal)==SEAL,'Immutable probe review seal')
    pins={Path(__file__).resolve():sha(Path(__file__).resolve()),seal:SEAL}
    for name,h in json.loads(seal.read_text(encoding='utf8'))['members'].items():
        q=(scope/name).resolve();need(q.is_relative_to(scope.resolve()) and sha(q)==h,'Exact sealed probe member');pins[q]=h
    filename={'reset':'probe_oz.py','clock':'probe_clock_oz.py','thunk':'probe_thunks.py'}[a.kind]
    producer=scope/filename
    spec=importlib.util.spec_from_file_location('selected_placement_probe',producer)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    dep=dependency(root,'v4160-clock-abi-2026-10-21' if a.kind=='clock' else 'v4160-reset-memory-2026-10-21')
    # Only path constants are adapted. The original producer validates exact
    # dependency/source/tool hashes and executes its unchanged static gates.
    if a.kind=='thunk':
        module.DEP=dep
        originals=[Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'),
                   Path('exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')]
        firmware=next((r for r in originals if (root/r).is_file() and sha(root/r)==IMAGE),None)
        need(firmware is not None,'Exact original firmware data')
        module.FIRMWARE=firmware;pins[(root/firmware).resolve()]=IMAGE
    else:module.DEPENDENCY=dep
    for q in (root/dep).glob('*.py'):pins[q.resolve()]=sha(q)
    argv=[str(producer),'--project-root',str(root),'--tool-dir',str(a.tool_dir.resolve())]
    if a.kind!='thunk':argv+=['--language',a.language]
    if a.fragment:argv.append('--fragment')
    old=sys.argv;out=io.StringIO()
    try:
        sys.argv=argv
        with contextlib.redirect_stdout(out):module.main()
    finally:sys.argv=old
    result=json.loads(out.getvalue().strip());need(result['passed'],'Original static producer gates passed')
    records=result.get('results',[result])
    for item in records:
        q=Path(item['receipt']).resolve()
        need(q.is_relative_to(root) and sha(q)==item['sha256'],'Actual contained producer receipt')
        need(not json.loads(q.read_text(encoding='utf8')).get('OTA_ready',False),'No OTA readiness claim')
    need(all(sha(q)==h for q,h in pins.items()),'Unchanged adapter, sealed inputs and static dependencies')
    build=HERE/'build'/('path-resolution-'+uuid.uuid4().hex);build.mkdir(parents=True)
    receipt=build/'verification.json'
    receipt.write_text(json.dumps(dict(schema='TSL9-placement-probe-path-adapter-v1',passed=True,kind=a.kind,fragment=a.fragment,
        inputs_sha256={str(q):h for q,h in pins.items()},dependency=str(root/dep),producer_argv=argv,producer_result=result,
        sealed_sources_modified=False,original_or_rebuilt_RV32_executed=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,kind=a.kind,fragment=a.fragment,receipt=str(receipt),sha256=sha(receipt),producer_result=result)))


if __name__=='__main__':main()
