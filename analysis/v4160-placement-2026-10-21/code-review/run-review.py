#!/usr/bin/env python3
"""Independent host-only register-boundary behavior tests and compiled mutations."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def execute(argv,env,cwd,log,require_success=True):
    r=subprocess.run([str(x) for x in argv],env=env,cwd=cwd,capture_output=True,
                     encoding='utf-8',errors='replace',timeout=90)
    log.write_text(r.stdout+r.stderr,encoding='utf-8')
    if require_success and r.returncode:
        raise ValueError('Command failed: '+str(log))
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--language',choices=['c','cpp'],required=True)
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    model=project/'experiments/tsl9-v4160-interrupt-registers';source=model/'src/interrupt_registers.c'
    helper=project/'scripts/portable_verify.py'
    spec=importlib.util.spec_from_file_location('portable',helper);portable=importlib.util.module_from_spec(spec);spec.loader.exec_module(portable)
    compiler,env,msvc=portable.compiler_for(a.language)
    build=root/'build'/(uuid.uuid4().hex+'-'+a.language);build.mkdir(parents=True)
    selected=[source,model/'src/interrupt_registers.h',model/'src/irq_io.h',model/'tests/test_io.h',
              root/'independent-tests.c',Path(__file__).resolve(),helper]
    pins={str(p):sha(p) for p in selected};compiler_sha=sha(compiler)
    flags=(['/nologo','/W4','/WX','/Od','/TP' if a.language=='cpp' else '/TC',
            '/std:c++17' if a.language=='cpp' else '/std:c11','/DTSL9_IRQ_REGISTERS_HOST_TEST=1','/Fo'+str(build)+os.sep]
           if msvc else ['-x','c++' if a.language=='cpp' else 'c','-std=c++17' if a.language=='cpp' else '-std=c11',
                         '-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_REGISTERS_HOST_TEST=1'])
    flags+=(['/I'+str(model/'src'),'/I'+str(model/'tests')] if msvc else ['-I',str(model/'src'),'-I',str(model/'tests')])
    def check(text,name):
        chosen=source
        if text is not None:
            chosen=build/(name+'.c');chosen.write_text(text,encoding='utf-8')
        executable=build/(name+('.exe' if os.name=='nt' else ''))
        cmd=([compiler,*flags,chosen,root/'independent-tests.c','/Fe'+str(executable),'/link','/INCREMENTAL:NO'] if msvc
             else [compiler,*flags,chosen,root/'independent-tests.c','-o',executable])
        execute(cmd,env,build,build/(name+'-compile.log'))
        run=execute([executable],env,build,build/(name+'-run.log'),require_success=text is None)
        if text is None:
            result=json.loads(run.stdout)
            if not result.get('passed') or result['groups']!=4 or result['cases']!=3820:
                raise ValueError('Independent coverage mismatch')
        else:
            if run.returncode==0 or 'FAIL ' not in run.stderr:
                raise ValueError('Compiled mutation did not reach assertion rejection: '+name)
            result={'rejected':True,'exit_code':run.returncode,'failure':run.stderr.strip()}
        return {'executable':str(executable),'executable_sha256':sha(executable),'result':result}
    positive=check(None,'positive');raw=source.read_text()
    changes=[
      ('normalize-enabled','IR_RCC_OUTPUTS(after,enabled,','IR_RCC_OUTPUTS(after,enabled?1u:0u,',2),
      ('only-enabled-one','enabled?(before|mask):(before&~mask)','enabled==1u?(before|mask):(before&~mask)',1),
      ('enabled-A4-full-address','IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),before);','IR_RCC_OUTPUTS(after,enabled,address,before);',1),
      ('disabled-A5-full-address','IR_RCC_OUTPUTS(after,enabled,before,UINT32_C(0x40021000));','IR_RCC_OUTPUTS(after,enabled,before,address);',1),
      ('enabled-A5-after','IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),before);','IR_RCC_OUTPUTS(after,enabled,UINT32_C(0x40021000),after);',1),
      ('disabled-A4-after','IR_RCC_OUTPUTS(after,enabled,before,UINT32_C(0x40021000));','IR_RCC_OUTPUTS(after,enabled,after,UINT32_C(0x40021000));',1),
      ('wrong-helper-address','return update32(UINT32_C(0x40021018),mask,enabled);','return update32(UINT32_C(0x4002101c),mask,enabled);',1),
      ('cached-read','const uint32_t before=IR_READ32(address);','static uint32_t old=0u;static uint32_t have=0u;const uint32_t before=have?old:IR_READ32(address);old=before;have=1u;',1),
      ('write-before-read','const uint32_t before=IR_READ32(address);','IR_WRITE32(address,0u);const uint32_t before=IR_READ32(address);',1),
      ('wrong-write-width','IR_WRITE32(address,after);','IR_WRITE8(address,(uint8_t)after);',1),
      ('main-wrong-A0','IR_INIT_OUTPUTS(result,0u,','IR_INIT_OUTPUTS(result^1u,0u,',1),
      ('main-wrong-A1','IR_INIT_OUTPUTS(result,0u,','IR_INIT_OUTPUTS(result,1u,',1),
      ('main-wrong-A4','IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),','IR_INIT_OUTPUTS(result,0u,UINT32_C(0x20),',1),
      ('main-wrong-A5','IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));','IR_INIT_OUTPUTS(result,0u,UINT32_C(0x80),UINT32_C(0xe000e104));',1),
      ('main-wrong-return','return result;','return result^1u;',1),
      ('main-wrong-CSR-set','IR_CSR_SET(UINT32_C(0x88));','IR_CSR_SET(UINT32_C(0x80));',1),
      ('main-clear-becomes-set','IR_CSR_CLEAR(UINT32_C(0x88));','IR_CSR_SET(UINT32_C(0x88));',1),
      ('main-drop-last-PFIC','IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x80));','/* omitted final original PFIC write */',1)]
    mutants={}
    for name,old,new,count in changes:
        if raw.count(old)!=count:raise ValueError('Mutant anchor mismatch: '+name)
        mutants[name]=check(raw.replace(old,new),name)
    if any(sha(p)!=pins[str(p)] for p in selected) or sha(compiler)!=compiler_sha:
        raise ValueError('Frozen source/input/compiler changed')
    receipt={'schema':'TSL9-interrupt-registers-independent-behavior-review-v1','passed':True,'language':a.language,
             'compiler':str(compiler),'compiler_sha256':compiler_sha,'input_sha256':pins,'positive':positive,
             'actually_compiled_mutants':mutants,'compiled_mutants_rejected':len(mutants),
             'host_boundary_outputs_only':True,'actual_A2_A3_preservation_proved':False,
             'native_entry_IRQ_ABI_proved':False,'target_execution':False,'ISA_emulation':False,
             'network':False,'hardware':False,'OTA_ready':False}
    path=build/'verification.json';path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    selected_dir=root/'receipts';selected_dir.mkdir(exist_ok=True)
    destination=selected_dir/(build.name+'.json')
    destination.write_bytes(path.read_bytes())
    print(json.dumps({'passed':True,'receipt':str(destination),'receipt_sha256':sha(destination),
                      'tests':positive['result'],'compiled_mutants_rejected':len(mutants)},sort_keys=True))

if __name__=='__main__':main()
