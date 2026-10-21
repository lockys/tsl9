#!/usr/bin/env python3
"""Offline C/C++ clock register-contract tests; no RV32 code is executed."""
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


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOLS=load('clock_register_tools',ROOT/'scripts/portable_verify.py')


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def register_source_proof():
    mapping=read(MODEL/'source-map.json')
    seal=TOOLS.first(['analysis/v4160-clock-abi-2026-10-21/source-review/final-audit.json',
                      'apk-analysis/tsl9-v4160-clock-abi-2026-10-21/source-review/final-audit.json'])
    TOOLS.need(TOOLS.digest(seal)==mapping['register_source_seal_sha256'],'Exact register source review seal')
    inputs={seal:TOOLS.digest(seal)}
    for member in read(seal)['members']:
        p=(seal.parent/member['path']).resolve()
        TOOLS.need(p.is_relative_to(seal.parent.resolve()) and p.stat().st_size==member['bytes']
                   and TOOLS.digest(p)==member['sha256'],'Exact register review member')
        inputs[p]=member['sha256']
    old=TOOLS.first(['analysis/v4160-system-clock-query-2026-10-21/source/final-audit.json',
                     'apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/final-audit.json']).parent
    # Reuse the sealed format decoder directly, with the layout resolved here.
    # Its historical V1 CLI assumes an older analysis-directory prefix.
    checker=load('clock_register_source_decoder',seal.parent/'check-source-review.py')
    facts=checker.inspect(old)
    expected=read(seal.parent/'source-facts.json')['destination_fields']
    TOOLS.need(facts==expected,'All original destination fields match sealed facts')
    result=dict(passed=True,integer_write_allowlists={k:v['may_write_integer_registers'] for k,v in facts.items()},
                destination_instruction_counts={k:len(v['writes']) for k,v in facts.items()},
                normal_return_formulas_static_review_only=True,original_ABI_proved=False)
    return inputs,result


def verify(mode,tests_only):
    build=MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode)
    build.mkdir(parents=True)
    inputs={p:TOOLS.digest(p) for p in MODEL.rglob('*') if p.is_file()
            and not {'build','__pycache__'}.intersection(p.relative_to(MODEL).parts)}
    inputs[ROOT/'scripts/portable_verify.py']=TOOLS.digest(ROOT/'scripts/portable_verify.py')
    for name,value in read(MODEL/'source-map.json')['dependency_inputs'].items():
        p=ROOT/name;TOOLS.need(TOOLS.digest(p)==value,'Exact reused memory fixture dependency');inputs[p]=value
    source=registers=None
    if not tests_only:
        spec=dict(scope='v4160-system-clock-query-2026-10-21',proof=dict(
            target_bytes=214,target_instructions=69,raw_operand_mutation_rejections=50))
        pins,source=TOOLS.source_proof(spec,MODEL,build);inputs.update(pins)
        pins,registers=register_source_proof();inputs.update(pins)
    compiler,environment,msvc=TOOLS.compiler_for(mode)
    executable=build/('host-tests.exe' if os.name=='nt' else 'host-tests')
    sources=[MODEL/'src/clock_query.c',MODEL/'src/clock_fields.c',MODEL/'tests/test_registers.c']
    includes=[MODEL/'src',MODEL/'tests',ROOT/'experiments/tsl9-v4160-native-clock/src']
    if msvc:
        flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
               '/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_CLOCK_REGISTER_HOST_TEST=1',
               '/Fo'+str(build)+os.sep]+['/I'+str(p) for p in includes]
        argv=[compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
               '-O0','-Wall','-Wextra','-Werror','-DTSL9_CLOCK_REGISTER_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        argv=[compiler,*flags,*sources,'-o',executable]
    compiler_hash=TOOLS.digest(compiler)
    TOOLS.run(argv,cwd=build,env=environment,log=build/'compiler.log')
    result=json.loads(TOOLS.run([executable],cwd=build,env=environment,log=build/'test-output.json').strip())
    TOOLS.need(result==dict(passed=True,groups=6,checks=293845),'All memory and return-register tests')
    TOOLS.need(all(TOOLS.digest(p)==h for p,h in inputs.items()),'Host inputs changed')
    TOOLS.need(TOOLS.digest(compiler)==compiler_hash,'Compiler changed')
    receipt=dict(schema='TSL9-clock-return-register-host-v1',passed=True,mode=mode,tests=result,
                 source_sha256={str(p):h for p,h in inputs.items()},original_source=source,register_source=registers,
                 source_proof_checked=not tests_only,compiler=str(compiler),compiler_sha256=compiler_hash,
                 compile_flags=flags,executable=str(executable),executable_sha256=TOOLS.digest(executable),
                 native_registers_checked=False,original_ABI_proved=False,original_executed=False,
                 ISA_emulation=False,hardware=False,network=False,OTA_ready=False)
    path=build/'verification.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(path),sha256=TOOLS.digest(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['c','cpp','both'],default='both')
    parser.add_argument('--tests-only',action='store_true',help='Explicitly omit raw source/register proof')
    args=parser.parse_args()
    results=[]
    for mode in ['c','cpp'] if args.language=='both' else [args.language]:
        print('Verifying clock memory and return registers: '+mode,file=sys.stderr,flush=True)
        result=verify(mode,args.tests_only);results.append(result)
        print('CLOCK_REGISTERS_HOST_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_checked=False,original_ABI_proved=False,OTA_ready=False)))


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError) as error:
        print('Verification failed: '+str(error),file=sys.stderr);sys.exit(1)
