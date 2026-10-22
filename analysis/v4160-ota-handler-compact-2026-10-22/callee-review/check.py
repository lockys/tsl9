#!/usr/bin/env python3
"""Metadata default; explicit firmware performs actual bounded static reads."""
import argparse,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--candidate-root',type=Path);p.add_argument('--original-object',type=Path);a=p.parse_args()
    s=importlib.util.spec_from_file_location('UID_callee_readonly_review',HERE/'review.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R);root=a.project_root.resolve(strict=True)
    if (HERE/'seal.json').exists():R.closed(HERE,R.sha(HERE/'seal.json'))
    if a.firmware:result=R.inspect(root,a.firmware,a.candidate_root,a.original_object)
    else:
        R.need(a.candidate_root is None and a.original_object is None,'Artifact/source overrides require explicit firmware read')
        old=R.case(root,'v4160-ota-handler-2026-10-22')/'source-review';R.closed(old,R.OLD_SEAL)
        pins=R.read(HERE/'reference-pins.json');retained=R.read(HERE/'copy-instructions.json');R.need(len(pins['candidate_files'])==2 and len(retained)==18,'Bounded two-candidate metadata and18 retained rows')
        R.need(__import__('hashlib').sha256(b''.join(bytes.fromhex(r['raw_hex']) for r in retained)).hexdigest()==R.COPY_SHA,'Recorded body byte-pin consistency; not an actual external body read')
        result=dict(schema='ID2966-UID-callee-metadata-v1',passed=True,metadata_only=True,candidate_body_sha256=R.COPY_SHA,candidate_body_pins_checked=True,actual_original_firmware_read=False,actual_candidate_source_bodies_read=0,actual_App_carrier_replayed=False,raw_operand_controls_replayed=False,dropping_ambient_args_authorized=False,installed_resident_identity_proved=False,transitive_original_ABI_proved=False,HOST_or_compiler_run=False,target_execution=False,ISA_emulation=False,network=False,hardware=False)
    print(json.dumps(result))
if __name__=='__main__':main()
