#!/usr/bin/env python3
"""Source-bound static proof and corrupted-artifact rejection; no ISA execution."""
import argparse
import contextlib
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
S = B['S']
need, sha = B['need'], B['sha']
need(sha(ROOT/S['reader']) == S['reader_sha256'], 'Pinned ELF reader')
E = runpy.run_path(str(ROOT/S['reader']))['ELF']
MASKS = {16:(4,0x01fff07f), 17:(4,0x00000fff), 44:(2,0xe383), 45:(2,0xe003)}
DEFS = {n:(a,z) for u in S['units'] for n,a,z in u['definitions']}
NEW = sorted([d for u in S['units'] if u['name'] in S['new_units'] for d in u['definitions']], key=lambda d:d[1])
PHDR = [[1,432,0x81b0,0x81b0,68340,68340,5,4096]]
DEST = runpy.run_path(str(ROOT/'experiments/tsl9-spi-filter-setup/probe-v2.py'))['target']


def functions(e):
    return [f for f in e.symbols if f['info'] & 15 == 2]


def code(e, f):
    s = e.sections[f['section']]
    at = f['value']-s['address']
    need(0 <= at <= s['size']-f['size'], 'FUNC entirely in its owned section')
    return e.data(s)[at:at+f['size']]


def edges(e, f):
    sec = e.sections[f['section']]
    start = f['value']-sec['address']
    return sorted((r['offset']-start, r['type'], e.symbols[r['symbol']]['name'], r['addend'])
                  for r in e.relocations if r['section'] == f['section'] and start <= r['offset'] < start+f['size'])


def canonical(e):
    need(e.header[6] == 1, 'Original RV32 RVC ELF flags')
    need(not [s for s in e.symbols if s['section'] == 0xfff1 and s['info'] >> 4], 'No global ABS substitutes')
    need(all(f['info'] == 18 and f['other'] == 0 and f['size'] > 0 for f in functions(e)), 'Strong visible nonempty FUNC')
    need(len({f['name'] for f in functions(e)}) == len(functions(e)), 'Unique FUNC definitions')
    need(all(s['info'] == 16 and s['other'] == s['value'] == s['size'] == 0 for s in e.symbols if s['name'] and s['section'] == 0), 'Canonical true UND symbols')


def instructions(data):
    at = 0
    count = 0
    while at < len(data):
        size = 4 if int.from_bytes(data[at:at+2], 'little') & 3 == 3 else 2
        need(at+size <= len(data), 'Complete RV32 instruction boundary')
        at += size
        count += 1
    return count


def native(raw, unit, firmware):
    e = E(raw)
    need(e.header[0] == 1 and e.header[3] == 0 and not e.program_headers, 'Native ET_REL only')
    canonical(e)
    defs = {n:(a,z) for n,a,z in unit['definitions']}
    need({f['name'] for f in functions(e)} == set(defs), 'Exact native FUNC inventory')
    allocations = set()
    controls = []
    all_edges = 0
    for f in functions(e):
        address, size = defs[f['name']]
        sec = e.sections[f['section']]
        need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align'],f['value'],f['size'],sec['name']) ==
             (1,6,0,size,2,0,size,'.text.'+f['name']), 'Native FUNC section ownership and full extent')
        allocations.add(sec['index'])
        original = firmware[address-0x8000:address-0x8000+size]
        mask = bytearray([255]*size)
        for at, kind, target, addend in edges(e, f):
            need(kind in MASKS and addend == 0 and target in DEFS, 'Known typed original control')
            width,bits = MASKS[kind]
            need(0 <= at <= size-width and all(v == 255 for v in mask[at:at+width]), 'Disjoint complete control fields')
            mask[at:at+width] = bits.to_bytes(width,'little')
            need(DEST(original[at:at+width], address+at, kind) == DEFS[target][0], 'Original branch/call/tail target')
            controls.append((address+at, kind, target))
            all_edges += 1
        actual = code(e,f)
        need(all((a^b)&m == 0 for a,b,m in zip(actual,original,mask)), 'All original non-relocation bits')
    need(allocations == {s['index'] for s in e.sections if s['flags']&2 and s['size']}, 'No extra native allocations')
    need(all_edges == len(e.relocations), 'Every native relocation owned')
    used = {e.symbols[r['symbol']]['name'] for r in e.relocations}
    need({s['name'] for s in e.symbols if s['name'] and s['section'] == 0} == used-set(defs), 'All and only genuine external providers')
    return e, controls


