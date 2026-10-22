#!/usr/bin/env python3
"""Compile only owned host C/C++ using a sealed independent synthetic oracle."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

ORACLE_SHA='e40f4b8e986e705d6c8c29a34c793ce74d7c37a506e0ddedfecd80a1e2b783b4'
ORACLE_SEAL='cf4881fc4618d32fa3d982659f733b649a4bee1445ffa52232feb249cbfed279'
EXPECTED={'passed':True,'groups':4,'cases':3820,'checks':138312}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def execute(argv,env,cwd,log,okay=True):
    r=subprocess.run([str(x) for x in argv],env=env,cwd=cwd,capture_output=True,encoding='utf-8',errors='replace',timeout=90)
    log.write_text(r.stdout+r.stderr,encoding='utf-8')
    need(not okay or r.returncode==0,'Command failed; inspect '+str(log))
    return r
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--language',choices=['c','cpp'],required=True)
    a=p.parse_args();project=a.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    candidates=[root.parent.parent/n/'code-review' for n in ('tsl9-v4160-placement-2026-10-21','v4160-placement-2026-10-21')]
    candidates=[p for p in candidates if (p/'final-audit.json').is_file()]
    need(len(candidates)==1,'One sealed independent oracle layout');old=candidates[0];oracle=old/'independent-tests.c'
    need(sha(oracle)==ORACLE_SHA and sha(old/'final-audit.json')==ORACLE_SEAL,'Independent oracle identity')
    for m in json.loads((old/'final-audit.json').read_text(encoding='utf-8'))['members']:
        q=(old/m['path']).resolve(strict=True);q.relative_to(old.resolve())
        need(sha(q)==m['sha256'] and q.stat().st_size==m['bytes'],'Oracle sealed member')
    model=project/'experiments/tsl9-v4160-irq-callframe';prior=project/'experiments/tsl9-v4160-interrupt-registers'
    native=project/'experiments/tsl9-v4160-irq-native'
    source=model/'src/interrupt_callframe.c';helpers=model/'src/rcc_helpers.c';header=model/'src/callframe_io.h'
    portable_path=project/'scripts/portable_verify.py'
    spec=importlib.util.spec_from_file_location('portable',portable_path);portable=importlib.util.module_from_spec(spec);spec.loader.exec_module(portable)
    compiler,env,msvc=portable.compiler_for(a.language)
    build=root/'build'/(uuid.uuid4().hex+'-'+a.language);build.mkdir(parents=True)
    inputs=[source,helpers,header,native/'src/native_io.h',prior/'src/interrupt_registers.h',prior/'tests/test_io.h',oracle,old/'final-audit.json',portable_path,Path(__file__).resolve()]
    pins={str(p):sha(p) for p in inputs};compiler_sha=sha(compiler)
    flags=(['/nologo','/W4','/WX','/Od','/TP' if a.language=='cpp' else '/TC','/std:c++17' if a.language=='cpp' else '/std:c11','/DTSL9_IRQ_REGISTERS_HOST_TEST=1','/Fo'+str(build)+os.sep] if msvc else ['-x','c++' if a.language=='cpp' else 'c','-std=c++17' if a.language=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_IRQ_REGISTERS_HOST_TEST=1'])
    includes=[model/'src',native/'src',prior/'src',prior/'tests']
    flags+=['/I'+str(p) for p in includes] if msvc else [x for p in includes for x in ('-I',str(p))]
    def check(name,main_text=None,helper_text=None,header_text=None):
        main_file=source;helper_file=helpers;mutant=any(x is not None for x in (main_text,helper_text,header_text))
        if main_text is not None or header_text is not None:
            main_file=build/(name+'-main.c');text=source.read_text() if main_text is None else main_text
            if header_text is not None:
                hn=name+'-callframe_io.h';(build/hn).write_text(header_text,encoding='utf-8');text=text.replace('#include "callframe_io.h"','#include "'+hn+'"')
            main_file.write_text(text,encoding='utf-8')
        if helper_text is not None:
            helper_file=build/(name+'-helpers.c');helper_file.write_text(helper_text,encoding='utf-8')
        exe=build/(name+('.exe' if os.name=='nt' else ''))
        command=([compiler,*flags,main_file,helper_file,oracle,'/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc else [compiler,*flags,main_file,helper_file,oracle,'-o',exe])
        execute(command,env,build,build/(name+'-compile.log'))
        r=execute([exe],env,build,build/(name+'-run.log'),okay=not mutant)
        if mutant:
            need(r.returncode!=0 and 'FAIL ' in r.stderr,'Compiled behavior rejection: '+name)
            result={'rejected':True,'exit_code':r.returncode,'failure':r.stderr.strip()}
        else:
            result=json.loads(r.stdout);need(result==EXPECTED,'Complete independent coverage')
        return {'executable':str(exe),'executable_sha256':sha(exe),'result':result}
    positive=check('positive');raw=source.read_text();hraw=helpers.read_text();io=header.read_text()
    changes=[
      ('wrong-first-call','main','CF_CALL(tsl9_rebuild_rcc_registers_19142,CF_FAST_MASK(),1u)','CF_CALL(tsl9_rebuild_rcc_registers_19124,CF_FAST_MASK(),1u)',1),
      ('wrong-call-order','main','CF_CALL(tsl9_rebuild_rcc_registers_19124,CF_SLOW_MASK(),1u);\n    (void)CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),1u)','CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),1u);\n    (void)CF_CALL(tsl9_rebuild_rcc_registers_19124,CF_SLOW_MASK(),1u)',1),
      ('reset-call-enabled','main','CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),0u)','CF_CALL(tsl9_rebuild_rcc_registers_1917e,CF_FAST_MASK(),1u)',1),
      ('last-clear-wrong-helper','main','CF_FINAL_CLEAR(tsl9_rebuild_rcc_registers_19160,','CF_FINAL_CLEAR(tsl9_rebuild_rcc_registers_19124,',1),
      ('main-result-corruption','main','CF_RETURN(result)','CF_RETURN(result^1u)',1),
      ('drop-CSR-clear','main','CF_CSR_CLEAR();','/* omitted CSR clear */',1),
      ('drop-CSR-set','main','CF_CSR_SET();','/* omitted CSR set */',1),
      ('PFIC-wrong-zero-address','main','CF_ZERO8(0x42du)','CF_ZERO8(0x42cu)',1),
      ('PFIC-word-as-byte','main','CF_WRITE32(0x104u,0x2000u)','CF_WRITE8(0x104u,0x20u)',1),
      ('PFIC-byte-as-word','main','CF_WRITE8(0x424u,0x20u)','CF_WRITE32(0x424u,0x20u)',1),
      ('PFIC-last-mask','main','CF_WRITE32(0x104u,0x80u)','CF_WRITE32(0x104u,0x40u)',1),
      ('enabled-only-one','helpers','if(enabled) {','if(enabled==1u) {',1),
      ('normalize-enabled','helpers','return ir_rcc_return(after,enabled,','return ir_rcc_return(after,enabled?1u:0u,',2),
      ('enabled-full-address','helpers','return ir_rcc_return(after,enabled,base,before);','return ir_rcc_return(after,enabled,base+offset,before);',1),
      ('disabled-full-address','helpers','return ir_rcc_return(after,enabled,before,base);','return ir_rcc_return(after,enabled,before,base+offset);',1),
      ('enabled-after-residue','helpers','return ir_rcc_return(after,enabled,base,before);','return ir_rcc_return(after,enabled,base,after);',1),
      ('disabled-after-residue','helpers','return ir_rcc_return(after,enabled,before,base);','return ir_rcc_return(after,enabled,after,base);',1),
      ('mask-truncated','helpers','IR_MASK_VALUE(value);','IR_MASK_VALUE(value&255u);',2),
      ('cache-branch-read','helpers','const uint32_t before=IR_READ32(base+offset);','static uint32_t saved=0u;static uint32_t seen=0u;const uint32_t before=seen?saved:IR_READ32(base+offset);saved=before;seen=1u;',2),
      ('write-before-read','helpers','const uint32_t before=IR_READ32(base+offset);','IR_WRITE32(base+offset,0u);const uint32_t before=IR_READ32(base+offset);',2),
      ('helper-wrong-width','helpers','IR_WRITE32(base+offset,after);','IR_WRITE8(base+offset,(uint8_t)after);',2),
      ('clear-as-OR','helpers','const uint32_t after=before&~mask;','const uint32_t after=before|~mask;',1),
      ('fast-mask','header','(cf_fast+6u)','(cf_fast+7u)',1),
      ('slow-mask','header','(cf_slow+29u)','(cf_slow+28u)',1),
      ('final-call-enabled','header','#define CF_FINAL_CLEAR(name,mask) name((mask),0u)','#define CF_FINAL_CLEAR(name,mask) name((mask),1u)',1),
      ('host-return-value','header','ir_init_return((value),0u,0x80u,UINT32_C(0xe000e000))','(ir_init_return((value),0u,0x80u,UINT32_C(0xe000e000))^1u)',1),
      ('host-output-A1','header','ir_init_return((value),0u,0x80u,','ir_init_return((value),1u,0x80u,',1),
      ('host-output-A4','header','ir_init_return((value),0u,0x80u,','ir_init_return((value),0u,0x40u,',1),
      ('host-output-A5','header','ir_init_return((value),0u,0x80u,UINT32_C(0xe000e000))','ir_init_return((value),0u,0x80u,UINT32_C(0xe000e104))',1),
      ('CSR-mask','header','uint32_t cf_csr=0x88u','uint32_t cf_csr=0x80u',1)]
    negatives={}
    for name,part,anchor,replacement,count in changes:
        text={'main':raw,'helpers':hraw,'header':io}[part];need(text.count(anchor)==count,'Frozen mutation anchor: '+name)
        kw={'main':'main_text','helpers':'helper_text','header':'header_text'}[part]
        negatives[name]=check(name,**{kw:text.replace(anchor,replacement)})
    need(all(sha(p)==pins[str(p)] for p in inputs) and sha(compiler)==compiler_sha,'Frozen inputs/compiler unchanged')
    receipt={'schema':'TSL9-irq-callframe-independent-host-review-v1','passed':True,'language':a.language,'compiler':str(compiler),'compiler_sha256':compiler_sha,'inputs_sha256':pins,'reused_oracle_sha256':ORACLE_SHA,'reused_oracle_seal_sha256':ORACLE_SEAL,'positive':positive,'compiled_behavior_mutants':negatives,'compiled_mutants_rejected':len(negatives),'actual_source_translation_units':2,'host_only':True,'native_bridge_or_register_proof':False,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'OTA_ready':False}
    path=build/'verification.json';path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    out=root/'receipts';out.mkdir(exist_ok=True);selected=out/(build.name+'.json');selected.write_bytes(path.read_bytes())
    print(json.dumps({'passed':True,'receipt':str(selected),'receipt_sha256':sha(selected),'tests':positive['result'],'compiled_mutants_rejected':len(negatives)},sort_keys=True))
if __name__=='__main__':main()
