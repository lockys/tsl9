import hashlib,importlib.util,json,os,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3]
p=root/'experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='f1982360434f89dcf661e8b143ae5e9d4822c76d9837ec6bf1c2e94c639713eb'
s=importlib.util.spec_from_file_location('tx_probe_guard',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
model=root/'experiments/tsl9-v4160-ota-tx';base=model/'build'/('host-probe-'+uuid.uuid4().hex)
for mode in ('c','cpp'):
 f=base/mode;f.mkdir(parents=True);exe=f/'test.exe';cc,env,msvc=g.host_tools(root).compiler_for(mode)
 files=[model/'src/tx_native.c',model/'src/host_io.c',model/'tests/test_tx.c']
 if msvc:args=[cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTX_HOST_TEST=1','/I'+str(model/'src'),'/Fo'+str(f)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
 else:args=[cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-DTX_HOST_TEST=1','-I',model/'src',*files,'-o',exe]
 c,_=g.execute(args,f,'compile',env)
 t,out=g.execute([exe],f,'tests',env,host_test=True)
 print(json.dumps(dict(mode=mode,folder=str(f),tests=json.loads(out),commands=[c,t])))
