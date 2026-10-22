#!/usr/bin/env python3
"""Bind already frozen actual HOST/native pairs; seal metadata without binaries."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
NATIVE_CLI='783918ed872b02c62321d1997bb4be2db08447f0f1d1def10a722c209f06fa8f'
HOST_EXPECTED={'c':'6123a01eac010395983a02e2b41b7f375cccfe7538362b5b0757fa7bc5ffbcec',
               'cpp':'7c7332d0b673fb1ed508cc99f35eafda77e8ccf0c50330ed12a2c785387f123f'}
NATIVE_EXPECTED={'c':'08f8303f84124386c4f8ac8cc52813d03f673583aa936140561e0710a95efbee',
                 'cpp':'5c49dbc54130a472250ed848a6ce6ae2b463cc96b7f5fa659f995f13670deee7'}


def need(value,message):
    if not value:raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    path.write_bytes((json.dumps(value,indent=2)+'\n').encode('utf8'))


def close(root,firmware,host_base,native_base):
    need(not (HERE/'seal.json').exists(),'Create-only independent metadata seal')
    case=root/'apk-analysis/tsl9-v4160-event-callback-2026-10-22'
    if not case.exists():case=root/'analysis/v4160-event-callback-2026-10-22'
    need(sha(case/'implementation/verify_native.py')==NATIVE_CLI,'Explicit producer final native freeze')
    layered=runpy.run_path(str(HERE/'review.py'));native=runpy.run_path(str(HERE/'review-native.py'))
    summaries={}
    for mode in ('c','cpp'):
        host=host_base/mode/'verification.json';folder=native_base/mode
        need(sha(host)==HOST_EXPECTED[mode] and sha(folder/'verification.json')==NATIVE_EXPECTED[mode],
             'Final selected actual frozen HOST/native pair '+mode)
        result=layered['inspect'](root,firmware,host,folder)
        need(result['HOST']['tests']==dict(cases=23,checks=3541,conditional_HOST_only=True,
                                         physical_GPR_or_ROM_proof=False),'Exact independent HOST effects')
        need(result['native']['facts']['allocated_bytes']==658 and
             result['native']['facts']['fits_original_extent'] is False,'Actual658 component does not fit632')
        write(HERE/('selected-'+mode+'.json'),result)
        need(result==layered['inspect'](root,firmware,host,folder),'Actual final layered read-only replay '+mode)
        write(HERE/('selected-host-'+mode+'.json'),json.loads(host.read_bytes()))
        write(HERE/('selected-native-'+mode+'.json'),native['inspect'](root,folder))
        summaries[mode]=dict(host_receipt=host.relative_to(root).as_posix(),
                            host_receipt_sha256=HOST_EXPECTED[mode],
                            native_folder=folder.relative_to(root).as_posix(),
                            native_producer_receipt_sha256=NATIVE_EXPECTED[mode],
                            independent_layered_receipt_sha256=sha(HERE/('selected-'+mode+'.json')),
                            native_ELF_sha256=result['native']['ELF_sha256'],
                            HOST=result['HOST']['tests'],compiled_semantic_controls=3,
                            actual_native_ELF_controls=2)
    (HERE/'README.md').write_bytes((HERE/'readme.zh-TW.md').read_bytes())
    write(HERE/'summary.json',dict(schema='TSL9-callback-independent-ABI-summary-v1',selected=summaries,
          producer_native_CLI_sha256=NATIVE_CLI,pure_native_checker_sha256=sha(HERE/'native.py'),
          source_callback_bytes=632,native_callback_bytes=658,native_overflow_bytes=26,
          source_frame_bytes=48,native_frame_bytes=48,physical_frame_layout_equal=False,
          source_raw_controls=5,default_mode='metadata-only',generated_build_artifacts_included=False,
          original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False))
    files=[]
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name!='seal.json':
            raw=path.read_bytes()
            need(b'\r\n' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),
                 'UTF8 LF one final newline '+path.name)
            files.append(dict(path=path.name,bytes=len(raw),sha256=sha(path)))
    write(HERE/'seal.json',dict(schema='TSL9-callback-independent-ABI-metadata-seal-v1',files=files,
          generated_build_artifacts_included=False))
    print(json.dumps(dict(seal_sha256=sha(HERE/'seal.json'),members=len(files),
                         actual_C_CPP_HOST_native_review_passed=True,native_bytes=658,
                         original_full_ABI_admitted=False,placement_admitted=False,hardware_OTA_proved=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--firmware',required=True,type=Path);p.add_argument('--host-base',required=True,type=Path)
    p.add_argument('--native-base',required=True,type=Path);a=p.parse_args()
    close(a.project_root.resolve(),a.firmware.resolve(),a.host_base.resolve(),a.native_base.resolve())
