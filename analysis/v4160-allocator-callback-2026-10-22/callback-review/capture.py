"""Create-only local bounded static ledger. No compiler or target execution."""
import argparse
import json
from pathlib import Path
import check as C
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--candidate-root',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True);decode=C.decoder(root)
    records=[C.capture_record(x,decode) for x in C.candidate_data(root,a.candidate_root)]
    result=dict(schema='TSL9-conditional-callback-owner-ledger-v1',candidates=records,installed_identity_proved=False,computed_or_indirect_writes_excluded=False,zero_state_lifetime_proved=False)
    with (C.HERE/'ledger.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(candidates=2,init_prefix_rows=len(records[0]['init_prefix']),zero_helper_rows=len(records[0]['zero_helper']))))
if __name__=='__main__':main()
