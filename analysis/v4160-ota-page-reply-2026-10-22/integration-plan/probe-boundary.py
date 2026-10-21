#!/usr/bin/env python3
"""Compile a zero-byte original entry boundary plus the new native reply.

This is a partial two-object link probe, not a complete image or hardware test.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OWNER = '.text.tsl9v4160.ota_handler_9b8e'
NATIVE = '.text.tsl9_ota_page_reply_9b8e'
PUBLIC = '__tsl9v4160_ota_code_9b8e'
LOCAL = '.Lota_handler_00009b8e'
NAME = 'tsl9_ota_page_reply_9b8e'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def filter_source(raw):
    output, active, seen = [], False, 0
    anchor = ('.section ' + OWNER + ',"ax",@progbits\n.balign 2\n.globl ' + PUBLIC +
              '\n.type ' + PUBLIC + ',@notype\n' + PUBLIC + ':\n' + LOCAL +
              ':\n.size ' + PUBLIC + ',0\n')
    for line in raw.decode('utf8').splitlines(keepends=True):
        stripped = line.strip()
        text = json.loads(stripped) if stripped.startswith('"') else None
        if text and text.startswith('.section '):
            need(not active, 'Removed source owner must end at its exact size directive')
            if text.split(',', 1)[0] == '.section ' + OWNER:
                active, seen = True, seen + 1
                output.extend('    ' + json.dumps(part + '\n') + '\n' for part in anchor.splitlines())
        if active:
            need(text is not None, 'Only original quoted assembly is removed')
            if text == '.size ' + PUBLIC + ',0\n':
                active = False
            continue
        output.append(line)
    need(not active and seen == 1, 'Exactly one original raw function removed')
    return ''.join(output).encode('utf8')


def role(elf, symbol):
    index = symbol['index']
    owner = 'UND' if index == 0 else 'ABS' if index == 0xfff1 else elf.sections[index]['name']
    return dict(name=symbol['name'], owner=owner, offset=symbol['value'],
                bytes=symbol['size'], info=symbol['info'], other=symbol['other'])


def relocation(elf, row):
    return dict(owner=row['owner'], offset=row['offset'], type=row['type'], addend=row['addend'],
                symbol=role(elf, row['symbol']))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--tool-dir', type=Path, required=True)
    p.add_argument('--native-folder', type=Path, required=True)
    p.add_argument('--mode', choices=['c', 'cpp'], required=True)
    a = p.parse_args()
    root = a.project_root.resolve()
    native_folder = a.native_folder.resolve()
    need(native_folder.is_relative_to(root), 'Explicit project-local fresh native component')
    parser = root / 'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    if not parser.is_file():
        parser = root / 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    need(sha(parser.read_bytes()) == PARSER_SHA, 'Pinned bounded ELF parser')
    ELF = runpy.run_path(str(parser))['ELF']
    tools = {}
    for name, pin in TOOLS.items():
        path = next(path for path in (a.tool_dir / (name + '.exe'), a.tool_dir / name) if path.is_file())
        need(sha(path.read_bytes()) == pin, 'Exact compiler/linker binary')
        tools[name] = path.resolve()
    native = native_folder / 'source-ordered.o'
    source_receipt = native_folder / 'verification.json'
    native_receipt = json.loads(source_receipt.read_bytes())
    need(native_receipt['passed'], 'Existing passed native component receipt')
    native_checker = HERE.parent / 'implementation/verify_native.py'
    verified = runpy.run_path(str(native_checker))['replay'](root, source_receipt)
    need(verified['passed'], 'Fresh full native compiler/provenance replay')
    before = ELF(native)
    native_body = before.data(before.byname[NATIVE])
    # The byte digest is measured below; semantic admission comes from the
    # separately pinned source-owned ordering pass and actual component replay.
    order = runpy.run_path(str(root / 'experiments/tsl9-v4160-reply-abi-order/order.py'))
    order['replay'](root, native_folder / 'ABI-order.json')
    folder = HERE / 'build' / ('boundary-' + a.mode + '-' + uuid.uuid4().hex)
    folder.mkdir(parents=True)
    original = root / 'experiments/tsl9-v4160-startup/src/ota_handler_native.c'
    manifest = json.loads((root / 'experiments/tsl9-v4160-register-image-integration/source-manifest.json').read_bytes())
    need(sha(original.read_bytes()) == manifest['source_files'][original.relative_to(root).as_posix()],
         'Exact previously sealed raw carrier source')
    filtered = folder / 'ota_handler_native.c'
    filtered.write_bytes(filter_source(original.read_bytes()))
    commands = []

    def run(argv, label):
        process = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=60)
        log = folder / (label + '.log')
        log.write_bytes(process.stdout + process.stderr)
        commands.append(dict(argv=[str(x) for x in argv], exit=process.returncode,
                             log=log.name, log_sha256=sha(log.read_bytes())))
        need(process.returncode == 0, 'Actual boundary command: ' + label)

    carrier = folder / 'carrier.o'
    run([tools['clang'], '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32',
         '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-Wall', '-Wextra', '-Werror',
         '-x', 'c' if a.mode == 'c' else 'c++', '-std=c11' if a.mode == 'c' else '-std=c++17',
         '-I', original.parent, '-c', filtered, '-o', carrier], 'compile-boundary-carrier')
    raw = ELF(carrier)
    section = raw.byname[OWNER]
    need(section['size'] == 0 and section['flags'] == 6, 'Actual zero-byte original AX boundary')
    expected_roles = [dict(name=PUBLIC, owner=OWNER, offset=0, bytes=0, info=16, other=0),
                      dict(name=LOCAL, owner=OWNER, offset=0, bytes=0, info=0, other=0)]
    selected = [role(raw, s) for s in raw.symbols if s['index'] == section['index'] and s['name']]
    need(Counter(json.dumps(x, sort_keys=True) for x in selected) ==
         Counter(json.dumps(x, sort_keys=True) for x in expected_roles), 'Two exact original boundary roles')
    script = folder / 'reply-section.ld'
    script.write_bytes(('SECTIONS {\n ' + OWNER + ' 0 : { KEEP(*(' + OWNER + ')) KEEP(*(' + NATIVE + ')) }\n}\n').encode())
    linked_path = folder / 'partial.o'
    run([tools['ld.lld'], '-r', '--no-relax', '-T', script, carrier, native, '-o', linked_path], 'partial-boundary-link')
    linked = ELF(linked_path)
    body = linked.data(linked.byname[OWNER])
    need(body == native_body and len(body) == 124, 'No anchor byte, fill, fallback or source-copy addition')
    wanted = expected_roles + [dict(name=NAME, owner=OWNER, offset=0, bytes=124, info=18, other=0)]
    actual = [role(linked, s) for s in linked.symbols if s['name'] in (PUBLIC, LOCAL, NAME)]
    need(Counter(json.dumps(x, sort_keys=True) for x in actual) ==
         Counter(json.dumps(x, sort_keys=True) for x in wanted), 'Original NOTYPE/local plus real C FUNC roles')
    incoming = [relocation(linked, r) for r in linked.relocations
                if r['symbol']['index'] == linked.byname[OWNER]['index']]
    need(len(incoming) == 1 and incoming[0]['owner'] == '.text.tsl9v4160.ota_handler_9c4a'
         and incoming[0]['offset'] == 426 and incoming[0]['type'] == 45
         and incoming[0]['addend'] == 0 and incoming[0]['symbol'] == expected_roles[1],
         'Original actual compressed incoming reference retains exact local boundary role')
    outgoing = [relocation(linked, r) for r in linked.relocations if r['owner'] == OWNER]
    need(len(outgoing) == 1 and outgoing[0]['offset'] == 82 and outgoing[0]['type'] == 17
         and outgoing[0]['symbol']['name'] == '__tsl9v4160_call_8a56', 'Only actual TX relocation remains')
    need(not any(s['name'] == '.Lota_handler_00009bfa' for s in linked.symbols), 'Private null label discharged')
    for other in raw.sections:
        if other['flags'] & 2 and other['size']:
            new_section = linked.byname[other['name']]
            need(all(other[k] == new_section[k] for k in
                     ('type', 'flags', 'size', 'alignment', 'entry_size')),
                 'Every retained carrier allocation attribute')
            need(raw.data(other) == linked.data(new_section), 'Every other actual carrier section byte retained')
    outside_before = [relocation(raw, r) for r in raw.relocations if r['owner'] != OWNER]
    outside_after = [relocation(linked, r) for r in linked.relocations if r['owner'] != OWNER]
    counter = lambda rows: Counter(json.dumps(row, sort_keys=True) for row in rows)
    need(counter(outside_before) == counter(outside_after),
         'Every outside actual RELA owner/site/type/addend/target role/multiplicity preserved')
    report = dict(schema='TSL9-page-reply-section-boundary-actual-probe-v1', passed=True, mode=a.mode,
                  commands=commands, original_source_sha256=sha(original.read_bytes()),
                  filtered_source_sha256=sha(filtered.read_bytes()), native_receipt_sha256=sha(source_receipt.read_bytes()),
                  native_provenance_replayed=True, native_checker_sha256=sha(native_checker.read_bytes()),
                  ordered_object_sha256=sha(native.read_bytes()), carrier_sha256=sha(carrier.read_bytes()),
                  partial_object_sha256=sha(linked_path.read_bytes()), reply_body_sha256=sha(body),
                  exact_roles=actual, exact_incoming=incoming, outgoing=outgoing,
                  retained_outside_RELA=len(outside_after),
                  retained_outside_RELA_semantic_sha256=sha(json.dumps(sorted(outside_after, key=lambda row:
                      json.dumps(row, sort_keys=True)), sort_keys=True).encode()),
                  zero_anchor_bytes=True, original_global_NOTYPE_size_zero_preserved=True,
                  actual_local_incoming_role_preserved=True, complete_image_integration=False,
                  original_BIN_read_for_generation=False, target_execution=False, ISA_emulation=False,
                  hardware=False, OTA_ready=False)
    (folder / 'verification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, mode=a.mode, zero_anchor_bytes=True,
                         original_global_NOTYPE_size_zero_preserved=True,
                         actual_local_incoming_role_preserved=True, receipt=str(folder / 'verification.json'),
                         complete_image_integration=False, OTA_ready=False)))


if __name__ == '__main__':
    main()
