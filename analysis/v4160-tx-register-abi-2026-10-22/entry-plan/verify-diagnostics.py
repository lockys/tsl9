#!/usr/bin/env python3
"""Compile synthetic compiler diagnostics, then inspect RV32 objects as data only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
PROFILE = '253b5fb067d5f5c90e517e2df4593381ef807dfbdd6143de2526c97a84744525'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
DECODER = 'da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
RESOURCE = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
SOURCES = {
    'minimal_guard.c': '6332a2d3083d0844eb0b54d30369b95b2b6ed7cf6705bfd2cf2c17119a90d2df',
    'global_owned_s0.c': '426c0949b426824e400a9546c426dc4eb9d4583a07f3bb350ea1e4e435d18e7a',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(root, slug):
    return next(p for p in (root / 'analysis' / slug,
                            root / 'apk-analysis' / ('tsl9-' + slug)) if p.is_dir())


def operands(body, decode):
    result, pc = [], 0
    while pc < len(body):
        halfword = int.from_bytes(body[pc:pc + 2], 'little')
        if halfword & 3 == 0 and halfword >> 13 == 6:
            # This synthetic diagnostic adds C.SW, absent from the immutable
            # original TX decoder. Decode instruction fields, never CPU state.
            offset = (((halfword >> 10) & 7) << 3) | (((halfword >> 6) & 1) << 2) | (((halfword >> 5) & 1) << 6)
            row = {'PC': pc, 'bytes': 2, 'raw_hex': body[pc:pc + 2].hex(),
                   'op': 'sw', 'rd': None, 'rs1': 8 + ((halfword >> 7) & 7),
                   'rs2': 8 + ((halfword >> 2) & 7), 'immediate': offset,
                   'target': None, 'memory_width': 32}
        else:
            row = decode(body[pc:], pc)
        need(row['bytes'] in (2, 4), 'actual instruction width')
        result.append(row)
        pc += row['bytes']
    need(pc == len(body), 'whole instructions only')
    return result


def guard_contract(body, decode):
    rows = operands(body, decode)
    limits = [r for r in rows if r['op'] == 'addi'
              and (r['rd'], r['rs1'], r['immediate']) == (15, 0, 1039)]
    guards = [r for r in rows if r['op'] == 'bltu'
              and (r['rs1'], r['rs2']) == (15, 13)]
    frames = [r for r in rows if r['op'] == 'addi'
              and (r['rd'], r['rs1'], r['immediate']) == (2, 2, -16)]
    need(len(limits) == len(guards) == len(frames) == 1, 'unique guard and frame')
    guard, frame = guards[0], frames[0]
    need(limits[0]['PC'] < guard['PC'] < frame['PC'], 'actual guard before frame')
    before = [r for r in rows if r['PC'] < frame['PC']]
    need(all(r['memory_width'] is None for r in before), 'no pre-guard memory')
    target = next(r for r in rows if r['PC'] == guard['target'])
    need(target['op'] == 'jalr' and (target['rd'], target['rs1'], target['immediate'])
         == (0, 1, 0), 'rejected branch reaches actual RET directly')
    return {'bytes': len(body), 'guard_offset': guard['PC'],
            'frame_offset': frame['PC'], 'rejected_RET_offset': target['PC'],
            'guard_before_frame': True}


def owned_contract(body, decode):
    rows = operands(body, decode)
    def select(op, **fields):
        return [r for r in rows if r['op'] == op and all(r[k] == v for k, v in fields.items())]
    frame = select('addi', rd=2, rs1=2, immediate=-16)
    save = select('sw', rs1=2, rs2=8, immediate=12)
    restore = select('lw', rd=8, rs1=2, immediate=12)
    need(len(frame) == len(save) == len(restore) == 1, 'actual S0 autosave/restore')
    writes = [r for r in rows if r['rd'] == 8 and r['op'] != 'lw']
    need(len(writes) == 1 and frame[0]['PC'] < save[0]['PC'] < writes[0]['PC']
         < restore[0]['PC'], 'compiler restores globally declared S0 after source write')
    return {'bytes': len(body), 'frame_offset': frame[0]['PC'],
            'save_offset': save[0]['PC'], 'write_offset': writes[0]['PC'],
            'restore_offset': restore[0]['PC'], 'global_register_owns_frame': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--build-root', type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    here = case(root, 'v4160-tx-register-abi-2026-10-22') / 'entry-plan'
    old = case(root, 'v4160-ota-tx-2026-10-22')
    profile = old / 'implementation/verify_native.py'
    raw_path = old / 'source-review/raw.py'
    elf_path = case(root, 'v4160-irq-native-2026-10-21') / 'compiler-review/elf32.py'
    pins = {profile: PROFILE, raw_path: DECODER, elf_path: PARSER,
            **{here / name: pin for name, pin in SOURCES.items()},
            Path(__file__).resolve(): sha(Path(__file__))}
    need(all(sha(p) == pin for p, pin in pins.items()), 'pinned diagnostic inputs')
    helper = runpy.run_path(str(profile))
    ELF = runpy.run_path(str(elf_path))['ELF']
    decode = runpy.run_path(str(raw_path))['decode']
    tools = {name: next(p for p in (args.tool_dir / (name + '.exe'),
                                    args.tool_dir / name) if p.is_file())
             for name in ('clang', 'llvm-objdump')}
    pins.update({p: helper['TOOLS'][name] for name, p in tools.items()})
    need(all(sha(p) == pin for p, pin in pins.items()), 'pinned actual tools')
    build = (args.build_root or here / 'build' / ('verified-' + uuid.uuid4().hex)).resolve()
    need(build.is_relative_to(root) and not build.exists(), 'create-only local output')
    build.mkdir(parents=True)
    temp = build / 'compiler-temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    commands, results = [], []
    def run(label, argv):
        argv = [str(x) for x in argv]
        result = subprocess.run(argv, cwd=build, env=env, capture_output=True, timeout=120)
        log = build / (label + '.log')
        log.write_bytes(result.stdout + result.stderr)
        commands.append({'label': label, 'argv': argv, 'exit': result.returncode,
                         'log': log.name, 'sha256': sha(log)})
        need(result.returncode == 0, 'actual compiler diagnostic ' + label)
        return result
    resource = Path(run('resource-dir', [tools['clang'], '-print-resource-dir']).stdout.decode().strip()) / 'include/stdint.h'
    need(sha(resource) == RESOURCE, 'actual compiler resource header')
    pins[resource] = RESOURCE
    for mode in ('c', 'cpp'):
        for source in SOURCES:
            stem = mode + '-' + Path(source).stem
            obj, dep = build / (stem + '.o'), build / (stem + '.d')
            run(stem, [tools['clang'], *helper['flags'](mode), '-c', '-MD', '-MF', dep,
                       '-MT', stem + '.o', here / source, '-o', obj])
            run(stem + '-disassembly', [tools['llvm-objdump'], '-d', obj])
            rule = dep.read_text().replace('\\\r\n', ' ').replace('\\\n', ' ')
            need(rule.startswith(stem + '.o:'), 'actual dependency target')
            # Clang escapes spaces and drive separators in Make paths.
            words = re.findall(r'(?:\\[ #:]|[^\s])+', rule.split(':', 1)[1])
            actual = {str(Path(re.sub(r'\\([ #:])', r'\1', w)).resolve()).replace('\\', '/').lower()
                      for w in words}
            expected = {str(p.resolve()).replace('\\', '/').lower() for p in (here / source, resource)}
            need(actual == expected, 'exact -MD source/resource closure')
            elf = ELF(obj)
            need(elf.kind == 1 and elf.flags == 1 and not elf.relocations,
                 'actual RV32 RVC object with no unresolved references')
            observations = []
            functions = [s for s in elf.symbols if s['info'] & 15 == 2]
            need(len(functions) == (2 if source == 'minimal_guard.c' else 1), 'exact diagnostic functions')
            for symbol in functions:
                body = elf.function_bytes(symbol)
                check = guard_contract if source == 'minimal_guard.c' else owned_contract
                fact = check(body, decode)
                if source == 'minimal_guard.c':
                    altered = bytearray(body)
                    altered[fact['guard_offset'] + 1] ^= 0x20  # unsigned BLTU -> signed BLT
                    try:
                        check(bytes(altered), decode)
                    except ValueError:
                        fact['actual_branch_operand_control_rejected'] = True
                    else:
                        raise ValueError('altered actual guard unexpectedly accepted')
                observations.append({'function': symbol['name'], **fact})
            results.append({'language': mode, 'source': source, 'object': obj.name,
                            'object_sha256': sha(obj), 'observations': observations})
    need(all(sha(p) == pin for p, pin in pins.items()), 'stable inputs and actual tools')
    receipt = {'schema': 'TSL9-compiler-entry-diagnostics-v2', 'diagnostics_passed': True,
               'results': results, 'commands': commands,
               'inputs': {str(p): pin for p, pin in pins.items()},
               'artifacts': {p.relative_to(build).as_posix(): sha(p) for p in build.rglob('*') if p.is_file()},
               'original_TX_ABI_proved': False, 'RV32_execution': False,
               'ISA_emulation': False, 'network': False, 'hardware': False}
    target = build / 'verification.json'
    target.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
    print(json.dumps({'passed': True, 'receipt': str(target), 'sha256': sha(target), 'results': results}))


if __name__ == '__main__':
    main()
