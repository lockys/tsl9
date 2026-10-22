"""Create-only bounded operand ledger from already present candidate references."""
import argparse
import hashlib
import json
from pathlib import Path
import check as C

def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--candidate-root',required=True,type=Path);a=p.parse_args()
    root=a.project_root.resolve(strict=True);decode=C.decoder(root);items=[]
    for item in C.inputs(root,a.candidate_root):
        record={k:v for k,v in item.items() if k not in ('wrapper','core_prefix')}
        for key,pc in [('wrapper',0x20000236),('core_prefix',0x20000040)]:
            record[key]=C.rows(item[key],pc,decode);record[key+'_sha256']=hashlib.sha256(item[key]).hexdigest()
        C.gate(record['wrapper'],record['core_prefix'],record['callback_word_address']);items.append(record)
    data=dict(schema='conditional-slot70-retained-operand-ledger-v1',candidates=items,
              conditional_ISA_profile='Existing LLVM HasVendorXwchc QK_C_SH definition; not installed-device ISA proof',
              Xwchc_format_sha256=C.TD_SHA,installed_identity_proved=False,whole_core_reviewed=False)
    with (C.HERE/'source-ledger.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(candidates=len(items),wrapper_rows=len(items[0]['wrapper']),prefix_rows=len(items[0]['core_prefix']))))
if __name__=='__main__':main()
