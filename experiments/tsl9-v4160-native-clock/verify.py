#!/usr/bin/env python3
"""Verify our readable clock C/C++ on the host, never execute RV32 code."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

MODEL = Path(__file__).resolve().parent
ROOT = MODEL.parents[1]
SPEC = importlib.util.spec_from_file_location('tsl9_clock_tools', ROOT/'scripts/portable_verify.py')
TOOLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOLS)


def verify_host(mode, tests_only):
    build = MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode)
    build.mkdir(parents=True)
    compiler, environment, msvc = TOOLS.compiler_for(mode)
    sources = [MODEL/'src/native_clock.c', MODEL/'tests/test_native_clock.c']
    includes = [MODEL/'src', MODEL/'tests']
    paths = sources + [p for d in includes for p in d.glob('*.h')]
    paths += [MODEL/n for n in ('README.md','readme.en.md','readme.zh-TW.md',
                               'source-map.json','verify.sh','verify.py')]
    paths += [ROOT/'scripts/portable_verify.py']
    inputs = {p:TOOLS.digest(p) for p in paths}
    proof = None
    if not tests_only:
        spec = dict(scope='v4160-system-clock-query-2026-10-21', proof=dict(
            target_bytes=214, target_instructions=69, raw_operand_mutation_rejections=50))
        proof_inputs, proof = TOOLS.source_proof(spec, MODEL, build)
        inputs.update(proof_inputs)
    executable = build/('host-tests.exe' if os.name == 'nt' else 'host-tests')
    if msvc:
        flags = ['/nologo','/W4','/WX','/Od','/TP' if mode == 'cpp' else '/TC',
                 '/std:c++17' if mode == 'cpp' else '/std:c11',
                 '/DTSL9_CLOCK_HOST_TEST=1','/Fo'+str(build)+os.sep]
        flags += ['/I'+str(p) for p in includes]
        command = [compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags = ['-x','c++' if mode == 'cpp' else 'c',
                 '-std=c++17' if mode == 'cpp' else '-std=c11',
                 '-O0','-Wall','-Wextra','-Werror','-DTSL9_CLOCK_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        command = [compiler,*flags,*sources,'-o',executable]
    compiler_hash = TOOLS.digest(compiler)
    TOOLS.run(command,cwd=build,env=environment,log=build/'compiler.log')
    output = TOOLS.run([executable],cwd=build,env=environment,log=build/'test-output.json')
    result = json.loads(output.strip())
    TOOLS.need(result.get('passed') and (result['groups'],result['checks']) == (6,269618),
               'All selected clock host checks must pass')
    TOOLS.need(all(TOOLS.digest(p) == h for p,h in inputs.items()),'Inputs changed during verification')
    TOOLS.need(TOOLS.digest(compiler) == compiler_hash,'Compiler changed during verification')
    receipt = dict(schema='TSL9-native-clock-host-verification-v1',passed=True,mode=mode,
                   tests=result,source_sha256={str(p):h for p,h in inputs.items()},
                   original_source=proof,source_proof_checked=not tests_only,
                   compiler=str(compiler),compiler_sha256=compiler_hash,compile_flags=flags,
                   executable=str(executable),executable_sha256=TOOLS.digest(executable),
                   original_executed=False,ISA_emulation=False,hardware=False,network=False,
                   original_ABI_proved=False,native_BIN=False,OTA_ready=False)
    path = build/'verification.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(path),sha256=TOOLS.digest(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['c','cpp','both'],default='both')
    parser.add_argument('--tests-only',action='store_true',
                        help='Explicitly omit the original raw-byte proof; receipt records this')
    args = parser.parse_args()
    modes = ['c','cpp'] if args.language == 'both' else [args.language]
    results = []
    for mode in modes:
        print('Checking our native-clock host tests: '+mode,file=sys.stderr,flush=True)
        result = verify_host(mode,args.tests_only)
        results.append(result)
        print('CLOCK_HOST_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_component_checked=False,
                         hardware=False,OTA_ready=False)))


if __name__ == '__main__':
    try:
        main()
    except (OSError,RuntimeError,ValueError) as error:
        print('Verification failed: '+str(error),file=sys.stderr)
        sys.exit(1)
