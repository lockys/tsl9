#!/usr/bin/env python3
"""Verify the exact twelve-owner plan and current generation dependencies.

Default checks source/metadata only; no historical .o or BIN is opened.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MANIFEST_SHA = '2bac53620548772e2e06197dd52b9e0ca6e50a7f88d27b6f39fd1fddf2ac3f78'
PARENT_SHA = '2ac3a0e317f7e67d30306be8e50e4ed53e9f794596a12ae5a29ab3ced14047d0'
CASE_FILES = ['README.md', 'readme.zh-TW.md', 'readme.en.md', 'prepare-plan.py',
              'source-manifest.json', 'verification.json', 'check-plan.py']


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(root, relative):
    path = root/relative
    if not path.is_file() and relative.startswith('apk-analysis/tsl9-'):
        path = root/relative.replace('apk-analysis/tsl9-', 'analysis/', 1)
    need(path.is_file() and path.resolve().is_relative_to(root), 'Contained known dependency '+relative)
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--seal', action='store_true')
    a = p.parse_args()
    root = a.project_root.resolve()
    manifest_path = HERE/'source-manifest.json'
    need(sha(manifest_path) == MANIFEST_SHA, 'Exact actual-derived twelve-owner ledger')
    need(sha(root/'experiments/tsl9-v4160-register-image-integration/source-manifest.json') == PARENT_SHA,
         'Exact immutable eleven-owner ancestor')
    manifest = json.loads(manifest_path.read_bytes())
    for name, pin in manifest['source_files'].items():
        need(sha(locate(root, name)) == pin, 'Current native source/header '+name)
    for group in ('frame_schedule_source_files', 'reply_order_source_files'):
        for name, pin in manifest[group].items():
            need(sha(locate(root, name)) == pin, 'Exact explicit source-owned ABI backend '+name)
    for key in ('reply_boundary_filter', 'reply_native_profile'):
        item = manifest[key]
        need(sha(locate(root, item['path'])) == item['sha256'], 'Exact supported reply helper')
    resource = Path(manifest['compiler_resource_directory']).resolve()
    for item in manifest['compiler_resource_header_inputs']:
        path = Path(item['path']).resolve()
        need(path.is_relative_to(resource) and path.relative_to(resource).as_posix() == item['resource_relative']
             and sha(path) == item['sha256'], 'Actual compiler resource header identity')
    reply = root/'analysis/v4160-ota-page-reply-2026-10-22'
    if not reply.is_dir():
        reply = root/'apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22'
    need(sha(reply/'entry-call-correction/seal.json') == manifest['incoming_call']['correction_seal_sha256'],
         'Exact incoming C.JAL correction')
    need(len(manifest['selected_sections']) == 12 and len(manifest['retained_storage']) == 679
         and manifest['retained_RELA_count'] == 8257 and len(manifest['external_incoming_RELA']) == 21,
         'Exact actual original-role partition')
    need(manifest['full_twelve_function_image_build_completed'] is False,
         'Plan alone does not assert a completed image')
    members = [dict(path=name, bytes=(HERE/name).stat().st_size, sha256=sha(HERE/name)) for name in CASE_FILES]
    seal = dict(schema='TSL9-twelve-function-image-plan-seal-v1', members=members,
                metadata_only=True, actual_old_object_replayed_by_default=False,
                full_image_build_completed=False, hardware=False, OTA_ready=False)
    output = HERE/'seal.json'
    if a.seal:
        need(not output.exists(), 'Create-only new scope seal')
        with output.open('xb') as out:
            out.write((json.dumps(seal, indent=2)+'\n').encode())
    else:
        need(json.loads(output.read_bytes()) == seal, 'Exact complete plan seal')
    need((HERE/'README.md').read_bytes() == (HERE/'readme.zh-TW.md').read_bytes(), 'Full TW default README')
    print(json.dumps(dict(passed=True, metadata_only=True, members=len(members),
                         seal_sha256=sha(output), native_generation_source_files=len(manifest['source_files']),
                         compiler_resource_headers=len(manifest['compiler_resource_header_inputs']),
                         actual_old_object_replay=False, complete_image_built=False, OTA_ready=False)))


if __name__ == '__main__':
    main()
