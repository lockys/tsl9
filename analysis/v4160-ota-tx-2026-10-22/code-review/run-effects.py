#!/usr/bin/env python3
"""Independent bounded TX effects, compiled only for the actual host."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-v4160-ota-tx'
GUARD = 'experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN = 'f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
CORE = {'host_io.c': 'f795021fc5116ba18a16000eeebf6a2a235b3a2c9de4d0104f2396d7872d81aa',
        'host_io.h': '1755ca187eb54fb95bb5b1523c8955c8f99883048115e5c8481972d706c8c4c6',
        'tx_native.c': 'd246669c3758acc93808339b40a84c9ac74d4fd163bc8748ac4d0e99cf1ba0dd',
        'tx_native.h': 'c4bce9d222ededc14da5360fb9bd834a14d89c49cfc136ea3658461d9c44f0f4',
        'tx_io.h': '1af1906c7cde16a5b77a642a716af718b576ed5aad90e988495cbe3dedad957f'}
MUTANTS = [
    ('length1039_rejected', 'tx_native.c', 'if(length>limit)', 'if(length>=limit)'),
    ('length_u16_guard', 'tx_native.c', 'if(length>limit)', 'if((length&65535u)>limit)'),
    ('cached_second_GP', 'tx_native.c', 'gp+0x9au,handle', '0x2100009au,handle'),
    ('gate2_reloads_A2_A3', 'host_io.c', 'tx_set(h,1,site+2u);', 'tx_set(h,1,site+2u);if(site==0x8ab4u){tx_set(h,12,h->regs[9]);tx_set(h,13,h->regs[8]);}'),
    ('gate2_failed_A2_zero', 'tx_native.c', 'lane=TX_LANE2(1u);', 'lane=TX_LANE2(0u);'),
    ('wrong_record_stride', 'host_io.h', 'TX_ARG5(1062u)', 'TX_ARG5(1060u)'),
    ('wrong_magic', 'host_io.h', 'TX_ARG4(0x7f55u)', 'TX_ARG4(0x7f56u)'),
    ('zero_metadata_SW32', 'tx_native.c', 'TX_WRITE16(0x8b36u,record+4u,0u);', 'tx_write(h,0x8b36u,record+4u,4u,0u,1);TX_STOP();'),
    ('tail_handle_wrong_table', 'tx_native.c', 'lane+gp+0x94u', 'lane+gp+0x96u'),
    ('restore_cached_SP', 'host_io.c', '(void)tx_read(h,site,sp+offset,4u,reg);', '(void)tx_read(h,site,(sp-sp+0x22000fe0u)+offset,4u,reg);'),
    ('copy_repeats_first_byte', 'tx_native.c', 'payload=TX_ARG0(payload+index);', 'payload=TX_ARG0(payload);'),
    ('checksum_mask127', 'host_io.h', 'TX_ARG4(v)&255u', 'TX_ARG4(v)&127u'),
    ('tail_value_normalized', 'host_io.c', 'r.value=h->regs[10];', 'r.value=0u;'),
    ('target_lowbit_unmasked', 'host_io.c', 'e->target=raw&~1u;', 'e->target=raw;'),
]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v, m):
    if not v: raise ValueError(m)
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, v): p.write_bytes((json.dumps(v, indent=2)+'\n').encode('utf-8'))
def load(p, name):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def inputs(root):
    need(sha(root/GUARD)==GUARD_PIN,'Immutable host executable guard')
    for n,pin in CORE.items(): need(sha(root/MODEL/'src'/n)==pin,'Frozen TX source '+n)
    return {'core':CORE,'guard':GUARD_PIN,'portable_helper':sha(root/'scripts/portable_verify.py'),'oracle':sha(HERE/'expected-effects.c'),'runner':sha(Path(__file__))}
def arguments(compiler,msvc,mode,src,folder,exe):
    files=[src/'tx_native.c',src/'host_io.c',HERE/'expected-effects.c']
    if msvc:return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTX_HOST_TEST=1','/I'+str(src),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DTX_HOST_TEST=1','-I',src,*files,'-o',exe]
def verify(root,folder,mode,positive_only=False):
    folder.mkdir(parents=True);before=inputs(root);g=load(root/GUARD,'TX_independent_guard');compiler,env,msvc=g.host_tools(root).compiler_for(mode);compiler_pin=sha(compiler);env=dict(env);env['TMP']=str(folder);env['TEMP']=str(folder)
    exe=folder/('effects.exe' if os.name=='nt' else 'effects');cc,_=g.execute(arguments(compiler,msvc,mode,root/MODEL/'src',folder,exe),folder,'compile',env);tt,out=g.execute([exe],folder,'tests',env,host_test=True);tests=json.loads(out);need(tests=={'passed':True,'groups':4,'cases':31,'checks':78283,'target_execution':False},'Exact independent directed source-effect fixtures')
    controls=[]
    for name,member,old,new in ([] if positive_only else MUTANTS):
        work=folder/'controls'/name;work.mkdir(parents=True);src=work/'src';src.mkdir()
        for n in CORE:(src/n).write_bytes((root/MODEL/'src'/n).read_bytes())
        path=src/member;text=path.read_text(encoding='utf-8');need(text.count(old)==1,'Unique semantic mutation '+name);path.write_bytes(text.replace(old,new).encode('utf-8'))
        target=work/('negative.exe' if os.name=='nt' else 'negative');c,_=g.execute(arguments(compiler,msvc,mode,src,work,target),work,'compile',env);t,_=g.execute([target],work,'tests',env,expect=1,host_test=True);need('independent failure line' in (work/'tests.log').read_text(errors='replace'),'Compiled semantic assertion '+name);controls.append({'case':name,'file':member,'old':old,'new':new,'mutant_sha256':sha(path),'commands':[c,t]})
    need(inputs(root)==before and sha(compiler)==compiler_pin,'Source/compiler unchanged throughout')
    result={'schema':'ID2966-TX-independent-host-v1','passed':True,'mode':mode,'tests':tests,'inputs':before,'compiler':{'path':str(compiler),'sha256':compiler_pin},'commands':[cc,tt],'actual_compiled_semantic_controls':controls,'artifacts':{p.relative_to(folder).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in folder.rglob('*') if p.is_file()},'RV32_execution':False,'ISA_emulation':False,'native_prefix_proof':False,'native_callee_preservation_proved':False,'network':False,'hardware':False,'OTA_ready':False}
    write(folder/'verification.json',result);return {'receipt':str(folder/'verification.json'),'sha256':sha(folder/'verification.json'),'mode':mode,'tests':tests,'actual_compiled_semantic_controls':len(controls)}
def replay(root,path):
    path=path.resolve();folder=path.parent;r=read(path);need(r['passed'] and r['inputs']==inputs(root),'Actual source/runner identity');need(sha(Path(r['compiler']['path']))==r['compiler']['sha256'],'Actual compiler identity');g=load(root/GUARD,'TX_independent_replay_guard')
    for n,pin in r['artifacts'].items():
        member=(folder/n).resolve();need(member.is_relative_to(folder) and member.stat().st_size==pin['bytes'] and sha(member)==pin['sha256'],'Actual artifact '+n)
    need(read(folder/'tests.log')==r['tests']=={'passed':True,'groups':4,'cases':31,'checks':78283,'target_execution':False},'Exact actual positive test output');need(len(r['actual_compiled_semantic_controls'])==len(MUTANTS),'Fourteen actual compiled controls')
    compiler=Path(r['compiler']['path']);msvc=compiler.name.lower()=='cl.exe';mode=r['mode'];exe=folder/('effects.exe' if os.name=='nt' else 'effects')
    need(r['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,root/MODEL/'src',folder,exe)] and r['commands'][1]['argv']==[str(exe)],'Exact positive compile/run recipes')
    need([v['exit'] for v in r['commands']]==[0,0],'Positive exits')
    commands=[(folder,c) for c in r['commands']]
    for row,expected in zip(r['actual_compiled_semantic_controls'],MUTANTS):
        name,member,old,new=expected;need((row['case'],row['file'],row['old'],row['new'])==expected,'Control recipe identity');work=folder/'controls'/name;need(sha(work/'src'/member)==row['mutant_sha256'],'Mutant source');need('independent failure line' in (work/'tests.log').read_text(errors='replace'),'Actual semantic rejection')
        for n in CORE:
            original=(root/MODEL/'src'/n).read_bytes()
            if n==member:
                need(original.decode('utf-8').count(old)==1,'Unique control source anchor')
                original=original.decode('utf-8').replace(old,new).encode('utf-8')
            need((work/'src'/n).read_bytes()==original,'Exact single-change source '+name)
        target=work/('negative.exe' if os.name=='nt' else 'negative')
        need(row['commands'][0]['argv']==[str(v) for v in arguments(compiler,msvc,mode,work/'src',work,target)] and row['commands'][1]['argv']==[str(target)],'Exact negative compile/run recipes')
        need([v['exit'] for v in row['commands']]==[0,1],'Compile passed and semantic assertion failed')
        commands += [(work,c) for c in row['commands']]
    launches=0
    for work,command in commands:
        need(sha(work/command['log'])==command['log_sha256'],'Actual command log')
        if command['log']=='tests.log':
            need(bool(command['host_executable_guard']),'Every launch has a recorded guard')
            need(g.host_executable(Path(command['argv'][0]))==command['host_executable_guard'],'Native host executable reparsed');launches+=1
        else:need(command['host_executable_guard'] is None,'Compile command does not claim a host-test launch guard')
    need(launches==15,'Positive plus fourteen guarded negative executables')
    return {'passed':True,'mode':r['mode'],'receipt_sha256':sha(path),'tests':r['tests'],'actual_compiled_semantic_controls':len(MUTANTS),'host_executables_reparsed':launches,'target_execution':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--positive-only',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.build_root is None and not a.positive_only,'Replay is read-only');print(json.dumps(replay(root,a.replay)));return
    base=a.build_root.resolve() if a.build_root else HERE/'build'/('independent-'+uuid.uuid4().hex);need(base.is_relative_to(HERE/'build') and not base.exists(),'Create-only owned host build directory');print(json.dumps({'passed':True,'results':[verify(root,base/m,m,a.positive_only) for m in (['c','cpp'] if a.language=='both' else [a.language])]}))
if __name__=='__main__':main()
