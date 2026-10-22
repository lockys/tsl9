#!/usr/bin/env python3
"""Link real C providers into an offline component ELF, never a firmware BIN."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ENTRY = 'tsl9_nv_write_callback_197be'
TOOLS = {'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_bytes())


def locate(root, name):
    p = root / name
    if name.startswith('analysis/') and not p.is_file():
        p = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    return p


def parser(root):
    return locate(root, 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def call_target(data, offset, pc, kind):
    a = struct.unpack_from('<I', data, offset)[0]
    if kind == 17:
        need(a & 127 == 0x6f and (a >> 7) & 31 == 1, 'Actual JAL with linkRA')
        imm = ((a >> 31) << 20) | (((a >> 12) & 255) << 12) | (((a >> 20) & 1) << 11) | (((a >> 21) & 1023) << 1)
        return (pc + sx(imm, 21)) & 0xffffffff
    need(kind == 19, 'Only actual CALL_PLT or JAL relocations')
    b = struct.unpack_from('<I', data, offset + 4)[0]
    need(a & 127 == 0x17 and (a >> 7) & 31 == 1, 'CALL_PLT AUIPC RA')
    need(b & 0x707f == 0x67 and (b >> 7) & 31 == 1 and (b >> 15) & 31 == 1, 'CALL_PLT JALR RA,RA')
    return (pc + sx(a & 0xfffff000, 32) + sx(b >> 20, 12)) & 0xffffffff


def audit(root, folder, record):
    native = Path(record['native_folder'])
    for name, pin in record['source_pins'].items():
        need(sha(Path(name)) == pin, 'Frozen component input/source/tool ' + name)
    tools = {n: Path(v) for n, v in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == h for n, h in TOOLS.items()), 'Exact local linker/reader')
    expected = recipes(native, folder, tools)
    need([(c['label'], c['argv']) for c in record['commands']] == [(n, [str(x) for x in a]) for n, a in expected], 'Exact no-relax/no-GC component recipes')
    for c in record['commands']:
        need(c['exit'] == 0 and sha(folder / c['log']) == c['log_sha256'], 'Actual successful component log')
    E = runpy.run_path(str(parser(root)))['ELF']
    source, linked = E(native / 'native.o'), E(folder / 'linked.elf')
    need(source.kind == 1 and linked.kind == 2 and source.flags == linked.flags == 1, 'Actual RV32/RVC REL/EXEC')
    for e in (source, linked):
        need(not any(s['index'] == 0 and s['name'] for s in e.symbols), 'No undefined provider')
        need(not any(s['index'] == 0xfff1 and s['info'] >> 4 for s in e.symbols), 'No fabricated ABS provider')
    funcs = {f['name']: f for f in source.symbols if f['info'] == 18 and f['size']}
    out = {f['name']: f for f in linked.symbols if f['info'] == 18 and f['size']}
    need(len(funcs) == len(out) == 8 and set(funcs) == set(out) and sum(f['size'] for f in funcs.values()) == 394, 'All eight genuine functions retained')
    need(len(source.relocations) == 10 and not linked.relocations, 'Ten real input relocations fully resolved')
    need(sorted(r['type'] for r in source.relocations) == [17] * 5 + [19] * 5, 'Five JAL plus five CALL_PLT, no relaxation relocations')
    alloc = [s for s in linked.sections if s['flags'] & 2 and s['size']]
    need(len(alloc) == 1 and alloc[0]['name'] == '.text' and alloc[0]['address'] == 0
         and alloc[0]['type'] == 1 and alloc[0]['flags'] == 6 and alloc[0]['size'] == 394, 'One exact code-only component allocation')
    cursor = 0
    for f in sorted(out.values(), key=lambda x: x['value']):
        need(f['index'] == alloc[0]['index'] and f['value'] == cursor, 'No holes, duplicate bodies or unused-tail borrowing')
        cursor += f['size']
    need(cursor == 394, 'Entire component code classified by real functions')
    calls = []
    for name, f in funcs.items():
        before, after = source.function_bytes(f), linked.function_bytes(out[name])
        need(f['size'] == out[name]['size'], 'Exact input/output function extent')
        mask = set()
        for r in source.relocations:
            if r['owner'] != source.sections[f['index']]['name']:
                continue
            symbol = r['symbol']; target = out.get(symbol['name'])
            need(symbol['info'] == 18 and symbol['index'] not in (0, 0xfff1) and target is not None and r['addend'] == 0, 'Every call uses a real defined C function')
            width = 4 if r['type'] == 17 else 8
            need(r['offset'] + width <= len(before), 'Complete owned relocation span')
            pc = out[name]['value'] + r['offset']
            need(call_target(after, r['offset'], pc, r['type']) == target['value'], 'Actual linked target equals genuine provider')
            mask.update(range(r['offset'], r['offset'] + width))
            calls.append(dict(owner=name, offset=r['offset'], type=r['type'], PC=pc, target=symbol['name'], target_value=target['value'], provider_bytes=target['size']))
        need(all(a == b for i, (a, b) in enumerate(zip(before, after)) if i not in mask), 'All non-relocation code bytes preserved')
    raw = linked.raw
    entry, phoff = struct.unpack_from('<II', raw, 24)
    entsize, count = struct.unpack_from('<HH', raw, 42)
    need(entry == out[ENTRY]['value'] and entsize == 32 and count == 2, 'Explicit component entry plus LOAD and RISC-V attributes PHDRs')
    ph = dict(zip(('type', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'flags', 'align'), struct.unpack_from('<8I', raw, phoff)))
    need(ph['type'] == 1 and ph['offset'] == alloc[0]['offset'] and ph['vaddr'] == ph['paddr'] == 0
         and ph['filesz'] == ph['memsz'] == 394 and ph['flags'] == 5, 'Exact RX LOAD, no file/header/hole coverage')
    attr = linked.byname['.riscv.attributes']
    meta = dict(zip(('type', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'flags', 'align'), struct.unpack_from('<8I', raw, phoff + entsize)))
    need(attr['flags'] == 0 and meta['type'] == 0x70000003 and meta['offset'] == attr['offset']
         and meta['filesz'] == meta['memsz'] == attr['size'] and meta['flags'] == 4 and meta['align'] == 1
         and meta['vaddr'] == meta['paddr'] == 0, 'Exact non-LOAD RISC-V attributes metadata; not executable allocation')
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], global_functions=8, allocated_bytes=394,
                UND=0, RELA=0, ABS_providers=0, input_JAL=5, input_CALL_PLT=5, calls=calls,
                entry=entry, functions=[dict(name=n, value=f['value'], bytes=f['size']) for n, f in sorted(out.items())],
                LOAD=ph, non_LOAD_RISCV_attributes=meta, text_sha256=hashlib.sha256(linked.data(alloc[0])).hexdigest(), linked_ELF_sha256=sha(folder / 'linked.elf'),
                all_unused_real_functions_retained=True, component_VMA_is_physical=False,
                full_original_ABI_proved=False, installed_ROM_proved=False, hardware_OTA_proved=False,
                target_execution=False, BIN_generated=False, rebuilt_flashable_BIN=False)


def recipes(native, folder, tools):
    return [('actual-component-link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', native / 'native.o', '-o', folder / 'linked.elf']),
            ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'linked.elf'])]


def replay(root, receipt):
    record = read(receipt)
    folder = receipt.parent
    need(record['artifacts'] == {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in folder.iterdir() if p.is_file() and p != receipt}, 'Whole actual component inventory')
    result = audit(root, folder, record)
    need(result == record['result'], 'Read-only actual component replay equality')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--native-folder', type=Path)
    p.add_argument('--tool-dir', type=Path)
    p.add_argument('--build-root', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args(); root = a.project_root.resolve()
    if a.replay:
        need(a.native_folder is None and a.tool_dir is None and a.build_root is None, 'Read-only mode')
        print(json.dumps(replay(root, a.replay.resolve()))); return
    need(a.native_folder is not None and a.tool_dir is not None and a.build_root is not None, 'Explicit actual input/tool/output')
    native, folder = a.native_folder.resolve(), a.build_root.resolve()
    need(folder.is_relative_to(HERE.parent / 'build') and not folder.exists(), 'New owned component output only')
    tools = {n: next(x.resolve() for x in (a.tool_dir / (n + '.exe'), a.tool_dir / n) if x.is_file()) for n in TOOLS}
    need(all(sha(tools[n]) == h for n, h in TOOLS.items()), 'Pinned LLVM link tools')
    old = read(native / 'verification.json')
    sources = dict(old['source_pins'])
    sources.update({str(x): sha(x) for x in [HERE / 'probe.py', HERE / 'component.ld', native / 'native.o', native / 'verification.json', parser(root), *tools.values()]})
    folder.mkdir(parents=True)
    commands = []
    for label, args in recipes(native, folder, tools):
        r = subprocess.run([str(x) for x in args], cwd=folder, capture_output=True, timeout=120)
        log = folder / (label + '.log'); log.write_bytes(r.stdout + r.stderr)
        commands.append(dict(label=label, argv=[str(x) for x in args], exit=r.returncode, log=log.name, log_sha256=sha(log)))
        need(r.returncode == 0, 'Actual component tool failed: ' + str(log))
    record = dict(schema='TSL9-offline-NV-write-component-v1', mode=old['mode'], native_folder=str(native),
                  tools={n: str(v) for n, v in tools.items()}, source_pins=sources, commands=commands)
    record['result'] = audit(root, folder, record)
    record['artifacts'] = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in folder.iterdir() if p.is_file()}
    receipt = folder / 'verification.json'; receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(replay(root, receipt)))


if __name__ == '__main__':
    main()
