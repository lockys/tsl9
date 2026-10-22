#!/usr/bin/env python3
"""Bounded synthetic HOST checks only; every executable is machine-guarded."""
import argparse,hashlib,json,os,runpy,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-event-callback'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py';GPIN='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
MUTATIONS=[('sign-mask','if(event_word&0x8000u)','if(event_word&0x80000000u)'),('exact-one','if(a[0]!=1u)goto clear_pending;','if(!(a[0]&1u))goto clear_pending;'),('low-bit','if(!(a[0]&1u))goto dispose;','if(a[0]!=1u)goto dispose;'),('capacity-wrap','capacity=(a[0]-3u)&0xffffu;','capacity=a[0]-3u;'),('message-residue','CB_READ(h,0x8646u,a[0],8,type);a[4]=type;','CB_READ(h,0x8646u,a[0],8,type);')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def compile_args(cc,msvc,mode,source,where):
    exe=where/('tests.exe' if os.name=='nt' else 'tests');files=[source/'src/callback.c',source/'src/host_io.c',source/'tests/smoke.c']
    if msvc:return [cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DCB_HOST=1','/I'+str(source/'src'),'/Fo'+str(where)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
    return [cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DCB_HOST=1','-I',source/'src',*files,'-o',exe]
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());model=root/MODEL;guard=root/GUARD;need(sha(guard)==GPIN,'immutable host guard');g=runpy.run_path(str(guard));need(r['passed'] and r['mode'] in('c','cpp'),'successful HOST receipt')
    for n,pin in r['source_pins'].items():need(sha(Path(n))==pin,'current exact HOST source/runner/helper')
    need(str(Path(__file__).resolve()) in r['source_pins'] and r['source_pins'][str(Path(__file__).resolve())]==sha(Path(__file__)),'current HOST verifier')
    need(set(r['artifacts'])=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=receipt},'complete actual HOST artifact set')
    for n,v in r['artifacts'].items():p=(folder/n).resolve();need(p.is_relative_to(folder) and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],'actual HOST artifact pin')
    cc=Path(r['compiler']['path']);need(sha(cc)==r['compiler']['sha256'],'actual compiler identity');need(r['tests']==dict(groups=1,cases=12,checks=34)==json.loads((folder/'tests.log').read_bytes()),'exact directed HOST result');need(len(r['commands'])==12 and len(r['actual_compiled_controls'])==5,'exact positive and five compiled controls')
    groups=[(folder,model,False)]+[(folder/name,folder/name/'model',True) for name,_,_ in MUTATIONS]
    for i,(where,source,negative) in enumerate(groups):
        if negative:
            tag,old,new=MUTATIONS[i-1]
            for d in('src','tests'):
                expected={p.name for p in(model/d).glob('*') if p.is_file()};need(expected=={p.name for p in(source/d).glob('*') if p.is_file()},'exact copied mutant source set')
                for n in expected:
                    positive=(model/d/n).read_bytes();wanted=positive.decode().replace(old,new).encode() if (d,n)==('src','callback.c') else positive;need((source/d/n).read_bytes()==wanted,'actual mutant exactly one declared source change')
        c,t=r['commands'][2*i:2*i+2];need(c['argv']==[str(x) for x in compile_args(cc,r['compiler']['msvc'],r['mode'],source,where)] and c['exit']==0 and c['host_executable_guard'] is None,'exact compile recipe/exit and no test guard claim');exe=where/('tests.exe' if os.name=='nt' else 'tests');need(t['argv']==[str(exe)] and bool(t['host_executable_guard']) and g['host_executable'](exe)==t['host_executable_guard'],'each actual HOST test launch has matching current machine guard');need(t['exit']!=0 if negative else t['exit']==0,'actual test/control exit')
        for q,label in((c,'compile'),(t,'tests')):need(q['log']==label+'.log' and Path(q['folder'])==where and sha(where/(label+'.log'))==q['log_sha256'],'actual command/log/source association')
    return dict(passed=True,receipt=str(receipt),tests=r['tests'],actual_compiled_controls=5,actual_build_archives_read=True,target_execution=False,native_ABI_proved=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default=None);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve();model=root/MODEL
    if a.replay:need(a.language is None and a.build_root is None,'build options forbidden in readonly HOST replay');print(json.dumps(replay(root,a.replay)));return
    guard=root/GUARD;need(sha(guard)==GPIN,'immutable native HOST executable guard');g=runpy.run_path(str(guard));base=a.build_root.resolve() if a.build_root else model/'build'/('host-'+uuid.uuid4().hex);need(not base.exists() and base.is_relative_to(model/'build'),'create-only owned HOST output');base.mkdir(parents=True);pins={str(p):sha(p) for p in[Path(__file__).resolve(),guard,root/'scripts/portable_verify.py',*model.joinpath('src').glob('*'),*model.joinpath('tests').glob('*')] if p.is_file()};results=[]
    for mode in('c','cpp') if a.language in(None,'both') else(a.language,):
        folder=base/mode;folder.mkdir();cc,env,msvc=g['host_tools'](root).compiler_for(mode);cc=Path(cc);pin=sha(cc);env=dict(env,TMP=str(folder),TEMP=str(folder));commands=[]
        def compile_test(where,source,negative=False):
            exe=where/('tests.exe' if os.name=='nt' else 'tests');argv=compile_args(cc,msvc,mode,source,where)
            c,_=g['execute'](argv,where,'compile',env);t,out=g['execute']([exe],where,'tests',env,expect=1 if negative else 0,host_test=True);commands.extend([dict(folder=str(where),**c),dict(folder=str(where),**t)]);return out
        out=compile_test(folder,model);tests=json.loads(out);need(tests==dict(groups=1,cases=12,checks=34),'exact actual12-case smoke result');controls=[]
        for name,old,new in MUTATIONS:
            where=folder/name;where.mkdir();source=where/'model';(source/'src').mkdir(parents=True);(source/'tests').mkdir()
            for d in('src','tests'):
                for pth in(model/d).glob('*'):
                    if pth.is_file():(source/d/pth.name).write_bytes(pth.read_bytes())
            path=source/'src/callback.c';text=path.read_text();need(text.count(old)==1,'one exact actual C mutation '+name);path.write_bytes(text.replace(old,new).encode());compile_test(where,source,True);controls.append(dict(name=name,source_sha256=sha(path),rejected=True))
        need(sha(cc)==pin and all(sha(Path(n))==v for n,v in pins.items()),'stable exact host source/tool/helper inputs');r=dict(schema='TSL9-event-callback-synthetic-host-smoke-v1',passed=True,mode=mode,tests=tests,source_pins=pins,compiler=dict(path=str(cc),sha256=pin,msvc=msvc),commands=commands,actual_compiled_controls=controls,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},native_ABI_proved=False,target_execution=False,hardware=False);write(folder/'verification.json',r);results.append(dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),tests=tests))
    print(json.dumps(dict(passed=True,results=results,target_execution=False)))
if __name__=='__main__':main()
