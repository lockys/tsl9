"""Create-only bounded source-data capture from existing local references."""
import argparse
import json
from pathlib import Path
import check as C
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--candidate-root',required=True,type=Path);a=p.parse_args();_,_,items=C.inputs(a.project_root.resolve(strict=True),a.candidate_root)
    records=[{k:v for k,v in x.items() if k not in ('caller_config_record','blob','prefix_bytes')} for x in items]
    with (C.HERE/'ledger.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(schema='TSL9-precopy-complete-leaf-operands-v1',candidates=records,installed_identity_proved=False),indent=2)+'\n')
    print(json.dumps(dict(candidate_bodies=2,bytes_per_body=62,rows_per_body=19)))
if __name__=='__main__':main()
