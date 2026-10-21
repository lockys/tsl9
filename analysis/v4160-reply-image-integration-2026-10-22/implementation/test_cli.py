#!/usr/bin/env python3
"""Bounded readonly CLI regression; no compiler or target code is executed."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reply_image_CLI_checked_runner',H/'verify_image.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--build-root',required=True,type=Path);p.add_argument('--receipts-root',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve();folder=a.build_root.resolve();V.need(folder.is_relative_to(root) and not folder.exists(),'create-only project-local CLI evidence');folder.mkdir(parents=True);ctx=V.context(root);canonical=ctx['flash']['firmware'].resolve();records=[];pins={str(H/'verify_image.py'):sha(H/'verify_image.py'),str(Path(__file__)):sha(Path(__file__)),str(root/V.MODEL/'verify.py'):sha(root/V.MODEL/'verify.py'),str(Path(sys.executable)):sha(Path(sys.executable))}
 cases=[('C-default','c',[],True),('CPP-default','cpp',[],True),('C-explicit-reference','c',['--firmware',str(canonical)],True),('wrong-language','c',['--language','cpp'],False),('replay-tool-override','c',['--clang',sys.executable],False)]
 for name,mode,extra,passes in cases:
  receipt=a.receipts_root.resolve()/mode/'verification.json';argv=[sys.executable,'-X','utf8','-B',str(root/V.MODEL/'verify.py'),'--project-root',str(root),'--replay',str(receipt),*extra];r=subprocess.run(argv,capture_output=True,cwd=root,timeout=180);log=folder/(name+'.log');log.write_bytes(r.stdout+r.stderr);V.need((r.returncode==0)==passes,'actual readonly CLI outcome '+name)
  if passes:V.need(json.loads(r.stdout)['passed'],'actual readonly artifacts replayed')
  records.append(dict(case=name,argv=argv,exit=r.returncode,log=log.name,log_sha256=sha(log)))
 V.need(all(sha(Path(n))==pin for n,pin in pins.items()),'stable readonly CLI runner/wrapper/Python/test identities');report=dict(passed=True,runner_sha256=sha(H/'verify_image.py'),script_sha256=sha(Path(__file__)),before_after_pins=pins,records=records,reference_sha256=sha(canonical),compilation=False,RV32_execution=False)
 V.write(folder/'verification.json',report);print(json.dumps(dict(passed=True,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),CLI_cases=5,compilation=False,RV32_execution=False)))
