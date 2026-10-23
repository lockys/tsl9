#!/usr/bin/env python3
"""Version3 retains v1/v2 and rejects independently demonstrated UND/SSA escapes.

Version1 checker/receipt are preserved. No target execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = json.loads((HERE/'spec.json').read_bytes())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(ROOT/S['reader']) == S['reader_sha256'], 'Frozen ELF reader')
E = runpy.run_path(str(ROOT/S['reader']))['ELF']
B = runpy.run_path(str(HERE/'build.py'))
DEFS = {n: (a, z) for n, a, z in S['parent_definitions']}
DEFS['tsl9_queue_external_9b36'] = (0x9B36, 24)
FRONTIER = {n: a for n, a in S['parent_missing_providers'].items() if n not in DEFS}
MASKS = {16: (4, 0x01FFF07F), 17: (4, 0x00000FFF), 44: (2, 0xE383), 45: (2, 0xE003)}
LEAF_HEX = '83c7810a89ebb717014003a7c7801347270023a6e7808280'
LEAF_PHDR = [[6, 52, 36916, 36916, 128, 128, 4, 4],
             [1, 0, 36864, 36864, 180, 180, 4, 4096],
             [1, 2870, 39734, 39734, 24, 24, 5, 4096],
             [0x6474E551, 0, 0, 0, 0, 0, 6, 0]]
PINS = {'native.o': 'df3f285c1996ec30c35ab85452274143d3d87f74ed96d3771db7e141b0ae4600',
        'LEAF-ONLY-NOT-FIRMWARE.elf': '6b4d7581d1d7749220ce7ca7ef33761725d5ec81d48290d5ddc833a730294cd5',
        'UNRESOLVED-FULL-PLUS-LEAF.o': 'da50985e5af82c20d20aded44aca8449cc5ecb8a891fea82c0667d851b3bb42b'}


def functions(e):
    return [s for s in e.symbols if s['info'] & 15 == 2]


def canonical(name):
    return S['alias'].get(name, name)


def code(e, f):
    sec = e.sections[f['section']]
    at = f['value'] - sec['address']
    return e.data(sec)[at:at+f['size']]


def edges(e, f):
    sec = e.sections[f['section']]
    start = f['value'] - sec['address']
    return sorted((r['offset']-start, r['type'], canonical(e.symbols[r['symbol']]['name']), r['addend'])
                  for r in e.relocations if r['section'] == f['section'] and start <= r['offset'] < start+f['size'])


def sign(value, bits):
    return value-(1 << bits) if value & (1 << (bits-1)) else value


def destination(word, kind, pc):
    if kind == 17:
        need(word & 127 == 0x6F, 'Original JAL family')
        value = ((word >> 31) << 20) | (((word >> 21) & 1023) << 1) | (((word >> 20) & 1) << 11) | (((word >> 12) & 255) << 12)
        return pc+sign(value, 21)
    if kind == 16:
        need(word & 127 == 0x63, 'Original branch family')
        value = ((word >> 31) << 12) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1) | (((word >> 7) & 1) << 11)
        return pc+sign(value, 13)
    if kind == 45:
        need(word & 0xE003 in (0xA001, 0x2001), 'Original compressed jump family')
        value = (((word >> 12) & 1) << 11) | (((word >> 11) & 1) << 4) | (((word >> 9) & 3) << 8) | (((word >> 8) & 1) << 10) | (((word >> 7) & 1) << 6) | (((word >> 6) & 1) << 7) | (((word >> 3) & 7) << 1) | (((word >> 2) & 1) << 5)
        return pc+sign(value, 12)
    need(kind == 44 and word & 0xE003 in (0xC001, 0xE001), 'Original compressed branch family')
    value = (((word >> 12) & 1) << 8) | (((word >> 10) & 3) << 3) | (((word >> 5) & 3) << 6) | (((word >> 3) & 3) << 1) | (((word >> 2) & 1) << 5)
    return pc+sign(value, 9)


def instruction_count(raw):
    at = count = 0
    while at < len(raw):
        need(at+2 <= len(raw), 'Complete instruction halfword')
        width = 4 if int.from_bytes(raw[at:at+2], 'little') & 3 == 3 else 2
        need(at+width <= len(raw), 'Complete instruction extent')
        at += width
        count += 1
    return count


def leaf(raw, linked):
    e = E(raw)
    need(e.header[0] == (2 if linked else 1) and e.header[3] == (0x9B36 if linked else 0), 'Leaf ELF type/entry')
    need(e.program_headers == (LEAF_PHDR if linked else []), 'Exact complete leaf PHDR inventory')
    fs = functions(e)
    need(len(fs) == 1, 'One leaf FUNC')
    f = fs[0]
    need(f['name'] == 'tsl9_queue_external_9b36' and f['info'] == 18 and f['other'] == 0 and f['size'] == 24,
         'Genuine strong visible leaf FUNC')
    sec = e.sections[f['section']]
    need((sec['name'], sec['type'], sec['flags'], sec['size'], sec['align'], sec['address']) ==
         ('.toggle' if linked else '.text.tsl9_queue_external_9b36', 1, 6, 24, 2, 0x9B36 if linked else 0), 'Leaf code ownership')
    need(f['value'] == sec['address'] and e.data(sec).hex() == LEAF_HEX, 'All original leaf bytes')
    need(not e.relocations and not [s for s in e.symbols if s['name'] and s['section'] == 0], 'Leaf has no RELA/UND')
    need(not [s for s in e.symbols if s['section'] == 0xFFF1 and s['info'] >> 4], 'No global ABS')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [sec['index']], 'Only leaf allocation')
    return e


def scoped_sources(llvm, mode):
    manifest = json.loads((ROOT/'src/source-manifest.json').read_bytes())
    selected_names = {u['name'] for u in S['units']}
    actual_units = [{k: u[k] for k in S['units'][0]} for u in manifest['native_units'] if u['name'] in selected_names]
    selected_files = {f['destination'] for f in S['manifest_scope']['files']}
    actual_files = [f for f in manifest['files'] if f['destination'] in selected_files]
    need(sorted(actual_units, key=lambda u: u['name']) == sorted(S['manifest_scope']['units'], key=lambda u: u['name'])
         and actual_files == S['manifest_scope']['files'], 'Exact selected source manifest entries')
    for f in actual_files:
        need(sha(ROOT/f['origin']) == f['origin_sha256'] and sha(ROOT/f['destination']) == f['sha256'], 'Actual selected source identities')
    base = ROOT/S['curation_root']
    need(sha(base/'verification.json') == S['curation_receipt_sha256'], 'Immutable fresh curation receipt')
    receipt = json.loads((base/'verification.json').read_bytes())
    result = {}
    for u in S['units']:
        folder = base/u['name']/mode/'curated'
        command = next(c for c in receipt['commands'] if (c['unit'], c['mode'], c['variant']) == (u['name'], mode, 'curated'))
        expected = [str(llvm/'clang.exe')]+S['unit_flags'][u['name']][mode]+['-c', '-MD', '-MF', str(folder/'unit.d'), '-MT', 'unit.o', str(ROOT/u['curated_unit']), '-o', str(folder/'unit.o')]
        need(command['argv'] == expected and command['exit'] == 0 and command['log_sha256'] == sha(folder/'compile.log'), 'Actual scoped compile recipe '+u['name'])
        deps = receipt['dependencies'][folder.relative_to(base).as_posix()]
        need(str(ROOT/u['curated_unit']) in deps, 'Actual source dependency')
        for p, pin in deps.items():
            need(sha(p) == pin, 'Current dependency identity')
        for name in ('unit.o', 'unit.d', 'compile.log'):
            need(sha(folder/name) == receipt['artifacts'][(folder/name).relative_to(base).as_posix()], 'Captured scoped artifact identity')
        obj = E(folder/'unit.o')
        for f in functions(obj):
            name = canonical(f['name'])
            need(name not in result and f['info'] == 18 and f['other'] == 0, 'Unique genuine scoped source FUNC')
            result[name] = (obj, f)
    need(set(result) == set(DEFS), 'All108 functions map to current scoped C sources')
    return result


def joined(raw, sources, firmware, parent):
    e = E(raw)
    need(e.header[0] == 1 and e.header[3] == 0 and not e.program_headers, 'Diagnostic ET_REL, no entry/PHDR')
    sec = e.section('.full_plus_leaf')
    need((sec['type'], sec['flags'], sec['address'], sec['size'], sec['align']) == (1, 6, 0, 1926, 2), 'Exact component section')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [sec['index']], 'Only diagnostic code allocation')
    need(e.data(sec) == parent.data('.full')+bytes.fromhex(LEAF_HEX), 'Unchanged genuine parent prefix and new leaf')
    fs = functions(e)
    need(len(fs) == 108 and {f['name'] for f in fs} == set(DEFS), 'Exact genuine function inventory')
    need(not [s for s in e.symbols if s['section'] == 0xFFF1 and s['info'] >> 4], 'No global ABS provider substitutes')
    und = sorted(s['name'] for s in e.symbols if s['name'] and s['section'] == 0)
    need(und == sorted(FRONTIER), 'Three true remaining undefined providers')
    need(all(s['info'] == 16 and s['other'] == s['value'] == s['size'] == 0 for s in e.symbols if s['name'] and s['section'] == 0), 'Strong canonical zero-valued zero-sized UND records')
    parent_fs = {f['name']: f for f in functions(parent)}
    pc_edges = []
    occupied = []
    for f in sorted(fs, key=lambda x: x['value']):
        name = f['name']
        address, size = DEFS[name]
        need(f['info'] == 18 and f['other'] == 0 and f['section'] == sec['index'] and f['size'] == size, 'Strong FUNC ownership '+name)
        need(f['value'] == sum(occupied), 'Contiguous nonoverlapping FUNC coverage')
        occupied.append(size)
        if name in parent_fs:
            old = parent_fs[name]
            need(f['value'] == old['value'] and code(e, f) == code(parent, old) and edges(e, f) == edges(parent, old), 'Unchanged parent FUNC/edge '+name)
        else:
            need(f['value'] == 1902 and name == 'tsl9_queue_external_9b36', 'New genuine leaf placement')
        obj, source_func = sources[name]
        need(code(e, f) == code(obj, source_func) and edges(e, f) == edges(obj, source_func), 'Exact current scoped source body/typed edges '+name)
        raw_code = code(e, f)
        original = firmware[address-0x8000:address-0x8000+size]
        need(len(original) == size, 'Original firmware extent')
        masks = bytearray([255]*size)
        for at, kind, target, addend in edges(e, f):
            need(kind in MASKS and addend == 0, 'Permitted typed relocation with zero addend')
            width, mask = MASKS[kind]
            need(0 <= at <= size-width and all(v == 255 for v in masks[at:at+width]), 'Nonoverlapping control field ownership')
            masks[at:at+width] = mask.to_bytes(width, 'little')
            target_pc = DEFS[target][0] if target in DEFS else FRONTIER[target]
            pc = address+at
            need(destination(int.from_bytes(original[at:at+width], 'little'), kind, pc) == target_pc, 'Original typed edge destination')
            pc_edges.append(dict(original_PC=pc, relocation_type=kind, target=target, target_PC=target_pc, addend=0))
        need(all(a & m == b & m for a, b, m in zip(raw_code, original, masks)), 'All original nonrelocation bits '+name)
    need(sum(occupied) == 1926 and len(e.relocations) == len(pc_edges) == 97, 'Complete function and relocation coverage')
    new = next(x for x in pc_edges if x['original_PC'] == 0x12D1C)
    need(new['target'] == 'tsl9_queue_external_9b36' and new['target_PC'] == 0x9B36, 'Original queue call binds genuine new provider')
    need(instruction_count(e.data(sec)) == 669, '669 complete instructions')
    return e, pc_edges


def IR(text):
    # Explicit SSA chain of the compiler output; instructions are not executed.
    start = text.index('define dso_local void @tsl9_queue_external_9b36()')
    body = text[start:text.index('\n}', start)+2]
    need(hashlib.sha256(body.encode()).hexdigest() == 'd7ae07d179353c26a68ba395d0fb647445a6755f22b0344cef4ab5ed4da5f69e', 'Complete exact SSA body including all extracts, ports and calls')
    need(body.count('asm sideeffect ""') == 6 and not re.search(r'asm sideeffect "[^\"]+', body), 'Only six empty register ports')
    need(len(re.findall(r'load volatile', body)) == 2 and len(re.findall(r'store volatile', body)) == 1, 'Exactly three volatile accesses')
    snippets = ['"={x3},={x14},~{memory}"()', '%4 = add i32 %2, 168',
                '%6 = load volatile i8, ptr %5, align 1', '%7 = zext i8 %6 to i32',
                '%9 = icmp eq i32 %8, 0', 'br i1 %9, label %10, label %25',
                '(i32 %3, i32 1073811456)', '%13 = add i32 %12, -2036',
                '%15 = load volatile i32, ptr %14, align 4', '%19 = xor i32 %17, 2',
                '%23 = add i32 %22, -2036', 'store volatile i32 %21, ptr %24, align 4',
                '%26 = phi i32 [ %21, %10 ], [ %3, %0 ]',
                '%27 = phi i32 [ %22, %10 ], [ %8, %0 ]', '(i32 %26, i32 %27)', 'ret void']
    positions = [body.index(x) for x in snippets]
    need(positions == sorted(positions), 'Ordered SSA guard/read/XOR/store and preserved skip outputs')
    need(not re.search(r'\balloca\b|\b(?:atomicrmw|cmpxchg|fence)\b|call.*@(?!tsl9)', body), 'No hidden stack/call/atomicity promise')
    return dict(empty_register_ports=6, volatile_accesses=3, skip_preserves_entry_A4=True, C_owns_guard_read_XOR2_write=True)


def rejected(fn):
    try:
        fn()
    except (ValueError, KeyError, IndexError, struct.error):
        return True
    return False


def verify(llvm, folder, mode, write):
    measurement = json.loads((folder/'measurement.json').read_bytes())
    need(measurement['inputs'] == B['portable'](B['inputs'](llvm, mode), llvm), 'Exact current producer input identities')
    clang = str(llvm/'clang.exe')
    flags = S['unit_flags']['gp-word-toggle'][mode]
    source = str(ROOT/S['curated'])
    parent_path = ROOT/'experiments/tsl9-receive-transmit-chain/build/integration-v2'/mode/'UNRESOLVED-FULL-COMPONENT.o'
    recipes = [
        ('compile', [clang]+flags+['-c', '-MD', '-MF', str(folder/'native.d'), '-MT', 'native.o', source, '-o', str(folder/'native.o')]),
        ('IR', [clang]+flags+['-S', '-emit-llvm', source, '-o', str(folder/'native.ll')]),
        ('native-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'native.o')]),
        ('leaf-link', [str(llvm/'ld.lld.exe'), '--no-relax', '-T', str(HERE/'leaf.ld'), str(folder/'native.o'), '-o', str(folder/'LEAF-ONLY-NOT-FIRMWARE.elf')]),
        ('leaf-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'LEAF-ONLY-NOT-FIRMWARE.elf')]),
        ('joined-link', [str(llvm/'ld.lld.exe'), '-r', '--no-relax', '-T', str(HERE/'joined.ld'), str(parent_path), str(folder/'native.o'), '-o', str(folder/'UNRESOLVED-FULL-PLUS-LEAF.o')]),
        ('joined-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'UNRESOLVED-FULL-PLUS-LEAF.o')])]
    expected_commands = [dict(label=label, argv=B['portable'](argv, llvm), exit=0, log_sha256=sha(folder/(label+'.log'))) for label, argv in recipes]
    need(measurement['commands'] == expected_commands, 'Exact seven actual argv/exit/log records')
    need(measurement['mode'] == mode and folder.name == mode, 'Proof language identity')
    need(set(measurement['artifacts']) == {'IR.log', 'LEAF-ONLY-NOT-FIRMWARE.elf', 'UNRESOLVED-FULL-PLUS-LEAF.o', 'compile.log', 'joined-link.log', 'joined-read.log', 'leaf-link.log', 'leaf-read.log', 'native-read.log', 'native.d', 'native.ll', 'native.o'}, 'Exact producer artifact inventory')
    dep = ROOT/S['curation_root']/'gp-word-toggle'/mode/'curated/unit.d'
    need((folder/'native.d').read_bytes().replace(b'native.o:', b'unit.o:', 1) == dep.read_bytes(), 'Exact separately captured compiler dependency closure')
    for n, item in measurement['artifacts'].items():
        need(sha(folder/n) == item['sha256'] and (folder/n).stat().st_size == item['bytes'], 'Unchanged compiler artifact '+n)
    for name, pin in PINS.items():
        need(sha(folder/name) == pin, 'Pinned whole generated ELF '+name)
    firmware = (ROOT/S['firmware']).read_bytes()
    need(sha(ROOT/S['firmware']) == S['firmware_sha256'] and firmware[0x1B36:0x1B4E].hex() == LEAF_HEX, 'Actual original leaf bytes')
    need(sha(HERE/'frozen/manifest-before-toggle.json') == S['old_manifest_sha256'], 'Historical manifest preserved')
    source_objects = scoped_sources(llvm, mode)
    parent = E(ROOT/'experiments/tsl9-receive-transmit-chain/build/integration-v2'/mode/'UNRESOLVED-FULL-COMPONENT.o')
    native = leaf((folder/'native.o').read_bytes(), False)
    standalone = leaf((folder/'LEAF-ONLY-NOT-FIRMWARE.elf').read_bytes(), True)
    component, edge_rows = joined((folder/'UNRESOLVED-FULL-PLUS-LEAF.o').read_bytes(), source_objects, firmware, parent)
    ir = IR((folder/'native.ll').read_text(encoding='utf8'))
    for log, count, obj, name in [('native-read.log', 7, native, '.text.tsl9_queue_external_9b36'),
                                  ('leaf-read.log', 7, standalone, '.toggle'),
                                  ('joined-read.log', 669, component, '.full_plus_leaf')]:
        rows = re.findall(r'^\s*([0-9a-f]+):\s+([0-9a-f]{2}(?: [0-9a-f]{2}){1,3})\s{2,}\S.*$', (folder/log).read_text(encoding='utf8'), re.M)
        need(len(rows) == count, 'Actual LLVM decoded row inventory '+log)
        sec = obj.section(name)
        at = 0
        for address, octets in rows:
            data = bytes.fromhex(octets)
            need(int(address, 16) == sec['address']+at and len(data) == (4 if data[0] & 3 == 3 else 2), 'Every readback address/width')
            need(data == obj.data(sec)[at:at+len(data)], 'Every actual LLVM byte equals ELF byte')
            at += len(data)
        need(at == sec['size'], 'Complete actual LLVM readback coverage')
    negatives = []
    for obj, linked in [(native, False), (standalone, True)]:
        section = obj.sections[functions(obj)[0]['section']]
        for at in range(24):
            b = bytearray(obj.raw); b[section['offset']+at] ^= 1
            need(rejected(lambda: leaf(bytes(b), linked)), 'Mutated leaf byte rejected')
            negatives.append('leaf-byte-'+str(linked)+'-'+str(at))
    for at in range(1926):
        b = bytearray(component.raw); b[component.section('.full_plus_leaf')['offset']+at] ^= 1
        need(rejected(lambda: joined(bytes(b), source_objects, firmware, parent)), 'Mutated joined code byte rejected')
        negatives.append('joined-byte-'+str(at))
    for label, offset, fmt, value in [('entry', 24, '<I', 0x9B38), ('RX-extent', 52+64+16, '<I', 26),
                                      ('extra-LOAD', 52+96, '<I', 1), ('LOAD-align', 52+64+28, '<I', 2)]:
        b = bytearray(standalone.raw); struct.pack_into(fmt, b, offset, value)
        need(rejected(lambda: leaf(bytes(b), True)), 'Mutated mapping rejected '+label)
        negatives.append(label)
    symtab = next(s for s in component.sections if s['type'] == 2)
    f = next(f for f in functions(component) if f['name'] == 'tsl9_queue_external_9b36')
    b = bytearray(component.raw); b[symtab['offset']+16*f['index']+12] = 34
    need(rejected(lambda: joined(bytes(b), source_objects, firmware, parent)), 'Weak new FUNC rejected')
    negatives.append('weak-provider')
    relsec = next(s for s in component.sections if s['type'] == 4)
    for label, field, value in [('RELA-addend', 8, 2), ('RELA-owner-offset', 0, 1926), ('RELA-symbol', 4, 17)]:
        b = bytearray(component.raw); struct.pack_into('<I', b, relsec['offset']+field, value)
        need(rejected(lambda: joined(bytes(b), source_objects, firmware, parent)), 'Mutated relocation rejected '+label)
        negatives.append(label)
    for old, new in [('xor i32 %17, 2', 'xor i32 %17, 3'), ('load volatile i8', 'load i8'),
                     ('[ %3, %0 ]', '[ 0, %0 ]')]:
        text = (folder/'native.ll').read_text(encoding='utf8')
        need(old in text and rejected(lambda: IR(text.replace(old, new))), 'Mutated SSA chain rejected')
        negatives.append('IR-'+old)
    und_symbol = next(s for s in component.symbols if s['name'] and s['section'] == 0)
    for label, offset, fmt, value in [('weak-UND', 12, '<B', 32), ('UND-value', 4, '<I', 4), ('UND-size', 8, '<I', 4)]:
        b = bytearray(component.raw)
        struct.pack_into(fmt, b, symtab['offset']+16*und_symbol['index']+offset, value)
        need(rejected(lambda: joined(bytes(b), source_objects, firmware, parent)), 'Independent UND escape now rejected '+label)
        negatives.append(label)
    for old, new in [('%17 = extractvalue { i32, i32 } %16, 0', '%17 = extractvalue { i32, i32 } %16, 1'),
                     ('  ret void', '  call void @tsl9_unproved()\n  ret void'),
                     ('={x14},={x15},{x14},{x15}', '={x13},={x15},{x13},{x15}')]:
        text = (folder/'native.ll').read_text(encoding='utf8')
        need(old in text and rejected(lambda: IR(text.replace(old, new))), 'Independent SSA escape now rejected')
        negatives.append('independent-IR-'+old)
    result = dict(schema='TSL9-gp-word-toggle-static-proof-v3', passed=True, mode=mode,
                  checker_sha256=sha(Path(__file__)), measurement_sha256=sha(folder/'measurement.json'),
                  source_sha256=S['source_sha256'], leaf_bytes=24, leaf_instructions=7,
                  independent_UND_and_SSA_escapes_rejected=6,
                  exact_command_recipes_verified=True, curation_receipt_sha256=S['curation_receipt_sha256'],
                  scoped_objects={u['name']: sha(ROOT/S['curation_root']/u['name']/mode/'curated/unit.o') for u in S['units']},
                  leaf_code_sha256=S['leaf_code_sha256'], compiled_ELF_SHA256=PINS, IR=ir,
                  joined_bytes=1926, joined_instructions=669, strong_FUNC=108, typed_RELA=97,
                  remaining_UND=sorted(FRONTIER), current_source_units_checked=13,
                  scoped_source_manifest_checked=True, whole_mutable_manifest_pinned=False,
                  original_typed_edges=edge_rows, negative_controls=len(negatives),
                  negative_controls_without_whole_ELF_hash=True,
                  parent_1902_code_unchanged=True, old_manifest_snapshot_preserved=True,
                  historical_receipts_rewritten=False, historical_full_receipt_replayed_after_manifest_change=False,
                  architectural_register_ports=True, ordinary_function_ABI_proved=False,
                  physical_MMIO_purpose_proved=False, full_runtime_graph_proved=False,
                  target_executed=False, ISA_emulated=False, hardware_accessed=False,
                  firmware_BIN_generated=False, firmware_ready=False, hardware_OTA_proved=False)
    if write:
        destination = folder/'verification-v3.json'
        need(not destination.exists(), 'Create-only new verification receipt')
        destination.write_bytes(B['encode'](result))
    else:
        need((folder/'verification-v3.json').read_bytes() == B['encode'](result), 'Exact saved proof bytes reproduced read-only')
    print(json.dumps({k: result[k] for k in ('passed', 'mode', 'leaf_bytes', 'joined_bytes', 'strong_FUNC', 'typed_RELA', 'remaining_UND', 'negative_controls', 'firmware_ready')}))


if __name__ == '__main__':
    try:
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument('--tool-dir', type=Path, required=True)
        p.add_argument('--folder', type=Path, required=True)
        p.add_argument('--mode', choices=['c', 'cpp'], required=True)
        p.add_argument('--write', action='store_true')
        a = p.parse_args()
        verify(a.tool_dir.resolve(), a.folder.resolve(), a.mode, a.write)
    except (ValueError, OSError, KeyError) as error:
        print('FAIL: '+str(error), file=sys.stderr)
        sys.exit(1)
