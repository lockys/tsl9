#!/usr/bin/env python3
"""Independent compiled host tests; original RV32 is never executed."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MODEL=ROOT/'experiments/tsl9-v4160-interrupt-init'
HELPER=ROOT/'scripts/portable_verify.py'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(okay,message):
    if not okay:raise RuntimeError(message)

def source_evidence():
    seal_path=HERE.parent/'abi-review/final-audit.json'
    need(sha(seal_path)=='0ff5d04207572f5f0cb9e4168de5583f28e15901938b47428d1664d90b26451a','ABI source seal identity')
    seal=json.loads(seal_path.read_text())
    for member in seal['members']:
        p=seal_path.parent/member['path']
        need(p.stat().st_size==member['bytes'] and sha(p)==member['sha256'],'ABI sealed member')
    facts=json.loads((seal_path.parent/'verification.json').read_text(encoding='utf-8-sig'))
    need(facts['passed'] and facts['byte_count']==264 and facts['instruction_count']==94,'Exact raw source scope')
    need(facts['source_sha256']=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Original runtime identity')
    return seal_path,seal,facts

def run(mode):
    seal_path,seal,facts=source_evidence()
    spec=importlib.util.spec_from_file_location('review_portable_tools',HELPER)
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    compiler,environment,msvc=tool.compiler_for(mode)
    build=HERE/'build'/('independent-'+uuid.uuid4().hex+'-'+mode);build.mkdir(parents=True)
    source=MODEL/'src/interrupt_init.c'
    pins=[source,MODEL/'src/interrupt_init.h',MODEL/'tests/test_io.h',MODEL/'tests/test_interrupt_init.c',MODEL/'verify.py',HELPER,HERE/'audit.py',HERE/'test_io.h',HERE/'test_independent.c',seal_path]
    pins += [seal_path.parent/m['path'] for m in seal['members']]
    before={p:sha(p) for p in pins};compiler_before=sha(Path(compiler))
    original=source.read_text(encoding='utf-8')
    variants={
        'original':original,
        'cached-read':original.replace('const uint32_t before=read32(address);','static uint32_t cached;\n    const uint32_t before=enabled?(cached=read32(address)):cached;'),
        'restore-csr':original.replace('uint32_t result;','uint32_t result;\n    const uint32_t saved_csr=tsl9_review_csr_snapshot();').replace('tsl9_test_csr_set(mask);','tsl9_review_csr_restore(mask);').replace('set_csr800(UINT32_C(0x88));','set_csr800(saved_csr);'),
        'wrong-write-width':original.replace('write8(UINT32_C(0xe000e424),UINT8_C(0x20));','write32(UINT32_C(0xe000e424),UINT32_C(0x20));'),
    }
    need(all(v!=original for k,v in variants.items() if k!='original'),'Each compiled mutant actually changes C')
    results=[]
    for name,contents in variants.items():
        folder=build/name;folder.mkdir();mutant=folder/'interrupt_init.c';mutant.write_text(contents,encoding='utf-8')
        exe=folder/('test.exe' if os.name=='nt' else 'test')
        includes=[MODEL/'src',HERE]
        if msvc:
            flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_IRQ_HOST_TEST=1','/Fo'+str(folder)+os.sep]+['/I'+str(p) for p in includes]
            command=[compiler,*flags,mutant,HERE/'test_independent.c','/Fe'+str(exe),'/link','/INCREMENTAL:NO']
        else:
            flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_HOST_TEST=1']+[x for p in includes for x in ('-I',str(p))]
            command=[compiler,*flags,mutant,HERE/'test_independent.c','-o',exe]
        tool.run(command,cwd=folder,env=environment,log=folder/'compiler.log')
        need(exe.is_file(),'Actual compiled executable exists')
        proc=subprocess.run([str(exe)],cwd=folder,env=environment,capture_output=True,text=True,timeout=30)
        (folder/'stdout.txt').write_text(proc.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(proc.stderr,encoding='utf-8')
        if name=='original':
            need(proc.returncode==0,'Original reconstruction passes independent behavior suite')
            tests=json.loads(proc.stdout);need(tests['passed'] and tests['groups']==4 and tests['checks']>20000,'Complete independent test groups')
        else:
            need(proc.returncode==17 and 'REVIEW_FAIL ' in proc.stderr,'Compiled mutant rejected by runtime assertions')
            tests={'rejected':True,'failure':proc.stderr.strip()}
        results.append(dict(variant=name,compiled=True,exit_code=proc.returncode,tests=tests,source_sha256=sha(mutant),executable_sha256=sha(exe),compile_flags=flags,compiler_log_sha256=sha(folder/'compiler.log')))
    need(all(sha(p)==h for p,h in before.items()),'Inputs immutable during compiled review')
    need(sha(Path(compiler))==compiler_before,'Compiler immutable during compiled review')
    receipt=dict(schema='TSL9-readable-interrupt-init-independent-review-v1',passed=True,mode=mode,source_sha256={str(p.relative_to(ROOT)):h for p,h in before.items()},compiler=str(compiler),compiler_sha256=compiler_before,variants=results,original_source_bytes=facts['byte_count'],original_source_instructions=facts['instruction_count'],source_executed=False,ISA_emulated=False,physical_IO=False,native_component_ABI_proved=False,OTA_ready=False)
    out=build/'verification.json';out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return dict(mode=mode,passed=True,receipt=str(out.relative_to(ROOT)),sha256=sha(out),tests=results[0]['tests'],compiled_negatives=3)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--language',choices=['c','cpp','both'],default='both');args=parser.parse_args()
    results=[]
    for mode in (['c','cpp'] if args.language=='both' else [args.language]):
        item=run(mode);results.append(item);print('INDEPENDENT_REVIEW_RESULT '+json.dumps(item),flush=True)
    print(json.dumps(dict(passed=True,results=results,OTA_ready=False)))

if __name__=='__main__':
    main()
