#!/usr/bin/env python3
"""Compile/launch only independent synthetic HOST ADC tests; native is excluded."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import runpy
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-adc-config'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
MUTATIONS=[('wrong_mask_bit','UINT32_C(0xe0f0feff)','UINT32_C(0xe0f0fefe)'),('masked_fullword','bits|=v<<8;','bits|=(v&255u)<<8;'),('byte_without_decrement','((v-1u)&255u)<<20','(v&255u)<<20')]
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def source_reader():
    s=importlib.util.spec_from_file_location('adc_host_source',HERE/'source.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def guard(root):
    need(sha(root/GUARD)==GUARD_PIN,'Sealed HOST executable guard');return runpy.run_path(str(root/GUARD))
def inputs(root):
    paths=[Path(__file__).resolve(),HERE/'host_harness.c',HERE/'source.py',HERE/'source-ledger.json',HERE/'reference-pins.json',Path(sys.executable).resolve(),root/GUARD,root/'scripts/portable_verify.py']
    paths += [root/MODEL/'src'/n for n in('adc_config.c','adc_config.h','host_io.c')]
    paths += [root/'experiments/tsl9-resident-memory-leaves/src'/n for n in('memory_leaves.h','io.h')]
    return {str(p):sha(p) for p in paths}
def recipes(cc,msvc,mode,root,folder,core=None):
    src=root/MODEL/'src';files=[core if core is not None else src/'adc_config.c',src/'host_io.c',HERE/'host_harness.c'];objects=[];out=[]
    for i,path in enumerate(files):
        obj=folder/('unit'+str(i)+('.obj' if msvc else '.o'));objects.append(obj);dep=folder/('dependencies'+str(i)+('.json' if msvc else '.d'))
        args=[cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/I'+str(src),'/c',path,'/Fo'+str(obj),'/sourceDependencies',dep] if msvc else [cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-I',src,'-c',path,'-MD','-MF',dep,'-MT',obj.name,'-o',obj]
        out.append(('compile'+str(i),args))
    exe=folder/('tests.exe' if os.name=='nt' else 'tests')
    out.append(('link',[cc,'/nologo',*objects,'/Fe'+str(exe),'/link','/INCREMENTAL:NO'] if msvc else [cc,*objects,'-o',exe]))
    out.append(('tests',[exe]));return out
def resources(folder,msvc):
    out={}
    for i in range(3):
        p=folder/('dependencies'+str(i)+('.json' if msvc else '.d'))
        if msvc:
            v=read(p)['Data'];paths=[Path(v['Source']),*[Path(x) for x in v['Includes']]]
        else:
            text=p.read_text().replace('\\\n',' ');_,_,rhs=text.partition(':');paths=[Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',rhs)]
        for path in paths:out[str(path)]=sha(path)
    return out
def clone(root,where,mutation):
    where.mkdir();_,old,new=mutation;p=where/'mutant-core.c';text=(root/MODEL/'src/adc_config.c').read_text();need(text.count(old)==1,'Exactly one declared semantic mutation');p.write_bytes(text.replace(old,new).encode())
def verify_clone(root,where,mutation):
    _,old,new=mutation
    need({p.name for p in where.iterdir()}=={'mutant-core.c'},'Only actual mutant source retained')
    expected=(root/MODEL/'src/adc_config.c').read_text().replace(old,new).encode();need((where/'mutant-core.c').read_bytes()==expected,'Actual mutant exact single source change')
def replay(root,receipt):
    receipt=Path(receipt).resolve();folder=receipt.parent;r=read(receipt);g=guard(root);source_reader().inspect(root)
    need(r['source_pins']==inputs(root),'Current exact independent HOST/source/helper pins')
    need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual HOST artifact inventory')
    cc=Path(r['compiler']['path']);need(sha(cc)==r['compiler']['sha256'],'Actual HOST compiler bytes')
    for p,pin in r['compiler']['additional_tools'].items():need(sha(p)==pin,'Actual HOST linker bytes')
    variants=[('positive',folder,root,False)]+[(name,folder/name,folder/name/'model',True) for name,_,_ in MUTATIONS]
    for i,(name,where,src,negative) in enumerate(variants):
        if negative:verify_clone(root,src,MUTATIONS[i-1])
        actual=r['variants'][i];need(actual['name']==name,'Exactly positive plus three semantic controls')
        expected=recipes(cc,r['compiler']['msvc'],r['mode'],root,where,src/'mutant-core.c' if negative else None)
        need([(x['label'],x['argv']) for x in actual['commands']]==[(label,[str(v) for v in argv]) for label,argv in expected],'Exact HOST compile/link/test commands')
        for command in actual['commands']:
            need(sha(where/command['log'])==command['log_sha256'],'Actual compile/test logs')
            need(command['exit']!=0 if negative and command['label']=='tests' else command['exit']==0,'Actual compile and semantic test exit')
            if command['label']=='tests':need(g['host_executable'](Path(command['argv'][0]))==command['host_executable_guard'],'Reparse actual local-machine executable, never RISC-V')
        need(actual['dependency_resources']==resources(where,r['compiler']['msvc']),'Exact compiler-reported sources and resource header hashes')
        if negative:need('failure line' in (where/'tests.log').read_text(),'Control rejected by semantic assertion')
    need(r['tests']==read(folder/'tests.log') and r['tests']['passed'] and r['tests']['cases']==74 and r['tests']['ordered_effects']==14 and r['tests']['synthetic_IO'] and not r['tests']['RV32_execution'],'Actual independent74-case HOST suite')
    return dict(passed=True,mode=r['mode'],receipt=str(receipt),tests=r['tests'],compiled_controls=3,actual_HOST_artifacts_read=True,target_execution=False,physical_ABI_proved=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--language',choices=['c','cpp','both']);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.language is None and a.build_root is None,'Read-only replay excludes generation');print(json.dumps(replay(root,a.replay)));return
    source_reader().inspect(root);g=guard(root);case=source_reader().case(root,'v4160-adc-config-2026-10-22');base=a.build_root.resolve() if a.build_root else HERE/'build'/('host-'+uuid.uuid4().hex)
    owners=[HERE/'build',case/'build',root/MODEL/'build']
    need(any(base!=owner and base.is_relative_to(owner) for owner in owners) and not base.exists(),'Owned create-only fresh HOST build');base.mkdir(parents=True);before=inputs(root);results=[]
    for mode in('c','cpp') if a.language in(None,'both') else(a.language,):
        folder=base/mode;folder.mkdir();cc,env,msvc=g['host_tools'](root).compiler_for(mode);cc=Path(cc);env=dict(env,TMP=str(folder),TEMP=str(folder));compiler=dict(path=str(cc),sha256=sha(cc),msvc=msvc,additional_tools={str(cc.parent/'link.exe'):sha(cc.parent/'link.exe')} if msvc else {})
        variants=[];tests=None
        for i,mutation in enumerate([None,*MUTATIONS]):
            negative=mutation is not None;where=folder/mutation[0] if negative else folder;src=where/'model' if negative else root
            if negative:where.mkdir();clone(root,src,mutation)
            commands=[]
            for label,argv in recipes(cc,msvc,mode,root,where,src/'mutant-core.c' if negative else None):
                command,text=g['execute'](argv,where,label,env,expect=1 if negative and label=='tests' else 0,host_test=label=='tests');commands.append(dict(label=label,**command))
                if not negative and label=='tests':tests=json.loads(text)
            variants.append(dict(name=mutation[0] if negative else 'positive',commands=commands,dependency_resources=resources(where,msvc)))
        need(inputs(root)==before and sha(cc)==compiler['sha256'],'Stable before/after inputs/compiler')
        record=dict(schema='TSL9-ADC1892E-independent-HOST-v1',mode=mode,passed=True,tests=tests,compiler=compiler,source_pins=before,variants=variants,target_execution=False,physical_ABI_proved=False)
        record['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';write(receipt,record);results.append(replay(root,receipt))
    print(json.dumps(dict(passed=True,results=results,target_execution=False)))
if __name__=='__main__':main()
