#!/usr/bin/env python3
"""Verify original source and our own C/C++ boundary tests; no RV32 execution."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

MODEL=Path(__file__).resolve().parent
ROOT=MODEL.parents[1]
spec=importlib.util.spec_from_file_location('irq_register_tools',ROOT/'scripts/portable_verify.py')
TOOLS=importlib.util.module_from_spec(spec);spec.loader.exec_module(TOOLS)


def read(p):return json.loads(p.read_text(encoding='utf8'))


def source_proof(build):
    mapping=read(MODEL/'source-map.json')
    source=TOOLS.first(['analysis/v4160-interrupt-init-2026-10-21/source/final-audit.json',
                        'apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/source/final-audit.json'])
    TOOLS.need(TOOLS.digest(source)==mapping['source_seal_sha256'],'Exact original IRQ source seal')
    seal=read(source);TOOLS.need(seal['passed'] and len(seal['files'])==7,'Completed original source review')
    inputs={source:TOOLS.digest(source)}
    for item in seal['files']:
        p=(source.parent/item['path']).resolve()
        TOOLS.need(p.is_relative_to(source.parent.resolve()) and p.stat().st_size==item['bytes']
                   and TOOLS.digest(p)==item['sha256'],'Exact sealed original source member')
        inputs[p]=item['sha256']
    firmware=TOOLS.original_by_hash(mapping['runtime_sha256']);inputs[firmware]=mapping['runtime_sha256']
    output=TOOLS.run([sys.executable,'-X','utf8','-B',source.parent/'inspect-source.py','--check',
                      '--firmware',firmware,'--source-root',source.parent],cwd=ROOT,log=build/'source-proof.log')
    result=json.loads(output.strip())
    TOOLS.need(result['passed'] and all(result[k]==v for k,v in dict(source_bytes=264,instructions=94,
               ranges=5,raw_negative_controls_rejected=94).items()),'Complete 94-instruction original proof')
    abi=TOOLS.first(['analysis/v4160-placement-2026-10-21/abi-review/seal.json',
                     'apk-analysis/tsl9-v4160-placement-2026-10-21/abi-review/seal.json'])
    TOOLS.need(TOOLS.digest(abi)==mapping['abi_seal_sha256'],'Exact original/native ABI counterevidence seal')
    reviewed=read(abi);TOOLS.need(reviewed['schema']=='immutable-review-seal-v1' and len(reviewed['files'])==5,'Completed ABI review seal')
    inputs[abi]=TOOLS.digest(abi)
    for item in reviewed.get('members',reviewed.get('files',[])):
        p=(abi.parent/item['path']).resolve()
        TOOLS.need(p.is_relative_to(abi.parent.resolve()) and TOOLS.digest(p)==item['sha256'],'Exact ABI review member')
        inputs[p]=item['sha256']
    result_abi=read(abi.parent/'verification.json')
    TOOLS.need(result_abi['schema']=='TSL9-placement-ABI-counterevidence-v1' and result_abi['passed'],'Completed ABI counterevidence')
    return inputs,result


def verify(mode,tests_only):
    build=MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode);build.mkdir(parents=True)
    inputs={p:TOOLS.digest(p) for p in MODEL.rglob('*') if p.is_file()
            and not {'build','__pycache__'}.intersection(p.relative_to(MODEL).parts)}
    inputs[ROOT/'scripts/portable_verify.py']=TOOLS.digest(ROOT/'scripts/portable_verify.py')
    proof=None
    if not tests_only:
        pins,proof=source_proof(build);inputs.update(pins)
    compiler,environment,msvc=TOOLS.compiler_for(mode)
    executable=build/('host-tests.exe' if os.name=='nt' else 'host-tests')
    sources=[MODEL/'src/interrupt_registers.c',MODEL/'tests/test_interrupt_registers.c']
    includes=[MODEL/'src',MODEL/'tests']
    if msvc:
        flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
               '/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_IRQ_REGISTERS_HOST_TEST=1',
               '/Fo'+str(build)+os.sep]+['/I'+str(p) for p in includes]
        argv=[compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
               '-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_REGISTERS_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        argv=[compiler,*flags,*sources,'-o',executable]
    compiler_hash=TOOLS.digest(compiler)
    TOOLS.run(argv,cwd=build,env=environment,log=build/'compiler.log')
    result=json.loads(TOOLS.run([executable],cwd=build,env=environment,log=build/'test-output.json').strip())
    TOOLS.need(result==dict(passed=True,groups=4,cases=9184,checks=246384),'Complete IRQ register host suite')
    TOOLS.need(all(TOOLS.digest(p)==h for p,h in inputs.items()) and TOOLS.digest(compiler)==compiler_hash,'Unchanged host inputs and compiler')
    receipt=dict(schema='TSL9-interrupt-register-host-verification-v1',passed=True,mode=mode,tests=result,
                 source_sha256={str(p):h for p,h in inputs.items()},source_proof_checked=not tests_only,original_source=proof,
                 compiler=str(compiler),compiler_sha256=compiler_hash,compile_flags=flags,
                 executable=str(executable),executable_sha256=TOOLS.digest(executable),
                 native_registers_checked=False,original_full_ABI_proved=False,original_IRQ_ABI_proved=False,
                 original_executed=False,ISA_emulation=False,hardware=False,network=False,OTA_ready=False)
    path=build/'verification.json';path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(path),sha256=TOOLS.digest(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['c','cpp','both'],default='both')
    parser.add_argument('--tests-only',action='store_true',help='Explicitly omit original source/ABI proof')
    a=parser.parse_args();results=[]
    for mode in ['c','cpp'] if a.language=='both' else [a.language]:
        print('Checking IRQ normal-register source/host: '+mode,file=sys.stderr,flush=True)
        result=verify(mode,a.tests_only);results.append(result)
        print('IRQ_REGISTERS_HOST_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_checked=False,original_full_ABI_proved=False,OTA_ready=False)))


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError) as e:
        print('Verification failed: '+str(e),file=sys.stderr);sys.exit(1)
