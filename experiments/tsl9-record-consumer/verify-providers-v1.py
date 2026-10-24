#!/usr/bin/env python3
"""Select genuine compiled provider regions and inspect bytes/relocations offline."""
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
K = json.loads((HERE/'providers-v1.json').read_bytes())
N = runpy.run_path(str(HERE/'build-v1.py'))
B = N['B']
portable, encoded = N['portable'], N['encoded']

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pins(llvm):
    for key in ('state_checker', 'state_spec', 'dispatch_legacy_checker'):
        need(sha(ROOT/K[key]) == K[key+'_sha256'], 'Pinned provider provenance')
    for path, pin in K['pins'].items():
        need(sha(ROOT/path) == pin, 'Actual provider input unchanged')
    for name, pin in N['S']['tools'].items():
        need(sha(llvm/name) == pin, 'Pinned local tool')

def full_state(path):
    # Only the inspected positive ELF audit is invoked, never its CLI.
    return runpy.run_path(str(ROOT/K['state_checker']))['audit_object'](path)

def object_path(mode, kind):
    return ROOT/K[kind+'_objects'][mode]

def selected_path(folder, mode):
    return folder/mode/'selected-state-read.o'

def audit_regions(path, regions, undefined, combined):
    e = N['elf'](path)
    fw = (ROOT/N['S']['firmware']).read_bytes()
    need(e.header[0] == 1 and e.header[1] == 243 and not e.program_headers, 'RISC-V ET_REL only')
    rows = [x for x in e.symbols if x['info'] >> 4]
    gm = {x['name']: x for x in rows}
    need(len(gm) == len(rows) and set(gm) == {x['name'] for x in regions}|set(undefined), 'Exact actual provider symbols')
    for name in undefined:
        x = gm[name]
        need(x['info'] == 16 and x['section'] == x['value'] == x['size'] == 0, 'Honest unresolved provider')
    starts = {x['start']: x['name'] for x in regions}
    external = {int(name.rsplit('_',1)[1],16):name for name in undefined}
    expected = Counter()
    covered = {}
    count = code = noncontrol = 0
    direct = []
    for region in regions:
        f = gm[region['name']]
        need(f['info'] == 18 and f['other'] == 0 and f['size'] == region['bytes'] and 0 < f['section'] < 0xff00, 'Genuine full-sized function region')
        sec = e.sections[f['section']]
        need(sec['flags'] == 6 and sec['type'] == 1 and sec['address'] == 0, 'Exact native allocation')
        if combined:
            need(sec['name'] == '.state_read_code', 'Selected actual section')
        else:
            need(sec['name'] == '.text.'+f['name'] and f['value'] == 0 and sec['size'] == f['size'], 'Whole existing dispatch allocation')
        at = f['value']
        need(at+f['size'] <= sec['size'], 'Owned provider byte interval')
        covered.setdefault(sec['index'], []).append((at, at+f['size']))
        raw = e.data(sec)[at:at+f['size']]
        original = fw[region['start']-0x8000:region['end']-0x8000]
        need(sha_bytes(original) == region['original_sha256'], 'Pinned original provider range')
        normalized = bytearray(raw)
        off = 0
        while off < len(raw):
            width = 4 if original[off]&3 == 3 else 2
            need(off+width <= len(raw) and (4 if raw[off]&3 == 3 else 2) == width, 'Whole original instruction width')
            edge = B['decode_control'](original[off:off+width], region['start']+off)
            if edge:
                kind, destination = edge
                name = starts.get(destination, external.get(destination))
                need(name is not None, 'Every original direct destination owned or explicit')
                w, mask = B['MASKS'][kind]
                a = int.from_bytes(raw[off:off+w], 'little')
                b = int.from_bytes(original[off:off+w], 'little')
                need(w == width and a&mask == b&mask and a&(~mask&((1<<(8*w))-1)) == 0, 'Exact native control carrier and zero displacement')
                normalized[off:off+w] = (a|B['immediate'](kind,destination-region['start']-off)).to_bytes(w,'little')
                expected[(sec['index'], at+off, kind, 0, name)] += 1
                direct.append(dict(PC=region['start']+off,type=kind,target_PC=destination,target=name))
            else:
                noncontrol += width
            off += width
            count += 1
        need(bytes(normalized) == original, 'Every original provider byte after static original-VA encoding')
        code += len(raw)
    need({s['index'] for s in e.sections if s['flags']&2 and s['size']} == set(covered), 'All actual allocated sections owned')
    for idx, intervals in covered.items():
        cursor = 0
        for start,end in sorted(intervals):
            need(start == cursor and end > start, 'No hidden byte, gap or overlap')
            cursor = end
        need(cursor == e.sections[idx]['size'], 'Every allocated byte covered')
    actual = Counter((x['section'],x['offset'],x['type'],x['addend'],e.symbols[x['symbol']]['name']) for x in e.relocations)
    need(actual == expected, 'Exact owned typed-reference inventory')
    return dict(passed=True,code_bytes=code,instructions=count,FUNC=len(regions),RELA=len(e.relocations),
                UND=sorted(undefined),noncontrol_bytes_equal=noncontrol,direct_references=direct,
                native_object_sha256=sha(path),complete_original_VA_encoded_bytes_equal=True,
                target_executed=False,HOST_model_executed=False,ISA_emulated=False,
                hardware_accessed=False,network=False,negative_cases_executed=0,firmware_BIN_generated=False)

