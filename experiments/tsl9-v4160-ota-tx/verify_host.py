#!/usr/bin/env python3
"""Build/run synthetic HOST tests only, behind the immutable machine guard."""
import argparse,hashlib,importlib.util,json,os,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-tx'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GUARD_PIN='76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189'
EXPECTED=dict(passed=True,groups=4,cases=107,checks=15605,synthetic_provider=True,RV32_execution=False)
MUTATIONS=[
 ('stride','src/host_io.h','(v)*TX_ARG5(1062u)','(v)*TX_ARG5(1063u)'),
 ('checksum','src/tx_native.c','checksum=TX_ARG4(checksum+byte);','checksum=TX_ARG4(checksum+1u);'),
 ('metadata_width','src/host_io.h','tx_write(h,(site),(addr),2,(v),1);','tx_write(h,(site),(addr),4,(v),1);'),
 ('ambient_A2','src/host_io.c','tx_set(h,1,site+2u);','tx_set(h,1,site+2u);tx_set(h,12,0u);'),
 ('stale_GP','src/host_io.h','(v)=tx_get(h,3);','(v)=0x20000000u;'),
 ('tail_status','src/host_io.c','if(h->flow==TX_CONTINUE)h->flow=TX_RETURNED;','if(h->flow==TX_CONTINUE){tx_set(h,10,0u);h->flow=TX_RETURNED;}'),
 ('stale_source','src/tx_native.c','TX_LIVE_S1(payload);payload=TX_ARG0(payload+index);','payload=TX_ARG0(source+index);'),
 ('invented_bound','src/tx_native.c','        TX_LIVE_S0(n);\n        if(TX_INDEX0(index)>=n)','        TX_LIVE_S0(n);n=length;\n        if(TX_INDEX0(index)>=n)')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def read(p):return json.loads(p.read_bytes())
def guard(root):
 p=root/GUARD;need(sha(p)==GUARD_PIN,'immutable machine guard');s=importlib.util.spec_from_file_location('ota_tx_guard',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g);return g
def pins(model):return {p.relative_to(model).as_posix():sha(p) for d in ('src','tests') for p in (model/d).glob('*') if p.is_file()}
def args(cc,msvc,mode,model,folder,exe):
 files=[model/'src/tx_native.c',model/'src/host_io.c',model/'tests/test_tx.c']
 if msvc:return [cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTX_HOST_TEST=1','/I'+str(model/'src'),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
 return [cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DTX_HOST_TEST=1','-I',model/'src',*files,'-o',exe]
def verify(root,folder,mode):
 folder.mkdir(parents=True);model=root/MODEL;g=guard(root);src=pins(model);runner=sha(Path(__file__));helper=sha(root/'scripts/portable_verify.py');cc,env,msvc=g.host_tools(root).compiler_for(mode);cc=Path(cc);ccpin=sha(cc);env=dict(env);env.update(TMP=str(folder),TEMP=str(folder));exe=folder/('tests.exe' if os.name=='nt' else 'tests')
 c,_=g.execute(args(cc,msvc,mode,model,folder,exe),folder,'compile',env);t,out=g.execute([exe],folder,'tests',env,host_test=True);tests=json.loads(out);need(tests==EXPECTED,'exact directed host tests')
 controls=[]
 for name,file,old,new in MUTATIONS:
  base=folder/'compiled-controls'/name;base.mkdir(parents=True)
  for n in src:p=base/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model/n).read_bytes())
  p=base/file;text=p.read_text();need(text.count(old)==1,'unique control '+name);p.write_bytes(text.replace(old,new).encode());neg=base/('negative.exe' if os.name=='nt' else 'negative')
  a,_=g.execute(args(cc,msvc,mode,base,base,neg),base,'compile',env);b,_=g.execute([neg],base,'tests',env,1,host_test=True);need('failure line' in (base/'tests.log').read_text(),'actual semantic rejection '+name);controls.append(dict(name=name,file=file,old=old,new=new,commands=[a,b]))
 need(src==pins(model) and runner==sha(Path(__file__)) and helper==sha(root/'scripts/portable_verify.py') and ccpin==sha(cc) and sha(root/GUARD)==GUARD_PIN,'stable exact inputs/tools')
 r=dict(schema='TSL9-OTA-TX-synthetic-host-v1',passed=True,mode=mode,tests=tests,source_sha256=src,runner_sha256=runner,helper_sha256=helper,guard_sha256=GUARD_PIN,compiler=dict(path=str(cc),sha256=ccpin),commands=[c,t],actual_compiled_controls=controls,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},RV32_execution=False,ISA_emulation=False,physical_GPR_prefix=False,native_callee_SP_preservation_proved=False,network=False,hardware=False)
 write(folder/'verification.json',r);return dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),tests=tests)
