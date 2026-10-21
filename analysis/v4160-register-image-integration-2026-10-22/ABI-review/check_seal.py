"""Default source/metadata verification only; generated build outputs are not required or replayed."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=HERE.parents[2]);a=p.parse_args();seal=json.loads((HERE/'seal.json').read_bytes())
    if seal.get('schema')!='TSL9-register-image-independent-ABI-metadata-seal-v1' or seal.get('passed') is not True:raise ValueError('independent metadata seal schema/pass')
    for m in seal['members']:
        path=Path(m['path'])
        if path.is_absolute() or '..' in path.parts or 'build' in path.parts or path.suffix not in ('.py','.sh','.md','.json'):raise ValueError('source/receipt/metadata members only')
        b=(HERE/path).read_bytes();b.decode('utf-8')
        if len(b)!=m['bytes'] or hashlib.sha256(b).hexdigest()!=m['sha256']:raise ValueError('member '+m['path'])
        if b'\r' in b or not b.endswith(b'\n') or b.endswith(b'\n\n'):raise ValueError('UTF8/LF/single EOF '+m['path'])
    if (HERE/'README.md').read_bytes()!=(HERE/'readme.zh-TW.md').read_bytes():raise ValueError('full Traditional Chinese README')
    v=runpy.run_path(str(HERE/'review.py'));metadata,_=v['metadata'](a.project_root.resolve());historical=[]
    for mode in ('c','cpp'):
        r=json.loads((HERE/'receipts'/f'{mode}.json').read_bytes())
        if r.get('schema')!='TSL9-independent-register-image-ABI-actual-v1' or not r.get('passed') or r['reviewer_sha256']!=hashlib.sha256((HERE/'review.py').read_bytes()).hexdigest():raise ValueError('historical actual receipt identity')
        if r['producer']['mode']!=mode or len(r['bounded_new_integration_controls'])!=5 or not all(c['rejected'] for c in r['bounded_new_integration_controls']):raise ValueError('historical actual mode/control evidence')
        historical.append(dict(mode=mode,recorded_actual_pass=True,recorded_original_image_identity=r['checks']['image']['sha256']))
    print(json.dumps(dict(passed=True,metadata_only=True,actual_build_replayed=False,generated_build_outputs_required=False,members=len(seal['members']),source_check=metadata,historical_records=historical),sort_keys=True))


if __name__=='__main__':main()
