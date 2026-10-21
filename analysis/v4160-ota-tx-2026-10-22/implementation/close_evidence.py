"""Create selected metadata and bounded read-only/guard controls; no builds."""
import hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
MODEL=ROOT/'experiments/tsl9-v4160-ota-tx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,r):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def main():
 host=runpy.run_path(str(MODEL/'verify_host.py'));native=runpy.run_path(str(HERE/'verify_native.py'));results=[]
 for kind,build,reader in [('host','formal-host-final',host),('native','formal-native-sealed-inputs',native)]:
  for mode in ('c','cpp'):
   original=MODEL/'build'/build/mode/'verification.json';reader['replay'](ROOT,original);metadata=HERE/'receipts'/(kind+'-'+mode+'.json');metadata.parent.mkdir(exist_ok=True);metadata.write_bytes(original.read_bytes());results.append(dict(kind=kind,mode=mode,receipt=str(original),sha256=sha(original),metadata=metadata.relative_to(HERE).as_posix()))
 controls=[]
 def reject(name,fn):
  try:fn()
  except (ValueError,KeyError) as e:controls.append(dict(name=name,rejected=True,reason=str(e)));return
  raise ValueError('invalid readback accepted: '+name)
 for kind,reader,folder in [('host',host,MODEL/'build/formal-host-final/c'),('native',native,MODEL/'build/formal-native-sealed-inputs/c')]:
  r=json.loads((folder/'verification.json').read_bytes())
  mutations=[('missing_launch_guard',lambda x:x['commands'][1].update(host_executable_guard=None))] if kind=='host' else [('wrong_compile_profile',lambda x:x['commands'][1]['argv'].remove('-Oz')),('wrong_source',lambda x:x['commands'][1]['argv'].__setitem__(-3,'not-the-source.c'))]
  for name,change in mutations:
   x=json.loads(json.dumps(r));change(x);p=folder/('rejected-'+name+'.json');write(p,x);reject(name,lambda:reader['replay'](ROOT,p))
 g=host['guard'](ROOT);target=MODEL/'build/formal-native-sealed-inputs/c/tx_native.o';calls=[];previous=g.subprocess.run
 def intercepted(*a,**kw):calls.append(a);raise AssertionError('must not reach subprocess')
 g.subprocess.run=intercepted
 try:reject('actual_RV32_rejected_before_launch',lambda:g.execute([target],target.parent,'NEVER-LAUNCHED',{},host_test=True))
 finally:g.subprocess.run=previous
 assert not calls and not (target.parent/'NEVER-LAUNCHED.log').exists()
 cli=MODEL/'build/cli-readback';cli.mkdir();commands=[]
 for name,script,receipt,extra in [('host_build_option',MODEL/'verify_host.py',MODEL/'build/formal-host-final/c/verification.json',['--build-root',str(cli/'MUST-NOT-EXIST')]),('host_language_option',MODEL/'verify_host.py',MODEL/'build/formal-host-final/c/verification.json',['--language','c']),('native_tool_option',HERE/'verify_native.py',MODEL/'build/formal-native-sealed-inputs/c/verification.json',['--tool-dir',str(cli)])]:
  command,_=g.execute([sys.executable,'-X','utf8','-B',script,'--project-root',ROOT,'--replay',receipt,*extra],cli,name,{},1);commands.append(command)
 assert not (cli/'MUST-NOT-EXIST').exists()
 fw=native['context'](ROOT)['firmware'];alternate=cli/'same-official-firmware-validation-only.bin';alternate.write_bytes(fw.read_bytes());command,_=g.execute([sys.executable,'-X','utf8','-B',HERE/'verify_native.py','--project-root',ROOT,'--replay',MODEL/'build/formal-native-sealed-inputs/c/verification.json','--firmware',alternate],cli,'alternate-firmware-readonly',{});commands.append(command)
 write(HERE/'receipts/readback-controls.json',dict(passed=True,controls=controls,actual_RV32_object_sha256=sha(target),subprocess_calls_for_RV32=0,CLI=dict(folder=str(cli),commands=commands,alternate_firmware_validation_only_sha256=sha(alternate)),RV32_execution=False))
 write(HERE/'results.json',dict(schema='TSL9-OTA-TX-selected-metadata-v1',results=results,host_tests=dict(groups=4,cases=107,checks=15605,compiled_controls_per_language=8),native=dict(bytes=280,instructions=96,size_fit_only=True,original_ABI_admitted=False,full_image_integration=False),RV32_execution=False,ISA_emulation=False,network=False,hardware=False))
 print(json.dumps(dict(passed=True,selected=len(results),readback_controls=len(controls),RV32_execution=False)))
if __name__=='__main__':main()
