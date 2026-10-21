"""One alternate-reference location regression; target code is never executed."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import verify_native as N
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--build-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();base=a.build_root.resolve();N.need(base.is_relative_to(root) and not base.exists(),'create-only option regression folder');base.mkdir(parents=True)
    ctx=N.context(root);pins=dict(ctx['pins']);pins[str(Path(__file__).resolve())]=sha(Path(__file__));reference=base/'same-ID2966-alternate-location.bin';reference.write_bytes(ctx['firmware'].read_bytes());N.need(sha(reference)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and reference!=ctx['firmware'],'actual pinned bytes at a different location')
    commands=[]
    def run(label,args,expected=0):
        command=[sys.executable,'-B',str(H/'verify_native.py'),'--project-root',str(root),*map(str,args)];r=subprocess.run(command,cwd=root,capture_output=True,timeout=120);log=base/(label+'.log');log.write_bytes(r.stdout+r.stderr);N.need(r.returncode==0 if expected==0 else r.returncode!=0,'CLI option assertion '+label);commands.append(dict(argv=command,exit=r.returncode,log=log.name,log_sha256=sha(log)));return r
    directory=a.tool_dir.resolve();tools={k:N.context(root)['legacy'].resolve_tool(None,directory,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objdump','llvm-objdump')]}
    run('compile-alternate',['--language','c','--build-root',base/'native','--firmware',reference,*[v for k,path in tools.items() for v in ('--'+k,path)]])
    receipt=base/'native/c/verification.json';r=N.read(receipt);N.need(r['mode']=='c','fresh language option honored')
    run('replay-alternate',['--replay',receipt,'--firmware',reference]);failed=run('replay-default-must-reject',['--replay',receipt],1)
    N.need(b'exact source/checker/tool snapshot' in failed.stderr,'default context must not silently substitute alternate reference')
    N.need(all(sha(Path(p))==pin for p,pin in pins.items()),'stable runner/proofs/core during CLI regression')
    result=dict(schema='ID2966-flash-entry-order-CLI-options-v1',passed=True,runner_sha256=sha(H/'verify_native.py'),script_sha256=sha(Path(__file__)),reference=dict(path=str(reference),sha256=sha(reference),alternate_location=True),native_receipt=dict(path=str(receipt),sha256=sha(receipt)),commands=commands,explicit_tools={k:dict(path=str(v),sha256=sha(v)) for k,v in tools.items()},source_sha256=N.CORE,language='c',project_root=str(root),alternate_reference_compile_passed=True,same_explicit_reference_replay_passed=True,wrong_default_context_rejected=True,target_execution=False,hardware=False,network=False)
    path=base/'verification.json';N.write(path,result);print(json.dumps(dict(passed=True,receipt=str(path),sha256=sha(path),target_execution=False)))
if __name__=='__main__':main()
