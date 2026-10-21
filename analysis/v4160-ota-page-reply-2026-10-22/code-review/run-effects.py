#!/usr/bin/env python3
"""Compile independent bounded synthetic C/C++ tests; guard every host launch."""
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
MODEL='experiments/tsl9-v4160-ota-page-reply'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
CORE={'host_io.c':'fb4073a071639cbefae21d2e983e57e55882c30cc4b7a583eb2ade4bca71e444',
      'host_io.h':'e35b951040704fab033c4b834d613fc7e21475fe67a510f48406fb1bef8709a2',
      'page_reply.c':'0b2ea78e7a55dcee6e5adc3857e1b272b9faa578f1c8776b930fd4812abef9f0',
      'page_reply.h':'5f84c99810942eeaaa31ad194751a544cf38c476cc72a45e0c2c81f09d862a1e',
      'reply_io.h':'b6f693cecac98b87a320cbf14d7c23177d48a6b9133c917baed1fb83ae40aa1d'}
MUTANTS=[
 ('narrow_source_index','host_io.h','((value)+(index))','((value)+((index)&65535u))'),
 ('reversed_header_order','page_reply.c','OP_WRITE8(0x9bb6u,buffer+1u,live_index);\n    OP_WRITE8(0x9bbau,buffer,high);','OP_WRITE8(0x9bbau,buffer,high);\n    OP_WRITE8(0x9bb6u,buffer+1u,live_index);'),
 ('cached_copy_base','page_reply.c','base+0x4cu,target','0x4004cu,target'),
 ('wrong_copy_size','host_io.h','#define OP_COPY_SIZE2() op_bind(h,12u,1024u)','#define OP_COPY_SIZE2() op_bind(h,12u,1026u)'),
 ('cached_free_base','page_reply.c','base+0x68u,target','0x40068u,target'),
 ('wrong_free_buffer','page_reply.c','OP_LIVE_S0(buffer);buffer=OP_ARG0(buffer);','buffer=OP_ARG0(0x3200u);'),
 ('cached_restore_SP','host_io.c','read_word(h,site,sp+offset,&value)','read_word(h,site,0x21002000u+offset,&value)'),
 ('normalized_tail_value','host_io.c','result=op_finish(h,event.value,event.value_known);','result=op_finish(h,0u,event.value_known);'),
 ('overwritten_TX_A1','page_reply.c','OP_RESTORE_S0();','OP_ARG1(0u);OP_RESTORE_S0();'),
 ('tail_target_not_masked','host_io.c','event.target=target&~1u;op_set(h,10u,buffer);','event.target=target;op_set(h,10u,buffer);')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,data):path.write_bytes((json.dumps(data,indent=2)+'\n').encode('utf-8'))
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def inputs(root):
    need(sha(root/GUARD)==GUARD_PIN,'Immutable host executable guard')
    for n,pin in CORE.items():need(sha(root/MODEL/'src'/n)==pin,'Frozen source '+n)
    return {'core':CORE,'guard':GUARD_PIN,'portable_helper':sha(root/'scripts/portable_verify.py'),'oracle':sha(HERE/'expected-effects.c'),'runner':sha(Path(__file__))}
def args(compiler,msvc,mode,src,folder,exe):
    files=[src/'page_reply.c',src/'host_io.c',HERE/'expected-effects.c']
    if msvc:return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DOP_HOST_TEST=1','/I'+str(src),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
    return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DOP_HOST_TEST=1','-I',src,*files,'-o',exe]
