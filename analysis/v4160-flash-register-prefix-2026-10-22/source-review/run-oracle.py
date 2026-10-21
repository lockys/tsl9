#!/usr/bin/env python3
"""One positive independent host oracle per language; every launch is host-guarded."""
import argparse
import ast
import importlib.util
import json
import os
from pathlib import Path
import uuid
import frontier as F

HERE=Path(__file__).resolve().parent
ORACLE='d2387b7983052b2b3b863223eaf3873e00435a1bd03b5833ba31a4c7ad569705'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def guarded_source(old,new):
    F.need(F.sha(old)=='be7ad39a8f05003bbba371d11f4f2337338165dbc5f9700ce3d7c50a2878659f','Immutable reviewed host executable guard')
    names={'sha','need','host_architecture','host_executable','execute'}
    def bodies(path):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(x,ast.FunctionDef) and x.name in names}
    a=bodies(old);b=bodies(new);F.need(set(a)==names and a==b,'Actual current host guard closure matches reviewed function ASTs')
def run(root,mode,build):
    model=root/'experiments/tsl9-v4160-flash-register-prefix';runner=model/'verify_host.py';old=root/'experiments/tsl9-v4160-flash-native/verify_host.py';guarded_source(old,runner);guard=module('prefix_guarded_host',runner);helper=root/'scripts/portable_verify.py';tools=module('prefix_host_compiler',helper);oracle=HERE/'expected-effects.c';F.need(F.sha(oracle)==ORACLE,'Exact retained independent twelve-scenario oracle')
    inputs=[*sorted((model/'src').glob('*')),oracle,runner,old,helper,Path(__file__).resolve()];before={str(p):F.sha(p) for p in inputs if p.is_file()};compiler,env,msvc=tools.compiler_for(mode);compiler=Path(compiler);compiler_pin=F.sha(compiler)
    F.need(not build.exists(),'Create-only independent positive host build');build.mkdir(parents=True);env=dict(env);env['TMP']=str(build);env['TEMP']=str(build);exe=build/('test.exe' if os.name=='nt' else 'test');source=model/'src'
    flags=(['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_FLASH_HOST_TEST=1','/I'+str(source),'/Fo'+str(build)+os.sep] if msvc else ['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_FLASH_HOST_TEST=1','-I',source])
    argv=[compiler,*flags,source/'flash_native.c',source/'host_io.c',oracle];argv+=['/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc else ['-o',exe]
    compile_row,unused=guard.execute(argv,build,'compile',env);run_row,text=guard.execute([exe],build,'tests',env,host_test=True);result=json.loads(text);F.need(result=={'passed':True,'groups':1,'cases':12,'checks':8964,'synthetic_effects_only':True},'Actual complete independent positive oracle')
    F.need(all(F.sha(Path(p))==pin for p,pin in before.items()) and F.sha(compiler)==compiler_pin,'Unchanged exact source/oracle/runner/compiler inputs')
    r={'schema':'ID2966-prefix-independent-positive-host-v1','passed':True,'mode':mode,'input_pins':before,'compiler':{'path':str(compiler),'sha256':compiler_pin},'commands':[compile_row,run_row],'result':result,'actual_fresh_independent_semantic_mutants':0,'historical_oracle_bytes_reused':True,'host_executable_guard_checked_before_launch':True,'host_executable_sha256':F.sha(exe),'artifacts':{p.relative_to(build).as_posix():{'bytes':p.stat().st_size,'sha256':F.sha(p)} for p in build.rglob('*') if p.is_file()},'target_execution':False,'ISA_emulation':False,'hardware':False,'network':False,'physical_native_register_prefix_proved':False}
    payload=(json.dumps(r,indent=2)+'\n').encode('utf-8');(build/'verification.json').write_bytes(payload);selected=HERE/'receipts'/('host-'+mode+'.json');selected.parent.mkdir(exist_ok=True);F.need(not selected.exists(),'Create-only selected positive host receipt');selected.write_bytes(payload);return selected,r
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--language',choices=('c','cpp'),required=True);p.add_argument('--build-root',type=Path);a=p.parse_args();build=(a.build_root or HERE/'build'/('host-'+uuid.uuid4().hex+'-'+a.language)).resolve();build.relative_to(HERE);selected,r=run(a.project_root.resolve(),a.language,build);print(json.dumps({'passed':True,'receipt':str(selected),'sha256':F.sha(selected),'tests':r['result'],'fresh_independent_semantic_mutants':0}))
if __name__=='__main__':main()
