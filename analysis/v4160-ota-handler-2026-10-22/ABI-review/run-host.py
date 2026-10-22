#!/usr/bin/env python3
"""Compile independent synthetic fixtures for the actual local host only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-ota-handler/src'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189'
CORE=('ota_handler.c','ota_handler.h','io.h','host_io.c')
MUTANTS=(
    ('command_byte_truncation','s->context=context;s->buffer=payload;',
     's->context=context;s->buffer=payload;command&=255u;'),
    ('stale_S_payload_after_UID','OH_READ(h,0x9da0,s->buffer,8,first);',
     'OH_READ(h,0x9da0,payload,8,first);'),
    ('S_active_forced_one','OH_WRITE(h,0x9da6,OH_GP(h)+0xa9u,8,s->flash);',
     'OH_WRITE(h,0x9da6,OH_GP(h)+0xa9u,8,1u);'),
    ('RAM_read_before_Flash',
     'OH_READ(h,0x9d10,s->flash+offset,32,flash_word);\n            OH_READ(h,0x9d16,s->source+offset,32,source_word);',
     'OH_READ(h,0x9d16,s->source+offset,32,source_word);\n            OH_READ(h,0x9d10,s->flash+offset,32,flash_word);'))


def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf8'))


def load(path):
    spec=importlib.util.spec_from_file_location('independent_ota_host_guard',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def inputs(root,draft):
    need(sha(root/GUARD)==GUARD_PIN,'Immutable host executable machine guard')
    core={name:sha(root/MODEL/name) for name in CORE}
    if not draft:need(core==json.loads((HERE/'core-pins.json').read_bytes()),'Explicit frozen producer sources')
    return dict(core=core,oracle=sha(HERE/'independent_host.c'),runner=sha(HERE/'run-host.py'),
                guard=GUARD_PIN,portable_helper=sha(root/'scripts/portable_verify.py'),draft=draft)


def arguments(compiler,msvc,mode,source,work,target):
    files=[source/'ota_handler.c',source/'host_io.c',HERE/'independent_host.c']
    if msvc:
        return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
                '/std:c++17' if mode=='cpp' else '/std:c11','/DOH_HOST=1','/I'+str(source),
                '/Fo'+str(work)+os.sep,*files,'/Fe'+str(target),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
            '-O1','-Wall','-Wextra','-Werror','-DOH_HOST=1','-I',source,*files,'-o',target]


def verify(root,folder,mode,draft=False):
    folder.mkdir(parents=True);before=inputs(root,draft);g=load(root/GUARD)
    compiler,environment,msvc=g.host_tools(root).compiler_for(mode);compiler_pin=sha(compiler)
    environment=dict(environment);environment['TMP']=str(folder);environment['TEMP']=str(folder)
    executable=folder/('independent.exe' if os.name=='nt' else 'independent')
    compile_row,_=g.execute(arguments(compiler,msvc,mode,root/MODEL,folder,executable),folder,'compile',environment)
    test_row,out=g.execute([executable],folder,'tests',environment,host_test=True)
    tests=json.loads(out)
    need(tests['narrative_cases']==16 and tests['synthetic_HOST_only'] is True and
         tests['physical_ABI_proof'] is False,'Actual independent conditional narrative tests')
    controls=[]
    for name,old,new in (() if draft else MUTANTS):
        work=folder/'controls'/name;source=work/'src';source.mkdir(parents=True)
        for member in CORE:(source/member).write_bytes((root/MODEL/member).read_bytes())
        file=source/'ota_handler.c';text=file.read_text(encoding='utf8')
        need(text.count(old)==1,'Unique actual compiled semantic anchor '+name)
        file.write_bytes(text.replace(old,new).encode('utf8'))
        target=work/('negative.exe' if os.name=='nt' else 'negative')
        c,_=g.execute(arguments(compiler,msvc,mode,source,work,target),work,'compile',environment)
        t,_=g.execute([target],work,'tests',environment,expect=1,host_test=True)
        need('independent OTA handler check failed' in (work/'tests.log').read_text(errors='replace'),
             'Actual assertion rejection after successful compilation '+name)
        controls.append(dict(name=name,old=old,new=new,source_sha256=sha(file),commands=[c,t]))
    need(before==inputs(root,draft) and sha(compiler)==compiler_pin,'Stable actual source/compiler inputs')
    result=dict(schema='TSL9-OTA-handler-independent-HOST-v1',passed=True,mode=mode,inputs=before,
                tests=tests,compiler=dict(path=str(compiler),sha256=compiler_pin),commands=[compile_row,test_row],
                actual_compiled_semantic_controls=controls,
                artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
                           for p in folder.rglob('*') if p.is_file()},
                target_execution=False,ISA_emulation=False,physical_ABI_proof=False,
                full_original_ABI_proved=False,hardware_OTA_proved=False)
    write(folder/'verification.json',result)
    return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),
                tests=tests,compiled_semantic_controls=len(controls),draft=draft)


def replay(root,path):
    folder=path.parent;r=json.loads(path.read_bytes());draft=r['inputs']['draft']
    need(r['inputs']==inputs(root,draft),'Recorded actual independent source inputs')
    g=load(root/GUARD);compiler=Path(r['compiler']['path']);mode=r['mode'];msvc=compiler.name.lower()=='cl.exe'
    need(sha(compiler)==r['compiler']['sha256'],'Recorded actual compiler identity')
    for name,pin in r['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.stat().st_size==pin['bytes'] and
                                      sha(p)==pin['sha256'],'Actual hosted artifact '+name)
    need(json.loads((folder/'tests.log').read_bytes())==r['tests'],'Actual positive output log')
    exe=folder/('independent.exe' if os.name=='nt' else 'independent')
    need(r['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,root/MODEL,folder,exe)] and
         r['commands'][1]['argv']==[str(exe)] and [v['exit'] for v in r['commands']]==[0,0],
         'Exact actual positive recipes/exits')
    commands=[(folder,row) for row in r['commands']];selected=() if draft else MUTANTS
    need(len(r['actual_compiled_semantic_controls'])==len(selected),'Actual selected compiled control count')
    for row,(name,old,new) in zip(r['actual_compiled_semantic_controls'],selected):
        work=folder/'controls'/name;source=work/'src'
        need((row['name'],row['old'],row['new'])==(name,old,new),'Exact semantic control identity')
        for member in CORE:
            wanted=(root/MODEL/member).read_bytes()
            if member=='ota_handler.c':
                text=wanted.decode('utf8');need(text.count(old)==1,'Unique semantic anchor')
                wanted=text.replace(old,new).encode('utf8')
            need((source/member).read_bytes()==wanted,'Actual single-mutant source '+name)
        need(sha(source/'ota_handler.c')==row['source_sha256'],'Actual mutant source pin')
        exe=work/('negative.exe' if os.name=='nt' else 'negative')
        need(row['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,source,work,exe)] and
             row['commands'][1]['argv']==[str(exe)] and row['commands'][0]['exit']==0 and row['commands'][1]['exit']!=0,
             'Successful compile then semantic rejection')
        need('independent OTA handler check failed' in (work/'tests.log').read_text(errors='replace'),
             'Actual assertion log '+name)
        commands.extend((work,command) for command in row['commands'])
    launches=0
    for work,command in commands:
        if command['log']=='tests.log':
            need(g.host_executable(Path(command['argv'][0]))==command['host_executable_guard'],
                 'Reparsed actual native HOST executable, never RISC-V')
            launches+=1
        else:need(command['host_executable_guard'] is None,'Compile is not a test launch')
        need(sha(work/command['log'])==command['log_sha256'],'Actual command output log')
    need(launches==1+len(selected),'All actual HOST launches rechecked without relaunch')
    return dict(passed=True,actual_host_artifacts_replayed=True,mode=mode,tests=r['tests'],
                compiled_semantic_controls=len(selected),host_executables_reparsed=launches,draft=draft,
                target_execution=False,physical_ABI_proof=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--language',choices=('c','cpp','both'),default='both')
    p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--draft',action='store_true')
    a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.build_root is None and not a.draft,'Readonly actual receipt replay')
        print(json.dumps(replay(root,a.replay.resolve())))
    else:
        base=a.build_root.resolve() if a.build_root else HERE/'build'/('host-'+uuid.uuid4().hex)
        need(base.is_relative_to(HERE/'build') and not base.exists(),'Create-only owned HOST build root')
        print(json.dumps(dict(passed=True,results=[verify(root,base/m,m,a.draft) for m in
                         (('c','cpp') if a.language=='both' else (a.language,))])))
