#!/usr/bin/env python3
"""Local, non-executable selected-link exploration; incomplete by design."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'manifest': ('src/source-build-manifest.json', '466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739'),
    'owner': ('src/native/receive/feature_state_records.c', '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3'),
    'callback': ('src/native/receive/feature_callback.c', '6de8a0bd3b39b9f9d5fd420fd924ed742b30658c015b1d2644260bca14a695f5'),
    'leaf': ('experiments/v4160-new-leaf-turn/leaf.c', 'e358a04a1c0d57589107315751ac0daf33cad9c53e104da80a7598da983396ff'),
    'splitter': ('experiments/v4160-105c4-source-split-replay/verify.py', 'f00f3d5fd4719b802315b9e3002caca9f76dc6ffdc4981ec8a78c219311f81f6'),
    'parser': ('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py', '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'),
    'bin': ('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'),
}
TOOLS = {'clang.exe': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld.exe': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'stdint.h': '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'}
NAME = 'tsl9_feature_state_records_provider_105c4'
SECTIONS = [
    ('target', 0x105c4, 12, '.text.' + NAME),
    ('trampoline_b', 0x107c6, 18, '.text.tsl9_feature_state_records_provider_107c6'),
    ('trampoline_a', 0x1083c, 12, '.text.tsl9_feature_external_1083c'),
    ('caller_a', 0x10944, 22, '.text.tsl9_feature_external_10944'),
    ('tail', 0x10bbe, 4, '.text.tsl9_feature_state_records_block_10bbe'),
    ('caller_b', 0x10bde, 26, '.text.tsl9_feature_state_records_block_10bde'),
]
EXPECTED_RELOCATIONS = [
    ('.text.tsl9_feature_external_10944', 8, 23, NAME, 0),
    ('.text.tsl9_feature_external_10944', 12, 24, '.Lfeature_state_records_literal_1094c', 0),
    ('.text.tsl9_feature_external_10944', 18, 17, 'tsl9_feature_external_1083c', 0),
    ('.text.tsl9_feature_state_records_block_10bbe', 0, 17, 'tsl9_feature_state_records_provider_107c6', 0),
    ('.text.tsl9_feature_state_records_block_10bde', 6, 23, NAME, 0),
    ('.text.tsl9_feature_state_records_block_10bde', 10, 24, '.Lfeature_state_records_literal_10be4', 0),
    ('.text.tsl9_feature_state_records_block_10bde', 24, 45, 'tsl9_feature_state_records_block_10bbe', 0),
]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path, digest):
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == digest, 'pin: ' + path.name)
    return data


def run_tool(path, args, cwd):
    pinned(path, TOOLS[path.name])
    env = {k: os.environ[k] for k in ('SYSTEMROOT', 'WINDIR', 'PATH') if k in os.environ}
    env.update(TEMP=str(cwd), TMP=str(cwd), TMPDIR=str(cwd))
    p = subprocess.run([str(path), *map(str, args)], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    pinned(path, TOOLS[path.name])
    return p


def linker_script(candidate):
    lines = ['PHDRS { evidence PT_NULL; }', 'SECTIONS {']
    for label, address, _, name in SECTIONS:
        if label == 'target' and candidate:
            name = '.leaf'
        lines.append(' .out_%s 0x%x : SUBALIGN(1) { KEEP(*(%s)) } :NONE' % (label, address, name))
    lines.append(' /DISCARD/ : { *(.text*) *(.rodata*) *(.data*) *(.bss*) *(.sdata*) *(.sbss*) *(.eh_frame*) *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) }')
    return '\n'.join(lines + ['}']) + '\n'


def selected(e, image):
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', e.raw)
    need(e.kind == 2 and e.flags == 1 and h[9] == 32 and h[5]+h[9]*h[10] <= len(e.raw), 'ELF header')
    need(not any(struct.unpack_from('<I', e.raw, h[5]+32*i)[0] == 1 for i in range(h[10])), 'PT_LOAD')
    need(not any(s['type'] == 11 for s in e.sections), 'dynamic symbol table')
    tables = [s for s in e.sections if s['type'] == 2]
    need(len(tables) == 1, 'symbol table count')
    symtab = tables[0]
    need(symtab['size'] >= 16 and symtab['entry_size'] == 16 and
         symtab['link'] < len(e.sections) and e.sections[symtab['link']]['type'] == 3 and
         symtab['index'] in e.symbol_tables and len(e.symbol_tables[symtab['index']]) > 0,
         'symbol table layout')
    need(not [s for s in e.symbols if s['name'] and s['index'] == 0], 'named undefined')
    alloc = [s['name'] for s in e.sections if s['flags'] & 2]
    need(sorted(alloc) == sorted('.out_'+row[0] for row in SECTIONS), 'alloc section inventory')
    rows = []
    for label, addr, size, input_name in SECTIONS:
        hits = [s for s in e.sections if s['name'] == '.out_'+label]
        need(len(hits) == 1, 'section count '+label)
        sec = hits[0]
        need((sec['type'], sec['flags'], sec['address'], sec['size']) == (1, 6, addr, size), 'section layout '+label)
        symbol_name = input_name.removeprefix('.text.')
        symbols = [s for s in e.symbols if s['name'] == symbol_name]
        need(len(symbols) == 1 and symbols[0]['index'] == sec['index'] and symbols[0]['value'] == addr,
             'selected symbol '+label)
        b = e.data(sec); need(b == image[addr-0x8000:addr-0x8000+size], 'BIN mismatch '+label)
        rows.append({'name': label, 'address': hex(addr), 'bytes': b.hex(),
                     'symbol': {'name': symbol_name, 'value': hex(symbols[0]['value']), 'section_index': symbols[0]['index']}})
    return rows


def expect_rejection(fn, expected):
    try:
        fn()
    except ValueError as exc:
        need(str(exc) == expected, 'unexpected rejection: ' + str(exc))
    else:
        raise ValueError('negative accepted: ' + expected)


def run():
    raw = {key: pinned(ROOT / path, digest) for key, (path, digest) in PINS.items()}
    need(len(raw['bin']) == 76800, 'BIN length')
    base = Path(os.environ['TSL9_NDK_BIN']).resolve()
    clang, lld = base/'clang.exe', base/'ld.lld.exe'
    header = pinned(base.parent/'lib/clang/18/include/stdint.h', TOOLS['stdint.h'])
    splitter = types.ModuleType('splitter'); splitter.__file__ = str(ROOT/PINS['splitter'][0])
    exec(compile(raw['splitter'], 'splitter.py', 'exec'), splitter.__dict__)
    split, offset = splitter.split_verified(raw['owner'])
    parser = types.ModuleType('elf32'); exec(compile(raw['parser'], 'elf32.py', 'exec'), parser.__dict__)
    profiles = json.loads(raw['manifest'])['code_profiles']['queue-consumer-a0-a5']
    results = []
    with tempfile.TemporaryDirectory(prefix='tsl9-105c4-six-') as tmp:
        d = Path(tmp); inc = d/'include'; inc.mkdir(); (inc/'stdint.h').write_bytes(header)
        snapshots = {'owner': raw['owner'], 'split': split, 'callback': raw['callback'], 'leaf': raw['leaf']}
        for k, content in snapshots.items():
            (d/(k+'.c')).write_bytes(content)
        def check_sources():
            need((inc/'stdint.h').read_bytes() == header, 'header snapshot changed')
            for key, content in snapshots.items():
                need((d/(key+'.c')).read_bytes() == content, 'source snapshot changed: '+key)
        for mode in ('c', 'cpp'):
            outputs = d / mode
            outputs.mkdir()
            for k in ('owner', 'split', 'callback', 'leaf'):
                args = ['--no-default-config', *profiles[mode], '-nostdinc']
                if k == 'leaf': args += ['-Dleaf='+NAME]
                else: args += ['-isystem', inc, '-H']
                check_sources()
                output = outputs / (k+'.o')
                need(not output.exists(), 'compile output already exists: '+k)
                p = run_tool(clang, [*args, '-c', d/(k+'.c'), '-o', output], d)
                check_sources()
                need(p.returncode == 0, 'compile %s/%s: %s' % (mode, k, p.stderr.decode('utf8', 'replace')))
                need(output.is_file(), 'compile output missing: '+mode+'/'+k)
                if k != 'leaf':
                    lines = p.stderr.decode('utf8', 'replace').splitlines()
                    need(len(lines) == 1 and lines[0].startswith('. ') and Path(lines[0][2:]).resolve() == (inc/'stdint.h').resolve(), 'include trace ' + k)
            object_snapshots = {k: (outputs/(k+'.o')).read_bytes() for k in snapshots}
            def check_objects():
                check_sources()
                for key, content in object_snapshots.items():
                    need((outputs/(key+'.o')).read_bytes() == content, 'object snapshot changed: '+key)
            relocations = {}
            for owner_unit in ('owner', 'split'):
                found = []
                for unit in (owner_unit, 'callback'):
                    obj = parser.ELF(outputs/(unit+'.o'))
                    owners = {row[3] for row in SECTIONS}
                    for rel in obj.relocations:
                        if rel['owner'] in owners:
                            found.append((rel['owner'], rel['offset'], rel['type'], rel['symbol']['name'], rel['addend']))
                need(found == EXPECTED_RELOCATIONS, 'selected input relocations: '+owner_unit)
                relocations[owner_unit] = found
            leaf_obj = parser.ELF(outputs/'leaf.o')
            need(not [r for r in leaf_obj.relocations if r['owner'] == '.leaf'], 'leaf relocations')
            for case in ('original', 'split'):
                layout = outputs/'layout.ld'; layout.write_text(linker_script(case == 'split'), encoding='ascii')
                objects = [outputs/(('owner' if case == 'original' else 'split')+'.o'), outputs/'callback.o']
                if case == 'split': objects.append(outputs/'leaf.o')
                output = outputs/(case+'.elf')
                need(not output.exists(), 'link output already exists: '+mode+'/'+case)
                check_objects(); layout_snapshot = layout.read_bytes()
                p = run_tool(lld, ['--no-undefined', '--no-relax', '--gc-sections', '--fatal-warnings', '-T', layout,
                                   '-e', 'tsl9_feature_external_10944', *objects, '-o', output], d)
                check_objects(); need(layout.read_bytes() == layout_snapshot, 'layout snapshot changed')
                need(p.returncode == 0, 'link %s/%s: %s' % (mode, case, p.stderr.decode('utf8', 'replace')))
                need(output.is_file(), 'link output missing: '+mode+'/'+case)
                final = parser.ELF(output)
                rows = selected(final, raw['bin'])
                # Mutate a real linked ELF, then verify the parser sees the change before
                # exercising this guard. This is a bounded negative, not an ELF audit.
                shoff = struct.unpack_from('<I', final.raw, 32)[0]
                symtab = next(s for s in final.sections if s['type'] == 2)
                corrupted = bytearray(final.raw)
                struct.pack_into('<I', corrupted, shoff + symtab['index'] * 40 + 4, 1)
                mutated_path = outputs / 'missing-symtab.elf'; mutated_path.write_bytes(corrupted)
                mutated = parser.ELF(mutated_path)
                need(not any(s['type'] == 2 for s in mutated.sections), 'symtab mutation')
                expect_rejection(lambda: selected(mutated, raw['bin']), 'symbol table count')
                corrupt_dyn = bytearray(final.raw)
                struct.pack_into('<I', corrupt_dyn, shoff + symtab['index'] * 40 + 4, 11)
                mutated_path = outputs / 'dynamic-symtab.elf'; mutated_path.write_bytes(corrupt_dyn)
                mutated = parser.ELF(mutated_path)
                need(any(s['type'] == 11 for s in mutated.sections), 'dynsym mutation')
                expect_rejection(lambda: selected(mutated, raw['bin']), 'dynamic symbol table')
                truncated = bytearray(final.raw)
                need(final.raw[symtab['offset']:symtab['offset']+16] == bytes(16), 'symbol zero bytes')
                struct.pack_into('<I', truncated, shoff + symtab['index'] * 40 + 20, 16)
                struct.pack_into('<I', truncated, shoff + symtab['index'] * 40 + 28, 1)
                mutated_path = outputs / 'null-only-symtab.elf'; mutated_path.write_bytes(truncated)
                mutated = parser.ELF(mutated_path)
                null_table = next(s for s in mutated.sections if s['type'] == 2)
                need(null_table['size'] == 16 and null_table['info'] == 1 and
                     mutated.raw[null_table['offset']:null_table['offset']+16] == bytes(16) and
                     len(mutated.symbols) == 1 and mutated.symbols[0]['name'] == '', 'null-only symtab mutation')
                expect_rejection(lambda: selected(mutated, raw['bin']), 'selected symbol target')
                entries = final.symbol_tables[symtab['index']]
                selected_names = {row[3].removeprefix('.text.') for row in SECTIONS}
                spare = next((i for i, s in enumerate(entries) if s['name'] and s['name'] not in selected_names and s['index'] != 0), None)
                need(spare is not None, 'spare symbol for duplicate negative')
                symbol_negatives = []
                for label, address, _, input_name in SECTIONS:
                    name = input_name.removeprefix('.text.')
                    matches = [i for i, s in enumerate(entries) if s['name'] == name]
                    need(len(matches) == 1, 'selected symbol mutation source '+label)
                    i = matches[0]; ent = symtab['offset'] + 16*i
                    for kind in ('missing', 'duplicate', 'wrong-address', 'wrong-section'):
                        altered = bytearray(final.raw)
                        if kind == 'missing':
                            struct.pack_into('<I', altered, ent, 0)
                        elif kind == 'duplicate':
                            struct.pack_into('<I', altered, symtab['offset'] + 16*spare,
                                             struct.unpack_from('<I', final.raw, ent)[0])
                        elif kind == 'wrong-address':
                            struct.pack_into('<I', altered, ent+4, address+2)
                        else:
                            struct.pack_into('<H', altered, ent+14, 0xfff1)  # SHN_ABS
                        path = outputs / 'wrong-symbol.elf'; path.write_bytes(altered)
                        observed = parser.ELF(path)
                        symbols = [s for s in observed.symbols if s['name'] == name]
                        if kind == 'missing': need(not symbols, 'missing symbol mutation '+label)
                        elif kind == 'duplicate': need(len(symbols) == 2, 'duplicate symbol mutation '+label)
                        elif kind == 'wrong-address': need(len(symbols) == 1 and symbols[0]['value'] == address+2, 'symbol value mutation '+label)
                        else: need(len(symbols) == 1 and symbols[0]['index'] == 0xfff1, 'symbol section mutation '+label)
                        expect_rejection(lambda: selected(observed, raw['bin']), 'selected symbol '+label)
                        symbol_negatives.append(label+':'+kind)
                results.append({'mode': mode, 'case': case, 'bytes_matched': sum(r[2] for r in SECTIONS), 'sections': rows,
                                'final_elf_sha256': hashlib.sha256(final.raw).hexdigest(),
                                'elf_negatives': ['missing-symtab', 'dynamic-symtab', 'null-only-symtab'],
                                'symbol_negatives': symbol_negatives})
            # Strong undefined must fail without the candidate; no synthetic provider.
            layout.write_text(linker_script(True), encoding='ascii')
            common = ['--no-undefined', '--no-relax', '--gc-sections', '--fatal-warnings', '-T', layout,
                      '-e', 'tsl9_feature_external_10944']
            p = run_tool(lld, [*common, outputs/'split.o', outputs/'callback.o', '-o', outputs/'missing.elf'], d)
            need(p.returncode != 0 and b'undefined symbol' in p.stderr and NAME.encode() in p.stderr, 'missing leaf negative')
            changed_layout = linker_script(True).replace('.out_target 0x105c4', '.out_target 0x105c6')
            need(changed_layout != linker_script(True), 'layout mutation')
            layout.write_text(changed_layout, encoding='ascii')
            p = run_tool(lld, [*common, outputs/'split.o', outputs/'callback.o', outputs/'leaf.o', '-o', outputs/'wrong-address.elf'], d)
            need(p.returncode == 0, 'wrong address link negative')
            expect_rejection(lambda: selected(parser.ELF(outputs/'wrong-address.elf'), raw['bin']), 'section layout target')
            p = run_tool(clang, ['--no-default-config', *profiles[mode], '-nostdinc', '-Dleaf='+NAME,
                                 '-DNEGATIVE', '-c', d/'leaf.c', '-o', outputs/'negative.o'], d)
            need(p.returncode == 0 and (outputs/'negative.o').is_file(), 'negative leaf compile')
            layout.write_text(linker_script(True), encoding='ascii')
            p = run_tool(lld, [*common, outputs/'split.o', outputs/'callback.o', outputs/'negative.o', '-o', outputs/'negative.elf'], d)
            need(p.returncode == 0 and (outputs/'negative.elf').is_file(), 'negative leaf link')
            expect_rejection(lambda: selected(parser.ELF(outputs/'negative.elf'), raw['bin']), 'BIN mismatch target')
            check_objects()
            results.append({'mode': mode, 'negative_checks': ['missing-leaf undefined', 'wrong-target-address', 'wrong-leaf-constant'],
                            'object_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in object_snapshots.items()},
                            'selected_original_and_split_relocations': relocations})
    return {'status': 'INCOMPLETE_FAIL_CLOSED', 'passed': False, 'selected_checks_passed': True,
            'input_sha256': {key: hashlib.sha256(data).hexdigest() for key, data in raw.items()},
            'checked_tool_sha256': TOOLS, 'split_offset': offset, 'cases': results,
            'limits': 'Selected static sections only. Symbol checks cover name, address and section index, not type, binding, size or visibility. Listed discard patterns include addrsig; unselected non-alloc sections are not inventoried. Fallthrough, full ABI, reachability, owner and complete BIN not proved. No target execution.'}


if __name__ == '__main__':
    try:
        need(not sys.argv[1:], 'no arguments supported')
        need(sys.version_info >= (3, 9), 'Python 3.9 or newer required')
        print(json.dumps(run(), indent=2))
    except Exception as exc:
        print(json.dumps({'status': 'INCOMPLETE_FAIL_CLOSED', 'passed': False, 'selected_checks_passed': False,
                          'error': type(exc).__name__ + ': ' + str(exc)}, indent=2))
    sys.exit(1)
