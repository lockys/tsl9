#!/usr/bin/env python3
"""Create the bounded source/metadata closure after an explicit producer freeze."""
import argparse
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PRODUCER='1e67599d1290092f013d1dde69f8223e1bd7a8a2e3d2c648cfc302d7099c0fc9'
EXPECTED={'c':'9b76a657fae241ab83a598ced274bbd819ffd45dc1c5133d33281f00311bb2e7',
          'cpp':'1de21bcb781f1bb0718d008620eca555dd586a67c6ae650cb228510376afdc1c'}
DEPENDENCIES=(
    'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py',
    'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py',
    'apk-analysis/tsl9-v4160-reply-image-integration-2026-10-22/ABI-review/review.py',
    'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/native.py',
    'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/original.py',
    'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review/raw.py',
    'apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/loop.py',
    'apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/selected-c.json',
    'experiments/tsl9-v4160-frame-schedule/schedule.py',
    'experiments/tsl9-v4160-frame-schedule/frame-policy.json',
    'experiments/tsl9-v4160-reply-abi-order/order.py',
    'experiments/tsl9-v4160-reply-abi-order/order-policy.json',
    'experiments/tsl9-v4160-tx-register-abi/postpass/schedule.py',
    'experiments/tsl9-v4160-tx-register-abi/postpass/policy.json',
    'apk-analysis/tsl9-v4160-tx-image-integration-2026-10-22/implementation/tx_order.py',
    'apk-analysis/tsl9-v4160-tx-image-integration-2026-10-22/implementation/verify_image.py')


def main(root,firmware,folders):
    r=runpy.run_path(str(HERE/'review.py'));b=runpy.run_path(str(HERE/'base.py'))
    need=b['need'];need(not (HERE/'seal.json').exists(),'Create-only final source/metadata seal')
    producer=b['case'](root,'v4160-tx-image-integration-2026-10-22')/'implementation/verify_image.py'
    need(b['sha'](producer)==PRODUCER,'Explicit final producer freeze')
    selected={}
    for mode,folder in folders.items():
        need(b['sha'](folder/'verification.json')==EXPECTED[mode],'Selected actual final producer receipt '+mode)
        receipt=json.loads((folder/'verification.json').read_bytes())
        need(receipt['runner_sha256']==PRODUCER and receipt['mode']==mode and receipt['passed'] is True,
             'Final producer mode/version metadata')
        result=r['inspect'](root,folder,firmware)
        b['write'](HERE/('selected-'+mode+'.json'),result)
        # Read-only replay equality without relying on a producer's passed flag.
        need(result==r['inspect'](root,folder,firmware),'Actual final independent readonly replay '+mode)
        selected[mode]=dict(folder=result['actual_folder'],producer_receipt_sha256=EXPECTED[mode],
                            independent_receipt_sha256=b['sha'](HERE/('selected-'+mode+'.json')),
                            allocations=691,total_RELA=8261,recorded_boundary_refs=30,
                            negative_controls=len(result['checks']['negative_controls']),
                            image=result['checks']['image']['sha256'])
    need(selected['c']['image']==selected['cpp']['image'],'Actual C/C++ image equality')
    (HERE/'README.md').write_bytes((HERE/'readme.zh-TW.md').read_bytes())
    deps=[]
    for name in DEPENDENCIES:
        p=root/name
        if not p.exists() and name.startswith('apk-analysis/tsl9-'):
            p=root/'analysis'/name[len('apk-analysis/tsl9-'):]
        deps.append(dict(path=name,sha256=b['sha'](p)))
    b['write'](HERE/'dependency-pins.json',deps)
    b['write'](HERE/'summary.json',dict(schema='TSL9-TX-full-image-independent-summary-v1',
              selected=selected,producer_runner_sha256=PRODUCER,
              independent_review_sha256=b['sha'](HERE/'review.py'),
              baseline_sha256=r['BASELINE'],approved_nonoriginal_component_sha256=r['APPROVED_LINKED'],
              generated_build_artifacts_included=False,default_mode='metadata-only',
              actual_review_requires_explicit_folder_firmware=True,
              original_BIN_codegen_input=False,original_full_ABI_admitted=False,hardware_OTA_proved=False,
              recorded_boundary_refs=dict(outside_selected=29,page_reply=1,all_calls_enumeration=False)))
    files=[]
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name!='seal.json':
            raw=path.read_bytes()
            need(b'\r\n' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),
                 'UTF8 LF single final newline '+path.name)
            files.append(dict(path=path.name,bytes=len(raw),sha256=b['H'](raw)))
    b['write'](HERE/'seal.json',dict(schema='TSL9-TX-full-image-independent-ABI-seal-v1',
              generated_build_artifacts_included=False,files=files))
    print(json.dumps(dict(seal_sha256=b['sha'](HERE/'seal.json'),members=len(files),
                         actual_final_C_CPP_artifact_review_passed=True,
                         image_sha256=selected['c']['image'],hardware_OTA_proved=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--firmware',required=True,type=Path);p.add_argument('--c',required=True,type=Path)
    p.add_argument('--cpp',required=True,type=Path);a=p.parse_args()
    main(a.project_root.resolve(),a.firmware.resolve(),dict(c=a.c.resolve(),cpp=a.cpp.resolve()))
