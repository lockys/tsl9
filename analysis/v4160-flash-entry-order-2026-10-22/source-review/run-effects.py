#!/usr/bin/env python3
"""Fresh independent host oracle; every executable launch uses the reviewed guard."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import uuid

MODEL='experiments/tsl9-v4160-flash-entry-order'
OLD='experiments/tsl9-v4160-flash-native'
ORACLE='d2387b7983052b2b3b863223eaf3873e00435a1bd03b5833ba31a4c7ad569705'
GUARD='9c58f4ec67704d64ae8c72eb46c0cb05286e1e3558c21677594683b07f5977b9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project-root',type=Path,required=True);parser.add_argument('--language',choices=('c','cpp'),required=True);parser.add_argument('--build-root',type=Path);a=parser.parse_args()
    root=a.project_root.resolve(strict=True);here=Path(__file__).resolve().parent;model=root/MODEL
    guard_path=model/'verify_host.py';oldguard=root/OLD/'verify_host.py'
    need(sha(oldguard)==GUARD and guard_path.read_bytes().replace(MODEL.encode(),OLD.encode())==oldguard.read_bytes(),'New launcher differs from reviewed guarded launcher only by model path')
    guard=module('entry_order_guarded_host',guard_path)
    helper=root/'scripts/portable_verify.py';tools=module('entry_order_host_compiler',helper)
    oracle=here/'expected-effects.c';need(sha(oracle)==ORACLE,'Exact immutable independent expected-effect fixture')
    inputs=[*sorted((model/'src').glob('*')),oracle,guard_path,oldguard,helper,Path(__file__).resolve()]
    before={str(p):sha(p) for p in inputs if p.is_file()}
    compiler,env,msvc=tools.compiler_for(a.language);compiler_pin=sha(compiler)
    build=(a.build_root or here/'build'/('effects-'+uuid.uuid4().hex+'-'+a.language)).resolve();build.relative_to(here);need(not build.exists(),'Create-only owned independent build root');build.mkdir(parents=True)
    env=dict(env);env['TMP']=str(build);env['TEMP']=str(build)
    def check(name,file=None,anchor=None,replacement=None,count=1):
        folder=build/name;folder.mkdir();source=folder/'src';source.mkdir()
        for p in (model/'src').glob('*'):
            if p.is_file():(source/p.name).write_bytes(p.read_bytes())
        if file:
            target=source/file;text=target.read_text(encoding='utf-8');need(text.count(anchor)==count,'Exact bounded source mutation '+name);target.write_bytes(text.replace(anchor,replacement).encode('utf-8'))
        exe=folder/('test.exe' if os.name=='nt' else 'test')
        flags=(['/nologo','/W4','/WX','/Od','/TP' if a.language=='cpp' else '/TC','/std:c++17' if a.language=='cpp' else '/std:c11','/DTSL9_FLASH_HOST_TEST=1','/I'+str(source),'/Fo'+str(folder)+os.sep] if msvc else ['-x','c++' if a.language=='cpp' else 'c','-std=c++17' if a.language=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_FLASH_HOST_TEST=1','-I',source])
        argv=[compiler,*flags,source/'flash_native.c',source/'host_io.c',oracle]
        argv+=['/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc else ['-o',exe]
        compile_row,_=guard.execute(argv,folder,'compile',env)
        run_row,text=guard.execute([exe],folder,'tests',env,expect=1 if file else 0,host_test=True)
        output=(folder/'tests.log').read_text(encoding='utf-8',errors='replace')
        if file:need('REVIEW_FAIL ' in output,'Compiled mutant fails an independent semantic assertion');result={'rejected':True,'exit':run_row['exit']}
        else:
            result=json.loads(text);need(result=={'passed':True,'groups':1,'cases':12,'checks':8964,'synthetic_effects_only':True},'Exact independent twelve-scenario coverage')
        return {'case':name,'mutation_file':file,'anchor':anchor,'replacement':replacement,'anchor_count':count,'result':result,'commands':[compile_row,run_row],'executable_sha256':sha(exe),'artifacts':{p.relative_to(folder).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in folder.rglob('*') if p.is_file()}}
    positive=check('positive')
    controls=[
      ('unlock-key-order','flash_native.c','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key1);','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key2);'),
      ('status-not49','flash_native.c','FN_CALL_STATUS(FN_K(49u))','FN_CALL_STATUS(FN_K(48u))'),
      ('align128-host-macro','native_io.h','#define FN_ALIGN0(v) FN_AND((v),FN_K(0xffffff00u))','#define FN_ALIGN0(v) FN_AND((v),FN_K(0xffffff80u))'),
      ('erase-wrong-final-mask','flash_native.c','FN_MASK3(0xfffdffffu)','FN_MASK3(0xfffeffffu)'),
      ('program-wrong-mode','flash_native.c','FN_MASK3(0x10000u)','FN_MASK3(0x20000u)'),
      ('write-before-source-read','flash_native.c','FN_READ(0x18f1eu,FN_ADD(source,FN_K(offset)),last_word);','FN_WRITE(0x18f26u,FN_ADD(destination,FN_K(offset)),FN_K(0u));FN_READ(0x18f1eu,FN_ADD(source,FN_K(offset)),last_word);'),
      ('per-word-poll-wrong-bit','flash_native.c','FN_POLL_TRUE(0x18f2eu,status,2u)','FN_POLL_TRUE(0x18f2eu,status,1u)'),
      ('cached-CTRL-before-commit','flash_native.c','FN_READ(0x18f36u,FN_ADD(base,FN_K(16u)),before);','/* omitted required fresh CTRL read */'),
      ('status-return-zero','flash_native.c','FN_RET_STATUS(status,base)','FN_RET_STATUS(FN_K(0u),base)'),
      ('lock-wrong-A5','flash_native.c','FN_RET_UNLOCK(incoming_a0,mask,base,after)','FN_RET_UNLOCK(incoming_a0,mask,base,before)'),
      ('stride8','flash_native.c','offset+=4u;','offset+=8u;'),
      ('cached-frame-source','flash_native.c','FN_FRAME_RELOAD(source);','/* removed fresh frame source reload */')]
    negatives=[check(*control) for control in controls]
    need(all(sha(Path(p))==pin for p,pin in before.items()) and sha(compiler)==compiler_pin,'Unchanged core/oracle/runner/compiler before and after actual host execution')
    receipt={'schema':'ID2966-entry-order-independent-effects-v1','passed':True,'language':a.language,'input_pins':before,'compiler':{'path':str(compiler),'sha256':compiler_pin},'guard_runner_sha256':sha(guard_path),'guard_normalized_old_runner_sha256':GUARD,'oracle_sha256':ORACLE,'positive':positive,'actually_compiled_mutants':negatives,'actual_mutants_rejected':12,'host_executables_guarded':13,'target_execution':False,'ISA_emulation':False,'hardware':False,'network':False,'native_register_prefix_proved':False}
    encoded=(json.dumps(receipt,indent=2)+'\n').encode('utf-8');(build/'verification.json').write_bytes(encoded)
    selected=here/'receipts'/('effects-'+build.name+'.json');selected.parent.mkdir(exist_ok=True);need(not selected.exists(),'Create-only selected receipt');selected.write_bytes(encoded)
    print(json.dumps({'passed':True,'receipt':str(selected),'sha256':sha(selected),'tests':positive['result'],'actual_compiled_mutants':12,'guarded_executables':13,'target_execution':False}))
if __name__=='__main__':main()