def nominal(raw, firmware):
    e = E(raw)
    need(e.header[0] == 2 and e.header[3] == 0x12abe and e.program_headers == PHDR, 'Exact diagnostic entry/full PHDR inventory')
    canonical(e)
    need(not e.relocations and not [s for s in e.symbols if s['name'] and s['section'] == 0], 'No static UND/RELA')
    need(len(functions(e)) == 94 and {f['name'] for f in functions(e)} == set(DEFS), 'All94 real source FUNC')
    sections = set()
    for lo,hi,digest in S['spans']:
        sec = e.section('.code_'+format(lo,'x'))
        need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align']) == (1,6,lo,hi-lo,2), 'Original-PC proved section extent')
        need(e.data(sec) == firmware[lo-0x8000:hi-0x8000], 'Whole original bytes including displacement and PC-sensitive bits')
        sections.add(sec['index'])
        for f in functions(e):
            address,size = DEFS[f['name']]
            if lo <= address < hi:
                need((f['section'],f['value'],f['size']) == (sec['index'],address,size), 'Original FUNC VA/size/section identity')
                code(e,f)
    need(sections == {s['index'] for s in e.sections if s['flags']&2 and s['size']}, 'Only six proved code allocations')
    need(sum(instructions(e.data(e.section('.code_'+format(lo,'x')))) for lo,hi,d in S['spans']) == 445, 'All445 original instructions')
    return e


def joined(raw, parent, natives):
    e = E(raw)
    need(e.header[0] == 1 and e.header[3] == 0 and not e.program_headers, 'Diagnostic unresolved ET_REL')
    canonical(e)
    sec = e.section('.channel_graph')
    need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align']) == (1,6,0,3166,2), 'Exact3166B graph extent')
    need([s['index'] for s in e.sections if s['flags']&2 and s['size']] == [sec['index']], 'No hidden graph allocations')
    old = {f['name']:(parent,f) for f in functions(parent)}
    selected = {f['name']:(z,f) for name,z in natives.items() if name in S['new_units'] for f in functions(z)}
    need(not set(old)&set(selected), 'No duplicate parent/source provider')
    full = {f['name']:f for f in functions(e)}
    need(len(full) == 191 and set(full) == set(old)|set(selected), 'All191 genuine FUNC providers')
    sequence = list(old) + [d[0] for d in NEW]
    expected_bytes = parent.data('.program_graph')+b''.join(code(*selected[n]) for n in sequence[len(old):])
    need(e.data(sec) == expected_bytes, 'Exact genuine2250B prefix plus916B C-owned extension')
    positions = {n:f['value'] for n,(p,f) in old.items()}
    at = 2250
    for n,address,size in NEW:
        positions[n] = at
        at += size
    for n,(source,f) in {**old,**selected}.items():
        actual = full[n]
        need((actual['section'],actual['value'],actual['size']) == (sec['index'],positions[n],f['size']), 'Every FUNC source/owner/position')
        need(code(e,actual) == code(source,f) and edges(e,actual) == edges(source,f), 'Every source body and typed control retained')
    need(len(e.relocations) == 144, 'All144 pending direct controls')
    need([s['name'] for s in e.symbols if s['name'] and s['section'] == 0] == ['tsl9_queue_external_14d2e'], 'One local direct-provider frontier')
    need(instructions(e.data(sec)) == 1104, 'All1104 complete instructions')
    return e


def rejected(call):
    try:
        call()
    except (ValueError, KeyError, IndexError, struct.error):
        return True
    return False


