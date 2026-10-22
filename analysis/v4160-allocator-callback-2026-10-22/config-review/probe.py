#!/usr/bin/env python3
"""Compile data-only RV32 layout probes against explicit, pinned vendor headers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CC = '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
HEADERS = ['fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e',
           '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c']
RESOURCE = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
EXPECTED = [0, 4, 8, 12, 14, 52, 56, 60, 64, 4]


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parser(root):
    name = 'v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    p = next(p for p in (root / 'analysis' / name, root / 'apk-analysis' / ('tsl9-' + name)) if p.is_file())
    need(sha(p) == PARSER, 'Pinned ELF parser')
    return p, runpy.run_path(str(p))['ELF']


def inspect(root, folder, record):
    path, E = parser(root)
    need(record['parser_sha256'] == sha(path) and sha(HERE / 'config_layout.c') == record['source_sha256'], 'Actual source and parser')
    cc = Path(record['compiler'])
    need(sha(cc) == record['compiler_sha256'] == CC, 'Actual pinned compiler')
    need(sha(Path(record['resource_header'])) == record['resource_sha256'] == RESOURCE, 'Actual compiler stdint input')
    need([r['sha256'] for r in record['headers']] == HEADERS, 'Exact V1.40 and historical SDK headers')
    actual = []
    for row in record['headers']:
        header = Path(row['path'])
        need(sha(header) == row['sha256'], 'Actual explicit SDK header')
        obj = folder / row['object']
        need(sha(obj) == row['object_sha256'], 'Actual layout object')
        elf = E(obj)
        owners = [s for s in elf.sections if s['flags'] & 2 and s['size']]
        need(len(owners) == 1 and owners[0]['name'] == '.rodata.tsl9_config_layout'
             and not owners[0]['flags'] & 4 and owners[0]['size'] == 40, 'Data-only40-byte layout object')
        values = list(struct.unpack('<10I', elf.data(owners[0])))
        need(values == EXPECTED and not elf.relocations, 'Actual RV32 ILP32 vendor structure offsets')
        need(not any(s['name'] and s['index'] == 0 for s in elf.symbols), 'No fabricated external provider')
        need(sha(folder / row['log']) == row['log_sha256'], 'Actual compile log')
        actual.append(dict(header_sha256=row['sha256'], fields=values, target_code_executed=False))
    return dict(passed=True, metadata_only=False, actual_layout_objects_read=True, headers=actual,
                compiler_reinvoked=False, target_code_executed=False, hardware=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--headers', nargs=2, type=Path)
    p.add_argument('--tool-dir', type=Path)
    p.add_argument('--build-root', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    if a.replay:
        need(a.headers is None and a.tool_dir is None and a.build_root is None, 'Replay has no fresh flags')
        print(json.dumps(inspect(root, a.replay.resolve().parent, json.loads(a.replay.read_bytes()))))
        return
    need(a.headers is not None and a.tool_dir is not None, 'Explicit headers and compiler directory required')
    cc = next(p.resolve() for p in (a.tool_dir / 'clang.exe', a.tool_dir / 'clang') if p.is_file())
    need(sha(cc) == CC, 'Pinned Windows LLVM compiler')
    build = a.build_root.resolve() if a.build_root else HERE / 'build' / ('layout-' + uuid.uuid4().hex)
    need(build.is_relative_to(HERE / 'build') and not build.exists(), 'New owned build directory')
    build.mkdir(parents=True)
    r = subprocess.run([str(cc), '-print-resource-dir'], capture_output=True, timeout=30)
    need(r.returncode == 0, 'Actual compiler resource path')
    resource = Path(r.stdout.decode().strip()) / 'include/stdint.h'
    need(sha(resource) == RESOURCE and [sha(p.resolve()) for p in a.headers] == HEADERS, 'Explicit pinned resource and SDK headers before compilation')
    reader, _ = parser(root)
    record = dict(source_sha256=sha(HERE / 'config_layout.c'), compiler=str(cc), compiler_sha256=sha(cc),
                  parser_sha256=sha(reader), resource_header=str(resource), resource_sha256=sha(resource), headers=[])
    for i, supplied in enumerate(a.headers):
        header = supplied.resolve(strict=True)
        before = sha(header)
        obj, log = build / ('header-' + str(i) + '.o'), build / ('header-' + str(i) + '.log')
        command = [str(cc), '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                   '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-std=c11',
                   '-DTSL9_CONFIG_HEADER="' + header.as_posix() + '"', '-c', str(HERE / 'config_layout.c'), '-o', str(obj)]
        result = subprocess.run(command, cwd=build, env=dict(os.environ, TEMP=str(build), TMP=str(build)), capture_output=True, timeout=60)
        log.write_bytes(result.stdout + result.stderr)
        need(result.returncode == 0 and sha(header) == before, 'Actual header layout compile: ' + str(log))
        record['headers'].append(dict(path=str(header), sha256=before, object=obj.name, object_sha256=sha(obj),
                                      log=log.name, log_sha256=sha(log), command=command, exit=0))
    receipt = build / 'verification.json'
    record['result'] = inspect(root, build, record)
    receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, receipt=str(receipt), sha256=sha(receipt), actual_compiler_invoked=True,
                          data_only_objects=2, layout=EXPECTED, target_code_executed=False)))


if __name__ == '__main__':
    main()
