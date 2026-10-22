"""Create-only original operand ledger and observed helper ELF role."""
import argparse
import json
from pathlib import Path
import check as C
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--image-elf',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True)
    C.need(C.sha(a.firmware)==C.FW,'Official original ID2966');data=a.firmware.read_bytes();decode,E=C.context(root);groups={key:C.rows(data[x-0x8000:y-0x8000],x,decode) for key,(x,y) in C.RANGES.items()};C.gate(groups)
    e=E(a.image_elf.resolve(strict=True));symbol=next(s for s in e.symbols if s['name']=='__tsl9v4160_call_18f56');owner=e.sections[symbol['index']]
    C.need(e.data(owner)==data[0x10f56:0x10f88],'Actual original helper matches observed linked section')
    record=dict(schema='TSL9-original-six-byte-helper-ledger-v1',firmware_sha256=C.FW,groups=groups,helper_ELF_role=dict(owner={k:owner[k] for k in ('name','type','flags','address','size','alignment')},canonical_symbols=[{k:symbol[k] for k in ('name','value','size','info','other')}]),initial_observed_ELF_sha256=C.sha(a.image_elf),normal_static_path_only=True,whole_config_lifetime_proved=False)
    with (C.HERE/'ledger.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(helper_rows=len(groups['helper']),caller_rows=len(groups['caller']))))
if __name__=='__main__':main()
