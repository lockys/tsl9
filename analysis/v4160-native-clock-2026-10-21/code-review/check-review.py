#!/usr/bin/env python3
"""Read-only receipt closure; executes no compiled program or firmware."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=(
    ('experiments/tsl9-v4160-native-clock/build/host-92a26eb7bd794589aaf41679bae912bf-c/verification.json','0a2b188b15d28d554be0f2a23177c0c6683aa929f02435e0f1a3633524382b83'),
    ('experiments/tsl9-v4160-native-clock/build/host-a9ce3c604c40411aba95caefbeb90ff6-cpp/verification.json','8b15b8847a2988b7ccce99d84c28b72e1b876e3c3eb94aaf17680cabe451d420'),
)
INDEPENDENT=(
    ('build/independent-791d7e88cda24c628de5bf0df3f0dc99-c/verification.json','b00d4f3929e62a9c95db61f1befc042808949d6eb34f4f97f4944763f891cfd3'),
    ('build/independent-9e7076b5fc5245da9e41c6b8ead6d664-cpp/verification.json','64f359db0030dcf734bced6c0286c8220e7cc7da22671b55e6977f93996ad240'),
)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)

def check():
    records=[]
    for relative,digest in PARENT:
        p=ROOT/relative;need(sha(p)==digest,'Final parent receipt identity');r=json.loads(p.read_text())
        need(r['passed'] and r['tests']=={'passed':True,'groups':6,'checks':269618},'Final complete parent suite')
        need(r['source_proof_checked'],'Parent original-byte gate ran')
        original=r['original_source']
        need(original['passed'] and original['target_bytes']==214 and original['target_instructions']==69
             and original['raw_operand_mutation_rejections']==50,'Parent exact old source proof replay')
        need(not any(r[k] for k in ('original_executed','ISA_emulation','hardware','network','original_ABI_proved','native_BIN','OTA_ready')),'Parent proof boundaries')
        for path,expected in r['source_sha256'].items():
            q=Path(path);q=q if q.is_absolute() else ROOT/q
            need(sha(q)==expected,'Parent current input identity')
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Parent actual compiler identity')
        need(sha(Path(r['executable']))==r['executable_sha256'],'Parent actual hosted executable identity')
        records.append(dict(kind='parent',path=relative,sha256=digest,mode=r['mode'],groups=6,checks=269618))
    for relative,digest in INDEPENDENT:
        p=HERE/relative;need(sha(p)==digest,'Independent receipt identity');r=json.loads(p.read_text())
        need(r['passed'],'Independent compiled review passed')
        need(not any(r[k] for k in ('original_executed','ISA_emulation','physical_IO','original_ABI_proved','OTA_ready')),'Independent boundaries')
        for path,expected in r['source_sha256'].items():need(sha(ROOT/path)==expected,'Independent current input identity')
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Independent actual compiler identity')
        need(len(r['variants'])==6,'One original and five compiled mutants')
        for variant in r['variants']:
            folder=p.parent/variant['variant'];exe=folder/'test.exe'
            if not exe.exists():exe=folder/'test'
            need(variant['compiled'] and sha(exe)==variant['executable_sha256'],'Actual independent executable identity')
            need(sha(folder/'native_clock.c')==variant['source_sha256'],'Actual independent C identity')
            need(sha(folder/'compiler.log')==variant['compiler_log_sha256'],'Actual independent compiler log')
            if variant['variant']=='original':
                need(variant['exit_code']==0 and variant['tests']=={'passed':True,'groups':4,'cases':5345,'checks':214811},'Independent complete behavior suite')
            else:
                need(variant['exit_code']==17 and variant['tests']['rejected']
                     and variant['tests']['failure'].startswith('REVIEW_FAIL '),'Compiled mutant rejected at runtime')
        records.append(dict(kind='independent',path=str(p.relative_to(ROOT)),sha256=digest,mode=r['mode'],groups=4,cases=5345,checks=214811,compiled_negatives=5))
    return dict(schema='TSL9-readable-native-clock-code-review-closure-v1',passed=True,blocking_findings=[],
        receipts=records,original_source_bytes=214,original_source_instructions=69,old_raw_mutations_rejected=50,
        compiled_behavioral_negatives_rejected=10,original_executed=False,ISA_emulation=False,
        physical_IO=False,original_ABI_proved=False,OTA_ready=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
