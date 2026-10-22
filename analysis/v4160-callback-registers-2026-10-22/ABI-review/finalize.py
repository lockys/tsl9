#!/usr/bin/env python3
"""Close the actual selected profile evidence without shipping compiled artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
RUNNER='6e35d93ca70c258244dd5fd47e91d18d4c8a6cfd09a87bc8e58d63eaad299657'
EXPECTED={'c':'6613db876bdf1c6980b5dee782b41b9b81d14986881c1679bf67c4c15c08e98b',
          'cpp':'bb7892655bf304a1bcc9ce9a61444fd88e152f9f14d939668e17316250d03208'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def write(path,value):path.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf8'))


def close(root,base):
    need(not (HERE/'seal.json').exists(),'Create-only independent metadata seal')
    case=root/'apk-analysis/tsl9-v4160-callback-registers-2026-10-22'
    if not case.exists():case=root/'analysis/v4160-callback-registers-2026-10-22'
    need(sha(case/'implementation/verify_native.py')==RUNNER,'Explicit final producer freeze')
    module=runpy.run_path(str(HERE/'review-ordered.py'));selected={}
    for mode in ('c','cpp'):
        pre=base/'pre'/mode;folder=base/'ordered'/mode
        need(sha(folder/'verification.json')==EXPECTED[mode],'Actual selected final native receipt '+mode)
        result=module['inspect'](root,pre,folder);write(HERE/('selected-'+mode+'.json'),result)
        need(result==module['inspect'](root,pre,folder),'Actual final independent readonly replay '+mode)
        selected[mode]=dict(pre=result['actual_pre'],ordered=result['actual_folder'],
                            producer_receipt_sha256=EXPECTED[mode],
                            independent_receipt_sha256=sha(HERE/('selected-'+mode+'.json')),
                            ordered_ELF_sha256=result['ordered_ELF_sha256'],
                            raw_countercases=len(result['source']['actual_artifact_countercases']),
                            frame_countercases=len(result['scheduling']['controls']))
    need(selected['c']['ordered_ELF_sha256']==selected['cpp']['ordered_ELF_sha256'],'Actual C/C++ ordered ELF equality')
    (HERE/'README.md').write_bytes((HERE/'readme.zh-TW.md').read_bytes())
    paths=[case/'implementation/verify_native.py',case/'implementation/probe_gp.py',
           case/'implementation/source_gate.py',root/'experiments/tsl9-v4160-callback-registers/postpass/frame.py']
    paths += [root/'experiments'/model/'src'/name for model in
              ('tsl9-v4160-callback-registers','tsl9-v4160-event-callback')
              for name in ('callback.c','callback.h','io.h')]
    field=runpy.run_path(str(HERE/'fields.py'))
    for slug in field['PINS']:
        paths.append(next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_file()))
    write(HERE/'source-pins.json',[dict(path=p.relative_to(root).as_posix(),sha256=sha(p)) for p in paths])
    write(HERE/'summary.json',dict(schema='TSL9-callback-register-independent-summary-v1',selected=selected,
          producer_runner_sha256=RUNNER,raw_review_sha256=sha(HERE/'review.py'),
          ordered_review_sha256=sha(HERE/'review-ordered.py'),
          original_bytes=632,sealed_baseline_bytes=658,reservation_only_bytes=656,
          selected_bytes=624,instructions=223,frame_bytes=48,existing_save_words_swapped=2,
          changed_object_bytes=4,GP_reads=6,GP_writes=0,S10_S11_encoded_uses=0,
          mathematical_size_fits=True,whole632_storage_covered=False,unowned_original_tail_bytes=8,
          original_relative_save_order_matched=True,whole_original_prefix_equal=False,
          HOST_suite_rerun=False,target_execution=False,ISA_emulation=False,
          original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False,
          default_mode='metadata-only',generated_build_artifacts_included=False))
    files=[]
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name!='seal.json':
            raw=path.read_bytes()
            need(b'\r\n' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),
                 'UTF8 LF one final newline '+path.name)
            files.append(dict(path=path.name,bytes=len(raw),sha256=sha(path)))
    write(HERE/'seal.json',dict(schema='TSL9-callback-register-independent-metadata-seal-v1',files=files,
          generated_build_artifacts_included=False))
    print(json.dumps(dict(seal_sha256=sha(HERE/'seal.json'),members=len(files),
                         actual_C_CPP_native_readback_passed=True,bytes=624,
                         whole632_storage_covered=False,original_full_ABI_admitted=False,
                         placement_admitted=False,hardware_OTA_proved=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--base',required=True,type=Path);a=p.parse_args();close(a.project_root.resolve(),a.base.resolve())
