#!/usr/bin/env python3
"""Compile only owned host C/C++ with bounded fake numeric memory effects."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(argv, env, cwd, log, okay=True):
    r = subprocess.run([str(x) for x in argv], env=env, cwd=cwd, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=60)
    log.write_text(r.stdout+r.stderr, encoding='utf-8')
    if okay and r.returncode:
        raise ValueError('Command failed: ' + str(log))
    return r

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--firmware', required=True, type=Path)
    p.add_argument('--language', choices=['c', 'cpp'], required=True)
    a = p.parse_args()
    project = a.project_root.resolve(strict=True)
    root = Path(__file__).resolve().parent
    model = project/'experiments/tsl9-v4160-reset-memory'
    original = a.firmware.resolve(strict=True)
    if original.stat().st_size != 76800 or sha(original) != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('Exact original-data identity required')
    helper = project/'scripts/portable_verify.py'
    spec = importlib.util.spec_from_file_location('portable', helper)
    portable = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(portable)
    compiler, environment, msvc = portable.compiler_for(a.language)
    build = root/'build'/(uuid.uuid4().hex+'-'+a.language)
    build.mkdir(parents=True)
    source = model/'src/reset_memory.c'
    includes = [model/'src', model/'tests']
    test = root/'independent-tests.c'
    inputs = [source, model/'src/reset_memory.h', model/'tests/test_io.h', test, helper, Path(__file__).resolve(), original]
    before = {str(f): sha(f) for f in inputs}
    compiler_sha = sha(compiler)
    flags = (['/nologo','/W4','/WX','/Od','/TP' if a.language=='cpp' else '/TC',
              '/std:c++17' if a.language=='cpp' else '/std:c11','/DTSL9_RESET_MEMORY_HOST_TEST=1','/Fo'+str(build)+os.sep]
             if msvc else ['-x','c++' if a.language=='cpp' else 'c','-std=c++17' if a.language=='cpp' else '-std=c11',
                           '-O0','-Wall','-Wextra','-Werror','-DTSL9_RESET_MEMORY_HOST_TEST=1'])
    flags += (['/I'+str(x) for x in includes] if msvc else [s for x in includes for s in ('-I',str(x))])
    def compile_run(text, name):
        selected = source
        if text is not None:
            selected = build/(name+'.c')
            selected.write_text(text, encoding='utf-8')
        exe = build/(name+('.exe' if os.name=='nt' else ''))
        argv = ([compiler,*flags,selected,test,'/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc
                else [compiler,*flags,selected,test,'-o',exe])
        command(argv,environment,build,build/(name+'-compile.log'))
        run = command([exe,original],environment,build,build/(name+'-run.log'),okay=text is None)
        if text is None:
            result = json.loads(run.stdout)
            if not result.get('passed') or result.get('groups') != 5 or result.get('cases') != 538:
                raise ValueError('Independent test coverage mismatch')
        elif run.returncode == 0 or 'FAIL ' not in run.stderr:
            raise ValueError('Mutant did not reach an actual assertion rejection: '+name)
        else:
            result = {'rejected': True, 'exit_code': run.returncode, 'failure': run.stderr.strip()}
        return {'executable':str(exe),'executable_sha256':sha(exe),'result':result}
    normal = compile_run(None,'positive')
    raw = source.read_text()
    changes = [
        ('cached-copy-end','const uint32_t copy_end=RM_GP()+128u;','const uint32_t copy_end=destination+128u;'),
        ('cached-clear-GP','clear=RM_GP()+128u;','clear=destination+128u;'),
        ('signed-copy-compare','while(destination<copy_end)','while((int32_t)destination<(int32_t)copy_end)'),
        ('copy-step-eight','source+=4u;destination+=4u;','source+=8u;destination+=4u;'),
        ('zero-step-eight','clear+=4u;','clear+=8u;'),
        ('copy-includes-bound','while(destination<copy_end)','while(destination<=copy_end)'),
        ('zero-includes-bound','while(clear<zero_end)','while(clear<=zero_end)'),
        ('wrong-A0','RM_OUTPUTS(clear,zero_end,copy_end);','RM_OUTPUTS(clear+4u,zero_end,copy_end);'),
        ('wrong-A1','RM_OUTPUTS(clear,zero_end,copy_end);','RM_OUTPUTS(clear,zero_end+4u,copy_end);'),
        ('wrong-A2','RM_OUTPUTS(clear,zero_end,copy_end);','RM_OUTPUTS(clear,zero_end,copy_end+4u);'),
        ('read-ahead','const uint32_t word=RM_READ32(source);','const uint32_t word=RM_READ32(source+4u);')]
    negatives = {}
    for name, old, new in changes:
        if raw.count(old) != 1:
            raise ValueError('Exact mutant anchor mismatch: '+name)
        negatives[name] = compile_run(raw.replace(old,new), name)
    if any(sha(f) != before[str(f)] for f in inputs) or sha(compiler) != compiler_sha:
        raise ValueError('Input or compiler changed during review')
    receipt = {'schema':'TSL9-reset-memory-independent-code-review-v1','passed':True,'language':a.language,
               'compiler':str(compiler),'compiler_sha256':compiler_sha,'inputs_sha256':before,
               'positive':normal,'compiled_mutants':negatives,'compiled_mutants_rejected':len(negatives),
               'target_execution':False,'ISA_emulation':False,'physical_memory':False,'network':False,'OTA_ready':False}
    out = build/'verification.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'receipt':str(out),'sha256':sha(out),'tests':normal['result'],
                      'compiled_mutants_rejected':len(negatives)},sort_keys=True))

if __name__ == '__main__':
    main()
