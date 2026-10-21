#!/usr/bin/env python3
"""Owned host code only; reuse sealed independent synthetic fixtures."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

ORACLE_SHA='e40f4b8e986e705d6c8c29a34c793ce74d7c37a506e0ddedfecd80a1e2b783b4'
ORACLE_SEAL='4757434b52178f0394efe252688340c1be19f43a16708e1b70b4e1d0b453dce9'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def execute(argv,env,cwd,log,okay=True):
    r=subprocess.run([str(x) for x in argv],env=env,cwd=cwd,capture_output=True,
                     encoding='utf-8',errors='replace',timeout=90)
    log.write_text(r.stdout+r.stderr,encoding='utf-8')
    need(not okay or r.returncode==0,'Command failed; inspect '+str(log))
    return r
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--language',choices=['c','cpp'],required=True)
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    oldroots=[root.parent.parent/n/'code-review' for n in ('tsl9-v4160-placement-2026-10-21','v4160-placement-2026-10-21')]
    oldroots=[p for p in oldroots if (p/'final-audit.json').is_file()];need(len(oldroots)==1,'One known sealed independent oracle')
    old=oldroots[0];oracle=old/'independent-tests.c';need(sha(oracle)==ORACLE_SHA and sha(old/'final-audit.json')==ORACLE_SEAL,'Immutable independent fixture identity')
    for member in json.loads((old/'final-audit.json').read_text(encoding='utf-8'))['members']:
        target=(old/member['path']).resolve(strict=True);target.relative_to(old.resolve())
        need(sha(target)==member['sha256'] and target.stat().st_size==member['bytes'],'Immutable oracle evidence member')
    model=project/'experiments/tsl9-v4160-irq-native';prior=project/'experiments/tsl9-v4160-interrupt-registers'
    source=model/'src/interrupt_registers.c';header=model/'src/native_io.h';helper=project/'scripts/portable_verify.py'
    spec=importlib.util.spec_from_file_location('portable',helper);portable=importlib.util.module_from_spec(spec);spec.loader.exec_module(portable)
    compiler,env,msvc=portable.compiler_for(a.language)
    build=root/'build'/(uuid.uuid4().hex+'-'+a.language);build.mkdir(parents=True)
    inputs=[source,header,prior/'src/interrupt_registers.h',prior/'tests/test_io.h',oracle,old/'final-audit.json',helper,Path(__file__).resolve()]
    pins={str(p):sha(p) for p in inputs};compiler_sha=sha(compiler)
    flags=(['/nologo','/W4','/WX','/Od','/TP' if a.language=='cpp' else '/TC','/std:c++17' if a.language=='cpp' else '/std:c11',
            '/DTSL9_IRQ_REGISTERS_HOST_TEST=1','/Fo'+str(build)+os.sep]
           if msvc else ['-x','c++' if a.language=='cpp' else 'c','-std=c++17' if a.language=='cpp' else '-std=c11',
                         '-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_REGISTERS_HOST_TEST=1'])
    include=[model/'src',prior/'src',prior/'tests']
    flags+=['/I'+str(p) for p in include] if msvc else [x for p in include for x in ('-I',str(p))]
    def check(core_text,io_text,name):
        chosen=source
        if core_text is not None or io_text is not None:
            chosen=build/(name+'.c');text=source.read_text() if core_text is None else core_text
            if io_text is not None:
                io_name=name+'-native_io.h';(build/io_name).write_text(io_text,encoding='utf-8')
                text=text.replace('#include "native_io.h"','#include "'+io_name+'"')
            chosen.write_text(text,encoding='utf-8')
        exe=build/(name+('.exe' if os.name=='nt' else ''))
        argv=([compiler,*flags,chosen,oracle,'/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc
              else [compiler,*flags,chosen,oracle,'-o',exe])
        execute(argv,env,build,build/(name+'-compile.log'))
        result=execute([exe],env,build,build/(name+'-run.log'),okay=core_text is None and io_text is None)
        if core_text is None and io_text is None:
            tests=json.loads(result.stdout)
            need(tests=={'passed':True,'groups':4,'cases':3820,'checks':138312},'Complete independent coverage')
        else:
            need(result.returncode!=0 and 'FAIL ' in result.stderr,'Compiled mutant must reach assertion rejection: '+name)
            tests={'rejected':True,'exit_code':result.returncode,'failure':result.stderr.strip()}
        return {'executable':str(exe),'executable_sha256':sha(exe),'result':tests}
    positive=check(None,None,'positive');raw=source.read_text();io=header.read_text()
    changes=[
      ('enabled-only-one','if(enabled) {','if(enabled==1u) {',1),
      ('normalize-enabled','return ir_rcc_return(after,enabled,','return ir_rcc_return(after,enabled?1u:0u,',2),
      ('enabled-full-address','return ir_rcc_return(after,enabled,base,before);','return ir_rcc_return(after,enabled,base+offset,before);',1),
      ('disabled-full-address','return ir_rcc_return(after,enabled,before,base);','return ir_rcc_return(after,enabled,before,base+offset);',1),
      ('enabled-modified-residue','return ir_rcc_return(after,enabled,base,before);','return ir_rcc_return(after,enabled,base,after);',1),
      ('disabled-modified-residue','return ir_rcc_return(after,enabled,before,base);','return ir_rcc_return(after,enabled,after,base);',1),
      ('OR-becomes-AND','const uint32_t after=before|mask;','const uint32_t after=before&mask;',1),
      ('clear-becomes-OR','const uint32_t after=before&~mask;','const uint32_t after=before|~mask;',1),
      ('wrong-helper-offset','return update32(0x18u,mask,enabled);','return update32(0x1cu,mask,enabled);',1),
      ('truncate-dynamic-mask','IR_MASK_VALUE(value);','IR_MASK_VALUE(value&255u);',2),
      ('cached-branch-read','const uint32_t before=IR_READ32(base+offset);','static uint32_t cached=0u;static uint32_t have=0u;const uint32_t before=have?cached:IR_READ32(base+offset);cached=before;have=1u;',2),
      ('write-before-read','const uint32_t before=IR_READ32(base+offset);','IR_WRITE32(base+offset,0u);const uint32_t before=IR_READ32(base+offset);',2),
      ('wrong-word-width','IR_WRITE32(base+offset,after);','IR_WRITE8(base+offset,(uint8_t)after);',2),
      ('main-wrong-A0','return ir_init_return(result,0u,','return ir_init_return(result^1u,0u,',1),
      ('main-wrong-A1','return ir_init_return(result,0u,','return ir_init_return(result,1u,',1),
      ('main-wrong-A4','return ir_init_return(result,0u,UINT32_C(0x80),','return ir_init_return(result,0u,UINT32_C(0x20),',1),
      ('main-wrong-A5','return ir_init_return(result,0u,UINT32_C(0x80),UINT32_C(0xe000e000));','return ir_init_return(result,0u,UINT32_C(0x80),UINT32_C(0xe000e104));',1),
      ('wrong-CSR-set','IR_CSR_SET(0x88u);','IR_CSR_SET(0x80u);',1),
      ('CSR-clear-becomes-set','IR_CSR_CLEAR(0x88u);','IR_CSR_SET(0x88u);',1),
      ('drop-last-PFIC','IR_WRITE32(UINT32_C(0xe000e104),UINT32_C(0x80));','/* omitted last PFIC word write */',1)]
    negatives={}
    for name,old_text,new_text,count in changes:
        need(raw.count(old_text)==count,'Frozen source mutation anchor: '+name)
        negatives[name]=check(raw.replace(old_text,new_text),None,name)
    need(io.count('return a0;')==3,'Two host return bridges plus native commit bridge')
    first=io.replace('tsl9_ir_test_rcc_outputs(a0,a1,a4,a5);return a0;','tsl9_ir_test_rcc_outputs(a0,a1,a4,a5);return a0^1u;')
    need(first!=io,'Host RCC bridge anchor')
    negatives['host-RCC-bridge-return']=check(None,first,'host-RCC-bridge-return')
    second=io.replace('tsl9_ir_test_init_outputs(a0,a1,a4,a5);return a0;','tsl9_ir_test_init_outputs(a0,a1,a4,a5);return a0^1u;')
    need(second!=io,'Host initializer bridge anchor')
    negatives['host-init-bridge-return']=check(None,second,'host-init-bridge-return')
    need(all(sha(p)==pins[str(p)] for p in inputs) and sha(compiler)==compiler_sha,'Frozen inputs/compiler unchanged')
    receipt={'schema':'TSL9-irq-native-independent-host-review-v1','passed':True,'language':a.language,
             'compiler':str(compiler),'compiler_sha256':compiler_sha,'inputs_sha256':pins,
             'reused_oracle_sha256':ORACLE_SHA,'reused_oracle_seal_sha256':ORACLE_SEAL,'positive':positive,
             'compiled_behavior_mutants':negatives,'compiled_mutants_rejected':len(negatives),
             'host_only':True,'native_bridge_or_register_proof':False,'target_execution':False,
             'ISA_emulation':False,'network':False,'hardware':False,'OTA_ready':False}
    path=build/'verification.json';path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    out=root/'receipts';out.mkdir(exist_ok=True);selected=out/(build.name+'.json');selected.write_bytes(path.read_bytes())
    print(json.dumps({'passed':True,'receipt':str(selected),'receipt_sha256':sha(selected),
                      'tests':positive['result'],'compiled_mutants_rejected':len(negatives)},sort_keys=True))
if __name__=='__main__':main()
