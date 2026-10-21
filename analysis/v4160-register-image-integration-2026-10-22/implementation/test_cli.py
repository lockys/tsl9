"""Read-only CLI and firmware-context regression; never compiles or runs RV32."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import verify_image as V
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();folder=root/V.MODEL/'build/cli-readonly';folder.mkdir();ctx=V.context(root);canonical=ctx['flash']['firmware'].resolve();alternate=folder/'same-ID2966.reference';alternate.write_bytes(canonical.read_bytes());alt=V.context(root,alternate)
    V.need(alt['flash']['firmware'].resolve()==alternate.resolve(),'explicit alternate reference reaches native dependency context');V.need(sha(alternate)==sha(canonical),'same fixed firmware reference only')
    cases=[('c-default','c',[],True),('cpp-default','cpp',[],True),('c-explicit-reference','c',['--firmware',str(canonical)],True),('wrong-language','c',['--language','cpp'],False),('replay-tool-override','c',['--clang',sys.executable],False)]
    records=[]
    for label,mode,extra,passes in cases:
        receipt=root/V.MODEL/'build/formal-final'/mode/'verification.json';argv=[sys.executable,'-X','utf8','-B',str(root/V.MODEL/'verify.py'),'--project-root',str(root),'--replay',str(receipt),*extra];result=subprocess.run(argv,capture_output=True,cwd=root,timeout=180);log=folder/(label+'.log');log.write_bytes(result.stdout+result.stderr);V.need((result.returncode==0)==passes,'bounded CLI result '+label)
        if passes:V.need(json.loads(result.stdout)['passed'],'actual read-only proof replay')
        records.append(dict(case=label,argv=argv,exit=result.returncode,log=log.name,log_sha256=sha(log),passed=True))
    value=dict(passed=True,runner_sha256=sha(H/'verify_image.py'),script_sha256=sha(Path(__file__)),records=records,alternate_reference_context_forwarding=True,alternate_reference_fresh_build_performed=False,reference_sha256=sha(canonical),target_execution=False,compilation=False)
    (folder/'verification.json').write_bytes((json.dumps(value,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),CLI_cases=len(records),alternate_context_test_only=True,target_execution=False)))
if __name__=='__main__':main()
