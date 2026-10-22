#!/usr/bin/env python3
"""Independent conditional callback tests compiled exclusively for this host."""
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
MODEL='experiments/tsl9-v4160-event-callback/src'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189'
MUTANTS=(('exact_gate_changed_to_lowbit','if(a[0]!=1u)','if(!(a[0]&1u))'),
         ('capacity_underflow_clamped','capacity=(a[0]-3u)&0xffffu;','capacity=a[0]<3u?0u:((a[0]-3u)&0xffffu);'),
         ('sixth_argument_wrong_task','a[5]=s->task;','a[5]=s->connection;'))


def need(value,message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    path.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf8'))


def load(path):
    spec=importlib.util.spec_from_file_location('independent_callback_host_guard',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def inputs(root):
    need(sha(root/GUARD)==GUARD_PIN,'Immutable host executable machine guard')
    pins=json.loads((HERE/'core-pins.json').read_bytes())
    for name,pin in pins.items():
        need(sha(root/MODEL/name)==pin,'Explicit producer-frozen callback source '+name)
    return dict(core=pins,oracle=sha(HERE/'independent_host.c'),runner=sha(HERE/'run-host.py'),
                guard=GUARD_PIN,portable_helper=sha(root/'scripts/portable_verify.py'))


def arguments(compiler,msvc,mode,source,work,target):
    files=[source/'callback.c',source/'host_io.c',HERE/'independent_host.c']
    if msvc:
        return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC',
                '/std:c++17' if mode=='cpp' else '/std:c11','/DCB_HOST=1','/I'+str(source),
                '/Fo'+str(work)+os.sep,*files,'/Fe'+str(target),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11',
            '-O1','-Wall','-Wextra','-Werror','-DCB_HOST=1','-I',source,*files,'-o',target]


def verify(root,folder,mode):
    folder.mkdir(parents=True);before=inputs(root);g=load(root/GUARD)
    compiler,environment,msvc=g.host_tools(root).compiler_for(mode);compiler_pin=sha(compiler)
    environment=dict(environment);environment['TMP']=str(folder);environment['TEMP']=str(folder)
    executable=folder/('independent.exe' if os.name=='nt' else 'independent')
    compile_row,_=g.execute(arguments(compiler,msvc,mode,root/MODEL,folder,executable),folder,'compile',environment)
    test_row,out=g.execute([executable],folder,'tests',environment,host_test=True)
    tests=json.loads(out)
    need(tests['cases']>=20 and tests['conditional_HOST_only'] is True and
         tests['physical_GPR_or_ROM_proof'] is False,'Actual independent conditional effects')
    controls=[]
    for name,old,new in MUTANTS:
        work=folder/'controls'/name;source=work/'src';source.mkdir(parents=True)
        for member in before['core']:
            (source/member).write_bytes((root/MODEL/member).read_bytes())
        file=source/'callback.c';text=file.read_text(encoding='utf8')
        need(text.count(old)==1,'Unique compiled semantic countercase '+name)
        file.write_bytes(text.replace(old,new).encode('utf8'))
        target=work/('negative.exe' if os.name=='nt' else 'negative')
        c,_=g.execute(arguments(compiler,msvc,mode,source,work,target),work,'compile',environment)
        t,_=g.execute([target],work,'tests',environment,expect=1,host_test=True)
        need('independent callback check failed' in (work/'tests.log').read_text(errors='replace'),
             'Actual assertion failure after successful compile '+name)
        controls.append(dict(name=name,old=old,new=new,source_sha256=sha(file),commands=[c,t]))
    need(before==inputs(root) and sha(compiler)==compiler_pin,'Stable frozen input/compiler hashes')
    result=dict(schema='TSL9-callback-independent-conditional-HOST-v1',passed=True,mode=mode,
                inputs=before,tests=tests,compiler=dict(path=str(compiler),sha256=compiler_pin),
                commands=[compile_row,test_row],actual_compiled_semantic_controls=controls,
                artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
                           for p in folder.rglob('*') if p.is_file()},
                target_execution=False,ISA_emulation=False,physical_GPR_or_ROM_proof=False,
                full_original_ABI_proved=False,hardware_OTA_proved=False)
    write(folder/'verification.json',result)
    return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),
                tests=tests,compiled_semantic_controls=3)


