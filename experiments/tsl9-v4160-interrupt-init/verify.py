#!/usr/bin/env python3
"""Build our own IRQ reconstruction tests; never execute RISC-V firmware."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

MODEL=Path(__file__).resolve().parent
ROOT=MODEL.parents[1]
SPEC=importlib.util.spec_from_file_location('tsl9_portable_tools',ROOT/'scripts/portable_verify.py')
TOOLS=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOLS)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_proof(build):
    mapping=read_json(MODEL/'source-map.json')
    scope='v4160-interrupt-init-2026-10-21'
    candidates=[ROOT/'analysis'/scope/'source',ROOT/'apk-analysis'/('tsl9-'+scope)/'source']
    source=next((p for p in candidates if (p/'final-audit.json').is_file()),None)
    TOOLS.need(source is not None,'Required local IRQ source proof')
    seal=source/'final-audit.json'
    TOOLS.need(sha(seal)==mapping['source_seal_sha256'],'Exact sealed source proof')
    sealed=read_json(seal)
    TOOLS.need(sealed['schema']=='TSL9-interrupt-init-source-audit-v1' and sealed['passed']
               and len(sealed['files'])==7,'Completed exact source proof schema')
    inputs={seal:sha(seal),MODEL/'source-map.json':sha(MODEL/'source-map.json')}
    for item in sealed['files']:
        p=(source/item['path']).resolve()
        TOOLS.need(p.is_relative_to(source.resolve()),'Contained source proof member')
        TOOLS.need(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Immutable source proof member')
        inputs[p]=sha(p)
    firmware=TOOLS.original_by_hash(mapping['runtime_sha256'])
    inputs[firmware]=mapping['runtime_sha256']
    result=json.loads(TOOLS.run([sys.executable,'-B',source/'inspect-source.py','--check',
                               '--firmware',firmware,'--source-root',source],
                              cwd=ROOT,log=build/'source-proof.log').strip())
    TOOLS.need(result.get('passed') and result['source_bytes']==264 and result['instructions']==94
               and result['ranges']==5 and result['raw_negative_controls_rejected']==94,
               'Full selected IRQ source proof')
    return inputs,result


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def verify_host(mode,tests_only):
    build=MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode)
    build.mkdir(parents=True)
    compiler,environment,msvc=TOOLS.compiler_for(mode)
    sources=[MODEL/'src/interrupt_init.c',MODEL/'tests/test_interrupt_init.c']
    includes=[MODEL/'src',MODEL/'tests']
    inputs={p:sha(p) for p in sources if p.exists()}
    for directory in includes:
        inputs.update({p:sha(p) for p in directory.glob('*.h')})
    inputs[Path(__file__).resolve()]=sha(Path(__file__).resolve())
    inputs[ROOT/'scripts/portable_verify.py']=sha(ROOT/'scripts/portable_verify.py')
    for name in ('README.md','readme.en.md','readme.zh-TW.md','source-map.json','verify.sh'):
        inputs[MODEL/name]=sha(MODEL/name)
    proof=None
    if not tests_only:
        proof_inputs,proof=source_proof(build)
        inputs.update(proof_inputs)
    executable=build/('host-tests.exe' if os.name=='nt' else 'host-tests')
    if msvc:
        flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
               '/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_IRQ_HOST_TEST=1',
               '/Fo'+str(build)+os.sep]+['/I'+str(p) for p in includes]
        command=[compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
               '-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        command=[compiler,*flags,*sources,'-o',executable]
    compiler_before=sha(compiler)
    TOOLS.run(command,cwd=build,env=environment,log=build/'compiler.log')
    result=json.loads(TOOLS.run([executable],cwd=build,env=environment,log=build/'test-output.json').strip())
    TOOLS.need(result.get('passed') and result['groups']==4 and result['checks']==6680,'Complete IRQ host suite')
    TOOLS.need(all(sha(p)==value for p,value in inputs.items()),'Immutable host inputs')
    TOOLS.need(sha(compiler)==compiler_before,'Immutable compiler')
    receipt=dict(passed=True,mode=mode,tests=result,source_sha256={str(p):h for p,h in inputs.items()},
                 original_source=proof,source_proof_checked=not tests_only,
                 compiler=str(compiler),compiler_sha256=compiler_before,compile_flags=flags,
                 executable=str(executable),executable_sha256=sha(executable),
                 original_executed=False,ISA_emulation=False,physical_IO=False,OTA_ready=False)
    p=build/'verification.json'
    p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(p),sha256=sha(p))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['c','cpp','both'],default='both')
    parser.add_argument('--tests-only',action='store_true',help='Explicitly skip raw source proof; receipt records the omission')
    args=parser.parse_args()
    modes=['c','cpp'] if args.language=='both' else [args.language]
    results=[]
    for mode in modes:
        print('Verifying own IRQ reconstruction: '+mode,file=sys.stderr,flush=True)
        value=verify_host(mode,args.tests_only);results.append(value)
        print('IRQ_HOST_RESULT '+json.dumps(value),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_component_checked=False,hardware=False,OTA_ready=False)))


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError) as error:
        print('Verification failed: '+str(error),file=sys.stderr)
        sys.exit(1)
