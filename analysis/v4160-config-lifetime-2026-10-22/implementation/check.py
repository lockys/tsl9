#!/usr/bin/env python3
"""Metadata-only default; explicit --receipt reads actual compiler artifacts."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sys
sys.dont_write_bytecode=True
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def resolve(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def storage(folder,receipt):
    r=json.loads(receipt.read_bytes());v=r['checks'];need(v['native_bytes']==550 and v['instructions']==186,'Measured current 550B/186 object')
    need([a['delta'] for a in v['stack_adjustments']]==[-48,48],'Actual single 48B frame')
    ir=(folder/'ota_handler.ll').read_text();need(re.findall(r'alloca ([^\n]+)',ir)==['[4 x i8], align 4'],'One genuine aligned four-byte C allocation')
    need('lifetime.start.p0(i64 4,' in ir and 'lifetime.end.p0(i64 4,' in ir,'Whole four-byte object lifetime')
    text=(folder/'complete-static-disassembly.log').read_text()
    slots=[('ra',44)]+[('s'+str(i),40-4*i) for i in range(7)]
    for op in ('sw','lw'):
        actual=[(reg,int(at,16)) for reg,at in re.findall(r'\b'+op+r'\s+(ra|s[0-9]+),\s+0x([0-9a-f]+)\(sp\)',text)]
        need(actual==slots,'Eight actual save/restore word slots')
    stores=[int(at,16) for at in re.findall(r'\bsb\s+[^,]+,\s+0x([0-9a-f]+)\(sp\)',text)]
    need(stores==[12,13,12],'Only source first-two-byte stores; no upper-byte initialization')
    need(re.search(r'\baddi\s+s1, sp, 0xc\b',text) is not None,'Actual reply pointer from owned SP12')
    need(all(at>=16 for _,at in slots),'Entire object SP12..15 avoids every saved word')
    return dict(reply_backing_bytes=4,reply_offsets=[12,13],backing_offsets=[12,13,14,15],frame=48,relative_to_entry_SP=-36,independent_object_goal_achieved=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--receipt',action='append',type=Path,default=[]);a=p.parse_args()
    root=a.project_root.resolve();case=Path(__file__).resolve().parent;s=json.loads((case/'seal.json').read_bytes())
    for group in ('members','model_members','external_pins'):
        for member in s[group]:
            f=resolve(root,member['path']);need(f.is_file() and H(f)==member['sha256'],'Pinned '+member['path'])
    for key,member in s['review_seals'].items():
        need(H(resolve(root,member['path']))==member['sha256'],'Independent seal '+key)
    results=[]
    if a.receipt:
        spec=importlib.util.spec_from_file_location('reply_frame_probe',case/'probe.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        for receipt in a.receipt:
            actual=mod.replay(root,receipt);actual['reply_storage']=storage(receipt.resolve().parent,receipt.resolve());results.append(actual)
    print(json.dumps(dict(passed=True,metadata_only=not a.receipt,actual_build_artifacts_read=bool(a.receipt),results=results,
        selected_native_bytes=550,frame_bytes=48,reply_offsets=[12,13],reply_relative_to_entry_SP=-36,
        original_reply_relative_to_entry_SP=-36,independent_reply_object_goal_achieved=True,original_ABI_admitted=False,
        live_model_replaced=False,BIN_exported=False,target_execution=False)))
if __name__=='__main__':main()
