#!/usr/bin/env python3
"""Read-only closure of hosted memory/register commitment evidence."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=(
    ('experiments/tsl9-v4160-clock-registers/build/host-503ee82a7ace4558b82176061482e8a9-c/verification.json','2ac07388bccc32500add619f7379e7f50f1a70862c2a9dfd8615c2a8751f1d35'),
    ('experiments/tsl9-v4160-clock-registers/build/host-c95c3a066f244deb957f96bba77728ff-cpp/verification.json','c8e7b53ca94c03585261eef0d57cabc5d9287350071f2646131b1cb51873441d'),
)
INDEPENDENT=(
    ('build/independent-81702d95d222479793cacaf60ba022e1-c/verification.json','5b391dd9a3e948ba9c766b666541bb4ebea68a13439a0153a452e09f2207df00'),
    ('build/independent-e75a392dc5dc4695ac5d4ca3cf6b17b7-cpp/verification.json','1c9011b62e2054cb6e618ba018c7e2a09208adb7e554f7dbb371ba10c8aab1a3'),
)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)

def check():
    records=[]
    for relative,digest in PARENT:
        p=ROOT/relative;need(sha(p)==digest,'Final parent receipt identity');r=json.loads(p.read_text())
        need(r['passed'] and r['tests']=={'passed':True,'groups':6,'checks':293845},'Final parent complete host test')
        need(r['source_proof_checked'],'Parent raw source proof ran')
        source=r['original_source'];registers=r['register_source']
        need(source['passed'] and source['target_bytes']==214 and source['target_instructions']==69
             and source['raw_operand_mutation_rejections']==50,'Old exact source proof replay')
        need(registers['passed'] and registers['integer_write_allowlists']=={'query18834':[12,13,14,15],'derive1973c':[14,15]}
             and registers['destination_instruction_counts']=={'query18834':44,'derive1973c':8}
             and registers['normal_return_formulas_static_review_only'],'Original decoded register destination facts')
        need(not any(r[k] for k in ('native_registers_checked','original_ABI_proved','original_executed','ISA_emulation','hardware','network','OTA_ready')),'Parent hosted proof boundaries')
        for path,expected in r['source_sha256'].items():
            q=Path(path);need(sha(q if q.is_absolute() else ROOT/q)==expected,'Parent current input identity')
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Parent actual compiler identity')
        need(sha(Path(r['executable']))==r['executable_sha256'],'Parent actual host executable identity')
        records.append(dict(kind='parent',path=relative,sha256=digest,mode=r['mode'],groups=6,checks=293845))
    for relative,digest in INDEPENDENT:
        p=HERE/relative;need(sha(p)==digest,'Independent receipt identity');r=json.loads(p.read_text())
        need(r['passed'] and r['caller_a3_obligation_checked'],'Independent caller/register contract checked')
        need(not any(r[k] for k in ('original_executed','ISA_emulation','physical_IO','actual_native_register_commitments_proved','original_ABI_proved','OTA_ready')),'Independent hosted boundaries')
        for path,expected in r['source_sha256'].items():need(sha(ROOT/path)==expected,'Independent current compiled/evidence input identity')
        need(sha(Path(r['compiler']))==r['compiler_sha256'],'Independent actual compiler identity')
        need(len(r['variants'])==9,'Original and eight actual compiled source variants')
        for variant in r['variants']:
            folder=p.parent/variant['variant'];exe=folder/'test.exe'
            if not exe.exists():exe=folder/'test'
            need(variant['compiled'] and sha(exe)==variant['executable_sha256'],'Actual independent executable identity')
            need(all(sha(folder/name)==h for name,h in variant['source_sha256'].items()),'Actual compiled source/header bytes')
            need(sha(folder/'compiler.log')==variant['compiler_log_sha256'],'Actual compiler log identity')
            if variant['variant']=='original':
                need(variant['exit_code']==0 and variant['tests']=={'passed':True,'groups':4,'cases':5345,'checks':250316},'Independent complete memory/register suite')
            else:
                need(variant['exit_code']==17 and variant['tests']['rejected'] and variant['tests']['failure'].startswith('REVIEW_FAIL '),'Compiled source negative rejected by actual assertion')
        records.append(dict(kind='independent',path=str(p.relative_to(ROOT)),sha256=digest,mode=r['mode'],groups=4,cases=5345,checks=250316,compiled_negatives=8))
    return dict(schema='TSL9-clock-register-reconstruction-review-closure-v1',passed=True,blocking_source_findings=[],
        receipts=records,original_source_bytes=214,original_source_instructions=69,old_raw_mutations_rejected=50,
        original_destination_instruction_counts={'query':44,'fields':8},compiled_source_negatives_rejected=16,
        hosted_normal_return_commitments_checked=True,actual_native_register_commitments_proved=False,
        original_executed=False,ISA_emulation=False,physical_IO=False,original_ABI_proved=False,OTA_ready=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
