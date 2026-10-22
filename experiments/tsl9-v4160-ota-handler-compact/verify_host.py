#!/usr/bin/env python3
"""Small synthetic HOST suite; immutable native-machine guard before every run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import uuid
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-handler-compact'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GPIN='76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189'
EXPECTED=dict(groups=1,cases=10,checks=8292)
MUTATIONS=[('UID_zero_result','if(a[0])return;\n        OH_READ(h,0x9d40','if(!a[0])return;\n        OH_READ(h,0x9d40'),
 ('Flash_before_RAM','OH_READ(h,0x9d10,s->flash+offset,32,flash_word);\n            OH_READ(h,0x9d16,s->source+offset,32,source_word);','OH_READ(h,0x9d16,s->source+offset,32,source_word);\n            OH_READ(h,0x9d10,s->flash+offset,32,flash_word);'),
 ('R_no_W_range_guard','a[0]=s->context;a[1]=0x52u;a[2]=second|(first<<8);','a[0]=s->context;a[1]=0x52u;a[2]=second|(first<<8);if(a[2]>27u)return;')]
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def compile_args(cc,msvc,mode,source,where):
    exe=where/('tests.exe' if os.name=='nt' else 'tests');files=[source/'src/ota_handler.c',source/'src/host_io.c',source/'tests/smoke.c']
    if msvc:return [cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DOH_HOST=1','/I'+str(source/'src'),'/Fo'+str(where)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
    return [cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DOH_HOST=1','-I',source/'src',*files,'-o',exe]
def inputs(root):
    model=root/MODEL
    paths=[Path(__file__).resolve(),root/GUARD,root/'scripts/portable_verify.py',*model.joinpath('src').glob('*'),*model.joinpath('tests').glob('*')]
    return {str(p.resolve()):H(p) for p in paths if p.is_file()}
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=read(receipt);model=root/MODEL
    need(H(root/GUARD)==GPIN,'Immutable HOST executable guard');g=runpy.run_path(str(root/GUARD))
    need(r['passed'] and r['source_pins']==inputs(root),'Current exact HOST runner/source/helper identity')
    need(set(r['artifacts'])=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual HOST artifact inventory')
    for name,pin in r['artifacts'].items():
        path=(folder/name).resolve();need(path.is_relative_to(folder) and path.stat().st_size==pin['bytes'] and H(path)==pin['sha256'],'Actual HOST artifact bytes')
    cc=Path(r['compiler']['path']);need(H(cc)==r['compiler']['sha256'],'Actual compiler identity')
    need(r['tests']==read(folder/'tests.log')==EXPECTED,'Exact selected10-case HOST result')
    need(len(r['commands'])==8 and len(r['compiled_controls'])==3,'Positive+three actual negative launch pairs')
    variants=[(folder,model,False)]+[(folder/name,folder/name/'model',True) for name,_,_ in MUTATIONS]
    for i,(where,source,negative) in enumerate(variants):
        if negative:
            _,old,new=MUTATIONS[i-1]
            for part in ('src','tests'):
                expected={p.name for p in (model/part).iterdir() if p.is_file()};need(expected=={p.name for p in (source/part).iterdir() if p.is_file()},'Exact actual mutant source set')
                for name in expected:
                    before=(model/part/name).read_bytes();wanted=before.decode().replace(old,new).encode() if (part,name)==('src','ota_handler.c') else before
                    need((source/part/name).read_bytes()==wanted,'Exactly one declared compiled semantic mutation')
        compile_,test=r['commands'][2*i:2*i+2];exe=where/('tests.exe' if os.name=='nt' else 'tests')
        need(compile_['argv']==[str(x) for x in compile_args(cc,r['compiler']['msvc'],r['mode'],source,where)] and compile_['exit']==0 and compile_['host_executable_guard'] is None,'Exact host compile command')
        need(test['argv']==[str(exe)] and bool(test['host_executable_guard']) and g['host_executable'](exe)==test['host_executable_guard'],'Each executable launch reparses actual local-machine format')
        need(test['exit']!=0 if negative else test['exit']==0,'Actual positive/negative test exit')
        for row,label in ((compile_,'compile'),(test,'tests')):need(Path(row['folder'])==where and row['log']==label+'.log' and H(where/(label+'.log'))==row['log_sha256'],'Actual command/log identity')
    return dict(passed=True,receipt=str(receipt),tests=r['tests'],actual_host_archives_read=True,compiled_controls=3,target_execution=False,native_ABI_proved=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both']);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.language is None and a.build_root is None,'Read-only replay rejects fresh arguments');print(json.dumps(replay(root,a.replay)));return
    need(H(root/GUARD)==GPIN,'Immutable machine guard');g=runpy.run_path(str(root/GUARD));model=root/MODEL
    base=a.build_root.resolve() if a.build_root else model/'build'/('host-'+uuid.uuid4().hex)
    need(base.is_relative_to(model/'build') and not base.exists(),'Create-only owned HOST build root');base.mkdir(parents=True)
    pins=inputs(root);results=[]
    for mode in ('c','cpp') if a.language in (None,'both') else(a.language,):
        where=base/mode;where.mkdir();cc,env,msvc=g['host_tools'](root).compiler_for(mode);cc=Path(cc);compiler_pin=H(cc);env=dict(env,TMP=str(where),TEMP=str(where));commands=[]
        def run(folder,source,negative=False):
            compile_,_=g['execute'](compile_args(cc,msvc,mode,source,folder),folder,'compile',env)
            exe=folder/('tests.exe' if os.name=='nt' else 'tests');test,out=g['execute']([exe],folder,'tests',env,expect=1 if negative else 0,host_test=True)
            commands.extend([dict(folder=str(folder),**compile_),dict(folder=str(folder),**test)]);return out
        out=run(where,model);tests=json.loads(out);need(tests==EXPECTED,'Actual10-case smoke output');controls=[]
        for name,old,new in MUTATIONS:
            folder=where/name;folder.mkdir();source=folder/'model'
            for part in ('src','tests'):
                (source/part).mkdir(parents=True)
                for path in (model/part).iterdir():
                    if path.is_file():(source/part/path.name).write_bytes(path.read_bytes())
            path=source/'src/ota_handler.c';text=path.read_text();need(text.count(old)==1,'One exact mutation site '+name);path.write_bytes(text.replace(old,new).encode())
            run(folder,source,True);controls.append(dict(name=name,rejected=True,source_sha256=H(path)))
        need(inputs(root)==pins and H(cc)==compiler_pin,'Stable before/after HOST inputs/compiler')
        record=dict(schema='TSL9-readable-OTA-handler-host-smoke-v1',passed=True,mode=mode,tests=tests,source_pins=pins,
                    compiler=dict(path=str(cc),sha256=compiler_pin,msvc=msvc),commands=commands,compiled_controls=controls,
                    artifacts={p.relative_to(where).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in where.rglob('*') if p.is_file()},
                    target_execution=False,native_ABI_proved=False,hardware_OTA_proved=False)
        receipt=where/'verification.json';receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode());results.append(dict(mode=mode,receipt=str(receipt),sha256=H(receipt),tests=tests))
    print(json.dumps(dict(passed=True,results=results,target_execution=False)))
if __name__=='__main__':main()
