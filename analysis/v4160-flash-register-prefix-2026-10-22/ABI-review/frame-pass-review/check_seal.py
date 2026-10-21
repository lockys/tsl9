"""Read-only frame-audit member verification and pure semantic replay."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=HERE.parents[3]);a=p.parse_args();s=json.loads((HERE/'seal.json').read_bytes())
    if s.get('schema')!='TSL9-independent-frame-scheduling-audit-seal-v1' or not s.get('passed'):raise ValueError('frame audit seal schema/pass')
    for m in s['members']:
        b=(HERE/m['path']).read_bytes()
        if len(b)!=m['bytes'] or hashlib.sha256(b).hexdigest()!=m['sha256']:raise ValueError('member '+m['path'])
        if m['path'].endswith(('.json','.md','.py','.sh')):
            b.decode('utf-8')
            if b'\r' in b or not b.endswith(b'\n') or b.endswith(b'\n\n'):raise ValueError('UTF8/LF/single EOF '+m['path'])
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('full Traditional Chinese README')
    v=runpy.run_path(str(HERE/'audit.py'));result=v['replay'](a.project_root.resolve(),HERE/'report.json');print(json.dumps(dict(passed=True,members=len(s['members']),replay=result),sort_keys=True))


if __name__=='__main__':main()