def negatives(nom, full, firmware, parent, natives):
    count = 0
    for e, names, gate in [
        (nom, ['.code_'+format(lo,'x') for lo,hi,d in S['spans']], lambda raw:nominal(raw,firmware)),
        (full, ['.channel_graph'], lambda raw:joined(raw,parent,natives))]:
        for name in names:
            s = e.section(name)
            for at in range(s['size']):
                raw = bytearray(e.raw)
                raw[s['offset']+at] ^= 1
                need(rejected(lambda:gate(bytes(raw))), 'Every altered allocated byte rejected without ELF digest')
                count += 1
        table = e.section('.symtab')
        for f in functions(e):
            for delta,fmt,value in [(12,'B',17),(13,'B',2),(14,'H',0xfff1),(8,'I',f['size']+2)]:
                raw = bytearray(e.raw)
                struct.pack_into('<'+fmt,raw,table['offset']+16*f['index']+delta,value)
                need(rejected(lambda:gate(bytes(raw))), 'Altered FUNC type/visibility/owner/size rejected')
                count += 1
        for delta,value in [(24,0x8000),(36,0)]:
            raw = bytearray(e.raw)
            struct.pack_into('<I',raw,delta,value)
            need(rejected(lambda:gate(bytes(raw))), 'Altered ELF entry/flags rejected')
            count += 1
    # A zero-sized/wrong-owner symbol must not escape full-extent validation.
    for f in functions(nom):
        raw = bytearray(nom.raw)
        wrong = next(s['index'] for s in nom.sections if s['flags']&2 and s['size'] and s['index'] != f['section'])
        struct.pack_into('<H',raw,nom.section('.symtab')['offset']+16*f['index']+14,wrong)
        need(rejected(lambda:nominal(bytes(raw),firmware)), 'Nominal FUNC cannot borrow another proved section')
        count += 1
    for index in range(len(nom.program_headers)):
        for field in range(8):
            raw = bytearray(nom.raw)
            raw[nom.header[4]+32*index+4*field] ^= 1
            need(rejected(lambda:nominal(bytes(raw),firmware)), 'Every PHDR field rejected')
            count += 1
    # Mutate every pending relocation, preserving all source bytes.
    for section in full.sections:
        if section['type'] != 4:
            continue
        for at in range(0,section['size'],12):
            raw = bytearray(full.raw)
            struct.pack_into('<i',raw,section['offset']+at+8,2)
            need(rejected(lambda:joined(bytes(raw),parent,natives)), 'Every nonzero relocation addend rejected')
            count += 1
    return count


