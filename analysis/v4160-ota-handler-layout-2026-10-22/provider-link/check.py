#!/usr/bin/env python3
"""Metadata-only partial-provider evidence check; explicit replay reads archives."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def H(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--receipt',type=Path);a=p.parse_args()
    seal=json.loads((HERE/'seal.json').read_bytes())
    for name,pin in seal['members'].items():
        path=(HERE/name).resolve();need(path.is_relative_to(HERE) and H(path)==pin,'Exact partial-link source/metadata '+name)
    for row in seal['dependencies']:
        path=next((a.project_root.resolve()/name for name in row['paths'] if (a.project_root.resolve()/name).is_file()),None)
        need(path is not None and H(path)==row['sha256'],'Exact retained source dependency '+row['paths'][0])
    index=json.loads((HERE/'results.json').read_bytes());need(len(index['results'])==2,'Two retained language metadata receipts')
    for row in index['results']:
        path=HERE/row['metadata'];need(H(path)==row['sha256'],'Byte-identical selected partial metadata')
        r=json.loads(path.read_bytes());q=r['checks']
        need(r['passed'] and r['mode']==row['mode'] and len(q['providers'])==9 and q['remaining_undefined']==['__tsl9v4160_rom_entry'] and q['output_allocations']==692 and q['output_relocations']==8281,'Measured real partial-provider closure')
        need(not q['entry_rerouted'] and not q['final_image'] and not q['JAL_applied_or_range_checked'],'Partial-only boundaries')
    replay=runpy.run_path(str(HERE/'link.py'))['replay'](a.project_root.resolve(),a.receipt) if a.receipt else None
    print(json.dumps(dict(passed=True,metadata_only=a.receipt is None,actual_partial_link_artifacts_read=a.receipt is not None,replay=replay,provider_bindings=9,remaining_undefined=['__tsl9v4160_rom_entry'],entry_rerouted=False,final_image=False,JAL_applied_or_range_checked=False,target_execution=False)))
if __name__=='__main__':main()
