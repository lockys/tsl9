#!/usr/bin/env python3
"""Read-only closure of source-bound hosted review receipts."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=(
    ('experiments/tsl9-v4160-interrupt-init/build/host-949e5d0ee5cc4fec87db802b9e0b0f69-c/verification.json','49d7e2bf6166b22cd6f638df8e777d1c26a8bbf6c058f7dd064399952380d0be'),
    ('experiments/tsl9-v4160-interrupt-init/build/host-9cb4139ed496484b8134791bc72adb88-cpp/verification.json','d31e56fe0f7c7b1eb680e3a447f7e135e39a92b3e61f695a2fa6a0afb6ce4a59'),
)
INDEPENDENT=(
    ('build/independent-902d92401f284658adaad9860c34dfdf-c/verification.json','4a414f643ece2db6af426398b1c4e150f7d46f83ee5703ca2deaad9691c26000'),
    ('build/independent-d12af0cfc05448129ad6af986e2d1418-cpp/verification.json','58d3cb4ac1446009ebd9c5a0ba8d5688ddfc3e3445064426d48abef096c2ec2c'),
)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)

def check():
    records=[];superseded=[]
    for relative,digest in PARENT:
        p=ROOT/relative;need(sha(p)==digest,'Parent receipt identity');r=json.loads(p.read_text())
        need(r['passed'] and r['tests']=={'passed':True,'groups':4,'checks':6680},'Parent behavior suite')
        need(r['source_proof_checked'],'Parent raw-source gate ran')
        original=r['original_source']
        need(original['passed'] and original['source_bytes']==264 and original['instructions']==94 and original['raw_negative_controls_rejected']==94,'Parent exact raw proof')
        need(not any(r[k] for k in ('original_executed','ISA_emulation','physical_IO','OTA_ready')),'Parent boundaries')
        for path,expected in r['source_sha256'].items():need(sha(Path(path))==expected,'Parent current input identity')
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Parent actual compiler identity')
        need(sha(Path(r['executable']))==r['executable_sha256'],'Parent actual hosted executable identity')
        records.append(dict(kind='parent',path=relative,sha256=digest,mode=r['mode'],groups=4,checks=6680))
    for relative,digest in INDEPENDENT:
        p=HERE/relative;need(sha(p)==digest,'Independent receipt identity');r=json.loads(p.read_text())
        need(r['passed'],'Independent review passed')
        need(not any(r[k] for k in ('source_executed','ISA_emulated','physical_IO','native_component_ABI_proved','OTA_ready')),'Independent boundaries')
        for path,expected in r['source_sha256'].items():
            actual=sha(ROOT/path)
            if actual!=expected:
                normalized=path.replace('\\','/')
                need(r['mode']=='c' and normalized=='experiments/tsl9-v4160-interrupt-init/verify.py'
                     and expected=='4119d853e336c082ab57a0a9da802ff6535fda17b78d8681befc7e22868b28ec'
                     and actual=='8d229eb0bbd0c6491b9a9f64b7d098e889bb12f30804a9d621186e7411835865',
                     'Independent current compiled input identity')
                superseded.append(dict(path=normalized,recorded_sha256=expected,current_sha256=actual,
                    reason='Non-compiled parent verification-script context changed after C run; final script bound by both parent receipts and independent C++ receipt.'))
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Independent actual compiler identity')
        need(len(r['variants'])==4,'One original and three compiled mutants')
        for item in r['variants']:
            folder=p.parent/item['variant'];exe=folder/'test.exe'
            if not exe.exists():exe=folder/'test'
            need(item['compiled'] and sha(exe)==item['executable_sha256'],'Actual independently compiled executable')
            need(sha(folder/'interrupt_init.c')==item['source_sha256'],'Actual independently compiled C')
            need(sha(folder/'compiler.log')==item['compiler_log_sha256'],'Actual compiler log')
            if item['variant']=='original':
                need(item['exit_code']==0 and item['tests']=={'passed':True,'groups':4,'checks':34267},'Independent behavior suite')
            else:need(item['exit_code']==17 and item['tests']['rejected'] and item['tests']['failure'].startswith('REVIEW_FAIL '),'Compiled negative actually rejected')
        records.append(dict(kind='independent',path=str(p.relative_to(ROOT)),sha256=digest,mode=r['mode'],groups=4,checks=34267,compiled_negatives=3))
    return dict(schema='TSL9-readable-interrupt-init-code-review-closure-v1',passed=True,blocking_findings=[],receipts=records,superseded_context_inputs=superseded,original_source_bytes=264,original_source_instructions=94,compiled_negatives_rejected=6,source_executed=False,ISA_emulated=False,physical_IO=False,original_ABI_proved=False,OTA_ready=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
