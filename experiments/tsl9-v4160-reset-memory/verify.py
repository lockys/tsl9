#!/usr/bin/env python3
"""Offline source/host checks of our reset-memory C/C++, not RV32 execution."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

MODEL=Path(__file__).resolve().parent
ROOT=MODEL.parents[1]
SPEC=importlib.util.spec_from_file_location('reset_memory_tools',ROOT/'scripts/portable_verify.py')
TOOLS=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(TOOLS)


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def source_proof(build,firmware):
    mapping=read(MODEL/'source-map.json')
    seal=TOOLS.first(['analysis/v4160-reset-memory-2026-10-21/source-review/final-audit.json',
                      'apk-analysis/tsl9-v4160-reset-memory-2026-10-21/source-review/final-audit.json'])
    TOOLS.need(TOOLS.digest(seal)==mapping['source_seal_sha256'],'Exact reset-memory source seal')
    sealed=read(seal)
    TOOLS.need(sealed['passed'] and sealed['sealed'],'Completed source review')
    pins={seal:TOOLS.digest(seal)}
    for item in sealed['members']:
        p=(seal.parent/item['path']).resolve()
        TOOLS.need(p.is_relative_to(seal.parent.resolve()) and p.stat().st_size==item['bytes']
                   and TOOLS.digest(p)==item['sha256'],'Exact sealed source member')
        pins[p]=item['sha256']
    output=TOOLS.run([sys.executable,'-X','utf8','-B',seal.parent/'check-source-review.py',
                      '--firmware',firmware,'--review-root',seal.parent],cwd=ROOT,log=build/'source-proof.log')
    result=json.loads(output.strip())
    TOOLS.need(result['passed'] and all(result[k]==v for k,v in dict(source_bytes=62,instructions=17,
               raw_mutations_rejected=17,reset_context_bytes=138,initializer_bytes=128).items()),'Full exact selected source proof')
    return pins,result


def verify(mode,tests_only):
    build=MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode);build.mkdir(parents=True)
    mapping=read(MODEL/'source-map.json')
    firmware=TOOLS.original_by_hash(mapping['firmware_sha256'])
    inputs={p:TOOLS.digest(p) for p in MODEL.rglob('*') if p.is_file()
            and not {'build','__pycache__'}.intersection(p.relative_to(MODEL).parts)}
    inputs[firmware]=mapping['firmware_sha256']
    inputs[ROOT/'scripts/portable_verify.py']=TOOLS.digest(ROOT/'scripts/portable_verify.py')
    info=mapping['initializer'];raw=firmware.read_bytes()[info['file_offset']:info['file_offset']+info['bytes']]
    fixture=build/'initializer.bin';fixture.write_bytes(raw)
    TOOLS.need(len(raw)==128 and TOOLS.digest(fixture)==info['sha256'],'Exact original initializer data copy')
    proof=None
    if not tests_only:
        pins,proof=source_proof(build,firmware);inputs.update(pins)
    compiler,environment,msvc=TOOLS.compiler_for(mode)
    executable=build/('host-tests.exe' if os.name=='nt' else 'host-tests')
    sources=[MODEL/'src/reset_memory.c',MODEL/'tests/test_reset_memory.c']
    includes=[MODEL/'src',MODEL/'tests']
    if msvc:
        flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
               '/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_RESET_MEMORY_HOST_TEST=1',
               '/Fo'+str(build)+os.sep]+['/I'+str(p) for p in includes]
        argv=[compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
               '-O0','-Wall','-Wextra','-Werror','-DTSL9_RESET_MEMORY_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        argv=[compiler,*flags,*sources,'-o',executable]
    compiler_hash=TOOLS.digest(compiler)
    TOOLS.run(argv,cwd=build,env=environment,log=build/'compiler.log')
    result=json.loads(TOOLS.run([executable,'initializer.bin'],cwd=build,env=environment,log=build/'test-output.json').strip())
    TOOLS.need(result==dict(passed=True,groups=5,cases=338,checks=133601),'Complete reset-memory host suite')
    TOOLS.need(all(TOOLS.digest(p)==h for p,h in inputs.items()),'Host inputs changed')
    TOOLS.need(TOOLS.digest(compiler)==compiler_hash and TOOLS.digest(fixture)==info['sha256'],'Compiler or initializer copy changed')
    receipt=dict(schema='TSL9-reset-memory-host-verification-v1',passed=True,mode=mode,tests=result,
                 source_sha256={str(p):h for p,h in inputs.items()},source_proof_checked=not tests_only,
                 original_source=proof,initializer_data_sha256=info['sha256'],initializer_data_bytes=128,
                 compiler=str(compiler),compiler_sha256=compiler_hash,compile_flags=flags,
                 executable=str(executable),executable_sha256=TOOLS.digest(executable),
                 original_executed=False,ISA_emulation=False,native_checked=False,
                 original_entry_adapter_proved=False,original_IRQ_ABI_proved=False,hardware=False,network=False,OTA_ready=False)
    path=build/'verification.json';path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(path),sha256=TOOLS.digest(path))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--language',choices=['c','cpp','both'],default='both')
    p.add_argument('--tests-only',action='store_true',help='Explicitly omit raw source proof, still require original initializer data')
    a=p.parse_args();results=[]
    for mode in ['c','cpp'] if a.language=='both' else [a.language]:
        print('Checking reset-memory source/host: '+mode,file=sys.stderr,flush=True)
        result=verify(mode,a.tests_only);results.append(result)
        print('RESET_MEMORY_HOST_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_checked=False,entry_adapter_proved=False,OTA_ready=False)))


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError) as error:
        print('Verification failed: '+str(error),file=sys.stderr);sys.exit(1)