def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def audit_state(path):
    return audit_regions(path, K['state_regions'], [], True)

def audit_dispatch(path):
    facts = audit_regions(path, K['dispatch_regions'], K['dispatch_undefined'], False)
    need(facts['code_bytes'] == 102 and facts['instructions'] == 35 and facts['RELA'] == 9, 'Whole original dispatch scope')
    return facts

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()}

def inputs(llvm):
    paths = [Path(__file__),HERE/'providers-v1.json',HERE/'state-read-v1.ld',HERE/'build-v1.py',
             HERE/'spec-v1.json',ROOT/K['state_checker'],ROOT/K['state_spec'],ROOT/K['dispatch_legacy_checker'],
             ROOT/N['S']['firmware'],ROOT/N['S']['reader'],N['SHARED']]
    paths += [ROOT/p for p in K['pins']]
    paths += [llvm/n for n in ('ld.lld.exe','llvm-objdump.exe')]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(paths))}

def audit(folder, llvm):
    pins(llvm)
    result = {}
    for mode in ('c','cpp'):
        whole = full_state(object_path(mode,'state'))
        selected = audit_state(selected_path(folder,mode))
        dispatch = audit_dispatch(object_path(mode,'dispatch'))
        need(whole['code_bytes'] == 336 and selected['code_bytes'] == 42 and selected['FUNC'] == 4, 'Actual 42B subset of genuine 336B source')
        result[mode] = dict(full_state_positive_audit=whole,selected_state=selected,dispatch=dispatch,
                            artifacts=inventory(folder/mode))
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--output',type=Path)
    g.add_argument('--replay',type=Path)
    a = p.parse_args()
    llvm = a.tool_dir.resolve()
    pins(llvm)
    before = portable(inputs(llvm),llvm)
    if a.replay:
        out = a.replay.resolve()
        need(out.parent == HERE/'build', 'Owned retained provider output')
        saved = json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs'] == before and saved['modes'] == audit(out,llvm), 'Complete actual provider replay')
        print(json.dumps(dict(passed=True,mode='read-only-actual-provider-replay',target_executed=False)))
        return
    out = a.output.resolve()
    need(out.parent == HERE/'build' and not out.exists(), 'Create-only owned provider selection')
    for mode in ('c','cpp'):
        folder = out/mode
        folder.mkdir(parents=True)
        full_state(object_path(mode,'state'))
        # All four architectural regions are roots: native fall-through is not a relocation.
        argv = [str(llvm/'ld.lld.exe'),'-r','--gc-sections','--no-relax']
        argv += ['--undefined='+x['name'] for x in K['state_regions']]
        argv += ['-T',str(HERE/'state-read-v1.ld'),str(object_path(mode,'state')),'-o',str(selected_path(out,mode))]
        for label,cmd in [('select',argv),('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(selected_path(out,mode))])]:
            proc = subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (folder/(label+'.log')).write_bytes(proc.stdout)
            need(proc.returncode == 0, 'Actual provider selection command failed; log retained')
    result = audit(out,llvm)
    need(before == portable(inputs(llvm),llvm), 'All provider inputs unchanged during selection')
    report = dict(schema='TSL9-genuine-provider-selection-v1',inputs=before,modes=result,
                  every_implicit_fallthrough_region_explicitly_retained=True,
                  firmware_bytes_copied_to_executable=False,target_executed=False,network=False)
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
    print(json.dumps(dict(passed=True,providers={m:{k:result[m][k] for k in ('selected_state','dispatch')} for m in result})))
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps(dict(passed=False,error=str(error))),file=sys.stderr)
        raise SystemExit(1)
