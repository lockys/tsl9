#!/usr/bin/env python3
"""Derive the twelfth-owner image plan from actual sealed objects and sources.

Plan preparation reads original bytes as evidence only. It does not generate
an object or BIN and never executes RV32 code.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OWNER = '.text.tsl9v4160.ota_handler_9b8e'
NATIVE = '.text.tsl9_ota_page_reply_9b8e'
FUNCTION = 'tsl9_ota_page_reply_9b8e'
RAW_SOURCE = 'experiments/tsl9-v4160-startup/src/ota_handler_native.c'
MODEL = 'experiments/tsl9-v4160-ota-page-reply'
PARENT_MANIFEST = 'experiments/tsl9-v4160-register-image-integration/source-manifest.json'
PARENT_SHA = '743c087e24760779073cd27ef06b7355b9f61ced6a8b14a2e9fc410d3fa10c5e'
PARENT_OBJECT_SHA = '4e86cebc1119d30a726386cc520d73c5384920bb74bd97dbbc5dfa505c6bfbf2'
PREVIOUS_RUNNER_SHA = '73d3fb0525d5f47c772632a2e397533d86fd3b58e2a26feeecfbd06ddac1bdb1'
REPLY_RUNNER_SHA = '23b0dfe90a4cde21c8066c2fd318bfd9e19b32ebb758b83eb9f294dc3dae6ee3'
CLANG_SHA = '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6'
FIRMWARE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--tool-dir', required=True, type=Path)
    p.add_argument('--baseline-object', required=True, type=Path)
    p.add_argument('--reply-build', required=True, type=Path)
    p.add_argument('--firmware', required=True, type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    for path in (a.baseline_object, a.reply_build, a.firmware):
        need(path.resolve().is_relative_to(root), 'Explicit project-local source evidence')
    need(sha(root/PARENT_MANIFEST) == PARENT_SHA, 'Immutable prior eleven-function source ledger')
    need(sha(a.baseline_object) == PARENT_OBJECT_SHA and sha(a.firmware) == FIRMWARE_SHA,
         'Actual previous scheduled partial object and official original image')
    previous_path = root/'apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/implementation/verify_image.py'
    need(sha(previous_path) == PREVIOUS_RUNNER_SHA, 'Pinned previous integration helpers')
    previous = module(previous_path, 'twelfth_plan_old_integration')
    old_context = previous.context(root, a.firmware.resolve())
    V, ELF = old_context['V'], old_context['ELF']
    original = ELF(a.baseline_object.resolve())
    previous.merged_gate(original, old_context)
    old = read(root/PARENT_MANIFEST)
    reply_case = root/'apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22'
    reply_path = reply_case/'implementation/verify_native.py'
    need(sha(reply_path) == REPLY_RUNNER_SHA, 'Pinned standalone reply source/compiler verifier')
    reply = module(reply_path, 'twelfth_plan_reply_compiler')
    fixed = {}
    compilers = {}
    ordered = {}
    native_receipts = {}
    for mode in ('c', 'cpp'):
        folder = a.reply_build.resolve()/mode
        receipt = folder/'verification.json'
        replay = reply.replay(root, receipt)
        need(replay['passed'], 'Actual standalone compiler and fixed-placement artifact replay')
        raw, post = ELF(folder/'page_reply.o'), ELF(folder/'source-ordered.o')
        compilers[mode] = raw.data(raw.byname[NATIVE])
        ordered[mode] = post.data(post.byname[NATIVE])
        linked = ELF(folder/'ADDRESS-WITNESS-ONLY.elf')
        fixed[mode] = linked.data(linked.byname['.reply'])
        native_receipts[mode] = dict(path=receipt.relative_to(root).as_posix(), sha256=sha(receipt))
    need(compilers['c'] == compilers['cpp'] and ordered['c'] == ordered['cpp'] and fixed['c'] == fixed['cpp'],
         'Actual compiler, ordered and fixed-placement C/C++ instruction streams agree')
    original_body = original.data(original.byname[OWNER])
    need(fixed['c'] == original_body and len(original_body) == 124, 'Reply full original byte identity')
    manifest = copy.deepcopy(old)
    manifest['schema'] = 'TSL9-explicit-twelve-function-source-image-plan-v1'
    manifest['parent_eleven_manifest_sha256'] = PARENT_SHA
    manifest['parent_scheduled_partial_object_sha256'] = PARENT_OBJECT_SHA
    manifest['reply_native_receipts'] = native_receipts
    for row in manifest['selected_sections']:
        row['typed_provider_object_sha256'] = row['compiler_native_object_sha256']
        row['typed_input_section'] = row['name']
        row['original_global_alias_info'] = 18
        row['original_global_alias_bytes'] = row['bytes']
    def digest(payload):
        return hashlib.sha256(payload).hexdigest()
    row = dict(name=OWNER, originalVA=0x9b8e, bytes=124,
               global_alias='__tsl9v4160_ota_code_9b8e', producer=RAW_SOURCE,
               family='OTAReply', new_C_symbol=FUNCTION, typed_input_section=NATIVE,
               original_global_alias_info=16, original_global_alias_bytes=0,
               original_local_entry='.Lota_handler_00009b8e',
               native_object_sha256=digest(ordered['c']),
               typed_provider_object_sha256=digest(ordered['c']),
               raw_compiler_native_object_sha256=digest(compilers['c']),
               native_linked_bytes=fixed['c'].hex(), original_bytes=original_body.hex(),
               original_boundary_bytes=0, compiler_alone_emitted_final_order=False)
    manifest['selected_sections'].append(row)
    selected = {item['name'] for item in manifest['selected_sections']}
    need(len(selected) == 12 and sum(item['bytes'] for item in manifest['selected_sections']) == 650,
         'Twelve distinct readable source owners / 650 bytes')
    del manifest['retained_storage'][OWNER]
    need(len(manifest['retained_storage']) == 679, 'Actual remaining retained owner count')
    for name, proof in manifest['retained_storage'].items():
        need(digest(V.data(original, original.byname[name])) == proof['sha256'], 'Actual retained byte identity')
    outside = [V.relocation(original, item) for item in original.relocations if item['owner'] not in selected]
    need(len(outside) == 8257, 'Actual remaining outside RELA count')
    manifest['retained_RELA_count'] = len(outside)
    manifest['retained_RELA_semantic_sha256'] = V.digest(sorted(outside, key=lambda x: json.dumps(x, sort_keys=True)))
    reply_owned = [V.relocation(original, item) for item in original.relocations if item['owner'] == OWNER]
    need([(r['offset'], r['type']) for r in reply_owned] == [(34, 44), (82, 17)], 'Actual private branch and TX relocation')
    for item in reply_owned:
        if item['type'] == 44:
            item['original_branch_bytes'] = original_body[item['offset']:item['offset']+2].hex()
    manifest['old_selected_RELA'] += reply_owned
    manifest['external_incoming_RELA'] = [item for item in outside if item['symbol']['owner'] in selected]
    need(len(manifest['external_incoming_RELA']) == 21, 'Actual twelve-owner incoming entry count')
    need(len(manifest['section_relative_bindings']) == 53, 'Retain existing canonical bindings; no fake local-entry assignment')
    boundary_path = reply_case/'integration-plan/probe-boundary.py'
    boundary = module(boundary_path, 'twelfth_plan_zero_boundary_filter')
    filtered = boundary.filter_source((root/RAW_SOURCE).read_bytes())
    manifest['filtered_carrier_units'].append(dict(path=RAW_SOURCE, removed=[OWNER],
        before_sha256=sha(root/RAW_SOURCE), filtered_sha256=digest(filtered),
        removed_source_bytes=(root/RAW_SOURCE).stat().st_size-len(filtered),
        retained_zero_byte_boundary_roles=[dict(name=row['global_alias'], info=16, bytes=0, offset=0),
                                          dict(name=row['original_local_entry'], info=0, bytes=0, offset=0)]))
    for name in ('page_reply.c', 'page_reply.h', 'reply_io.h'):
        path = root/MODEL/'src'/name
        manifest['source_files'][path.relative_to(root).as_posix()] = sha(path)
    for name, pin in manifest['source_files'].items():
        need(sha(root/name) == pin, 'All actual native generation sources/headers pinned')
    manifest['reply_order_source_files'] = {path.relative_to(root).as_posix(): sha(path)
        for path in (root/'experiments/tsl9-v4160-reply-abi-order').iterdir() if path.is_file()}
    manifest['reply_boundary_filter'] = dict(path=boundary_path.relative_to(root).as_posix(), sha256=sha(boundary_path))
    manifest['reply_native_profile'] = dict(path=reply_path.relative_to(root).as_posix(), sha256=sha(reply_path))
    manifest['incoming_call'] = dict(PC=0x9df4, raw_hex='693b', encoding='RV32 C.JAL', rd=1,
                                    target=0x9b8e, return_PC=0x9df6,
                                    correction_seal_sha256=sha(reply_case/'entry-call-correction/seal.json'))
    clang = next(path.resolve() for path in (a.tool_dir/'clang.exe', a.tool_dir/'clang') if path.is_file())
    need(sha(clang) == CLANG_SHA, 'Pinned actual clang dependency discovery')
    work = HERE/'build'/('dependencies-'+uuid.uuid4().hex)
    work.mkdir(parents=True)
    calls = []
    def run(argv, label):
        result = subprocess.run([str(x) for x in argv], cwd=root, capture_output=True, timeout=60)
        (work/(label+'.stdout')).write_bytes(result.stdout)
        (work/(label+'.stderr')).write_bytes(result.stderr)
        calls.append(dict(argv=[str(x) for x in argv], exit=result.returncode,
                          stdout_sha256=digest(result.stdout), stderr_sha256=digest(result.stderr)))
        need(result.returncode == 0, 'Actual bounded dependency discovery '+label)
        return result.stdout
    resource = Path(run([clang, '--print-resource-dir'], 'resource-dir').decode().strip()).resolve()
    discovered = {}
    for mode in ('c', 'cpp'):
        deps = run([clang, *reply.flags(mode), '-M', '-MT', 'reply.o', root/MODEL/'src/page_reply.c'], 'deps-'+mode)
        dep_file = work/('reply-'+mode+'.d')
        dep_file.write_bytes(deps)
        paths = previous.dependency_rule(dep_file, 'reply.o', root/MODEL/'src/page_reply.c')
        external = []
        for path in paths:
            if path.is_relative_to(root):
                name = path.relative_to(root).as_posix()
                need(name in manifest['source_files'] and sha(path) == manifest['source_files'][name], 'Pinned native project include')
            else:
                need(path.is_relative_to(resource), 'Only compiler resource files may be nonproject includes')
                external.append(dict(path=str(path), resource_relative=path.relative_to(resource).as_posix(), sha256=sha(path)))
        discovered[mode] = external
    need(discovered['c'] == discovered['cpp'] and discovered['c'], 'Actual matching nonempty C/C++ resource-header closure')
    manifest['compiler_resource_header_inputs'] = discovered['c']
    manifest['compiler_resource_directory'] = str(resource)
    manifest['expected_differences'] = []
    manifest['differences_from_previous_full_image'] = []
    manifest['differences_from_previous_IRQ_image'] = []
    manifest['pipeline'] = 'Fresh C/C++ plus standalone reply ordering, canonical partial link, then IRQ/quarter frame ordering'
    manifest['compiler_alone_emitted_final_order'] = False
    manifest['full_twelve_function_image_build_completed'] = False
    manifest['hardware'] = manifest['OTA_ready'] = False
    output = HERE/'source-manifest.json'
    with output.open('xb') as out:
        out.write((json.dumps(manifest, indent=2)+'\n').encode())
    report = dict(schema='TSL9-twelfth-owner-actual-plan-preparation-v1', passed=True,
                  previous_manifest_sha256=PARENT_SHA, previous_partial_sha256=PARENT_OBJECT_SHA,
                  source_manifest_sha256=sha(output), readable_functions=12, readable_bytes=650,
                  retained_storage=679, outside_RELA=len(outside), incoming=len(manifest['external_incoming_RELA']),
                  explicit_native_receipt_replays=native_receipts,
                  actual_dependency_discovery=dict(commands=calls, resource_headers=discovered),
                  full_image_build_completed=False, target_execution=False, ISA_emulation=False,
                  hardware=False, OTA_ready=False)
    with (HERE/'verification.json').open('xb') as out:
        out.write((json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True, source_manifest_sha256=sha(output), retained_storage=679,
                         outside_RELA=len(outside), compiler_resource_headers=len(discovered['c']),
                         complete_image_built=False)))


if __name__ == '__main__':
    main()
