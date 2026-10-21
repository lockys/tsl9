"""Read-only native-review seal check and actual C/C++ semantic replay."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=HERE.parents[2]);p.add_argument('--firmware',type=Path);a=p.parse_args();seal=json.loads((HERE/'seal.json').read_bytes())
    if seal.get('schema')!='TSL9-native-register-prefix-independent-review-seal-v1' or seal.get('passed') is not True:raise ValueError('native review seal schema/pass')
    for m in seal['members']:
        b=(HERE/m['path']).read_bytes()
        if len(b)!=m['bytes'] or hashlib.sha256(b).hexdigest()!=m['sha256']:raise ValueError('member '+m['path'])
        b.decode('utf-8')
        if b'\r' in b:raise ValueError('new member LF '+m['path'])
        if m['path'].endswith(('.md','.json','.py','.sh')) and (not b.endswith(b'\n') or b.endswith(b'\n\n')):raise ValueError('single EOF '+m['path'])
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('full Traditional Chinese README')
    review=runpy.run_path(str(HERE/'review.py'));results=[review['replay'](a.project_root.resolve(),HERE/'receipts'/f'{mode}.json',a.firmware) for mode in ('c','cpp')]
    print(json.dumps(dict(passed=True,members=len(seal['members']),replays=results),sort_keys=True))


if __name__=='__main__':main()
