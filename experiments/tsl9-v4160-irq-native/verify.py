#!/usr/bin/env python3
"""Run the new C/C++ core against pinned source proofs and the canonical host oracle."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

MODEL = Path(__file__).resolve().parent
ROOT = MODEL.parents[1]
OLD = ROOT/'experiments/tsl9-v4160-interrupt-registers'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOLS = load('irq_native_host_tools', ROOT/'scripts/portable_verify.py')


def verify(mode):
    mapping = json.loads((MODEL/'source-map.json').read_text(encoding='utf8'))
    inputs = {}
    for name, pin in mapping['host_dependencies_sha256'].items():
        p = (ROOT/name).resolve()
        TOOLS.need(p.is_relative_to(ROOT.resolve()) and TOOLS.digest(p) == pin, 'Pinned canonical host dependency')
        inputs[p] = pin
    previous = load('irq_native_original_proof', OLD/'verify.py')
    build = MODEL/'build'/('host-'+uuid.uuid4().hex+'-'+mode)
    build.mkdir(parents=True)
    source_inputs, proof = previous.source_proof(build)
    inputs.update(source_inputs)
    TOOLS.need(all(proof[k] == v for k, v in dict(source_bytes=264,instructions=94,ranges=5,
               raw_negative_controls_rejected=94).items()), 'Complete original five-range evidence')
    for name in ('verify.py','verify.sh','source-map.json','src/interrupt_registers.c','src/native_io.h'):
        p = MODEL/name
        inputs[p] = TOOLS.digest(p)
    compiler, environment, msvc = TOOLS.compiler_for(mode)
    compiler_hash = TOOLS.digest(compiler)
    executable = build/('host-tests.exe' if os.name == 'nt' else 'host-tests')
    sources = [MODEL/'src/interrupt_registers.c', OLD/'tests/test_interrupt_registers.c']
    includes = [MODEL/'src', OLD/'src', OLD/'tests']
    if msvc:
        flags = ['/nologo','/W4','/WX','/Od','/TP' if mode == 'cpp' else '/TC',
                 '/std:c++17' if mode == 'cpp' else '/std:c11','/DTSL9_IRQ_REGISTERS_HOST_TEST=1',
                 '/Fo'+str(build)+os.sep] + ['/I'+str(p) for p in includes]
        argv = [compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags = ['-x','c++' if mode == 'cpp' else 'c','-std=c++17' if mode == 'cpp' else '-std=c11',
                 '-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_REGISTERS_HOST_TEST=1']
        flags += [x for p in includes for x in ('-I',str(p))]
        argv = [compiler,*flags,*sources,'-o',executable]
    TOOLS.run(argv,cwd=build,env=environment,log=build/'compiler.log')
    result = json.loads(TOOLS.run([executable],cwd=build,env=environment,log=build/'test-output.json').strip())
    TOOLS.need(result == dict(passed=True,groups=4,cases=9184,checks=246384), 'Complete canonical host coverage')
    TOOLS.need(all(TOOLS.digest(p) == h for p,h in inputs.items()) and TOOLS.digest(compiler) == compiler_hash,
               'Unchanged source, oracle, proofs and compiler')
    receipt = dict(schema='TSL9-IRQ-native-host-verification-v1',passed=True,mode=mode,tests=result,
                   source_sha256={str(p):h for p,h in inputs.items()},source_proof_checked=True,original_source=proof,
                   compiler=str(compiler),compiler_sha256=compiler_hash,compile_flags=flags,
                   executable=str(executable),executable_sha256=TOOLS.digest(executable),
                   native_registers_checked=False,original_full_ABI_proved=False,original_IRQ_ABI_proved=False,
                   original_executed=False,ISA_emulation=False,hardware=False,network=False,OTA_ready=False)
    path = build/'verification.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,mode=mode,tests=result,receipt=str(path),sha256=TOOLS.digest(path))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--language',choices=['c','cpp','both'],default='both')
    a = p.parse_args()
    results = []
    for mode in ['c','cpp'] if a.language == 'both' else [a.language]:
        print('Checking new IRQ source and canonical host oracle: '+mode,file=sys.stderr,flush=True)
        result = verify(mode)
        results.append(result)
        print('IRQ_NATIVE_HOST_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,native_checked=False,OTA_ready=False)))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError,OSError,ValueError) as e:
        print('Verification failed: '+str(e),file=sys.stderr)
        sys.exit(1)
