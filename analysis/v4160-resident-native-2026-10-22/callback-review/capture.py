"""Create-only original callback operand data and observed ELF role."""
import argparse
import json
from pathlib import Path
import check as C
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--image-elf',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True)
    C.need(C.sha(a.firmware)==C.FW,'Exact original official firmware');raw=a.firmware.read_bytes();old,decode,E,_,_=C.context(root)
    groups={key:old.rows(raw[x-0x8000:y-0x8000],x,decode) for key,(x,y,_,_) in C.RANGES.items()};C.gate(groups);e=E(a.image_elf.resolve(strict=True));role=C.role(e);section=e.byname[role['owner']['name']];at=0x197f0-section['address'];C.need(e.data(section)[at:at+364]==raw[0x117f0:0x1195c],'Actual full code slice agrees with official image')
    data=dict(schema='TSL9-original-callback-and-small-dependencies-v1',firmware_sha256=C.FW,groups=groups,ELF_role=role,initial_observed_ELF_sha256=C.sha(a.image_elf),range_source='Raw instruction partition/control flow; NOTYPE size0 does not prove function extent',all_nested_effects_proved=False)
    with (C.HERE/'ledger.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(callback_bytes=364,callback_rows=130,total_bytes=454,total_rows=167)))
if __name__=='__main__':main()
