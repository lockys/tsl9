"""New-scope driver of the immutable, source-owned ten-word scheduling policy."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
PIN='7a516d1098ed0b45cf6c3ff92515f14cf831a3472a32621352a10f1914526d7a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def apply(root,src,dst,receipt):
    tool=root/'experiments/tsl9-v4160-tx-register-abi/postpass/schedule.py';need(sha(tool)==PIN,'immutable ten-word scheduling implementation');m=runpy.run_path(str(tool));ctx=m['context'](root);policy=tool.with_name('policy.json');m['policy_gate'](policy)
    need(src.is_file() and all(not p.exists() for p in (dst,receipt)) and len({src,dst,receipt})==3,'existing input/create-only distinct outputs')
    need(all(p.is_relative_to(root/'experiments/tsl9-v4160-tx-image-integration/build') for p in (dst,receipt)),'new integration build output scope')
    pins={str(p):sha(p) for p in (Path(__file__).resolve(),tool,policy,ctx['parser'],ctx['raw'],src)};e=ctx['ELF'](src);raw,facts=m['transform'](e,ctx['decode']);need(all(sha(Path(p))==s for p,s in pins.items()),'stable scheduling inputs')
    with dst.open('xb') as f:f.write(raw)
    result=dict(schema='TSL9-TX-image-explicit-frame-order-v1',passed=True,input=dict(path=str(src),sha256=sha(src)),output=dict(path=str(dst),sha256=sha(dst)),source_pins=pins,facts=facts,compiler_only=False,new_opcodes_generated=False,original_BIN_codegen_input=False,target_execution=False)
    with receipt.open('xb') as f:f.write((json.dumps(result,indent=2)+'\n').encode())
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path);a=p.parse_args();print(json.dumps(apply(a.project_root.resolve(),a.input.resolve(),a.output.resolve(),a.receipt.resolve())))
