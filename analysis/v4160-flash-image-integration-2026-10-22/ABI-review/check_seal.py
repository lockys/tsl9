"""Read-only member verification and fresh semantic replay of both independent receipts."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--project-root',type=Path,default=HERE.parents[2]);ap.add_argument('--firmware',type=Path);ap.add_argument('--parser',type=Path);a=ap.parse_args()
    seal=json.loads((HERE/'seal.json').read_bytes())
    if seal.get('schema')!='TSL9-eleven-image-independent-ABI-seal-v1' or seal.get('passed') is not True:raise ValueError('seal schema/pass')
    for member in seal['members']:
        p=HERE/member['path'];b=p.read_bytes()
        if len(b)!=member['bytes'] or hashlib.sha256(b).hexdigest()!=member['sha256']:raise ValueError('sealed member '+member['path'])
        if b'\r' in b or not b.endswith(b'\n') or b.endswith(b'\n\n'):raise ValueError('new member UTF8/LF/single EOF '+member['path'])
        b.decode('utf-8')
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('Traditional Chinese README copy')
    review=runpy.run_path(str(HERE/'review.py'));results=[review['replay'](a.project_root.resolve(),HERE/'receipts'/f'{mode}.json',a.firmware,a.parser) for mode in ('c','cpp')]
    print(json.dumps(dict(passed=True,sealed_members=len(seal['members']),replays=results),ensure_ascii=False,sort_keys=True))


if __name__=='__main__':main()
