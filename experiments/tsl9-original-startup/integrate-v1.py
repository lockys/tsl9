#!/usr/bin/env python3
"""Partial-link actual C/C++ startup and initializer; never execute target code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = json.loads((HERE / 'spec-v1.json').read_bytes())
K = json.loads((HERE / 'integration-v1.json').read_bytes())
B = runpy.run_path(str(HERE / 'build-v1.py'))
need, sha, encoded, portable = (B[n] for n in ('need', 'sha', 'encoded', 'portable'))
OUTPUT = 'UNRESOLVED-ORIGINAL-STARTUP.o'

def curated(unit, mode):
    return (ROOT / K['curation']).parent / unit / mode / 'curated/unit.o'

def inputs(llvm):
    paths = [Path(__file__), HERE/'integration-v1.json', HERE/'joined-v1.ld',
             HERE/'spec-v1.json', HERE/'build-v1.py', ROOT/'src/source-manifest.json',
             ROOT/K['curation'], ROOT/K['previous_curation'], ROOT/K['standalone_receipt'],
             ROOT/K['parent_manifest_deriver'], ROOT/K['data_source'],
             ROOT/K['new_file_entry']['destination'],
             llvm/'llvm-objcopy.exe', llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [ROOT/S[n] for n in ('source','firmware','reader','curation_checker','author','source_map')]
    for mode in ('c','cpp'):
        paths += [curated('boot-original',mode), curated('startup-data',mode),
                  (ROOT/K['standalone_receipt']).parent/mode/'native.o']
    paths += [llvm/n for n in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(paths))}

def source_proof(llvm):
    for k in ('firmware','reader','curation_checker','source','author','source_map'):
        need(sha(ROOT/S[k]) == S[k+'_sha256'], 'Pinned '+k)
    for n,pin in S['tools'].items():
        need(sha(llvm/n) == pin, 'Pinned tool '+n)
    need(sha(llvm/'llvm-objcopy.exe') == K['objcopy_sha256'], 'Pinned section selector')
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256'], 'Pinned header')
    for name in ('curation','previous_curation','standalone_receipt','parent_manifest_deriver','data_source'):
        need(sha(ROOT/K[name]) == K[name+'_sha256'], 'Pinned '+name)
    need(sha(ROOT/'src/source-manifest.json') == K['current_manifest_sha256'], 'Exact current79-file manifest')
    raw = runpy.run_path(str(ROOT/K['parent_manifest_deriver']))['raw_parent']()
    need(hashlib.sha256(raw).hexdigest() == K['previous_manifest_sha256'], 'Exact78-file parent manifest')
    old = json.loads(raw)
    old['files'].append(K['new_file_entry'])
    old['native_units'].append(K['new_unit_entry'])
    need(old == json.loads((ROOT/'src/source-manifest.json').read_bytes()), 'Only one genuine source/unit extension')
    previous = json.loads((ROOT/K['previous_curation']).read_bytes())
    current = json.loads((ROOT/K['curation']).read_bytes())
    need(len(previous['results']) == 104 and len(current['results']) == 106 and
         current['results'][:104] == previous['results'], 'Every prior104 comparison unchanged')
    need(len(previous['artifacts']) == 625 and len(current['artifacts']) == 637 and
         all(current['artifacts'].get(k) == v for k,v in previous['artifacts'].items()), 'Every prior625 artifact record unchanged')
    p = subprocess.run([sys.executable,'-B',str(ROOT/S['curation_checker']),
                        '--replay',str(ROOT/K['curation'])],cwd=ROOT,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    need(p.returncode == 0, 'Current full source replay')
    replay = json.loads(p.stdout)
    need(replay['passed'] and replay['comparisons'] == 106, 'Actual106 current comparisons')
    standalone = json.loads((ROOT/K['standalone_receipt']).read_bytes())
    need(standalone['inputs'] == portable(B['inputs'](llvm),llvm), 'Every standalone producer input unchanged')
    for mode in ('c','cpp'):
        original = (ROOT/K['standalone_receipt']).parent/mode/'native.o'
        need(sha(original) == K['standalone_native_object_sha256'], 'Actual standalone code object')
        need(B['audit_object'](original) == standalone['modes'][mode]['result'], 'Complete original572B212i audit')
        need(sha(curated('boot-original',mode)) == K['curated_native_object_sha256'], 'Actual curated code object')
        measured = B['audit_object'](curated('boot-original',mode))
        need(measured == dict(standalone['modes'][mode]['result'],
                             native_object_sha256=K['curated_native_object_sha256']), 'Curated code complete original-VA identity')
        need(sha(curated('startup-data',mode)) == K['data_object_sha256'], 'Actual C-compiled initializer carrier')
    return dict(passed=True,source_C_H_files=79,native_units=53,current_comparisons=106,
                current_objects=212,prior104_comparisons_and625_artifacts_unchanged=True,
                actual_standalone_and_curated_code_original_VA_equal=True,
                source_extension='One source and one native unit; exact retained parent manifest',
                target_executed=False,negative_cases_executed=0)

def elf(path):
    return runpy.run_path(str(ROOT/S['reader']))['ELF'](path)

def globals_by_name(e):
    symbols = [s for s in e.symbols if s['info']>>4]
    need(len({s['name'] for s in symbols}) == len(symbols), 'Unique real global symbols')
    need(all(s['section'] != 0xfff1 for s in symbols), 'No ABS provider substitutes')
    return {s['name']:s for s in symbols}

def original_data():
    fw = (ROOT/S['firmware']).read_bytes()
    off = K['data_original_start']-0x8000
    data = fw[off:off+K['data_bytes']]
    need(len(data) == 128 and hashlib.sha256(data).hexdigest() == K['data_sha256'], 'Original full128B initializer')
    return data

def audit_selected(path, mode):
    selected = elf(path)
    carrier = elf(curated('startup-data',mode))
    allocated = [s for s in selected.sections if s['flags']&2 and s['size']]
    need(len(allocated) == 1, 'Only actual initializer allocated')
    sec = allocated[0]
    need(sec['name'] == K['data_section'] and sec['flags'] == 2 and sec['type'] == 1 and
         sec['address'] == 0 and sec['size'] == 128, 'Exact readonly initializer section')
    need(selected.header[0] == 1 and not selected.program_headers and not selected.relocations,
         'Real data-only relocatable object without loading headers')
    need(selected.data(sec) == carrier.data(K['data_section']) == original_data(), 'Selected bytes equal real C data and original firmware')
    symbols = globals_by_name(selected)
    need(set(symbols) == {K['data_symbol']}, 'No diagnostic RAM/stack or unrelated definitions retained')
    s = symbols[K['data_symbol']]
    need(s['info'] == 17 and s['value'] == 0 and s['size'] == 128 and s['section'] == sec['index'],
         'Genuine strong128B C OBJECT provider')
    return dict(passed=True,selected_bytes=128,object_sha256=sha(path),
                original_initializer_sha256=K['data_sha256'],
                diagnostic_BSS_or_stack_retained=False,source_carrier_modified=False)

def audit_component(path, mode):
    n = elf(curated('boot-original',mode))
    e = elf(path)
    nm = globals_by_name(n)
    em = globals_by_name(e)
    need(e.header[0] == 1 and not e.program_headers, 'Unresolved ET_REL without execution headers')
    offsets = {}
    pieces = []
    at = 0
    for region in S['regions']:
        fn = nm[region['name']]
        sec = n.sections[fn['section']]
        offsets[sec['name']] = at
        pieces.append(n.data(sec))
        at += region['bytes']
    need(at == 572, 'Exact original startup code extent')
    allowed = {'.boot_code':(6,572),'.initializer':(2,128)}
    need({s['name'] for s in e.sections if s['flags']&2 and s['size']} == set(allowed), 'Only genuine code and initializer allocated')
    for name,(flags,size) in allowed.items():
        sec = e.section(name)
        need(sec['flags'] == flags and sec['size'] == size and sec['address'] == 0 and
             sec['type'] == 1, 'Exact section and no final memory map '+name)
    need(e.data('.boot_code') == b''.join(pieces), 'All572 compiled code carrier bytes unchanged')
    need(e.data('.initializer') == original_data(), 'Whole original128B initializer bound')
    need(set(em) == set(nm)|{K['data_symbol']}, 'Complete genuine global symbol inventory')
    for name,s in nm.items():
        actual = em[name]
        if s['section']:
            owner = n.sections[s['section']]['name']
            need(actual['info'] == 18 and actual['other'] == s['other'] and actual['size'] == s['size'] and
                 e.sections[actual['section']]['name'] == '.boot_code' and
                 actual['value'] == offsets[owner]+s['value'], 'Real compiled FUNC owner '+name)
        elif name == K['data_alias']:
            need(actual['info'] == 17 and actual['other'] == 0 and actual['size'] == 0 and
                 e.sections[actual['section']]['name'] == '.initializer' and actual['value'] == 0,
                 'Section-relative alias to genuine data provider')
        else:
            need(actual['info'] == 16 and actual['section'] == 0 and actual['value'] == 0 and
                 actual['size'] == 0, 'Unresolved external remains explicit '+name)
    provider = em[K['data_symbol']]
    need(provider['info'] == 17 and provider['other'] == 0 and provider['size'] == 128 and
         e.sections[provider['section']]['name'] == '.initializer' and provider['value'] == 0,
         'Actual full-size OBJECT owner retained')
    expected = Counter()
    for rel in n.relocations:
        symbol = n.symbols[rel['symbol']]
        owner = n.sections[rel['section']]['name']
        if symbol['info']>>4:
            bound = em[symbol['name']]
            target = e.sections[bound['section']]['name'] if bound['section'] else ''
            role = (bound['name'],bound['info'],bound['other'],bound['size'],target,bound['value'])
        else:
            need(symbol['section'] > 0 and symbol['section'] != 0xfff1, 'Real local HI-label owner')
            src = n.sections[symbol['section']]['name']
            role = (symbol['name'],symbol['info'],symbol['other'],symbol['size'],
                    '.boot_code',offsets[src]+symbol['value'])
        expected[('.boot_code',offsets[owner]+rel['offset'],rel['type'],rel['addend'],role)] += 1
    actual = Counter()
    for rel in e.relocations:
        symbol = e.symbols[rel['symbol']]
        target = e.sections[symbol['section']]['name'] if symbol['section'] else ''
        role = (symbol['name'],symbol['info'],symbol['other'],symbol['size'],target,symbol['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)] += 1
    need(actual == expected and len(e.relocations) == 82, 'All82 typed RELA and complete local/global ownership')
    undefined = sorted(name for name,s in em.items() if s['section'] == 0)
    need(undefined == K['unresolved'], 'Exactly three genuine outstanding interfaces')
    return dict(passed=True,mode=mode,code_bytes=572,instructions=212,FUNC=99,
                original_initializer_bytes=128,RELA=82,PC_relative_RELA=6,
                direct_control_RELA=76,UND=undefined,data_provider=K['data_symbol'],
                data_alias=K['data_alias'],alias_section_relative=True,ABS_providers=0,
                all_code_carriers_unchanged=True,all_code_original_VA_equal=True,
                all_global_and_local_relocation_targets_owned=True,
                all_initializer_bytes_original_equal=True,diagnostic_RAM_stack_excluded=True,
                ELF_VMA_zero=True,executable=False,component_sha256=sha(path),
                target_executed=False,ISA_emulated=False,HOST_model_executed=False,
                hardware_accessed=False,network=False,negative_cases_executed=0,
                firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(folder.iterdir()) if p.is_file()}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--output',type=Path)
    group.add_argument('--replay',type=Path)
    a = p.parse_args()
    llvm = a.tool_dir.resolve()
    proof = source_proof(llvm)
    before = portable(inputs(llvm),llvm)
    if a.replay:
        out = a.replay.resolve()
        need(out.parent == HERE/'build', 'Owned retained build folder')
        saved = json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs'] == before and saved['source_proof'] == proof, 'Every retained actual input unchanged')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts'] == inventory(out/mode), 'Complete retained output inventory')
            need(saved['modes'][mode]['selected_data'] == audit_selected(out/mode/'initializer-only.o',mode), 'Actual selected-data replay')
            need(saved['modes'][mode]['result'] == audit_component(out/mode/OUTPUT,mode), 'Complete normal component replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-artifact-replay',source_proof=proof)))
        return
    out = a.output.resolve()
    need(out.parent == HERE/'build' and not out.exists(), 'Create-only direct child output')
    report = dict(schema='TSL9-original-startup-partial-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        f = out/mode
        f.mkdir(parents=True)
        selected = f/'initializer-only.o'
        output = f/OUTPUT
        commands = []
        recipes = [
            ('select-initializer',[str(llvm/'llvm-objcopy.exe'),'--only-section='+K['data_section'],
                                   str(curated('startup-data',mode)),str(selected)]),
            ('joined-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),
                            str(curated('boot-original',mode)),str(selected),'-o',str(output)]),
            ('joined-read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        data_audit = None
        for label,argv in recipes:
            result = subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode == 0, 'Actual '+label+' failed; original log retained')
            if label == 'select-initializer':
                data_audit = audit_selected(selected,mode)
        audit = audit_component(output,mode)
        (f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode] = dict(result=audit,selected_data=data_audit,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in audit.items() if k!='UND'}|dict(UND_count=len(audit['UND']))))
    need(before == portable(inputs(llvm),llvm), 'All inputs unchanged during actual partial link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__ == '__main__':
    try:
        main()
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        message = str(error)
        for path,token in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message = message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr)
        sys.exit(1)