def verify(root,folder,mode):
    folder.mkdir(parents=True);before=inputs(root);g=load(root/GUARD,'reply_independent_guard');compiler,env,msvc=g.host_tools(root).compiler_for(mode);compiler_pin=sha(compiler);env=dict(env);env['TMP']=str(folder);env['TEMP']=str(folder)
    exe=folder/('effects.exe' if os.name=='nt' else 'effects');cc,_=g.execute(args(compiler,msvc,mode,root/MODEL/'src',folder,exe),folder,'compile',env);tt,out=g.execute([exe],folder,'tests',env,host_test=True);tests=json.loads(out);need(tests['passed'] and tests['groups']==3 and tests['ordered_effects']==21,'Independent complete effect oracle')
    controls=[]
    for name,member,old,new in MUTANTS:
        work=folder/'controls'/name;work.mkdir(parents=True);src=work/'src';src.mkdir()
        for n in CORE:(src/n).write_bytes((root/MODEL/'src'/n).read_bytes())
        path=src/member;text=path.read_text(encoding='utf-8');need(text.count(old)==1,'Unique semantic mutation '+name);path.write_bytes(text.replace(old,new).encode('utf-8'))
        target=work/('negative.exe' if os.name=='nt' else 'negative');c,_=g.execute(args(compiler,msvc,mode,src,work,target),work,'compile',env);t,_=g.execute([target],work,'tests',env,expect=1,host_test=True);need('independent failure line' in (work/'tests.log').read_text(errors='replace'),'Semantic assertion (not compile/launch failure) '+name);controls.append({'case':name,'file':member,'old':old,'new':new,'mutant_sha256':sha(path),'commands':[c,t]})
    need(inputs(root)==before and sha(compiler)==compiler_pin,'Inputs/compiler unchanged throughout')
    result={'schema':'ID2966-page-reply-independent-host-v1','passed':True,'mode':mode,'tests':tests,'inputs':before,'compiler':{'path':str(compiler),'sha256':compiler_pin},'commands':[cc,tt],'actual_compiled_semantic_controls':controls,'artifacts':{p.relative_to(folder).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in folder.rglob('*') if p.is_file()},'RV32_execution':False,'ISA_emulation':False,'native_prefix_proof':False,'native_callee_preservation_proved':False,'network':False,'hardware':False,'OTA_ready':False}
    write(folder/'verification.json',result);return {'receipt':str(folder/'verification.json'),'sha256':sha(folder/'verification.json'),'mode':mode,'tests':tests,'actual_compiled_semantic_controls':len(controls)}
def replay(root,path):
    path=path.resolve();folder=path.parent;r=read(path);need(r['passed'] and r['inputs']==inputs(root),'Actual independent source/runner identity');need(sha(Path(r['compiler']['path']))==r['compiler']['sha256'],'Actual compiler identity');g=load(root/GUARD,'reply_independent_replay_guard')
    for n,pin in r['artifacts'].items():
        member=(folder/n).resolve();need(member.is_relative_to(folder) and member.stat().st_size==pin['bytes'] and sha(member)==pin['sha256'],'Actual independent artifact '+n)
    need(read(folder/'tests.log')==r['tests'],'Positive actual test output');need(len(r['actual_compiled_semantic_controls'])==len(MUTANTS),'Ten actual semantic controls')
    commands=[(folder,c) for c in r['commands']]
    for row,expected in zip(r['actual_compiled_semantic_controls'],MUTANTS):
        name,member,old,new=expected;need((row['case'],row['file'],row['old'],row['new'])==expected,'Exact independent control identity');work=folder/'controls'/name;need(sha(work/'src'/member)==row['mutant_sha256'],'Actual control source');need('independent failure line' in (work/'tests.log').read_text(errors='replace'),'Actual semantic negative output');commands += [(work,c) for c in row['commands']]
    for work,command in commands:
        need(sha(work/command['log'])==command['log_sha256'],'Actual compiler/host log')
        if command['host_executable_guard']:need(g.host_executable(Path(command['argv'][0]))==command['host_executable_guard'],'Reparse native host machine before any future launch')
    return {'passed':True,'mode':r['mode'],'receipt_sha256':sha(path),'tests':r['tests'],'actual_compiled_semantic_controls':len(MUTANTS),'host_executables_reparsed':11,'target_execution':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.build_root is None,'Replay is read-only');print(json.dumps(replay(root,a.replay)));return
    base=a.build_root.resolve() if a.build_root else HERE/'build'/('independent-'+uuid.uuid4().hex);need(base.is_relative_to(HERE/'build') and not base.exists(),'New independent build directory only');print(json.dumps({'passed':True,'results':[verify(root,base/m,m) for m in (['c','cpp'] if a.language=='both' else [a.language])]}))
if __name__=='__main__':main()
