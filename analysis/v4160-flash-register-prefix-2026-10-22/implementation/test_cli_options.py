"""Bounded read-only replay-option regression; no target executable is launched."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();model=root/'experiments/tsl9-v4160-flash-register-prefix';folder=model/'build/cli-options';folder.mkdir();native=H/'verify_native.py';reference=model/'build/alternate-ID2966.reference';receipt=model/'build/cli-alternate/c/verification.json';r=json.loads(receipt.read_bytes())
    need(sha(reference)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and str(reference.resolve()) in r['input_pins'],'actual alternate-location input used by compiled C receipt')
    cases=[('explicit-reference',['--firmware',str(reference),'--language','c'],True),('wrong-default-reference',[],False),('wrong-language',['--firmware',str(reference),'--language','cpp'],False),('replay-tool-override',['--firmware',str(reference),'--clang',sys.executable],False),('replay-build-root',['--firmware',str(reference),'--build-root',str(folder/'unused')],False)]
    commands=[]
    for label,options,expected in cases:
        argv=[sys.executable,'-X','utf8','-B',str(native),'--project-root',str(root),'--replay',str(receipt),*options];result=subprocess.run(argv,capture_output=True,timeout=120,cwd=root);log=folder/(label+'.log');log.write_bytes(result.stdout+result.stderr)
        need((result.returncode==0)==expected,'CLI option result '+label);commands.append(dict(case=label,argv=argv,exit=result.returncode,log=log.name,log_sha256=sha(log),passed=True))
    output=dict(passed=True,runner_sha256=sha(native),script_sha256=sha(Path(__file__)),alternate_compile_receipt_sha256=sha(receipt),alternate_reference_compile_passed=True,same_explicit_reference_replay_passed=True,wrong_default_context_rejected=True,wrong_language_rejected=True,replay_build_and_tool_override_rejected=True,commands=commands,target_execution=False)
    (folder/'verification.json').write_bytes((json.dumps(output,indent=2)+'\n').encode());print(json.dumps(output))
if __name__=='__main__':main()
