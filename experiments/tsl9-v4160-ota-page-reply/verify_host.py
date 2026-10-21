#!/usr/bin/env python3
"""Only compiled native-host synthetic providers are executed; no RV32 execution."""
import argparse,hashlib,importlib.util,json,os,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-page-reply'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
EXPECTED=dict(passed=True,groups=3,cases=87,checks=3634,synthetic_provider=True,RV32_execution=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise ValueError(m)
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def read(p):return json.loads(p.read_bytes())
def guard(root):
 p=root/GUARD;need(sha(p)==GUARD_PIN,'immutable host-machine guard dependency');s=importlib.util.spec_from_file_location('page_reply_host_guard',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def compile_args(compiler,msvc,mode,model,folder,exe):
 files=[model/'src/page_reply.c',model/'src/host_io.c',model/'tests/test_page_reply.c']
 if msvc:return [compiler,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DOP_HOST_TEST=1','/I'+str(model/'src'),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
 return [compiler,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DOP_HOST_TEST=1','-I',model/'src',*files,'-o',exe]
def source_pins(model):return {p.relative_to(model).as_posix():sha(p) for d in ('src','tests') for p in (model/d).glob('*') if p.is_file()}
MUTATIONS=[
 ('header_low_wrong','src/page_reply.c','buffer+1u,live_index','buffer+1u,high'),
 ('narrow_full_index','src/host_io.h','((value)+(index))','((value)+((index)&65535u))'),
 ('stale_copy_base','src/page_reply.c','base+0x4cu,target','0x4004cu,target'),
 ('stale_stack_restore','src/host_io.c','sp+offset,&value','0x20001000u+offset,&value'),
 ('stale_free_buffer','src/page_reply.c','OP_LIVE_S0(buffer);buffer=OP_ARG0(buffer);','buffer=OP_ARG0(0x3000u);'),
 ('normalized_tail_result','src/host_io.c','result=op_finish(h,event.value,event.value_known);','result=op_finish(h,0u,event.value_known);')]
def verify(root,folder,mode):
 folder.mkdir(parents=True);model=root/MODEL;g=guard(root);runner=sha(Path(__file__));helper=sha(root/'scripts/portable_verify.py');pins=source_pins(model);compiler,env,msvc=g.host_tools(root).compiler_for(mode);cp=sha(compiler);env=dict(env);env['TMP']=str(folder);env['TEMP']=str(folder)
 exe=folder/('host-tests.exe' if os.name=='nt' else 'host-tests');c,_=g.execute(compile_args(compiler,msvc,mode,model,folder,exe),folder,'compile',env);t,output=g.execute([exe],folder,'tests',env,host_test=True);tests=json.loads(output);need(tests==EXPECTED,'exact frozen directed full-index/live-frame/prefix groups')
 controls=[]
 for name,file,old,new in MUTATIONS:
  base=folder/'compiled-controls'/name;base.mkdir(parents=True)
  for n in pins:p=base/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model/n).read_bytes())
  p=base/file;text=p.read_text(encoding='utf-8');need(text.count(old)==1,'one bounded mutation '+name);p.write_bytes(text.replace(old,new).encode());out=base/('negative.exe' if os.name=='nt' else 'negative');cc,_=g.execute(compile_args(compiler,msvc,mode,base,base,out),base,'compile',env);tt,_=g.execute([out],base,'tests',env,1,host_test=True);need('failure line' in (base/'tests.log').read_text(errors='replace'),'semantic assertion rejection '+name);controls.append(dict(name=name,commands=[cc,tt],file=file,old=old,new=new))
 need(pins==source_pins(model) and cp==sha(compiler) and runner==sha(Path(__file__)) and helper==sha(root/'scripts/portable_verify.py') and sha(root/GUARD)==GUARD_PIN,'stable sources/runner/helper/compiler/guard')
 r=dict(schema='TSL9-page-reply-synthetic-host-v1',passed=True,mode=mode,tests=tests,source_sha256=pins,runner_sha256=runner,helper_sha256=helper,guard_sha256=GUARD_PIN,compiler=dict(path=str(compiler),sha256=cp),commands=[c,t],actual_compiled_controls=controls,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},RV32_execution=False,ISA_emulation=False,physical_GPR_prefix=False,native_callee_SP_preservation_proved=False,network=False,hardware=False)
 write(folder/'verification.json',r);return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),tests=tests)
def replay(root,receipt):
 r=read(receipt);folder=receipt.parent;g=guard(root);need(r['passed'] and r['runner_sha256']==sha(Path(__file__)) and r['helper_sha256']==sha(root/'scripts/portable_verify.py') and r['source_sha256']==source_pins(root/MODEL),'host receipt current source/runner/helper identity');need(sha(Path(r['compiler']['path']))==r['compiler']['sha256'],'actual compiler identity')
 for n,pin in r['artifacts'].items():p=(folder/n).resolve();need(p.is_relative_to(folder.resolve()) and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'actual host artifact '+n)
 need(read(folder/'tests.log')==r['tests']==EXPECTED,'exact positive tests actual output')
 need(r['commands'][0]['exit']==r['commands'][1]['exit']==0,'successful positive compile/run')
 for c in r['commands']:need(sha(folder/c['log'])==c['log_sha256'],'positive command logs')
 for row,(name,file,old,new) in zip(r['actual_compiled_controls'],MUTATIONS):
  base=folder/'compiled-controls'/name;need((row['name'],row['file'],row['old'],row['new'])==(name,file,old,new),'bounded control identity')
  for n in r['source_sha256']:
   expected=(root/MODEL/n).read_bytes()
   if n==file:need(expected.decode().count(old)==1,'unique original mutation');expected=expected.decode().replace(old,new).encode()
   need((base/n).read_bytes()==expected,'actual one-change compiled source control')
  need(row['commands'][0]['exit']==0 and row['commands'][1]['exit']!=0 and 'failure line' in (base/'tests.log').read_text(errors='replace'),'actual compiled semantic rejection')
  for c in row['commands']:need(sha(base/c['log'])==c['log_sha256'],'negative command log')
 for command in r['commands']+[c for x in r['actual_compiled_controls'] for c in x['commands']]:
  exe=Path(command['argv'][0]);log=exe.parent/command['log'] if command['host_executable_guard'] else None
  if command['host_executable_guard']:need(g.host_executable(exe)==command['host_executable_guard'] and sha(log)==command['log_sha256'],'read-only reinspection guarded executable/run log')
 need(len(r['actual_compiled_controls'])==6,'six actual compiled negative controls');return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),tests=r['tests'],actual_compiled_controls=6,RV32_execution=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
 if a.replay:print(json.dumps(replay(root,a.replay.resolve())));return
 base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('host-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only build root inside project');print(json.dumps(dict(passed=True,results=[verify(root,base/m,m) for m in (['c','cpp'] if a.language=='both' else [a.language])],RV32_execution=False)))
if __name__=='__main__':main()
