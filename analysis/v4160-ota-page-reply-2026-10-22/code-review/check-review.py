#!/usr/bin/env python3
"""Source/metadata default; optional read-only actual host-archive inspection."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SOURCE_SEAL='66484b79f8ef5199e20c8c136797ca7f3ced8b19fc5d2f2f2fb79734a4028a3f'
EXPECTED={'passed':True,'groups':3,'cases':90,'checks':6699,'ordered_effects':21,'target_execution':False}
PRODUCER='d255aed146042a1f73e3ae79096a5948fdc3eafa50558e988062ccfacdd3c8e2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def closed(folder,expected=None):
    if expected:need(sha(folder/'seal.json')==expected,'Immutable source seal')
    for name,pin in read(folder/'seal.json')['members'].items():
        p=(folder/name).resolve();need(p.parent==folder.resolve() and sha(p)==pin,'Closed member '+name)
def actual(root,path,runner):
    path=path.resolve();r=read(path);folder=path.parent;summary=runner.replay(root,path);need(r['tests']==EXPECTED,'Exact independent90/6699 oracle')
    compiler=Path(r['compiler']['path']);mode=r['mode'];need(mode in ('c','cpp'),'Host language');msvc='/nologo' in r['commands'][0]['argv'];exe=folder/('effects.exe' if r['commands'][1]['argv'][0].endswith('.exe') else 'effects')
    need(r['commands'][0]['argv']==[str(x) for x in runner.args(compiler,msvc,mode,root/runner.MODEL/'src',folder,exe)],'Actual positive compile source/flags/output recipe')
    need(r['commands'][1]['argv']==[str(exe)] and all(c['exit']==0 for c in r['commands']),'Actual positive commands/exits')
    for row,(name,member,old,new) in zip(r['actual_compiled_semantic_controls'],runner.MUTANTS):
        work=folder/'controls'/name;src=work/'src';target=work/('negative.exe' if exe.suffix=='.exe' else 'negative')
        for n in runner.CORE:
            expected=(root/runner.MODEL/'src'/n).read_bytes()
            if n==member:expected=(root/runner.MODEL/'src'/n).read_text(encoding='utf-8').replace(old,new).encode('utf-8')
            need((src/n).read_bytes()==expected,'Actual single semantic mutation '+name+'/'+n)
        need(row['commands'][0]['argv']==[str(x) for x in runner.args(compiler,msvc,mode,src,work,target)],'Actual negative compile recipe')
        need(row['commands'][0]['exit']==0 and row['commands'][1]['exit']!=0 and row['commands'][1]['argv']==[str(target)],'Actual compiled semantic rejection')
    return summary
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path,action='append',default=[]);a=p.parse_args();root=a.project_root.resolve();closed(HERE)
    source=HERE.parent/'source-review';closed(source,SOURCE_SEAL);raw=load(source/'source-proof.py','reply_code_review_raw');fresh=raw.inspect(root,a.firmware.resolve());need(len(fresh['raw_controls'])==18,'Fresh original raw operand controls')
    runner=load(HERE/'run-effects.py','reply_code_review_runner');metadata=read(HERE/'selected-receipts.json');need(runner.inputs(root)==metadata['independent_inputs'],'Current frozen core/oracle/runner/host guard/helper identities')
    need(sha(root/runner.MODEL/'verify_host.py')==PRODUCER,'Final producer host CLI identity');need(sha(root/runner.MODEL/'tests/test_page_reply.c')==metadata['producer_test_sha256'],'Canonical producer test identity')
    need({row['mode'] for row in metadata['independent']}=={'c','cpp'} and all(row['tests']==EXPECTED and row['actual_compiled_semantic_controls']==10 for row in metadata['independent']),'Selected independently measured results')
    results=[actual(root,path,runner) for path in a.receipt]
    print(json.dumps({'passed':True,'raw_source_and18controls_rechecked':True,'current_core_identity_rechecked':True,'selected_independent_C_CPP_cases_each':90,'selected_independent_checks_each':6699,'selected_compiled_semantic_controls_each':10,'actual_archived_artifacts_replayed':bool(results),'actual_replays':results,'native_prefix_or_callee_preservation_proved':False,'target_execution':False,'hardware':False,'OTA_ready':False}))
if __name__=='__main__':main()