def replay(root,path):
    folder=path.parent;r=json.loads(path.read_bytes());need(r['inputs']==inputs(root),'Frozen review inputs')
    g=load(root/GUARD);compiler=Path(r['compiler']['path']);mode=r['mode'];msvc=compiler.name.lower()=='cl.exe'
    need(sha(compiler)==r['compiler']['sha256'],'Actual compiler identity')
    for name,pin in r['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.stat().st_size==pin['bytes'] and
                                      sha(p)==pin['sha256'],'Exact actual hosted artifact '+name)
    need(json.loads((folder/'tests.log').read_bytes())==r['tests'],'Actual positive output log')
    exe=folder/('independent.exe' if os.name=='nt' else 'independent')
    need(r['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,root/MODEL,folder,exe)] and
         r['commands'][1]['argv']==[str(exe)] and [v['exit'] for v in r['commands']]==[0,0],
         'Exact actual positive recipes and exits')
    commands=[(folder,row) for row in r['commands']]
    need(len(r['actual_compiled_semantic_controls'])==3,'Exactly three compiled controls')
    for row,(name,old,new) in zip(r['actual_compiled_semantic_controls'],MUTANTS):
        work=folder/'controls'/name;source=work/'src'
        need((row['name'],row['old'],row['new'])==(name,old,new),'Exact negative recipe identity')
        for member in r['inputs']['core']:
            wanted=(root/MODEL/member).read_bytes()
            if member=='callback.c':
                text=wanted.decode('utf8');need(text.count(old)==1,'Unique semantic anchor')
                wanted=text.replace(old,new).encode('utf8')
            need((source/member).read_bytes()==wanted,'Exact single-mutant source '+name)
        need(sha(source/'callback.c')==row['source_sha256'],'Actual compiled mutant source hash')
        exe=work/('negative.exe' if os.name=='nt' else 'negative')
        need(row['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,source,work,exe)] and
             row['commands'][1]['argv']==[str(exe)] and [v['exit'] for v in row['commands']]==[0,1],
             'Actual successful negative compile then semantic rejection')
        need('independent callback check failed' in (work/'tests.log').read_text(errors='replace'),
             'Actual directed assertion rejection '+name)
        commands.extend((work,command) for command in row['commands'])
    launches=0
    for work,command in commands:
        if command['log']=='tests.log':
            need(g.host_executable(Path(command['argv'][0]))==command['host_executable_guard'],
                 'Reparsed actual host executable machine identity')
            launches+=1
        else:
            need(command['host_executable_guard'] is None,'Compile is not a guarded test launch')
        need(sha(work/command['log'])==command['log_sha256'],'Actual guarded launch log')
    need(launches==4,'Positive and three negative host executable guards')
    return dict(passed=True,actual_host_artifacts_replayed=True,mode=mode,tests=r['tests'],
                compiled_semantic_controls=3,host_executables_reparsed=4,target_execution=False,
                physical_GPR_or_ROM_proof=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--language',choices=('c','cpp','both'),default='both')
    p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.build_root is None,'Readonly actual artifact replay');print(json.dumps(replay(root,a.replay.resolve())))
    else:
        base=a.build_root.resolve() if a.build_root else HERE/'build'/('host-'+uuid.uuid4().hex)
        need(base.is_relative_to(HERE/'build') and not base.exists(),'Create-only owned host build root')
        print(json.dumps(dict(passed=True,results=[verify(root,base/m,m) for m in
                         (('c','cpp') if a.language=='both' else (a.language,))])))
