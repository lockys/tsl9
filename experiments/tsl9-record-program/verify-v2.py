#!/usr/bin/env python3
"""Version2 preserves v1 and fixes nominal FUNC ownership; no ISA execution."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B = runpy.run_path(str(HERE/'build.py'))
S = B['S']; P = B['P']; need = B['need']; sha = B['sha']
need(sha(ROOT/S['reader']) == S['reader_sha256'], 'Frozen ELF reader')
need(sha(ROOT/P['previous_checker']) == P['previous_checker_sha256'], 'Frozen upstream proof')
G = runpy.run_path(str(ROOT/P['previous_checker']))
E = runpy.run_path(str(ROOT/S['reader']))['ELF']
DEFS = {n: (a, z) for n, a, z in S['definitions']}


def functions(e):
    return [f for f in e.symbols if f['info'] & 15 == 2]


def code(e, f):
    sec = e.sections[f['section']]
    at = f['value']-sec['address']
    return e.data(sec)[at:at+f['size']]


def edges(e, f):
    sec = e.sections[f['section']]
    start = f['value']-sec['address']
    return sorted((r['offset']-start, r['type'], e.symbols[r['symbol']]['name'], r['addend'])
                  for r in e.relocations if r['section'] == f['section'] and start <= r['offset'] < start+f['size'])


def canonical_symbols(e):
    need(e.header[6] == 1, 'Original RV32 RVC ELF flags')
    need(not [x for x in e.symbols if x['section'] == 0xFFF1 and x['info'] >> 4], 'No global ABS substitutes')
    need(all(f['info'] == 18 and f['other'] == 0 for f in functions(e)), 'All genuine strong visible FUNC')
    need(all(f['info'] == 16 and f['other'] == f['value'] == f['size'] == 0 for f in e.symbols if f['name'] and f['section'] == 0), 'Canonical genuine UND records')


def native(raw, firmware):
    e = E(raw)
    need(e.header[0] == 1 and e.header[3] == 0 and not e.program_headers, 'Native ET_REL')
    canonical_symbols(e)
    need(len(functions(e)) == 19 and {f['name'] for f in functions(e)} == set(DEFS), 'Exact19 original regions')
    need(not [x for x in e.symbols if x['name'] and x['section'] == 0], 'No native UND')
    actual_controls = []
    allocated = []
    for f in functions(e):
        address, size = DEFS[f['name']]
        sec = e.sections[f['section']]
        need((sec['type'], sec['flags'], sec['address'], sec['size'], sec['align'], f['value'], f['size'], sec['name']) == (1, 6, 0, size, 2, 0, size, '.text.'+f['name']), 'Native region ownership/extent')
        allocated.append(sec['index'])
        data = code(e, f)
        original = firmware[address-0x8000:address-0x8000+size]
        mask = bytearray([255]*size)
        for at, kind, target, addend in edges(e, f):
            need(kind in G['MASKS'] and addend == 0 and target in DEFS, 'Typed known direct control')
            width, bits = G['MASKS'][kind]
            need(0 <= at <= size-width and all(v == 255 for v in mask[at:at+width]), 'Disjoint control fields')
            mask[at:at+width] = bits.to_bytes(width, 'little')
            need(G['destination'](int.from_bytes(original[at:at+width], 'little'), kind, address+at) == DEFS[target][0], 'Actual original control destination')
            actual_controls.append([address+at, kind, target, addend])
        need(all(a & m == b & m for a, b, m in zip(data, original, mask)), 'Every original noncontrol bit')
    need(sorted(actual_controls) == S['controls'] and len(e.relocations) == 12, 'All12 typed controls')
    need(set(allocated) == {s['index'] for s in e.sections if s['flags'] & 2 and s['size']}, 'No hidden allocations')
    return e


def nominal(raw, firmware):
    e = E(raw)
    need(e.header[0] == 2 and e.header[3] == 0x9454 and e.program_headers == P['nominal_PHDR'], 'Exact diagnostic entry and full PHDR inventory')
    canonical_symbols(e)
    sec = e.section('.program')
    need((sec['type'], sec['flags'], sec['address'], sec['size'], sec['align']) == (1, 6, 0x93AA, 324, 2), 'Original code section')
    need(e.data(sec) == firmware[0x13AA:0x14EE], 'All324 original bytes including controls and PC-dependent addresses')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [sec['index']], 'Only original code allocation')
    need(not e.relocations and not [s for s in e.symbols if s['name'] and s['section'] == 0], 'No nominal RELA/UND')
    need(all(f['section'] == sec['index'] and sec['address'] <= f['value'] and f['value']+f['size'] <= sec['address']+sec['size'] for f in functions(e)), 'Every nominal FUNC belongs to proved code extent')
    need(sorted((f['name'], f['value'], f['size']) for f in functions(e)) == sorted(tuple(x) for x in S['definitions']), 'Every original FUNC address and size')
    return e


def joined(raw, parent, source):
    e = E(raw)
    need(e.header[0] == 1 and e.header[3] == 0 and not e.program_headers, 'Diagnostic partial link only')
    canonical_symbols(e)
    sec = e.section('.program_graph')
    need((sec['type'], sec['flags'], sec['address'], sec['size'], sec['align']) == (1, 6, 0, 2250, 2), 'Exact2250B diagnostic section')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [sec['index']], 'No hidden full-component allocations')
    new_funcs = {f['name']: f for f in functions(source)}
    new_bytes = b''.join(code(source, new_funcs[n]) for n, a, z in S['definitions'])
    need(e.data(sec) == parent.data('.full_plus_leaf')+new_bytes, 'Actual genuine1926 prefix and324 source bytes')
    old_funcs = {f['name']: f for f in functions(parent)}
    full_funcs = {f['name']: f for f in functions(e)}
    need(len(functions(e)) == 127 and set(full_funcs) == set(old_funcs)|set(DEFS), 'Exact127 genuine FUNC definitions')
    at = 1926
    for name, address, size in S['definitions']:
        f = full_funcs[name]
        need(f['section'] == sec['index'] and f['value'] == at and f['size'] == size, 'New FUNC positions')
        need(code(e, f) == code(source, new_funcs[name]) and edges(e, f) == edges(source, new_funcs[name]), 'Actual current C source bodies/edges')
        at += size
    for name, old in old_funcs.items():
        f = full_funcs[name]
        need(f['section'] == sec['index'] and f['value'] == old['value'] and f['size'] == old['size'] and code(e, f) == code(parent, old) and edges(e, f) == edges(parent, old), 'Unchanged genuine parent FUNC/edges')
    need(len(e.relocations) == 109, 'All109 pending controls retained')
    need(sorted(s['name'] for s in e.symbols if s['name'] and s['section'] == 0) == ['tsl9_queue_external_12abe', 'tsl9_queue_external_14d2e'], 'Two true remaining direct providers')
    need(G['instruction_count'](e.data(sec)) == 778, 'All778 complete instructions')
    return e


def rejected(fn):
    try:
        fn()
    except (ValueError, KeyError, IndexError, struct.error):
        return True
    return False


def verify(llvm, folder, mode, write):
    need(folder.name == mode, 'Language folder')
    measurement = json.loads((folder/'measurement.json').read_bytes())
    need(measurement['inputs'] == B['portable'](B['inputs'](llvm, mode), llvm), 'Exact captured input bytes')
    commands = [dict(label=n, argv=B['portable'](args, llvm), exit=0, log_sha256=sha(folder/(n+'.log'))) for n, args in B['recipes'](llvm, folder, mode)]
    need(measurement['mode'] == mode and measurement['commands'] == commands, 'Exact actual compiler/linker/reader records')
    expected_names = {'native.o', 'native.d', 'native.ll', 'PROGRAM-ONLY-NOT-FIRMWARE.elf', 'UNRESOLVED-PROGRAM-GRAPH.o'}|{n+'.log' for n, args in B['recipes'](llvm, folder, mode)}
    need(set(measurement['artifacts']) == expected_names, 'Exact producer artifact inventory')
    for name, facts in measurement['artifacts'].items():
        need(sha(folder/name) == facts['sha256'] and (folder/name).stat().st_size == facts['bytes'], 'Unchanged compiler output '+name)
    for name, pin in S['tools'].items():
        need(sha(llvm/name) == pin, 'Pinned tool '+name)
    need(sha(ROOT/S['source']) == sha(ROOT/S['curated']) == S['source_sha256'], 'Exact current selected C source')
    need(sha(ROOT/S['firmware']) == S['firmware_sha256'], 'Pinned original firmware')
    need(sha(ROOT/P['curation_root']/'verification.json') == P['curation_receipt_sha256'], 'Frozen80-comparison source receipt')
    manifest = json.loads((ROOT/'src/source-manifest.json').read_bytes())
    need([f for f in manifest['files'] if f['destination'] == S['curated']] == [P['file_entry']], 'Current selected source entry')
    units = [{k: u[k] for k in P['unit_compile_identity']} for u in manifest['native_units'] if u['name'] == 'record-program']
    need(units == [P['unit_compile_identity']], 'Current selected compile identity')
    with contextlib.redirect_stdout(io.StringIO()):
        G['verify'](llvm, B['parent'](mode).parent, mode, False)
    need(sha(B['parent'](mode)) == P['parent_component_sha256'], 'Unchanged source-bound parent')
    firmware = (ROOT/S['firmware']).read_bytes()
    obj = native((folder/'native.o').read_bytes(), firmware)
    nom = nominal((folder/'PROGRAM-ONLY-NOT-FIRMWARE.elf').read_bytes(), firmware)
    full = joined((folder/'UNRESOLVED-PROGRAM-GRAPH.o').read_bytes(), E(B['parent'](mode)), obj)
    curated = ROOT/P['curation_root']/'record-program'/mode/'curated'
    need((folder/'native.d').read_bytes().replace(b'native.o:', b'unit.o:', 1) == (curated/'unit.d').read_bytes(), 'Independent curation MD identity')
    need((folder/'native.o').read_bytes() == (curated/'unit.o').read_bytes(), 'Exact independently compiled current source object')
    count = 0
    for e, sec_name, gate in [(nom, '.program', lambda raw: nominal(raw, firmware)), (full, '.program_graph', lambda raw: joined(raw, E(B['parent'](mode)), obj))]:
        sec = e.section(sec_name)
        for at in range(sec['size']):
            b = bytearray(e.raw); b[sec['offset']+at] ^= 1
            need(rejected(lambda: gate(bytes(b))), 'Every changed allocated code byte rejected without ELF hash')
            count += 1
    for field, value in [(16, 326), (28, 2)]:
        b = bytearray(nom.raw); struct.pack_into('<I', b, 52+64+field, value)
        need(rejected(lambda: nominal(bytes(b), firmware)), 'Expanded/misaligned LOAD rejected')
        count += 1
    table = next(s for s in full.sections if s['type'] == 2)
    missing = next(s for s in full.symbols if s['name'] and s['section'] == 0)
    for offset, fmt, value in [(12, '<B', 32), (4, '<I', 4), (8, '<I', 4)]:
        b = bytearray(full.raw); struct.pack_into(fmt, b, table['offset']+16*missing['index']+offset, value)
        need(rejected(lambda: joined(bytes(b), E(B['parent'](mode)), obj)), 'Canonical UND metadata enforced')
        count += 1
    nt = next(s for s in nom.sections if s['type'] == 2)
    wrong_section = next(s for s in nom.sections if s['name'] == '.strtab')['index']
    for fn in functions(nom):
        b = bytearray(nom.raw)
        struct.pack_into('<H', b, nt['offset']+16*fn['index']+14, wrong_section)
        need(rejected(lambda: nominal(bytes(b), firmware)), 'Every wrong nominal FUNC owner rejected')
        count += 1
    b = bytearray(nom.raw)
    struct.pack_into('<I', b, 36, 0)
    need(rejected(lambda: nominal(bytes(b), firmware)), 'Changed RVC ABI flag rejected')
    count += 1
    b = bytearray(nom.raw)
    b[nt['offset']+16*functions(nom)[0]['index']+12] = 34
    need(rejected(lambda: nominal(bytes(b), firmware)), 'Weak nominal FUNC rejected')
    count += 1
    result = dict(schema='TSL9-record-program-static-proof-v2', passed=True, mode=mode,
                  checker_sha256=sha(Path(__file__)), measurement_sha256=sha(folder/'measurement.json'),
                  original_code_sha256=S['original_code_sha256'], source_sha256=S['source_sha256'],
                  source_bytes=324, source_instructions=109, source_architectural_regions=19,
                  nominal_complete_bytes_equal=True, native_typed_controls=12,
                  native_source_object_equals_independent_curation=True, previous13_source_units_proof_replayed=True,
                  compiled_ELF_SHA256={n: sha(folder/n) for n in ('native.o', 'PROGRAM-ONLY-NOT-FIRMWARE.elf', 'UNRESOLVED-PROGRAM-GRAPH.o')},
                  full_bytes=2250, full_instructions=778, strong_FUNC=127, pending_RELA=109,
                  remaining_UND=['0x12ABE', '0x14D2E'], negative_controls_without_whole_ELF_hash=count,
                  opaque_original_transfers=[dict(PC='0x942A', slot='0x40068', link_RA='0x942C'), dict(PC='0x9452', slot='0x40070', link_RA=False)],
                  resident_preservation_assumed=False, memory_ownership_proved=False, CPU_IRQ_masking_added=False,
                  physical_peripheral_purpose_proved=False, installed_ROM_proved=False,
                  target_executed=False, ISA_emulated=False, hardware_accessed=False, network=False,
                  firmware_BIN_generated=False, firmware_ready=False, hardware_OTA_proved=False)
    destination = folder/'verification-v2.json'
    if write:
        need(not destination.exists(), 'Create-only proof receipt')
        destination.write_bytes(B['encode'](result))
    else:
        need(destination.read_bytes() == B['encode'](result), 'Exact saved receipt bytes replayed')
    print(json.dumps({k: result[k] for k in ('passed', 'mode', 'source_bytes', 'full_bytes', 'remaining_UND', 'negative_controls_without_whole_ELF_hash', 'firmware_ready')}))


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