def replay(root,receipt):
 r=read(receipt);folder=receipt.parent;model=root/MODEL;g=guard(root);need(r['passed'] and r['mode'] in ('c','cpp') and r['source_sha256']==pins(model) and r['runner_sha256']==sha(Path(__file__)) and r['helper_sha256']==sha(root/'scripts/portable_verify.py') and r['guard_sha256']==GUARD_PIN,'current input/runner/guard identities');need(sha(Path(r['compiler']['path']))==r['compiler']['sha256'],'actual compiler identity')
 for n,v in r['artifacts'].items():p=(folder/n).resolve();need(p.is_relative_to(folder.resolve()) and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],'actual host artifact '+n)
 need(read(folder/'tests.log')==r['tests']==EXPECTED,'actual exact tests log');need(len(r['actual_compiled_controls'])==len(MUTATIONS),'exact compiled controls')
 groups=[(folder,r['commands'])]
 cc=Path(r['compiler']['path']);msvc=cc.name.lower()=='cl.exe';mode=r['mode'];exe=folder/('tests.exe' if os.name=='nt' else 'tests')
 need(r['commands'][0]['argv']==[str(x) for x in args(cc,msvc,mode,model,folder,exe)] and r['commands'][1]['argv']==[str(exe)],'exact positive source compile/run recipe')
 need([c['exit'] for c in r['commands']]==[0,0],'positive exits')
 for row,(name,file,old,new) in zip(r['actual_compiled_controls'],MUTATIONS):
  base=folder/'compiled-controls'/name;need((row['name'],row['file'],row['old'],row['new'])==(name,file,old,new),'control identity')
  for n in r['source_sha256']:
   expected=(model/n).read_bytes()
   if n==file:need(expected.decode().count(old)==1,'unique mutation');expected=expected.decode().replace(old,new).encode()
   need((base/n).read_bytes()==expected,'one-change source '+name)
  neg=base/('negative.exe' if os.name=='nt' else 'negative');need(row['commands'][0]['argv']==[str(x) for x in args(cc,msvc,mode,base,base,neg)] and row['commands'][1]['argv']==[str(neg)],'exact actual mutation compile/run recipes');need([x['exit'] for x in row['commands']]==[0,1] and 'failure line' in (base/'tests.log').read_text(),'semantic rejection');groups.append((base,row['commands']))
 for base,commands in groups:
  for i,c in enumerate(commands):
   need(sha(base/c['log'])==c['log_sha256'],'actual command log')
   if i==0:need(c['host_executable_guard'] is None,'compiler command is not a test launch')
   else:need(bool(c['host_executable_guard']) and g.host_executable(Path(c['argv'][0]))==c['host_executable_guard'],'every actual HOST launch has matching machine guard')
 return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),tests=EXPECTED,actual_compiled_controls=len(MUTATIONS),RV32_execution=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--language',choices=['c','cpp','both']);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
 if a.replay:need(a.build_root is None and a.language is None,'replay rejects build-only options');print(json.dumps(replay(root,a.replay.resolve())));return
 language=a.language or 'both';base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('host-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only project build root');print(json.dumps(dict(passed=True,results=[verify(root,base/m,m) for m in (['c','cpp'] if language=='both' else [language])],RV32_execution=False)))
if __name__=='__main__':main()
