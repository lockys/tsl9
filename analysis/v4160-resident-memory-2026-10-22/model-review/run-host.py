#!/usr/bin/env python3
"""Independent authored HOST narratives; never execute candidate RV32 code."""
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
MODEL='experiments/tsl9-resident-memory-leaves/src'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
CORE=('memory_leaves.c','memory_leaves.h','io.h','host_io.c')
MUTANTS=(('truncate_compare_expected','(byte&255u)!=expected','(byte&255u)!=(expected&255u)'),
         ('skip_guard_for_null_compare','uint32_t saved,byte,end,answer=0;','uint32_t saved,byte,end,answer=0;\n    if(!address)return completed(0);'),
         ('reuse_first_copy_source','source+offset,&byte','source,&byte'))
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def load(p):
    s=importlib.util.spec_from_file_location('independent_memory_guard',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inputs(root):
    need(sha(root/GUARD)==GUARD_PIN,'Immutable HOST machine guard')
    core={n:sha(root/MODEL/n) for n in CORE}
    need(core==json.loads((HERE/'core-pins.json').read_bytes()),'Explicit frozen candidate sources')
    return dict(core=core,oracle=sha(HERE/'independent_host.c'),runner=sha(HERE/'run-host.py'),guard=GUARD_PIN)
def arguments(compiler,msvc,mode,source,work,target):
    files=[source/'memory_leaves.c',source/'host_io.c',HERE/'independent_host.c']
    if msvc:return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/I'+str(source),'/Fo'+str(work)+os.sep,*files,'/Fe'+str(target),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-I',source,*files,'-o',target]
def verify(root,folder,mode):
    folder.mkdir(parents=True);before=inputs(root);g=load(root/GUARD)
    compiler,environment,msvc=g.host_tools(root).compiler_for(mode);compiler_pin=sha(compiler)
    environment=dict(environment);environment['TMP']=str(folder);environment['TEMP']=str(folder)
    exe=folder/('independent.exe' if os.name=='nt' else 'independent')
    c,_=g.execute(arguments(compiler,msvc,mode,root/MODEL,folder,exe),folder,'compile',environment)
    t,out=g.execute([exe],folder,'tests',environment,host_test=True);tests=json.loads(out)
    need(tests['narrative_cases']==16 and tests['synthetic_HOST_only'] is True and tests['physical_ABI_proof'] is False,'Independent narrative count/scope')
    controls=[]
    for name,old,new in MUTANTS:
        work=folder/'controls'/name;source=work/'src';source.mkdir(parents=True)
        for member in CORE:(source/member).write_bytes((root/MODEL/member).read_bytes())
        f=source/'memory_leaves.c';s=f.read_text(encoding='utf8');need(s.count(old)==1,'Unique semantic anchor '+name);f.write_bytes(s.replace(old,new).encode('utf8'))
        target=work/('negative.exe' if os.name=='nt' else 'negative')
        nc,_=g.execute(arguments(compiler,msvc,mode,source,work,target),work,'compile',environment)
        nt,_=g.execute([target],work,'tests',environment,expect=1,host_test=True)
        need('independent memory check failed' in (work/'tests.log').read_text(errors='replace'),'Actual compiled assertion rejection '+name)
        controls.append(dict(name=name,source_sha256=sha(f),commands=[nc,nt]))
    need(before==inputs(root) and sha(compiler)==compiler_pin,'Stable source/tool inputs')
    r=dict(schema='TSL9-resident-memory-independent-HOST-v1',passed=True,mode=mode,inputs=before,tests=tests,
           compiler=dict(path=str(compiler),sha256=compiler_pin),commands=[c,t],actual_compiled_semantic_controls=controls,
           artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},
           target_execution=False,ISA_emulation=False,physical_ABI_proof=False,installed_provider_proved=False)
    write(folder/'verification.json',r)
    return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),tests=tests,compiled_semantic_controls=len(controls))
def replay(root,path):
    folder=path.parent;r=json.loads(path.read_bytes());need(r['inputs']==inputs(root),'Recorded independent input pins')
    g=load(root/GUARD);compiler=Path(r['compiler']['path']);mode=r['mode'];msvc=compiler.name.lower()=='cl.exe'
    need(sha(compiler)==r['compiler']['sha256'],'Actual compiler identity')
    for n,pin in r['artifacts'].items():
        p=(folder/n).resolve();need(p.is_relative_to(folder) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'Actual HOST artifact '+n)
    need(json.loads((folder/'tests.log').read_bytes())==r['tests'],'Actual positive output')
    exe=folder/('independent.exe' if os.name=='nt' else 'independent')
    need(r['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,root/MODEL,folder,exe)] and r['commands'][1]['argv']==[str(exe)] and [x['exit'] for x in r['commands']]==[0,0],'Exact positive recipes')
    need(len(r['actual_compiled_semantic_controls'])==len(MUTANTS),'Compiled control count')
    commands=[(folder,x) for x in r['commands']]
    for row,(name,old,new) in zip(r['actual_compiled_semantic_controls'],MUTANTS):
        work=folder/'controls'/name;source=work/'src';need(row['name']==name,'Control identity')
        for member in CORE:
            expected=(root/MODEL/member).read_bytes()
            if member=='memory_leaves.c':
                s=expected.decode('utf8');need(s.count(old)==1,'Unique frozen anchor');expected=s.replace(old,new).encode('utf8')
            need((source/member).read_bytes()==expected,'Single semantic mutation '+name)
        target=work/('negative.exe' if os.name=='nt' else 'negative')
        need(row['source_sha256']==sha(source/'memory_leaves.c') and row['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,source,work,target)] and row['commands'][1]['argv']==[str(target)] and row['commands'][0]['exit']==0 and row['commands'][1]['exit']==1,'Actual compiled control recipe')
        need('independent memory check failed' in (work/'tests.log').read_text(errors='replace'),'Actual negative output')
        commands.extend((work,x) for x in row['commands'])
    for work,row in commands:
        need(sha(work/row['log'])==row['log_sha256'],'Actual log bytes')
        need((g.host_executable(Path(row['argv'][0])) if row['log']=='tests.log' else None)==row['host_executable_guard'],'Reparse HOST machine; no target execution')
    return dict(passed=True,actual_host_artifacts_replayed=True,mode=mode,tests=r['tests'],compiled_semantic_controls=len(MUTANTS),target_execution=False,physical_ABI_proof=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--language',choices=('c','cpp','both'),default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.build_root is None,'Readonly replay');print(json.dumps(replay(root,a.replay.resolve())))
    else:
        base=a.build_root.resolve() if a.build_root else HERE/'build'/('host-'+uuid.uuid4().hex)
        need(base.is_relative_to(HERE/'build') and not base.exists(),'Create-only owned HOST build')
        print(json.dumps(dict(passed=True,results=[verify(root,base/m,m) for m in (('c','cpp') if a.language=='both' else (a.language,))])))