def verify(llvm, folder, mode, write, upstream=True):
    need(folder.name == mode, 'Selected language folder')
    for k in ('reader','parent_checker','curation_checker','firmware'):
        need(sha(ROOT/S[k]) == S[k+'_sha256'], 'Frozen '+k)
    for n,pin in S['tools'].items():
        need(sha(llvm/n) == pin, 'Pinned actual tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256'], 'Pinned stdint')
    need(sha(ROOT/S['curation_root']/'verification.json') == S['curation_receipt_sha256'], 'Unchanged original90-comparison receipt')
    measurement = json.loads((folder/'measurement.json').read_bytes())
    need(measurement['mode'] == mode and measurement['inputs'] == B['portable'](B['inputs'](llvm,mode),llvm), 'Exact producer inputs')
    commands = [dict(label=n,argv=B['portable'](a,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,a in B['recipes'](llvm,folder,mode)]
    need(measurement['commands'] == commands, 'Actual IR/link/read command identity and zero exit')
    expected = {u['name']+'.ll' for u in S['units']}|{n+'.log' for n,a in B['recipes'](llvm,folder,mode)}|{'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf','UNRESOLVED-CHANNEL-GRAPH.o'}
    need(set(measurement['artifacts']) == expected, 'Complete producer output inventory')
    for n,record in measurement['artifacts'].items():
        p = folder/n
        need(sha(p) == record['sha256'] and p.stat().st_size == record['bytes'], 'Unchanged actual output '+n)
    C = runpy.run_path(str(ROOT/S['curation_checker']))
    manifest = C['metadata']()
    curation = json.loads((ROOT/S['curation_root']/'verification.json').read_bytes())
    if upstream:
        with contextlib.redirect_stdout(io.StringIO()):
            C['audit'](ROOT/S['curation_root'],curation,manifest)
            G = runpy.run_path(str(ROOT/S['parent_checker']))
            G['verify'](llvm,B['parent'](mode).parent,mode,False)
    need(sha(B['parent'](mode)) == S['parent_object_sha256'], 'Genuine source-bound2250B parent')
    firmware = (ROOT/S['firmware']).read_bytes()
    natives = {}
    controls = []
    for u in S['units']:
        need([f for f in manifest['files'] if f['destination'] == u['source']] == [u['file_entry']], 'Current source provenance identity')
        actual = [{k:x[k] for k in u['unit_identity']} for x in manifest['native_units'] if x['name'] == u['name']]
        need(actual == [u['unit_identity']], 'Current compile profile identity')
        need(sha(ROOT/u['source']) == u['source_sha256'], 'Selected current C source')
        p = B['obj'](u,mode)
        n,edges_found = native(p.read_bytes(),u,firmware)
        natives[u['name']] = n
        controls += edges_found
        ir = (folder/(u['name']+'.ll')).read_text(encoding='utf-8')
        names = re.findall(r'^define\b[^\n]*@([A-Za-z0-9_]+)\(',ir,re.M)
        need(set(names) == {d[0] for d in u['definitions']}, 'All source definitions remain actual LLVM IR regions')
        need(not re.search(r'\.(?:incbin|byte|2byte|4byte|word|half)\b',ir), 'No original-code byte embedding')
    parent = E(B['parent'](mode))
    nom = nominal((folder/'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf').read_bytes(),firmware)
    full = joined((folder/'UNRESOLVED-CHANNEL-GRAPH.o').read_bytes(),parent,natives)
    negative_count = negatives(nom,full,firmware,parent,natives)
    report = dict(schema='TSL9-channel-filter-static-verification-v1',passed=True,mode=mode,
        checker_sha256=sha(Path(__file__)),source_objects=len(natives),native_FUNC=94,native_controls=len(controls),
        original_PC_proved_bytes=1242,original_PC_instructions=445,original_PC_sections=6,
        nominal_ELF_sha256=sha(folder/'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf'),nominal_PHDR=nom.program_headers,
        RX_load_bytes=68340,RX_unproved_gap_bytes=67098,static_UND=0,static_RELA=0,global_ABS_substitutes=0,
        unresolved_graph_bytes=3166,unresolved_graph_instructions=1104,unresolved_graph_FUNC=191,unresolved_graph_RELA=144,
        unresolved_graph_sha256=sha(folder/'UNRESOLVED-CHANNEL-GRAPH.o'),unresolved_graph_UND=['tsl9_queue_external_14d2e'],
        opaque_runtime_sites=S['opaque_sites'],new_opaque_runtime_sites=7,full_graph_opaque_runtime_sites=15,
        negative_controls=negative_count,curated_comparisons=90,curated_objects=180,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,network=False,hardware_accessed=False,
        firmware_BIN_generated=False,firmware_ready=False,ROM_identity_proved=False,hardware_OTA_proved=False,
        limits=['Private architectural regions are not ordinary C ABI functions.',
                'No installed ROM identity, call preservation, full memory/IRQ/startup/OTA proof.',
                'Six original-PC code sections are proved; unproved LOAD gaps are not firmware.',
                'VMA0 ET_REL retains PC-sensitive code and pending controls; never execute it.',
                'One UND is this local graph frontier; 14D2E expands to at least71 external direct targets.'])
    output = folder/'verification.json'
    if write:
        need(not output.exists(), 'Create-only verification receipt')
        output.write_bytes(B['encode'](report))
    elif output.exists():
        need(json.loads(output.read_bytes()) == report, 'Exact read-only receipt replay')
    print(json.dumps({k:v for k,v in report.items() if k not in ['limits','opaque_runtime_sites','nominal_PHDR']}))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--mode',choices=['c','cpp'],required=True)
    p.add_argument('--write',action='store_true')
    a = p.parse_args()
    verify(a.tool_dir.resolve(),a.folder.resolve(),a.mode,a.write)
